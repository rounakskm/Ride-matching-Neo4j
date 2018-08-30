#!/usr/bin/env python3
"""
Created on Mon Aug 13 22:09:58 2018

@author: Arima/Soumya
"""

import numpy as np
import pandas as pd
import pickle
 
from sklearn.linear_model import LinearRegression


def predict(X):

    # load the model from disk
    filename = 'trained_model.sav'
    regressor = pickle.load(open(filename, 'rb'))

    arr = np.array(X)
    y_pred = regressor.predict(arr.reshape(1, -1))

    from math import floor, ceil
    if (y_pred % 1) >= 0.4:
        y_pred = ceil(y_pred)
    else:
        y_pred = floor(y_pred)
    
    return y_pred

