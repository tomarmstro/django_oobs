#!/usr/bin/env python

# Imports
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import os
import plotly.graph_objects as go
import xarray as xr
import plotly.express as px
import pandas as pd
import plotly.io as pio
import pathlib

#importing python scripts
import getLTSPname

# ---------------------------------------------------------------
# Constants etc
external_stylesheets = [dbc.themes.LUMEN, "assets/base-styles.css"]
pio.templates.default = "simple_white"
px.defaults.color_continuous_scale = px.colors.sequential.Blackbody

DATA_SKIP = 500

#Colours
TRANSPARENT_COLOUR = "rgba(0, 0, 0, 0)"
IMOS_DEEP_BLUE_COLOUR = "#3b6e8f"
IMOS_SEA_BLUE_COLOUR = "#54bceb"
IMOS_SAND_COLOUR = "#d9d7bd"
IMOS_MID_GREY_COLOUR = "#3c3c3c"
BODY_BACKGROUND_COLOUR = IMOS_SAND_COLOUR
BODY_BORDER_COLOUR = IMOS_MID_GREY_COLOUR
map_colours = ['#11c216', '#808080']

DEGREES_SYMBOL = u'\xb0'

PATH = pathlib.Path(__file__).parent

pd.set_option('display.max_rows', None)
app = DjangoDash('data', external_stylesheets=external_stylesheets)

#Site names
GBR = ['GBRLSL', 'GBRLSH', 'GBRMYR', 'GBRPPS', 'GBRHIS', 'GBROTE', 'GBRCCH', 'GBRELR', 'GBRHIN']
NWS = ['NWSROW', 'NWSLYN', 'NWSBAR', 'NWSBRW', 'TAN100']
NRS = ['NRSYON', 'NRSDAR', 'NRSKAI', 'NRSMAI', 'NRSNIN', 'NRSROT', 'NRSNSI']
ITF = ['ITFFTB', 'ITFMHB', 'ITFTIS', 'ITFJBG']
KIM = ['KIM050', 'KIM100', 'KIM400'] #KIM200?
CAM = ['CAM050', 'CAM150'] #CAM100 or CAM150?
PIL = ['PIL050', 'PIL100', 'PIL200']
MOORINGS = GBR + NWS + NRS + ITF + KIM + CAM + PIL
# MOORINGS = ['GBRLSL', 'GBRLSH', 'GBRMYR', 'GBRPPS', 'GBRHIS', 'GBROTE', 'GBRCCH', 'GBRELR', 'GBRHIN', 'NWSROW', 'NWSLYN', 'NWSBAR', 'NWSBRW', 'TAN100', 'NRSYON', 'NRSDAR']
map_selection = "TAN100"
active_tab = 'vcur_tab'


# Create map
def render_map():
    map_data = pd.read_excel('sites.xlsx')
    map_data = pd.DataFrame(map_data)
    map_data = map_data.drop(columns=['x', 'y'])
    return [dcc.Graph(id='moorings_map', figure=px.scatter_mapbox
        (
        map_data,
        lat=map_data['Latitude'],
        lon=map_data['Longitude'],
        color='Group',
        size=map_data['d'],
        size_max=10,
        color_discrete_sequence=map_colours,
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
# def collect_working_files(variable):
#     working_files = []
#     for mooring in MOORINGS:
#         if variable == 'velocity-hourly':
#             LTSP_filename = (getLTSPname.getLTSPfileName(mooring, variable))
#         elif variable == 'aggregated':
#             LTSP_filename = (getLTSPname.getLTSPfileName(mooring, variable))
#         else:
#             print('incorrect variable for collecting files')
#         print(LTSP_filename.split("timeseries/", 1)[1])
#         working_files.append(LTSP_filename)
#     return working_files

#Build main tabs (Velocity and Temperature)
def build_tabs():
    return dbc.Tabs(
        [
            dbc.Tab(label='Velocity',
                    tab_id='vel_tab',
                    tabClassName="flex-grow-1 text-center",
                    active_label_style={
                        "backgroundColor": IMOS_DEEP_BLUE_COLOUR,
                        "color": "white"
                    },
                        label_style={
                            'border-color': IMOS_DEEP_BLUE_COLOUR,
                        }),
            dbc.Tab(label='Temperature',
                    tab_id='temp_tab',
                    tabClassName="flex-grow-1 text-center",
                    active_label_style={
                        "backgroundColor": IMOS_DEEP_BLUE_COLOUR,
                        "color": "white"
                    },
                        label_style={
                            'border-color': IMOS_DEEP_BLUE_COLOUR,
                        }),
        ],
        id='tabs',
        active_tab="vel_tab",
        # style={'width': "100%"},
        className="custom-tabs"
    )

# Basic figure layout
def fig_layout(fig):
    fig.update_layout(
        plot_bgcolor=BODY_BACKGROUND_COLOUR,
        paper_bgcolor=BODY_BACKGROUND_COLOUR,
        font_color=BODY_BORDER_COLOUR,
        # plot_bgcolor = IMOS_MID_GREY_COLOUR,
        # paper_bgcolor = IMOS_MID_GREY_COLOUR,
        # font_color = IMOS_SAND_COLOUR,
        margin=dict(t=50)
    )

#Build Velocity Tabs
vel_tabs = html.Div(
    [dbc.Tabs(
        [
            dbc.Tab(
            label="Cross and Alongshore",
            tab_id="cross_alongshore_tab",
            # tabClassName="flex-grow-1 text-center",
            active_label_style={
                "backgroundColor": IMOS_DEEP_BLUE_COLOUR,
                "color": "white"
                },
            label_style={
                'border-color': IMOS_DEEP_BLUE_COLOUR,
                }
            ),
            dbc.Tab(
            label="North/East",
            tab_id="ne_tab",
            # tabClassName="flex-grow-1 text-center",
            active_label_style={
                "backgroundColor": IMOS_DEEP_BLUE_COLOUR,
                "color": "white"
                },
            label_style={
                'border-color': IMOS_DEEP_BLUE_COLOUR,
                }
            ),
        ],
        id="vel_tabs",
        active_tab="cross_alongshore_tab",
        className="custom-tabs",
    )])

#Build Temperature Tabs
temp_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Climatology",
                        tab_id="climatology_tab",
                        # tabClassName="flex-grow-1 text-center",
                        active_label_style={
                            "backgroundColor": IMOS_DEEP_BLUE_COLOUR,
                            "color": "white"
                        },
                        label_style={
                            'border-color': IMOS_DEEP_BLUE_COLOUR,
                        }),
                dbc.Tab(label="Gridded Temperature",
                        tab_id="gridded_temp_tab",
                        # tabClassName="flex-grow-1 text-center",
                        active_label_style={
                            "backgroundColor": IMOS_DEEP_BLUE_COLOUR,
                            "color": "white"
                        },
                        label_style={
                            'border-color': IMOS_DEEP_BLUE_COLOUR,
                        }),
                dbc.Tab(label="Anomaly",
                        tab_id="anomaly_tab",
                        # tabClassName="flex-grow-1 text-center",
                        active_label_style={
                            "backgroundColor": IMOS_DEEP_BLUE_COLOUR,
                            "color": "white"
                        },
                        label_style={
                            'border-color': IMOS_DEEP_BLUE_COLOUR,
                        }),
            ],
            id="temp_tabs",
            active_tab="climatology_tab",
        ),
        # html.Div(id="temp_tab_content"),
    ]
)

#Build map popup/modal
map_modal_style = ({"backgroundColor": IMOS_DEEP_BLUE_COLOUR, 'color': 'white'})
map_modal = html.Div(
    [
        dbc.Row(dbc.Button("Select Mooring", id="open-map-modal", color='primary', size="lg"), justify="center", align="center"),
        dbc.Modal(
            [
                dbc.ModalHeader(html.H2("Please select a mooring location"),
                              style = map_modal_style),
                # dbc.ModalBody(f"Selected mooring: {map_selection}"),
                dbc.ModalBody(render_map(),
                              style = map_modal_style),
                dbc.ModalFooter(dbc.Button("Close", id="close-dismiss"),
                              style = map_modal_style),
            ],
            id="map_modal",
            style={"max-width": "none", "width": "90%", "backgroundColor": IMOS_MID_GREY_COLOUR})
            # is_open=False,
        # ),
    ]
)

# Callback and toggle for map modal
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

#Velocity tabs more info button and popup/modal
info_modal_style = ({"backgroundColor": IMOS_DEEP_BLUE_COLOUR, 'color': 'white'})
vel_more_info_modal = html.Div(
    [
        dbc.Button("Info",
            id="open-vel-more-info-modal",
            n_clicks=0,
            color='info',
            style={"color": "DarkSlateGrey",
                  "display": "inline-block",
                  "width": "10%",
                  "margin-right": "150px",
                  "verticalAlign": "top",
                  "right": "0px",
                  "position": "absolute"})
            ,
        dbc.Modal(
            [
                dbc.ModalHeader(html.H2("Velocity Information"),
                                style = info_modal_style
                                # style={"backgroundColor": IMOS_MID_GREY_COLOUR}
                                ),
                dbc.ModalBody("*Placeholder for velocity information*",
                                style = info_modal_style),
                dbc.ModalFooter(dbc.Button("Close", id="vel-close-dismiss"),
                                style = info_modal_style
                ),
            ],
            centered=True,
            id="vel_more_info_modal",
            style={"max-width": "none", "width": "90%"})
            # is_open=False,
    ]
)

#Velocity tabs more info popup callback
@app.callback(
    Output(component_id="vel_more_info_modal", component_property="is_open"),
    [Input(component_id="open-vel-more-info-modal", component_property="n_clicks"),
     Input(component_id="vel-close-dismiss", component_property="n_clicks")],
    State(component_id="vel_more_info_modal", component_property="is_open"),
)
def toggle_vel_more_info_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

#Temperature more info modal/popup
temp_more_info_modal = html.Div(
    [
        dbc.Button("Info",
            id="open-temp-more-info-modal",
            n_clicks=0,
            color='info',
            style={"color": "DarkSlateGrey",
                  "display": "inline-block",
                  "width": "10%",
                  "margin-right": "150px",
                  "verticalAlign": "top",
                  "right": "0px",
                  "position": "absolute"})
            ,
        dbc.Modal(
            [
                dbc.ModalHeader(html.H2("Temperature Information"),
                                style = info_modal_style
                                # style={"backgroundColor": IMOS_MID_GREY_COLOUR}
                                ),
                dbc.ModalBody("*Placeholder for temperature information*",
                                style = info_modal_style),
                dbc.ModalFooter(dbc.Button("Close", id="temp-close-dismiss"),
                                style = info_modal_style
                ),
            ],
            centered=True,
            id="temp_more_info_modal",
            style={"max-width": "none", "width": "90%"})
            # is_open=False,
    ]
)

#Temperature more info callback
@app.callback(
    Output(component_id="temp_more_info_modal", component_property="is_open"),
    [Input(component_id="open-temp-more-info-modal", component_property="n_clicks"),
     Input(component_id="temp-close-dismiss", component_property="n_clicks")],
    State(component_id="temp_more_info_modal", component_property="is_open"),
)
def toggle_temp_more_info_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

#Velocity Colour rangeslider to change contour plot colour range (z-axis)
contour_rangeslider = html.Div(
    [
    html.H4("Adjust colour range"),
    dcc.RangeSlider(
        min=-1, max=1, step=0.01, value=[-0.25, 0.25], id='slider', allowCross=False,
        marks={
            -1: {'label': -1},
            1: {'label': 1}
            },
        tooltip={
            "placement": "bottom",
            },
        ),
    ])

#Velocity colour rangeslider callback
@app.callback(
    Output('slider-output', 'children'),
    [Input('slider', 'value')])
def update_output(value):
    return value

#Temperature Colour rangeslider to change contour plot colour range (z-axis)
temp_contour_rangeslider = html.Div(
    [
    html.H4("Adjust colour range"),
    dcc.RangeSlider(
        min=0, max=40, step=1, value=[20, 32], id='temp_slider', allowCross=False,
        marks={
            0: {'label': 0},
            40: {'label': 40}
            },
        tooltip={
            "placement": "bottom",
            },
        ),
    ])

#Temperature colour rangeslider callback
@app.callback(
    Output('temp-slider-output', 'children'),
    [Input('temp_slider', 'value')])
def update_output(value):
    return value

#Dates slider for contour plots
dates_rangeslider = html.Div(
            [
            html.H4("Adjust date range"),
            dcc.RangeSlider(min=2005, max=2022, step=1, value=[2015, 2016], id='date_slider', allowCross=False,
                            marks={
                                2005: {'label': 2005},
                                2022: {'label': 2022}},
                            tooltip={
                                "placement": "bottom",
                                # "always_visible": True
                            },
                            ),
                html.Div(id='date-slider-output')
            ])

#Dates slider callback
@app.callback(
    Output('date-slider-output', 'children'),
    [Input('date_slider', 'date_value')])
def update_date(date_value):
    return date_value

#Download button
def download_button(map_selection, variable):
    if map_selection not in MOORINGS:
        map_selection = 'TAN100'
    thredds_path = "http://thredds.aodn.org.au//thredds/fileServer/IMOS/ANMN/"
    LTSP_filename = (getLTSPname.getLTSPfileName(map_selection, variable))
    downloadable_file = (LTSP_filename.split("IMOS/ANMN/", 1)[1])
    download_href = thredds_path + downloadable_file
    print(download_href)
    download_button = html.Div(
        [dbc.Row(
            dbc.Button(
                "Download",
                href=download_href,
                download=downloadable_file,
                external_link=True,
                color="primary", size="lg"), justify="center", align="center"),
        ],
    )
    return download_button

# Plotly/Dash Main App Layout
app.layout = html.Div(
    # style={"backgroundColor": DARK_BLUE_COLOUR, 'display': 'inline-block', 'width': '100%'},
    id="container",
    children=[
        html.Br(),
        map_modal,
        html.Br(),

        build_tabs(),
        # velocity_toggle(),
        html.Div(id='tab_content',
                 className="p-4"
            ),
        html.Br(),
        ],
    style={
        'width': '100%',
        'height': '80%',
        'backgroundColor': BODY_BACKGROUND_COLOUR,
        'padding-right': '100px',
        'padding-left': '0px',
        'padding-bottom': '00px',
        'margin-bottom': '0px',
        'display': 'inline-block',
        'vertical-align': 'center'
        }
    )

#Main tabs callback (Velocity/Temperature Tabs and Map Selection
@app.callback(
    Output(component_id='tab_content', component_property='children'),
    [Input(component_id='tabs', component_property='active_tab'),
    Input(component_id="moorings_map", component_property="clickData")])
def render_tab_content(active_tab, clickData):
    fig = go.Figure()
    fig_layout(fig)
    fig2 = go.Figure()
    fig_layout(fig2)
    map_selection = 'TAN100'
    if clickData is not None:
        map_selection = clickData['points'][0]['hovertext']
        print(f"{map_selection} selected from the map.")
    print(f"{active_tab} selected.")
    if active_tab == 'vel_tab':
        return vel_tabs, html.Div(id='vel_tab_content'), contour_rangeslider, dates_rangeslider, download_button(map_selection, "velocity-hourly"),
    if active_tab == 'temp_tab':
        return temp_tabs, html.Div(id='temp_tab_content'), temp_contour_rangeslider, dates_rangeslider

#Velocity Tab Callback
@app.callback(Output(component_id="vel_tab_content", component_property="children"),
              [Input(component_id="vel_tabs", component_property="active_tab"),
               Input(component_id="moorings_map", component_property="clickData"),
               Input(component_id='slider', component_property='value'),
               Input(component_id='date_slider', component_property='value')]
               )
def sub_velocity_tabs(vel_tabs, clickData, value, date_slider):
    print("slider value is: ", value)
    print("date value is: ", date_slider)
    fig = go.Figure()
    fig_layout(fig)
    fig2 = go.Figure()
    fig_layout(fig2)
    map_selection = 'TAN100'
    if clickData is not None:
        map_selection = clickData['points'][0]['hovertext']
        print(f"{map_selection} selected from the map.")
    print(f"{vel_tabs} selected.")
    if vel_tabs == "cross_alongshore_tab":
        return cross_along_velocity_tab_content(map_selection, fig, fig2, value, date_slider, vel_tabs)
    elif vel_tabs == "ne_tab":
        return north_east_velocity_tab_content(map_selection, fig, fig2, value, date_slider, vel_tabs)
    # return html.P("This shouldn't ever be displayed...")

#Temperature Tab Callback
@app.callback(Output(component_id="temp_tab_content", component_property="children"),
              [Input(component_id="temp_tabs", component_property="active_tab"),
               Input(component_id="moorings_map", component_property="clickData"),
               Input(component_id='temp_slider', component_property='value'),
               Input(component_id='date_slider', component_property='value')])
def sub_temperature_tabs(temp_tabs, clickData, value, date_slider):
    fig = go.Figure()
    fig_layout(fig)
    fig2 = go.Figure()
    fig_layout(fig2)
    map_selection = 'TAN100'
    if clickData is not None:
        map_selection = clickData['points'][0]['hovertext']
        print(f"{map_selection} selected from the map.")
    print(f"{temp_tabs} selected.")
    if temp_tabs == "climatology_tab":
        return climatology(map_selection, fig, value, date_slider, temp_tabs)
    elif temp_tabs == "gridded_temp_tab":
        return gridded_temperature(map_selection, fig, value, date_slider, temp_tabs)
    elif temp_tabs == "anomaly_tab":
        return anomaly(map_selection, fig, value, date_slider, temp_tabs)
    return html.P("This shouldn't ever be displayed...")

#Cross/Alongshore Velocity Tab
def cross_along_velocity_tab_content(map_selection, fig, fig2, value, date_slider, vel_tabs):
    while True:
        try:
            render_plots(map_selection=map_selection, start_time=str(date_slider[0]), end_time=str(date_slider[1]), zmax=value[1], zmin=value[0], ncontours=40,
                         directory='VV', file_prefix='_VV_daily.nc', fig=fig, variable='UU', fig2=fig2, variable_2='VV', vel_tabs=vel_tabs)
            return \
                html.Br(), \
                html.Div(
                    dbc.Row([html.H3(f'Gridded Daily Velocities at {map_selection}',
                    style={"color": "DarkSlateGrey",
                        "display": "inline-block",
                        "width": "40%",
                        "margin-left": "20px",
                        "verticalAlign": "top",
                        'backgroundColor': BODY_BACKGROUND_COLOUR}),
                    vel_more_info_modal],
                    justify="left", align="start")), \
                dcc.Graph(
                    id='local_vel_tab', figure=fig2,
                ), \
                dcc.Graph(
                    id='local_vel_tab', figure=fig,
                    )
        except FileNotFoundError:
            return html.Br(), html.H1("Error: File not found.")

#North/East Velocity Tab
def north_east_velocity_tab_content(map_selection, fig, fig2, value, date_slider, vel_tabs):
    while True:
        try:
            render_plots(map_selection=map_selection, start_time=str(date_slider[0]), end_time=str(date_slider[1]), zmax=value[1], zmin=value[0], ncontours=40, directory='VV', file_prefix='_VV_daily.nc', fig=fig,
                         variable='UCUR', fig2=fig2, variable_2='VCUR', vel_tabs=vel_tabs)
            return \
                html.Br(), \
                    html.Div(
                        dbc.Row([html.H3(f'Gridded Daily Velocities at {map_selection}',
                            style={
                                "color": "DarkSlateGrey",
                                "display": "inline-block",
                                "width": "40%",
                                "margin-left": "20px",
                                "verticalAlign": "top"}),
                         vel_more_info_modal],
                        justify="left", align="start")), \
                        dcc.Graph(id='local_vel_tab', figure=fig2,
                          ), \
                        dcc.Graph(id='local_vel_tab', figure=fig)
        except FileNotFoundError:
            return html.Br(), html.H1("Error: File not found.")

#Climatology Tab
def climatology(map_selection, fig, value, date_slider, temp_tabs):
    while True:
        try:
            render_plots(map_selection=map_selection, start_time='2015', end_time=None, zmax=value[1], zmin=value[0], ncontours=40,
                         directory='CLIM', file_prefix='_CLIM.nc', fig=fig,
                         variable='CLIM', fig2=None, variable_2=None, temp_tabs=temp_tabs)
            fig.update_xaxes(title_text='Time',
                             tickformat="%B")
            fig.update_layout(
                height=450)
            return html.Br(),\
                html.Div(
                    dbc.Row([html.H3(f'Climatology at {map_selection}',
                        style={"color": "DarkSlateGrey",
                            "display": "inline-block",
                            "width": "40%",
                            "margin-left": "20px",
                            "verticalAlign": "top"}),
                    temp_more_info_modal],
                    justify="left", align="start")), \
                    dcc.Graph(id='climatology_tab', figure=fig),
        except FileNotFoundError:
            return html.Br(), html.H1("Error: File not found.")

#Gridded Temperature Tab
def gridded_temperature(map_selection, fig, value, date_slider, temp_tabs):
    while True:
        try:
            render_plots(map_selection=map_selection, start_time=str(date_slider[0]), end_time=str(date_slider[1]), zmax=value[1], zmin=value[0], ncontours=40,
                         directory='CLIM', file_prefix='_TEMP_daily.nc', fig=fig, variable='TEMP', fig2=None,
                         variable_2=None, temp_tabs=temp_tabs)
            fig.update_layout(
                height=450)
            return \
                html.Br(),\
                html.Div(
                    dbc.Row(
                        [html.H3(f'Gridded temperature at {map_selection}',
                            style={"color": "DarkSlateGrey",
                                "display": "inline-block",
                                "width": "40%",
                                "margin-left": "20px",
                                "verticalAlign": "top"}
                            ),
                        temp_more_info_modal,
                        ],
                        justify="left", align="start")
                    ), \
                dcc.Graph(id='gridded_temp_tab', figure=fig)
        except FileNotFoundError:
            return html.Br(), html.H1("Error: File not found.")

#Anomaly Tab
def anomaly(map_selection, fig, value, date_slider, temp_tabs):
    while True:
        try:
            render_plots(map_selection=map_selection, start_time=str(date_slider[0]), end_time=str(date_slider[1]), zmax=2.5, zmin=-2.5, ncontours=20,
                         directory='CLIM', file_prefix='_TEMP_daily.nc', fig=fig, variable='CLIM', fig2=None, variable_2='TEMP', temp_tabs=temp_tabs)
            fig.update_xaxes(title_text='Time',
                             # tickformat="%B"
                             )
            fig.update_layout(
                height=450)
            return html.Br(),\
                html.Div(dbc.Row([html.H3(f'Temperature anomalies at {map_selection}',
                    style={"color": "DarkSlateGrey",
                        "display": "inline-block",
                        "width": "40%",
                        "margin-left": "20px",
                        "verticalAlign": "top"}),
                    temp_more_info_modal],
                    justify="left", align="start")), dcc.Graph(id='anomaly_tab', figure=fig)
        except FileNotFoundError:
            return html.Br(), html.H1("Error: File not found.")

#Build/Render Plots function - Built into each tab for plotting all contour plots
def render_plots(map_selection, start_time, end_time, zmax, zmin, ncontours, directory, file_prefix, fig,  variable, fig2=None, variable_2=None, temp_tabs=None, vel_tabs=None):
    nc_files = PATH.joinpath(os.path.abspath(os.curdir) + "/assets/data/" + directory).resolve()
    # if map_selection not in MOORINGS:
    #     print("TAN100 Selected by Default")
    #     map_selection = 'TAN100'
    nc_file = xr.open_dataset(nc_files.joinpath(map_selection + file_prefix))
    if temp_tabs != "climatology_tab":
        nc_file = nc_file.sel(TIME=slice(start_time, end_time))

    if vel_tabs == "cross_alongshore_tab":
        nc_file = nc_file.sel(TIME=slice(start_time, end_time))
        rotated_degs = nc_file[directory].attrs['reference_datum degrees']
        fig.update_layout(title=f"Daily Cross-Shore Velocity at ({round(rotated_degs)}{DEGREES_SYMBOL} CW from N)")
        fig2.update_layout(title=f"Daily Along-Shore Velocity at ({round(rotated_degs)}{DEGREES_SYMBOL} CW from N)")
    if vel_tabs == "ne_tab":
        nc_file = nc_file.sel(TIME=slice(start_time, end_time))
        fig.update_layout(title=f"Daily North-South Velocity")
        fig2.update_layout(title=f"Daily East-West Velocity")
    z1 = nc_file[variable]
    if variable_2 is not None:
        z2 = nc_file[variable_2]
        if temp_tabs == "anomaly_tab":
            z1 = nc_file[variable_2] - nc_file[variable]
    fig.add_trace(
        go.Contour(
            z=z1,
            y=nc_file['DEPTH'],
            x=nc_file['TIME'],
            transpose=True,
            line_width=0,
            # colorscale = ([0, 'rgb(0,0,255)'], [1, 'rgb(0,255,0)']),
            zmax=zmax,
            zmin=zmin,
            ncontours=ncontours,
            y0=0,
        ),
        # row=1, col=1
    )
    fig['layout']['yaxis']['autorange'] = "reversed"
    fig.update_layout(
        height=300,
        width=1000,
        margin=dict(t=50),
        # yaxis_range=(0, max(nc_file['DEPTH']))
    )
    # fig.update(layout_yaxis_range=(0, max(nc_file['DEPTH'])))
    fig.update_xaxes(title_text='Time')
    fig.update_yaxes(title_text='Depth', range=[3, 9])
    if fig2 is not None:
        fig2.update_xaxes(title_text='Time')
        fig2.update_yaxes(title_text='Depth')
        fig2.add_trace(
            go.Contour(
                z=z2,
                y=nc_file['DEPTH'],
                x=nc_file['TIME'],
                transpose=True,
                line_width=0,
                # colorscale = ([0, 'rgb(0,0,255)'], [1, 'rgb(0,255,0)']),
                zmax=zmax,
                zmin=zmin,
                ncontours=ncontours,
            ),
            # row=2, col=1
        )
        fig2['layout']['yaxis']['autorange'] = "reversed"
        fig2.update_layout(
            height=300,
            width=1000,
            margin=dict(t=50)
        )
