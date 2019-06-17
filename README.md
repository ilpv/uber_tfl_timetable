Arrival times using Transport for London Unified API
----
App was created as a part of [Uber code challenge](https://github.com/uber-archive/coding-challenge-tools/blob/master/coding_challenge.md)
### Architecture
**Frontend** 
 - Javascript AJAX with jQuery
 - Google Maps API to visualize geo location and nearest stops, choose stop to show arrival times

**Backend** 
 - Flask and Python
 - Instant requests/response to TFL live arrivals API
 - Horizontal sharding database cache by sqlalchemy 
 - 3x3 mysql databases on one google cloud sql instance created for example
 
**Unit testing**
 - unittest library
----
### Usage
 1. Current position displayed as red circle. 
	 - App use Geo location to obtain current user position. 
	 - In case of failure it uses center of London as default. 
	 - User can change current position manually **right clicking** on the map.
 2. Stops displayed as red markers.
	 - App find nearest stops to current position within defined distance ( 500 m by default ) 
	 - Clicking on stops markers user can see timetable below the map 
 3. Arrival times displayed as html table
	 - First arriving are on the top
 4. Arrival times are cached by sharding database
	 - Split London's transport area to squares
	 - For every square stops information stored in corresponding database shard
	 - Depending from coordinates and distance we chose proper shards ( it may be one or several )
	 - All stops coordinates and initially loaded to database from official xml and all requests for nearest stops goes to database 
	 - Timetables requests are cached by corresponding database shard and refreshed upon request ( 120 sec by default )
----
### TODO
- Improve concurrency and performance
- Filter stops with no arrival data ( probably additional exits from main stop ) or take it from main stop
- Javascript unit tests for edge cases
- Distance to stops changes and other GUI improvements

----
### Written code 
Frontend
> static/style.css
> static/tfl_gmaps.js
> templates/index.html 

Backend
> timetable.py
> tfl_api.py
> database_shard.py

Unit tests
> run_unittests.py

Official xml with TFL API stoppoints
> NaPTANxml.zip

Cloud deployment support
> appengine_config.py
> Pipfile
> app.yaml
> cloud_sql_proxy    

----
### Deployment
App was deployed on Google AppEngine 
https://tflapiusage-1557507922735.appspot.com
