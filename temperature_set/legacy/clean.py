#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 12:48:13 2020

@author: kenton
"""

#import useful packages
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import glob
import os

#define class
class cleanandmerge: 
    """ Used for cleaning, merging and exporting data
    """
    
    def __init__(self):
        ncurves = 4     
        curvenames = ['10mV_on', '10mV_off', '30mV_on','30mV_off']
        measured = ['Vgs', 'Ids']
        folder = './raw_data/'
        keepall = True
        
        self.ncurves = ncurves
        self.curvenames = curvenames
        self.measured = measured
        self.folder = folder
        self.keepall = keepall
        pass
    
  
    def extractnames(self, filepaths): 
        ''' uses specific naming pattern to identify the device name in a loop
        
        Example
        -------
        Filename: Transfer [0312a25(2) ; 7_16_2020 4_14_24 PM].csv
        This selects all .csv files, and extracts the name by selecting the string
        before the '[' and ' ', hence 0312a25(2). 
        '''
        names = []
        for i in filepaths:
            dev = ''
            reading = False
            for char in i:
                if char == ' ': 
                    reading = False             
                if reading:
                    dev += char
                if char == '[': 
                    reading = True  
            names.append(dev)
        return names


    def extractdata(self, filepath):
        ''' Extracts data from input files, accounting for different file formats
            so to skip different number of rows
        '''
        with open(filepath, 'r') as f:
            try:
                data = sp.loadtxt(f, skiprows = 1, delimiter= ',')
            except: 
                try:
                    data = sp.loadtxt(f, skiprows= 252, delimiter=',', usecols = [1, 2])
                except: 
                    data = sp.loadtxt(f, skiprows= 255, delimiter=',', usecols = [1,3])
        return data


    def readandsort(self, path):
        ''' Automatically reads CSV files and extract device names, sort
        '''
        
        filepaths = glob.glob(path + '/*.csv')
        names = self.extractnames(filepaths)
        names, filepaths = [list(i) for i in zip(*sorted(zip(names,filepaths), key= lambda dual: dual[0]))]
            
        return names, filepaths


    def splitdata(self, filepaths, names, ncurves, curvenames): 
        ''' Organises data in the form of a dictionary, used in conjunction with clean()
        '''
        
        result = {}
        
        # Loop through each device
        for filepath, devname in zip(filepaths, names):
            data = self.extractdata(filepath)
            
            # Determining the starting point of each curve, assumes same number of points per curve
            totpts = len(data[:, 0])
            curvepts = int(totpts / ncurves)
            curvestarts = sp.arange(0, totpts, curvepts)
            
            combined_data = []
            
            #loop through curves
            for i, crvname  in zip(curvestarts, curvenames): 
                x = data[i: i + curvepts, 0]
                y = data[i: i + curvepts, 1]

                if y[0] > y[-1]: # flip datasets so they align 
                    y = sp.flip(y)
                    x = sp.flip(x)
                
                combined_data.append(x) 
                combined_data.append(y)
                
            result[devname] = combined_data
                     
        return result


    def clean(self, path, ncurves, curvenames, temp):
        ''' Obtains full dictionary output and the concatenated data
        
        Parameters
        ----------
            path: filepath 
            ncurves: number of curves plotted per device
            curvenames: setting of each curve, used for labelling
            temp: temperature
        Returns
        ----------
            result: dictionary
        '''
        names, filepaths = self.readandsort(path)
    
        result = self.splitdata(filepaths, names, ncurves, curvenames)
        
        print('At %iK, %i devices/trials in total were tested!' %(temp,len(names)))
        
        return result


    def getpaths(self, folder):
        ''' 
        '''
        wnames = set() 
        conditions = set()
        temperatures = []
        
        direcs = []
        for txt in os.listdir(folder):
            if txt != '.DS_Store': # exclude this irrelevant file
                [wn, cond, temp] = txt.split('_')
                wnames.add(wn)
                conditions.add(cond)
                temperatures.append(int(temp.strip('K')))
                direcs.append(txt)
         
        paths = []
        for i in [x for y, x in sorted(zip(temperatures, direcs))]:
            paths.append(folder + i)
            
        return paths, sorted(temperatures), wnames, conditions


    def getcols(self, temp):
        cols = []
        
        for i in self.curvenames:
            for j in self.measured:
                cols.append(str(temp)+ 'K_' + i + '_' + j)
        return cols


    def getmerged(self, paths, temperatures):
        ''' return merged data
        '''
        
        for p, temp in zip(paths,temperatures):
            result = self.clean(p, self.ncurves, self.curvenames, temp)

            if p == paths[0]: #create new DataFrame during first run
                x = pd.DataFrame.from_dict(result, orient='index')
                
#                x.columns = pd.MultiIndex.from_product([[str(temp)+'K'], self.curvenames, self.measured])
                x.columns = self.getcols(temp)
            
            else: # for remaining runs, merge with existing DataFrame
                y = pd.DataFrame.from_dict(result, orient='index')
#                y.columns = pd.MultiIndex.from_product([[str(temp)+'K'], self.curvenames, self.measured]
                
                y.columns = self.getcols(temp)
                if self.keepall: # choice of whether to keep all rows (devices/trials)
                    x = pd.merge(x, y, left_index=True, right_index=True, how='outer')
                else: 
                    x = pd.merge(x, y, left_index=True, right_index=True, how='inner')      
        return x
  
    def savejson(self, x, path):
        '''
        '''
        x.to_json('./cleaned_data/'+ path.strip('./raw_data/')+'.json')
        
    def main(self):
        
        paths, temperatures, wnames, conditions = self.getpaths(self.folder)
        print('For %s in %s' %(str(wnames), str(conditions)))
        print('----------')
        
        merged = self.getmerged(paths, temperatures)
        
        return merged
    
#%%

#cm = cleanandmerge()
#merged = cm.main()
