# -*- coding: utf-8 -*-
"""
@author: Rosa
"""
import numpy as np
import scipy.sparse
from scipy.sparse import diags
from scipy.sparse import linalg
import matplotlib.pyplot as plt
import time
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button


def bright(z,t,v1,v2,n,z01,z02,k):
    "solution for a bright soliton whith Vext=0"
    imag= 0.0 + 1j
    arg1=((z-z01)*v1)
    arg2=(t*0.5*(1 - v1**2))
    arg3=(-(z-z02)*v2)
    arg4=(t*0.5*(k - v2**2))
    psi=np.sqrt(n)*(1/np.cosh((z-z01) -v1*t))*np.exp(arg1*imag)*np.exp(arg2*imag)
    psi2=np.sqrt(k*n)*(1/np.cosh(np.sqrt(k)*(z-z02 +v2*t)))*np.exp(arg3*imag)*np.exp(arg4*imag)
    return psi  + psi2
    
def gaussian(x,t,mu,sigma,w):
    return (np.exp(-(x - mu)**2/(2*sigma**2))*np.exp(-0.5j*w*t))/(np.sqrt(2*np.pi*sigma**2))

    
def grey(z,t,v,n,z0):
    "solution for a dark soliton whith Vext=0"
    imag=0.0 +1j
    psi=np.sqrt(n)*(imag*v + np.sqrt(1-v**2)*np.tanh((z-z0)/np.sqrt(2)-v*t)*np.sqrt(1-v**2))
    return psi

def d_bright(z,t,v1,n,z01):
    "analytic firs derivative for a bright soliton"
    imag= 0.0 + 1j
    dpsi= imag*v1*bright(z,t,v1,0,n,z01,0,0) - np.tanh(z-z01-v1*t)*bright(z,t,v1,0,n,z01,0,0)
    return dpsi
    
#normalitzation function
def Normalitzation(array,h):
    """
    Computes the normalitzation constant using the simpson's method for a 1D integral
    the function to integrate is an array, h is the spacing between points 
    and returns a float
    """
    constant=0.0
    for i in range(len(array)):
        if (i == 0 or i==len(array)):
            constant+=array[i]*array[i].conjugate()
        else:
            if (i % 2) == 0:
                constant += 2.0*array[i]*array[i].conjugate()
            else:
                constant += 4.0*array[i]*array[i].conjugate()
    constant=(h/3.)*constant
    return np.sqrt(1/np.real(constant))
    
#simpsion method
def Simpson(array,h):
    """
    Simpson's method for a 1D integral. Takes the function to integrate as
    an array. h is the spacing between points. Returns a float
    """
    suma=0.0
    for i in range(len(array)):
        if (i==0 or i==len(array)):
            suma+=array[i]
        else:
            if (i % 2) == 0:
                suma+= 2.0*array[i]
            else:
                suma+= 4.0*array[i]
    suma=(h/3.)*suma
    return suma

    
#interaction term of the GP equation    
def interact(g,n,funct):
    """
    Interaction term of the GP equation g is g/|g|=1 for grey solitons, +1
    for bright solitons, n is the density of the infinity for grey solitons and
    the central density n_0 for bright solitons. funct is an array with 
    the state of the system at a certain time.
    """
    return g*np.real(funct*funct.conjugate())/n


def potential(x,x0):
    """
    External potential, typically it will depend on the positon.
    """
    pot=10*(np.exp(-(x)**2/(2*0.5**2)))/(np.sqrt(2*np.pi*0.5**2))
    return 0.5*x**2*0
    
    
    
def Energies(x,dx,g,n,V,gint):
    """
    Computes the three contributions of the total energy and returns
    the values in a list.
    """
    T=0 #kinetic
    K=0 #interaction
    U=0 #potential
    E=0 #total
    for i in range(1,(len(x)-1),2): #odd
        T+=2*(np.absolute((x[i+1]-x[i-1])/(2*dx)))**2
        K+=2*g*(np.absolute(x[i]))**4/n
        U+=4*(np.real(V[i])*(np.absolute(x[i]))**2)/(n*gint)
    for i in range(2,(len(x)-1),2): #even
        T+=(np.absolute((x[i+1]-x[i-1])/(2*dx)))**2
        K+=g*(np.absolute(x[i]))**4/n
        U+=2*(np.real(V[i])*(np.absolute(x[i]))**2)/(n*gint)
    T+=0.5*(np.absolute((x[1])/(2*dx)))**2 #first point
    T+=0.5*(np.absolute((-x[-2])/(2*dx)))**2 #last point
    T=dx*T/3
    K+=0.5*g*(np.absolute(x[0]))**4/n
    K+=0.5*g*(np.absolute(x[-1]))**4/n
    K=dx*K/3
    U+=(np.real(V[0])*(np.absolute(x[0]))**2)/(n*gint)
    U+=(np.real(V[-1])*(np.absolute(x[-1]))**2)/(n*gint)
    U=dx*U/3
    E=T+K+U
    return[T,K,U,E]

#define the spacing and time interval
limits=10
dt=0.002 #time interval
dz=np.sqrt(dt/2) #spacing interval so that fullfills r=0.5
Nz=(limits-(-limits))/dz #number of points
z=np.linspace(-limits,limits,Nz) #position vector, from -10 to 10 Nz points

"""
PLOTING VARIABLES
"""
ev_time= 20
interval_frames=0.1 #time interval to show the frames
steps=int(ev_time/dt)
frame=int(ev_time/interval_frames) #number of frames
save=int(steps/frame) #interval between cn steps before saving a frame



"""
PARAMETERS 
"""
v1=0.9 #velocity (goes from 0 to 1)
v2=0.9
n=10 #density, n_inf for grey solitons, n_0 for bright solitons
z01=-4 #initial position 
z02=3.5
k=3 #proportionality

"""
"""

g=-1 #interaction term, -1 for bright solitons, 1 for grey solitons 0 harmonic
w=1#harmonic oscillator    
#sytem at time t
func_0=[]
if g == -1:
    for position in z:
        func_0.append(bright(position,0,v1,v2,n,z01,z02,k))
elif g == 1:
    for position in z:
        func_0.append(grey(position,0,v,n,0.5))
else:
    for position in z:
        func_0.append(gaussian(position,0,z0,1,w))

func_0=np.asanyarray(func_0) #turns to an ndarray (needed for the tridiag solver)
#we store the norm at t=0 as it will be useful for cheking if it is preserved during
#the time evolution.
norm_0=Normalitzation(func_0,dz)
if g==0:
    constant=1/np.sqrt(Simpson(np.real(func_0*func_0.conjugate()),dz))
    func_0=func_0*constant
    norm_0=Simpson(np.real(func_0*func_0.conjugate()),dz)
    print('norm_0', norm_0)

print('Close the plot window initial configuration to start computing')
#system to evolve
plt.ylim(0,6)
plt.title('Initial configuration')
plt.xlabel('$\~z$', fontsize=16)
plt.ylabel('$|\psi(\~z)|^2/n$', fontsize=16)
plt.fill_between(z,np.absolute(func_0)**2/n,  alpha=0.5)
plt.plot(z,np.absolute(func_0)**2/n, label='v1=%.2f,v2=%.2f,k=%.0f' %(v1,v2,k))
plt.plot(z,np.absolute(potential(z,0))/n, label='External potential')
plt.legend(loc=0, ncol=2)
plt.show() #WHEN RUNING THE PROGRAM CLOSE THE PLOT WINDOW TO START COMPUTING!
#IF NOT CLOSED THE PROGRAM WON'T CONTINUE.



#we create a figure window, create a single axis in the figure and then
#create a line object which will be modified in the animation.
#we simply plot an empty line, data will be added later
fig = plt.figure()
ax = plt.axes(autoscale_on=False,xlim=(-limits, limits), ylim=(0, 6))
plt.xlabel('$\~z$', fontsize=16)
plt.ylabel('$|\psi(\~z)|^2/n$', fontsize=16)
line1, = ax.plot(z, np.real(func_0*np.conjugate(func_0))/n, lw=1)
fill=ax.fill_between(z,np.real(func_0*np.conjugate(func_0))/n,y2=0, alpha=0)
line2, =ax.plot([],[], lw=1)
time_template = 'time = %.1f'
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)





r= (1j*dt)/(4*dz**2) #parameter of the method 
print('r', r)
print('evolution time:',ev_time, 'time units')
print('time steps:',steps)
print('number of frames',frame)

infinit_wall=1000000 #limits of the box

V=[]
for position in z:
    V.append(2*r*dz**2*potential(position,0)/(n))
V=np.array(V)
V[0]=infinit_wall
V[-1]=infinit_wall


#saves the external potential as a vector
Vext=[]
for position in z:
    Vext.append(potential(position,0))
Vext[0]=infinit_wall
Vext[-1]=infinit_wall

#energies
E_kin=[]
E_pot=[]
E_int=[]
E_tot=[]
times=[]
analyticT=[]

#to enable interactive plotting
def cn(state):
    global E_kin,E_pot,E_int,E_tot,times,analyticT,t
    #matrixs for the Crank-Nicholson method
    #first [] the numbers to plug in the diagonals, second [] position of the 
    #diagonals (0 is the main one), shape: matrix's shape
    #we compute the main diagonals of the matrices, which in general will depend 
    #on the position z
    mainA=[1+2*r +2*r*dz**2*interact(g,n,state)] #main diagonal of A matrix (time t+ 1)
    mainB=[1-2*r -2*r*dz**2*interact(g,n,state)] #main diagonal of B matrix (time t)
    mainA= np.array(mainA) + V #add the external potential
    mainB= np.array(mainB) - V #add the external potential
    A=diags([-r,mainA,-r],[-1,0,1], shape=(len(state),len(state)))
    A=scipy.sparse.csr_matrix(A) #turs to sparse csr matrix (needed for the tridiag solver)
    B=diags([r,mainB,r],[-1,0,1], shape=(len(state),len(state)))
    #ndarray b product of B and the system's state at time t
    prod=B.dot(state)
    #solver of a tridiagonal problem
    func_1=linalg.spsolve(A,prod)
    return func_1

start_time = time.time()
t=0 #time 
ev_mx=[] #stores all the states of the system at diferent times as a matrix
ev_mx.append(func_0)#save the state of the system at time t=0
count=1
for i in range(steps):
    system=cn(func_0)
    if count%save==0:
        ev_mx.append(system)
        #energy
        ene_system=Energies(system,dz,g,n,Vext,1) #avalues the energy
        E_kin.append(ene_system[0])
        E_int.append(ene_system[1])
        E_pot.append(ene_system[2])
        E_tot.append(ene_system[3])
        times.append(t)
    t+=dt
    count+=1
    func_0=system


print('comptuting time',time.time()-start_time,'s')

counter=0
def previous_computing(i):
    global fill, counter
    line1.set_data(z,np.absolute(ev_mx[counter])**2/n)
    line2.set_data(z,np.absolute(potential(z,0))/n)
    fill.remove()
    fill = ax.fill_between(z,np.absolute(ev_mx[counter])**2/n,y2=0, alpha=0.5)
    time_text.set_text(time_template % (i*dt*save))
    counter+=1
    if counter == frame: #end of the matrix
        counter=0 #enables a bucle
    return line1, line2, time_text

def init():
    line1.set_ydata(np.ma.array(z, mask=True))
    line2.set_data([],[])
    time_text.set_text('')
    #its important to return the line object, this tells the aimator which objects on the plot
    #to update after each frame
    return line1, line2, time_text

print(abs(E_tot[0]-max(E_tot)))
a=FuncAnimation(fig, previous_computing, init_func=init, frames=frame ,interval=30, repeat=True)
plt.show()
print(time.time()-start_time)



"""
MASS
"""

mass_p=[]
mass_n=[]
for i in range(len(times)):
    positive=[]
    negative=[]
    for j in range(int(len(z)/2)):
        positive.append(np.absolute((ev_mx[i][-j]))**2/n)
        negative.append(np.absolute((ev_mx[i][j]))**2/n)
    mass_p.append(Simpson(positive,dz))
    mass_n.append(Simpson(negative,dz))
    
plt.xlabel('$\~t$',fontsize=16)
plt.ylabel('mass', fontsize=16)
plt.plot(times,mass_p, label='positive')
plt.plot(times,mass_n, label='negative')
plt.legend(loc=9,bbox_to_anchor=(0.5, 1.12), ncol=2)
plt.grid(which='both')
plt.show(block=True)

"""
Energy
"""

plt.xlabel('$\~t$',fontsize=16)
plt.ylabel('$\~E$',fontsize=16)
plt.plot(times, E_kin, label='E_kin')
plt.plot(times, E_int, label='E_int')
plt.plot(times, E_pot, label='E_pot')
plt.plot(times, E_tot, label='E_tot')
#plt.plot(times,analyticT, label='Analytic')
plt.legend(loc=9,bbox_to_anchor=(0.5, 1.12), ncol=4)
plt.grid(which='both')
plt.show(block=True)


