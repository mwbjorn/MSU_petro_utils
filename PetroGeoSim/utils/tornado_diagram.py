# tornado_diagram.py
import copy
import re
import numpy as np
from PetroGeoSim.models import Model
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

TORNADO_CONFIG = {
    "enabled": True,
    "target_results": [],
    "quantile_type": "p10_p90",
    "use_risked": False, #not wrk
    "low_quantile": "P10",
    "high_quantile": "P90",
    "base_quantile": "P50"
}

def extract_variables_from_equation(equation: str) -> list:
    """
    Извлекает переменные из уравнения, учитывая скобки и выражения
    Например: "GRV * ntg * poro * (gor * 0.001) * 6.29" -> ["GRV", "ntg", "poro", "gor"]
    """
    # Находим все выражения в скобках
    bracket_pattern = r'\([^()]+\)'
    bracket_exprs = re.findall(bracket_pattern, equation)
    
    # Извлекаем переменные из скобочных выражений
    variables = []
    for expr in bracket_exprs:
        # Удаляем скобки и парсим внутреннее выражение
        inner_expr = expr.strip('()')
        # Извлекаем переменные из внутреннего выражения
        inner_vars = extract_simple_variables(inner_expr)
        variables.extend(inner_vars)
        # Заменяем скобочное выражение на временный маркер
        equation = equation.replace(expr, '')
    
    # Извлекаем оставшиеся переменные
    simple_vars = extract_simple_variables(equation)
    variables.extend(simple_vars)
    
    # Убираем дубликаты, сохраняя порядок
    seen = set()
    unique_vars = []
    for var in variables:
        if var not in seen:
            seen.add(var)
            unique_vars.append(var)
    
    return unique_vars

def extract_simple_variables(expression: str) -> list:
    """
    Извлекает простые переменные из выражения без скобок
    """
    # Заменяем операторы на пробелы
    temp = expression
    for op in ['*', '/', '+', '-', '(', ')']:
        temp = temp.replace(op, ' ')
    
    # Разбиваем на токены
    tokens = temp.split()
    
    # Фильтруем только переменные (не числа)
    variables = []
    for token in tokens:
        token = token.strip()
        if token:
            # Проверяем, что это не число
            try:
                float(token)
            except ValueError:
                if token not in ['', '(', ')']:
                    variables.append(token)
    
    return variables

def evaluate_equation_with_dict(equation: str, values: dict) -> float:
    """
    Вычисляет уравнение с подстановкой значений
    Поддерживает выражения в скобках
    """
    logger.debug(f"eq: {equation}")
    logger.debug(f"values: {values}")
    
    # Создаем копию уравнения для обработки
    processed_equation = equation
    
    # Обрабатываем все выражения в скобках
    bracket_pattern = r'\([^()]+\)'
    bracket_exprs = re.findall(bracket_pattern, processed_equation)
    logger.debug(f"found expressions: {bracket_exprs}")
    
    for bracket_expr in bracket_exprs:
        # Извлекаем переменные из скобочного выражения
        inner_expr = bracket_expr.strip('()')
        inner_vars = extract_simple_variables(inner_expr)
        logger.debug(f"Переменные в {bracket_expr}: {inner_vars}")
        
        # Создаем словарь значений для внутреннего выражения
        inner_values = {}
        for var in inner_vars:
            if var in values:
                inner_values[var] = values[var]
            else:
                logger.warning(f"Перменная {var} не найдена в значениях, => 0")
                inner_values[var] = 0
        
        # Вычисляем значение скобочного выражения
        try:
            # Создаем безопасное пространство имен для eval
            namespace = {"__builtins__": {}}
            namespace.update(inner_values)
            result = eval(inner_expr, namespace)
            logger.debug(f"eval {bracket_expr} = {result}")
            # Заменяем выражение на результат
            processed_equation = processed_equation.replace(bracket_expr, str(result))
        except Exception as e:
            logger.error(f"Error evaluating expression {bracket_expr}: {e}")
            # Если не удалось вычислить, заменяем на 0
            processed_equation = processed_equation.replace(bracket_expr, "0")
    
    # Теперь обрабатываем оставшиеся переменные
    remaining_vars = extract_simple_variables(processed_equation)
    logger.debug(f"Перменные после: {remaining_vars}")
    
    # Создаем пространство имен для финального вычисления
    namespace = {"__builtins__": {}}
    for var in remaining_vars:
        if var in values:
            namespace[var] = values[var]
        else:
            logger.warning(f"Перменная {var} не найждена, => 0")
            namespace[var] = 0
    
    # Вычисляем итоговое выражение
    try:
        result = eval(processed_equation, namespace)
        logger.debug(f"result: {result}")
        return float(result)
    except Exception as e:
        logger.error(f"Ошибка в выражении {processed_equation}: {e}")
        return 0.0

def calculate_tornado_for_formula(model: Model, formula: str, formula_name: str = None) -> dict:
    """
    Рассчитывает торнадо-диаграмму для конкретной формулы
    """
    try:
        logger.info(f"Обсёт формулды: {formula_name or formula}")
        
        # Получаем все свойства (inputs и results)
        stats = model.get_all_properties("stats", include=("inputs", "results"))
        logger.info(f"stats, regions: {list(stats.keys())}")
        
        # Регионы
        regions = list(stats.keys())
        if not regions:
            logger.warning("no regions")
            return None
        
        first_region = regions[0]
        region_data = stats[first_region]
        logger.info(f"region: {first_region}, keys: {list(region_data.keys())[:10]}")
        
        # Создаем маппинг между отображаемыми именами и переменными
        # Получаем все входные переменные из модели с их маппингом
        variable_mapping = {}  # {variable_code: display_name}
        display_to_code = {}   # {display_name: variable_code}
        
        if hasattr(model, 'regions'):
            for region in model.regions.values():
                for display_name, input_prop in region.inputs.items():
                    if hasattr(input_prop, 'variable'):
                        variable_code = input_prop.variable
                        variable_mapping[variable_code] = display_name
                        display_to_code[display_name] = variable_code
                        logger.debug(f"Map: {variable_code} -> {display_name}")
        
        logger.info(f"mapping: {variable_mapping}")
        
        # Получаем все входные переменные (отображаемые имена)
        input_display_names = list(display_to_code.keys())
        logger.info(f"Input names: {input_display_names}")
        
        # Извлекаем переменные из формулы
        formula_vars = extract_variables_from_equation(formula)
        logger.info(f"Переменные в формуле '{formula}': {formula_vars}")
        
        # Преобразуем переменные из формулы в отображаемые имена
        valid_display_names = []
        valid_code_names = []
        
        for var in formula_vars:
            # Проверяем, есть ли переменная в маппинге
            if var in variable_mapping:
                display_name = variable_mapping[var]
                valid_display_names.append(display_name)
                valid_code_names.append(var)
                logger.info(f"мап {var} -> {display_name}")
            else:
                # Если переменная не найдена в маппинге, возможно это число или оператор
                # Проверяем, не является ли это число
                try:
                    float(var)
                    # Это число, пропускаем
                    logger.debug(f"пропуск: {var}")
                except ValueError:
                    logger.warning(f"Переменная {var} не найдена в модели.")
        
        if not valid_display_names:
            logger.warning(f"Нет переменных в формуле {formula_name}")
            return None
        
        # Получаем статистики для переменных (используем отображаемые имена)
        inputs_dict = {}
        for display_name in valid_display_names:
            if display_name in region_data:
                value = region_data[display_name]
                if isinstance(value, dict) and any(p in value for p in ['P10', 'P50', 'P90', 'Mean']):
                    inputs_dict[display_name] = value
                    logger.info(f"stats {display_name}: {list(value.keys())}")
                else:
                    logger.warning(f"stats {display_name} неверного формата")
            else:
                logger.warning(f"Имя: {display_name} не найдена в region_data")
        
        logger.info(f"stats {len(inputs_dict)} variables: {list(inputs_dict.keys())}")
        
        if not inputs_dict:
            logger.warning(f"names valid: {valid_display_names}")
            return None
        
        # Квантили
        low_quantile = TORNADO_CONFIG["low_quantile"]
        high_quantile = TORNADO_CONFIG["high_quantile"]
        base_quantile = TORNADO_CONFIG["base_quantile"]
        logger.info(f"quantiles: low={low_quantile}, base={base_quantile}, high={high_quantile}")
        
        # Базовые значения для всех переменных (используем отображаемые имена)
        base_inputs_display = {}
        for display_name in valid_display_names:
            if display_name in inputs_dict:
                input_stats = inputs_dict[display_name]
                if base_quantile in input_stats:
                    base_inputs_display[display_name] = input_stats[base_quantile]
                elif "Mean" in input_stats:
                    base_inputs_display[display_name] = input_stats["Mean"]
                else:
                    base_inputs_display[display_name] = 0
                logger.info(f"Base for {display_name}: {base_inputs_display[display_name]}")
        
        # Для вычисления формулы нужно преобразовать обратно в коды переменных
        base_inputs_for_formula = {}
        for i, display_name in enumerate(valid_display_names):
            code_name = valid_code_names[i]
            base_inputs_for_formula[code_name] = base_inputs_display[display_name]
        
        logger.info(f"Base inputs: {base_inputs_for_formula}")
        
        # Вычисляем базовый результат
        try:
            base_result = evaluate_equation_with_dict(formula, base_inputs_for_formula)
            logger.info(f"Base result: {base_result}")
        except Exception as e:
            logger.error(f"Error evaluating base result: {e}", exc_info=True)
            return None
        
        # проверка
        all_vars_in_formula = extract_variables_from_equation(formula)
        for var in all_vars_in_formula:
            if var not in base_inputs_for_formula and var in variable_mapping:
                display_name = variable_mapping[var]
                if display_name in inputs_dict:
                    input_stats = inputs_dict[display_name]
                    if base_quantile in input_stats:
                        base_inputs_for_formula[var] = input_stats[base_quantile]
                    elif "Mean" in input_stats:
                        base_inputs_for_formula[var] = input_stats["Mean"]
                    else:
                        base_inputs_for_formula[var] = 0
                    logger.info(f"Неверная переменная {var} , значение: {base_inputs_for_formula[var]}")

        # Рассчитываем влияние каждой переменной
        tornado_data = []
        
        for i, display_name in enumerate(valid_display_names):
            try:
                code_name = valid_code_names[i]
                logger.info(f"variable: {display_name} (code: {code_name})")
                
                input_stats = inputs_dict[display_name]
                low_value = input_stats.get(low_quantile, input_stats.get("Mean", 0))
                high_value = input_stats.get(high_quantile, input_stats.get("Mean", 0))
                base_value = base_inputs_display.get(display_name, 0)
                logger.info(f" Values: low={low_value}, base={base_value}, high={high_value}")
                
                # Низкое значение
                low_inputs = base_inputs_for_formula.copy()
                low_inputs[code_name] = low_value
                low_result = evaluate_equation_with_dict(formula, low_inputs)
                logger.info(f" Low result: {low_result}")
                
                # Высокое значение
                high_inputs = base_inputs_for_formula.copy()
                high_inputs[code_name] = high_value
                high_result = evaluate_equation_with_dict(formula, high_inputs)
                logger.info(f" High result: {high_result}")
                
                if low_result is not None and high_result is not None:
                    low_impact = low_result - base_result
                    high_impact = high_result - base_result
                    impact_range = abs(high_impact - low_impact)
                    if low_impact < 0:
                        # увеличивает результат
                        high_impact, low_impact = high_impact, low_impact
                        #positive_color = "#51cf66"  # зеленый
                        #negative_color = "#ff6b6b"  # красный
                    
                    tornado_data.append({
                        "variable": display_name,
                        "variable_code": code_name,
                        "base_value": float(base_value),
                        "low_value": float(low_value),
                        "high_value": float(high_value),
                        "base_result": float(base_result),
                        "low_result": float(low_result),
                        "high_result": float(high_result),
                        "low_impact": float(low_impact),
                        "high_impact": float(high_impact),
                        "impact_range": float(impact_range),
                        "unit": "",
                        "description": display_name,
                        "p10_value": float(low_value),   # low_value P10
                        "p90_value": float(high_value)   # high_value P90
                    })
                    logger.info(f" Add data for {display_name}, impact_range={impact_range}")
                else:
                    logger.warning(f" Ошибка получения результата {display_name}: low={low_result}, high={high_result}")
                    
            except Exception as e:
                logger.error(f"Error processing {display_name}: {e}", exc_info=True)
                continue
        
        if not tornado_data:
            logger.warning(f"Нет данных для торнадо для {formula_name}")
            return None
        
        logger.info(f"OK. {len(tornado_data)} variables")
        
        # Сортируем по диапазону влияния
        tornado_data.sort(key=lambda x: x["impact_range"])#, reverse=True)
        
        # Создаем данные для Plotly
        variables = [item["variable"] for item in tornado_data]
        #low_deviations = [item["low_result"] - base_result for item in tornado_data]
        #high_deviations = [item["high_result"] - base_result for item in tornado_data]
        low_deviations = []
        high_deviations = []
        low_texts = []
        high_texts = []
        low_colors = []
        high_colors = []
        for item in tornado_data:
            low_impact = item["low_impact"]
            high_impact = item["high_impact"]
            
            # Изменение логики цвета. Обратно зависимые части формул тоже вправо зеленым
            if low_impact > 0:
                # зеленым
                low_deviations.append(low_impact)
                high_deviations.append(high_impact)
                low_colors.append("#51cf66")
                high_colors.append("#ff6b6b")
                low_texts.append(f"{item['low_result']:.2f}")
                high_texts.append(f"{item['high_result']:.2f}")
            else:
                # красным
                low_deviations.append(low_impact)
                high_deviations.append(high_impact)
                low_colors.append("#ff6b6b")
                high_colors.append("#51cf66")
                low_texts.append(f"{item['high_result']:.2f}")
                high_texts.append(f"{item['low_result']:.2f}")
        
        plotly_data = {
            "data": [
                {
                    "y": variables,
                    "x": low_deviations,
                    "name": f"Уменьшение", #f"Low ({low_quantile})", #
                    "orientation": "h",
                    "marker": {"color": low_colors, "opacity": 0.7},
                    "type": "bar",
                    #"text": [f"{item['low_result']:.2f}" for item in tornado_data],
                    "text": low_texts,
                    "textposition": "outside",
                    "width": 0.4
                },
                {
                    "y": variables,
                    "x": high_deviations,
                    "name": f"Увеличение", #f"High ({high_quantile})",
                    "orientation": "h",
                    "marker": {"color": high_colors, "opacity": 0.7},
                    "type": "bar",
                    #"text": [f"{item['high_result']:.2f}" for item in tornado_data],
                    "text": high_texts,
                    "textposition": "outside",
                    "width": 0.4
                }
            ],
            "layout": {
                "title": f"Торнадо диаграмма: {formula_name or formula}<br><sup>Base: {base_result:.2f}</sup>",
                "xaxis": {
                    "title": "Отклонения",
                    "zeroline": True, 
                    "zerolinecolor": "black",
                    "zerolinewidth": 2,
                    "gridcolor": "lightgray"
                },
                "yaxis": {"title": "Значения", "automargin": True},
                "barmode": "overlay",
                "bargap": 0.2,
                "showlegend": True,
                "legend": {"x": 1.05, "y": 1},
                "height": max(500, len(variables) * 35),
                "margin": {"l": 180, "r": 120, "t": 80, "b": 50}
            }
        }
        
        return {
            "target_result": formula_name or formula,
            "formula": formula,
            "base_result": float(base_result),
            "low_quantile": low_quantile,
            "high_quantile": high_quantile,
            "base_quantile": base_quantile,
            "use_risked": TORNADO_CONFIG["use_risked"],
            "data": tornado_data,
            "plotly_data": plotly_data
        }
        
    except Exception as e:
        logger.error(f"Error in calculate_tornado_for_formula: {e}", exc_info=True)
        return None

def calculate_tornado_data(model: Model) -> dict:
    """
    Рассчитывает торнадо-диаграммы для всех формул
    """
    if not TORNADO_CONFIG["enabled"]:
        logger.info("Торнадо выключен")
        return None
    
    try:
        logger.info("Начало обсчёта...")
        
        # Получаем все свойства
        all_props = model.get_all_properties("stats", include=("inputs", "results"))
        
        regions = list(all_props.keys())
        logger.info(f"regions: {regions}")
        
        if not regions:
            logger.warning("No regions found")
            return None
        
        # Получаем список формул из модели
        formulas = []
        if hasattr(model, 'regions'):
            logger.info(f"regions: {list(model.regions.keys())}")
            for region_name, region in model.regions.items():
                logger.info(f"curr region: {region_name}")
                logger.info(f"curr results: {list(region.results.keys())}")
                for result_name, result_prop in region.results.items():
                    if hasattr(result_prop, 'equation') and result_prop.equation:
                        logger.info(f"formula: {result_name} = {result_prop.equation}")
                        formulas.append({
                            "name": result_name,
                            "equation": result_prop.equation
                        })
        
        logger.info(f"Формула: {len(formulas)}")
        
        if not formulas:
            logger.warning("Нет формул")
            return None
        
        # Рассчитываем торнадо для каждой формулы
        tornado_results = {}
        for formula_info in formulas:
            logger.info(f"Обсчёт: {formula_info['name']}")
            result = calculate_tornado_for_formula(
                model, 
                formula_info["equation"], 
                formula_info["name"]
            )
            if result:
                logger.info(f"OK {formula_info['name']}")
                tornado_results[formula_info["name"]] = result
            else:
                logger.warning(f"Ошибка обсчёта формулы {formula_info['name']}")
        
        if not tornado_results:
            logger.warning("Не обсчитано")
            return None
        
        return {
            "tornado_diagrams": tornado_results,
            "available_formulas": [f["name"] for f in formulas]
        }
        
    except Exception as e:
        logger.error(f"Error in calculate_tornado_data: {e}", exc_info=True)
        return None
