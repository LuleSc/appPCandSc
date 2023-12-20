# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 12:41:58 2023

@author: lucile.schulthe
"""


import dash_bootstrap_components as dbc
from dash import Dash, dcc, Input, Output, Patch,html
import plotly.express as px
import pandas as pd

pd.DataFrame.iteritems = pd.DataFrame.items

# Sample data

file='../data/20231030_Input Outputs.csv'
data= pd.read_csv(file,encoding='ISO-8859-1')
df=pd.DataFrame(data)


# Parallel coordinate

dims = ["Wall Structure", "Wall Insulation", "Glazing", "Frame","Shading Position","WWR",  "Balcony Depth",  "Floor WDR",  "Operational GWP",
          "Facade GWP",  "sDA","Glazing area"]

fig = px.parallel_coordinates(df, color="Glazing area",
                              dimensions=dims,color_continuous_scale=px.colors.sequential.thermal)


# Scatter plot

figScatter_inputs = dict(x="Facade GWP", y="sDA", color="Glazing area", marginal_y="histogram", marginal_x="histogram") 
figScatter = px.scatter(df, **figScatter_inputs)


#%%

# Initialisation de l'application Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
# Mise en page de l'application 
app.layout = html.Div([
        
        dcc.Graph(id="my-graph", figure=fig), # Graphique Parallel Coordinates
        dcc.Graph(id='scatter-plot',figure=figScatter), # Graphique de dispersion
    
        dcc.Store(id='activefilters', data={})
])

#%%
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

# Callback pour récupérer les points sélectionnés
@app.callback(
    Output('my-graph', 'figure'),
    [Input('scatter-plot', 'selectedData')]
)
def update_parallel_coordinates_plot(selectedData):
    if selectedData is None:
        return px.parallel_coordinates(df, color="Glazing area",
                                      dimensions=dims,color_continuous_scale=px.colors.sequential.thermal)
    
    selected_points_x = [point['x'] for point in selectedData['points']]
    selected_points_y = [point['y'] for point in selectedData['points']]
    
    # Utilisez les coordonnées x et y pour filtrer le DataFrame ou effectuer d'autres opérations
    filtered_df = df[df['Facade GWP'].isin(selected_points_x) & df['sDA'].isin(selected_points_y)]

    
    return px.parallel_coordinates(filtered_df, color="Glazing area",
                                  dimensions=dims,color_continuous_scale=px.colors.sequential.thermal)


#%%

# Lancement de l'application
if __name__ == '__main__':
    app.run_server(debug=True)
    # Exportez l'application en HTML

