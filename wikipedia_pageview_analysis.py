'''this file will take the JSON data created in wikipedia_pageview_timeseries_generator
and run analysis and processing on it to generate three charts

Chart 1: Maximum Average and Minimum Average - contains time series for the articles that have 
the highest average page requests and the lowest average page requests for desktop access and mobile access. 
This graph should have four lines (max desktop, min desktop, max mobile, min mobile).


Chart 2: Top 10 Peak Page Views - contains time series for the top 10 article pages by largest (peak) page views 
over the entire time by access type. This is done by finding the month for each article that contains the highest (peak) page views, 
and then ordering the articles by these peak values. The graph will contain the top 10 for desktop and top 10 for mobile access (20 lines).

Chart 3: Fewest Months of Data - contains pages that have the fewest months of available data. 
These will all be relatively short time series, some may only have one month of data. 
The graph will show the 10 articles with the fewest months of data for desktop access and the 10 articles with the fewest months of data for mobile access.
'''
#may need to install pandas and matplotlib before running this cell
import pandas as pd
import json
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

CHART_1_OUTPUT_FNAME = "highest_lowest_average_views_by_access_type.png"
CHART_1_TITLE =  "Highest and lowest average views for mobile and desktop"

CHART_2_OUTPUT_FNAME = "peak_viewership_pages_by_access_type.png"
CHART_2_TITLE = "Webpages with highest PEAK viewership across timespan"

CHART_3_OUTPUT_FNAME = "lowest_availibility_pages_by_access_type.png"
CHART_3_TITLE = "Webpages with lowest data availibility"

CHART_Y_AXIS_TITLE =  "Webpage Views"
MOBILE_DATA_PATH = "dino_monthly_mobile_201506-202208.json"
DESKTOP_DATA_PATH = "dino_monthly_desktop_201506-202208.json"

#this function takes in paths to two JSONS generated in the wikipedia_pageview_timeseries_generator script and loads them
def load_data(mobile_path = MOBILE_DATA_PATH, desktop_path = DESKTOP_DATA_PATH):
    desktop_json = json.load(open(desktop_path))
    mobile_json =  json.load(open(mobile_path))
    return desktop_json, mobile_json

#will calculate the average view count of a webpage, returns -1 if there is no time series data available for the webpage.
#timeseries in this case is an array of JSON objects returned from API calls to the wikipedia API
def average_page_view_calculator(timeseries):
    if  len(timeseries) == 0:
        return -1
    all_page_views = 0.0
    for month in timeseries:
        all_page_views += month["views"]
    return all_page_views / float(len(timeseries))
#calculates the highest peak in views for a particular webpage, returns -1 if there is no time series data available for the webpage
#timeseries in this case is an array of JSON objects returned from API calls to the wikipedia API
def max_page_view_calculator(timeseries):
    if len(timeseries) == 0:
        return -1
    highest_page_view = 0
    for month in timeseries:
        highest_page_view = max(highest_page_view, int(month["views"]))
    return highest_page_view
#returns the number of months available for analysis in the timeseries for a particular webpage.
#timeseries in this case is an array of JSON objects returned from API calls to the wikipedia API.
#returns 0 if timeseries is empty 
def fewest_months_of_data_calculator(timeseries):
    return len(timeseries)

#this function will take a dictionary containing names and timeseries and plot them all together on a matplotlib plot
#also will take title of the plot and ylabel of the plot and an output file name to save the image to.
def time_series_plotter(name_to_timeseries, title, ylabel, output_f_name):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1,1,1)  
    for name, timeseries in name_to_timeseries.items():
        #timestamps = [datetime.strptime(month["timestamp"], "%Y%M%d%S") for month in timeseries]
        timestamps = [month["timestamp"] for month in timeseries]
        
        views = [month["views"] for month in timeseries]
        plt.plot(timestamps, views, label=name)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3)) #this will set our x labels not to be so close together and only every 3 months
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.savefig(output_f_name)
    plt.show()

"""
This function will process the JSON data and calculate the information needed to generate chart 1 in the top comment of this file.
@param: desktop_json: a JSON file containing the desktop users queried from the wikimedia API in wikipedia_pageview_timeseries_generator.py
@param: mobile_json: a JSON file containing the mobile users queried from the wikimedia API in wikipedia_pageview_timeseries_generator.py
@param: output_f_name: the output file name or path to which the chart will be saved
@param: chart_y_axis: the y axis title of the chart
@param: chart_title: the charts main title
@returns None, will save png file to output_f_name and show an image of the chart in the terminal as well
"""
def generate_average_chart(desktop_json, mobile_json, output_f_name = CHART_1_OUTPUT_FNAME, chart_y_axis = CHART_Y_AXIS_TITLE, chart_title=CHART_1_TITLE):
        #Lets create a dictionary which contains each dinosaur and its average views along the timeseries. 
    average_page_views_desktop = {}
    for name,timeseries in desktop_json.items():
        average= average_page_view_calculator(timeseries)
        if average > 0: #this will exclude any names with no timeseries available. KEY ASSUMPTION
            average_page_views_desktop[name] = average

    average_page_views_mobile = {}
    for name,timeseries in mobile_json.items():
        average= average_page_view_calculator(timeseries)
        if average > 0: #this will exclude any names with no timeseries available. KEY ASSUMPTION
            average_page_views_mobile[name] = average
    #lets identify which dinosaur had highest average page views on desktop using the above dict
    most_popular_desktop = max(average_page_views_desktop, key=average_page_views_desktop.get)
    most_popular_mobile = max(average_page_views_mobile, key=average_page_views_mobile.get)
    least_popular_desktop = min(average_page_views_desktop, key=average_page_views_desktop.get)
    least_popular_mobile = min(average_page_views_mobile, key=average_page_views_mobile.get)
    print(most_popular_desktop, most_popular_mobile, least_popular_desktop, least_popular_mobile)

    #Maximum Average and Minimum Average
    name_to_timeseries = {str(most_popular_desktop)+"_Desktop": desktop_json[most_popular_desktop], str(most_popular_mobile)+"_Mobile": mobile_json[most_popular_mobile], \
        str(least_popular_desktop)+"_Desktop": desktop_json[least_popular_desktop], str(least_popular_mobile)+"_Mobile": mobile_json[least_popular_mobile]}
    time_series_plotter(name_to_timeseries, chart_title, chart_y_axis, output_f_name)

"""
This function will process the JSON data and calculate the information needed to generate chart 2 in the top comment of this file.
@param: desktop_json: a JSON file containing the desktop users queried from the wikimedia API in wikipedia_pageview_timeseries_generator.py
@param: mobile_json: a JSON file containing the mobile users queried from the wikimedia API in wikipedia_pageview_timeseries_generator.py
@param: output_f_name: the output file name or path to which the chart will be saved
@param: chart_y_axis: the y axis title of the chart
@param: chart_title: the charts main title
@returns None, will save png file to output_f_name and show an image of the chart in the terminal as well
"""
def generate_peak_viewers_chart(desktop_json, mobile_json, output_f_name = CHART_2_OUTPUT_FNAME, chart_y_axis = CHART_Y_AXIS_TITLE, chart_title = CHART_2_TITLE):
    #Lets create a dictionary which contains each dinosaur and its highest peak views along the timeseries. 
    highest_page_views_desktop = {}
    for name,timeseries in desktop_json.items():
        highest= max_page_view_calculator(timeseries)
        if highest > 0: #this will exclude any names with no timeseries available.
            highest_page_views_desktop[name] = highest

    highest_page_views_mobile = {}
    for name,timeseries in mobile_json.items():
        highest= max_page_view_calculator(timeseries)
        if highest > 0: #this will exclude any names with no timeseries available.
            highest_page_views_mobile[name] = highest
    #lets identify which 10 dinosaur had highest peak viewership on desktop and mobile
    highest_peak_desktop = sorted(highest_page_views_desktop, key=highest_page_views_desktop.get, reverse=True)[:10]
    highest_peak_mobile = sorted(highest_page_views_mobile, key=highest_page_views_mobile.get, reverse=True)[:10]
    #Highest peak by access type, lets combine them with their raw timeseries data for plotting.
    name_to_timeseries = {}
    for name in highest_peak_desktop:
        name_to_timeseries[name + "_Desktop"] = desktop_json[name]

    for name in highest_peak_mobile:
        name_to_timeseries[name + "_Mobile"] = mobile_json[name]
    time_series_plotter(name_to_timeseries, chart_title, chart_y_axis, output_f_name)


"""
This function will process the JSON data and calculate the information needed to generate chart 3 in the top comment of this file.
@param: desktop_json: a JSON file containing the desktop users queried from the wikimedia API in wikipedia_pageview_timeseries_generator.py
@param: mobile_json: a JSON file containing the mobile users queried from the wikimedia API in wikipedia_pageview_timeseries_generator.py
@param: output_f_name: the output file name or path to which the chart will be saved
@param: chart_y_axis: the y axis title of the chart
@param: chart_title: the charts main title
@returns None, will save png file to output_f_name and show an image of the chart in the terminal as well
"""
def generate_least_data_chart(desktop_json, mobile_json, output_f_name = CHART_3_OUTPUT_FNAME, chart_y_axis = CHART_Y_AXIS_TITLE, chart_title = CHART_3_TITLE):
    #Lets create a dictionary which contains each dinosaur and the number of months in its timeseries. 
    num_months_desktop = {}
    for name,timeseries in desktop_json.items():
        num_months= fewest_months_of_data_calculator(timeseries)
        num_months_desktop[name] = num_months

    num_months_mobile = {}
    for name,timeseries in mobile_json.items():
        num_months= max_page_view_calculator(timeseries)
        num_months_mobile[name] = num_months
    #lets identify which 10 dinosaur had least data on desktop and mobile
    lowest_months_desktop = sorted(num_months_desktop, key=num_months_desktop.get)[:10]
    lowest_months_mobile = sorted(num_months_mobile, key=num_months_mobile.get)[:10]
    print(lowest_months_desktop, lowest_months_mobile)
    #lets combine the lowest month count for mobile and desktop together so we can plot it
    name_to_timeseries = {}
    for name in lowest_months_desktop:
        name_to_timeseries[name + "_Desktop"] = desktop_json[name]

    for name in lowest_months_mobile:
        name_to_timeseries[name + "_Mobile"] = mobile_json[name]
    time_series_plotter(name_to_timeseries, chart_title, chart_y_axis , output_f_name)

desktop_json, mobile_json = load_data()
generate_average_chart(desktop_json, mobile_json)
generate_peak_viewers_chart(desktop_json, mobile_json)
generate_least_data_chart(desktop_json, mobile_json)


        