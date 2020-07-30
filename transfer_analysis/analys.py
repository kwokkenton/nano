#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 23:16:30 2020

@author: kenton
"""

import matplotlib.pyplot as plt
import seaborn as sns
from cleanse import cleanse
import pandas as pd
import scipy as sp

sns.set_style("darkgrid")
sns.set_context("talk") 

class analys: 
    def __init__(self):
        self.c = cleanse()
        self.df = self.c.getdf()
        self.augdf = self.augmentTrans(self.df, 9)
        self.pardf = self.genParams(self.augdf)
        pass
    
    ### preprocessing suite ######################
    def filterdf(self, df, filters):
        ''' filters dataframes based on a filter input using AND for layers 
        and OR for sublayers
        '''
        original = df
    
        for f in filters:
            if f == ['all'] or list(f) == ['all']: # do not filter this layer if all is required
                pass
            else:
                for cond in f: 
                    temp = df.filter(like=cond)  # and method
                    if temp.empty: # or method
                        df = df.join(original.filter(like=cond))   
                    else: 
                        df = temp
            original = df # backup for each layer        
        return df 

    ### mechanical suite #########################            

    def convOrder(self, order):
        ''' converts a list of strings into indexable parameters
        '''
        convert = []
        
        for o in order:
            if o == 'temperatures' or o=='temperature':
                convert.append([str(temp) +'K' for temp in self.c.temperatures])
            if o == 'devices' or o=='device':
                convert.append(list(self.c.devs))
            if o == 'trials':
                convert.append(list(self.c.trials))
            if o == 'experiments':
                convert.append(self.c.curvenames)
        return convert
            
   
    def genloop(self, order, split, df, func):
        ''' main function for a looping plot
        '''
        convert = self.convOrder(order) 
        splitpos = [split == o for o in order]
        self.forplot(convert, splitpos, df, func)
        pass
    
    
    def forplot(self, convert, splitpos, df, func, args = []):
        ''' recursively plots
        '''
        conv, s = convert[0], splitpos[0]
        convert, splitpos = convert[1:], splitpos[1:]
        
        if s:
            firstrun = True
            for i in df.columns:
                if firstrun: 
                    title = list(i.split('_'))
                    firstrun = False
            else: 
                title = list(set(i.split('_')) & set(title))
            
            title.sort(reverse=True)
            exec(func)
            return
        else:
            for citem in conv:
                smallerdf = df.filter(like= citem)
                if not smallerdf.empty: # if citem is in filtered DataFrame
                    args.append(citem)
                    self.forplot(convert, splitpos, smallerdf, func, args)  
           
            
    ### augment suite ###################
    def augmentTrans(self, df, deg):
        ''' joins calculated and fitted transconductances to existing dataframe
        '''
        xs = sp.array(df.filter(like='Vgs'))
        ys = df.filter(like='Ids')
        grad_cols = [i.replace('Ids', 'tcd') for i in ys.columns] 
        fit_cols = [i.replace('Ids', 'tcfit') for i in ys.columns] 
        
        grads = []
        fits  = []
        for x, y in zip(sp.array(xs).T, sp.array(ys).T): 
            g = sp.gradient(y,x)
            grads.append(g)
            
            p = sp.polyfit(x, g, deg)      
            fit = sp.poly1d(p)(x)
            fits.append(fit)
            
        graddf = pd.DataFrame(sp.array(grads).T, columns = grad_cols)
        fitdf = pd.DataFrame(sp.array(fits).T, columns = fit_cols)
        
        df = df.join(graddf)
        df = df.join(fitdf)
        
        return df
    
    
    def genParams(self, df):
        data = []
        ys = sp.array(df.filter(like='Ids')).T
        fits = sp.array(df.filter(like='tcfit')).T
        
        cols = [i.replace('_Ids','') for i in df.filter(like='Ids').columns]
        
        for y, f in zip(ys, fits): 
            on = sp.amax(y)
            off = sp.amin(y)
            data.append([off, on, on/off, sp.amax(f)])
        datadf = pd.DataFrame(sp.array(data).T, index=['off','on','onoff', 'maxtc'], columns = cols)
        return datadf

    
    #### plotting suite #################
    def getLabels(self, columns, title, remove):
        ''' generates an array of useful labels
        '''
        firstRun = True
        for i in columns:
            splitted = i.split('_')
            splitted.remove(remove)
            if firstRun: 
                labels = list([sorted(set(splitted) ^ set(title))])
                firstRun = False
            else :
                labels.append(sorted((set(splitted) ^ set(title))))
        return labels
    
    
    def plotTransfer(self, dataframe, title=None):
        ''' plots transfer curves based on what is provided in the dataframe
        '''
        x = dataframe.filter(like = 'Vgs')
        y = dataframe.filter(like = 'Ids')
        plt.plot(x,y)
        
        # returns a set of labels that are deemed useful for comparison
        labels = self.getLabels(y.columns, title, 'Ids')
                
        plt.legend(labels) 
        
        plt.xlabel('$V_{gs}$  (V)')
        plt.ylabel('$I_{ds}$  (A)')
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        plt.title(title)
        plt.show()      
        pass


    def plotTC(self, dataframe, title=None):
        
        x = dataframe.filter(like = 'Vgs')
        y = dataframe.filter(like = 'tcd')
        
        fit = dataframe.filter(like = 'tcfit')
        
        labels = self.getLabels(y.columns, title, 'tcd')
        
        for i in range(len(labels)):
            
            plt.scatter(x.iloc[:,1],y.iloc[:,i], s=10, label = labels[i])
            
        plt.plot(x, fit)
        plt.ylim(y.min().min(), y.max().max())

        plt.legend()
        plt.xlabel('$V_{gs}$  (V)')
        plt.ylabel('Transconductance ($S$)')
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        plt.title(title)
        plt.show()
        
        pass
    
    def plotPars(self, dataframe, title=None):
        
        plt.hist(dataframe.loc['on/off'])
        plt.title(title)
        
        pass
    
    ### main suite || test cases ######################
    
    def main1(self):
        ''' transfer curve plots
        '''
        temperatures = ['80K']
        devices = ['0303d69']
        trials = ['all']
        experiments = ['10mV-off']
        filters = [temperatures, devices, trials, experiments]
        
        filtered = self.filterdf(self.df, filters)

        order = ['devices', 'temperatures', 'trials', 'experiments']
        self.split = 'devices'
        self.genloop(order, self.split, filtered, 'self.plotTransfer(df, title)')
        
        pass
    
    
    def main2(self):
        ''' transconductance plots
        '''
        temperatures = ['all']
        devices = ['all']
        trials = ['(1)']
        experiments = ['10mV-off']
        filters = [temperatures, devices, trials, experiments]
        
        order = ['temperatures', 'devices', 'trials', 'experiments']
        split = 'devices'
            
            
        filtered = self.filterdf(self.augdf, filters)
        self.genloop(order, split, filtered, 'self.plotTC(df, title)')

        pass


#a = analys()
#a.main3()

# TODO some GUI
