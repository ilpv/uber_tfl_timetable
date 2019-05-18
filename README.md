Arrival times using Transport for London Unified API
--------------------------------------------------------
App was created as a part of [Uber code challenge](https://github.com/uber-archive/coding-challenge-tools/blob/master/coding_challenge.md)
### Architecture
**Fronted** 
 -  Javascript AJAX with jQuery
 - Google Maps API to visualize geo location and nearest stops, choose stop to show arrival times

**Backed** 
 -  Flask and Python
 - Instant requests/response to TFL live arrivals API
 
**Unit testing**
-  unittest library
 ------------------------------------------------------------------------------------
  ### Usage
 1. Current position displayed as red circle. 
	 - App use Geo location to obtain current user position. 
	 - In case of failure it uses center of London as default. 
	 - User can change current position manually **right clicking** on the map.
 2. Stops displayed as red markers.
	 - App find nearest stops to current position within defined distance ( 300 m by default ) 
	 - Clicking on stops markers user can see timetable below the map 
 3. Arrival times displayed as html table
	 - First arriving are on the top

### TODO
- Use database caching and refreshing
- Filter stops with no arrival data ( probably additional exits from main stop ) or take it from main stop
- Javascript unit tests for edge cases
- Distance to stops changes and other GUI improvements

--------------------------------------------------------------
### Written code 
Frontend
> static/style.css
> static/tfl_gmaps.js
> templates/index.html 

Backend
> timetable.py
> tfl_api.py

Unit tests
> run_unittests.py

Cloud deployment support
> appengine_config.py
> requirements.txt
> app.yaml

### Deployment
App was deployed on Google AppEngine 
https://tflapiusage-1557507922735.appspot.com
