# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 10:23:30 2020

@author: Chataing thibaut
"""

import os, json
from flask import Flask, jsonify, abort, request
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

def initGlobalData():
    global CASES_DF, DEATHS_DF, RECOVERIES_DF, WORLD_SUMMARY_DF
    global SET_COUNTRY, SET_DATE, MAX_DATE
    
    dir_path="data"
    CASES_DF = pd.read_csv(os.path.join(dir_path, "cases_data.csv"))
    DEATHS_DF = pd.read_csv(os.path.join(dir_path, "deaths_data.csv"))
    RECOVERIES_DF = pd.read_csv(os.path.join(dir_path, "recoveries_data.csv"))
    WORLD_SUMMARY_DF = pd.read_csv(os.path.join(dir_path, "world_data.csv"))
    
    SET_COUNTRY = set(CASES_DF["country"].to_list())
    app.logger.debug("Columns : %s", CASES_DF.columns.to_list())
    SET_DATE = CASES_DF.columns.to_list()[2:] # date format m/j/yy
    MAX_DATE = max(SET_DATE)
    SET_DATE = set(SET_DATE)
    
    app.logger.debug("Global %s", [SET_COUNTRY, SET_DATE, MAX_DATE])


def getDataInDF(country, date):
    cases = CASES_DF.loc[CASES_DF["country"] == str(country)]
    cases = cases[date]
    app.logger.debug("Cases : %s", cases)
    cases = int(cases.iloc[0])
    
    deaths = DEATHS_DF.loc[DEATHS_DF["country"] == str(country)]
    deaths = deaths[date]
    deaths = int(deaths.iloc[0])
    
    recoveries = RECOVERIES_DF.loc[RECOVERIES_DF["country"] == str(country)]
    recoveries = recoveries[date]
    recoveries = int(recoveries.iloc[0])
    
    ret = {
        "country" : country,
        "date" : date,
        "cases" : cases,
        "deaths" : deaths,
        "recoveries": recoveries
        }
    return ret


@app.route("/")
def hello():
    return "Hello World!"

"""
Api for request by country and by date.
@params :
    country (str) : country wanted 
    date (str) : date in the format m/d/y
@return :
    - Error 400 : Bad request  if parameter are not found in the data
    - JSON : {
        "country" : str,
        "date" : str,
        "cases" : int,
        "deaths" : int,
        "recoveries": int
        }
"""
@app.route("/api/<country>/<path:date>", methods=['GET'])
def getStatsByCountryAndByDate(country, date):
    if not(country in SET_COUNTRY):
        app.logger.error("Wrong input country=%s", country)
        abort(400)
    if not(date in SET_DATE):
        app.logger.error("Wrong input date=%s", date)
        abort(400)
        
    app.logger.info("Request by country and date [%s,%s]", country, date)
    
    ret = getDataInDF(country, date)
    
    return jsonify(ret)

"""
Api for request of latrest data by country
@params :
    country (str) : country wanted 
@return :
    - Error 400 : Bad request  if parameter are not found in the data
    - JSON : {
        "country" : str,
        "date" : str,
        "cases" : int,
        "deaths" : int,
        "recoveries": int
        }
"""
@app.route("/api/latest/<country>")
def getLatestByCountry(country):
    if not(country in SET_COUNTRY):
        app.logger.error("Wrong input country=%s", country)
        abort(400)
    
    
    ret = getDataInDF(country, MAX_DATE)
    return ret
    
"""
Api for request of world summary data by date
@params :
    date (str) : date in the format m/d/y
@return :
    - Error 400 : Bad request  if parameter are not found in the data
    - JSON :     ret = {
        "date" : str,
        "cases" : int,
        "total_deaths" : int,
        "total_recoveries": int,
        "total_active": int,
        "mortality_rate": float,
        "recoveries_rate": float
        }
"""
@app.route("/api/world_summary/<path:date>")
def getWorlSummaryByDate(date):
    if not(date in SET_DATE):
        app.logger.error("Wrong input date=%s", date)
        abort(400)
        
    world_summary = WORLD_SUMMARY_DF[str(date)].to_list()
      
    ret = {
        "date" : date,
        "cases" : int(world_summary[0]),
        "total_deaths" : int(world_summary[1]),
        "total_recoveries": int(world_summary[2]),
        "total_active": int(world_summary[3]),
        "mortality_rate": float(world_summary[4]),
        "recoveries_rate": float(world_summary[5])
        }
    
    return jsonify(ret)

@app.route("/api/countryByDate", methods=['PUT'])
def putByCountryAndByDate():

    app.logger.debug("PUT data %s",request.data)
    data = json.loads(request.data)
    app.logger.debug("OU, %s", [data, type(data["cases"])])
    
    # Tester l'intégrité du json (key and value type)
    """
    JSON : {
        "country": str
        "date": str,
        "cases" : int,
        "deaths" : int,
        "recoveries": int
        }
    """
    if (data["country"] in SET_COUNTRY):
        i = CASES_DF.loc[CASES_DF["country"]==data["country"]].index[0]
        
        new_cases_df = CASES_DF.copy()
        new_deaths_df = DEATHS_DF.copy()
        new_recoveries_df = RECOVERIES_DF.copy()

        new_cases_df.loc[i,data["date"]] = data["cases"]
        new_deaths_df.loc[i,data["date"]] = data["deaths"]
        new_recoveries_df.loc[i,data["date"]] = data["recoveries"]

                
    else:        
        new_cases_df = CASES_DF.append({'country': str(data["country"]),
                                        data["date"]: int(data["cases"])}, ignore_index=True).fillna(0)
        new_deaths_df = DEATHS_DF.append({'country': data["country"],
                                        data["date"]: int(data["deaths"])}, ignore_index=True).fillna(0)
        new_recoveries_df = RECOVERIES_DF.append({'country': data["country"],
                                    data["date"]: int(data["recoveries"])}, ignore_index=True).fillna(0)
    column = new_cases_df.columns.to_list()[0]
    new_cases_df.pop(column)
    new_deaths_df.pop(column)
    new_recoveries_df.pop(column)
    app.logger.debug("test %s", new_cases_df.loc[new_cases_df["country"]==data["country"]])
    dir_path="data"
    new_cases_df.to_csv(os.path.join(dir_path, "cases_data.csv"))
    new_deaths_df.to_csv(os.path.join(dir_path, "deaths_data.csv"))
    new_recoveries_df.to_csv(os.path.join(dir_path, "recoveries_data.csv"))
    
    #Calcul for world summary
    
    cases_sum = new_cases_df[data["date"]].sum()
    death_sum = new_deaths_df[data["date"]].sum()
    recovered_sum = new_recoveries_df[data["date"]].sum()
    
    new_world_data = {
    "cases": cases_sum,
    "total_deaths": death_sum,
    "total_recovered": recovered_sum,
    "total_active": (cases_sum-death_sum-recovered_sum), 
    "mortality_rate": (death_sum/cases_sum),
    "recovery_rate": (recovered_sum/cases_sum)
    }
    
    new_world_summary_df = WORLD_SUMMARY_DF.append(new_world_data, ignore_index=True).fillna(0)
    new_world_summary_df.to_csv(os.path.join(dir_path, "world_data.csv"))
    
    initGlobalData()
    
    return jsonify({"Reponse": 'Data updated'})
    

        
if __name__ == "__main__":
    initGlobalData()
    app.run(debug=True)