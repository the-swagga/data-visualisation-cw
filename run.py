import altair as alt
import pandas as pd
import charts

# Following countries' Population and GDP manually added to the dataset (source: imf.org IMF Datamapper):
# Czechia - ID:203 Population:10.9 GDP:383
# Democratic Republic of Congo - ID:180 Population:106.55 GDP:82
# Guinea-Bissau - ID:624 Population:2.02 GDP:2.47
# Eswatini - ID:748 Population:1.18 GDP:5
# North Korea - ID:408 Population:26.5 GDP:32 - 2024 Estimated GDP (source: https://www.bok.or.kr/eng/bbs/E0000634/view.do?nttId=10093293&searchCnd=1&searchKwd=&depth2=400417&depth=400417&pageUnit=10&pageIndex=1&programType=newsDataEng&menuNo=400423&oldMenuNo=400417)
# North Macedonia - ID:807 Population:1.81 GDP:19
# Western Sahara - ID:732 Population:0.6 GDP:1 - No reliable data, imputed with rough estimates

# Area and Currency also manually added for countries in the Global South


# Read Dataset from CSV and Pre-Process #
dataset = pd.read_csv('data/mod_country_economics_data.csv')
dataset['GDP Per Capita'] = (dataset['GDP'] * 1000000000) / (dataset['Population'] * 1000000)
dataset['Population Density'] = (dataset['Population'] / dataset['Area']) * 1000000
dataset['ID'] = dataset['ID'].astype(int)
global_south_regions = ["Northern Africa", "Southern Asia", "South-Eastern Asia", "Middle Africa", "Eastern Asia",
                        "Western Africa", "Eastern Africa", "Central Asia", "Caribbean", "Western Asia",
                        "Central America", "South America", "Southern Africa"]
global_south_dataset = dataset[dataset["Subregion"].isin(global_south_regions)].copy()

# Generate Charts #
gdp_per_capita_map = charts.gdp_per_capita_map(global_south_dataset)
unemployment_scatter = charts.unemployment_scatter(global_south_dataset)
gdp_growth_bar = charts.gdp_growth_bar(global_south_dataset)
affiliation_scatter = charts.affiliation_scatter(global_south_dataset)

charts = alt.vconcat((gdp_per_capita_map | gdp_growth_bar), (affiliation_scatter | unemployment_scatter)).resolve_scale(color='independent')

# Generate Title #
title_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(strokeWidth=1, color='black').encode(
    y=alt.Y('y:Q', axis=None)
).properties(
    width=1925,
    height=1
)
dashboard = alt.vconcat(title_line, charts).properties(
    title={
        "text": "Exploring the Economics of the Global South in 2025",
        "fontSize": 24,
        "anchor": "middle"
    }
)

dashboard.save("dashboard.html")