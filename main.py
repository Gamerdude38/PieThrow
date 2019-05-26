'''
John Maurer

Description: A driver class for Pie Throw, a class that demonstrates
knowledge of the Panda3D engine, focusing on the use of Tasks, Event
Handlers, Audio, Collisions, and basic health-bar game logic
'''

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from random_cog import RandomCog
import sys,os

class PieThrow(ShowBase):
	def __init__(self):
		#Initialize the Panda window & disable the default mouse controls
		ShowBase.__init__(self)
		#self.disableMouse()
		self.oobe()
		
		#Establish where the current directory of the running file is
		self.currentDirectory = os.path.abspath(sys.path[0])
		self.pandaDirectory = Filename.fromOsSpecific(self.currentDirectory).getFullpath()
		
		#Load the main terrain to be used
		self.terrain = self.loader.loadModel(self.pandaDirectory + '/resources/terrain/LawbotPlaza.bam')
		self.terrain.reparentTo(self.render)
		
		self.cog = RandomCog()
		
pieThrow = PieThrow()
pieThrow.run()
