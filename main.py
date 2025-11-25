import altair as alt
import pandas as pd
import json

# Following countries' Population and GDP manually added to the dataset (source: imf.org IMF Datamapper):
# Czechia - ID:203 Population:10.9 GDP:383
# Democratic Republic of Congo - ID:180 Population:106.55 GDP:82
# Guinea-Bissau - ID:624 Population:2.02 GDP:2.47
# Eswatini - ID:748 Population:1.18 GDP:5
# North Korea - ID:408 Population:26.5 GDP:32 - 2024 Estimated GDP (source: https://www.bok.or.kr/eng/bbs/E0000634/view.do?nttId=10093293&searchCnd=1&searchKwd=&depth2=400417&depth=400417&pageUnit=10&pageIndex=1&programType=newsDataEng&menuNo=400423&oldMenuNo=400417)
# North Macedonia - ID:807 Population:1.81 GDP:19
# Western Sahara - ID:732 Population:0.6 GDP:1 - No reliable data, imputed with rough estimates

dataset = pd.read_csv('mod_country_economics_data.csv')
dataset['GDP Per Capita'] = dataset['GDP'] / dataset['Population']
dataset['Population Density'] = (dataset['Population'] / dataset['Area']) * 1000000
dataset['ID'] = dataset['ID'].astype(int)

global_south_regions = ["Northern Africa", "Southern Asia", "South-Eastern Asia", "Middle Africa", "Eastern Asia",
                        "Western Africa", "Eastern Africa", "Central Asia", "Caribbean", "Western Asia",
                        "Central America", "South America", "Southern Africa"]
global_south_dataset = dataset[dataset["Subregion"].isin(global_south_regions)].copy()

with open("world_110m.json", "r") as world_110m_json:
    world_110m = json.load(world_110m_json)

countries = alt.Data(values=world_110m, format=alt.DataFormat(type='topojson', feature='countries'))

gdp_per_capita_map = (alt.Chart(countries).mark_geoshape(stroke='white', strokeWidth=0.25).encode(
    color=alt.Color('GDP Per Capita:Q', scale=alt.Scale(range=['lightblue', 'darkblue']), title='GDP Per Capita ($B)', legend=alt.Legend(orient='right')))
    .transform_lookup(
        lookup='id',
        from_=alt.LookupData(data=global_south_dataset, key='ID', fields=['GDP Per Capita']))
    .project(
        type='naturalEarth1')
    .properties(
        width=800,
        height=400)
)

gdp_pop_scatter = alt.Chart(global_south_dataset).mark_circle(clip=True).encode(
    x=alt.X('GDP Per Capita:Q', title='GDP Per Capita', scale=alt.Scale(type='log'), axis=alt.Axis(grid=False)),
    y=alt.Y('Jobless Rate:Q', title='Unemployment Rate (%)', scale=alt.Scale(domain=[0, 50]), axis=alt.Axis(grid=False)),
    color=alt.Color('Region:N', scale=alt.Scale(domain=['Africa', 'Asia', 'Americas'], range=['Blue', 'Red', 'Orange']), legend=alt.Legend(title='Region', orient='bottom')),
    size=alt.Size('GDP:Q', scale=alt.Scale(range=[75, 750]), legend=None)).properties(
        width = 1000,
        height = 400
)

continent_bar = alt.Chart(global_south_dataset).transform_filter(
    'datum.Subregion != null'
).mark_bar().encode(
    x=alt.X('mean(GDP Growth):Q', title='Average GDP Growth (%)', axis=alt.Axis(grid=False)),
    y=alt.Y('Subregion:N', title='', sort='-x'),
    color=alt.Color('Region:N', scale=alt.Scale(domain=['Africa', 'Asia', 'Americas'], range=['Blue', 'Red', 'Orange']), legend=None)
).properties(
    width=600,
    height=400,
    title="GDP Growth in the Global South"
)

dashboard = (gdp_per_capita_map | continent_bar) & (gdp_pop_scatter)

dashboard.save("dashboard.html")