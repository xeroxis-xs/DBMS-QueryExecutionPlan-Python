from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
from interface_components.navbar import navbar
from interface_components.graph_plot import GraphPlot
from db.db import Database
from db.query_list import query_template_list
from preprocessing import Graph
import pandas as pd
import psycopg2
import plotly.graph_objs as go
import feffery_markdown_components as fmc
import json
from whatif import whatif_query


class Interface:
    def __init__(self):
        self.app = Dash(
            __name__,
            external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP],
        )
        self.set_layout()
        self.set_callbacks()
        self.db = None
        self.qep = None
        self.qep_cost = None
        self.qep_rows = None
        self.modified_qep = None
        self.modified_qep_cost = None

    def set_layout(self):
        self.app.layout = html.Div([
            navbar(),
            dbc.Container([
                dbc.Row([
                    html.H3("DBMS Query Execution Plan"),
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
                                dbc.Input(id="port", placeholder="Enter port", type="number", value=5432),
                                width=9,
                            )
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Label("Database", html_for="dbname", width=3),
                            dbc.Col(
                                dbc.Input(id="dbname", placeholder="Enter database name", type="text",
                                          value="TPC-H"),
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
                                    style={"maxHeight": "400px", "overflowY": "auto"},
                                    children=[
                                        dbc.Table(
                                            id='table-schemas',
                                            bordered=True,
                                            hover=True,
                                            responsive=True,
                                            striped=True,
                                            style={
                                                "fontSize": "14px",
                                                "padding": "2px",
                                                "margin": "0",
                                                "whiteSpace": "nowrap",
                                                "overflow": "hidden",
                                                "textOverflow": "ellipsis",
                                            }
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
                            dbc.Label("Query Template", html_for="query-template", className="mb-3"),
                            dbc.Col(
                                dbc.Select(
                                    id="query-template",
                                    placeholder="Select a query template",
                                    value=query_template_list[0]["value"],
                                    options=query_template_list,
                                ),
                            )
                        ], className="mb-3"),

                        dbc.Row([
                            dbc.Label("Query", html_for="query-input", className="mb-3"),
                            dbc.Col(
                                dbc.Textarea(
                                    id="query-input",
                                    placeholder="Enter SQL query",
                                    rows=5,
                                    value=query_template_list[0]["value"]
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
                                            "maxWidth": "100%",
                                            "overflowX": "auto",
                                            "maxHeight": "400px",
                                            "overflowY": "auto"
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
                                            # codeTheme="coy",
                                            codeBlockStyle={"maxHeight": "488px"},
                                            codeStyle={"fontSize": "14px", "lineHeight": "1.5"},
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
                                        html.P(id="qep-cost", className="my-3"),
                                        html.P(id="qep-rows-estimate", className="my-3"),
                                        html.Div(id="qep-graph", children=[
                                            dcc.Graph(id="qep-interactive-graph", figure=go.Figure(),
                                                      style={"display": "none"}),
                                        ]),
                                    ]
                                ),
                            ),
                        ], className="mb-3"),
                    ], width=6),
                ]),
                # What-If Queries Section
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.H5([
                            html.B("What-If Queries")
                        ], className="bg-light text-dark p-3 py-3 rounded-3 mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Row([
                                    dbc.Label("Alternate Join Type", html_for="join-type-dropdown", width=6),
                                    dbc.Col(
                                        dbc.Select(
                                            id='join-type-dropdown',
                                            options=[
                                                {'label': 'No modification', 'value': 'none'},
                                                {'label': 'Hash Join', 'value': 'hash'},
                                                {'label': 'Merge Join', 'value': 'merge'},
                                                {'label': 'Nested Loop Join', 'value': 'nested'}
                                            ],
                                            value='none',
                                        ),
                                        width=6
                                    ),
                                ]),
                            ], className="mb-3", width=6),
                            dbc.Col([
                                dbc.Row([
                                    dbc.Label("Alternate Scan Type", html_for="scan-type-dropdown", width=6),
                                    dbc.Col(
                                        dbc.Select(
                                            id='scan-type-dropdown',
                                            options=[
                                                {'label': 'No modification', 'value': 'none'},
                                                {'label': 'Sequential Scan', 'value': 'seq'},
                                                {'label': 'Index Scan', 'value': 'index'},
                                                {'label': 'Bitmap Scan', 'value': 'bitmap'}
                                            ],
                                            value='none',
                                        ),
                                        width=6
                                    ),
                                ]),
                            ], className="mb-3", width=6),
                            dbc.Col([
                                dbc.Row([
                                    dbc.Label("Alternate Aggregate Type", html_for="aggregate-type-dropdown", width=6),
                                    dbc.Col(
                                        dbc.Select(
                                            id='aggregate-type-dropdown',
                                            options=[
                                                {'label': 'No modification', 'value': 'hash'},
                                                {'label': 'Disable Hash Aggregate', 'value': 'no_hash'}
                                            ],
                                            value='hash',
                                        ),
                                        width=6
                                    ),
                                ]),
                            ], className="mb-3", width=6),
                        ]),
                        dbc.Button(["Execute What-If Query", html.I(className="bi bi-play-fill ms-2")],
                                   id="execute-whatif-query-btn", color="primary", className="my-3", disabled=True),

                        dbc.Alert(id="whatif-query-status", color="info", is_open=False),
                    ], width=12),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        html.H5([
                            html.B("AQP")
                        ], className="bg-light text-dark p-3 py-3 rounded-3 mb-3"),
                        dbc.Row([
                            dbc.Col(
                                dcc.Loading(
                                    id="loading-whatif-qep",
                                    type="default",
                                    children=[
                                        fmc.FefferyMarkdown(
                                            id="whatif-qep-output",
                                            # codeTheme="coy",
                                            codeBlockStyle={"maxHeight": "542px"},
                                            codeStyle={"fontSize": "14px", "lineHeight": "1.5"},
                                        ),
                                    ]
                                ),
                            )
                        ], className="mb-3"),
                    ], width=6),

                    dbc.Col([
                        html.H5([
                            html.B("AQP Graph")
                        ], className="bg-light text-dark p-3 py-3 rounded-3 mb-3"),
                        dbc.Row([
                            dbc.Col(
                                dcc.Loading(
                                    id="loading-whatif-qep-graph",
                                    type="default",
                                    children=[
                                        html.P(id="whatif-cost", className="my-3"),
                                        html.P(id="cost_difference", className="my-3"),
                                        html.Div(id="whatif-qep-graph", children=[
                                            dcc.Graph(id="updated-qep-graph", figure=go.Figure())
                                        ])
                                    ]
                                ),
                            )
                        ], className="mb-3"),
                    ], width=6),
                ], className="mb-5"),

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
                        "success", True, table_children, f"Time taken: {round(time_taken * 1000):,} ms", False,
                        False)
            except psycopg2.OperationalError as e:
                print(f"Connection failed: {e}")
                return ([html.I(className="bi bi-x-octagon-fill me-2"), "Connection failed:",
                         fmc.FefferyMarkdown(markdownStr=f"```sh\n{e}\n```", codeTheme="atom-dark", className="mt-3")],
                        "danger", True, [], "", True, True)

        @self.app.callback(
            Output("query-input", "value"),
            Input("query-template", "value")
        )
        def update_query_input(selected_template):
            return selected_template

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
                            "fontSize": "14px",
                            "padding": "2px",
                            "margin": "0",
                            "whiteSpace": "nowrap",
                            "overflow": "hidden",
                            "textOverflow": "ellipsis",
                        }
                    )
                    return [html.I(className="bi bi-check-circle-fill me-2"),
                            "Query executed successfully!"], "success", True, table, f"Time taken: {round(time_taken * 1000):,} ms", f"Rows returned: {rows}"
                else:
                    return [html.I(className="bi bi-check-circle-fill me-2"),
                            "Query executed successfully!"], "success", True, html.P(
                        "Query executed successfully!"), f"Time taken: {round(time_taken * 1000):,} ms", "No rows returned"
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
            Output("execute-whatif-query-btn", "disabled"),
            Input("qep-button", "n_clicks"),
            State("query-input", "value"),
        )
        def get_qep(n_clicks, query):
            if n_clicks is None:
                return "", "info", False, None, "", True, True

            try:
                # Get the query execution plan
                self.qep, self.qep_cost, self.qep_rows, time_taken, error = self.db.get_qep(query)

                if error:
                    raise psycopg2.Error(error)

                return ([html.I(className="bi bi-check-circle-fill me-2"),
                        "Query execution plan generated successfully!"], "success",
                        True, f"```json\n{self.qep}\n```", f"Time taken: {round(time_taken * 1000):,} ms", False, False)
            except psycopg2.Error as e:
                return [html.I(className="bi bi-x-octagon-fill me-2"), "Error generating query execution plan:",
                        fmc.FefferyMarkdown(markdownStr=f"```sh\n{str(e)}\n```", codeTheme="atom-dark",
                                            className="mt-3")], "danger", True, "", "", True

        @self.app.callback(
            Output("qep-graph", "children"),
            Output("qep-graph-status", "children"),
            Output("qep-graph-status", "color"),
            Output("qep-graph-status", "is_open"),
            Output("qep-cost", "children"),
            Output("qep-rows-estimate", "children"),
            Input("show-qep-graph", "n_clicks"),
        )
        def show_qep_graph(n_clicks):
            if n_clicks is None:
                return None, "", "info", False, "", ""

            if self.qep:
                qep_dict = json.loads(self.qep)
                graph = Graph()
                graph.parse_qep(qep_dict)
                # graph.print_graph()
                graph_plot = GraphPlot(graph.build_graph())
                return (
                    dcc.Graph(id="qep-interactive-graph", figure=graph_plot.plot_graph()),
                    [
                        html.I(className="bi bi-check-circle-fill me-2"),
                        "QEP Graph generated successfully!"
                    ],
                    "success",
                    True,
                    html.Span([
                        "QEP Query Cost: ",
                        html.Strong(f'{round(self.qep_cost):,}')
                    ]),
                    f'Query Planner Output Rows Estimate: {self.qep_rows:,}'
                )
            else:
                return None, [html.I(className="bi bi-x-octagon-fill me-2"),
                              "No QEP available to generate graph"], "danger", True, "", ""

        @self.app.callback(
            Output("whatif-query-status", "children"),
            Output("whatif-query-status", "color"),
            Output("whatif-query-status", "is_open"),
            Output("whatif-qep-output", "markdownStr"),
            Output("whatif-qep-graph", "children"),
            Output("whatif-cost", "children"),
            Output("cost_difference", "children"),
            Input("execute-whatif-query-btn", "n_clicks"),
            State("join-type-dropdown", "value"),
            State("scan-type-dropdown", "value"),
            State("aggregate-type-dropdown", "value"),
            State("query-input", "value"),
        )
        def execute_whatif_query(n_clicks, join_type, scan_type, aggregate_type, query):
            if n_clicks is None:
                return "", "info", False, "", "", "", ""

            try:
                # Send the What-If parameters and query to the backend to get the new QEP
                self.modified_qep, self.modified_qep_cost, modified_qep_rows, modified_execution_time, error = whatif_query(
                    self.db, query, join_type, scan_type, aggregate_type)

                if error:
                    raise Exception(error)

                # Displaying Updated QEP in JSON format
                qep_markdown = f"```json\n{self.modified_qep}\n```"

                # Creating QEP Graph from the retrieved graph data
                if self.modified_qep:
                    modified_qep_dict = json.loads(self.modified_qep)
                    modified_graph = Graph()
                    modified_graph.parse_qep(modified_qep_dict)
                    modified_graph_plot = GraphPlot(modified_graph.build_graph())
                    modified_qep_graph = dcc.Graph(id="updated-qep-graph", figure=modified_graph_plot.plot_graph())

                perfomance_boost = 100 * (self.qep_cost - self.modified_qep_cost) / self.qep_cost
                cost_string = "Perfomance Boost (%):" if perfomance_boost >= 0 else "Perfomance Fall (%):"

                if perfomance_boost > 0:
                    color = "success"
                elif perfomance_boost < 0:
                    color = "danger"
                else:
                    color = "body"

                return [
                    html.I(className="bi bi-check-circle-fill me-2"), "What-If Query executed successfully!"
                ], "success", True, qep_markdown, modified_qep_graph, html.Span([
                    "AQP Query Cost: ", html.Strong(f'{round(self.modified_qep_cost):,}')
                ]), html.Span(f'{cost_string} {abs(perfomance_boost):.2f}', className=f'text-{color}')

            except Exception as e:
                # Handle any errors that occurred
                return [
                    html.I(className="bi bi-x-octagon-fill me-2"),
                    "Error executing What-If query:",
                    fmc.FefferyMarkdown(markdownStr=f"```sh\n{str(e)}\n```", codeTheme="atom-dark",
                                        className="mt-3")], "danger", True, "", "", "", ""

    def run(self):
        self.app.run(debug=True)
