import pandas as pd

dataset = pd.read_csv('country_economics_data.csv')
dataset['Affiliation'] = "''"
dataset.to_csv('mod_countries_economics_data.csv', index=False)