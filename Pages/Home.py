import pandas as pd
from dash import register_page, html, Input, Output, dcc, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.express as px
from utils import final_df

# Year selector with improved styling
year_d = dmc.Select(
    id="year-selector",
    label="Select Year",
    data=[{"label": year, "value": year} for year in sorted(final_df['Year'].dropna().unique())],
    value=final_df['Year'].dropna().iloc[0],
    clearable=False,
    style={"width": 200},
    rightSection=DashIconify(icon="radix-icons:chevron-down"),
    radius="md",
    size="md"
)

register_page(__name__, path="/", name="Home", order=0)

layout = dmc.Container(
    fluid=True,
    children=[
        # Page header
        dmc.Stack(
            [
                dmc.Title("Global Migration Dashboard", order=1, style={"color": "#006FBA"}),
                dmc.Text("Visualizing migration patterns with detailed breakdowns", c="dimmed", size="lg"),
                year_d
            ],
            gap="xs",
            style={"marginBottom": "30px"}
        ),
        
        # Main grid with modified card structure
        dmc.Grid(
            [
                # Map column
                dmc.GridCol(
                    span=7,
                    children=[
                        dmc.Paper(
                            dcc.Graph(id="world-migration-chart", style={"height": "75vh"}),
                            withBorder=True,
                            radius="md",
                            shadow="sm",
                            style={"height": "100%"}
                        )
                    ],
                    style={"height": "75vh"}
                ),
                
                # Stats cards column
                dmc.GridCol(
                    span=5,
                    children=dmc.Stack(
                        [
                            # First row - summary cards
                            dmc.Grid(
                                [
                                    dmc.GridCol(span=4, children=dmc.Paper(
                                        dmc.Card(id="total-countries", withBorder=True, p=0),
                                        withBorder=True, shadow="sm", radius="md"
                                    )),
                                    dmc.GridCol(span=4, children=dmc.Paper(
                                        dmc.Card(id="total-migrants", withBorder=True, p=0),
                                        withBorder=True, shadow="sm", radius="md"
                                    )),
                                    dmc.GridCol(span=4, children=dmc.Paper(
                                        dmc.Card(id="total-population", withBorder=True, p=0),
                                        withBorder=True, shadow="sm", radius="md"
                                    )),
                                ],
                                gutter="md"
                            ),
                            
                            # Second row - detailed country stats
                            dmc.Paper(
                                dmc.Card(id="country-stats-card", withBorder=True, p=0),
                                withBorder=True, shadow="sm", radius="md",
                                style={"height": "22vh"}
                            ),
                            
                            # Third row - continent breakdown
                            dmc.Paper(
                                dmc.Card(id="continent-stats-card", withBorder=True, p=0),
                                withBorder=True, shadow="sm", radius="md",
                                style={"height": "22vh"}
                            ),
                            
                            # Fourth row - gender breakdown
                            dmc.Paper(
                                dmc.Card(id="gender-stats-card", withBorder=True, p=0),
                                withBorder=True, shadow="sm", radius="md",
                                style={"height": "22vh"}
                            )
                        ],
                        gap="md",
                        style={"height": "75vh", "overflowY": "auto"}
                    )
                )
            ],
            gutter="xl"
        ),
        
        # Hover toolkit at bottom
        dmc.Paper(
            id="hover-toolkit",
            withBorder=True,
            radius="md",
            shadow="xs",
            p="md",
            style={"marginTop": "20px"}
        )
    ],
    style={"maxWidth": "2000px", "padding": "20px"}
)

@callback(
    [
        Output("world-migration-chart", "figure"),
        Output("total-countries", "children"),
        Output("total-migrants", "children"),
        Output("total-population", "children"),
        Output("gender-stats-card", "children")
    ],
    [Input("year-selector", "value")]
)
def update_dashboard(selected_year):
    # Filter data
    year_df = final_df[final_df['Year'] == selected_year]
    
    # Create world map
    fig = px.choropleth(
        year_df,
        locations="country",
        locationmode="country names",
        color="migration_both",
        hover_name="country",
        hover_data={
            "migration_male": ":,.0f",
            "migration_female": ":,.0f",
            "population_both": ":,.0f",
            "country": False
        },
        projection="natural earth",
        title=f"<b>Global Migration Patterns ({selected_year})</b>",
        color_continuous_scale=px.colors.sequential.Plasma,
        range_color=[0, year_df['migration_both'].quantile(0.95)]
    )
    
    # Enhanced map layout
    fig.update_layout(
        margin={"r": 2, "t": 20, "l": 20, "b": 30},
        title_font_size=18,
        title_x=0.05,
        title_y=0.95,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="LightGray",
            landcolor="rgba(255, 255, 255, 0.5)",
            bgcolor="rgba(0,0,0,0)"
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title="Migrants",
            thickness=15,
            len=0.5,
            yanchor="middle",
            y=0.5
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Roboto"
        )
    )
    
    # Calculate metrics
    total_countries = len(year_df['country'].unique())
    total_migrants = year_df['migration_both'].sum()
    total_population = year_df['population_both'].sum()

    # 1. Summary Cards
    countries_card = dmc.CardSection(
        [
            dmc.Group([DashIconify(icon="emojione:globe-showing-americas"), 
                      dmc.Text("Countries")], gap="xs"),
            dmc.Text(f"{total_countries:,}", size="xl", fw=700),
            dmc.Progress(value=100, color="blue", size="sm", mt=5)
        ],
        p="lg"
    )
    
    migrants_card = dmc.CardSection(
        [
            dmc.Group([DashIconify(icon="mdi:account-group"), 
                     dmc.Text("Migrants")], gap="xs"),
            dmc.Text(f"{total_migrants:,.0f}", size="xl", fw=700),
            dmc.Group(
                [
                    dmc.Badge(f"♂ {year_df['migration_male'].sum():,.0f}", color="blue"),
                    dmc.Badge(f"♀ {year_df['migration_female'].sum():,.0f}", color="pink")
                ],
                gap="xs"
            )
        ],
        p="lg"
    )
    
    population_card = dmc.CardSection(
        [
            dmc.Group([DashIconify(icon="mdi:earth"), 
                     dmc.Text("Population")], gap="xs"),
            dmc.Text(f"{total_population:,.0f}", size="xl", fw=700),
            dmc.Text(f"{(total_migrants/total_population*100):.2f}% migrants", size="sm", c="dimmed")
        ],
        p="lg"
    )
    
    # 2. Gender Breakdown Card
    gender_card = dmc.CardSection(
        [
            dmc.Title("Gender Distribution", order=4, mb="sm"),
            dmc.Group(
                [
                    dmc.Stack(
                        [
                            dmc.Text("Male", c="blue"),
                            dmc.Text(f"{year_df['migration_male'].sum()/1e6:.1f}M", size="xl"),
                            dmc.RingProgress(
                                sections=[{"value": (year_df['migration_male'].sum()/total_migrants*100), "color": "blue"}],
                                label=dmc.Text(f"{(year_df['migration_male'].sum()/total_migrants*100):.1f}%")
                            )
                        ],
                        align="center"
                    ),
                    dmc.Stack(
                        [
                            dmc.Text("Female", c="pink"),
                            dmc.Text(f"{year_df['migration_female'].sum()/1e6:.1f}M", size="xl"),
                            dmc.RingProgress(
                                sections=[{"value": (year_df['migration_female'].sum()/total_migrants*100), "color": "pink"}],
                                label=dmc.Text(f"{(year_df['migration_female'].sum()/total_migrants*100):.1f}%")
                            )
                        ],
                        align="center"
                    )
                ],
                justify="apart"
            )
        ],
        p="lg"
    )
    
    return fig, countries_card, migrants_card, population_card, gender_card

@callback(
    Output("continent-stats-card", "children"),
    [Input("year-selector", "value")]
)
def update_continent_stats(selected_year):
    # Filter data for selected year
    year_df = final_df[final_df['Year'] == selected_year]
    
    # Calculate continent statistics
    continent_stats = year_df.groupby('continent').agg({
        'migration_both': 'sum',
        'population_both': 'sum',
        'migration_male': 'sum',
        'migration_female': 'sum'
    }).reset_index()
    
    # Calculate global totals for percentages
    total_migrants = year_df['migration_both'].sum()
    total_population = year_df['population_both'].sum()
    
    return dmc.CardSection(
        [
            dmc.Title("Continental Statistics", order=4, mb="md"),
            dmc.SimpleGrid(
                cols=3,
                spacing="lg",
                children=[
                    dmc.Paper(
                        [
                            dmc.Text(cont['continent'], fw=600, size="sm"),
                            dmc.Divider(variant="solid", my=5),
                            dmc.Stack(
                                [
                                    dmc.Group(
                                        [
                                            DashIconify(icon="mdi:account-group", width=16),
                                            dmc.Text("Migrants", size="xs", c="dimmed")
                                        ],
                                        gap=4
                                    ),
                                    dmc.Text(f"{cont['migration_both']/1e6:.2f}M", fw=700),
                                    dmc.Progress(
                                        value=cont['migration_both']/total_migrants*100,
                                        color="blue",
                                        size="sm",
                                        mt=4
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Badge(f"♂ {cont['migration_male']/1e6:.1f}M", color="blue", variant="light"),
                                            dmc.Badge(f"♀ {cont['migration_female']/1e6:.1f}M", color="pink", variant="light")
                                        ],
                                        gap=4,
                                        mt=4
                                    )
                                ],
                                gap=2
                            ),
                            dmc.Stack(
                                [
                                    dmc.Group(
                                        [
                                            DashIconify(icon="mdi:earth", width=16),
                                            dmc.Text("Population", size="xs", c="dimmed")
                                        ],
                                        gap=4
                                    ),
                                    dmc.Text(f"{cont['population_both']/1e6:.2f}M", fw=700),
                                    dmc.Progress(
                                        value=cont['population_both']/total_population*100,
                                        color="orange",
                                        size="sm",
                                        mt=4
                                    ),
                                    dmc.Text(
                                        f"{(cont['migration_both']/cont['population_both']*100):.2f}% migrants",
                                        size="xs",
                                        c="dimmed",
                                        mt=4
                                    )
                                ],
                                gap=2,
                                mt=10
                            )
                        ],
                        p="sm",
                        withBorder=True,
                        radius="sm",
                        style={"height": "100%"}
                    ) for _, cont in continent_stats.iterrows()
                ]
            )
        ],
        p="lg"
    )

@callback(
    Output("country-stats-card", "children"),
    [Input("world-migration-chart", "hoverData"),
     Input("year-selector", "value")]
)
def update_country_details(hoverData, selected_year):
    if not hoverData:
        return dmc.Alert("Hover over a country to see details", title="Country Data", color="blue")
    
    country = hoverData["points"][0]["location"]
    year_df = final_df[final_df['Year'] == selected_year]
    row = year_df[year_df["country"] == country].iloc[0]
    
    migration_rate = (row["migration_both"] / row["population_both"]) * 100 if row["population_both"] else 0
    
    return dmc.CardSection(
        [
            dmc.Title(row["country"], order=4),
            dmc.SimpleGrid(
                cols=2,
                spacing="lg",
                children=[
                    dmc.Stack(
                        [
                            dmc.Text("Total Migrants", size="sm", c="dimmed"),
                            dmc.Text(f"{row['migration_both']:,}", size="lg", fw=600),
                            dmc.Text(f"{migration_rate:.2f}% of population", size="sm")
                        ]
                    ),
                    dmc.Stack(
                        [
                            dmc.Text("Population", size="sm", c="dimmed"),
                            dmc.Text(f"{row['population_both']:,}", size="lg", fw=600),
                            dmc.Text(f"Rank: {row.get('rank', 'N/A')}", size="sm")
                        ]
                    ),
                    dmc.Stack(
                        [
                            dmc.Text("Male Migrants", size="sm", c="dimmed"),
                            dmc.Text(f"{row['migration_male']:,}", size="md", c="blue"),
                            dmc.Progress(
                                value=(row['migration_male']/row['migration_both']*100),
                                color="blue",
                                size="sm"
                            )
                        ]
                    ),
                    dmc.Stack(
                        [
                            dmc.Text("Female Migrants", size="sm", c="dimmed"),
                            dmc.Text(f"{row['migration_female']:,}", size="md", c="pink"),
                            dmc.Progress(
                                value=(row['migration_female']/row['migration_both']*100),
                                color="pink",
                                size="sm"
                            )
                        ]
                    )
                ]
            )
        ],
        p="lg"
    )

@callback(
    Output("hover-toolkit", "children"),
    [Input("world-migration-chart", "hoverData"),
     Input("year-selector", "value")]
)
def update_hover_toolkit(hoverData, selected_year):
    if not hoverData:
        return dmc.Alert("Hover over a country for detailed insights", color="blue")
    
    country = hoverData["points"][0]["location"]
    year_df = final_df[final_df['Year'] == selected_year]
    row = year_df[year_df["country"] == country].iloc[0]
    
    return dmc.Stack(
        [
            dmc.Text(f"Migration Insights: {row['country']}", fw=700),
            dmc.Divider(),
            dmc.SimpleGrid(
                cols=3,
                spacing="md",
                children=[
                    dmc.Stack(
                        [
                            dmc.Text("Total Population", size="sm", c="dimmed"),
                            dmc.Text(f"{row['population_both']:,}", size="md")
                        ]
                    ),
                    dmc.Stack(
                        [
                            dmc.Text("Migration Rate", size="sm", c="dimmed"),
                            dmc.Text(f"{(row['migration_both']/row['population_both']*1000):.2f} per 1000", size="md")
                        ]
                    ),
                    dmc.Stack(
                        [
                            dmc.Text("Gender Ratio", size="sm", c="dimmed"),
                            dmc.Text(f"{(row['migration_male']/row['migration_female']):.2f} M/F", size="md")
                        ]
                    )
                ]
            )
        ],
        gap="sm"
    )