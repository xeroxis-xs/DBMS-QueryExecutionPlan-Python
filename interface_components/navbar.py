import dash_bootstrap_components as dbc
from dash import html


def navbar():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(
                children=[
                    html.I(className="bi bi-book me-2"),
                    "PostgreSQL Documentation (EXPLAIN)",

                ],
                href="https://www.postgresql.org/docs/current/using-explain.html",
                target="_blank"
            )),
            dbc.NavItem(dbc.NavLink(
                children=[
                    html.I(className="bi bi-github me-2"),  # Add Bootstrap icon here
                    "GitHub Repo",
                ],
                href="https://github.com/xeroxis-xs/DBMS-QueryExecutionPlan-Python",
                target="_blank"
            )),
        ],
        brand="SC3020 Group Project 2 | Group 4",
        brand_href="#",
        color="primary",
        dark=True,
    )