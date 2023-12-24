import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

CSV_NAME = 'results.csv'
data = pd.read_csv(CSV_NAME)

# Convert 'winner' to a binary variable where 'hostiles' = 1 and 'non-hostiles' = 0
data['winner'] = data['winner'].apply(lambda x: 1 if x == 'hostiles' else 0)

# Group by 'dex', 'dice', and 'health', and calculate the mean 'winner' value to get the win rate for hostiles
grouped_data = data.groupby(['dex', 'dice', 'health']).mean().reset_index()

# Create a Dash application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Interactive Heatmap Visualization"),
    dcc.Dropdown(
        id='xaxis-column',
        options=[{'label': i, 'value': i} for i in grouped_data.columns if i != 'winner'],
        value='dex'
    ),
    dcc.Dropdown(
        id='yaxis-column',
        options=[{'label': i, 'value': i} for i in grouped_data.columns if i != 'winner'],
        value='dice'
    ),
    dcc.Dropdown(
        id='filter-dropdown',
        options=[{'label': str(health), 'value': health} for health in sorted(grouped_data['health'].unique())],
        value=grouped_data['health'].median()
    ),
    dcc.Graph(id='heatmap-graph')
])

# Callback for updating the graph
@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('filter-dropdown', 'value')]
)







def update_graph(xaxis_column_name, yaxis_column_name, filter_value):




    # Filter data based on the slider value
    filtered_data = grouped_data[grouped_data['health'] == filter_value]
    
    # Create a heatmap
    fig = px.density_heatmap(filtered_data, x=xaxis_column_name, y=yaxis_column_name, z='winner', nbinsx=max(filtered_data[xaxis_column_name])-min(filtered_data[xaxis_column_name]),nbinsy=max(filtered_data[yaxis_column_name])-min(filtered_data[yaxis_column_name]))
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
