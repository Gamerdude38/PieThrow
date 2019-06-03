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
		
		#Source for collision learning: https://discourse.panda3d.org/t/panda3d-collisions-made-simple/7441
		#Define collision handlers and the traverser
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
		
		self.terrain.ls()
		
		#Set tags for the terrain to mark everything
		self.terrain.find('**/collision_floors').setTag('collisions', 'floor')
		self.terrain.find('**/collision_walls').setTag('collisions', 'walls')
		self.terrain.find('**/Door_0_Collision').setTag('collisions', 'walls')
		
		#Further specify terrain for colliders
		self.floor = self.terrain.find('**/collision_floors')
		self.walls = self.terrain.find('**/collision_walls')

		#Load the wall to block off the exit tunnel
		self.wall = loader.loadModel(self.pandaDirectory + '/resources/terrain/LB_wall_panel.bam')
		self.wall.reparentTo(render)
		self.wall.setPos(-30, -185, 0)
		self.wall.setH(-30)
		self.wall.setScale(1.6, 1, 2)
		self.wall.setTag('collisions', 'walls')
		
		#Define floor collider
		self.floorCollider = self.floor
		self.floorCollider.node().setIntoCollideMask(FLOOR_MASK)
		
		#Define wall collider
		self.wallCollider = self.walls
		self.wallCollider.node().setIntoCollideMask(WALL_MASK)
		
		#Initialize the player model
		self.player = self.initToon()
		self.player.reparentTo(render)
		
		#Set up player wall collision capsule
		self.playerSphere = self.player.attachNewNode(CollisionNode('playerSphere'))
		self.playerSphere.node().addSolid(CollisionSphere(0, 0, 0, 1))
		self.playerSphere.setPos(0, 0, 3)
		self.playerSphere.node().setFromCollideMask(WALL_MASK)
		self.playerSphere.node().setIntoCollideMask(BitMask32.allOff())
		self.playerSphere.show()
		
		#Set up player floor collision ray
		self.playerRay = self.player.attachNewNode(CollisionNode('playerRay'))

		#The ray has to be a unit above to detect stairs and inclined planes
		self.playerRay.node().addSolid(CollisionRay(0, 0, 1, 0, 0, -1))
		self.playerRay.node().setFromCollideMask(FLOOR_MASK)
		self.playerRay.node().setIntoCollideMask(BitMask32.allOff())
		
		#Define pie node, which will serve as the flying part of the pie
		self.pieNode = NodePath('pieNode')
		self.pieNode.reparentTo(render)
		
		#Load the pie model and define its scaling motion
		self.pie = loader.loadModel(self.pandaDirectory + "/resources/toon/models/tart.bam")
		self.scalePie = LerpScaleInterval(self.pie, 1, 1, 0)
		
		#Set up pie wall collision capsule
		self.pieSphere = self.pieNode.attachNewNode(CollisionNode('pieSphere'))
		self.pieSphere.node().addSolid(CollisionSphere(0, 0, 0, 0.75))
		self.pieSphere.node().setFromCollideMask(WALL_MASK)
		self.pieSphere.node().setIntoCollideMask(BitMask32.allOff())
		self.pieSphere.show()
		
		#Set up pie floor collision segment
		self.pieSeg = self.pieNode.attachNewNode(CollisionNode('pieSeg'))
		self.pieSeg.node().addSolid(CollisionSegment(0, 0, 1, 0, 0, -1))
		self.pieSeg.node().setFromCollideMask(FLOOR_MASK)
		self.pieSeg.node().setIntoCollideMask(BitMask32.allOff())
		
		#Add collisions to handler
		self.floorHandler.addCollider(self.pieSeg, self.pieNode)
		self.floorHandler.addCollider(self.playerRay, self.player)
		self.wallHandler.addCollider(self.pieSphere, self.pieNode)
		self.wallHandler.addCollider(self.playerSphere, self.player)
		
		#Add important collision events to the handlers (tags are used 
		#since there are multiple GeomNodes under 'collision_floors' and walls)
		self.floorHandler.addInPattern('%fn-into-%(collisions)it')
		self.wallHandler.addInPattern('%fn-into-%(collisions)it')
		
		#Add handlers to traverser
		self.cTrav.addCollider(self.playerRay, self.floorHandler)
		self.cTrav.addCollider(self.pieSeg, self.floorHandler)
		self.cTrav.addCollider(self.playerSphere, self.wallHandler)
		self.cTrav.addCollider(self.pieSphere, self.wallHandler)
		
		#Render collisions
		self.cTrav.showCollisions(render)
		
		#Reparent the camera
		self.camera.reparentTo(self.player)
		self.camera.setPos(self.player, 0, -20, 5)
		
		#Initialize animations
		self.player.loop('neutral', 'torso')
		self.player.loop('neutral', 'legs')
		
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
		
		#Accept collision handling events (into-NodeName must be the name of the ACTUAL NODE in the scene graph)
		self.accept('pieSeg-into-floor', self.pieFloorCollision)
		self.accept('pieSphere-into-walls', self.pieWallCollision)
		
		#Set up throwing interval and sequence
		self.throwTorso = self.player.actorInterval('attackTorso', loop=0)
		self.throw = Sequence(Func(self.toggleIsThrowing),
									Parallel(self.throwTorso, self.scalePie),
									Func(self.toggleIsThrowing),
									Func(self.attackEnd)
									)
		
		#Tell the taskmanager to keep track of this task
		self.taskMgr.add(self.updateToon, 'Update Toon')
	
	def pieFloorCollision(self, entry):
		print('Floor collision!')
	
	def pieWallCollision(self, entry):
		print('Wall collision!')
		
	def toggleIsThrowing(self):
		self.isThrowing = not(self.isThrowing)
		
	def updateToon(self, task):
		#Update the player's position and heading
		if self.isMovingInY:
			self.player.setY(self.player, self.speed)
			
		if self.isTurning:
			self.player.setH(self.player, self.turnSpeed)
		
		self.playerCurrentH = self.player.getH()
		return task.cont
	
	def attackStart(self):
		#If the player is already throwing, ignore new request
		if self.isThrowing:
			return
		
		#Determine which group of animations to play
		if not self.isMovingInY and not self.isTurning:
			self.player.loop('attackLegs')
		
		#Render the pie, then throw it!
		self.pie.setHpr(0,0,0)
		self.pie.reparentTo(self.player.find('**/def_joint_right_hold'))
		self.taskMgr.doMethodLater(2.7, self.throwPie, 'throw pie')
		
		#Call the pre-defined sequence
		self.throw.start()
	
	def attackEnd(self):
		#Determine which animation to play after throwing
		if self.isMovingInY and self.speed > 0:
			self.player.loop('run', 'torso')
		elif self.isTurning:
			self.player.loop('walk', 'torso')
		else:
			self.player.loop('neutral', 'torso')
	
	def throwPie(self, task):
		#Get the current position and hpr of the pie for the pieNode
		self.pieNode.setPos(self.pie.getPos(render))
		pieHpr = Point3(self.player.getH(render) + 90, self.pie.getP(render), 80)
		
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
				self.player.setPlayRate(-1, 'walk')
				
		#If the player is not moving
		else:
			#Play the forward plain walking animations
			self.player.setPlayRate(1, 'walk')
			self.player.loop('walk', 'torso')
			self.player.loop('walk', 'legs')
		
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
			self.player.loop('neutral', 'torso')
			self.player.loop('neutral', 'legs')
		
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
			self.player.loop('run', 'torso')
			self.player.loop('run', 'legs')
		
		#Otherwise...
		elif direction == 'backward':
			#Set a negative speed and make the player walk backwards
			self.speed = -0.3
			self.player.setPlayRate(-1, 'walk')
			self.player.loop('walk', 'torso')
			self.player.loop('walk', 'legs')
		
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
			self.player.loop('neutral', 'torso')
			self.player.loop('neutral', 'legs')
			
		#Otherwise...
		else:
			#Make the player walk instead
			self.player.setPlayRate(1, 'walk')
			self.speed = 0.6
			self.player.loop('walk', 'torso')
			self.player.loop('walk', 'legs')
		
		#Tell the task manager to stop moving in local Y
		self.isMovingInY = False
		
	def initToon(self):
		#Create the toon!
		self.player = Actor({'torso': self.pandaDirectory + '/resources/toon/models/tt_a_chr_dgl_shorts_torso_1000.bam',
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
		self.player.attach('torso', 'legs', 'joint_hips')
		self.player.find('**/neck').setColor(1, 1, 0)
		self.player.find('**/legs').setColor(1, 1, 0)
		self.player.find('**/arms').setColor(1, 1, 0)
		self.player.find('**/hands').setColor(1, 1, 1)
		
		#Set textures and remove unnecessary models
		self.player.find('**/sleeves').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/toon/textures/ttr_t_chr_avt_shirtSleeve_cashbotCrusher.jpg'),1)
		self.player.find('**/torso-top').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/toon/textures/ttr_t_chr_avt_shirt_cashbotCrusher.jpg'),1)
		self.player.find('**/torso-bot').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/toon/textures/ttr_t_chr_avt_shorts_cashbotCrusher.jpg'),1)
		self.player.find('**/shoes').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/toon/textures/ttr_t_chr_avt_acc_sho_cashbotCrusher.jpg'),1)
		self.player.find('**/feet').removeNode()
		self.player.find('**/boots_short').removeNode()
		self.player.find('**/boots_long').removeNode()
		
		#Create the toon head!
		self.toonHead = loader.loadModel(self.pandaDirectory + '/resources/toon/models/tt_a_chr_dgm_skirt_head_1000.bam')
		self.toonHead.reparentTo(self.player.find('**/def_head'))
		self.toonHead.find('**/head').setColor(1, 1, 0)
		self.toonHead.find('**/head-front').setColor(1, 1, 0)
		
		#Add a cute hat
		self.topHat = loader.loadModel(self.pandaDirectory + '/resources/toon/models/tt_m_chr_avt_acc_hat_topHat.bam')
		self.topHat.reparentTo(self.toonHead.find('**/head'))
		self.topHat.setZ(0.5)
		self.topHat.setHpr(180,-45,0)
		self.topHat.setTexture(loader.loadTexture(self.pandaDirectory + '/resources/toon/textures/tt_t_chr_avt_acc_hat_topHatQuizmaster.jpg'),1)
		self.topHat.setScale(0.35)
		
		return self.player
		
pieThrow = PieThrow()
pieThrow.run()
