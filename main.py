# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 10:23:30 2020

@author: Chataing thibaut
"""

import os
from flask import Flask, jsonify
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
    
    cases_df = pd.read_csv(os.path.join(dir_path, "cases_data.csv"))
    deaths_df = pd.read_csv(os.path.join(dir_path, "deaths_data.csv"))
    recoveries_df = pd.read_csv(os.path.join(dir_path, "recoveries_data.csv"))
    world_summary = pd.read_csv(os.path.join(dir_path, "world_data.csv"))
    app.logger.info("Loaded")
    return (cases_df, deaths_df, recoveries_df, world_summary)


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/api/<country>/<path:date>")
def getStatsByCountry(country, date):
    app.logger.info("Country %s", country)
    app.logger.info("Date %s", date)
    # test date format m/j/yy
    (cases_df, deaths_df, recoveries_df, world_summary) = loadCsvData2DF()
    cases = cases_df.loc[cases_df["country"] == str(country)]
    cases = cases[str(date)]
    app.logger.debug("Cases : %s", cases)
    cases = str(cases.iloc[0])
    
    deaths = deaths_df.loc[deaths_df["country"] == str(country)]
    deaths = deaths[str(date)]
    deaths = str(deaths.iloc[0])
    
    recoveries = recoveries_df.loc[recoveries_df["country"] == str(country)]
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
    (cases_df, deaths_df, recoveries_df, world_summary) = loadCsvData2DF()
    app.run(debug=True)