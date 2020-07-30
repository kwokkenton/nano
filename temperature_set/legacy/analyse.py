#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 11:57:07 2020

@author: kenton
"""
import pandas as pd
import scipy as sp
from clean import cleanandmerge
import matplotlib.pyplot as plt


cm = cleanandmerge()
merged = cm.main()

off_curves = merged.filter(like='10mV_off')


def getio(curves):
    depvar = curves.filter(like='Ids')
    
    cols = []
    newcollist = ['oncurrent', 'offcurrent', 'onoffratio']
    for i in depvar.columns:
        for j in newcollist:
            cols.append(i+'_'+j)
            
    processed = {}
    
    for (indexName, rowData) in depvar.iterrows():
        processedArray = []
        for dataArray in rowData:
            maxval = sp.amax(dataArray)
            minval = sp.amin(dataArray)
            
            for val in [maxval, minval, maxval/minval]:
                processedArray.append(val)
            processed[indexName] = processedArray
                
        result = pd.DataFrame.from_dict(processed, orient='index')
        result.columns = cols
        
    return result


result = getio(off_curves)
#ior = result.filter(like='onoffratio')
#temps = ['80K', '100K', '150K', '200K', '250K', '300K']
#x = pd.DataFrame(ior.to_numpy(), columns=temps)
#ax = x.boxplot()
#ax.set_ylabel('On off ratios')
#%%
def gettrans(curves):
    #dependent and independent variables
    depvar = curves.filter(like='Ids')
    invar = curves.filter(like='Vgs')
    deg = 9
    
    processed = {}
    processed_max = {}
    
    for (dep, ind) in zip(depvar.iterrows(), invar.iterrows()):
        dep_index, dep_rowData  = dep
        in_index, in_rowData  = ind
        
        processedArray = []
        maxes = [] 
        
        for dep_data, in_data in zip(dep_rowData, in_rowData):
            deriv = sp.gradient(dep_data, in_data)
            processedArray.append(in_data)
            processedArray.append(deriv)
            
            try: 
                p = sp.polyfit(in_data, deriv, deg)      
                fit = sp.poly1d(p)(in_data)
                maxes.append(max(fit))
            except:
                maxes.append(None)

            
        processed[dep_index] = processedArray
        processed_max[dep_index] = maxes
        
    result = pd.DataFrame.from_dict(processed, orient='index')
    cols = [x.replace('Ids','tc') for x in curves.columns]
    result.columns = cols
    
    maxresult = pd.DataFrame.from_dict(processed_max, orient='index')
    cols = [x.replace('Ids','tc') for x in depvar.columns]
    maxresult.columns = cols  
    return result, maxresult


res, maxres = gettrans(off_curves)
#def batchplottrans(result, titletemp, curvepick=[1], deg = 9):
#    '''
#    '''
#    polys = []
#    maxtrans = [] 
#    
#    for dev in result:
#        plt.rcParams["figure.figsize"] = (7,4)
#        xpicked = (result[dev][0][i] for i in curvepick)
#        ypicked = (result[dev][1][i] for i in curvepick)
#        curvenamepicked = (curvenames[i] for i in curvepick)
#             
#        for x, y, cname in zip(xpicked, ypicked, curvenamepicked):
#            deriv = sp.gradient(y,x)
#            plt.scatter(x,deriv, label='Datapoints')
#            p = sp.polyfit(x, deriv, deg)
#            polys.append(p)
#            
#            fit = sp.poly1d(p)(x)
#            maxtrans.append(max(fit))
#            plt.plot(x, fit, color= 'orange', label='%sth degree fit' %deg)
#            
#            plt.ylim(0, 1.1 * max(deriv) )
#            xtickmin = min(x)
#            xtickmax = max(x)
#            plt.title(titletemp %dev)
#            plt.xlabel('Vgs (V)')
#            plt.ylabel('Transconductance (S)')
#            plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0)) #scientific axes
#            plt.xticks(sp.arange(xtickmin, xtickmax + 1))
#            plt.grid()
#            plt.legend()        
#            plt.show()
            
#    return polys, maxtrans
