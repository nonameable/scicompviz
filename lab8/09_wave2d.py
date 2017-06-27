import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import animation

# wave speed 
c = 1.0

# define the discretization grid
xmin =  -5.0  # left/bottom bound
xmax =   5.0  # right/top   bound
dx   = 0.1    # space increment (default 0.1)

nx = int((xmax-xmin)/dx) # number of points on xy grid

# compute timestep such that the scheme is stable
dt = dx/(1.415*c)

# set initial condition
x = np.linspace( xmin, xmax, nx )
X, Y = np.meshgrid( x, x )

u0 = np.exp( -np.sqrt((X-0.25)**2 + (Y+0.7)**2)/0.25 )
u1 = u0.copy()

# step wave equation
def step_wave(t):

    if t == 0:
        print( 'stability:', (c*dt/dx)**2 )

    un = u0.copy()

    # compute second x-derivative using central differences
    L = (
                              u0[1:nx-1,0:nx-2] +
          u0[2:nx,1:nx-1] - 4*u0[1:nx-1,1:nx-1] + u0[0:nx-2,1:nx-1] + 
                              u0[1:nx-1,2:nx]
        )

    # apply second-order central differences in time
    un[1:nx-1,1:nx-1] = 2*u0[1:nx-1,1:nx-1] - u1[1:nx-1,1:nx-1] + (c*dt/dx)**2 * L

    # apply boundary conditions
    un[0,0:nx+1]    = 0
    un[nx-1,0:nx+1] = 0
    un[0:nx+1,0]    = 0
    un[0:nx+1,nx-1] = 0

    # obstacle
    # un[40:-40,50:80] = 0

    u1[:] = u0
    u0[:] = un

    img.set_array(u1)
    return img,

fig = plt.figure()
img = plt.imshow( u0, 
                  vmax=0.1, 
                  vmin=-0.1, 
                  extent=[xmin, xmax, xmin, xmax], 
                  cmap=cm.Spectral )

anim = animation.FuncAnimation( fig, step_wave, 10000, 
                                interval=1, 
                                repeat=False, 
                                blit=True)

plt.title( "2D Wave Equation" )
plt.xlim( xmin, xmax )
plt.ylim( xmin, xmax )
plt.show()