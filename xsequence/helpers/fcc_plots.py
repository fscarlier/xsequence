import os, sys

import matplotlib
matplotlib.use('qt5agg')
import matplotlib.pyplot as plt


LABELS = {
          'dbet'  :r'$\Delta\beta/\beta$', 
          'dbet_p':r'$\Delta\beta/\beta$ [%]', 
          'dbetx'  :r'$\Delta\beta_x/\beta_x$', 
          'dbetx_p':r'$\Delta\beta_x/\beta_x$ [%]', 
          'dbety'  :r'$\Delta\beta_y/\beta_y$', 
          'dbety_p':r'$\Delta\beta_y/\beta_y$ [%]', 
          'betx' :r'$\beta_x$ [m]', 
          'bety' :r'$\beta_y$ [m]', 
          'dispx' :r'$\eta_x$ [m]', 
          'dispy' :r'$\eta_y$ [m]', 
          'ddispx' :r'$\Delta\eta_x$ [m]', 
          'ddispy' :r'$\Delta\eta_y$ [m]', 
          'alfx' :r'$\alpha_x$ ', 
          'alfy' :r'$\alpha_y$ ', 
          'x' :r'$x$ [m]', 
          'y' :r'$y$ [m]', 
          'dx' :r'$\Delta x$ [m]', 
          'dy' :r'$\Delta y$ [m]', 
         }


def fcc_axes(y_label=None):
    matplotlib.style.use('ggplot')
    matplotlib.rc('axes',edgecolor='black')
    matplotlib.rc('axes',facecolor='white')
    
    fig = plt.figure(figsize=(7,4))
    fig.patch.set_facecolor('white')
    ax = plt.axes([0.17, 0.15, 0.8, 0.75])
    ax.set_xlabel('s [m]', fontsize=14)
    ax.set_ylabel(y_label, fontsize=14)
    lhc_length = 97756.02181750233 
    ax.set_xlim([0, lhc_length])
    ips_pos = [0, 48878.01090875525]
    ips_labels = ['IP1', 'IP2']
    
    ax.tick_params(labelsize=14) 
    tx = ax.twiny()
    tx.set_xlim(ax.get_xlim())
    tx.grid(False)
    tx.set_xticks(ips_pos)
    tx.set_xticklabels(ips_labels, fontsize=14)
    return fig, ax

    
