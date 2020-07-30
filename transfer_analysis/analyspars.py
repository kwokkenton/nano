#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 15:53:29 2020

@author: kenton
"""

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from analys import analys

class analyspars: 
    def __init__(self):
        self.a = analys()
        self.layers = ['temperature', 'device', 'trial', 'experiment']
        self.df = self.categorisedf(self.a.pardf)
        pass
    
    def categorisedf(self, df):
        df = df.transpose().rename_axis('id').reset_index()
        df[self.layers] = df.id.str.split('_', expand = True)
        return df
    
    def getFiltered(self, filters):
        df = self.df
        layers = self.layers
        
        for fil, l in zip(filters, layers):
            if fil == 'all' or fil == ['all']: 
                pass
            else: 
                for f in fil:
                    df = df.loc[df[l] == f]
        
        df.loc[: , 'temperature'] = [int(i.replace('K','')) for i in df.loc[:, 'temperature']]
        return df
    
    def avgQuants(self, filtered): 
        ''' gives a set of average quantity plots
        '''
        avged = filtered.groupby(['temperature']).mean()
        stds = filtered.groupby(['temperature']).std()
        
        f, axes = plt.subplots(2, 2, figsize=(10, 4), sharex=True)
        #plt.title('hi')
        cols = avged.columns
        f.suptitle('Averaged quantities')
        
        sns.lineplot(x= avged.index, y = avged[cols[0]], ax=axes[0, 0])
        sns.lineplot(x= avged.index, y = avged[cols[1]], ax=axes[0, 1], ci='sd')
        sns.lineplot(x= avged.index, y = avged[cols[2]], color='g', ax=axes[1, 0])
        sns.lineplot(x= avged.index, y = avged[cols[3]], color = 'r', ax=axes[1, 1])
    #    axes[0,0].errorbar(x = avged.index, y = avged[cols[0]], yerr = stds[cols[0]])
    #    axes[0,1].errorbar(x = avged.index, y = avged[cols[1]], yerr = stds[cols[1]])
    #    axes[1,0].errorbar(x = avged.index, y = avged[cols[2]], yerr = stds[cols[2]], color='g')
    #    axes[1,1].errorbar(x = avged.index, y = avged[cols[3]], yerr = stds[cols[3]], color = 'r')
        
        axes[1,0].set_xlabel('Temperature (K)')
        axes[1,1].set_xlabel('Temperature (K)')
        
    def cat(self, df, yname):
        y = df[yname]
        
        sns.catplot(x="temperature", y= yname, hue="device", kind="swarm", data=df)
        plt.ylim(y.min(), y.max()* 1.1)


ap = analyspars()
#%%
#ap.layers
 
#temperatures = ['all']
#devices = ['all']
#trials = ['all']
#experiments = ['10mV-off']
#filters = [temperatures, devices, trials, experiments]
#
#filtered =  ap.getFiltered(filters)
#ap.cat(filtered, 'maxtc')