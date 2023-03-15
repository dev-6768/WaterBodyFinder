# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 13:44:55 2023

@author: HP
"""

from flask import Flask, render_template, request
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import geopy
import geocoder
import folium


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
@app.route("/", methods = ["GET", "POST"])

def locationApi():
    
    if(request.method == "POST"):
        locationCity = str(request.form.get("cityname"))
        locationCountry = str(request.form.get("countryname"))
        
        if(locationCity=="" or locationCountry==""):
            
            geocoderObject = geocoder.ip('me')
            first = str(geocoderObject.latlng[0])
            second = str(geocoderObject.latlng[1])
            
            locationObject = geopy.geocoders.Nominatim(user_agent="GetLoc")
            locationCurr = locationObject.reverse(first + ", " + second)
            locationCity = locationCurr.raw['address']['city']
            locationCountry = locationCurr.raw['address']['country']
            
        nominatim = Nominatim()
        areaId = nominatim.query(locationCity + ", " + locationCountry).areaId()
        
        nominatim_location = geopy.geocoders.Nominatim(user_agent="GetLoc")
        
        getLoc = nominatim_location.geocode(locationCity + " " + locationCountry)
        
        
        overpass = Overpass()
        query = overpassQueryBuilder(area=areaId, elementType=['way', 'relation'], selector='"natural"="water"', includeGeometry=True)
        result = overpass.query(query)
        
        firstElement = result.elements()[0]
        #print(firstElement.geometry()['coordinates'][0])
        
        sdf = firstElement.geometry()['coordinates'][0]
        
        dct = {}
        device = list(range(101, 101+len(sdf)))
        dct['GPSLat']=[]
        dct['GPSLng']=[]
        dct['device']=[]
        
        i=0
        for data in sdf:
            dct['device'].append(device[i])
            dct['GPSLat'].append(data[0])
            dct['GPSLng'].append(data[1])
            i+=1    
                    
        lati = getLoc.latitude
        longi = getLoc.longitude
        
        mapObj = folium.Map(location = [lati, longi],
        								zoom_start = 12)
        
        
        for i in range(len(dct['device'])):
            latitude = float(dct['GPSLat'][i])
            longitude = float(dct['GPSLng'][i])
            folium.CircleMarker(location = [longitude, latitude], 
                                radius = 5, popup = "Water Body No. "+str(i+1)).add_to(mapObj)
        
        mapObj.save('templates/mapData.html')
        
        return 'Data Submitted.<br>To View Map, <a href = "http://127.0.0.1:5000/map">Click here.</a>'

    return render_template("FrontService.html")

@app.route("/map", methods=['GET', 'POST'])
def mapRender():
    return render_template("mapData.html")


if(__name__=="__main__"):
    app.run()
    