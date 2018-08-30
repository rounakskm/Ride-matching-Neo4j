
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 22:09:58 2018

@author: Soumya/Arima
"""

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset
dataset = pd.read_csv('ride_data.csv')
X = dataset.iloc[:, :4].values # the input features 
y = dataset.iloc[:,-1].values  # the output  

print(X[0])
# Splitting the dataset into the Training set and Test set
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size = 0.2, 
                                                    random_state = 0)

#Optimizing the model using Backward Elimination

X = np.append(arr = np.ones((99,1)).astype(int), values = X, axis = 1)  
#used to append a column of ones in the begining of the features matrix. y=b0*x0+b1*x1....bn*xn. These ones make up x0


import statsmodels.formula.api as sm


def backwardElimination(x, SL = 0.4):
    '''
    Function performs backward elemination on the input features 
    based on a significance limit = 0.4 and returns only those 
    features that have the most impact on the result.
    
    Args:
        SL : significance limit
        x : input features appended with pne in the beginning
        
    Returns:
        The optimized list of features after eleminating weak features based
        on adjusted r-squared
        
    '''
    numVars = len(x[0])
    temp = np.zeros((99,6)).astype(int)
    flag = 1
    pvals = []
    for i in range(0, numVars):
        regressor_OLS = sm.OLS(y, x).fit()
        if (flag == 1):
            pvals = regressor_OLS.pvalues
            flag = 0
        maxVar = max(regressor_OLS.pvalues).astype(float)
        adjR_before = regressor_OLS.rsquared_adj.astype(float)
        if maxVar > SL:
            for j in range(0, numVars - i):
                if (regressor_OLS.pvalues[j].astype(float) == maxVar):
                    temp[:,j] = x[:, j]
                    x = np.delete(x, j, 1)
                    tmp_regressor = sm.OLS(y, x).fit()
                    adjR_after = tmp_regressor.rsquared_adj.astype(float)
                    if (adjR_before >= adjR_after):
                        x_rollback = np.hstack((x, temp[:,[0,j]]))
                        x_rollback = np.delete(x_rollback, j, 1)
                        print ()
                        return x_rollback
                    else:
                        continue
    regressor_OLS.summary()
    return x, pvals

SL = 0.4
X_opt = X[:, [0, 1, 2, 3, 4]] # starting with all columns

X_opt, pvals = backwardElimination(X_opt, SL)

selected_features = []
for i in range(0, len(pvals)):
    if pvals[i] <= SL:
        pass

# Using only optimal features 
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X_opt, y, 
                                                    test_size=0.2, 
                                                    random_state=0)      


#Fit model to training test
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(X_train, y_train)
      

#Predicting using the testing data
y_pred = regressor.predict(X_test)

# Note: This step will need to be performed after 
# the model gives out its predictions (not saved with trained model)
# Setting threshold and refining predictions
# May skiup this step if float type predictions 
# not mathcing test set are ok
from math import floor, ceil
for i,val in enumerate(y_pred):
        if (val % 1) >= 0.4:
            y_pred[i] = ceil(val)
        else:
            y_pred[i] = floor(val)

# Saving the model
import pickle

# save the model to disk
filename = 'trained_model.sav'
pickle.dump(regressor, open(filename, 'wb'))
