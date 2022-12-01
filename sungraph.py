# -*- coding: utf-8 -*-
"""
Created on Thu May  7 14:26:02 2020

@author: admin
"""


from pvlib import solarposition
from pvlib.solarposition import pyephem
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

tz = 'Europe/Paris'
lat, lon = 69.649, 18.955 # Tromsø

#tz = 'Europe/London'
#lat, lon = 51.1324, 0.2637 # Tunbridge Wells

days = pd.date_range('2020-01-01 00:00:00', '2021-01-01', closed='left',
                      freq='D', tz=tz)

try:
    print(f"Sun position already calculated for {len(data)} days.")
except:
    data = []
    for day in days:
        times = pd.date_range(day, day+pd.Timedelta(1, unit='D'), closed='left',
                              freq='min', tz=tz)
        solpos = solarposition.get_solarposition(times, lat, lon)
        data.append(solpos)

def time_of_elev(sunpos, elev=0):
    
    """ Takes sun position data for every day of the year and returns time when the
    sun crosses a specific elevation.
    """
    
    cross1, cross2 = [], []
    
    for day_idx, df in enumerate(sunpos):
        if max(df['apparent_elevation']) < elev:
            pass
        elif min(df['apparent_elevation']) > elev:
            pass
        else:
            above_elev = df[df['apparent_elevation'] > elev]
            cross1.append([day_idx, above_elev.index[0]])
            cross2.append([day_idx, above_elev.index[-1]])
        
    return cross1, cross2

def get_coords_from_crossings(cross1, cross2):
    
    """ Makes x and y arrays for plotting crossing for each day across the year"""
    
    x, y1, y2 = [], [], []
    
    for day in cross1:
        x.append(day[0])
        y=day[1].hour + day[1].minute/60
        y1.append(y)
        
    for day in cross2:
        y=day[1].hour + day[1].minute/60
        y2.append(y)
        
    return x, y1, y2


sunrise, sunset = time_of_elev(data)
civil_tw1, civil_tw2 = time_of_elev(data, elev=-6)
naut_tw1, naut_tw2 = time_of_elev(data, elev=-12)
astro_tw1, astro_tw2 = time_of_elev(data, elev=-18)

f, ax = plt.subplots(figsize=(12,4))


ax.set_facecolor('xkcd:midnight blue')

x, y1, y2 = get_coords_from_crossings(naut_tw1, naut_tw2)
ax.fill_between(x, y1, y2, color='mediumblue')

x, y1, y2 = get_coords_from_crossings(civil_tw1, civil_tw2)
ax.fill_between(x, y1, y2, color='cornflowerblue')

x, y1, y2 = get_coords_from_crossings(sunrise, sunset)
ax.fill_between(x, y1, y2, color='lightsteelblue')

ax.set_ylim([0, 24])
ax.set_yticks([0, 6, 12, 18, 24])
ax.set_yticklabels(['Midnight', '6AM', 'Noon', '6PM', 'Midnight'])

ax.set_xlim([0, 365])
ax.set_xticks([0, 30, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 364])
ax.set_xticklabels([])
#
xposlbl = [15, 45, 75, 105, 135, 165, 196, 227, 258, 288, 319, 349]
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

for pos, lbl in zip(xposlbl, months):
    ax.text(pos, -1.5, lbl, ha='center')
    
f.savefig('C:\\Users\\jmc010\\Dropbox\\Website\\images\\sungraph.pdf')


