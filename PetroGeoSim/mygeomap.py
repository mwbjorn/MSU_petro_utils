from collections import defaultdict

from PetroGeoSim.models import Model
from numpy import ndarray, nan_to_num, where, isnan

def send_mygeomap(model: Model) -> dict[str, dict]:
    initial_result = model.get_all_properties("values", include=("inputs", "results"))
    initial_stats = model.get_all_properties("stats", include=("inputs", "results"))
    initial_distribution = model.get_all_properties("distribution", include=("inputs", "results"))

    # Converts all NumPy arrays to lists (to enable serialization)
    final_result = defaultdict(dict)
    for reg, props in initial_result.items():
        # reg имя региона, props значение (словарь)
        # {'Площадь': array([]), ....  's * hef * poro * (1-sw) * (1/fvf)': array([]),
        # 'result1_probability': array([]), 'result2_probability': array([])}}
        
        # Собираем все ключи с вероятностными значениями
        probability_keys = [key for key in props.keys() if key.endswith('_probability')]
        
        for prop, vals in props.items():
            # Пропускаем служебные ключи
            if '_probability_values' in prop or '_probability_stats' in prop:
                continue
                
            if initial_distribution[reg][prop] and len(initial_distribution[reg][prop].get_distribution()) > 0:
                dmin = min(initial_distribution[reg][prop].distribution)
                dmax = max(initial_distribution[reg][prop].distribution)
            
            final_result[reg][prop] = {
                "values": vals.tolist(),
                "stats": {
                    "P90": (initial_stats[reg][prop]["P10"], 90),
                    "P50": (initial_stats[reg][prop]["P50"], 50),
                    "P10": (initial_stats[reg][prop]["P90"], 10),
                    "Mean": (initial_stats[reg][prop]["Mean"]),
                    "Std": (initial_stats[reg][prop]["Std"]),
                    "all": initial_stats[reg][prop].get("all", {}),
                    "distribution_min": dmin,
                    "distribution_max": dmax,
                },
                "distribution": initial_distribution[reg][prop].get_distribution().tolist() if initial_distribution[reg][prop] else []
            }
            
            # Обрабатываем вероятностные значения для каждого результата отдельно
            for prop, vals in props.items():
                if prop.endswith('_probability_values'):
                    base_prop = prop.replace('_probability_values', '')
                   
                    stats_key = base_prop + '_probability_stats'
                    if stats_key in props:
                        prob_stats = props[stats_key]
                        vals_probability = vals
                        if isinstance(vals_probability, ndarray) and len(vals_probability) > 0:
                            vals_probability = nan_to_num(vals_probability, nan=0.)
                            vals_probability[vals_probability < 1e-5] = 0
                        final_result[reg][base_prop + "_result_probability"] = {
                            "values": vals_probability.tolist(),
                            "stats": {
                                "P90": (prob_stats["P90"], 10),
                                "P50": (prob_stats["P50"], 50),
                                "P10": (prob_stats["P10"], 90),
                                "Mean": (prob_stats["Mean"]),
                                "Std": (prob_stats["Std"]),
                                "all": prob_stats.get("all", {}),
                            },
                        }

    return dict(final_result)


def receive_mygeomap(setup_config: dict[str, dict]) -> "Model":
    if "config" in setup_config:
        setup_config["regions"] = setup_config.pop("config")

    return Model.deserialize(setup_config)
