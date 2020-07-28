# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 10:23:30 2020

@author: Chataing thibaut
"""

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True)