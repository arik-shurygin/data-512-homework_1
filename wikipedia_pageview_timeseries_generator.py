import json, time, urllib.parse, requests
import pandas as pd



# The REST API 'pageviews' URL - this is the common URL/endpoint for all 'pageviews' API requests
API_REQUEST_PAGEVIEWS_ENDPOINT = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/'

# This is a parameterized string that specifies what kind of pageviews request we are going to make
# In this case it will be a 'per-article' based request. The string is a format string so that we can
# replace each parameter with an appropriate value before making the request
API_REQUEST_PER_ARTICLE_PARAMS = 'per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}'

# The Pageviews API asks that we not exceed 100 requests per second, we add a small delay to each request
API_LATENCY_ASSUMED = 0.002       # Assuming roughly 2ms latency on the API and network
API_THROTTLE_WAIT = (1.0/100.0)-API_LATENCY_ASSUMED

# When making a request to the Wikimedia API they ask that you include a "unique ID" that will allow them to
# contact you if something happens - such as - your code exceeding request limits - or some other error happens
REQUEST_HEADERS = {
    'User-Agent': 'shurygin@uw.edu, University of Washington, MSDS DATA 512 - AUTUMN 2022',
}

# This is just a list of English Wikipedia article titles for the dinosaurs we are looking at
ARTICLE_TITLES = pd.read_csv("dinosaur_names_to_links_sept_2022.csv") ["name"]
# Start end end dates in YYYYMMDDSS format. API will search between these dates for pageview metrics
START_DATE = "2015070100"
END_DATE = "2022100100"
# output path for JSON data to be stored in once API is queried.
MOBILE_DATA_PATH = "dino_monthly_mobile_"+ str(START_DATE[0:6]) + "-" + str(END_DATE[0:6]) +".json"
DESKTOP_DATA_PATH = "dino_monthly_desktop_" + str(START_DATE[0:6]) + "-" + str(END_DATE[0:6]) + ".json"
COMBINED_DATA_PATH = "dino_monthly_cumulative_"+str(START_DATE[0:6]) + "-" + str(END_DATE[0:6])+".json"

# This template is used to map parameter values into the API_REQUST_PER_ARTICLE_PARAMS portion of an API request. The dictionary has a
# field/key for each of the required parameters. In the example, below, we only vary the article name, so the majority of the fields
# can stay constant for each request. Of course, these values *could* be changed if necessary.
ARTICLE_PAGEVIEWS_PARAMS_TEMPLATE = {
    "project":     "en.wikipedia.org",
    "access":      "",             # this value will be set/changed before each request
    "agent":       "user",
    "article":     "",             # this value will be set/changed before each request
    "granularity": "monthly",
    "start":       "",             # this value will be set/changed before each request
    "end":         ""              # this value will be set/changed before each request
}

def request_pageviews_per_article(article_title = None, 
                                  endpoint_url = API_REQUEST_PAGEVIEWS_ENDPOINT, 
                                  endpoint_params = API_REQUEST_PER_ARTICLE_PARAMS, 
                                  request_template = ARTICLE_PAGEVIEWS_PARAMS_TEMPLATE,
                                  headers = REQUEST_HEADERS,
                                  access = "desktop",
                                  start = START_DATE,
                                  end = END_DATE):
    # Make sure we have an article title
    if not article_title: return None
    
    # Titles are supposed to have spaces replaced with "_" and be URL encoded
    article_title_encoded = urllib.parse.quote(article_title.replace(' ','_'))
    request_template['article'] = article_title_encoded
    request_template['access'] = access
    request_template['start'] = start
    request_template['end'] = end
    
    # now, create a request URL by combining the endpoint_url with the parameters for the request
    request_url = endpoint_url+endpoint_params.format(**request_template)
    
    # make the request
    try:
        # we'll wait first, to make sure we don't exceed the limit in the situation where an exception
        # occurs during the request processing - throttling is always a good practice with a free
        # data source like Wikipedia - or other community sources
        if API_THROTTLE_WAIT > 0.0:
            time.sleep(API_THROTTLE_WAIT)
        response = requests.get(request_url, headers=headers)
        json_response = response.json()
    except Exception as e:
        print(e)
        json_response = None
    return json_response

"""
Queries the WIKIMEDIA API to find all page titles in the array titles between the start and end dates.
Then queries the mobile user page view metrics for both mobile-web and mobile-app sources and combines them together.
returns a JSON with each title in titles followed by a list of JSON objects, one for each month available to the API from start-end dates.
May return an empty list if no data on the title could be found.
@param: titles: an array of string article titles
@param: start a string of format YYYYMMDDSS for the start date of the search
@param: end: a string of format YYYYMMDDSS for the end date of the search
"""
def generate_mobile_monthly_pageviews(titles = ARTICLE_TITLES, start = START_DATE, end = END_DATE):
    mobile_jsons = {}
    for title in titles:
        mobile_web_json = request_pageviews_per_article(article_title=title, access="mobile-web", start=start, end=end)
        mobile_app_json = request_pageviews_per_article(article_title=title, access="mobile-app", start=start, end=end)
        if mobile_web_json is None or mobile_app_json is None:
            print(str(title) + " NOT FOUND BY THE API")
            mobile_jsons[title] = {}
            continue
        if "items" not in mobile_web_json.keys() or "items" not in mobile_app_json.keys():
            print(str(title) + " NOT FOUND BY THE API")
            mobile_jsons[title] = {}
            continue
        mobile_web_json = mobile_web_json["items"]
        mobile_app_json = mobile_app_json["items"]
        combined_json = mobile_app_json
        for month_ind in range(len(mobile_web_json)):
            month = mobile_web_json[month_ind]
            views = month["views"]
            combined_json[month_ind]["views"] += views #combining the views from the mobile-web access with the mobile-app access so we have sum of mobile views
        mobile_jsons[title] = combined_json
    return json.dumps(mobile_jsons, indent=4)

"""
Queries the WIKIMEDIA API to find all page titles in the array titles between the start and end dates.
Then queries the mobile user page view metrics for ALL sources.
returns a JSON with each title in titles followed by a list of JSON objects, one for each month available to the API from start-end dates.
May return an empty list if no data on the title could be found.
@param: titles: an array of string article titles
@param: start a string of format YYYYMMDDSS for the start date of the search
@param: end: a string of format YYYYMMDDSS for the end date of the search
"""
def generate_cumulative_monthly_pageviews(titles = ARTICLE_TITLES,  start = START_DATE, end = END_DATE):
    combined_jsons = {}
    for title in titles:
        combined_json = request_pageviews_per_article(article_title=title, access="all-access", start=start, end=end)
        if combined_json is None:
            print(str(title) + " NOT FOUND BY THE API")
            combined_json[title] = {}
            continue
        if "items" not in combined_json.keys() :
            print(str(title) + "NOT FOUND BY THE LOOKUP")
            combined_jsons[title] = {}
            continue
        combined_json = combined_json["items"]
        running_sum_views = 0
        for month in combined_json:
            running_sum_views += month["views"]
            month["views"] = running_sum_views
        combined_jsons[title] = combined_json
        
    return json.dumps(combined_jsons, indent=4)

"""
Queries the WIKIMEDIA API to find all page titles in the array titles between the start and end dates.
Then queries the mobile user page view metrics for DESKTOP sources and combines them together.
returns a JSON with each title in titles followed by a list of JSON objects, one for each month available to the API from start-end dates.
May return an empty list if no data on the title could be found.
@param: titles: an array of string article titles
@param: start a string of format YYYYMMDDSS for the start date of the search
@param: end: a string of format YYYYMMDDSS for the end date of the search
"""
def generate_desktop_monthly_pageviews(titles = ARTICLE_TITLES,  start = START_DATE, end = END_DATE):
    dekstop_jsons = {}
    for title in titles:
        desktop_json = request_pageviews_per_article(article_title=title, access="desktop", start=start, end=end)
        if desktop_json is None:
            print(str(title) + " NOT FOUND BY THE API")
            desktop_json[title] = {}
            continue
        if "items" not in desktop_json.keys() :
            print(str(title) + "NOT FOUND BY THE LOOKUP")
            dekstop_jsons[title] = {}
            continue
        desktop_json = desktop_json["items"]
        dekstop_jsons[title] = desktop_json
        
    return json.dumps(dekstop_jsons, indent=4)

if __name__ == "__main__":
    #KEY NOTE. THE API fails to find the webpages for Tuebingosaurus and Elemgasem. Thus they are given empty timeseries and will show up later in analysis!
    print("Generating Monthly Pageviews of MOBILE users")
    mobile_jsons = generate_mobile_monthly_pageviews()
    jsonFile = open(MOBILE_DATA_PATH, "w")
    jsonFile.write(mobile_jsons)
    print("Generating Monthly Pageviews of DESKTOP users")
    desktop_jsons = generate_desktop_monthly_pageviews()
    jsonFile = open(DESKTOP_DATA_PATH, "w")
    jsonFile.write(desktop_jsons)
    print("Generating Monthly Pageviews of ALL users")
    combined_jsons = generate_cumulative_monthly_pageviews()
    jsonFile = open(COMBINED_DATA_PATH, "w")
    jsonFile.write(combined_jsons)
