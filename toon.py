'''
John Maurer

Description: A class that creates a toon and manipulates it based on key presses.
Also defines the toon's animations
'''

from panda3d.core import *
from direct.showbase import DirectObject
from direct.actor.Actor import Actor
from direct.interval.LerpInterval import LerpPosInterval,LerpHprInterval
from direct.interval.ActorInterval import ActorInterval
from direct.interval.IntervalGlobal import *
from direct.task import Task
import sys,os

class Toon(DirectObject.DirectObject):
	def __init__(self, taskMgr):
		#Establish where the current directory of the running file is
		self.currentDirectory = os.path.abspath(sys.path[0])
		self.pandaDirectory = Filename.fromOsSpecific(self.currentDirectory).getFullpath()
		
		#Define variables, particularly to tell if the model is moving
		self.isThrowing = False
		self.isMovingInY = False
		self.isTurning = False
		self.pieIsThrown = False
		self.movementHeading = ''
		self.turnHeading = ''
		self.speed = 0.0
		self.turnSpeed = 0.0
		self.health = 100
		
		#Set object variable to point to the global task manager
		self.taskMgr = taskMgr
		
		#Define pie node, which will serve as the flying part of the pie. Put it far enough away to not cause problems
		self.pieNode = NodePath('pieNode')
		self.pieNode.reparentTo(render)
		self.pieNode.setPos(100, 0, 0)
		
		#Load the pie model and define its scaling motion
		self.pie = loader.loadModel(self.pandaDirectory + "/resources/toon/models/tart.bam")
		self.scalePie = LerpScaleInterval(self.pie, 1, 1, 0)
		
		#Set up the Actor
		self.initActor()
		
		#Initialize animations
		self.toon.loop('neutral', 'torso')
		self.toon.loop('neutral', 'legs')
		
		#Define Y (Forwards/backwards) movement
		self.accept('arrow_up', self.moveInYStart, ['forward'])
		self.accept('arrow_up-up', self.moveInYEnd, ['forward'])
		self.accept('arrow_down', self.moveInYStart, ['backward'])
		self.accept('arrow_down-up', self.moveInYEnd, ['backward'])
		
		#Define turning movement
		self.accept('arrow_right', self.turnStart, ['right'])
		self.accept('arrow_right-up', self.turnEnd, ['right'])
		self.accept('arrow_left', self.turnStart, ['left'])
		self.accept('arrow_left-up', self.turnEnd, ['left'])
		
		#Define pie throwing animation control
		self.accept('control', self.attackStart)
		
		#Set up throwing interval and sequence
		self.throwTorso = self.toon.actorInterval('attackTorso', loop=0)
		self.throw = Sequence(Func(self.toggleIsThrowing),
									Parallel(self.throwTorso, self.scalePie),
									Func(self.toggleIsThrowing),
									Func(self.attackEnd)
									)
		
		#Tell the taskmanager to keep track of this task
		self.taskMgr.add(self.updateToon, 'Update Toon')
		
	def updateToon(self, task):
		#Update the player's position and heading
		if self.isMovingInY:
			self.toon.setY(self.toon, self.speed)
			
		if self.isTurning:
			self.toon.setH(self.toon, self.turnSpeed)
		
		return task.cont
		
	def toggleIsThrowing(self):
		self.isThrowing = not(self.isThrowing)
	
	def attackStart(self):
		#If the player is already throwing, ignore new request
		if self.isThrowing:
			return
		
		#Determine which group of animations to play
		if not self.isMovingInY and not self.isTurning:
			self.toon.loop('attackLegs')
		
		#Render the pie, then throw it!
		self.pie.setHpr(0,0,0)
		self.pie.reparentTo(self.toon.find('**/def_joint_right_hold'))
		self.taskMgr.doMethodLater(2.7, self.throwPie, 'throw pie')
		
		#Call the pre-defined sequence
		self.throw.start()
	
	def attackEnd(self):
		#Determine which animation to play after throwing
		if self.isMovingInY and self.speed > 0:
			self.toon.loop('run', 'torso')
			
		elif self.isMovingInY and self.speed < 0:
			self.toon.loop('walk', 'torso')
		
		elif self.isTurning:
			self.toon.loop('walk', 'torso')
		
		else:
			self.toon.loop('neutral', 'torso')
	
	def throwPie(self, task):
		#Get the current position and hpr of the pie for the pieNode
		self.pieNode.setPos(self.pie.getPos(render))
		pieHpr = Point3(self.toon.getH(render) + 90, self.pie.getP(render), 80)
		
		#Reparent the pie to the pieNode
		self.pie.reparentTo(self.pieNode)
		self.pie.setHpr(pieHpr)
		
		#Arch that pieNode puppy!
		self.flyingPie = ProjectileInterval(self.pieNode, startPos=self.pieNode.getPos(), 
											startVel=render.getRelativeVector(self.pie,Vec3(0,0,75)), duration=5)
		self.flyingPie.start()
		
		self.pieIsThrown = True
		
		return task.done
	
	def turnStart(self, direction):
		#If the player is already turning, ignore the new request
		if self.isTurning:
			return
		
		#Set the object heading to prevent pressing the right and left keys at the same time
		self.turnHeading = direction
		
		#If the player is moving in the Y direction...
		if self.isMovingInY:
			#And the player is moving backwards...
			if self.speed < 0:
				#Replace the run animation with walk and play it backwards
				self.toon.setPlayRate(-1, 'walk')
				
		#If the player is not moving
		else:
			#Play the forward plain walking animations
			self.toon.setPlayRate(1, 'walk')
			self.toon.loop('walk', 'torso')
			self.toon.loop('walk', 'legs')
		
		#Determine which heading the player will turn
		if direction == 'right':
			self.turnSpeed = -0.7
		elif direction == 'left':
			self.turnSpeed = 0.7
		
		#Tell task manager to start turning
		self.isTurning = True
		
	def turnEnd(self, direction):
		#If the requested direction conflicts with the heading, ignore the request
		if direction != self.turnHeading:
			return
			
		#If the player is not moving in the Y direction...
		if not self.isMovingInY:
			#Make the animation play neutral before stopping to turn
			self.toon.loop('neutral', 'torso')
			self.toon.loop('neutral', 'legs')
		
		#Tell task manager to stop turning
		self.isTurning = False
		
	def moveInYStart(self, direction):
		#If the player is already moving, ignore the new request
		if self.isMovingInY:
			return
		
		#Set the object heading to prevent pressing the up and down keys at the same time
		self.movementHeading = direction
		
		#If the up key is pressed...
		if direction == 'forward':
			#Set a positive speed and make the player run
			self.speed = 0.6
			self.toon.loop('run', 'torso')
			self.toon.loop('run', 'legs')
		
		#Otherwise...
		elif direction == 'backward':
			#Set a negative speed and make the player walk backwards
			self.speed = -0.3
			self.toon.setPlayRate(-1, 'walk')
			self.toon.loop('walk', 'torso')
			self.toon.loop('walk', 'legs')
		
		#Tell the task manager to start moving in local Y
		self.isMovingInY = True
			
	def moveInYEnd(self, direction):
		#If the requested direction conflicts with the heading, ignore the request
		if direction != self.movementHeading:
			return
		
		#If the player is not turning...
		if not self.isTurning:
			#Set the speed to positive and have the player idle
			self.speed = 0.6
			self.toon.loop('neutral', 'torso')
			self.toon.loop('neutral', 'legs')
			
		#Otherwise...
		else:
			#Make the player walk instead
			self.toon.setPlayRate(1, 'walk')
			self.speed = 0.6
			self.toon.loop('walk', 'torso')
			self.toon.loop('walk', 'legs')
		
		#Tell the task manager to stop moving in local Y
		self.isMovingInY = False
		
	def initActor(self):
		#Create the toon!
		self.toon = Actor({'torso': self.pandaDirectory + '/resources/toon/models/tt_a_chr_dgl_shorts_torso_1000.bam',
							'legs': self.pandaDirectory + '/resources/toon/models/tt_a_chr_dgm_shorts_legs_1000.bam'},
							{'torso':{
							'neutral': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgl_shorts_torso_neutral.bam',
							'run': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgl_shorts_torso_run.bam',
							'attackTorso': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgl_shorts_torso_pie-throw.bam',
							'walk': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgl_shorts_torso_walk.bam'
							},
							'legs':{
							'neutral': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgm_shorts_legs_neutral.bam',
							'run': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgm_shorts_legs_run.bam',
							'attackLegs': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgm_shorts_legs_pie-throw.bam',
							'walk': self.pandaDirectory + '/resources/toon/animations/tt_a_chr_dgm_shorts_legs_walk.bam'
							}})
		self.toon.attach('torso', 'legs', 'joint_hips')
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
