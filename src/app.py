from dash import Dash, dcc, callback, Output, Input, html, dash_table
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import pandas as pd
from typing import Literal

from data_manager import DataManager
from data.raw_data.states_localization import STATES_COORDS

load_figure_template('slate')

class COVIDDashboard:
    def __init__(self,) -> None:
        self.data_manager = DataManager()

        dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
        self.app = app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, dbc_css])

        self._setup_layout()
        self._setup_callbacks()

    def _setup_layout(self,) -> None:
        self.app.layout = [
            dbc.Container([
                dbc.Row([
                    # ------- Sidebar
                    dbc.Col([
                        html.H1('COVID-19 Dashboard', style={'color': 'white'}),
                        html.Hr(),
                        dcc.Markdown('##### Dados retirados de [Brasil.IO](https://brasil.io/dataset/covid19/caso_full/)'),
                        html.Br(),
                        dcc.Dropdown(
                            id='dropdown-state',
                            options=self.data_manager.df_last['state'].unique(),
                            placeholder='Estado (UF)',
                        ),
                        html.Br(),
                        dcc.Dropdown(
                            id='dropdown-city',
                            placeholder='Município',
                            multi=True
                        ),
                        html.Br(),
                        html.Label("Tipo de Dado:", className='mb-2'),
                        dbc.RadioItems(
                            id='radio-filter',
                            options=['Casos Confirmados', 'Óbitos'],
                            value='Casos Confirmados',
                            inline=True,
                        ),
                    ], width=2, style={'margin-left': '2vh', 'height': '100vh'}),

                    # ------- Graphs and KPIs
                    dbc.Col([

                        # ------- KPI Row
                        dbc.Row([
                            dbc.Col(dbc.Card(dbc.CardBody([
                                html.H5(id='kpi-total-title', children='Total Acumulado'),
                                html.H4(id='kpi-total', children='Sem valor disponível')
                            ], className='text-center'))),
                            dbc.Col(dbc.Card(dbc.CardBody([
                                html.H5(id='kpi-new-cases-title', children='Novos Casos / Óbitos'),
                                html.H4(id='kpi-new-cases', children='Sem valor disponível')
                            ], className='text-center'))),
                            dbc.Col(dbc.Card(dbc.CardBody([
                                html.H5(id='kpi-average-title', children='Média de Casos por Cidade'),
                                html.H4(id='kpi-average', children='Sem valor disponível')
                            ], className='text-center'))),
                            dbc.Col(dbc.Card(dbc.CardBody([
                                html.H5(children='Taxa de Letalidade'),
                                html.H4(id='kpi-fatality-rate', children='Sem valor disponível')
                            ], className='text-center'))),
                        ], style={'margin-bottom': '3vh'}),

                        # ------- Choropleth Graph
                        dbc.Row([
                            dbc.Col(
                                dcc.Graph(id='choropleth-map'),
                                width=6
                            ),
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(id='bar-chart'),
                                    style={'height': '450px', 'overflowY': 'scroll', 'overflowX': 'hidden'},
                                )
                            ),
                        ], style={'margin-bottom': '3vh'}),

                        # ------- Bar Graph
                        dbc.Row([
                            dcc.Graph(id='line-chart')
                        ]),

                    ], width=9)
                ], style={'margin-top': '2vh', 'margin-bottom': '3vh'}),
            ], fluid=True, className='dbc'),
        ]

    def _setup_callbacks(self,) -> None:
        # ----- Show cities in Dropdown, based in state selection
        @self.app.callback(
            Output('dropdown-city', 'options'),
            Input('dropdown-state', 'value')
        )
        def update_city(selected_state):
            return self.data_manager.df_last[self.data_manager.df_last['state'] == selected_state]['city'].unique()

        # ----- Update Choropleth Map based on filters
        @self.app.callback(
            Output('choropleth-map', 'figure'),
            Input('dropdown-state', 'value'),
            Input('dropdown-city', 'value'),
            Input('radio-filter', 'value')
        )
        def update_map(selected_state, selected_city, selected_radio):

            if selected_radio == 'Casos Confirmados':
                data_type = 'last_available_confirmed_per_100k_inhabitants'
            else:
                data_type = 'last_available_deaths_per_100k_inhabitants'

            if selected_state:
                if selected_city:
                    cities = selected_city
                else:
                    cities = self.data_manager.df_last[self.data_manager.df_last['state'] == selected_state]['city'].unique()

                selected_df = self.data_manager.df_last[(self.data_manager.df_last['city'].isin(cities)) & (self.data_manager.df_last['state'] == selected_state)]
            else:
                selected_state = 'BR'
                selected_df = self.data_manager.df_last.copy()

            selected_df = selected_df[selected_df['place_type'] == 'city']

            
            fig = px.choropleth_map(
                data_frame=selected_df,
                geojson=self.data_manager.geojson,
                featureidkey='properties.id',
                locations='city_ibge_code',
                #title='Mapa do COVID-19 no Brasil',
                color=data_type,
                color_continuous_scale='Viridis',
                template='plotly_dark',
                map_style='carto-darkmatter',
                center={"lat": STATES_COORDS[selected_state]['lat'], "lon": STATES_COORDS[selected_state]['lon']},
                zoom= STATES_COORDS[selected_state]['zoom'],
                opacity=0.5,
                hover_name='city',
                hover_data={
                    'state': True,
                    'last_available_confirmed': True,
                    'last_available_deaths': True,
                    'last_available_death_rate': ':.2%',
                    'city_ibge_code': False,
                    'last_available_confirmed_per_100k_inhabitants': ':.2f',
                    'last_available_deaths_per_100k_inhabitants': ':.2f'
                },
                labels={
                    'city': 'Município',
                    'state': 'UF',
                    'last_available_confirmed': 'Casos Confirmados',
                    'last_available_deaths': 'Óbitos Acumulados',
                    'last_available_death_rate': 'Taxa de Letalidade',
                    'last_available_confirmed_per_100k_inhabitants': 'Casos por 100k habitantes',
                    'last_available_deaths_per_100k_inhabitants': 'Óbitos por 100k habitantes',
                },
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin={"r":0,"t":0,"l":0,"b":0},
                coloraxis_colorbar=dict(
                    title_side='top',
                    orientation="h",
                    yanchor="bottom", y=0,
                    xanchor="center", x=0.5,
                    thickness=15,
                )
            )
            return fig

        # ----- Update KPIs based on filters
        @self.app.callback(
            Output('kpi-total', 'children'),
            Output('kpi-new-cases', 'children'),
            Output('kpi-average', 'children'),
            Output('kpi-fatality-rate', 'children'),
            Output('kpi-total-title', 'children'),
            Output('kpi-new-cases-title', 'children'),
            Output('kpi-average-title', 'children'),
            Input('dropdown-state', 'value'),
            Input('dropdown-city', 'value'),
            Input('radio-filter', 'value'),
        )
        def update_kpis(selected_state, selected_city, selected_radio):
            df_filtered = self.data_manager.df_last.copy()
            if selected_state:
                df_filtered = df_filtered[df_filtered['state'] == selected_state]
            if selected_city:
                df_filtered = df_filtered[df_filtered['city'].isin(selected_city)]

            if selected_radio == 'Casos Confirmados':
                total = df_filtered['last_available_confirmed'].sum()
                new_cases = df_filtered['new_confirmed'].sum()
                mean = df_filtered['last_available_confirmed'].mean()
                title = 'Casos'
            else:
                total = df_filtered['last_available_deaths'].sum()
                new_cases = df_filtered['new_deaths'].sum()
                mean = df_filtered['last_available_deaths'].mean()
                title = 'Óbitos'

            # ----- Formating thousands and decimals
            total = '{:,.0f}'.format(total).replace(',', '.')
            new_cases = '{:,.0f}'.format(new_cases).replace(',', '.')

            mean = '{:,.2f}'.format(mean).replace(',', 'X').replace('.', ',').replace('X', '.')
            mean += f' ({len(df_filtered)} municípios)'
            
            death_rate = df_filtered['last_available_death_rate'].mean() * 100
            death_rate = '{:.2f}'.format(death_rate) + "%"
            
            return total, new_cases, mean, death_rate, f'Total Acumulado de {title}', f'Novos {title}', f'Média de {title} por Município'

        # ----- Update Line Chart based on filters
        @self.app.callback(
            Output('line-chart', 'figure'),
            Input('dropdown-state', 'value'),
            Input('dropdown-city', 'value'),
            Input('radio-filter', 'value'),
        )
        def update_line_chart(selected_state, selected_city, selected_radio):
            if selected_radio == 'Casos Confirmados':
                line_chart_y = 'last_available_confirmed'
            else:
                line_chart_y = 'last_available_deaths'

            def group_by_date_and_location(selected_state: str, line_chart_y: str):

                column_selected = 'city' if selected_state else 'state'
                radio_item_title = 'Óbitos' if line_chart_y == 'last_available_deaths' else 'Casos'

                # ----- Selecting only cities, if state selected. Only states if not selected
                filtered_df = self.data_manager.df[self.data_manager.df['place_type'] == column_selected].copy()

                # ----- Grouping by cities or states
                if column_selected == 'city':
                    if selected_city:
                        title = 'Municípios filtrados pelo usuário'
                        cities = selected_city
                    else:
                        # ----- Top 10 CITIES by Deaths or Cases, depending on the RadioItem
                        title = f'10 municípios c/ maior qtd. de {radio_item_title.lower()}'
                        cities = self.data_manager.df_last[
                            (self.data_manager.df_last['place_type'] == column_selected) & 
                            (self.data_manager.df_last['state'] == selected_state)
                        ].sort_values(line_chart_y, ascending=False).head(10)[column_selected]

                    # ----- Grouping By CITY, STATE and DATE
                    df_grouped_by_date_n_location = self.data_manager.df_grouped_by_city.copy()

                    # ----- Filtering only the top 10 CITIES
                    df_grouped_by_date_n_location = df_grouped_by_date_n_location[
                        df_grouped_by_date_n_location[column_selected].isin(cities)
                    ]

                    # ----- Filtering the selected STATE
                    df_grouped_by_date_n_location = df_grouped_by_date_n_location[
                        df_grouped_by_date_n_location['state'] == selected_state
                    ]

                    title = f'{radio_item_title} Confirmados em Municípios por Mês ({title})'
                else:
                    # ----- Top 10 STATES by Deaths or Cases, depending on the RadioItem
                    top10 = self.data_manager.df_last[self.data_manager.df_last['place_type'] == column_selected].sort_values(line_chart_y, ascending=False).head(10)[column_selected]

                    # ----- Grouping By STATE and DATE
                    df_grouped_by_date_n_location = self.data_manager.df_grouped_by_state.copy()
                    
                    # ----- Filtering only the top 10 STATES
                    df_grouped_by_date_n_location = df_grouped_by_date_n_location[
                        df_grouped_by_date_n_location[column_selected].isin(top10)
                    ]

                    title = f'{radio_item_title} Confirmados em Estados por Mês (10 estados com maior número de {radio_item_title.lower()})'
                
                return df_grouped_by_date_n_location, column_selected, title

            filtered_df, column_selected, title = group_by_date_and_location(selected_state, line_chart_y)

            fig = px.line(
                data_frame=filtered_df,
                x='year-month',
                y=line_chart_y,
                color=column_selected,
                title=title,
                hover_name=column_selected,
                labels={
                    'state': 'UF',
                    'city': 'Município',
                    'year-month': 'Mês',
                    'last_available_confirmed': 'Casos Confirmados',
                    'last_available_deaths': 'Óbitos Acumulados',
                }
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin={"r":45,"t":35,"l":0,"b":0},
                
            )
            
            return fig

        # ----- Update Bar Chart based on filters
        @self.app.callback(
            Output('bar-chart', 'figure'),
            Input('dropdown-state', 'value'),
            Input('dropdown-city', 'value'),
            Input('radio-filter', 'value'),
        )
        def update_bar_chart(selected_state, selected_city, selected_radio):
            if selected_radio == 'Casos Confirmados':
                line_chart_x = 'last_available_confirmed'
            else:
                line_chart_x = 'last_available_deaths'

            if selected_state:
                if selected_city:
                    cities = self.data_manager.df_last[
                        (self.data_manager.df_last['place_type'] == 'city') &
                        (self.data_manager.df_last['state'] == selected_state) &
                        (self.data_manager.df_last['city'].isin(selected_city))
                    ].sort_values(line_chart_x)

                    title = 'Municípios filtrados pelo usuário'
                else:
                    cities = self.data_manager.df_last[
                        (self.data_manager.df_last['place_type'] == 'city') &
                        (self.data_manager.df_last['state'] == selected_state)
                    ].sort_values(line_chart_x)

                    if len(cities) > 50:
                        cities = cities.tail(50)

                    title = 'Limitado a 50 municípios'

                line_chart_y = 'city'

                title = f'Número de {selected_radio} por Município ({title})'

            else:
                cities = self.data_manager.df_last[
                    self.data_manager.df_last['place_type'] == 'state'
                ].sort_values(line_chart_x)

                line_chart_y = 'state'

                title = f'Número de {selected_radio} por Estado (UF)'

            fig = px.bar(
                data_frame=cities,
                x=line_chart_x,
                y=line_chart_y,
                title=title,
                text_auto='.2s',
                color=line_chart_x,
                color_continuous_scale='Viridis',
                orientation='h',
                hover_name=line_chart_y,
                hover_data={
                    'last_available_confirmed_per_100k_inhabitants': ':.2f'
                },
                labels={
                    'state': 'Estado (UF)',
                    'last_available_confirmed': 'Casos Confirmados',
                    'last_available_deaths': 'Óbitos Acumulados',
                    'last_available_confirmed_per_100k_inhabitants': 'Casos por 100k habitantes',
                }
            )

            dynamic_height = max(450, len(cities) * 30 + 150)

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                height=dynamic_height,
                plot_bgcolor='rgba(0,0,0,0)',
                margin={"r":0,"t":30,"l":0,"b":0},
                yaxis={'type': 'category', 'tickmode': 'linear'},
            )

            return fig

    def run(self, debug: bool = True, port: int = 8050) -> None:
        self.app.run(debug=debug, port=port)


if __name__ == '__main__':
    dashboard = COVIDDashboard()
    dashboard.run()