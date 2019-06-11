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
from toon import Toon
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
		
		#Source for collision learning: https://discourse.panda3d.org/t/panda3d-collisions-made-simple/7441
		#Define collision handlers and the traverser
		self.cTrav = CollisionTraverser()
		self.floorHandler = CollisionHandlerFloor()
		self.floorHandler.setMaxVelocity(40)
		self.wallHandler = CollisionHandlerPusher()
		
		#Define collision masks
		self.floorMaskBit = 1
		self.wallMaskBit = 2
		self.enemyMaskBit = 3
		self.FLOOR_MASK = BitMask32.bit(self.floorMaskBit)
		self.WALL_MASK = BitMask32.bit(self.wallMaskBit)
		self.ENEMY_MASK = BitMask32.bit(self.enemyMaskBit)
		
		#Load the main terrain to be used
		self.terrain = loader.loadModel(self.pandaDirectory + '/resources/terrain/CogGolfHub.bam')
		self.terrain.reparentTo(render)
		self.terrain.setScale(1.5)
		
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
		self.floorCollider.node().setIntoCollideMask(self.FLOOR_MASK)
		
		#Define wall collider
		self.wallCollider = self.walls
		self.wallCollider.node().setIntoCollideMask(self.WALL_MASK)
		
		#Initialize the player model
		self.player = Toon(self.taskMgr)
		self.player.toon.reparentTo(render)
		
		#Set up player wall collision capsule
		self.playerSphere = self.player.toon.attachNewNode(CollisionNode('playerSphere'))
		self.playerSphere.node().addSolid(CollisionSphere(0, 0, 0, 1))
		self.playerSphere.setZ(3)
		self.playerSphere.node().setFromCollideMask(self.WALL_MASK)
		self.playerSphere.node().setIntoCollideMask(self.WALL_MASK)
		self.playerSphere.show()
		
		#Set up player floor collision ray
		self.playerRay = self.player.toon.attachNewNode(CollisionNode('playerRay'))
		
		#The ray has to be a unit above to detect stairs and inclined planes
		self.playerRay.node().addSolid(CollisionRay(0, 0, 1, 0, 0, -1))
		self.playerRay.node().setFromCollideMask(self.FLOOR_MASK)
		self.playerRay.node().setIntoCollideMask(BitMask32.allOff())
		
		#Set up enemy for testing
		self.enemy = RandomCog(self.taskMgr, self.enemyMaskBit, self.wallMaskBit, self.player, 10, 0.05)
		
		#Set a pie mask so that it detects wall and enemy collisions
		self.pieSphereMask = BitMask32()
		self.pieSphereMask.setBit(self.wallMaskBit)
		self.pieSphereMask.setBit(self.enemyMaskBit)
		
		#Set up pie wall collision capsule
		self.pieSphere = self.player.pieNode.attachNewNode(CollisionNode('pieSphere'))
		self.pieSphere.node().addSolid(CollisionSphere(0, 0, 0, 0.75))
		self.pieSphere.node().setFromCollideMask(self.pieSphereMask)
		self.pieSphere.node().setIntoCollideMask(BitMask32.allOff())
		self.pieSphere.show()
		
		#Set up pie floor collision segment
		self.pieSeg = self.player.pieNode.attachNewNode(CollisionNode('pieSeg'))
		self.pieSeg.node().addSolid(CollisionSegment(0, 0, 1, 0, 0, -1))
		self.pieSeg.node().setFromCollideMask(self.FLOOR_MASK)
		self.pieSeg.node().setIntoCollideMask(BitMask32.allOff())
		
		#Add collisions to handler
		self.floorHandler.addCollider(self.pieSeg, self.player.pieNode)
		self.floorHandler.addCollider(self.playerRay, self.player.toon)
		self.wallHandler.addCollider(self.pieSphere, self.player.pieNode)
		self.wallHandler.addCollider(self.playerSphere, self.player.toon)
		self.wallHandler.addCollider(self.enemy.cogTorsoBox, self.enemy.cog)
		
		#Add important collision events to the handlers (tags are used 
		#since there are multiple GeomNodes under 'collision_floors' and walls)
		self.floorHandler.addInPattern('%fn-into-%(collisions)it')
		self.wallHandler.addInPattern('%fn-into-%(collisions)it')
		self.wallHandler.addInPattern('%fn-into-%in')
		
		#Add handlers to traverser
		self.cTrav.addCollider(self.playerRay, self.floorHandler)
		self.cTrav.addCollider(self.pieSeg, self.floorHandler)
		self.cTrav.addCollider(self.playerSphere, self.wallHandler)
		self.cTrav.addCollider(self.pieSphere, self.wallHandler)
		self.cTrav.addCollider(self.enemy.cogTorsoBox, self.wallHandler)
		
		#Render collisions
		self.cTrav.showCollisions(render)
		
		#Reparent the camera
		self.camera.reparentTo(self.player.toon)
		self.camera.setPos(self.player.toon, 0, -20, 5)
		
		#Accept collision handling events (into-NodeName must be the name of the ACTUAL NODE in the scene graph)
		#For this case, we're using tags instead
		self.accept('pieSeg-into-floor', self.pieTerrainCollision)
		self.accept('pieSphere-into-walls', self.pieTerrainCollision)
		self.accept('pieSphere-into-cogTorsoBox', self.pieEnemyCollision)
		self.accept('pieSphere-into-cogHeadBox', self.pieEnemyCollision)
		self.accept('pieSphere-into-cogLegsBox', self.pieEnemyCollision)
		self.accept('playerSphere-into-cogTorsoBox', self.cogToonCollision)
		self.accept('cogTorsoBox-into-playerSphere', self.cogToonCollision)
	
	def pieTerrainCollision(self, entry):
		print('Terrain collision!')
		
	def pieEnemyCollision(self, entry):
		#Reduce cog health and update it
		self.enemy.currentHealth -= 1
		self.enemy.updateHealth()
	
	def cogToonCollision(self, entry):
		#Reduce toon health, play toon damage animation, play finger wag
		#self.player.health -= 1
		
		print('Toon take damage!')
	
		
pieThrow = PieThrow()
pieThrow.run()
