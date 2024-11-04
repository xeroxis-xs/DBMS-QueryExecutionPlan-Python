from dash import Dash, html, dcc, callback_context, Output, Input, State
import dash_bootstrap_components as dbc
from interface_components.navbar import navbar
from db.db import Database
from interface_components.graph import Graph
import pandas as pd
import psycopg2
import plotly.graph_objs as go
import feffery_markdown_components as fmc
import json


class Interface:
    def __init__(self):
        self.app = Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
        )
        self.set_layout()
        self.set_callbacks()
        self.db = None
        self.qep = None

    def set_layout(self):
        self.app.layout = html.Div([
            navbar(),
            dbc.Container([
                dbc.Row([
                    html.H2("Query Execution Plan"),
                ], className="my-5"),
                dbc.Row([
                    dbc.Col([
                        html.H5([
                            html.B("Connection")
                        ], className="bg-light text-dark p-3 py-3 rounded-3 mb-3"),
                        dbc.Row([
                            dbc.Label("Host", html_for="host", width=3),
                            dbc.Col(
                                dbc.Input(id="host", placeholder="Enter host", type="text", value="localhost"),
                                width=9,
                            )
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label("Port", html_for="port", width=3),
                            dbc.Col(
                                dbc.Input(id="port", placeholder="Enter port", type="number", value=5433),
                                width=9,
                            )
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label("Database", html_for="dbname", width=3),
                            dbc.Col(
                                dbc.Input(id="dbname", placeholder="Enter database name", type="text",
                                          value="postgres"),
                                width=9,
                            )
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label("User", html_for="user", width=3),
                            dbc.Col(
                                dbc.Input(id="user", placeholder="Enter user", type="text", value="postgres"),
                                width=9,
                            )
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label("Password", html_for="password", width=3),
                            dbc.Col(
                                dbc.Input(id="password", placeholder="Enter password", type="password", value="admin"),
                                width=9,
                            )
                        ], className="mb-3"),
                        dbc.Button(["Connect", html.I(className="bi bi-database-fill-lock ms-2")], id="connect-button",
                                   color="primary", className="my-3"),
                        dbc.Alert(id="connection-status", color="info", is_open=False)
                    ], width=6),

                    dbc.Col([
                        html.H5([
                            html.B("Database Tables")
                        ], className="bg-light text-dark p-3 py-3 rounded-3 mb-3"),
                        dcc.Loading(
                            id="loading-connection",
                            type="default",
                            children=[
                                html.P(id="table-time-taken", className="my-3"),
                                html.Div(
                                    style={"max-height": "400px", "overflow-y": "auto"},
                                    children=[
                                        dbc.Table(
                                            id='table-schemas',
                                            bordered=True,
                                            hover=True,
                                            responsive=True,
                                            striped=True,
                                        )
                                    ]
                                )
                            ]
                        ),
                    ], width=6),
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.H5([
                            html.B("SQL Query Input")
                        ], className="bg-light text-dark p-3 py-3 rounded-3 mb-3"),

                        dbc.Row([
                            dbc.Col(
                                dbc.Textarea(
                                    id="query-input",
                                    placeholder="Enter SQL query",
                                    value="SELECT * FROM customer C,  orders O WHERE C.c_custkey = O.o_custkey AND C.c_custkey <=10"
                                ),
                            ),
                        ], className="mb-3"),

                        dbc.Button(["Execute", html.I(className="bi bi-play-fill ms-2")], id="execute-button",
                                   color="primary", className="my-3", disabled=True),
                        dbc.Alert(
                            id="query-status",
                            color="info",
                            is_open=False,
                        ),

                    ], width=6),
                    dbc.Col([
                        html.H5([
                            html.B("SQL Query Output")
                        ], className="bg-light text-dark p-3 py-3 rounded-3 mb-3"),
                        dbc.Row([
                            dbc.Col(
                                dcc.Loading(
                                    id="loading-query",
                                    type="default",
                                    children=[
                                        html.P(id="query-time-taken", className="my-3"),
                                        html.P(id="query-rows-count", className="my-3"),
                                        html.Div(id="query-output", style={
                                            "max-width": "100%",
                                            "overflow-x": "auto",
                                            "max-height": "400px",
                                            "overflow-y": "auto"
                                        })
                                    ]
                                ),
                            ),
                        ]),

                    ], width=6),
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.H5([
                            html.B("QEP")
                        ], className="bg-light text-dark p-3 py-3 rounded-3 mb-3"),
                        dbc.Button(["Get QEP", html.I(className="bi bi-filetype-json ms-2")], id="qep-button",
                                   color="primary", className="my-3", disabled=True),
                        dbc.Alert(id="qep-status", color="info", is_open=False),
                        dbc.Row([
                            dbc.Col(
                                dcc.Loading(
                                    id="loading-qep",
                                    type="default",
                                    children=[
                                        html.P(id="qep-time-taken", className="my-3"),
                                        fmc.FefferyMarkdown(
                                            id="qep-output",
                                            codeTheme="atom-dark",
                                            codeBlockStyle={"max-height": "500px"},
                                            codeStyle={"font-size": "14px"}
                                        ),
                                    ]
                                ),
                            ),
                        ], className="mb-3"),

                    ], width=6),
                    dbc.Col([
                        html.H5([
                            html.B("QEP Graph")
                        ], className="bg-light text-dark p-3 py-3 rounded-3 mb-3"),
                        dbc.Button(["Show QEP Graph", html.I(className="bi bi-diagram-3-fill ms-2")],
                                   id="show-qep-graph", color="primary", className="my-3", disabled=True),
                        dbc.Alert(id="qep-graph-status", color="info", is_open=False),
                        dbc.Row([
                            dbc.Col(
                                dcc.Loading(
                                    id="loading-qep-graph",
                                    type="default",
                                    children=[
                                        html.Div(id="qep-graph", children=[
                                            dcc.Graph(id="qep-interactive-graph", figure=go.Figure(),
                                                      style={"display": "none"}),
                                        ]),
                                    ]
                                ),

                            ),
                        ], className="mb-3"),
                        dbc.Row(id="dropdown-container", className="mb-3", children=[
                            dbc.Label(f"Select a Node", html_for="dropdown", width=3),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='dropdown',
                                    value='',
                                    disabled=True
                                ),
                                width=6)
                        ]),
                        dbc.Button(["Apply Changes", html.I(className="bi bi-check2-all ms-2")], id="apply-changes-button", color="primary", className="my-3", style={"display": "none"}),
                    ], width=6),
                ]),
                dbc.Row(className="py-5"),
            ]),
        ])

    def set_callbacks(self):
        @self.app.callback(
            Output("connection-status", "children"),
            Output("connection-status", "color"),
            Output("connection-status", "is_open"),
            Output("table-schemas", "children"),
            Output("table-time-taken", "children"),
            Output("qep-button", "disabled"),
            Output("execute-button", "disabled"),
            Input("connect-button", "n_clicks"),
            State("host", "value"),
            State("port", "value"),
            State("dbname", "value"),
            State("user", "value"),
            State("password", "value")
        )
        def connect_to_db(n_clicks, host, port, dbname, user, password):
            if n_clicks is None:
                return "", "info", False, None, "", True, True

            try:
                # Attempt to connect to the PostgreSQL database
                self.db = Database(host, port, dbname, user, password)
                self.db.connect()

                # Analyze the database
                result, analyze_time, error, _ = self.db.analyze()

                # Query to list all tables in the connected database
                tables, time_taken, error, _ = self.db.list_all_tables()
                table_rows = []
                time_taken = time_taken + analyze_time

                for schema, table in tables:
                    columns = []
                    # Get the columns for each table
                    columns_result, time_taken_col, error, _ = self.db.list_columns(schema, table)

                    for row in columns_result:
                        columns.append(row[0])
                    time_taken += time_taken_col

                    # Get the exact number of rows
                    row_count, time_taken_row = self.db.get_rows(schema, table)
                    time_taken += time_taken_row

                    # Create a table row
                    table_rows.append(html.Tr([
                        html.Td(table),
                        html.Td(', '.join(columns)),
                        html.Td(row_count)
                    ]))

                # Define table header
                table_header = [
                    html.Thead(html.Tr([
                        html.Th("Table"),
                        html.Th("Attributes"),
                        html.Th("Rows")
                    ]))
                ]

                # Combine header and body
                table_body = [html.Tbody(table_rows)]

                table_children = table_header + table_body

                return ([html.I(className="bi bi-check-circle-fill me-2"), "Connected successfully! "],
                        "success", True, table_children, f"Time taken: {round(time_taken * 1000)} milliseconds", False,
                        False)
            except psycopg2.OperationalError as e:
                print(f"Connection failed: {e}")
                return ([html.I(className="bi bi-x-octagon-fill me-2"), "Connection failed:",
                         fmc.FefferyMarkdown(markdownStr=f"```sh\n{e}\n```", codeTheme="atom-dark", className="mt-3")],
                        "danger", True, [], "", True, True)

        @self.app.callback(
            Output("query-status", "children"),
            Output("query-status", "color"),
            Output("query-status", "is_open"),
            Output("query-output", "children"),
            Output("query-time-taken", "children"),
            Output("query-rows-count", "children"),
            Input("execute-button", "n_clicks"),
            State("query-input", "value"),
        )
        def execute_query(n_clicks, query):
            if n_clicks is None:
                return "", "info", False, None, "", ""

            try:
                # Execute the query
                result, time_taken, error, rows = self.db.execute_query(query)

                if error:
                    raise psycopg2.Error(error)

                # If the query returns results
                if result:
                    df = pd.DataFrame(result, columns=[desc[0] for desc in self.db.cursor.description])
                    table = dbc.Table.from_dataframe(
                        df,
                        striped=True,
                        bordered=True,
                        hover=True,
                        style={
                            "font-size": "14px",
                            "padding": "2px",
                            "margin": "0",
                        }
                    )
                    return [html.I(className="bi bi-check-circle-fill me-2"),
                            "Query executed successfully!"], "success", True, table, f"Time taken: {round(time_taken * 1000)} milliseconds", f"Rows returned: {rows}"
                else:
                    return [html.I(className="bi bi-check-circle-fill me-2"),
                            "Query executed successfully!"], "success", True, html.P(
                        "Query executed successfully!"), f"Time taken: {round(time_taken * 1000)} milliseconds", "No rows returned"
            except psycopg2.Error as e:
                # Split error message by lines and format with HTML line breaks
                return [
                    html.I(className="bi bi-x-octagon-fill me-2"),
                    "Error executing query:",
                    fmc.FefferyMarkdown(markdownStr=f"```sh\n{str(e)}\n```", codeTheme="atom-dark", className="mt-3")
                ], "danger", True, None, "", ""

        @self.app.callback(
            Output("qep-status", "children"),
            Output("qep-status", "color"),
            Output("qep-status", "is_open"),
            Output("qep-output", "markdownStr"),
            Output("qep-time-taken", "children"),
            Output("show-qep-graph", "disabled"),
            Input("qep-button", "n_clicks"),
            State("query-input", "value"),
        )
        def get_qep(n_clicks, query):
            if n_clicks is None:
                return "", "info", False, None, "", True

            try:
                # Get the query execution plan
                self.qep, time_taken, error = self.db.get_qep(query)

                if error:
                    raise psycopg2.Error(error)

                return [html.I(className="bi bi-check-circle-fill me-2"),
                        "Query execution plan generated successfully!"], "success", True, f"```json\n{self.qep}\n```", f"Time taken: {round(time_taken * 1000)} milliseconds", False
            except psycopg2.Error as e:
                return [html.I(className="bi bi-x-octagon-fill me-2"), "Error generating query execution plan:",
                        fmc.FefferyMarkdown(markdownStr=f"```sh\n{str(e)}\n```", codeTheme="atom-dark",
                                            className="mt-3")], "danger", True, "", "", True

        @self.app.callback(
            Output("qep-graph", "children"),
            Output("qep-graph-status", "children"),
            Output("qep-graph-status", "color"),
            Output("qep-graph-status", "is_open"),
            Input("show-qep-graph", "n_clicks"),
        )
        def show_qep_graph(n_clicks):
            if n_clicks is None:
                return None, "", "info", False

            if self.qep:
                qep_dict = json.loads(self.qep)
                graph = Graph()
                graph.parse_qep(qep_dict)
                # graph.print_graph()
                graph.build_graph()
                return dcc.Graph(id="qep-interactive-graph", figure=graph.plot_graph()), [
                    html.I(className="bi bi-check-circle-fill me-2"),
                    "QEP Graph generated successfully!"], "success", True
            else:
                return None, [html.I(className="bi bi-x-octagon-fill me-2"),
                              "No QEP available to generate graph"], "danger", True

        @self.app.callback(
            Output("dropdown-container", "children"),
            Output("apply-changes-button", "style"),
            Input("qep-interactive-graph", "clickData"),
        )
        def show_dropdown(click_data):
            if click_data:
                print(click_data)
                node_id = click_data['points'][0]['id']
                node_type = click_data['points'][0]['text']

                if node_type == 'Hash Join' or node_type == 'Merge Join' or node_type == 'Nested Loop':
                    return [
                        dbc.Row([
                            dbc.Label(f"Operation", width=3),
                            dbc.Col(children=html.B("Join Operation"), width=9, className="d-flex align-items-center"),
                            ]),
                        dbc.Row([
                            dbc.Label(f"Node ID: {node_id}", html_for="dropdown", width=3),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='dropdown',
                                    options=[
                                        {'label': 'Hash Join', 'value': 'Hash Join'},
                                        {'label': 'Merge Join', 'value': 'Merge Join'},
                                        {'label': 'Nested Loop', 'value': 'Nested Loop'},
                                    ],
                                    value=node_type,
                                ),
                                width=9),
                            ]),
                    ], {"display": "block"}
                elif node_type == 'Seq Scan' or node_type == 'Index Scan' or node_type == 'Bitmap Index Scan':
                    return [
                        dbc.Row([
                            dbc.Label(f"Operation", width=3),
                            dbc.Col(children=html.B("Scan Operation"), width=9, className="d-flex align-items-center"),
                            ]),
                        dbc.Row([
                            dbc.Label(f"Node ID: {node_id}", html_for="dropdown", width=3),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='dropdown',
                                    options=[
                                        {'label': 'Seq Scan', 'value': 'Seq Scan'},
                                        {'label': 'Index Scan', 'value': 'Index Scan'},
                                        {'label': 'Bitmap Index (Multi-index) Scan', 'value': 'Bitmap Index Scan'},
                                    ],
                                    value=node_type,
                                ),
                                width=9),
                            ]),
                    ], {"display": "block"}

                elif node_type == 'Hash' or node_type == 'Sort':
                    return [
                        dbc.Row([
                            dbc.Label(f"Operation", width=3),
                            dbc.Col(children=html.B("Aggregation Operation"), width=9, className="d-flex align-items-center"),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label(f"Node ID: {node_id}", html_for="dropdown", width=3),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='dropdown',
                                    options=[
                                        {'label': 'Hash', 'value': 'Hash'},
                                        {'label': 'Sort', 'value': 'Sort'},
                                    ],
                                    value=node_type,
                                ),
                                width=9),
                            ]),
                    ], {"display": "block"}
                else:
                    return [
                        dbc.Row([
                            dbc.Label(f"Operation", width=3),
                            dbc.Col(children=html.B("Not covered in this project"), width=9, className="d-flex align-items-center"),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label(f"Node {node_id}", html_for="dropdown", width=3),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='dropdown',
                                    options=[
                                        {'label': node_type, 'value': node_type},
                                    ],
                                    value=node_type,
                                ),
                                width=9),
                            ]),
                    ], {"display": "block"}
            else:
                return None, {"display": "none"}

    def run(self):
        self.app.run(debug=True)
