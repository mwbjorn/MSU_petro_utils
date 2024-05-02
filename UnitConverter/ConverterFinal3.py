class MixinLinearConverter:
    """
    Класс-миксин для конвертации и вывода единиц измерения:
    convert принимает value, from_unit, to_unit - единицы измерения и возвращает рассчитанное значение
    format принимает результат метода convert и to_unit (единицу измерения) и возвращает строку с результатом конвертации(округление 6 знаков после запятой) и единицой измерения
    и интересующую нас единицу измерения
    """

    @classmethod
    def convert(cls, value, from_unit, to_unit):
        return value * cls.UNITS[from_unit] / cls.UNITS[to_unit]

    @staticmethod
    def format(value, unit):
        return f'{round(value, 3)} {unit}'

class DensityMixin:
    """
    Класс-миксин реализован для конвертации плотности
    convert принимает value, from_unit, to_unit - единицы измерения и возвращает рассчитанное значение
    format принимает результат метода convert и to_unit (единицу измерения) и возвращает строку с результатом конвертации(округление 6 знаков после запятой) и единицой измерения
    """

    @classmethod
    def convert(cls, value, from_unit, to_unit):
        if to_unit == 'deg API':
            convert_to_g_cm3 = value * cls.UNITS[from_unit] / cls.UNITS['g/cm^3']
            return 141.5/convert_to_g_cm3 - 131.5

        elif from_unit == 'deg API':
            convert_to_g_cm3 = 141.5/(value + 131.5)
            return convert_to_g_cm3 * cls.UNITS['g/cm^3'] / cls.UNITS[to_unit]

        return value * cls.UNITS[from_unit] / cls.UNITS[to_unit]


    @staticmethod
    def format(value, unit):
        return f'{round(value, 3)} {unit}'


class LengthConverter(MixinLinearConverter):
    """
    Класс LengthConverter используется для конвертации длины:
    'm' - метр
    'km'- километр
    'mi' - миля
    'mm' - миллиметр
    'cm' - сантиметр
    'inch' - дюйм
    'feet' - фут
    """
    UNITS = {
        'm': 1,
        'km': 1000,
        'mi': 1609.34,
        'mm': 0.001,
        'cm': 0.01,
        'inch': 0.0254,
        'feet': 0.3048
    }

class AreaConverter(MixinLinearConverter):
    """
    Класс AreaConverter используется для конвертации площади:
    'm^2' - метр квадратный,
    'km^2'- километр квадратный
    'hectare' - гектар
    'mi^2' - миля в квадрате
    'inch^2' - дюйм квадратный
    'feet^2' - футы в квадрате
    'yard^2' - ярд
    'mm^2' - миллиметр в квадрате
    'cm^2' - сантиметр в квадрате
    """
    UNITS = {
        'm^2': 1,
        'km^2': 1e6,
        'hectare': 1e4,
        'mi^2': 2.58999e6,
        'inch^2': 0.00064516,
        'feet^2': 0.092903,
        'yard^2': 0.836127,
        'mm^2': 1e-6,
        'cm^2': 1e-4,
    }

class VolumeConverter(MixinLinearConverter):
    """
    Класс AreaConverter используется для конвертации объема:
    'ml' - миллилитр
    'liter' - литр
    'm^3' - метр кубический
    'feet^3' - фут кубический
    'inch^3' - дюйм кубический
    'yard^3' - дюйм кубический
    'barrel' - баррель
    'gallon' - галлон
    """
    UNITS = {
        'ml': 0.001,
        'liter': 1,
        'm^3': 1000,
        'feet^3': 28.3168,
        'inch^3': 0.0163871,
        'yard^3': 764.555,
        'barrel': 158.987,
        'gallon': 3.78541
    }

class MassWeightConverter(MixinLinearConverter):
    """
    Класс MassWeightConverter используется для конвертации массы(веса):
    'mg' - миллиграмм
    'g' - грамм
    'kg' - килограмм
    'pound' - фунт
    'ounce' - унция
    'metric-ton' - тонна
    """
    UNITS = {
        'mg': 0.001,
        'g': 1,
        'kg': 1000,
        'pound': 453.592,
        'ounce': 28.3495,
        'metric-ton': 1000000
    }

class PressureConverter(MixinLinearConverter):
    """
    Класс PressureConverter используется для конвертации давления:
    'psi': фунт на квадратный дюйм ,
    'bar' - бар
    'Pa' - паскаль
    'kPa' - килопаскаль (паскаль * 10**3)
    'mPa' - миллипаскаль (паскаль * 1e-3)
    'atm' - атмосфера
    'kg/cm^2 - килограмм/сантиметр квадратный
    """
    UNITS = {
        'psi': 6894.76,
        'bar': 100000,
        'Pa': 1,
        'kPa': 1000,
        'mPa': 1e-3,
        'atm': 101325,
        'kg/cm^2': 98066.5
    }

class TimeConverter(MixinLinearConverter):
    """
    Класс TimeConverter используется для конвертации времени:
    'sec' - секунда
    'min' - минута
    'hour' - час
    'day' - день
    'week' - неделя
    'month' - месяц
    'year' - год
    'mln_year' - миллион лет
    """
    UNITS = {
        'sec': 1,
        'min': 60,
        'hour': 3600,
        'day': 86400,
        'week': 604800,
        'month': 2629757,
        'year': 31557600,
        'mln_year': 3.15576*1e+13
    }

class TemperatureConverter:
    """
    Класс TemperatureConverter используется для конвертации температуры:
    'C' - цельсии,
    'K' - кельвин,
    'F' - фаренгейт,
    'R' - ранкин
    convert принимает value, from_unit, to_unit - единицы измерения и возвращает рассчитанное значение
    format принимает результат метода convert и to_unit (единицу измерения) и возвращает строку с результатом конвертации(округление 6 знаков после запятой) и единицой измерения
    и интересующую нас единицу измерения
    """
    UNITS = {
        'C': {'to_C': lambda x: x, 'to_K': lambda x: x + 273.15, 'to_F': lambda x: x * 9/5 + 32, 'to_R': lambda x: (x + 273.15) * 9/5},
        'K': {'to_C': lambda x: x - 273.15, 'to_K': lambda x: x, 'to_F': lambda x: x * 9/5 - 459.67, 'to_R': lambda x: x * 9/5},
        'F': {'to_C': lambda x: (x - 32) * 5/9, 'to_K': lambda x: (x + 459.67) * 5/9, 'to_F': lambda x: x, 'to_R': lambda x: x + 459.67},
        'R': {'to_C': lambda x: (x - 491.67) * 5/9, 'to_K': lambda x: x * 5/9, 'to_F': lambda x: x - 459.67, 'to_R': lambda x: x}
    }

    @staticmethod
    def convert(value, from_unit, to_unit):
        return TemperatureConverter.UNITS[from_unit]['to_' + to_unit](value)

    @staticmethod
    def format(value, unit):
        return f'{value} °{unit}'

class ViscosityConverter(MixinLinearConverter):
    """
    Класс ViscosityConverter используется для конвертации вязкости:
    'poise' - пуаз
    'centipoise' - центи - пуаз
    'Pa.sec': - паскаль/секунду
    'dyne-sec/cm^2' - дина-секунда/сантиметр в квадрате
    'lbm/ft.sec' - фунт/фут*секунду
    'lbm/ft.hr' - фунт/фут*час
    'lbf.sec/ft^2' - фунт - секунда/
    'lbf.sec/in^2' - Pound-force second/фут в квадрате
    'g/cm.sec' - грамм/сантиметр*секунду
    'kg/m.hr' - килограмм/метр*час
    """
    UNITS = {
        'poise': 1,
        'centipoise': 0.01,
        'Pa.sec': 10,
        'dyne-sec/cm^2': 1,
        'lbm/ft.sec': 14.8816,
        'lbm/ft.hr': 0.00413,
        'lbf.sec/ft^2': 478.8025,
        'lbf.sec/in^2': 68947.543,
        'g/cm.sec': 0.01,
        'kg/m.hr': 0.00278
    }

class EnergyConverter(MixinLinearConverter):
    """
    Класс EnergyConverter используется для конвертации энергии:
    'joule' - джоуль
    'Nm' - ньютон*м
    'kjoule' - килоджоуль
    'Gjoule' - гигаджоуль
    'kcal' - килокалории
    'ftlb' - фут-фунт
    'Btu' - British Thermal Unit
    'watt/hr' - ватт/час
    'kw/hr' - киловатт/час
    """
    UNITS = {
        'joule': 1,
        'Nm': 1,
        'kjoule': 1000,
        'Gjoule': 1e+9,
        'kcal': 4184,
        'ftlb': 1.35582,
        'Btu': 1055.056,
        'watt/hr': 3600,
        'kw/hr': 36*(10**5),
    }

class EnergyConverterEV(MixinLinearConverter):
    """
    Класс EnergyConverterEV используется для конвертации энергии электронного заряда:
    'ev' - электронвольт
    'kev' - килоэлектронвольт
    'Gev' - гигаэлектронвольт
    """
    UNITS= {
        'ev': 1,
        'kev': 1000,
        'Gev': 1e+9
    }

class PowerConverter(MixinLinearConverter):
    """
    Класс PowerConverter используется для конвертации мощности:
    'hp' - лошадиная сила
    'joule/sec' - джоуль/секунда
    'Watt' - ватт
    'Btu/hr' - Британская термальная единица в час
    'Btu/min' - Британская термальная единица в минуту
    'kWatt' - киловатт
    'ft.lbf/sec' - фут-фунт сила в секунду
    'ft.lbf/min' - фут-фунт сила в минуту

    Метод convert_energy_time принимает (energy_value - int/float, energy_unit - str, time_value - int/float, time_unit - str)
    и возвращает энергию/время (energy_value/time_value) в новых единицах.
    """
    UNITS = {
        'hp': 745.6999,
        'joule/sec': 1,
        'Watt': 1,
        'Btu/hr': 0.29307,
        'Btu/min': 17.58427,
        'kWatt': 1000,
        'ft.lbf/sec': 1.35582,
        'ft.lbf/min': 0.0226,
    }

    @staticmethod
    def convert_energy_time(energy_value, energy_unit, time_value, time_unit):
        if f'{energy_unit}/{time_unit}' in PowerConverter.UNITS:
            return energy_value / time_value
        raise ValueError(f'Данная конвертация не поддерживается: {energy_unit}/{time_unit}')

class DensityConverter(DensityMixin):
    """
    Класс DensityConverter используется для конвертации плотности:
    'kg/m^3' - кг/м^3
    'g/cm^3' - г/см^3
    'g/ml' - г/мл
    'kg/l' - кг/л
    'g/lit' - г/л
    'pci' - фунт/кубический дюйм
    'ppg' -  фунт/галлон
    'pcf' - фунт/фут^3
    'bbl' - баррель
    'deg API' - градус API
    'psi/ft' - psi/фут
    'kPa/m' - кПа/м
    'bar/m' - бар/м

    Метод convert_mass_volume принимает (mass_value - int/float, mass_unit - str, volume_value - int/float, volume_unit - str)
    и возвращает массовый объем (mass_value/volume_value) в новых единицах.

    Метод convert_pressure_length принимает (pressure_value - int/float, pressure_unit - str, length_value - int/float, length_unit - str)
    и возвращает давление/длину (pressure_value/length_value) в новых единицах.
    """
    UNITS = {
        'kg/m^3': 1,
        'g/cm^3': 1000,
        'g/ml': 1000,
        'kg/l': 1000,
        'g/lit': 1000,
        'pci': 27679.91,
        'ppg': 119.8264,
        'pcf': 16.0185,
        'bbl': 2.85301,
        'deg API': None,
        'psi/ft': 2306.805,
        'kPa/m': 101.9783,
        'bar/m': 10197.838,
    }

    @staticmethod
    def convert_mass_volume(mass_value, mass_unit, volume_value, volume_unit):
        if f'{mass_unit}/{volume_unit}' in DensityConverter.UNITS:
            return mass_value / volume_value
        raise ValueError(f'Данная конвертация не поддерживается: {mass_unit}/{volume_unit}')

    @staticmethod
    def convert_pressure_lenght(pressure_value, pressure_unit, lenght_value, lenght_unit):
        if f'{pressure_unit}/{lenght_unit}' in DensityConverter.UNITS:
            return pressure_value / lenght_value
        raise ValueError(f'Данная конвертация не поддерживается: {pressure_unit}/{lenght_unit}')



class SpeedConverter(MixinLinearConverter):
    """
    Класс SpeedConverter используется для конвертации скорости:
    'm/s' - м/с
    'm/min' - м/мин
    'm/h' - м/час
    'km/h' - км/час
    'ft/s' - фут/сек
    'ft/min' - фут/мин
    'ft/h' - фут/час
    'mi/h' - миля/час
    'knot' - узел (One nautical mile per hour)

    Метод convert_len_time принимает (length_value - int/float, length_unit - str, time_value - int/float, time_unit - str)
    и возвращает скорость (length_value/time_value) в новых единицах.
    """
    UNITS = {
        'm/s': 1,
        'm/min': 0.01667,
        'm/h': 0.00028,
        'km/h': 0.27778,
        'ft/s': 0.3048,
        'ft/min': 0.00508,
        'ft/h': 8.0E-5,
        'mi/h': 0.44704,
        'knot': 0.51444
    }

    @staticmethod
    def convert_len_time(lenght_value, lenght_unit, time_value, time_unit):
        return lenght_value / time_value

class FlowrateVolumetricConverter(MixinLinearConverter):
    """
    Класс FlowrateVolumetricConverter используется для конвертации объемных расходов:

    Доступные единицы:
    - 'lit/hr': литры в час
    - 'lit/min': литры в минуту
    - 'lit/day': литры в день
    - 'm³/min': кубические метры в минуту
    - 'm³/hr': кубические метры в час
    - 'm³/day': кубические метры в день
    - 'gal/min': галлоны в минуту
    - 'gal/hr': галлоны в час
    - 'gal/day': галлоны в день
    - 'ft³/min': кубические футы в минуту
    - 'ft³/hr': кубические футы в час
    - 'ft³/day': кубические футы в день
    - 'Million ft³/day': миллионы кубических футов в день
    - 'bbl/min': баррели в минуту
    - 'bbl/hr': баррели в час
    - 'bbl/day': баррели в день

    Метод convert_vol_time принимает значения (vol_value - int/float, vol_unit - str, time_value - int/float, time_unit - str) и
    конвертирует их в объемный расход (volume rate) в указанных единицах объема и времени.
    """
    UNITS = {
        'lit/hr': 1,
        'lit/min': 60,
        'lit/day': 0.04167,
        'm³/min': 60000,
        'm³/hr': 1000,
        'm³/day': 41.66667,
        'gal/min ': 227.12471,
        'gal/hr': 3.78541,
        'gal/day': 0.15773,
        'ft³/min': 1699.011,
        'ft³/hr': 28.31685,
        'ft³/day': 1.17987,
        'Million ft³/day': 1179868.6,
        'bbl/min' : 9539.238,
        'bbl/hr': 158.9873,
        'bbl/day ': 6.62447,
    }

    @staticmethod
    def convert_vol_time(vol_value, vol_unit, time_value, time_unit):
        if f'{vol_unit}/{time_unit}' in FlowrateVolumetricConverter.UNITS:
            return vol_value/time_value
        raise ValueError(f'Данная конвертация не поддерживается: {vol_unit}/{time_unit}')

class FlowrateMassConverter(MixinLinearConverter):
    """
    Класс FlowrateMassConverter используется для конвертации массовых расходов:

    Доступные единицы:
    - 'kg/hr': килограммы в час
    - 'kg/min': килограммы в минуту
    - 'kg/day': килограммы в день
    - 'Metric ton/min': метрические тонны в минуту
    - 'Metric ton/hr': метрические тонны в час
    - 'Metric ton/day': метрические тонны в день
    - 'lb/min': фунты в минуту
    - 'lb/hr': фунты в час
    - 'lb/day': фунты в день
    - 'Short ton/day': короткие тонны в день
    - 'Long ton/day': длинные тонны в день

    Метод convert_mass_time принимает значения (mass_value - int/float, mass_unit - str, time_value - int/float, time_unit - str) и
    конвертирует их в массовый расход (mass rate) в указанных единицах массы и времени.
    """
    UNITS = {
        'kg/hr': 1,
        'kg/min': 60,
        'kg/day': 0.04167,
        'Metric ton/min': 60000,
        'Metric ton/hr': 1000,
        'Metric ton/day': 41.66667,
        'lb/min ': 27.21554,
        'lb/hr': 0.45359,
        'lb/day': 0.0189,
        'Short ton/day': 37.79936,
        'Long ton/day': 42.33529
    }
    @staticmethod
    def convert_mass_time(mass_value, mass_unit, time_value, time_unit):
        if f'{mass_unit}/{time_unit}' in FlowrateMassConverter.UNITS:
            return mass_value/time_value
        raise ValueError(f'Данная конвертация не поддерживается: {mass_unit}/{time_unit}')


v = VolumeConverter.convert(22.02, 'cm^3', 'mm^3')

print(VolumeConverter.format(v, 'mm^3'))




