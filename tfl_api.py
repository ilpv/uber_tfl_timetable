import urllib, json, logging
 
def getNearestStops(lat,lon):
    return geturl("https://api.tfl.gov.uk/Stoppoint?lat=%f&lon=%f&stoptypes=NaptanMetroStation,NaptanRailStation,NaptanBusCoachStation,NaptanFerryPort,NaptanPublicBusCoachTram"%(lat,lon))

def geturl(url):
    keys = {"app_id" : "e32d3714",
            "app_key" : "cb6fc56f2dcc7ea8538909f2438f810c"}
    user_agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
    headers = {'User-Agent': user_agent}
    url_full = url+"&"+urllib.urlencode(keys)
#    logging.info(url_full)
    response = urllib.urlopen(url_full)
    html = response.read()
#    logging.info(html)
    return html

