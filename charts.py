import altair as alt
import pandas as pd
import json

def gdp_per_capita_map(data):
    with open("data/world_110m.json", "r") as world_110m_json:
        world_110m = json.load(world_110m_json)

    countries = alt.Data(values=world_110m, format=alt.DataFormat(type='topojson', feature='countries'))

    data['Region '] = data['Region']
    map_select = alt.selection_point(fields=['Region '], on='click', clear='none')

    gdp_per_capita_map = alt.Chart(countries).mark_geoshape(stroke='white', strokeWidth=0.25).encode(
        color=alt.condition(map_select, alt.Color('GDP Per Capita:Q', scale=alt.Scale(range=['skyblue', 'darkblue']), legend=alt.Legend(title='GDP Per Capita ($)', orient='right')), alt.value('lightgray')),
        tooltip=[alt.Tooltip('Name:N', title='Country'), alt.Tooltip('GDP:Q', title='GDP ($B)'), alt.Tooltip('Currency:N', title='Currency'), alt.Tooltip('Area:Q', title='Area (M²)'), alt.Tooltip('Population:Q', title='Population (Million)')]
    ).transform_lookup(
        lookup='id', from_=alt.LookupData(data=data, key='ID',fields=['GDP Per Capita', 'Name', 'GDP', 'Currency', 'Area', 'Population', 'Region '])
    ).project(
        type='naturalEarth1'
    ).properties(
        width=762.5,
        height=425
    ).add_params(map_select)

    return gdp_per_capita_map


def gdp_growth_bar(data):
    gdp_growth_by_subregion = data.groupby(['Subregion', 'Region'], as_index=False)['GDP Growth'].mean().rename(columns={'GDP Growth': 'Mean GDP Growth'})
    gdp_growth_by_subregion['Mean GDP Growth Real'] = gdp_growth_by_subregion['Mean GDP Growth'].round(2)
    gdp_growth_by_subregion['Mean GDP Growth'] = gdp_growth_by_subregion['Mean GDP Growth Real'].astype(str) + '%'

    countries_per_subregion = data.groupby('Subregion').size().reset_index(name='Total Countries')
    gdp_growth_by_subregion = gdp_growth_by_subregion.merge(countries_per_subregion, on='Subregion', how='left')

    con_select = alt.selection_point(fields=['Region'], on='click', clear='none')

    gdp_growth_bar = alt.Chart(gdp_growth_by_subregion).transform_filter('datum.Subregion != null').mark_bar().encode(
        x=alt.X('Mean GDP Growth Real:Q', title='Average GDP Growth (%)', axis=alt.Axis(grid=False)),
        y=alt.Y('Subregion:N', title='', sort='-x'),
        color=alt.condition(con_select, alt.Color('Region:N', scale=alt.Scale(domain=['Africa', 'Asia', 'Americas'],range=['Blue', 'Red', 'Orange']), legend=None), alt.value('lightgray')),
        tooltip=['Region', 'Subregion', 'Mean GDP Growth', 'Total Countries:Q']
    ).properties(
        width=812.5,
        height=425,
        title='GDP Growth in the Global South'
    ).add_params(con_select)

    return gdp_growth_bar

def affiliation_scatter(data):
    data['Economic Stability Score'] = 20 + 5 * ((data['Gov. Budget'] / 2.8) * 0.1 + (data['Current Account'] * 2) * 0.1 - (data['Debt/GDP'] / 61) * 0.1 - (data['Inflation Rate'] / 8.3) * 0.3 - (data['Jobless Rate'] / 7.4) * 0.2 - (data['Interest Rate'] / 7.8) * 0.2).round(2)

    data['GDP Growth '] = data['GDP Growth'].astype(str) + '%'
    data['Inflation Rate '] = data['Inflation Rate'].astype(str) + '%'
    data['Jobless Rate '] = data['Jobless Rate'].astype(str) + '%'
    data['Interest Rate '] = data['Interest Rate'].astype(str) + '%'

    affiliation_text = pd.DataFrame({
        'x': [-6, -6, 16, 16],
        'y': [4, 52, 4, 52],
        'text': ['Stagnant and Unstable Economy', 'Stagnant and Stable Economy', 'Growing and Unstable Economy',
                 'Growing and Stable Economy']
    })
    affiliation_annotations = alt.Chart(affiliation_text).mark_text(align='center', baseline='top', fontWeight='bold', fontStyle='italic', opacity=0.75).encode(
        x='x:Q',
        y='y:Q',
        text='text:N'
    )

    aff_select = alt.selection_point(fields=['Affiliation'], on='click', clear='none')

    affiliation_scatter = alt.Chart(data).mark_point().encode(
        y=alt.Y('Economic Stability Score', title="Economic Stability Score", scale=alt.Scale(domain=[0, 55], clamp=True), axis=alt.Axis(grid=False)),
        x=alt.X('GDP Growth:Q', title='GDP Growth (%)', scale=alt.Scale(domain=[-10, 20], clamp=True), axis=alt.Axis(grid=False)),
        color=alt.condition(aff_select, alt.Color('Affiliation:N', scale=alt.Scale(domain=['G7', 'BRICS', 'ASEAN', 'Unaffiliated'], range=['Blue', 'Red', 'Orange', 'Gray']), legend=alt.Legend(title='Affiliation', orient='right', offset=12.5, symbolSize=200)), alt.value('lightgray')),
        size=alt.condition(aff_select, alt.value(66), alt.value(33)),
        tooltip=[alt.Tooltip('Name:N', title='Country'), 'Economic Stability Score', 'GDP Growth ', 'Inflation Rate ', 'Jobless Rate ', 'Interest Rate ']
    ).properties(
        width=800,
        height=425,
        title="Economic Stability against GDP Growth by Affiliation"
    ).add_params(aff_select)

    affiliation_scatter = (affiliation_annotations + affiliation_scatter).resolve_scale(color='independent')
    return affiliation_scatter


def unemployment_scatter(data):
    unemployment_text = pd.DataFrame({
        'x': [5000, 5000, 85000, 85000],
        'y': [-5, 36, -5, 36],
        'text': ['Low Income, Low Unemployment', 'Low Income, High Unemployment', 'High Income, Low Unemployment',
                 'High Income, High Unemployment']
    })
    unemployment_annotations = alt.Chart(unemployment_text).mark_text(align='center', baseline='top', fontWeight='bold',
                                                                      fontStyle='italic', opacity=0.75).encode(
        x='x:Q',
        y='y:Q',
        text='text:N'
    )

    data['Unemployment Rate'] = data['Jobless Rate'].astype(str) + '%'
    data['GDP Per Capita '] = (data['GDP Per Capita'].round(0)).astype(int).astype(
        str) + '$'

    une_select = alt.selection_point(fields=['Region'], on='click', clear='none')

    unemployment_scatter = alt.Chart(data).mark_circle(clip=True).encode(
        x=alt.X('GDP Per Capita:Q', title='GDP Per Capita', scale=alt.Scale(domain=[-10000, 100000]), axis=alt.Axis(grid=False)),
        y=alt.Y('Jobless Rate:Q', title='Unemployment Rate (%)', scale=alt.Scale(domain=[-10, 40]), axis=alt.Axis(grid=False)),
        color=alt.condition(une_select, alt.Color('Region:N', scale=alt.Scale(domain=['Africa', 'Asia', 'Americas'], range=['Blue', 'Red', 'Orange']), legend=alt.Legend(title='Region', orient='right', offset=12.5, symbolSize=200)), alt.value('lightgray')),
        tooltip=[alt.Tooltip('Name:N', title='Country'), 'Unemployment Rate', 'GDP Per Capita '],
        size=alt.condition(une_select, alt.Size('GDP:Q', scale=alt.Scale(range=[50, 500]), legend=None), alt.value(50))
    ).properties(
        width=812.5,
        height=425,
        title="Unemployment against GDP per Capita in the Global South"
    ).add_params(une_select)

    unemployment_scatter = (unemployment_annotations + unemployment_scatter).resolve_scale(color='independent')
    return unemployment_scatter