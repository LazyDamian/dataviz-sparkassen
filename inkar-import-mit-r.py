from rpy2.robjects.packages import importr, data
from rpy2 import robjects

# Load R's package
utils = importr('bonn')


sum_command = 'get_geographies()'
result = robjects.r(sum_command)

print(result)


# Create a simple R command to sum two numbers
sum_command = '( get_themes(geography="RBZ") ) '
result = robjects.r(sum_command)

print(result)

sum_command = '( get_variables(theme="011", geography="RBZ")  ) '
result = robjects.r(sum_command)

print(result)


sum_command = '( get_data(variable="12", geography="KRE", time="2023")  ) '
result = robjects.r(sum_command)

print(result)


sum_command = '( get_data(variable="12", geography="KRE", time="2023", primarykey="01002")  ) '
result = robjects.r(sum_command)


'''011
Arbeitslosigkeit                         Allgemein

022
Bauen und Wohnen      Gebäude- und Wohnungsbestand

033
Beschäftigung und Erwerbstätigkeit           Atypische Beschäftigung

041
Bevölkerung                    Altersstruktur

090
Öffentliche Finanzen              Öffentliche Finanzen

060
Privateinkommen, Private Schulden Privateinkommen, Private Schulden

121
Sozialleistungen                Leistungsempfänger

142
Wirtschaft          Wirtschaftliche Leistung'''