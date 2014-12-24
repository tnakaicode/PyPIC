#----------------------------------------------------------------------
#                                                                      
#                           CERN                                       
#                                                                      
#     European Organization for Nuclear Research                       
#                                                                      
#     
#     This file is part of the code:
#                                                                      		    
# 
#		           PyPIC Version 0.00                     
#                  
#                                                                       
#     Author and contact:   Giovanni IADAROLA 
#                           BE-ABP Group                               
#                           CERN                                       
#                           CH-1211 GENEVA 23                          
#                           SWITZERLAND  
#                           giovanni.iadarola@cern.ch                  
#                                                                      
#                contact:   Giovanni RUMOLO                            
#                           BE-ABP Group                               
#                           CERN                                      
#                           CH-1211 GENEVA 23                          
#                           SWITZERLAND  
#                           giovanni.rumolo@cern.ch                    
#                                                                      
#
#                                                                      
#     Copyright  CERN,  Geneva  2011  -  Copyright  and  any   other   
#     appropriate  legal  protection  of  this  computer program and   
#     associated documentation reserved  in  all  countries  of  the   
#     world.                                                           
#                                                                      
#     Organizations collaborating with CERN may receive this program   
#     and documentation freely and without charge.                     
#                                                                      
#     CERN undertakes no obligation  for  the  maintenance  of  this   
#     program,  nor responsibility for its correctness,  and accepts   
#     no liability whatsoever resulting from its use.                  
#                                                                      
#     Program  and documentation are provided solely for the use  of   
#     the organization to which they are distributed.                  
#                                                                      
#     This program  may  not  be  copied  or  otherwise  distributed   
#     without  permission. This message must be retained on this and   
#     any other authorized copies.                                     
#                                                                      
#     The material cannot be sold. CERN should be  given  credit  in   
#     all references.                                                  
#----------------------------------------------------------------------

import numpy as np
from PyPIC_Scatter_Gather import PyPIC_Scatter_Gather
from scipy.constants import e, epsilon_0
import scipy as sp

na = lambda x:np.array([x])


qe=e
eps0=epsilon_0

def fast_dst(x):
# Perform a fast DST on a vector. Since Matlab does not have a DST function,
# this just uses the built in FFT function.

	n = len(x);
	tmp = np.zeros((2*n + 2));
	tmp[1:n+1]=x
	tmp=-(sp.fft(tmp).imag)
	y = np.sqrt(2./(n+1.))*tmp[1:n+1];
	return y
	
def dst2(x):
	m, n = x.shape;
	x_bar = np.zeros((m,n)); 
	
	for j in xrange(n):
	    x_bar[:,j] = fast_dst(x[:,j]);
	
	for i in xrange(m):
	    x_bar[i,:] = fast_dst(x_bar[i,:])
	    
	return x_bar



class FFT_PEC_Boundary_SquareGrid(PyPIC_Scatter_Gather):
    #@profile
    def __init__(self, x_aper, y_aper, Dh):
        
		print 'Start PIC init.:'
		print 'FFT, PEC Boundary, Square Grid'


		super(FFT_PEC_Boundary_SquareGrid, self).__init__(x_aper, y_aper, Dh)

		
		
		self.i_min = np.min(np.where(self.xg>-x_aper)[0])
		self.i_max = np.max(np.where(self.xg<x_aper)[0])+1
		self.j_min = np.min(np.where(self.yg>-y_aper)[0])
		self.j_max = np.max(np.where(self.yg<y_aper)[0])+1

		self.rho = np.zeros((self.Nxg,self.Nyg))
		self.phi = np.zeros((self.Nxg,self.Nyg))
		self.efx = np.zeros((self.Nxg,self.Nyg))
		self.efy = np.zeros((self.Nxg,self.Nyg))
		
		
		m, n = self.rho[self.i_min:self.i_max,self.j_min:self.j_max].shape;

		xx = np.arange(1,m+0.5,1);
		yy = np.arange(1,n+0.5,1);
		
		YY, XX = np.meshgrid(yy,xx) 
		self.green = -4./eps0*(np.sin(XX/2*np.pi/(m+1.))**2/self.Dh**2+\
				   np.sin(YY/2.*np.pi/(n+1.))**2/self.Dh**2);

                        

    #@profile    
    def solve(self, rho = None, flag_verbose = False):
		if rho == None:
			rho = self.rho

		rhocut = self.rho[self.i_min:self.i_max,self.j_min:self.j_max]
		
		rho_bar =  dst2(rhocut)       
		phi_bar = rho_bar/self.green    
		self.phi[self.i_min:self.i_max,self.j_min:self.j_max] = dst2(phi_bar).copy()

		self.efy, self.efx = np.gradient(self.phi, self.Dh, self.Dh)
		self.efy = self.efy.T
		self.efx = self.efx.T
        
        



