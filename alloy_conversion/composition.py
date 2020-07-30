import numpy as np

class alloy:
    
    def __init__(self, metals, mu = 1):
        ''' 
        n: number of metals to add in alloy
        
        atpc: list of x where x% represents atomic percentage in alloy
        
        mmass: molar mass in g/mol of each metal
        
        mu = total make-up mass in g
        '''
        self.n = len(metals)
        self.atpc = np.array(list(metals.values())) / 100 #converts into decimals
        self.mu = mu
        self.metals = metals
        self.MGa = 69.723 
        self.MIn = 114.818
        self.MSn = 118.71
        self.MAl = 26.981538
        self.MZn = 65.4
        self.MHg = 200.59
        self.MAg = 107.868
        self.MBi = 208.9804
        
    def get_mmass(self):
        ''' converts element key into mass
        '''
        mmass = []
        for key in self.metals: 
            exec("mmass.append(self.M%s)" %key)
            
        self.mmass = np.reshape(mmass, (-1,1))
        
        return mmass
    
        
    def comp(self):
        ''' converts atomic percentage into mass make-up
        solved as a system of linear equations
        '''
        mmass = self.get_mmass()
        
        # A is the matrix of coefficients
        A = np.zeros((self.n, self.n))
        A[:,:] = self.atpc.reshape((-1,1)) / mmass
        A[:,0] = (self.atpc - np.ones(self.n)) / mmass
        A[-1, :] = np.ones(self.n) 
        
        # b is the ordinate vector
        b = np.zeros(self.n)
        b[-1] = self.mu

        x = np.linalg.solve(A,b)
        x = [format(i, '.5f') for i in x]
        print('---')
        print('To make up this alloy {0}'.format(self.metals))
        print('We need in grams, \n', dict(zip(metals,x)))
        print('')
        
        return x
    
        
#%%
gaList = [100, 85.8, 70, 50]
for i in gaList: 
    mu = 1
    metals = {'Ga': i, 'In':100-i}
    a = alloy(metals, mu)
    a.comp()
