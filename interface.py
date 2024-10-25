from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from interface_components.navbar import navbar
import plotly.express as px
import pandas as pd


class Interface:
    def __init__(self):
        self.app = Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        self.df = self.read_data()
        self.set_layout()
        self.set_callbacks()

    def read_data(self):
        df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
        return df

    def set_layout(self):
        self.app.layout = html.Div([
            navbar(),
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H1(children='Query Execution Plan', style={'textAlign':'center'})
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(self.df.country.unique(), 'Canada', id='dropdown-selection')
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='graph-content')
                    ])
                ])
            ]),
        ])



    def set_callbacks(self):
        @self.app.callback(
            Output('graph-content', 'figure'),
            Input('dropdown-selection', 'value')
        )
        def update_graph(value):
            dff = self.df[self.df.country == value]
            return px.line(dff, x='year', y='pop')

    def run(self):
        self.app.run(debug=True)
        print('Interface run')
