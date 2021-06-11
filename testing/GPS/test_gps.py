from gps import *
from geopy.geocoders import Nominatim
import time
import threading
import osm_rg as rg
 
gpsd = None
class GpsPoller(threading.Thread):
   def __init__(self):
       threading.Thread.__init__(self)
       global gpsd
       gpsd=gps(mode=WATCH_ENABLE)
       self.current_value = None
       self.running = True
   def run(self):
       global gpsd
       while gpsp.running:
           gpsd.next()
   
gpsp=GpsPoller()

try:
   gpsp.start()
    
   while True:
       print(str(gpsd.fix.latitude) + "," + str(gpsd.fix.longitude) + "\n")
       
       city = (gpsd.fix.latitude, gpsd.fix.longitude)
       results = rg.get(city) # default mode = 1, precision = 2
       print(results)
       
       #locator = Nominatim()
       #coordinates = str(gpsd.fix.longitude) + "," + str(gpsd.fix.latitude)
       #location = locator.reverse(coordinates)
       #print(location.raw)
       #time.sleep(10)
   
except(KeyboardInterrupt,SystemExit):
   gpsp.running = False
   gpsp.join()
