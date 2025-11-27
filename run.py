import altair as alt
import pandas as pd
import charts

# Following countries' information manually added to the dataset (source: imf.org IMF Datamapper):
# Czechia
# Democratic Republic of Congo
# Guinea-Bissau
# Eswatini
# North Korea (source: https://www.bok.or.kr/eng/bbs/E0000634/view.do?nttId=10093293&searchCnd=1&searchKwd=&depth2=400417&depth=400417&pageUnit=10&pageIndex=1&programType=newsDataEng&menuNo=400423&oldMenuNo=400417)
# North Macedonia
# Western Sahara - No reliable data, rough estimates used

# GDP Growth added for affiliated countries (source: imf.org IMF Datamapper)

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
gdp_per_capita_map = charts.gdp_per_capita_map(dataset)
gdp_growth_bar = charts.gdp_growth_bar(global_south_dataset)
affiliation_scatter = charts.affiliation_scatter(dataset)
unemployment_scatter = charts.unemployment_scatter(global_south_dataset)

charts = alt.vconcat((gdp_per_capita_map | gdp_growth_bar), (affiliation_scatter | unemployment_scatter)).resolve_scale(color='independent')

# Generate Title #
title_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(strokeWidth=1, color='black').encode(
    y=alt.Y('y:Q', axis=None)
).properties(
    width=1810,
    height=1
)
dashboard = alt.vconcat(title_line, charts).properties(
    title={
        "text": "Exploring the Global Economic Data of 2025",
        "fontSize": 24,
        "subtitle": "Highlighting the Rising Economic Influence of the Global South",
        "subtitleFontSize": 14,
        "subtitleFontStyle": "italic",
        "anchor": "middle"
    }
)

dashboard.save("global_economic_dashboard.html")