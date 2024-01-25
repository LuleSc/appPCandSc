# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 12:41:58 2023

@author: lucile.schulthe
"""


import dash_bootstrap_components as dbc
from dash import Dash, dcc, Input, Output, Patch,html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

pd.DataFrame.iteritems = pd.DataFrame.items

# Sample data

#data = pd.read_csv("../data/database.csv",encoding='ISO-8859-1')
data = pd.read_csv("../data/database1.csv.gzip", compression="gzip")
#file='../data/20240110_SFH database.csv'
# data= pd.read_csv(file,encoding='ISO-8859-1')
df=pd.DataFrame(data)


# Read data from the first CSV file (X data)
file='../data/20231018_Sunburst data.csv'
data1= pd.read_csv(file,encoding='ISO-8859-1')
df1= pd.DataFrame(data1)

#sunburst
fig_sunburst = px.sunburst(df1, path=['impact', 'category', 'component'], values='value')

# Parallel coordinate

dims = ['Facade orientation','Wall structure type','Facade cladding type','Wall insulation type',
'Glazing type','Frame type','Shading type','WWR',
 'WDR','DoL','Slab structure type','Building U', 'Heating system',
'PV %','Underground%','Climate','Context',
'OI','Facade EI', 'sDA','Glazing area']


dimswithname=list([
            dict(label = 'Orientation', tickvals = [1,2,3,4], ticktext = ['S', 'N-S', 'N-S-W', 'N-S-W-E'], values = df['Facade orientation']),
            dict(label = 'Wall_str', tickvals = [1,2,3,4], ticktext = ['Concrete', 'Brick', 'MassiveWood', 'WoodFramed'], values = df['Wall structure type']),
            dict(label = 'Fac_clad', tickvals = [1,2,3,4], ticktext = ['Min_plast', 'Cem_plast', 'Wood', 'Fibrocement'], values = df['Facade cladding type']),
            dict(label = 'Wall_ins', tickvals = [1,2,3,4], ticktext = ['Straw', 'Cellulose', 'Glass wool', 'EPS'], values = df['Wall insulation type']),
            dict(label = 'Glazing', tickvals = [1,2,3,4], ticktext = ['Double, 24 tmm', 'Double, 18 mm', 'Triple 40 mm', 'Triple 36 mm'], values = df['Glazing type']),
            dict(label = 'Frame', tickvals = [1,2,3,4], ticktext = ['Wood', 'Wood-Alu', 'Alu', 'PVC'], values = df['Frame type']),
            dict(label = 'Shading', tickvals = [1,2,3,4], ticktext = ['No shading', 'Projection','Venetian', 'Roller'], values = df['Shading type']),
            dict(label = 'WWR', tickvals = [1,2,3,4], ticktext = ['20%', '30%', '40%', '50%'], values = df['WWR']),
            dict(label = 'WDR', tickvals = [1,2,3,4], ticktext = ['0.8', '1', '1.2', '1.4'], values = df['WDR']),
            dict(label = 'Loggia D', tickvals = [1,2,3,4], ticktext = ['-2.4', '-1.2', '0', '1.2'], values = df['DoL']),
            dict(label = 'Slab_str', tickvals = [1,2,3,4], ticktext = ['Concrete', 'Wood', 'Wood-concrete', 'Metal-deck'], values = df['Slab structure type']),
            dict(label = 'U-value', tickvals = [1,2,3,4], ticktext = ['0.1', '0.15', '0.2', '0.25'], values = df['Building U']),
            dict(label = 'Heating', tickvals = [1,2,3,4], ticktext = ['Heat pump', 'District heat.', 'Biomass', 'Oil'], values = df['Heating system']),
            dict(label = 'PV%', tickvals = [1,2,3,4], ticktext = ['0%', '50%', '100%', '100%+S fac.'], values = df['PV %']),
            dict(label = 'Underground%', tickvals = [1,2,3,4], ticktext = ['0%', '33%', '66%', '100%'], values = df['Underground%']),
            dict(label = 'Climate', tickvals = [1,2,3,4], ticktext = ['Fribourg', 'Zurich', 'Zermatt', 'Lugano'], values = df['Climate']),
            dict(label = 'OI',  values = df['OI']),
            dict(label = 'Facade EI',  values = df['Facade EI']),
            dict(label = 'sDA',  values = df['sDA']),
            dict(label = 'Glazing area',range = [min(df['Glazing area']),max(df['Glazing area'])],  values = df['Glazing area']),
            ])


fig=go.Figure(go.Parcoords(
    line=dict(color=df['Glazing area'], colorscale='Thermal', showscale=False),
    dimensions=dimswithname))


# Scatter plot

figScatter_inputs = dict(x="Facade EI", y="sDA", color="Glazing area", marginal_y="histogram", marginal_x="histogram") 
figScatter = px.scatter(df, **figScatter_inputs)



#%%


# Initialisation de l'application Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Mise en page de l'application 
app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="my-graph", figure=fig),  # Parallel Coordinates plot
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="scatter-plot", figure=figScatter),  # Scatter plot
        ], width=7),  # Adjusted width
        dbc.Col([
            dcc.Graph(id="sunburst", figure=fig_sunburst),  # Sunburst plot
        ], width=5),  # Adjusted width
    ]),
    dcc.Store(id='activefilters', data={}),
])

#%%

@app.callback(
    Output('sunburst', 'figure'),
    [Input('scatter-plot', 'selectedData'),
     Input("activefilters", "data")]
)
def update_sunburst_plot(scatter_selectedData, parallel_selectedData):
    if scatter_selectedData is None and parallel_selectedData is None:
        return px.sunburst(df1, path=['impact', 'category', 'component'], values='value')

    selected_points_x = []
    selected_points_y = []

    if scatter_selectedData:
        selected_points_x += [point['x'] for point in scatter_selectedData['points']]
        selected_points_y += [point['y'] for point in scatter_selectedData['points']]
        filtered_df = df[df['Facade EI'].isin(selected_points_x) & df['sDA'].isin(selected_points_y)]
    else: 
        filtered_df=df

    if parallel_selectedData:
        dff = filtered_df.copy()
        for col in parallel_selectedData:
            if parallel_selectedData[col]:
                rng = parallel_selectedData[col][0]
                if isinstance(rng[0], list):
                    # if multiple choices combine df
                    dff3 = pd.DataFrame(columns=df.columns)
                    for i in rng:
                        dff2 = dff[dff[col].between(i[0], i[1])]
                        dff3 = pd.concat([dff3, dff2])
                    dff = dff3
                else:
                    # if one choice
                    dff = dff[dff[col].between(rng[0], rng[1])]
    else:
        dff=filtered_df
        
    df1['value']=[dff['Heating'].mean(),dff['Equipments'].mean(),dff['Hot water'].mean(),dff['Lighting'].mean(),dff['Ventilation'].mean(),dff['Slab structure'].mean(),dff['Slab finishing'].mean(),dff['Slab insulation'].mean(),dff['Wall structure'].mean(),dff['Wall insulation'].mean(),dff['Facade cladding'].mean(),dff['Glazing'].mean(),
                          dff['Shading'].mean(),dff['Frame'].mean(),dff['Heating installations'].mean(),dff['Ventilation installations'].mean(),dff['Electrical installations'].mean(),dff['Sanitary installations'].mean(),dff['Interior walls and finishing'].mean(),dff['Core walls'].mean(),dff['Pillars'].mean(),dff['Foundation'].mean(),dff['Underground roof'].mean(),dff['Peripheral walls'].mean(),
                         dff['Roof covering'].mean(),dff['Roof structure'].mean(),dff['Roof insulation'].mean(),dff['Shielding walls'].mean(),dff['Excavation'].mean()
                           ]
            
    return px.sunburst(df1, path=['impact', 'category', 'component'], values='value')





@app.callback(
    Output('scatter-plot', 'figure'),
    Input("activefilters", "data")
)
def update_scatter_plot(data):

    if data:
        dff = df.copy()
        for col in data:
            if data[col]:
                rng = data[col][0]
                if isinstance(rng[0], list):
                    # if multiple choices combine df
                    dff3 = pd.DataFrame(columns=df.columns)
                    for i in rng:
                        dff2 = dff[dff[col].between(i[0], i[1])]
                        dff3 = pd.concat([dff3, dff2])
                    dff = dff3
                else:
                    # if one choice
                    dff = dff[dff[col].between(rng[0], rng[1])]
        return px.scatter(dff, **figScatter_inputs)
    return px.scatter(df, **figScatter_inputs)


@app.callback(
    Output('activefilters', 'data'),
    Input("my-graph", "restyleData")
)
def updateFilters(data):
    if data:
        key = list(data[0].keys())[0]
        col = dims[int(key.split('[')[1].split(']')[0])]
        newData = Patch()
        newData[col] = data[0][key]
        return newData
    return {}

#%%
# update à partir du scatter plot:
# Callback pour récupérer les points sélectionnés
@app.callback(
    Output('my-graph', 'figure'),
    [Input('scatter-plot', 'selectedData')]
)
def update_parallel_coordinates_plot_SC(selectedData):
    if selectedData is None:
        fig.update_traces(
        line=dict(color=df['Glazing area'], colorscale='Thermal', showscale=False),
        dimensions=dimswithname)
        
        return fig
    
    selected_points_x = [point['x'] for point in selectedData['points']]
    selected_points_y = [point['y'] for point in selectedData['points']]
    
    # Utilisez les coordonnées x et y pour filtrer le DataFrame ou effectuer d'autres opérations
    filtered_df = df[df['Facade EI'].isin(selected_points_x) & df['sDA'].isin(selected_points_y)]
    dimswithname1=list([
                dict(label = 'Orientation', tickvals = [1,2,3,4], ticktext = ['S', 'N-S', 'N-S-W', 'N-S-W-E'], values = filtered_df['Facade orientation']),
                dict(label = 'Wall_str', tickvals = [1,2,3,4], ticktext = ['Concrete', 'Brick', 'MassiveWood', 'WoodFramed'], values = filtered_df['Wall structure type']),
                dict(label = 'Fac_clad', tickvals = [1,2,3,4], ticktext = ['Min_plast', 'Cem_plast', 'Wood', 'Fibrocement'], values = filtered_df['Facade cladding type']),
                dict(label = 'Wall_ins', tickvals = [1,2,3,4], ticktext = ['Straw', 'Cellulose', 'Glass wool', 'EPS'], values = filtered_df['Wall insulation type']),
                dict(label = 'Glazing', tickvals = [1,2,3,4], ticktext = ['Double, 24 mm', 'Double, 18 mm', 'Triple 40 mm', 'Triple 36 mm'], values = filtered_df['Glazing type']),
                dict(label = 'Frame', tickvals = [1,2,3,4], ticktext = ['Wood', 'Wood-Alu', 'Alu', 'PVC'], values = filtered_df['Frame type']),
                dict(label = 'Shading', tickvals = [1,2,3,4], ticktext = ['No shading', 'Projection','Venetian', 'Roller'], values = filtered_df['Shading type']),
                dict(label = 'WWR', tickvals = [1,2,3,4], ticktext = ['20%', '30%', '40%', '50%'], values = filtered_df['WWR']),
                dict(label = 'WDR', tickvals = [1,2,3,4], ticktext = ['0.8', '1', '1.2', '1.4'], values = filtered_df['WDR']),
                dict(label = 'Loggia D', tickvals = [1,2,3,4], ticktext = ['-2.4', '-1.2', '0', '1.2'], values = filtered_df['DoL']),
                dict(label = 'Slab_str', tickvals = [1,2,3,4], ticktext = ['Concrete', 'Wood', 'Wood-concrete', 'Metal-deck'], values = filtered_df['Slab structure type']),
                dict(label = 'U-value', tickvals = [1,2,3,4], ticktext = ['0.1', '0.15', '0.2', '0.25'], values = filtered_df['Building U']),
                dict(label = 'Heating', tickvals = [1,2,3,4], ticktext = ['Heat pump', 'District heat.', 'Biomass', 'Oil'], values = filtered_df['Heating system']),
                dict(label = 'PV%', tickvals = [1,2,3,4], ticktext = ['0%', '50%', '100%', '100%+S fac.'], values = filtered_df['PV %']),
                dict(label = 'Underground%', tickvals = [1,2,3,4], ticktext = ['0%', '33%', '66%', '100%'], values = filtered_df['Underground%']),
                dict(label = 'Climate', tickvals = [1,2,3,4], ticktext = ['Fribourg', 'Zurich', 'Zermatt', 'Lugano'], values = filtered_df['Climate']),
                dict(label = 'OI',  values = filtered_df['OI']),
                dict(label = 'Facade EI',  values = filtered_df['Facade EI']),
                dict(label = 'sDA',  values = filtered_df['sDA']),
                dict(label = 'Glazing area',range = [min(df['Glazing area']),max(df['Glazing area'])],  values = filtered_df['Glazing area']),
                ])
    
    
    fig.update_traces(
    line=dict(color=filtered_df['Glazing area'], colorscale='Thermal', showscale=False),
    dimensions=dimswithname1
)
    
    return fig


#%%

# Lancement de l'application
if __name__ == '__main__':
    app.run_server(debug=True)

