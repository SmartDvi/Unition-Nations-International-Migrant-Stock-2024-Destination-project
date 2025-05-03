import pandas as pd 
from dash import Input, Output, html, callback, _dash_renderer, page_container, Dash
import dash_mantine_components as dmc
import dash

from utils import final_df

_dash_renderer._set_react_version("18.3.1")

app = Dash(external_scripts=dmc.styles.ALL, use_pages=True)


# Navigation links (filter out 404 page)
nav_links = dmc.Group(
    children=[
        dmc.Anchor(
            page["name"],
            href=page["relative_path"],
            style={"textDecoration": "none", "fontWeight": 500}
        )
        for page in dash.page_registry.values()
        if page["module"] != "pages.not_found_404"
    ],
    gap="xl",
    mt=10
)

# Main layout with UN logo
app.layout = dmc.MantineProvider(
    children=[
        dmc.Container(
            fluid=True,
            children=[
                # Header with logo and navigation
                dmc.Grid(
                    children=[
                        # Left-aligned navigation
                        dmc.GridCol(
                            span=10,
                            children=dmc.Paper(
                                nav_links,
                                p="md",
                                shadow="sm",
                                style={"height": "40%"}
                            )
                        ),
                        # Right-aligned UN logo
                        dmc.GridCol(
                            span=2,
                            children=html.Div(
                                html.Img(
                                    src="/assets/un_logo.png",
                                    style={
                                        "height": "60px",
                                        "float": "right",
                                        "padding": "10px",
                                        "objectFit": "contain"
                                    }
                                ),
                                style={"height": "100%", "display": "flex", "alignItems": "center"}
                            )
                        )
                    ],
                    gutter="xl",
                    style={"alignItems": "center"}
                ),
                
                # Page content area
                dmc.Grid(
                    children=[
                        dmc.GridCol(
                            span=12,
                            children=page_container
                        )
                    ],
                    style={"minHeight": "80vh"}
                ),
                
                # Footer
                dmc.Grid(
                    children=[
                        dmc.GridCol(
                            span=12,
                            children=dmc.Text(
                                "© 2024 United Nations Migration Dashboard", 
                                tt="center",
                                c="dimmed"
                            )
                        )
                    ],
                    mt=20
                )
            ],
            style={"padding": "20px"}
        )
    ],
    theme={"colorScheme": "light"}
)




if __name__ == "__main__":
    app.run(debug = True, port = 6070)
