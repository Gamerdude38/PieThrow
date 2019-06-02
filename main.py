'''
John Maurer

Description: A driver class for Pie Throw, a class that demonstrates
knowledge of the Panda3D engine, focusing on the use of Tasks, Event
Handlers, Audio, Collisions, and basic health-bar game logic
'''

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.interval.LerpInterval import LerpPosInterval,LerpHprInterval
from direct.interval.ActorInterval import ActorInterval
from direct.interval.IntervalGlobal import *
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
		self.pieIsThrown = False
		self.movementHeading = ''
		self.turnHeading = ''
		self.speed = 0.0
		self.turnSpeed = 0.0
		self.toonCurrentH = 0
		
		#Source for collision learning: https://discourse.panda3d.org/t/panda3d-collisions-made-simple/7441
		#Define collision traverser and handlers
		self.cTrav = CollisionTraverser()
		self.floorHandler = CollisionHandlerFloor()
		self.floorHandler.setMaxVelocity(40)
		self.wallHandler = CollisionHandlerPusher()
		
		#Define collision masks
		FLOOR_MASK = BitMask32.bit(1)
		WALL_MASK = BitMask32.bit(2)
		
		#Load the main terrain to be used
		self.terrain = loader.loadModel(self.pandaDirectory + '/resources/terrain/CogGolfHub.bam')
		self.terrain.reparentTo(render)
		self.terrain.setScale(1.5)
		
		#Load the wall to block off the exit tunnel
		self.wall = loader.loadModel(self.pandaDirectory + '/resources/terrain/LB_wall_panel.bam')
		self.wall.reparentTo(render)
		self.wall.setPos(-30, -185, 0)
		self.wall.setH(-30)
		self.wall.setScale(1.6, 1, 2)
		
		#Load the pie model
		self.pieNode = NodePath('pieNode')
		self.pieNode.reparentTo(render)
		self.pieNode.setPos(0, 0, 5)
		self.pie = loader.loadModel(self.pandaDirectory + "/resources/toon/models/tart.bam")
		
		#Set up the pie's collision capsule (wall & cog collisions)
		self.pieCapsule = self.pieNode.attachNewNode(CollisionNode('pieCap'))
		self.pieCapsule.node().addSolid(CollisionCapsule(0, 0, 0.2, 0, 0, 0, 0.5))
		self.pieCapsule.node().setFromCollideMask(WALL_MASK)
		self.pieCapsule.node().setIntoCollideMask(BitMask32.allOff())
		
		#Set up the pie's collision ray (gravity & floor collisions)
		self.pieSeg = self.pieNode.attachNewNode(CollisionNode('pieSeg'))
		self.pieSeg.node().addSolid(CollisionRay(0, 0, 1, 0, 0, -1))
		self.pieSeg.node().setFromCollideMask(FLOOR_MASK)
		self.pieSeg.node().setIntoCollideMask(BitMask32.allOff())
		
		#Define intervals for the pie's spawning movement
		self.scalePie = LerpScaleInterval(self.pie, 1, 1, 0)
		
		#Initialize the toon model and its parent node
		self.toonNode = NodePath('toonNode')
		self.toonNode.reparentTo(render)
		self.toonNode.setHpr(-90,0,0)
		self.toonNode.setPos(2, 2, 5)
		self.toon = self.initToon()
		self.toon.reparentTo(self.toonNode)
		
		#Set up the toon collision capsule
		self.toonCapsule = self.toon.attachNewNode(CollisionNode('toonCap'))
		self.toonCapsule.node().addSolid(CollisionCapsule(0, 0, 2, 0, 0, 2, 1))
		self.toonCapsule.node().setFromCollideMask(WALL_MASK)
		self.toonCapsule.node().setIntoCollideMask(BitMask32.allOff())
		
		#Set up the toon collision ray
		self.toonRay = self.toonNode.attachNewNode(CollisionNode('toonRay'))
		self.toonRay.node().addSolid(CollisionRay(0, 0, 2, 0, 0, -1))
		self.toonRay.node().setFromCollideMask(FLOOR_MASK)
		self.toonRay.node().setIntoCollideMask(BitMask32.allOff())
		
		#Define the floor and wall coliding bodies
		self.floorCollider = self.terrain.find("**/collision_floors")
		self.wallCollider = self.terrain.find("**/collision_walls")
		self.floorCollider.node().setIntoCollideMask(FLOOR_MASK)
		self.wallCollider.node().setIntoCollideMask(WALL_MASK)
		
		#Add important collision events to the handlers
		self.floorHandler.addInPattern('%fn-into-%in')
		#self.wallHandler.addInPattern('%fn-into-%in')
		
		#Add the toon and pie colliders to the handlers
		self.floorHandler.addCollider(self.toonRay, self.toonNode)
		self.floorHandler.addCollider(self.pieSeg, self.pieNode)
		self.wallHandler.addCollider(self.toonCapsule, self.toonNode)
		self.wallHandler.addCollider(self.pieCapsule, self.pieNode)
		
		#Add the handlers to the traverser (collision driver)
		self.cTrav.addCollider(self.toonRay, self.floorHandler)
		self.cTrav.addCollider(self.pieSeg, self.floorHandler)
		self.cTrav.addCollider(self.toonCapsule, self.wallHandler)
		self.cTrav.addCollider(self.pieCapsule, self.wallHandler)
		
		self.cTrav.showCollisions(render)
		
		#Reparent the camera
		self.camera.reparentTo(self.toon)
		self.camera.setPos(self.toon, 0, -20, 5)
		
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
		
		#Accept collision handling events
		self.accept('self.pieSeg-into-self.floorCollider', self.pieFloorCollision)
		
		#Set up throwing interval and sequence
		self.throwTorso = self.toon.actorInterval('attackTorso', loop=0)
		self.throw = Sequence(Func(self.toggleIsThrowing),
									Parallel(self.throwTorso, self.scalePie),
									Func(self.toggleIsThrowing),
									Func(self.attackEnd)
									)
		
		#Tell the taskmanager to keep track of this task
		self.taskMgr.add(self.updateToon, 'Update Toon')
	
	def pieFloorCollision(self, entry):
		print('Floor collision!')
		
	def toggleIsThrowing(self):
		self.isThrowing = not(self.isThrowing)
		
	def updateToon(self, task):
		#Update the toon's position and heading
		if self.isMovingInY:
			self.toon.setY(self.toon, self.speed)
			
		if self.isTurning:
			self.toon.setH(self.toon, self.turnSpeed)
		
		self.toonCurrentH = self.toon.getH()
		return task.cont
	
	def attackStart(self):
		#If the toon is already throwing, ignore new request
		if self.isThrowing:
			return
		
		#Determine which group of animations to play
		if not self.isMovingInY and not self.isTurning:
			self.toon.loop('attackLegs')
		
		#Render the pie, then throw it!
		self.pie.reparentTo(self.toon.find('**/def_joint_right_hold'))
		self.taskMgr.doMethodLater(2.7, self.throwPie, 'throw pie')
		
		#Call the pre-defined sequence
		self.throw.start()
	
	def attackEnd(self):
		#Determine which animation to play after throwing
		if self.isMovingInY and self.speed > 0:
			self.toon.loop('run', 'torso')
		elif self.isTurning:
			self.toon.loop('walk', 'torso')
		else:
			self.toon.loop('neutral', 'torso')
	
	def throwPie(self, task):
		#Determine where to put the projectile pie
		#This isn't the prettiest solution, but its the most consistent
		#With the animations to make the toon throw the pie straight
		currentPiePos = self.pie.getPos(render)
		currentPieH = self.toonCurrentH
		currentPieP = self.toon.getP(render)
		currentPieR = 83
		
		#reparent the pie model to its parent node
		self.pieNode.setPos(currentPiePos)
		self.pieNode.setHpr(currentPieH, currentPieP, currentPieR)
		self.pie.reparentTo(self.pieNode)
		
		#Define path interval and start playing it
		self.flyingPie = ProjectileInterval(self.pieNode, startPos=self.pieNode.getPos(), 
											startVel=render.getRelativeVector(self.pieNode,Vec3(0,0,100)), duration=5)
		self.flyingPie.start()
		
		self.pieIsThrown = True
		
		return task.done
	
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
		
		return self.toon
		
pieThrow = PieThrow()
pieThrow.run()
