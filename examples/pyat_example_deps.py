#!/usr/bin/env python
# coding: utf-8

# In[1]:


from xsequence.lattice import Lattice
from xsequence.conversion_utils import conv_utils

lat = Lattice.from_madx_seqfile("FCCee_h.seq", 'l000013', energy=120)
plat = lat.to_pyat()


# Accelerator toolbox import and specific matplotlib environment settings for Jupyter notebook.

# In[2]:


import at
get_ipython().run_line_magic('matplotlib', 'qt')
import matplotlib.pyplot as plt
plt.ion()


# Creating pyAT optics plot

# In[3]:


plat.radiation_off()
l0,q,qp,l = at.linopt(plat,refpts=range(len(plat)))
ax1,=plt.plot(l.s_pos,l.beta[:,0], label='x')
ax2,=plt.plot(l.s_pos,l.beta[:,1], label='y')
plt.xlabel('s [m]')
plt.ylabel('beta [m]')
plt.legend()
plt.draw()


# Defining update function for optics plot

# In[4]:


def update_twiss(plat,elements):
    plat.radiation_off()
    l0,q,qp,l = at.linopt(plat,refpts=range(len(plat)))
    ax1.set_ydata(l.beta[:,0])
    ax2.set_ydata(l.beta[:,1])


# Setting up dependency manager

# In[5]:


import xdeps

plat.e=dict( (el.FamName,el) for el in plat)
plat.v = xdeps.utils.AttrDict()

manager = xdeps.Manager()
pref=manager.ref(plat,'plat')

pref.update_twiss=update_twiss
pref.up=pref.update_twiss(pref,pref.e)


# Creating knob 'dk' to modulate k1 of 'qc1l1.1' element

# In[6]:


pref.v.dk=0
pref.e['qc1l1.1'].K=-0.24949831119187935*(1+pref.v.dk)


# Changing values of the knob will automaticall change the plot of beta functions.

# In[10]:


pref.v.dk = 0.0001


# In[11]:


pref.v.dk = 0.0003


# In[12]:


pref.v.dk = 0.0005

