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
    
    if not(country in LIST_COUNTRY):
        app.logger.error("Wrong input country=%s", country)
        abort(400)
    if not(date in LIST_DATE):
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
    app.logger.info("Return %s", ret)
    
    return jsonify(ret)
    
    

if __name__ == "__main__":
    (CASES_DF, DEATHS_DF, RECOVERIES_DF, WORDL_SUMMAR_DF) = loadCsvData2DF()
    LIST_COUNTRY = set(CASES_DF["country"].to_list())
    LIST_DATE = set(CASES_DF.columns.to_list()[1:]) # date format m/j/yy
    
    app.run(debug=True)