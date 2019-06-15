import urllib, json
import zipfile
import os.path
from lxml import etree

user_agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
headers = {'User-Agent': user_agent}
url="https://api.tfl.gov.uk/"
keys = {"app_id" : "e32d3714",
        "app_key" : "cb6fc56f2dcc7ea8538909f2438f810c"}

# File name for xml data with stops coordinates 
localNaPTANxml = "NaPTANxml.zip"

# Wrap namespaces from tag
def wrapNm(tag):
    if '}' in tag:
        return tag.split('}', 1)[1]  

# Parse stops information from official xml file 
def getAllStops():
    pt = os.path.realpath(os.path.dirname(__file__))
    xml_file = os.path.join(pt, localNaPTANxml)
    napf = zipfile.ZipFile(xml_file, 'r')
    for name in napf.namelist():
        napxml = napf.open(name)
        break
    allstops = [] 
    context = etree.iterparse(napxml, events=('end',), tag='{http://www.naptan.org.uk/}StopPoint')
    for event, stoppoint in context:
        stopsDict = {} 
        ncode = stoppoint.find('{http://www.naptan.org.uk/}AtcoCode')
        place = stoppoint.find('{http://www.naptan.org.uk/}Place')
        desc = stoppoint.find('{http://www.naptan.org.uk/}Descriptor')
        if ncode is not None and place is not None and desc is not None:
            stopsDict[wrapNm(ncode.tag)] = ncode.text
            cname = desc.find('{http://www.naptan.org.uk/}CommonName')
            if cname is not None:
                stopsDict[wrapNm(cname.tag)] = cname.text
            for child in place.find('{http://www.naptan.org.uk/}Location') \
                              .find('{http://www.naptan.org.uk/}Translation'):
                stopsDict[wrapNm(child.tag)] = child.text
        allstops.append(stopsDict) 
        stoppoint.clear()
        while stoppoint.getprevious() is not None:
            del stoppoint.getparent()[0]
    return allstops                                                                                                                               

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
        dt = json.loads(html)
        if response.getcode()!=200:
            msg = dt["message"] if "message" in dt else "No message."
            resjson["Error"]='%s Response code %s'%(msg,response.getcode())
        else:
            resjson["Error"] = 0
        resjson["Data"] = dt 
    return resjson

# Obtain arrivals data by TFL API
def getStopPointArrivals(naptanId):
    urlStopPointId=url+"/StopPoint/%s/Arrivals"%naptanId
    urlStopPointId+="?"+urllib.urlencode(keys)
    return reqTflAPI(urlStopPointId)
