prefixes = ['sph','vpd','pr','rmin','rmax','srad','tmmn','tmmx','vs','th','pet',
            'etr','fm100','fm1000','bi','erc']
label_dict = {'sph': 'specific humidity',
 'vpd': 'mean vapor pressure deficit',
 'pr': 'precipitation amount',
 'rmin': 'min relative humidity',
 'rmax': 'max relative humidity',
 'srad': 'surface downwelling shortwave flux in air',
 'tmmn': 'min air temperature',
 'tmmx': 'max air temperature',
 'vs': 'wind speed',
 'th': 'wind from direction',
 'pet': 'potential evapotranspiration',
 'etr': 'reference evapotranspiration',
 'fm100': 'dead fuel moisture 100hr',
 'fm1000': 'dead fuel moisture 1000hr',
 'bi': 'burning index',
 'erc': 'energy release component',
 'pdsi': 'palmer drought severity index'}
primary_variables = {'sph': 'specific humidity',
 'pr': 'precipitation amount',
 'rmin': 'min relative humidity',
 'rmax': 'max relative humidity',
 'srad': 'surface downwelling shortwave flux in air',
 'tmmn': 'min air temperature',
 'tmmx': 'max air temperature',
 'vs': 'wind speed',
 'th': 'wind from direction'}
derived_variables = {'vpd': 'mean vapor pressure deficit',
 'pet': 'potential evapotranspiration',
 'etr': 'reference evapotranspiration',
 'fm100': 'dead fuel moisture 100hr',
 'fm1000': 'dead fuel moisture 1000hr',
 'bi': 'burning index',
 'erc': 'energy release component'} #,
#  'pdsi': 'palmer drought severity index'}
sensitive_pop = ['Asthma','LowBirtWt','Cardiovas']
socioecon_pop = ['Educatn','Ling_Isol', 'Poverty', 'Unempl', 'HousBurd']
all_factors = sensitive_pop + socioecon_pop

random_seed = 37126 #Chosen randomly on 4/27/2022