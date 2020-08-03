# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 10:23:30 2020

@author: Chataing thibaut
"""

import os
from flask import Flask, jsonify, abort
from logging.config import dictConfig

import pandas as pd

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})
app = Flask(__name__)


def loadCsvData2DF(dir_path="data"):
    
    CASES_DF = pd.read_csv(os.path.join(dir_path, "cases_data.csv"))
    DEATHS_DF = pd.read_csv(os.path.join(dir_path, "deaths_data.csv"))
    RECOVERIES_DF = pd.read_csv(os.path.join(dir_path, "recoveries_data.csv"))
    WORDL_SUMMAR_DF = pd.read_csv(os.path.join(dir_path, "world_data.csv"))
    app.logger.info("Loaded")
    return (CASES_DF, DEATHS_DF, RECOVERIES_DF, WORDL_SUMMAR_DF)


@app.route("/")
def hello():
    return "Hello World!"

"""
Api for request by country and by date.
@params :
    country (str) : country wanted 
    date (int) : date in the format m/d/y
@return :
    - Error 400 : Bad request  if parameter are not found in the data
    - JSON : {
        "country" : country,
        "date" : date,
        "cases" : cases,
        "deaths" : deaths,
        "recoveries": recoveries
        }
"""
@app.route("/api/<country>/<path:date>")
def getStatsByCountryAndByDate(country, date):
    if not(country in SET_COUNTRY):
        app.logger.error("Wrong input country=%s", country)
        abort(400)
    if not(date in SET_DATE):
        app.logger.error("Wrong input date=%s", date)
        abort(400)
        
    app.logger.info("Request by country and date [%s,%s]", country, date)

    cases = CASES_DF.loc[CASES_DF["country"] == str(country)]
    cases = cases[str(date)]
    app.logger.debug("Cases : %s", cases)
    cases = str(cases.iloc[0])
    
    deaths = DEATHS_DF.loc[DEATHS_DF["country"] == str(country)]
    deaths = deaths[str(date)]
    deaths = str(deaths.iloc[0])
    
    recoveries = RECOVERIES_DF.loc[RECOVERIES_DF["country"] == str(country)]
    recoveries = recoveries[str(date)]
    recoveries = str(recoveries.iloc[0])
    
    ret = {
        "country" : country,
        "date" : date,
        "cases" : cases,
        "deaths" : deaths,
        "recoveries": recoveries
        }
    
    return jsonify(ret)

"""
Api for request of latrest data by country
@params :
    country (str) : country wanted 
@return :
    - Error 400 : Bad request  if parameter are not found in the data
    - JSON : {
        "country" : country,
        "date" : date,
        "cases" : cases,
        "deaths" : deaths,
        "recoveries": recoveries
        }
"""
@app.route("/api/latest/<country>")
def getLatestByCountry(country):
    latest_date = max(SET_DATE)
    ret = getStatsByCountryAndByDate(country, latest_date)
    return ret
    

@app.route("/api/world_summary/<path:date>")
def getWorlSummaryByDate(date):
    if not(date in SET_DATE):
        app.logger.error("Wrong input date=%s", date)
        abort(400)
        
    world_summary = WORLD_SUMMARY_DF[str(date)].to_list()
      
    ret = {
        "date" : date,
        "cases" : world_summary[0],
        "total_deaths" : world_summary[1],
        "total_recoveries": world_summary[2],
        "total_active": world_summary[3],
        "mortality_rate": world_summary[4],
        "recoveries_rate": world_summary[5]
        }
    
    return jsonify(ret)
        
if __name__ == "__main__":
    (CASES_DF, DEATHS_DF, RECOVERIES_DF, WORLD_SUMMARY_DF) = loadCsvData2DF()
    SET_COUNTRY = set(CASES_DF["country"].to_list())
    SET_DATE = CASES_DF.columns.to_list()[2:] # date format m/j/yy
    SET_DATE.sort()
    SET_DATE = set(SET_DATE)

    app.run(debug=True)