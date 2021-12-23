import time
from datetime import datetime, timedelta

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import util_getAA as aa
from IPython import display
import ipywidgets as widget
import numpy as np
import pickle

from gtT1 import Ui_MainWindow

''' Matplot Global configuration '''
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['figure.figsize'] = (8, 4)
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['agg.path.chunksize'] = 10000
plt.rcParams['xtick.labelsize'] = 'small'
plt.rcParams['ytick.labelsize'] = 'small'
plt.rcParams['lines.linewidth'] = 0.5
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['savefig.dpi'] = 200
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['figure.max_open_warning'] = False


class Mainwindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def plotTimeData(data1,data2, data3, data4, ylim1=None, ylim2=None, ylim3=None, ylim4=None, exportImg=False):
        fig = plt.figure()
        ax1 = plt.subplot(2,1,1)    

        line1 = plt.plot(data1['ts'], data1['val'], linewidth=1.5, label=data1['name'])
        ax1.set_ylabel("HX QBPM", color='C0')
        ax1.grid()
        
        ax1.set_title(data3['name'][0:11])

        ax2 = ax1.twinx()
        line2 = plt.plot(data2['ts'], data2['val'], 'r', label=data2['name'])
        ax2.set_ylabel("Laser Shutter", color='r')


        ax3 = plt.subplot(2,1,2, sharex=ax1)
        line3 = plt.plot(data3['ts'], data3['val'], 'g', label=data3['name'] ,linewidth=1.2)
        
        ax4 = ax3.twinx()
        line4 = plt.plot(data4['ts'], data4['val'], 'm', label=data4['name'], linewidth=1.2)

        ax3.grid()
        ax3.set_ylabel("KBV Graph", color='g')
        ax4.set_ylabel("KBC Graph", color='m')
        
        split = data3['name'].split(':')
        
        strTitle = split[0] + ':' + split[1]
        
        ax1.set_title(strTitle)

        if ylim1 is not None:
            ax1.set_ylim(ylim1)
            
        if ylim2 is not None:
            ax2.set_ylim(ylim2)
            
        if ylim3 is not None:
            ax3.set_ylim(ylim3)
            
        if ylim4 is not None and np.min(data4['val'])< ylim4[1]:
            ax4.set_ylim(ylim4)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%Y-%m-%d'))
        if exportImg:
            filename = data3['name'].replace(':', '_') + '.png'
            fig.savefig(filename, bbox_inches='tight')


    pvList = ('BL:HX:OH:QBPM1:analog_in_totsum',
            'INJ:LASER:SHUTTER3:GPIO7',
            
            'INJ:LLRFGUN:KBC1_RMS_PERC_R',
            'INJ:LLRFGUN:KBV1_RMS_PERC_R',
            'INJ:LLRF01:KBC1_RMS_PERC_R',
            'INJ:LLRF01:KBV1_RMS_PERC_R',
            'INJ:LLRF02:KBC1_RMS_PERC_R',
            'INJ:LLRF02:KBV1_RMS_PERC_R',
            'HL1:LLRFXLI:KBC1_RMS_PERC_R',
            'HL1:LLRFXLI:KBV1_RMS_PERC_R',
            'HL1:LLRF01:KBC1_RMS_PERC_R',
            'HL1:LLRF01:KBV1_RMS_PERC_R',
            'HL1:LLRF02:KBC1_RMS_PERC_R',
            'HL1:LLRF02:KBV1_RMS_PERC_R',
            'HL2:LLRF01:KBC1_RMS_PERC_R',
            'HL2:LLRF01:KBV1_RMS_PERC_R',
            'HL2:LLRF02:KBC1_RMS_PERC_R',
            'HL2:LLRF02:KBV1_RMS_PERC_R',
            'HL2:LLRF03:KBC1_RMS_PERC_R',
            'HL2:LLRF03:KBV1_RMS_PERC_R',
            'HL2:LLRF04:KBC1_RMS_PERC_R',
            'HL2:LLRF04:KBV1_RMS_PERC_R',
            'HL2:LLRF05:KBC1_RMS_PERC_R',
            'HL2:LLRF05:KBV1_RMS_PERC_R',
            'HL2:LLRF06:KBC1_RMS_PERC_R',
            'HL2:LLRF06:KBV1_RMS_PERC_R',
            'HL2:LLRF07:KBC1_RMS_PERC_R',
            'HL2:LLRF07:KBV1_RMS_PERC_R',
            'HL2:LLRF08:KBC1_RMS_PERC_R',
            'HL2:LLRF08:KBV1_RMS_PERC_R',
            'HL2:LLRF09:KBC1_RMS_PERC_R',
            'HL2:LLRF09:KBV1_RMS_PERC_R',
            'HL2:LLRF10:KBC1_RMS_PERC_R',
            'HL2:LLRF10:KBV1_RMS_PERC_R',
            'HL3A:LLRF01:KBC1_RMS_PERC_R',
            'HL3A:LLRF01:KBV1_RMS_PERC_R',
            'HL3A:LLRF02:KBC1_RMS_PERC_R',
            'HL3A:LLRF02:KBV1_RMS_PERC_R',
            'HL3B:LLRF01:KBC1_RMS_PERC_R',
            'HL3B:LLRF01:KBV1_RMS_PERC_R',
            'HL3B:LLRF02:KBC1_RMS_PERC_R',
            'HL3B:LLRF02:KBV1_RMS_PERC_R',
            'HL4:LLRF01:KBC1_RMS_PERC_R',
            'HL4:LLRF01:KBV1_RMS_PERC_R',
            'HL4:LLRF02:KBC1_RMS_PERC_R',
            'HL4:LLRF02:KBV1_RMS_PERC_R',
            'HL4:LLRF03:KBC1_RMS_PERC_R',
            'HL4:LLRF03:KBV1_RMS_PERC_R',
            'HL4:LLRF04:KBC1_RMS_PERC_R',
            'HL4:LLRF04:KBV1_RMS_PERC_R',
            'HL4:LLRF05:KBC1_RMS_PERC_R',
            'HL4:LLRF05:KBV1_RMS_PERC_R',
            'HL4:LLRF06:KBC1_RMS_PERC_R',
            'HL4:LLRF06:KBV1_RMS_PERC_R',
            'HL4:LLRF07:KBC1_RMS_PERC_R',
            'HL4:LLRF07:KBV1_RMS_PERC_R',
            'HL4:LLRF08:KBC1_RMS_PERC_R',
            'HL4:LLRF08:KBV1_RMS_PERC_R',
            'HL4:LLRF09:KBC1_RMS_PERC_R',
            'HL4:LLRF09:KBV1_RMS_PERC_R',
            'HL4:LLRF10:KBC1_RMS_PERC_R',
            'HL4:LLRF10:KBV1_RMS_PERC_R',
            'HL4:LLRF11:KBC1_RMS_PERC_R',
            'HL4:LLRF11:KBV1_RMS_PERC_R',
            'HL4:LLRF12:KBC1_RMS_PERC_R',
            'HL4:LLRF12:KBV1_RMS_PERC_R',
            'HL4:LLRF13:KBC1_RMS_PERC_R',
            'HL4:LLRF13:KBV1_RMS_PERC_R',
            'HL4:LLRF14:KBC1_RMS_PERC_R',
            'HL4:LLRF14:KBV1_RMS_PERC_R',
            'HL4:LLRF15:KBC1_RMS_PERC_R',
            'HL4:LLRF15:KBV1_RMS_PERC_R',
            'HL4:LLRF16:KBC1_RMS_PERC_R',
            'HL4:LLRF16:KBV1_RMS_PERC_R',
            'HL4:LLRF17:KBC1_RMS_PERC_R',
            'HL4:LLRF17:KBV1_RMS_PERC_R',
            'HL4:LLRF18:KBC1_RMS_PERC_R',
            'HL4:LLRF18:KBV1_RMS_PERC_R',
            'HL4:LLRF19:KBC1_RMS_PERC_R',
            'HL4:LLRF19:KBV1_RMS_PERC_R',
            'HL4:LLRF20:KBC1_RMS_PERC_R',
            'HL4:LLRF20:KBV1_RMS_PERC_R',
            'HL4:LLRF21:KBC1_RMS_PERC_R',
            'HL4:LLRF21:KBV1_RMS_PERC_R',
            'HL4:LLRF22:KBC1_RMS_PERC_R',
            'HL4:LLRF22:KBV1_RMS_PERC_R',
            'HL4:LLRF23:KBC1_RMS_PERC_R',
            'HL4:LLRF23:KBV1_RMS_PERC_R',
            'HL4:LLRF24:KBC1_RMS_PERC_R',
            'HL4:LLRF24:KBV1_RMS_PERC_R',
            'HL4:LLRF25:KBC1_RMS_PERC_R',
            'HL4:LLRF25:KBV1_RMS_PERC_R',
            'HL4:LLRF26:KBC1_RMS_PERC_R',
            'HL4:LLRF26:KBV1_RMS_PERC_R',
            'HL4:LLRF27:KBC1_RMS_PERC_R',
            'HL4:LLRF27:KBV1_RMS_PERC_R',
            )

    dataperiod = 10
    process = 'mean'
    strStart = '2021-12-12T10:50:00'
    strEnd   = '2021-12-12T11:30:00'

    tStart = datetime.strptime(strStart, "%Y-%m-%dT%H:%M:%S")
    tEnd   = datetime.strptime(strEnd,   "%Y-%m-%dT%H:%M:%S")

    data = {}

    for i, pvname in enumerate(pvList):
        if 'RMS' in pvname or 'rms' in pvname:
            processname = 'max'
        else:
            processname = process
        
        data[pvname] = aa.getAAdata(pvname, process=processname, secs=dataperiod, timelimit=[tStart,tEnd])


    for idx in range(len(pvList)):
        if idx > 0 and idx%2 ==0:
            if np.max(data[pvList[idx]]['val']) > 0.02:
                plotTimeData(data[pvList[0]], data[pvList[1]], data[pvList[idx]],data[pvList[idx+1]],exportImg=False)
    plt.show()
    # start_x, start_y, dx, dy = (0, 0, 640, 550)

    # for i in range(5):
    #     if i%3 == 0:
    #         x = start_x
    #         y = start_y + (dy * (i//3))
    #     plt.figure()
    #     mngr = plt.get_current_fig_manager()
    #     mngr.window.setGeometry(x, y, dx, dy)
    #     x += dx
