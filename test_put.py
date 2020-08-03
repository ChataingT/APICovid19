# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 12:36:26 2020

@author: Chataing thibaut
"""

import requests

response = requests.put('http://127.0.0.1:5000/api/countryByDate', json={
        "country": "aPlace",
        "date": "8/3/20",
        "cases" : 1,
        "deaths" : 3,
        "recoveries": 1
        })
print(response.headers)