# # Import the required packages
import pandas as pd
from functools import lru_cache
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.plotting import figure, show

from bokeh.server.server import Server
from bokeh.themes import Theme

from bokeh.tile_providers import get_provider,STAMEN_TERRAIN
from bokeh.models import ColumnDataSource, Slider, PreText, Select, Div, Button, CustomJS, HoverTool,LabelSet

# IMPORTING LIBRARY
import numpy as np
import requests
import json
import time




## AREA EXTENT COORDINATE WGS4 (SET THIS TO WEST LA)
lon_min,lat_min= -118.4,33.8
lon_max,lat_max= -118.2,34.0

# class AirPort:

#         def __init__(self, flightnum = "null", alt = [], lat = [], lon = [], speed = []):

#             self.all_flights = []
            
#             self.flight = flightnum
#             self.altitude = alt
#             self.latitude = lat
#             self.longitude = lon
#             self.speed = speed

#         def add_airplane_data(info = []):
            
#             parsed_info = list(map(str.strip, info.split(",")))
#             all_flights[]

def sort_by_flight(list_to_sort = [], flight_num = 'null'):
    sorted = []
    for i in range(0, len(list_to_sort)):
        if list_to_sort[i][0] == flight_num:
            sorted.append(list_to_sort[i])
    return sorted

def high_pass_filter(list_to_sort = [], column_to_filter = 1):
    sorted = []
    for i in range(0, len(list_to_sort)):
        if list_to_sort[i][column_to_filter] != "0":
            sorted.append(list_to_sort[i])
    return sorted

def wgs84_web_mercator_point(lon,lat):
    k = 6378137
    x= lon * (k * np.pi/180.0)
    y= np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return x,y

#DATA FRAME
def wgs84_to_web_mercator(df, lon="Lon", lat="Lat"):
    k = 6378137
    df["x"] = (df[lon]) * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df









def bkapp(doc):
    ## MAIN LOOP ###

    # Initialize All Lists/Variables #
    airplane_list = []
    airplane_hex_codes = []
    airplane_data_log = {}

    total_flights_spotted = 0
    order_in_which_spotted = []



    ##### This code checks the end of csv file for data #####  
    # The idea is we read the very last line of the csv file every time
    # (last line provides most up-to-date info about an aircraft) 
    # ---->                                                                   <----

    # with open("/home/gnuradio/dump1090_sdrplus-master/aircraft_log.csv") as file:
    #     for last_line in file:
    #         pass


    ##### This code uses the entire aircraft_log,csv file to be imported into a pandas dataframe #####
    # ---->                                                                             <---- 

    source = []
    with open("/home/gnuradio/dump1090_sdrplus-master/aircraft_log.csv") as file:
        f = file.readlines()
        for i in f:
            source.append(list(map(str.strip, i.split(","))))
    
    altitude_log = []

    speed_log = []

    latitude_log = []

    longtiude_log = []
        
    flights = sort_by_flight(source, 'a6a11e')

    altitude_log = high_pass_filter(flights, 2)

    speed_log = high_pass_filter(flights, 3)
    
    flight_df = pd.DataFrame(flights, columns = ['Hex','Flight','Altitude','Speed','Lat','Lon','Track','Messages','Seen'])

    flight_df.set_index("Hex", inplace = True)

    print(flight_df)

    ## COORDINATE CONVERSION

    xy_min=wgs84_web_mercator_point(lon_min,lat_min)
    xy_max=wgs84_web_mercator_point(lon_max,lat_max)
    
    wgs84_to_web_mercator(flight_df)
    
    #flight_df['rot_angle']=flight_df['true_track']*-1 #Rotation angle
    icon_url='https://img1.pnghut.com/4/14/18/52nsQBCssu/paper-monochrome-cursor-logo-triangle.jpg' #Icon url
    flight_df['url']=icon_url

    ## FIGURE SETTING
    x_range,y_range=([xy_min[0],xy_max[0]], [xy_min[1],xy_max[1]])
    p=figure(x_range=x_range,y_range=y_range,x_axis_type='mercator',y_axis_type='mercator',sizing_mode='scale_width',height=300)

    ## PLOT BASEMAP AND AIRPLANE POINTS
    flight_source=ColumnDataSource(flight_df)
    tile_prov=get_provider('CARTODBPOSITRON')
    p.add_tile(tile_prov,level='image')
    p.image_url(url='url', x='x', y='y',source=flight_source,anchor='center',angle_units='deg',h_units='screen',w_units='screen',w=40,h=40)
    p.circle('x','y',source=flight_source,fill_color='red',hover_color='yellow',size=10,fill_alpha=0.8,line_width=0)

    ## HOVER INFORMATION AND LABEL
    my_hover=HoverTool()
    my_hover.tooltips=[('ICAO','@Hex'),('Speed(m/s)','@Speed'),('Altitude(m)','@Altitude')]
    labels = LabelSet(x='x', y='y', text='callsign', level='glyph',
                x_offset=5, y_offset=5, source=flight_source,background_fill_color='white',text_font_size="8pt")
    p.add_tools(my_hover)
    p.add_layout(labels)

    start = time.time()
    show(p)
    print(time.time() - start)


    df = ColumnDataSource(flight_df)

    
        
        
            

    #last_line = 'a45586,DAL1530 ,7125,259,0.000000,0.000000,85,52,1677185367'

    # PARSE INTO A LIST    
    #new_airplane_info = list(map(str.strip, last_line.split(",")))
    #hex_code = new_airplane_info[0]

    

    ## THIS CAN BE SPED UP ##

    # ## Data is logged in a list, airplane data is referenced by a dictionary of seen airplane hex codes ##
    # if hex_code in airplane_hex_codes:
    #     airplane_data_log[str(hex_code)].append(new_airplane_info)
    # else:
    #     airplane_hex_codes.append(hex_code)
    #     airplane_data_log[str(hex_code)] = []
    #     airplane_data_log[str(hex_code)].append(new_airplane_info)

    # ## remove out-of-date data entry ##
    # for i in airplane_list:
    #     if i[0] == hex_code:
    #         airplane_list.remove(i)

    # ## replace with up-to-date data entry ##
    # airplane_list.append(new_airplane_info)
    # airplane_list.append(new_airplane_info)
    # total_flights_spotted = len(airplane_list)

    # ## pandas dataframe ##
    # flight_df = pd.DataFrame(airplane_list)
    # flight_df.columns= ['Hex','Flight','Altitude','Speed','Lat','Lon','Track','Messages','Seen']

    # ## ordering flights by order in which they were seen ##
    # for i in range(0, total_flights_spotted):
    #     order_in_which_spotted.append("Flight "+str(i+1))
    # flight_df.index = order_in_which_spotted

    # set up widgets
    stats = PreText(text='', width=500)
    airplane1 = Select(value='Select a Flight to Track', options=['Flight1', "Flight2"])
    airplane2 = Select(value='Select another Flight to Track', options=['Flight3', "Flight4"])

    # # set up plots
    tools = 'pan,wheel_zoom,xbox_select,reset'

    corr = figure(width=400, height=350,
                tools='pan,wheel_zoom,box_select,reset', output_backend='webgl')
    corr.diamond('Messages', 'Altitude', size=2, source=df, color="red",
                selection_color="orange", alpha=0.6, nonselection_alpha=0.1, selection_alpha=0.4)


    # time_series1 = figure(width=900, height=200, tools=tools,
    #                     x_axis_type='datetime', active_drag="xbox_select", output_backend='webgl')
    # time_series1.line('date', 't1', source=source, color='orange')
    # time_series2 = figure(width=900, height=200, tools=tools,
    #                     x_axis_type='datetime', active_drag="xbox_select", output_backend='webgl')
    # time_series2.x_range = time_series1.x_range
    # time_series2.line('date', 't2', source=source, color='green')

    button = Button(label="Foo", button_type="success")
    button.js_on_click(CustomJS(code="console.log('button: click!', this.toString())"))
    
    

    plot = figure(x_axis_type='datetime', y_axis_label='Speed',title="Flight Speed Over Time")
    plot.line(x='Messages', y='Speed', source=df)


    def callback(attr, old, new):
        if new == 0:
            data = df
        else:
            data = df.rolling(f"{new}D").mean()
        source.data = ColumnDataSource.from_df(data)

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change('value', callback)

    doc.add_root(column(slider, plot))
    doc.add_root(column(button))
    doc.add_root(row(corr))

    doc.theme = Theme(filename="theme.yaml")

# Setting num_procs here means we can't touch the IOLoop before now, we must
# let Server handle that. If you need to explicitly handle IOLoops then you
# will need to use the lower level BaseServer class.
server = Server({'/': bkapp}, num_procs=2)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()







# ## MAIN LOOP ###

# # Initialize All Lists/Variables #
# airplane_list = []
# airplane_hex_codes = []
# airplane_data_log = []

# total_flights_spotted = 0
# order_in_which_spotted = []


# ## Checks the end of csv file ##            (last line provides most up-to-date info about an aircraft) 
# with open("/home/gnuradio/dump1090_sdrplus-master/aircraft_log.csv") as file:
#     for last_line in file:
#         pass

# # PARSE INTO A LIST    
# new_airplane_info = list(map(str.strip, last_line.split(",")))
# hex_code = new_airplane_info[0]



# ## THIS CAN BE SPED UP ##

# ## Data is logged in a list, airplane data is referenced by a dictionary of seen airplane hex codes ##
# if hex_code in airplane_hex_codes:
#     airplane_data_log[hex_code].append(new_airplane_info)
# else:
#     airplane_hex_codes.append(hex_code)
#     airplane_data_log[hex_code].append(new_airplane_info)

# ## remove out-of-date data entry ##
# for i in airplane_list:
#     if i[0] == hex_code:
#         airplane_list.remove(i)

# ## replace with up-to-date data entry ##
# airplane_list.append(new_airplane_info)
# airplane_list.append(new_airplane_info)
# total_flights_spotted = len(airplane_list)

# ## pandas dataframe ##
# flight_df = pd.DataFrame(airplane_list)
# flight_df.columns= ['Hex','Flight','Altitude','Speed','Lat','Lon','Track','Messages','Seen']

# ## ordering flights by order in which they were seen ##
# for i in range(0, total_flights_spotted):
#     order_in_which_spotted.append("Flight "+str(i+1))
# flight_df.index = order_in_which_spotted












































# # Put data into a ColumnDataSource
# source = ColumnDataSource(data = dict(Hex = [],Flight = [],Altitude = [],Speed =[],Lat = [],Lon =[],Track =[],Messages =[],Seen = []))





# # Define callbacks
# def change_ticker1(attrname, old, new):
#     airplane1.options = [new]
#     update()

# def change_ticker2(attrname, old, new):
#     airplane2.options = [new]
#     update()

# def update(selected=None):
#     t1, t2 = airplane1.value, airplane2.value

#     df = get_data(t1, t2)
#     data = df[['t1', 't2', 't1_returns', 't2_returns']]
#     source.data = data

#     update_stats(df, t1, t2)

#     corr.title.text = '%s returns vs. %s returns' % (t1, t2)
#     time_series1.title.text, time_series2.title.text = t1, t2

# def update_stats(data, t1, t2):
#     stats.text = str(data[[t1, t2, t1+'_returns', t2+'_returns']].describe())
#     airplane1.on_change('value', change_ticker1)
#     airplane2.on_change('value', change_ticker2)

# def selection_change(attrname, old, new):
#     t1, t2 = airplane1.value, airplane2.value
#     data = get_data(t1, t2)
#     selected = source.selected.indices
#     if selected:
#         data = data.iloc[selected, :]
#     update_stats(data, t1, t2)
#     source.selected.on_change('indices', selection_change)

# # Add the following code to read and load data for the webapp:
# # A function to read and load data
# # Note the use of @lru_cache() decorator is to cache the data and speed up reloads

# @lru_cache()
# def load_ticker(ticker):
#     data = pd.read_csv('all_stocks_5yr.csv', parse_dates=['date'])
#     data = data.set_index('date')
#     data = data[data['Name'] == ticker]
#     return pd.DataFrame({ticker: data.close, ticker+'_returns': data.close.diff()})

# # A function to create a dataframe for the selected tickers
# @lru_cache()
# def get_data(t1, t2):
#     df1 = load_ticker(t1)
#     df2 = load_ticker(t2)
#     data = pd.concat([df1, df2], axis=1)
#     data = data.dropna()
#     data['t1'] = data[t1]
#     data['t2'] = data[t2]
#     data['t1_returns'] = data[t1+'_returns']
#     data['t2_returns'] = data[t2+'_returns']
#     return data




# # set up layout
# # Add a title message to the app
# div = Div(
#     text="""
#         <p>Select two Stocks to compare key Statistics:</p>
#         """,
# width=900,
# height=30,
# )
# # Create layouts
# app_title = div
# widgets = column(ticker1, ticker2, stats)
# main_row = row(widgets, corr)
# series = column(time_series1, time_series2)
# layout = column(app_title, main_row, series)