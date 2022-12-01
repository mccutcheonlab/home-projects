# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 13:52:51 2019

@author: jmc010
"""

import matplotlib.pyplot as plt
import numpy as np
import datetime
import julian

n=0 # current Julian day

longitude=18.9553
latitude=69.6492
today=datetime.datetime.today()

n=julian.to_jd(today, fmt='jd')-2451545.0+0.0008
#n=0
#
Jstar=n-(longitude/np.radians(360)) # mean solar noon

M = np.mod((357.5291 + 0.98560028 * Jstar), 360) # solar mean anomaly
C = (1.9148*np.sin(M)) + (0.0200 * np.sin(2*M)) + (0.0003 * np.sin(3*M)) # equation of the center
lam = np.radians(np.mod((M + C + 180 + 102.9732), 360)) # ecliptic longitude

print(lam)

Jtran = 2451545.0 + Jstar + 0.0053*np.sin(M) - 0.0069*np.sin(2*lam) # solar transit

print(julian.from_jd(Jtran, fmt='jd'))


N=31 #(n days since 1st Jan)

declination=np.radians(-23.44)*np.cos(np.radians(360)/365*(N+10))

print(np.degrees(declination))

s1=np.cos(np.radians(90.833333))*(1/(np.cos(np.radians(latitude))))*(1/(np.cos(np.radians(declination))))
s2=np.tan(np.radians(latitude))*np.tan(np.radians(declination))

h=s1-s2

H = np.arccos(h)

print(np.degrees(H))

Hour_angle = np.degrees(H)/360

print(Hour_angle*24)
#Jrise=Jtran

