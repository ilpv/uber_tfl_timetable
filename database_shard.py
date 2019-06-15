from tfl_api import getStopPointArrivals,getAllStops 
from sqlalchemy import create_engine
from sqlalchemy import Column,Table,ForeignKey
from sqlalchemy import Integer,DateTime,Float,String
from sqlalchemy.ext.horizontal_shard import ShardedSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.sql import visitors
from sqlalchemy.sql import operators
import math
import datetime

# Grid XxY chunks for database shards
Xchunks = 3 
Ychunks = 3

# Coordinate bound for Greater London 
Ylow = -0.53
Yhigh = 0.35
Xlow = 51.25
Xhigh = 51.7

# Distances for nearest stops in meters
latMeters = 500. 
lonMeters = 500.

# Time to refresh database cache in sec
diff_time_sec = 60

# Radius of the Earth for 
# lat,lon to meters conversion
rEarth=6378137.

Debug = False
DataBaseSession = None
dbase = declarative_base()

#Sharding functions
def getStep(cur,high,low,num):
    size = (high-low)/float(num)
    return (float(cur)-float(low))/size 

def xy2id(x,y):
    return int(x)+int(y)*Xchunks

def getShardId(x,y):
    stepx = getStep(x,Xhigh,Xlow,Xchunks)
    stepy = getStep(y,Yhigh,Ylow,Ychunks)
    sid = xy2id(stepx,stepy)
    return sid

def getShardIds(sq_xlow,sq_xhigh,sq_ylow,sq_yhigh):
    ids = []
    stepxlow = getStep(sq_xlow,Xhigh,Xlow,Xchunks)
    stepxhigh = getStep(sq_xhigh,Xhigh,Xlow,Xchunks)
    stepylow = getStep(sq_ylow,Yhigh,Ylow,Ychunks)
    stepyhigh = getStep(sq_yhigh,Yhigh,Ylow,Ychunks)
    for x in range(int(stepxlow),int(stepxhigh)+1):
        for y in range(int(stepylow),int(stepyhigh)+1):
            ids.append(xy2id(x,y))
    return ids

#ORM classes
class Stops(dbase):
    __tablename__ = "Stops"
    lat = Column("lat", Float)
    lon = Column("lon", Float)
    stopName = Column("stopName", String(64))
    ref_time = Column("ref_time", DateTime, default = datetime.datetime.combine(datetime.date.min,datetime.time.min))
    stop_id = Column("stop_id",String(16),primary_key=True)
    timetables = relationship("Timetable", uselist=True, backref="stop")
    def __init__(self, stop_id, cname, lat, lon):
        self.stop_id = stop_id
        self.stopName = cname        
        self.lat = lat
        self.lon = lon

class Timetable(dbase):
    __tablename__ = "Timetable"
    id = Column(Integer, primary_key=True)
    stop_id = Column("stop_id", String(16), ForeignKey("Stops.stop_id"))
    stationName = Column("stationName", String(64))
    modeName = Column("modeName", String(32))
    lineName = Column("lineName", String(32))
    destinationName = Column("destinationName", String(64))
    timeToStation = Column("timeToStation", Integer)
    expectedArrival = Column("expectedArrival", String(32))
    def __init__(self, stop_id, stationName, modeName, lineName, destinationName, timeToStation, expectedArrival):
        self.stop_id = stop_id
        self.stationName = stationName
        self.modeName = modeName
        self.lineName = lineName
        self.destinationName = destinationName
        self.timeToStation = timeToStation
        self.expectedArrival = expectedArrival
   
def queryComparisons(query):
    binds = {}
    cls = set()
    cmps = []
    
    # Visitors
    def visit_bindparam(bind):
        if bind.key in query._params:
            value = query._params[bind.key]
        elif bind.callable:
            value = bind.callable()
        else:
            value = bind.value
        binds[bind] = value
    def visit_column(column):
        cls.add(column)
    def visit_binary(binary):
        if binary.left in cls and binary.right in binds:
            cmps.append((binary.left, binary.operator, binds[binary.right]))
        elif binary.left in binds and binary.right in cls:
            cmps.append((binary.right, binary.operator, binds[binary.left]))
    
    # Traverse query's criterion
    if query._criterion is not None:
        visitors.traverse_depthfirst(query._criterion,{},{
            "bindparam": visit_bindparam,
            "binary": visit_binary,
            "column": visit_column,
            },)
    return cmps

def shard_chooser(mapper, instance, clause=None):
    if isinstance(instance,Stops):
        return getShardId(instance.lat,instance.lon)
    else:
        return shard_chooser(mapper, instance.stop)

def id_chooser(query, ident):
    if query.lazy_loaded_from:
        return [query.lazy_loaded_from.identity_token]
    else:
        return range(Xchunks*Ychunks)
    
def query_chooser(query):
    ids = {}
    for column, operator, value in queryComparisons(query):
        if column.shares_lineage(Stops.__table__.c.lat):
            if operator == operators.lt:
                ids["LatHigh"]=value
            elif operator == operators.gt:
                ids["LatLow"]=value
        elif column.shares_lineage(Stops.__table__.c.lon):
            if operator == operators.lt:
                ids["LonHigh"]=value
            elif operator == operators.gt:
                ids["LonLow"]=value
    if len(ids) != 4:
        return range(Xchunks*Ychunks)
    else:
        return getShardIds(ids["LatLow"],ids["LatHigh"],ids["LonLow"],ids["LonHigh"])

# Init sharding database 
# with stops data parsed from xml
def init():
    db = {}
    for i in range(Xchunks*Ychunks):
        db[i] = create_engine(
                "mysql+mysqldb://root:uber@/tfl%d?unix_socket=/cloudsql/tflapiusage-1557507922735:us-central1:tfl-sql"%(i),
                echo=Debug)
    # create tables
    #for i in db:
    #    dbase.metadata.drop_all(db[i])
    #    dbase.metadata.create_all(db[i])
    session = sessionmaker(class_=ShardedSession)
    session.configure(shard_chooser=shard_chooser, id_chooser=id_chooser,
                      query_chooser=query_chooser, shards=db)
    DataBaseSession = session()
    #stopsDict = getAllStops()
    # Fill database shards with stops
    #for s in stopsDict:
    #    if "AtcoCode" in s and "Longitude" in s and "Latitude" in s and "CommonName" in s:
    #        sp = Stops(s["AtcoCode"],s["CommonName"],s["Latitude"],s["Longitude"])
    #        sp.timetables = []
    #        DataBaseSession.add(sp)
    #DataBaseSession.commit()
    return DataBaseSession

def getOffsets(lat,lon):
    latOff = (latMeters/rEarth)*180./math.pi
    lonOff = (lonMeters/(rEarth*math.cos(math.pi*lat/180.)))*180./math.pi
    return [latOff, lonOff] 

# Find nearest stops in database 
def getNearestStops(lat,lon,db):
    offs = getOffsets(lat,lon)
    stopData = db.query(Stops) \
               .filter(Stops.lat > lat-offs[0]).filter(Stops.lat < lat+offs[0]) \
               .filter(Stops.lon > lon-offs[1]).filter(Stops.lon < lon+offs[1])
    res = []
    for row in stopData:
        res.append({"naptanId":row.stop_id,"lat":row.lat,"lon":row.lon,"commonName":row.stopName}) 
    return res

# Obtain timetable by stop id 
# from database or through TFL API
def getTimeTable(naptanId,db):
    stp = db.query(Stops).get(naptanId)
    cur_time = datetime.datetime.now()
    res = {}
    if stp is None or stp.timetables is None:
        res["Error"]="Something goes wrong with database."
        return res
    if cur_time - stp.ref_time > datetime.timedelta(seconds=diff_time_sec):
        # Refresh database cache from tfl api
        res = getStopPointArrivals(naptanId)
        if res["Error"] == 0:
            dt = res["Data"]
            for tm in stp.timetables:
                db.delete(tm)
            for item in dt:
                stp.timetables.append(Timetable(item["naptanId"],item["stationName"],item["modeName"], \
                    item["lineName"],item["destinationName"],item["timeToStation"],item["expectedArrival"]))
            stp.ref_time = cur_time
            res["UpdateTime"] = cur_time
            db.add(stp)
            db.commit()
        else:
            res["Error"]="Timetable outdated."
    else:
        # Collect data from database
        dt = []
        for tt in stp.timetables:
            item = {}
            item["naptanId"] = tt.stop_id
            item["stationName"] = tt.stationName
            item["modeName"] = tt.modeName
            item["lineName"] = tt.lineName
            item["destinationName"] = tt.destinationName
            item["timeToStation"] = tt.timeToStation
            item["expectedArrival"] = tt.expectedArrival
            dt.append(item)
        res["UpdateTime"] = stp.ref_time
        res["Data"] = dt
    return res    
