import altair as alt
import pandas as pd
from vega_datasets import data

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
dataset['ID'] = dataset['ID'].astype(int)

countries = alt.topo_feature(data.world_110m.url, 'countries')

gdp_per_capita_map = (alt.Chart(countries).mark_geoshape(stroke='white', strokeWidth=0.25).encode(
    color=alt.Color('GDP Per Capita:Q', scale=alt.Scale(range=['lightblue', 'darkblue']), title='GDP Per Capita ($B)', legend=alt.Legend(orient='right')))
    .transform_lookup(
        lookup='id',
        from_=alt.LookupData(data=dataset, key='ID', fields=['GDP Per Capita']))
    .project(
        type='naturalEarth1')
    .properties(
        width=1000,
        height=500)
)

affiliation_scatter = alt.Chart(dataset).mark_circle().encode(
    x=alt.X('GDP Growth:Q', title='GDP Growth (%)', scale=alt.Scale(domain=[-5, 15])),
    y=alt.Y('Inflation Rate:Q', title='Inflation Rate (%)'),
    color=alt.Color('Affiliation:N', scale=alt.Scale(domain=['G7', 'BRICS', 'ASEAN'], range=['blue', 'darkgreen', 'red']), legend=alt.Legend(title='Affiliation')),
    size=alt.Size('GDP:Q', scale=alt.Scale(range=[50,500]), legend=None)).properties(
        width = 800,
        height = 400
)

dashboard = gdp_per_capita_map & affiliation_scatter

dashboard.save("dashboard.html")