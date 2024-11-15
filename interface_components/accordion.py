import dash_bootstrap_components as dbc
from dash import html


def accordion():
    return dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    html.P("If all other join methods are also disabled or cannot "
                           "be used for a particular query due to constraints ("
                           "e.g., missing indexes for nested loop, insufficient "
                           "memory for hash join), PostgreSQL might fall back to "
                           "a disabled join type as a last resort."),
                ],
                title="Note",
            ),
        ], start_collapsed=True, className="mt-3"
    )