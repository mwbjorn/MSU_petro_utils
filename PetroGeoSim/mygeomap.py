from collections import defaultdict
from PetroGeoSim.models import Model
from numpy import ndarray, nan_to_num, where, isnan
from PetroGeoSim.utils.tornado_diagram import calculate_tornado_data, TORNADO_CONFIG
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def send_mygeomap(model: Model) -> dict[str, dict]:
    """
    Отправляет данные геомодели
    """
    logger.info("Starting send_mygeomap")
    
    initial_result = model.get_all_properties("values", include=("inputs", "results"))
    initial_stats = model.get_all_properties("stats", include=("inputs", "results"))
    initial_distribution = model.get_all_properties("distribution", include=("inputs", "results"))

    final_result = defaultdict(dict)
    for reg, props in initial_result.items():
        for prop, vals in props.items():
            if '_probability_values' in prop or '_probability_stats' in prop:
                continue
                
            if prop in initial_distribution[reg] and initial_distribution[reg][prop] and len(initial_distribution[reg][prop].get_distribution()) > 0:
                dmin = min(initial_distribution[reg][prop].distribution)
                dmax = max(initial_distribution[reg][prop].distribution)
            else:
                dmin = None
                dmax = None
            
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
                "distribution": initial_distribution[reg][prop].get_distribution().tolist() if prop in initial_distribution[reg] and initial_distribution[reg][prop] else []
            }
        
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
                            "P90": (prob_stats["P10"], 90),
                            "P50": (prob_stats["P50"], 50),
                            "P10": (prob_stats["P90"], 10),
                            "Mean": (prob_stats["Mean"]),
                            "Std": (prob_stats["Std"]),
                            "all": prob_stats.get("all", {}),
                        },
                    }
    
    result = dict(final_result)
    
    # Торнадо данные для всех формул
    logger.info(f"TORNADO_CONFIG enabled: {TORNADO_CONFIG['enabled']}")
    
    if TORNADO_CONFIG["enabled"]:
        logger.info("Calculating tornado data...")
        tornado_data = calculate_tornado_data(model)
        if tornado_data:
            result["tornado"] = tornado_data
            logger.info(f"Tornado data added to response with {len(tornado_data.get('tornado_diagrams', {}))} diagrams")
            # Выводим первые несколько ключей для проверки
            diagrams = tornado_data.get('tornado_diagrams', {})
            if diagrams:
                logger.info(f"Tornado diagram keys: {list(diagrams.keys())}")
        else:
            logger.warning("Tornado data calculation returned None")
    else:
        logger.info("Tornado is disabled in config")
    
    logger.info(f"Final result keys: {list(result.keys())}")
    return result

def receive_mygeomap(setup_config: dict[str, dict]) -> "Model":
    if "config" in setup_config:
        setup_config["regions"] = setup_config.pop("config")
    # Удаляем tornado_config если он есть, чтобы не передавать в Model
    if "tornado_config" in setup_config:
        del setup_config["tornado_config"]
    return Model.deserialize(setup_config)