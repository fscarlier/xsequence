#!/usr/bin/env python
# coding: utf-8

# In[11]:


from xsequence.lattice import Lattice
from xsequence.conversion_utils import conv_utils

lat = Lattice.from_madx_seqfile("FCCee_h.seq", 'l000013', energy=120)
plat = lat.to_pyat()


# Accelerator toolbox import and specific matplotlib environment settings for Jupyter notebook.

# In[12]:


import at
get_ipython().run_line_magic('matplotlib', 'qt')
import matplotlib.pyplot as plt
plt.ion()


# Creating pyAT optics plot

# In[13]:


plat.radiation_off()
l0,q,qp,l = at.linopt(plat,refpts=range(len(plat)))
ax1,=plt.plot(l.s_pos,l.beta[:,0], label='x')
ax2,=plt.plot(l.s_pos,l.beta[:,1], label='y')
plt.xlabel('s [m]')
plt.ylabel('beta [m]')
plt.legend()
plt.draw()


# Defining update function for optics plot

# In[14]:


def update_twiss(plat,elements):
    plat.radiation_off()
    l0,q,qp,l = at.linopt(plat,refpts=range(len(plat)))
    ax1.set_ydata(l.beta[:,0])
    ax2.set_ydata(l.beta[:,1])


# Setting up dependency manager

# In[15]:


import xdeps

plat.e=dict( (el.FamName,el) for el in plat)
plat.v = xdeps.utils.AttrDict()

manager = xdeps.Manager()
pref=manager.ref(plat,'plat')

pref.update_twiss=update_twiss
pref.up=pref.update_twiss(pref,pref.e)


# Creating knob 'dk' to modulate k1 of 'qc1l1.1' element

# In[16]:


pref.v.dk=0
pref.e['qc1l1.1'].K=-0.24949831119187935*(1+pref.v.dk)


# Changing values of the knob will automaticall change the plot of beta functions.

# In[17]:


pref.v.dk = 0.0001


# In[18]:


pref.v.dk = 0.0003


# In[19]:


pref.v.dk = 0.0005

