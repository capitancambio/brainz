"""
This demo demonstrates how to draw a dynamic mpl (matplotlib) 
plot in a wxPython application.

It allows "live" plotting as well as manual zooming to specific
regions.

Both X and Y axes allow "auto" or "manual" settings. For Y, auto
mode sets the scaling of the graph to see all the data points.
For X, auto mode makes the graph "follow" the data. Set it X min
to manual 0 to always see the whole data from the beginning.

Note: press Enter in the 'manual' text box to make a new value 
affect the plot.

Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 31.07.2008
"""
import datetime
import logging
import threading
# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
import wxversion
wxversion.select('2.8')
import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas
import numpy as np
import pylab

        

class GraphFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'EEGdumper viewer' 
    def __init__(self,buff):
        wx.Frame.__init__(self, None, -1, self.title)
	self.buffProvider=buff
	self.buff=self.buffProvider.getBuff()
	self.chans=self.buff.shape[1]
       	self.logger=logging.getLogger("logger") 
	self.logger.debug("channels %i"%self.chans)
	self.axes=[]
	self.plot_data=[]
	self.bg=[]
        self.create_main_panel()
        
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
        self.redraw_timer.Start(1000)
	self.paused=False
	#self.sem=threading.Semaphore()
	self.sem=False
    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW,border=0)        

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi =20
        self.fig = Figure((45,35),dpi=self.dpi,edgecolor='white')
	for i in range(self.chans):
		self.axes.append(self.fig.add_subplot(self.chans,1,i+1))
		self.axes[i].set_axis_bgcolor('white')
		self.axes[i].set_xbound(lower=0, upper=self.buff.shape[0])
		self.axes[i].set_ybound(lower=-10, upper=10)
		self.axes[i].set_ylim(bottom=-10,top=10)
		pylab.setp(self.axes[i].get_xticklabels(), 
		    visible=False)
		pylab.setp(self.axes[i].get_yticklabels(), 
		    visible=False)
	self.fig.subplots_adjust(hspace=0)

        self.canvas = FigCanvas(self.panel, -1, self.fig)
	for i in range(self.chans):
		self.bg.append(self.canvas.copy_from_bbox(self.axes[i].bbox))
		self.plot_data.append( self.axes[i].plot(
		    self.buff[:,i].transpose(),
		    linewidth=2,
		    color=(1, 0, 0),
		    )[0])

    def draw_plot(self):
        """ Redraws the plot
        """
	if not self.sem:
		self.sem=True
		st=datetime.datetime.now()
		for i in range(self.chans):
			self.canvas.restore_region(self.bg[i])
			ymin=min([min(self.buff[:,i])])
			ymax=max([max(self.buff[:,i])])
			self.axes[i].set_ybound(lower=ymin, upper=ymax)
			#self.plot_data[i].set_xdata(np.arange(self.buff[:,i].shape[0]))
			
			self.plot_data[i].set_ydata(np.array(self.buff[:,i]))
			#self.axes[i].draw_artist(self.plot_data[i])	
			#self.canvas.blit(self.axes[i].bbox)
		
		t=datetime.datetime.now()-st
		#self.logger.debug( "TIME %f"%(t.seconds+t.microseconds/1000000.))
		st=datetime.datetime.now()
		self.canvas.draw()
		t=datetime.datetime.now()-st
		self.logger.debug("TIME2 %f"%(t.seconds+t.microseconds/1000000.))
		self.sem=False
	else:
		self.logger.debug("Not blocked!")
	

	#self.logger.debug("TIME2 %f"%(t.seconds+t.microseconds/1000000.))
	#wx.WakeUpIdle()
    
    def on_pause_button(self, event):
        self.paused = not self.paused
    
    def on_redraw_timer(self, event,other=None):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
       	self.buff=self.buffProvider.getBuff() 
	self.buff[self.buff==0]=None
   	self.draw_plot() 
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

class DataPlotter(threading.Thread):
	"""docstring for DataPlotter"""
	def __init__(self,buff):
		super(DataPlotter, self).__init__()
		self.buff=buff
		self.logger=logging.getLogger("logger")

	def run(self):
	    self.logger.debug("in plotter run") 
	    app = wx.PySimpleApp()
	    app.frame = GraphFrame(self.buff)
	    app.frame.Show()
	    app.MainLoop()
