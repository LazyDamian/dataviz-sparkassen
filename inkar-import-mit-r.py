from rpy2.robjects.packages import importr, data
from rpy2 import robjects

# Load R's package
utils = importr('bonn')

# Create a simple R command to sum two numbers
sum_command = 'head( get_themes(geography="KRE") ) '
result = robjects.r(sum_command)

print(result)

