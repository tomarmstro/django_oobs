#!/usr/bin/env python


# Imports
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import xarray as xr
import plotly.express as px
import glob
import pandas as pd
from datetime import datetime
import plotly.io as pio
import getLTSPname
import extractVariable
import matplotlib.pyplot as plt
import numpy as np
import pathlib

# ---------------------------------------------------------------
# Constants etc
external_stylesheets = [dbc.themes.LUMEN, "assets/base-styles.css"]
pio.templates.default = "simple_white"
px.defaults.color_continuous_scale = px.colors.sequential.Blackbody

DATA_SKIP = 500
TRANSPARENT_COLOUR = "rgba(0, 0, 0, 0)"
IMOS_DEEP_BLUE_COLOUR = "#3b6e8f"
IMOS_SEA_BLUE_COLOUR = "#54bceb"
IMOS_SAND_COLOUR = "#d9d7bd"
IMOS_MID_GREY_COLOUR = "#3c3c3c"

BODY_BACKGROUND_COLOUR = IMOS_SAND_COLOUR
BODY_BORDER_COLOUR = IMOS_MID_GREY_COLOUR

DEGREES_SYMBOL = u'\xb0'

PATH = pathlib.Path(__file__).parent

pd.set_option('display.max_rows', None)
app = DjangoDash('data', external_stylesheets=external_stylesheets)

MOORINGS = ['GBRMYR', 'GBRPPS', 'GBRLSL', 'GBRHIS', 'GBROTE', 'GBRCCH', 'NWSBAR', 'NWSLYN', 'NWSROW', 'NWSBRW',
            'NRSYON']
map_selection = "NRSYON"
active_tab = 'vcur_tab'

# Create map
def render_map():
    map_data = pd.read_excel('sites.xlsx')
    map_data = pd.DataFrame(map_data)
    map_data = map_data.drop(columns=['x', 'y', 'd'])
    return [dcc.Graph(id='moorings_map', figure=px.scatter_mapbox
        (
        map_data,
        lat=map_data['Latitude'],
        lon=map_data['Longitude'],
        color='Group',
        hover_name='Site',
        zoom=3.3,
        center={"lat": -27, "lon": 134},
        hover_data={'Latitude': False,
                    'Longitude': False,
                    'Group': False
                    },
        )
        .update_layout(
            {
            "font": {"color": "white"},
            'plot_bgcolor': TRANSPARENT_COLOUR,
            'paper_bgcolor': TRANSPARENT_COLOUR,
            },
        mapbox_style="open-street-map", height=750, width=960,
        # Remove legend
        showlegend=False, ),
        # stop zoomable map
        config={'scrollZoom': False}
        )]

# Get files
def collect_working_files(variable):
    working_files = []
    for mooring in MOORINGS:
        if variable == 'velocity-hourly':
            LTSP_filename = (getLTSPname.getLTSPfileName(mooring, variable))
        elif variable == 'aggregated':
            LTSP_filename = (getLTSPname.getLTSPfileName(mooring, variable))
        else:
            print('incorrect variable for collecting files')
        print(LTSP_filename.split("timeseries/", 1)[1])
        working_files.append(LTSP_filename)
    return working_files

def build_tabs():
    return dbc.Tabs(
        [
            # dbc.Tab(render_map(),
            #         label='map_select', tab_id='map_tab', ),
            dbc.Tab(label='Velocity', tab_id='vel_tab', tabClassName="flex-grow-1 text-center"),
            dbc.Tab(label='NE Velocity', tab_id='vcur_tab', tabClassName="flex-grow-1 text-center"),
            dbc.Tab(label='Temperature', tab_id='temp_tab', tabClassName="flex-grow-1 text-center"),
            dbc.Tab(label='Daily Temperature', tab_id='daily_temp_tab', tabClassName="flex-grow-1 text-center"),
            dbc.Tab(label='Climatology', tab_id='climatology_tab', tabClassName="flex-grow-1 text-center"),
            dbc.Tab(label='Gridded Temperature', tab_id='gridded_temp_tab', tabClassName="flex-grow-1 text-center"),

        ],
        id='tabs',
        active_tab="vel_tab",
        # style={'width': "100%"},
        className="custom-tabs",
    )

def fig_layout(fig):
    fig.update_layout(
        plot_bgcolor=BODY_BACKGROUND_COLOUR,
        paper_bgcolor=BODY_BACKGROUND_COLOUR,
        font_color=BODY_BORDER_COLOUR
        # plot_bgcolor = IMOS_MID_GREY_COLOUR,
        # paper_bgcolor = IMOS_MID_GREY_COLOUR,
        # font_color = IMOS_SAND_COLOUR
    )

def colourscale_rangeslider():
    return html.Div(
        html.Div(
            [
                dcc.Input(type='text', value=0),
                dcc.RangeSlider(
                    id='condition-range-slider',
                    min=0,
                    max=30,
                    value=[10, 15],
                    allowCross=False
                ),
                dcc.Input(type='text', value=100)
            ],
            style={"display": "grid", "grid-template-columns": "10% 40% 10%"}),
        style={'width': '20%'}
    )

def more_info_button():
    return dbc.Button("Info",
                id="more-info-modal",
                color='info',
                style={"color": "DarkSlateGrey",
                       "display": "inline-block",
                       "width": "10%",
                       "margin-right": "150px",
                       "verticalAlign": "top",
                       "right": "0px",
                       "position": "absolute"})


def build_velocity_tabs():
    return dbc.Tabs(
        [
            dbc.Tab(label='Local Velocity', tab_id='local_vel_tab', tabClassName="flex-grow-1 text-center"),
            dbc.Tab(label='NE Velocity', tab_id='ne_vel_tab', tabClassName="flex-grow-1 text-center"),
        ],
        id='velocity_tabs',
        active_tab='ne_vel_tab',
        style={'width': "100%", 'height': "100%"},
        className="custom-tabs"
    )

vel_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Tab 1", tab_id="tab-1"),
                dbc.Tab(label="Tab 2", tab_id="tab-2"),
            ],
            id="vel_tabs",
            active_tab="tab-1",
        ),
        html.Div(id="content"),
    ]
)

##################### MODAL #######################
map_modal = html.Div(
    [
        dbc.Row(dbc.Button("Select Mooring", id="open-map-modal", color='primary', size="lg"), justify="center", align="center"),
        dbc.Modal(
            [
                dbc.ModalHeader("Please select a mooring location"),
                # dbc.ModalBody(f"Selected mooring: {map_selection}"),
                dbc.ModalBody(render_map()),
                dbc.ModalFooter(dbc.Button("Close", id="close-dismiss")),
            ],
            id="map_modal",
            style={"max-width": "none", "width": "90%", }, )
            # is_open=False,
        # ),
    ]
)



@app.callback(
    Output(component_id="map_modal", component_property="is_open"),
    [Input(component_id="open-map-modal", component_property="n_clicks"),
     Input(component_id="close-dismiss", component_property="n_clicks")],
    State(component_id="map_modal", component_property="is_open"),
)
def toggle_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


# ---------------------------------------------------------------
# Layout
app.layout = html.Div(
    # style={"backgroundColor": DARK_BLUE_COLOUR, 'display': 'inline-block', 'width': '100%'},
    id="big-app-container",
    children=[
        html.Br(),
        map_modal,
        html.Br(),
        build_tabs(),
        # velocity_toggle(),
        # colourscale_rangeslider(),
        html.Div(id='tab_content',
                 className="p-4"
        ),
        # vel_tabs,


    ], style={'display': 'inline-block',
                        'width': '100%',
                        # 'height': '800px',
                        'backgroundColor': BODY_BACKGROUND_COLOUR,
                        }
)




# ---------------------------------------------------------------
# Get tab content
@app.callback(
    # Output(component_id="click-data", component_property="children"),
    Output(component_id='tab_content', component_property='children'),
    Input(component_id='tabs', component_property='active_tab'),
    Input(component_id="moorings_map", component_property="clickData"))
# Input(component_id='selected_time', component_property='active_time')])
def render_tab_content(active_tab, clickData):
    fig = go.Figure()
    fig_layout(fig)
    fig2 = go.Figure()
    fig_layout(fig2)

    data_dir = PATH.joinpath(os.path.abspath(os.curdir) + "/assets/data").resolve()
    map_selection = 'NRSYON'
    if clickData is not None:
        map_selection = clickData['points'][0]['hovertext']
        print(f"{map_selection} selected from the map.")
    print(active_tab)

    # if active_tab == 'vel_tab':
    #     return html.Div(id="vel_container",
    #         children=[
    #             build_velocity_tabs(),
    #             html.H3('HERE'),
    #             html.H6('AND HERE'),
    #             html.Div(id='vel_tab_content',
    #              className="p-6"
    #              ),
    #             html.H3('StILL')])

    if active_tab == 'vel_tab':
        # return html.Div(daily_velocity(map_selection, fig, fig2), vel_tabs)
        return vel_tabs, html.Div(id='content')

    if active_tab == 'vcur_tab':
        return ne_velocity(map_selection, fig, fig2)

    if active_tab == 'temp_tab':
        return temperature(map_selection, fig)

    if active_tab == 'daily_temp_tab':
        return daily_temperature(map_selection, fig)

    if active_tab == 'climatology_tab':
        return climatology(map_selection, fig)

    if active_tab == 'gridded_temp_tab':
        return gridded_temperature(map_selection, fig)
    #
    # if active_tab == 'local_vel_tab':
    #     return daily_velocity(map_selection, fig, fig2)
    #
    # if active_tab == 'ne_vel_tab':
    #     return ne_velocity(map_selection, fig, fig2)


@app.callback(Output("content", "children"), [Input("vel_tabs", "active_tab")])
def switch_tab(at):
    fig = go.Figure()
    fig_layout(fig)
    fig2 = go.Figure()
    fig_layout(fig2)

    data_dir = PATH.joinpath(os.path.abspath(os.curdir) + "/assets/data").resolve()
    map_selection = 'NRSYON'
    tab1_content = html.H3('working')
    if at == "tab-1":
        return tab1_content
    elif at == "tab-2":
        return daily_velocity(map_selection, fig, fig2)
    return html.P("This shouldn't ever be displayed...")


def ne_velocity(map_selection, fig, fig2):
    vcur_files = PATH.joinpath(os.path.abspath(os.curdir) + "/assets/data/vcur").resolve()
    ucur_files = PATH.joinpath(os.path.abspath(os.curdir) + "/assets/data/ucur").resolve()
    for file in os.listdir(vcur_files):
        mooring_site = file[0:6]
        fig.update_layout(
            height=300,
            width=1000,
            )
        fig2.update_layout(
            height=300,
            width=1000,
        )
        if mooring_site in MOORINGS and mooring_site == map_selection:
            vcur_file = pd.read_csv(vcur_files.joinpath(map_selection + '_vcur.csv'))
            fig.add_trace(go.Scatter(x=vcur_file['TIME'], y=vcur_file['VCUR'], name="NEMO"))
            ucur_file = pd.read_csv(ucur_files.joinpath(map_selection + '_ucur.csv'))
            fig2.add_trace(go.Scatter(x=ucur_file['TIME'], y=ucur_file['UCUR'], name="NEMO"))
            return html.Div([
                html.H3(f'VCUR at {map_selection}', style={"color": "DarkSlateGrey"}),
                dcc.Graph(
                figure=fig),
                html.H3(f'UCUR at {map_selection}', style={"color": "DarkSlateGrey"}),
                dcc.Graph(
                figure=fig2)],
                style={'backgroundColor': BODY_BACKGROUND_COLOUR}
                )

def temperature(map_selection, fig):
    csv_files = PATH.joinpath(os.path.abspath(os.curdir) + "/csv/temp").resolve()
    for file in os.listdir(csv_files):
        mooring_site = file[0:6]
        if mooring_site in MOORINGS and mooring_site == map_selection:
            csv_file = pd.read_csv(csv_files.joinpath(map_selection + '_temp.csv'))
            fig.add_trace(go.Scatter(x=csv_file['TIME'], y=csv_file['TEMP'], name="NEMO"))
            return \
                html.Div(
                    [html.H3(f'Temperature at {map_selection}',
                             style={"color": "DarkSlateGrey",
                                    "display": "inline-block",
                                    "width": "40%",
                                    "margin-left": "20px",
                                    "verticalAlign": "top"}),
                     more_info_button()],
                ), \
                dcc.Graph(
                    id='ucur_tab', figure=fig)
            # style={'backgroundColor': BODY_BACKGROUND_COLOUR})

def daily_temperature(map_selection, fig):
    csv_files = PATH.joinpath(os.path.abspath(os.curdir) + "/csv/daily_temp").resolve()
    for file in os.listdir(csv_files):
        mooring_site = file[0:6]
        if mooring_site in MOORINGS and mooring_site == map_selection:
            csv_file = pd.read_csv(csv_files.joinpath(map_selection + '_temp_dayavg.csv'))
            fig.add_trace(go.Scatter(x=csv_file['TIME'], y=csv_file['TEMP'], name="NEMO"))
            return html.H3(f'Daily averaged temperature at {map_selection}',
                           style={"color": "DarkSlateGrey"}), dcc.Graph(id='daily_temp_tab', figure=fig)

def climatology(map_selection, fig):
    nc_files = PATH.joinpath(os.path.abspath(os.curdir) + "/nc").resolve()
    if map_selection not in ['TAN100', 'GBRPPS', 'GBRMYR']:
        map_selection = 'GBRMYR'
    for file in os.listdir(nc_files):
        nc_file = xr.open_dataset(nc_files.joinpath('GBRMYR_LTSP_gridded_daily_MC.nc'))
        fig.add_trace(go.Contour(z=nc_file['CLIM'],
                                 x=nc_file['TIME'],
                                 transpose=True,
                                 line_width=0,
                                 zmax=35,
                                 zmin=10,
                                 ncontours=40,
                                 ))
        fig['layout']['yaxis']['autorange'] = "reversed"
        fig.update_xaxes(title_text='Time')
        fig.update_yaxes(title_text='Depth')
        return html.Div([html.H3(f'Climatology at {map_selection}',
                                 style={"color": "DarkSlateGrey"}), dcc.Graph(id='climatology_tab', figure=fig)])

def gridded_temperature(map_selection, fig):
    nc_files = PATH.joinpath(os.path.abspath(os.curdir) + "/assets/data/gridded/GBRMYR").resolve()
    if map_selection not in ['TAN100', 'GBRPPS', 'GBRMYR']:
        map_selection = 'GBRMYR'
    for file in os.listdir(nc_files):
        nc_file = xr.open_dataset(nc_files.joinpath(map_selection + '_LTSP_gridded_daily_MC.nc'))
        fig.add_trace(go.Contour(z=nc_file['TEMP'],
                                 x=nc_file['TIME'],
                                 transpose=True,
                                 line_width=0,
                                 zmax=35,
                                 zmin=10,
                                 ncontours=40,
                                 ))
        fig['layout']['yaxis']['autorange'] = "reversed"
        fig.update_xaxes(title_text='Time')
        fig.update_yaxes(title_text='Depth')
        return html.H3(f'Gridded temperature at {map_selection}',
                       style={"color": "DarkSlateGrey"}), dcc.Graph(id='gridded_temp_tab', figure=fig)

def daily_velocity(map_selection, fig, fig2):

    nc_files = PATH.joinpath(os.path.abspath(os.curdir) + "/assets/data/gridded/TAN100").resolve()
    for file in os.listdir(nc_files):
        nc_file = xr.open_dataset(nc_files.joinpath('TAN100_LTSP_VV_daily.nc'))
        fig.update_xaxes(title_text='Time')
        fig.update_yaxes(title_text='Depth')
        fig2.update_xaxes(title_text='Time')
        fig2.update_yaxes(title_text='Depth')
        rotated_degs = "{:.2f}".format(nc_file['VV'].attrs['reference_datum degrees'])
        # fig = make_subplots(
        #     # rows=4, cols=1,
        #     rows=2, cols=1,
        #     subplot_titles=(
        #         # f'Daily East velocity at {map_selection}',
        #         # f'Daily North velocity at {map_selection}',
        #         f'Daily Cross-Shelf velocity at {map_selection} (Theta deg CW from N)',
        #         f'Daily Alongshore velocity at {map_selection}  (Theta deg CW from E)'
        #     ))
        # fig_layout(fig)
        # fig.add_trace(go.Contour(z = nc_file['UCUR'],
        #                          x=nc_file['TIME'],
        #                          transpose=True,
        #                          line_width=0,
        #                          # colorscale = ([0, 'rgb(0,0,255)'], [1, 'rgb(0,255,0)']),
        #                          zmax=1,
        #                          zmin=-1,
        #                          ncontours=40,
        #                          ),
        #               row=1, col=1
        #               )
        # fig['layout']['yaxis']['autorange'] = "reversed"
        # fig.update_xaxes(title_text='Time')
        # fig.update_yaxes(title_text='Depth')
        # fig.add_trace(go.Contour(z=nc_file['VCUR'],
        #                           x=nc_file['TIME'],
        #                           transpose=True,
        #                           line_width=0,
        #                           # colorscale = ([0, 'rgb(0,0,255)'], [1, 'rgb(0,255,0)']),
        #                           zmax=1,
        #                           zmin=-1,
        #                           ncontours=40,
        #                           ),
        #               row=2, col=1
        #                )

        fig.add_trace(go.Contour(z=nc_file['UU'],
                                 y=nc_file['DEPTH'],
                                 x=nc_file['TIME'],
                                 transpose=True,
                                 line_width=0,
                                 # colorscale = ([0, 'rgb(0,0,255)'], [1, 'rgb(0,255,0)']),
                                 zmax=1,
                                 zmin=-1,
                                 ncontours=40,
                                 ),
                      # row=1, col=1
                      )

        fig2.add_trace(go.Contour(z=nc_file['VV'],
                                 y=nc_file['DEPTH'],
                                 x=nc_file['TIME'],
                                 transpose=True,
                                 line_width=0,
                                 # colorscale = ([0, 'rgb(0,0,255)'], [1, 'rgb(0,255,0)']),
                                 zmax=1,
                                 zmin=-1,
                                 ncontours=40,
                                 ),
                      # row=2, col=1
                      )
        fig.update_layout(height=300,
                          width=1000,
                          title=f"Daily Cross-Shore velocity at {map_selection} ({rotated_degs}{DEGREES_SYMBOL} CW from N)"
                          )
        fig2.update_layout(height=300,
                          width=1000,
                           title=f"Daily Alongshore velocity at {map_selection} ({rotated_degs}{DEGREES_SYMBOL} CW from E)"
                          )
        return \
            html.Div(
                [html.H3(f'Gridded Daily Velocities at {map_selection}',
                         style={"color": "DarkSlateGrey",
                                "display": "inline-block",
                                "width": "40%",
                                "margin-left": "20px",
                                "verticalAlign": "top"}),
                 more_info_button()],
            ), \
            dcc.Graph(id='local_vel_tab', figure=fig,
                      # title=f"Daily Cross-Shelf velocity at {map_selection} (Theta deg CW from E)"
                      ), \
            dcc.Graph(id='local_vel_tab', figure=fig2,
                      # title=f"Daily Alongshore velocity at {map_selection} (Theta deg CW from E)"
                      ),
            # html.H3(f'Daily Velocity Plot (North)', style={"color": "DarkSlateGrey"}), \
        # dcc.Graph(id='vel_tab', figure=fig2), \
        # html.H3(f'Daily Velocity Plot (Cross-Shelf)', style={"color": "DarkSlateGrey"}), \
        # dcc.Graph(id='vel_tab', figure=fig3), \
        # html.H3(f'Daily Velocity Plot (Alongshore)', style={"color": "DarkSlateGrey"}), \
        # dcc.Graph(id='vel_tab', figure=fig4)

# print("Always executed")

# if __name__ == '__main__':
#     app.run_server(debug=False)

# if __name__ == '__main__':
#     app.run_server(host='0.0.0.0', port=8080, debug=False, use_reloader=False)