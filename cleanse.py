#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 11:41:47 2020

@author: kenton
"""

#import useful packages
import pandas as pd
import scipy as sp
import glob
import os

#define class
class cleanse: 
    """ Used for cleaning, merging and exporting data
    """
    
    def __init__(self):
        ncurves = 4     
        curvenames = ['10mV-on', '10mV-off', '30mV-on','30mV-off']
        measured = ['Vgs', 'Ids']
        folder = './raw_data/'
        
        self.folder = folder
        self.ncurves = ncurves
        self.curvenames = curvenames
        self.measured = measured
        self.colscombo = self.getcols()
        self.dirs, self.temperatures = self.getpaths(self.folder)
        self.devs = set()
        self.trials = set()
        pass
    
    ### column name extraction suite
    def getcols(self):
        ''' function to generate dataframe column names, meant to be used once
        '''
        cols = []
        for i in self.curvenames:
            for j in self.measured:
                cols.append(i + '_' + j)
        return cols
    
    
    def extractdt(self, filepath):
        ''' returns the device names and trial number given a valid filepath
        
        Example
        -------
        Filename: Transfer [0312a25(2) ; 7_16_2020 4_14_24 PM].csv
        
        This selects all .csv files in filepaths
        and creates nested dictionaries in the form {'0312a25':{'2':DataFrame, ...}, ...}
        '''
        dt = ''
        read =  False
        
        for char in filepath: 
            if char == ')':#end reading
                read = False   
            if read:
                dt += char  
            if char == '[': #begin reading and storing device name
                read = True  
        dev, trial = dt.split('(')
            
        return dev, trial
    
    
    def extractcols(self):
        '''
        '''
        columns = []
        for t, direc in zip(self.temperatures, self.dirs):
            for fp in sorted(glob.glob(direc + '/*.csv')):
                dev, trial = self.extractdt(fp)
                self.devs.add(dev)
                self.trials.add('('+ str(trial)+')')
                for n in self.colscombo: 
                    columns.append('{0}K_{1}_({2})_{3}'.format(t, dev, trial, n))
        return columns
        
#    def recurCol(self, liste):
#        result = []
#        
#        def alltolist(liste):
#            result = []
#            for i in liste:
#                if type(i) == list:
#                    result.append(i)
#                else: 
#                    result.append([i])
#            return result
#        
#        def layer(liste):
#            if len(liste) == 1:
#                return liste[0]
#            
#            elif len(liste) == 2:
#                for i in liste[0]:
#                    for j in liste[1]:
#                        return i + '_' + j
#                    
#            elif len(liste) > 2:
#                for i in liste[0]:
#                    result.append(i+ '_'+ layer(liste[1:]))
#        
#        return layer(alltolist(liste))
    
    
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
        
        return paths, sorted(temperatures)
    
    
    ### Device data extraction suite ############################
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
            f.close()
        return data


    def splitdata(self, exp_filepath): 
        ''' Organises each experiment's data in the form of a DataFrame
        ------
        Args: 
            filepath: path for experiment CSV file
        Returns:
            list of 
        '''
        # extract array of data, which is flattened
        data = self.extractdata(exp_filepath)
        
        ### This creates a reshaped array of data
        # Determining the starting point of each curve, assumes same number of points per curve
        totpts = len(data[:, 0])
        curvepts = int(totpts / self.ncurves)
        curvestarts = sp.arange(0, totpts, curvepts)
        
        result = []
        #loop through curves, 
        for i, crvname in zip(curvestarts, self.curvenames): 
            x = data[i: i + curvepts, 0]
            y = data[i: i + curvepts, 1]

            if y[0] > y[-1]: # flip datasets so they align 
                y = sp.flip(y)
                x = sp.flip(x)
            result += [x,y]
        return result
    
    
    ### iteration suite
    def iterDevs(self, direc): 
        ''' 
        '''
        filepaths = sorted(glob.glob(direc + '/*.csv'))
        
        result = []
        for fp in filepaths: #loop over list of filepaths
            result += self.splitdata(fp)
        return result
    
    
    def iterTemps(self):
        '''
        '''
        result = []
        for direc in self.dirs:
            result += self.iterDevs(direc)
        return result
    
    
    def getdf(self):
        array = sp.array(self.iterTemps()).T
        cols = self.extractcols() #todo: move to __init__
        
        df = pd.DataFrame(array, columns=cols)
        return df


#%%
        
#c = cleanse()
#df = c.getdf()
#c.getpaths(c.folder)



            