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

# Area and Currency also manually added for countries in the Global South

dataset = pd.read_csv('mod_country_economics_data.csv')
dataset['GDP Per Capita'] = (dataset['GDP'] * 1000000000) / (dataset['Population'] * 1000000)
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
    color=alt.Color('GDP Per Capita:Q', scale=alt.Scale(range=['lightblue', 'darkblue']), title='GDP Per Capita ($)', legend=alt.Legend(orient='right')),
    tooltip=[alt.Tooltip('Name:N', title='Country'), alt.Tooltip('GDP:Q', title='GDP ($B)'), alt.Tooltip('Currency:N', title='Currency'), alt.Tooltip('Area:Q', title='Area (M²)'), alt.Tooltip('Population:Q', title='Population (Million)')]
).transform_lookup(
        lookup='id',
        from_=alt.LookupData(data=global_south_dataset, key='ID', fields=['GDP Per Capita', 'Name', 'GDP', 'Currency', 'Area', 'Population'])
).project(
        type='naturalEarth1'
).properties(
        width=800,
        height=400)
)

unemployment_text = pd.DataFrame({
    'x': [5000, 5000, 85000, 85000],
    'y': [-5, 36, -5, 36],
    'text': ['Low Income, Low Unemployment', 'Low Income, High Unemployment', 'High Income, Low Unemployment', 'High Income, High Unemployment']
})
unemployment_annotations = alt.Chart(unemployment_text).mark_text(align='center', baseline='top', fontWeight='bold', fontStyle='italic').encode(
    x='x:Q',
    y='y:Q',
    text='text:N'
)

global_south_dataset['Unemployment Rate'] = global_south_dataset['Jobless Rate'].astype(str) + '%'
global_south_dataset['GDP Per Capita '] = global_south_dataset['GDP Per Capita'].round(2)

unemployment_scatter = alt.Chart(global_south_dataset).mark_circle(clip=True).encode(
    x=alt.X('GDP Per Capita:Q', title='GDP Per Capita', scale=alt.Scale(domain=[-10000, 100000]), axis=alt.Axis(grid=False)),
    y=alt.Y('Jobless Rate:Q', title='Unemployment Rate (%)', scale=alt.Scale(domain=[-10, 40]), axis=alt.Axis(grid=False)),
    color=alt.Color('Region:N', scale=alt.Scale(domain=['Africa', 'Asia', 'Americas'], range=['Blue', 'Red', 'Orange']), legend=alt.Legend(title='Region', orient='right', offset=12.5, symbolSize=200)),
    tooltip=[alt.Tooltip('Name:N', title='Country'), 'Unemployment Rate', 'GDP Per Capita '],
    size=alt.Size('GDP:Q', scale=alt.Scale(range=[50, 500]), legend=None)
).properties(
        width = 1000,
        height = 400
)

unemployment_chart = (unemployment_annotations + unemployment_scatter).resolve_scale(color='independent')

gdp_growth_by_subregion = global_south_dataset.groupby(['Subregion', 'Region'], as_index=False)['GDP Growth'].mean().rename(columns={'GDP Growth': 'Mean GDP Growth'})
gdp_growth_by_subregion['Mean GDP Growth Real'] = gdp_growth_by_subregion['Mean GDP Growth'].round(2)
gdp_growth_by_subregion['Mean GDP Growth'] = gdp_growth_by_subregion['Mean GDP Growth Real'].astype(str) + '%'

continent_bar = alt.Chart(gdp_growth_by_subregion).transform_filter(
    'datum.Subregion != null'
).mark_bar().encode(
    x=alt.X('Mean GDP Growth Real:Q', title='Average GDP Growth (%)', axis=alt.Axis(grid=False)),
    y=alt.Y('Subregion:N', title='', sort='-x'),
    color=alt.Color('Region:N', scale=alt.Scale(domain=['Africa', 'Asia', 'Americas'], range=['Blue', 'Red', 'Orange']), legend=None),
    tooltip=['Region', 'Subregion', 'Mean GDP Growth']
).properties(
    width=700,
    height=400,
    title='GDP Growth in the Global South'
)

metrics = [
    "Interest Rate",
    "Inflation Rate",
    "Jobless Rate",
    "Gov. Budget",
    "Debt/GDP",
    "Current Account"
]

affiliation_dataset = dataset[dataset['Affiliation'].isin(['G7', 'BRICS', 'ASEAN'])].copy()
affiliation_dataset['Economic Stability Score'] = 15+5*((affiliation_dataset['Gov. Budget']/2.8)*0.1 + (affiliation_dataset['Current Account']*2)*0.1 - (affiliation_dataset['Debt/GDP']/61)*0.1 - (affiliation_dataset['Inflation Rate']/8.3)*0.3 - (affiliation_dataset['Jobless Rate']/7.4)*0.2 - (affiliation_dataset['Interest Rate']/7.8)*0.2).round(2)
affiliation_dataset['GDP Growth '] = affiliation_dataset['GDP Growth'].astype(str) + '%'
affiliation_dataset['Inflation Rate '] = affiliation_dataset['Inflation Rate'].astype(str) + '%'
affiliation_dataset['Jobless Rate '] = affiliation_dataset['Jobless Rate'].astype(str) + '%'
affiliation_dataset['Interest Rate '] = affiliation_dataset['Interest Rate'].astype(str) + '%'

affiliation_text = pd.DataFrame({
    'x': [-2, -2, 12, 12],
    'y': [4, 32.5, 4, 32.5],
    'text': ['Stagnant and Unstable Economy', 'Stagnant and Stable Economy', 'Growing and Unstable Economy', 'Growing and Stable Economy']
})
affiliation_annotations = alt.Chart(affiliation_text).mark_text(align='center', baseline='top', fontWeight='bold', fontStyle='italic').encode(
    x='x:Q',
    y='y:Q',
    text='text:N'
)

affiliation_scatter = alt.Chart(affiliation_dataset).mark_point(size=60).encode(
    y=alt.Y('Economic Stability Score', title="Economic Stability Score", scale=alt.Scale(domain=[0, 35]), axis=alt.Axis(grid=False)),
    x=alt.X('GDP Growth:Q', title='GDP Growth', scale=alt.Scale(domain=[-5, 15]), axis=alt.Axis(grid=False)),
    color=alt.Color('Affiliation', scale=alt.Scale(domain=['G7', 'BRICS', 'ASEAN'], range=['Blue', 'Red', 'Orange']), legend=alt.Legend(title='Affiliation', orient='right', offset=12.5, symbolSize=200)),
    tooltip=[alt.Tooltip('Name:N', title='Country'), 'Economic Stability Score', 'GDP Growth ', 'Inflation Rate ', 'Jobless Rate ', 'Interest Rate ']
).properties(
    width=575,
    height=400,
    title="G7 vs BRICS vs ASEAN: Economic Stability against GDP Growth"
)

affiliation_chart = (affiliation_annotations + affiliation_scatter).resolve_scale(color='independent')

title_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
    strokeWidth=1,
    color='black'
).encode(
    y=alt.Y('y:Q', axis=None)
).properties(
    width=1750,
    height=1
)

charts = alt.vconcat((gdp_per_capita_map | continent_bar), (unemployment_chart | affiliation_chart)).resolve_scale(color='independent')

dashboard = alt.vconcat(title_line, charts).properties(
    title={
        "text": "Exploring the Economics of the Global South in 2025",
        "fontSize": 24,
        "anchor": "middle"
    }
)

dashboard.save("dashboard.html")