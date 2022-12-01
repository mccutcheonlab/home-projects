# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 15:12:57 2019

@author: jmc010
"""

#import sunrise.py
from datetime import date

s=sun(lat=69.6492,long=18.9553)
t1 = datetime(year = 2020, month = 6, day = 12, hour=12, minute=1, second=0)

print('sunrise at ',s.sunrise(when=t1) )