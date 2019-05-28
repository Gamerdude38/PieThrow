'''
John Maurer

Description: A driver class for Pie Throw, a class that demonstrates
knowledge of the Panda3D engine, focusing on the use of Tasks, Event
Handlers, Audio, Collisions, and basic health-bar game logic
'''

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task
from random_cog import RandomCog
import sys,os

class PieThrow(ShowBase):
	def __init__(self):
		#Initialize the Panda window & disable the default mouse controls
		ShowBase.__init__(self)
		self.disableMouse()
		#self.oobe()
		
		#Establish where the current directory of the running file is
		self.currentDirectory = os.path.abspath(sys.path[0])
		self.pandaDirectory = Filename.fromOsSpecific(self.currentDirectory).getFullpath()
		
		#Define variables, particularly to tell if the model is moving
		self.isThrowing = False
		self.isMovingInY = False
		self.isTurning = False
		self.movementHeading = ''
		self.turnHeading = ''
		self.speed = 0.0
		self.turnSpeed = 0.0
		
		#Load the main terrain to be used
		self.terrain = self.loader.loadModel(self.pandaDirectory + '/resources/terrain/LawbotPlaza.bam')
		self.terrain.reparentTo(self.render)
		
		#Initialize the toon model
		self.toon = self.initToon()
		self.toon.setZ(-68)
		
		#Reparent the camera
		self.camera.reparentTo(self.toon)
		self.camera.setPos(self.toon, 0, -20, 5)
		
		#Initialize animations
		self.toon.loop('neutral', 'torso')
		self.toon.loop('neutral', 'legs')
		
		#Define Y (Forwards/backwards) movement
		self.accept('arrow_up', self.moveInYStart, ['forward'])
		#self.accept('arrow_up-repeat', self.moveInY, ['forward'])
		self.accept('arrow_up-up', self.moveInYEnd, ['forward'])
		self.accept('arrow_down', self.moveInYStart, ['backward'])
		#self.accept('arrow_down-repeat', self.moveInY, ['backward'])
		self.accept('arrow_down-up', self.moveInYEnd, ['backward'])
		
		#Define turning movement
		self.accept('arrow_right', self.turnStart, ['right'])
		#self.accept('arrow_right-repeat', self.turn, ['right'])
		self.accept('arrow_right-up', self.turnEnd, ['right'])
		self.accept('arrow_left', self.turnStart, ['left'])
		#self.accept('arrow_left-repeat', self.turn, ['left'])
		self.accept('arrow_left-up', self.turnEnd, ['left'])
		
		#Pie throwing key, 'control' is the keyName
		
		#Tell the taskmanager to keep track of this task
		self.taskMgr.add(self.updateToon, 'Update Toon')
		
	def updateToon(self, task):
		if self.isMovingInY:
			self.toon.setY(self.toon, self.speed)
			
		if self.isTurning:
			self.toon.setH(self.toon, self.turnSpeed)	
		return task.cont
	
	def turnStart(self, direction):
		#If the toon is already turning, ignore the new request
		if self.isTurning:
			return
		
		#Set the object heading to prevent pressing the right and left keys at the same time
		self.turnHeading = direction
		
		#If the toon is moving in the Y direction...
		if self.isMovingInY:
			#And the toon is moving backwards...
			if self.speed < 0:
				#Replace the run animation with walk and play it backwards
				self.toon.setPlayRate(-1, 'walk')
				
		#If the toon is not moving
		else:
			#Play the forward plain walking animations
			self.toon.setPlayRate(1, 'walk')
			self.toon.loop('walk', 'torso')
			self.toon.loop('walk', 'legs')
		
		#Determine which heading the toon will turn
		if direction == 'right':
			self.turnSpeed = -0.7
		elif direction == 'left':
			self.turnSpeed = 0.7
		
		#Tell task manager to start turning
		self.isTurning = True
		
	def turn(self, direction):
		print()
		
	def turnEnd(self, direction):
		#If the requested direction conflicts with the heading, ignore the request
		if direction != self.turnHeading:
			return
			
		#If the toon is not moving in the Y direction...
		if not self.isMovingInY:
			#Make the animation play neutral before stopping to turn
			self.toon.loop('neutral', 'torso')
			self.toon.loop('neutral', 'legs')
		
		#Tell task manager to stop turning
		self.isTurning = False
		
	def moveInYStart(self, direction):
		#If the toon is already moving, ignore the new request
		if self.isMovingInY:
			return
		
		#Set the object heading to prevent pressing the up and down keys at the same time
		self.movementHeading = direction
		
		#If the up key is pressed...
		if direction == 'forward':
			#Set a positive speed and make the toon run
			self.speed = 0.6
			self.toon.loop('run', 'torso')
			self.toon.loop('run', 'legs')
		
		#Otherwise...
		elif direction == 'backward':
			#Set a negative speed and make the toon walk backwards
			self.speed = -0.3
			self.toon.setPlayRate(-1, 'walk')
			self.toon.loop('walk', 'torso')
			self.toon.loop('walk', 'legs')
		
		#Tell the task manager to start moving in local Y
		self.isMovingInY = True
		
	def moveInY(self, direction):
		print()
			
	def moveInYEnd(self, direction):
		#If the requested direction conflicts with the heading, ignore the request
		if direction != self.movementHeading:
			return
		
		#If the toon is not turning...
		if not self.isTurning:
			#Set the speed to positive and have the toon idle
			self.speed = 0.6
			self.toon.loop('neutral', 'torso')
			self.toon.loop('neutral', 'legs')
			
		#Otherwise...
		else:
			#Make the toon walk instead
			self.toon.setPlayRate(1, 'walk')
			self.speed = 0.6
			self.toon.loop('walk', 'torso')
			self.toon.loop('walk', 'legs')
		
		#Tell the task manager to stop moving in local Y
		self.isMovingInY = False
		
	def initToon(self):
		#Create the toon!
		self.toon = Actor({'torso': self.pandaDirectory + '/resources/toon/models/tt_a_chr_dgl_shorts_torso_1000.bam',
							'legs': self.pandaDirectory + '/resources/toon/models/tt_a_chr_dgm_shorts_legs_1000.bam'},
							{'torso':{
							'neutral': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgl_shorts_torso_neutral.bam',
							'run': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgl_shorts_torso_run.bam',
							'attack': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgl_shorts_torso_pie-throw.bam',
							'walk': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgl_shorts_torso_walk.bam'
							},
							'legs':{
							'neutral': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgm_shorts_legs_neutral.bam',
							'run': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgm_shorts_legs_run.bam',
							'attack': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgm_shorts_legs_pie-throw.bam',
							'walk': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgm_shorts_legs_walk.bam'
							}})
		self.toon.attach('torso', 'legs', 'joint_hips')
		self.toon.reparentTo(render)
		self.toon.find('**/neck').setColor(1, 1, 0)
		self.toon.find('**/legs').setColor(1, 1, 0)
		self.toon.find('**/arms').setColor(1, 1, 0)
		self.toon.find('**/hands').setColor(1, 1, 1)
		
		#Set textures and remove unnecessary models
		self.toon.find('**/sleeves').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/toon/textures/ttr_t_chr_avt_shirtSleeve_cashbotCrusher.jpg'),1)
		self.toon.find('**/torso-top').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/toon/textures/ttr_t_chr_avt_shirt_cashbotCrusher.jpg'),1)
		self.toon.find('**/torso-bot').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/toon/textures/ttr_t_chr_avt_shorts_cashbotCrusher.jpg'),1)
		self.toon.find('**/shoes').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/toon/textures/ttr_t_chr_avt_acc_sho_cashbotCrusher.jpg'),1)
		self.toon.find('**/feet').removeNode()
		self.toon.find('**/boots_short').removeNode()
		self.toon.find('**/boots_long').removeNode()
		
		#Create the toon head!
		self.toonHead = loader.loadModel(self.pandaDirectory + '/resources/toon/models/tt_a_chr_dgm_skirt_head_1000.bam')
		self.toonHead.reparentTo(self.toon.find('**/def_head'))
		self.toonHead.find('**/head').setColor(1, 1, 0)
		self.toonHead.find('**/head-front').setColor(1, 1, 0)
		
		#Add a cute hat
		self.topHat = loader.loadModel(self.pandaDirectory + '/resources/toon/models/tt_m_chr_avt_acc_hat_topHat.bam')
		self.topHat.reparentTo(self.toonHead.find('**/head'))
		self.topHat.setZ(0.5)
		self.topHat.setHpr(180,-45,0)
		self.topHat.setTexture(loader.loadTexture(self.pandaDirectory + '/resources/toon/textures/tt_t_chr_avt_acc_hat_topHatQuizmaster.jpg'),1)
		self.topHat.setScale(0.35)
		
		return self.toon
		
pieThrow = PieThrow()
pieThrow.run()
