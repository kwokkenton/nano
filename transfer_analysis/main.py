#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 11:12:01 2020

@author: kenton
"""

from cleanse import cleanse 
from analys import analys 
from analyspars import analyspars
import glob

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

f = open('settings.txt')
exec(f.read())

c = cleanse()
a = analys(degree)
ap = analyspars()

filtered = a.filterdf(a.df, filters)

#%%
if plotTransferCurves: 
    plt.figure(figsize=(12,6))
    a.genloop(order, split, filtered, 'plt.figure(figsize=(12,6)); self.plotTransfer(df, title);')
    
if plotTransconductances:
    plt.figure(figsize=(12,6))
    a.genloop(order, split, a.filterdf(a.augdf, filters), 'plt.figure(figsize=(12,6)); self.plotTC(df, title)')   

### analysis of parameters
if plotAnalysedParams: 
    catdf = ap.categorisedf(a.genParams(a.filterdf(a.augdf, filters)))
    catdf.to_csv('./output/catdf.csv')
    
    ap.iohist(catdf)
    
    ap.cat(catdf, 'onoff')
    
    ap.cat(catdf, 'maxtc')

