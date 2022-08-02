#!/usr/bin/env python


# Imports
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
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
# from tqdm import tqdm, trange
# from time import sleep
# from tqdm import tqdm
# import json
import pathlib

from django_oobs.dash_apps.finished_apps import map_app

# ---------------------------------------------------------------
# Constants etc
external_stylesheets = [dbc.themes.LUMEN]
# https://hellodash.pythonanywhere.com/theme_change_components
pio.templates.default = "simple_white"
px.defaults.color_continuous_scale = px.colors.sequential.Blackbody

DATA_SKIP = 500
# DATA_PATH = r"37\\"
# DATA_PATH = 'http://thredds.aodn.org.au/thredds/dodsC/IMOS/ANMN/'
TRANSPARENT_COLOUR = "rgba(0, 0, 0, 0)"
DARK_BLUE_COLOUR = "#1e2130"

pd.set_option('display.max_rows', None)
app = DjangoDash('temperature_app', external_stylesheets=external_stylesheets)



MOORINGS = ['GBRMYR', 'GBRPPS', 'GBRLSL', 'GBRHIS', 'GBROTE', 'GBRCCH', 'NWSBAR', 'NWSLYN', 'NWSROW', 'NWSBRW',
            'NRSYON']
print("Running Dashboard Prototype...")
# map_selection = "NRSYON"
# print("IT WORKED! MAP SELECTION IS :", map_app.render_tab_content)

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
        mapbox_style="open-street-map", height=750, width=1100,
        # Remove legend
        showlegend=False, ),
        # stop zoomable map
        config={'scrollZoom': False}
        )]


# def render_dropdown():
#     mooring_options = []
#     for option in MOORINGS:
#         mooring_options.append({'label': option, 'value': option})
#     return dcc.Dropdown(
#         id='my_dropdown',
#         options=mooring_options,
#         value=MOORINGS[10],
#         style={'width': "80%"})


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
        # working_files = ['http://thredds.aodn.org.au/thredds/dodsC/IMOS/ANMN/QLD/NWSBRW/hourly_timeseries/IMOS_ANMN-QLD_VZ_20190731_NWSBRW_FV02_velocity-hourly-timeseries_END-20210505_C-20211221.nc']
    return working_files


##########################################################
# vel_working_files = collect_working_files('velocity-hourly')
# agg_working_files = collect_working_files('aggregated')
# print(agg_working_files[0])
##########################################################


def get_local_files(dropdown_selection):
    local_files = []
    for file in os.listdir(DATA_PATH):
        if file.startswith(dropdown_selection):
            local_files.append(file)

    local_file_ds = xr.open_dataset(r"37\\NRSYON-2006_ADCP_vel.nc")
    local_file_df = local_file_ds.to_dataframe()
    return local_file_df


def get_local_files2(dropdown_selection):
    local_files = []
    for file in os.listdir(DATA_PATH):
        if file.startswith(dropdown_selection):
            local_files.append(file)

    local_file_ds = xr.open_dataset(r"37\\NWSROW-2002_ADCP_2.nc")
    local_file_df = local_file_ds.to_dataframe()
    return local_file_df


def build_tabs():
    return dbc.Tabs(
        [
            dbc.Tab(render_map(),
                    label='map_select', tab_id='map_tab', ),
            dbc.Tab(label='Velocity', tab_id='vcur_tab'),
            dbc.Tab(label='Temperature', tab_id='temp_tab'),
            dbc.Tab(label='Daily Temperature', tab_id='daily_temp_tab'),
            dbc.Tab(label='Climatology', tab_id='climatology_tab'),
            dbc.Tab(label='Gridded Temperature', tab_id='gridded_temp_tab'),
            dbc.Tab(label='Daily Velocity', tab_id='daily_vel_tab'),



            # dcc.Tab(label='Map', value='map'),
        ],
        id='tabs',
        active_tab="map_tab",
        style={'width': "100%"},
        className="custom-tabs"
    )


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Ocean Observer Dashboard"),  ###Title
                    html.H6("Hourly IMOS Data"),  ###Heading under title
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.A(
                        html.Button(children="DATA SOURCE"),  ####Placeholder Button for something
                        href="https://thredds.aodn.org.au/thredds/catalog/IMOS/ANMN/QLD/catalog.html",
                        ###Url the button takes you to
                    ),
                    # html.Button(
                    #     id="learn-more-button", children="About/Help", n_clicks=0 ###About/Help Button top right
                    # ),
                    html.A(
                        html.Img(id="aims_logo", src=app.get_asset_url("aims_logo.jpg")),  #### logo top right
                        href="https://data.aims.gov.au/moorings/",
                    ),
                    html.A(
                        html.Img(id="imos_logo", src=app.get_asset_url("imos_logo.png")),  #### logo top right
                        href="https://imos.org.au/",
                    ),
                ],
            ),
        ],
    )


def fig_layout(fig):
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    fig.update_traces(marker=dict(size=12,
                                  line=dict(width=2,
                                            color='DarkSlateGrey')),
                      selector=dict(mode='markers'))


##################### MODAL #######################
# modal = html.Div(
#     [
#         dbc.Button("Extra large modal", id="open-xl", n_clicks=0),

#         dbc.Modal(
#             # dbc.ModalBody(["Map of IMOS moorings.",html.Br(),"Please select a mooring location."]),
#             html.Div(render_map(),
#         className="three columns", style={'display': 'inline-block', 'width': '80%'},
#         ),
#             # className="three columns", style={'display': 'inline-block', 'width': '80%'},
#             id="modal-xl",
#             size="xl",
#             centered=True,
#             is_open=False,
#             fade=False,
#                 ),
#             ]
#         )

# ---------------------------------------------------------------
# Layout
app.layout = html.Div(
    # style={"backgroundColor": DARK_BLUE_COLOUR, 'display': 'inline-block', 'width': '100%'},
    id="big-app-container",
    children=[
        # build_banner(),
        # render_dropdown(),
        # html.Br(),  ### Add a space
        build_tabs(),
        html.Div(id='tab_content'
                 , className="p-4", style={'display': 'inline-block', 'width': '100%'}
                 ),
        # html.Div(html.Pre(id='click-data'),
        #          className="three columns", style={'display': 'inline-block', 'width': '80%'},
        #     ),
        # modal,
    ],
)


######################################
###### MODAL ##########################
# def toggle_modal(n1, is_open):
#     if n1:
#         return not is_open
#     return is_open

# app.callback(
#     Output("modal-xl", "is_open"),
#     Input("open-xl", "n_clicks"),
#     State("modal-xl", "is_open"),
# )(toggle_modal)

########################################

# ---------------------------------------------------------------
# Get tab content
@app.callback(
    # Output(component_id="click-data", component_property="children"),
    Output(component_id='tab_content', component_property='children'),
    Input(component_id='tabs', component_property='active_tab'),
    Input(component_id="moorings_map", component_property="clickData"))
# Input(component_id='selected_time', component_property='active_time')])
def render_tab_content(active_tab, clickData):
    # print((LTSP_filename.split("IMOS/ANMN",1)[1])[5:11])
    # state = (LTSP_filename.split("IMOS/ANMN",1)[1])[1:4]
    # mooring = (LTSP_filename.split("IMOS/ANMN",1)[1])[5:11]
    # active_tab = 'salinity_tab'
    # map_selection = 'NRSYON'
    if clickData is not None:
        map_selection = clickData['points'][0]['hovertext']
        print(f"{map_selection} selected from the map.")

    print(active_tab)
    # print(collect_working_files())
    if active_tab == 'map_tab':
        return html.H3(f'Selected mooring: {map_selection}', style={"color": "DarkSlateGrey"})
    # if active_tab == 'bfgdbfgbfg':
    #     return render_map()
    file_counter = 0
    # fig_layout()

    # fig = go.Figure()
    # figs = make_subplots(rows=4, cols=1)
    # for file in os.listdir(DATA_PATH):
    # working_files = collect_working_files('velocity-hourly')
    # for file in vel_working_files:
    # for file in vel_working_files:
    #     try:
    #         print('dropdown selection: ', dropdown_selection)
    #         print('file: ', (file.split("IMOS/ANMN",1)[1])[5:11])
    #         if (file.split("IMOS/ANMN",1)[1])[5:11] == (str(dropdown_selection)):
    #             print("getting file")
    #             file_counter += 1
    #             # fig = go.Figure(layout_yaxis_range=[-0.4,0.3])
    #             fig = go.Figure()
    #             ds = xr.open_dataset(file)

    #             # df = df.groupby('TIME').mean().reset_index() #Averages per unique time
    #             print('plots created')
    #             print('active tab :', active_tab)
    #             # print(f"Loading file number {file_counter}: {day_avg.instrument_id} #{day_avg.instrument_index}")
    #             if active_tab == 'vcur_tab':
    #                 # print(file)
    #                 #LTSP
    #                 print(f"Creating {dropdown_selection} dataframe...")
    #                 df = ds.VCUR.to_dataframe()
    #                 print(f"Converting to daily timeseries...")
    #                 day_avg = df.groupby([df['TIME']]).mean()

    #                 # # shift the index forward 30min to centre the bins on the hour
    #                 # df_cell.index = df_cell.index + pd.Timedelta(minutes=30)

    #                 # day_avg = df.groupby([df['TIME'].dt.date]).mean()
    #                 print(f"Creating plot of {active_tab} at {dropdown_selection}...")
    #                 fig.add_trace(go.Scatter(x=day_avg.index, y=day_avg.VCUR, name="LTSP"))

    #                 #ADCP1
    #                 local_df = get_local_files(dropdown_selection)
    #                 # local_df = local_df.VCUR
    #                 # local_df.index = pd.to_datetime(df.index)
    #                 # [ts.hour for ts in local_df.index]
    #                 # local_day_avg = local_df.groupby(local_df.hour).mean()
    #                 # local_day_avg = local_df.groupby(local_df.index.get_level_values('TIME')).mean()
    #                 local_time_avg = local_df.groupby(local_df.index.get_level_values('TIME')).mean()
    #                 local_hour_avg = local_time_avg.resample('h').VCUR.mean()
    #                 # local_hour_avg_df = local_time_avg.to_frame()
    #                 local_hour_avg_df = local_hour_avg.to_frame()
    #                 local_hour_avg_df = local_hour_avg_df[1:]
    #                 print(local_hour_avg_df.VCUR.head())
    #                 fig.add_trace(go.Scatter(x=local_hour_avg_df.index, y=local_hour_avg_df.VCUR, name="NEMO"))

    #                 #getVariable
    #                 # file = 'http://thredds.aodn.org.au/thredds/dodsC/IMOS/ANMN/QLD/NWSROW/hourly_timeseries/IMOS_ANMN-QLD_VZ_20190804_NWSROW_FV02_velocity-hourly-timeseries_END-20210509_C-20211222.nc'
    #                 # extracted_ds = extractVariable.getVariable(file, 'VCUR', False)
    #                 # print(extracted_ds.head())
    #                 # print(extracted_ds.tail())
    #                 # extract_df = extracted_ds.VCUR.to_dataframe()
    #                 # print(extract_df.VCUR[1000:1020])
    #                 # # print(extract_df.VCUR.tail())
    #                 # fig.add_trace(go.Scatter(x=extract_df.index.get_level_values('TIME'), y=extract_df.VCUR, name="extracted"))

    #                 # print(day_avg.head())
    #                 # fig = px.line(day_avg.VCUR)
    #                 fig_layout(fig)
    #                 # print('vcur plotted')
    #                 return html.H3(f'VCUR line chart for {dropdown_selection}', style={"color": "white"}), dcc.Graph(id='vcur_tab', figure=fig)
    #                 # figs.add_trace((go.Scatter(x=list(df['time'][::DATA_SKIP]), y=list(sal[::DATA_SKIP]))), row=file_counter, col=1)
    #             elif active_tab == 'ucur_tab':
    #                 print(f"Creating {dropdown_selection} dataframe...")
    #                 df = ds.UCUR.to_dataframe()
    #                 print(f"Converting to daily timeseries...")
    #                 day_avg = df.groupby([df['TIME']]).mean()
    #                 # day_avg = df.groupby([df['TIME'].dt.date]).mean()
    #                 print(f"Creating plot of {active_tab} at {dropdown_selection}...")
    #                 fig.add_trace(go.Scatter(x=day_avg.index, y=day_avg.UCUR, name="LTSP"))

    #                 #ADCP1
    #                 local_df = get_local_files(dropdown_selection)
    #                 local_df = local_df[local_df.VCUR_quality_control == 1]
    #                 # local_df = local_df.VCUR
    #                 # local_df.index = pd.to_datetime(df.index)
    #                 # [ts.hour for ts in local_df.index]
    #                 # local_day_avg = local_df.groupby(local_df.hour).mean()
    #                 # local_day_avg = local_df.groupby(local_df.index.get_level_values('TIME')).mean()
    #                 local_time_avg = local_df.groupby(local_df.index.get_level_values('TIME')).mean()
    #                 local_hour_avg = local_time_avg.resample('h').UCUR.mean()
    #                 local_hour_avg_df = local_hour_avg.to_frame()
    #                 local_hour_avg_df = local_hour_avg_df[1:]
    #                 print(local_hour_avg_df.UCUR.head())
    #                 fig.add_trace(go.Scatter(x=local_hour_avg_df.index, y=local_hour_avg_df.UCUR, name="ADCP1"))

    #                 #ADCP2
    #                 local_df2 = get_local_files2(dropdown_selection)
    #                 local_df2 = local_df2[local_df2.VCUR_quality_control == 1]
    #                 # local_df = local_df.VCUR
    #                 # local_day_avg2 = local_df2.groupby(local_df2.index.get_level_values('TIME').date).mean()
    #                 local_time_avg2 = local_df2.groupby(local_df2.index.get_level_values('TIME')).mean()
    #                 local_hour_avg2 = local_time_avg2.resample('h').UCUR.mean()
    #                 local_hour_avg_df2 = local_hour_avg2.to_frame()
    #                 local_hour_avg_df2 = local_hour_avg_df2[1:]
    #                 print(local_hour_avg_df2.UCUR.head())
    #                 fig.add_trace(go.Scatter(x=local_hour_avg_df2.index, y=local_hour_avg_df2.UCUR, name="ADCP2"))
    #                 # fig.add_trace(go.Scatter(x=local_df2.index, y=local_df2.VCUR, name="ADCP2_full"))
    #                 # get_local_files2
    #                 # local_file_df = get_local_files(dropdown_selection)
    #                 # local_file_ds = xr.open_dataset(r"37\\NWSROW-2104_ADCP.nc")
    #                 fig_layout(fig)
    #                 return html.H3(f'UCUR line chart for {dropdown_selection}', style={"color": "white"}), dcc.Graph(id='ucur_tab', figure=fig)

    #     except AttributeError as e:
    #        print("Attribute error: Missing data")
    #        print(f"Error: {e}")
    #        pass
    # for file in agg_working_files:
    #     try:
    #         if (file.split("IMOS/ANMN",1)[1])[5:11] == (str(dropdown_selection)):
    #             print("getting file")
    #             file_counter += 1
    #             fig = go.Figure()
    #             ds = xr.open_dataset(file)
    #             if active_tab == 'temp_tab':
    #                 print(ds.head())
    #                 print(f"Creating {dropdown_selection} dataframe...")
    #                 # ds = ds.loc["2020-03-01": "2020-06-01", "IA"]
    #                 start = np.datetime64('2020-03-04T00:00')
    #                 stop = np.datetime64('2020-06-07T00:00')
    #                 # ds.TIME[-10000:]
    #                 # ds.sel(time=slice("2020-03-01", "2020-06-01"))
    #                 # ds.sel(ds.TIME=slice("2020-03-01", "2020-06-01"))
    #                 # df1 = ds.TEMP[-10000:].to_dataframe()
    #                 df2 = ds.TEMP[-10000:].to_dataframe()
    #                 # df2 = ds.TEMP[-45000:-40000].to_dataframe()
    #                 # df2 = ds.TEMP['20200301':'20201001'].to_dataframe()
    #                 # start = df2.index.searchsorted(datetime.datetime(2020, 4, 3))
    #                 # end = df2.index.searchsorted(datetime.datetime(2020, 12, 11))

    #                 local_df = get_local_files(dropdown_selection)
    #                 print(f"Converting to daily timeseries...")
    #                 # day_avg = df.groupby([df['TIME'].dt.date]).mean()
    #                 print(f"Creating plot of {active_tab} at {dropdown_selection}...")
    #                 # fig.add_trace(go.Scatter(x=df1.TIME, y=df1.TEMP))
    #                 fig.add_trace(go.Scatter(x=df2.TIME, y=df2.TEMP))
    #                 fig.add_trace(go.Scatter(x=local_df.index[::DATA_SKIP], y=local_df.TEMP[::DATA_SKIP]))
    #                 fig_layout(fig)
    #                 print("Plot created")

    # fig = px.line(day_avg.VCUR)
    # return html.H3(f'TEMP line chart for {dropdown_selection}', style={"color": "white"}), dcc.Graph(id='temp_tab', figure=fig)
    # except AttributeError as e:
    #    print("Attribute error: Missing data")
    #    print(f"Error: {e}")
    #    pass
    if active_tab == 'vcur_tab':
        fig = go.Figure()
        fig2 = go.Figure()
        PATH = pathlib.Path(__file__).parent
        # csv_files = PATH.joinpath("../oceanobs/csv/vcur").resolve()
        csv_files = PATH.joinpath(os.path.abspath(os.curdir) + "/csv/vcur").resolve()
        # csv_files = r"app/csv/"
        for file in os.listdir(csv_files):
            mooring_site = file[0:6]
            print(file)
            # if file[0:5] == map_selection:
            #     csv_file = pd.read_csv(map_selection + '_vel.csv')
            # print(file[0:6])
            if mooring_site in MOORINGS and mooring_site == map_selection:
                csv_file = pd.read_csv(csv_files.joinpath(map_selection + '_vcur.csv'))
                print(file[0:6] + " loaded.")
                # csv_file = pd.read_csv('data_csv.csv')csv_file = pd.read_csv('data_csv.csv')
                # print(csv_file)
                # csv_df = pd.DataFrame(csv_file)
                fig.add_trace(go.Scatter(x=csv_file['TIME'], y=csv_file['VCUR'], name="NEMO"))
                print("Trace added...")
                # print("Step 7...")
                # fig_layout(fig)
                print("Layout complete...")

                csv_files = PATH.joinpath(os.path.abspath(os.curdir) + "/csv/ucur").resolve()
                csv_file2 = pd.read_csv(csv_files.joinpath(map_selection + '_ucur.csv'))
                print(file[0:6] + " loaded.")
                # csv_file = pd.read_csv('data_csv.csv')csv_file = pd.read_csv('data_csv.csv')
                # print(csv_file)
                # csv_df = pd.DataFrame(csv_file)
                fig2.add_trace(go.Scatter(x=csv_file2['TIME'], y=csv_file2['UCUR'], name="NEMO"))
                print("Trace added...")
                # print("Step 7...")
                # fig_layout(fig2)
                print("Layout complete...")
                return html.H3(f'VCUR line chart for {map_selection}', style={"color": "DarkSlateGrey"}), dcc.Graph(
                    figure=fig), html.H3(f'UCUR line chart for {map_selection}', style={"color": "DarkSlateGrey"}), dcc.Graph(
                    figure=fig2)
    if active_tab == 'ucur_tab':
        fig = go.Figure()
        PATH = pathlib.Path(__file__).parent
        # csv_files = PATH.joinpath("../oceanobs/csv/ucur").resolve()
        csv_files = PATH.joinpath(os.path.abspath(os.curdir) + "/csv/ucur").resolve()
        # csv_files = r"app/csv/"
        for file in os.listdir(csv_files):
            mooring_site = file[0:6]
            print(file)
            # if file[0:5] == map_selection:
            #     csv_file = pd.read_csv(map_selection + '_vel.csv')
            # print(file[0:6])
            if mooring_site in MOORINGS and mooring_site == map_selection:
                csv_file = pd.read_csv(csv_files.joinpath(map_selection + '_ucur.csv'))
                print(file[0:6] + " loaded.")
                # csv_file = pd.read_csv('data_csv.csv')csv_file = pd.read_csv('data_csv.csv')
                # print(csv_file)
                # csv_df = pd.DataFrame(csv_file)
                fig.add_trace(go.Scatter(x=csv_file['TIME'], y=csv_file['UCUR'], name="NEMO"))
                print("Trace added...")
                # print("Step 7...")
                # fig_layout(fig)
                print("Layout complete...")

                return html.H3(f'UCUR line chart for {map_selection}', style={"color": "DarkSlateGrey"}), dcc.Graph(
                    id='ucur_tab', figure=fig)

    if active_tab == 'temp_tab':
        fig = go.Figure()
        PATH = pathlib.Path(__file__).parent
        # csv_files = PATH.joinpath("../oceanobs/csv/ucur").resolve()
        csv_files = PATH.joinpath(os.path.abspath(os.curdir) + "/csv/temp").resolve()
        # csv_files = r"app/csv/"
        for file in os.listdir(csv_files):
            mooring_site = file[0:6]
            print(file)
            # if file[0:5] == map_selection:
            #     csv_file = pd.read_csv(map_selection + '_vel.csv')
            # print(file[0:6])
            if mooring_site in MOORINGS and mooring_site == map_selection:
                csv_file = pd.read_csv(csv_files.joinpath(map_selection + '_temp.csv'))
                print(file[0:6] + " loaded.")
                # csv_file = pd.read_csv('data_csv.csv')csv_file = pd.read_csv('data_csv.csv')
                # print(csv_file)git
                # csv_df = pd.DataFrame(csv_file)
                fig.add_trace(go.Scatter(x=csv_file['TIME'], y=csv_file['TEMP'], name="NEMO"))
                print("Trace added...")
                # print("Step 7...")
                # fig_layout(fig)
                print("Layout complete...")

                return html.H3(f'TEMP line chart for {map_selection}', style={"color": "DarkSlateGrey"}), dcc.Graph(
                    id='ucur_tab', figure=fig)

    if active_tab == 'daily_temp_tab':
        fig = go.Figure()
        PATH = pathlib.Path(__file__).parent
        # csv_files = PATH.joinpath("../oceanobs/csv/temp").resolve()
        csv_files = PATH.joinpath(os.path.abspath(os.curdir) + "/csv/daily_temp").resolve()
        # csv_files = r"app/csv/"
        for file in os.listdir(csv_files):
            mooring_site = file[0:6]
            print(file)
            # if file[0:5] == map_selection:
            #     csv_file = pd.read_csv(map_selection + '_vel.csv')
            # print(file[0:6])
            if mooring_site in MOORINGS and mooring_site == map_selection:
                csv_file = pd.read_csv(csv_files.joinpath(map_selection + '_temp_dayavg.csv'))
                print(file[0:6] + " loaded.")
                # csv_file = pd.read_csv('data_csv.csv')csv_file = pd.read_csv('data_csv.csv')
                # print(csv_file)
                # csv_df = pd.DataFrame(csv_file)
                fig.add_trace(go.Scatter(x=csv_file['TIME'], y=csv_file['TEMP'], name="NEMO"))
                print("Trace added...")
                # print("Step 7...")
                # fig_layout(fig)
                print("Layout complete...")

                return html.H3(f'Daily averaged TEMP line chart for {map_selection}',
                               style={"color": "DarkSlateGrey"}), dcc.Graph(id='daily_temp_tab', figure=fig)


    if active_tab == 'climatology_tab':
        PATH = pathlib.Path(__file__).parent
        nc_files = PATH.joinpath(os.path.abspath(os.curdir) + "/nc").resolve()
        if map_selection not in ['TAN100', 'GBRPPS', 'GBRMYR']:
            map_selection = 'TAN100'
        for file in os.listdir(nc_files):
            fig = go.Figure()
            nc_file = xr.open_dataset(nc_files.joinpath('TAN100_LTSP_grid_daily.nc'))
            # print(nc_file['DEPTH'].head(30))
            fig.add_trace(go.Contour(z = nc_file['CLIM'], x=nc_file['TIME'], transpose=True, line_width=0))
            fig['layout']['yaxis']['autorange'] = "reversed"
            fig.update_xaxes(title_text='Time')
            fig.update_yaxes(title_text='Depth')
            # fig_layout(fig)
            return html.H3(f'Climatology Plot',
                                   style={"color": "DarkSlateGrey"}), dcc.Graph(id='climatology_tab', figure=fig)

    if active_tab == 'gridded_temp_tab':
        PATH = pathlib.Path(__file__).parent
        nc_files = PATH.joinpath(os.path.abspath(os.curdir) + "/nc").resolve()
        if map_selection not in ['TAN100', 'GBRPPS', 'GBRMYR']:
            map_selection = 'TAN100'
        for file in os.listdir(nc_files):
            fig = go.Figure()
            nc_file = xr.open_dataset(nc_files.joinpath(map_selection + '_LTSP_grid_daily.nc'))
            # print(nc_file['DEPTH'].head(30))
            fig.add_trace(go.Contour(z = nc_file['TEMP'], x=nc_file['TIME'], transpose=True, line_width=0))
            fig['layout']['yaxis']['autorange'] = "reversed"
            fig.update_xaxes(title_text='Time')
            fig.update_yaxes(title_text='Depth')
            # fig_layout(fig)
            return html.H3(f'Gridded Temperature Plot',
                                   style={"color": "DarkSlateGrey"}), dcc.Graph(id='gridded_temp_tab', figure=fig)

    if active_tab == 'daily_vel_tab':

        PATH = pathlib.Path(__file__).parent
        nc_files = PATH.joinpath(os.path.abspath(os.curdir) + "/nc").resolve()
        for file in os.listdir(nc_files):

            nc_file = xr.open_dataset(nc_files.joinpath('TAN100_LTSP_VV_daily.nc'))
            #East plot
            fig = make_subplots(rows=4, cols=1,
                                subplot_titles=('Daily Velocity Plot (East)',
                                                'Daily Velocity Plot (North)',
                                                'Daily Velocity Plot (Cross-Shelf)',
                                                'Daily Velocity Plot (Alongshore)'
                                                ))
            # fig = go.Figure()
            # print(nc_file['DEPTH'].head(30))
            fig.add_trace(go.Contour(z = nc_file['UCUR'],
                                     x=nc_file['TIME'],
                                     transpose=True,
                                     line_width=0,
                                     # colorscale = ([0, 'rgb(0,0,255)'], [1, 'rgb(0,255,0)']),
                                     zmax=1,
                                     zmin=-1,
                                     ncontours=40,
                                     ),
                          row=1, col=1
                          )
            fig['layout']['yaxis']['autorange'] = "reversed"
            fig.update_xaxes(title_text='Time')
            fig.update_yaxes(title_text='Depth')
            # fig_layout(fig)

            # North plot
            # fig2 = go.Figure()
            # print(nc_file['DEPTH'].head(30))
            fig.add_trace(go.Contour(z=nc_file['VCUR'],
                                      x=nc_file['TIME'],
                                      transpose=True,
                                      line_width=0,
                                      # colorscale = ([0, 'rgb(0,0,255)'], [1, 'rgb(0,255,0)']),
                                      zmax=1,
                                      zmin=-1,
                                      ncontours=40,
                                      ),
                          row=2, col=1
                           )
            # fig2['layout']['yaxis']['autorange'] = "reversed"
            # fig2.update_xaxes(title_text='Time')
            # fig2.update_yaxes(title_text='Depth')
            # fig_layout(fig)

            #Cross Shelf plot
            # fig3 = go.Figure()
            # print(nc_file['DEPTH'].head(30))
            fig.add_trace(go.Contour(z=nc_file['UU'],
                                      x=nc_file['TIME'],
                                      transpose=True,
                                      line_width=0,
                                      # colorscale = ([0, 'rgb(0,0,255)'], [1, 'rgb(0,255,0)']),
                                      zmax=1,
                                      zmin=-1,
                                      ncontours=40,
                                      ),
                          row=3, col=1
                           )
            # fig3['layout']['yaxis']['autorange'] = "reversed"
            # fig3.update_xaxes(title_text='Time')
            # fig3.update_yaxes(title_text='Depth')
            # fig_layout(fig)

            #Alongshore plot
            # fig4 = go.Figure()
            # print(nc_file['DEPTH'].head(30))
            fig.add_trace(go.Contour(z=nc_file['VV'],
                                      x=nc_file['TIME'],
                                      transpose=True,
                                      line_width=0,
                                      # colorscale = ([0, 'rgb(0,0,255)'], [1, 'rgb(0,255,0)']),
                                      zmax = 1,
                                      zmin = -1,
                                      ncontours=40,
                                      ),
                          row=4, col=1
                           )
            # fig4['layout']['yaxis']['autorange'] = "reversed"
            # fig4.update_xaxes(title_text='Time')
            # fig4.update_yaxes(title_text='Depth')
            # fig_layout(fig)

            fig.update_layout(height=1000,
                              width=1000,
                              # title_text="Gridded Daily Velocities",

                              )

            return \
                html.H3(f'Gridded Daily Velocities', style={"color": "DarkSlateGrey"}), \
                dcc.Graph(id='daily_vel_tab', figure=fig), \
                   # html.H3(f'Daily Velocity Plot (North)', style={"color": "DarkSlateGrey"}), \
                   # dcc.Graph(id='daily_vel_tab', figure=fig2), \
                   # html.H3(f'Daily Velocity Plot (Cross-Shelf)', style={"color": "DarkSlateGrey"}), \
                   # dcc.Graph(id='daily_vel_tab', figure=fig3), \
                   # html.H3(f'Daily Velocity Plot (Alongshore)', style={"color": "DarkSlateGrey"}), \
                   # dcc.Graph(id='daily_vel_tab', figure=fig4)



# print("Always executed")

# if __name__ == "main":
#     print("If clause reached")
# else:
#     print("Else clause reached")

# if __name__ == '__main__':
#     app.run_server(debug=False)

# if __name__ == '__main__':
#     app.run_server(host='0.0.0.0', port=8080, debug=False, use_reloader=False)