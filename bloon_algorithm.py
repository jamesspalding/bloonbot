import pandas as pd
import random

##### Genetic Algorithm #####
# Filter top results by round survived, lives, money
# "Inherit" columns (location, tower, upgrades)
# Row crossover
# Random Row/Col mutations

tower_data = pd.read_csv('data/tower_data.csv')
attempt_data = pd.read_csv('data/attempt_data.csv')