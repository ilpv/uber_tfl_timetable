import urllib, json, logging 
user_agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
headers = {'User-Agent': user_agent}
stopTypes = ["NaptanRailStation","NaptanPublicBusCoachTram", "NaptanMetroStation", "NaptanCoachBay","NaptanBusCoachStation"]
url="https://api.tfl.gov.uk/"
radius=500
keys = {"app_id" : "e32d3714",
        "app_key" : "cb6fc56f2dcc7ea8538909f2438f810c"}

def getNearestStops(lat,lon):
    urlStopPoints=url+"Stoppoint?lat=%f&lon=%f"%(lat,lon)+"&radius=%s"%radius
    urlStopPoints+="&"+urllib.urlencode(keys)+"&stoptypes=%s"%','.join(stopTypes)
    return reqTflAPI(urlStopPoints)

def getTimeTable(naptanId):
    urlStopPointId=url+"/StopPoint/%s/Arrivals"%naptanId
    urlStopPointId+="?"+urllib.urlencode(keys)
    return reqTflAPI(urlStopPointId)

def reqTflAPI(url_req):
    # Make request to server and return dict result
    # Add 'Error' to it for error handling
    resjson = {}
    try:
        response = urllib.urlopen(url_req)
    except HTTPError as err:
        resjson["Error"]='Server not responding %s'%err.code
    except URLError as err:
        resjson["Error"]='Server not reachable %s'%err.reason
    else:    
        html = response.read()
        resjson["Data"] = json.loads(html)
        resjson["Error"] = 0
    return resjson
