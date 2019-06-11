'''
John Maurer

Description: A class that generates a random cog model, renders it, and
defines its animations and collisions
'''

from direct.actor.Actor import Actor
from direct.interval.LerpInterval import LerpPosInterval,LerpHprInterval
from direct.interval.ActorInterval import ActorInterval
from direct.interval.IntervalGlobal import *
from panda3d.core import *
import sys,os
import random

class RandomCog():
	def __init__(self, taskMgr, enemyMaskBit, wallMaskBit, player, maxHealth, speed):
		#Initialize variables for the cog's health, speed, and scale
		self.maxHealth = maxHealth
		self.currentHealth = self.maxHealth
		self.speed = speed
		self.scale = 1
		
		#Set masks
		self.enemyMaskBit = enemyMaskBit
		self.wallMaskBit = wallMaskBit
		self.ENEMY_MASK = BitMask32.bit(self.enemyMaskBit)
		self.WALL_MASK = BitMask32.bit(self.wallMaskBit)
		
		#Establish current file path location
		self.currentDirectory = os.path.abspath(sys.path[0])
		self.pandaDirectory = Filename.fromOsSpecific(self.currentDirectory).getFullpath()
		
		#Set object variable to point to the global task manager
		self.taskMgr = taskMgr
		
		#Define location of the toon node
		self.player = player
		
		#Select the cog from random
		self.pickRandomCog()
		
		#Render the head and actor
		self.cog.reparentTo(render)
		self.head.reparentTo(self.cog.find('**/def_head'))
		
		#Scale the model
		self.cog.setScale(self.scale)
		
		'''
		After doing some research into using the life meter, I found a class from Toontown Empire that
		was particularly helpful. https://github.com/AnonymousDeveloper13/Toontown-Empire/blob/master/src/toontown/suit/SuitHealthBar.py
		'''
		
		#Set up life meter
		self.lifeMeter = loader.loadModel(self.pandaDirectory + '/resources/cogs/models/matching_game_gui.bam').find('**/minnieCircle')
		self.lifeMeter.reparentTo(self.cog.find('**/def_joint_attachMeter'))
		self.lifeMeter.setHpr(180, 0.8, 0)
		self.lifeMeter.setY(0.02)
		self.lifeMeter.setScale(3)
		self.lifeMeter.setColor(0, 1, 0)
		
		self.lifeMeterGlow = loader.loadModel(self.pandaDirectory + '/resources/cogs/models/glow.bam')
		self.lifeMeterGlow.reparentTo(self.lifeMeter)
		self.lifeMeterGlow.setScale(0.25)
		self.lifeMeterGlow.setPos(-0.01, 0.01, 0.02)
		
		#Get the sizes of the head, torso, and legs
		min, max = self.head.getTightBounds()
		self.headSize = max - min
		min, max = self.cog.find('**/torso').getTightBounds()
		self.torsoSize = max - min
		min, max = self.cog.find('**/legs').getTightBounds()
		self.legSize = max - min
		
		#Set up box collider for cog head
		self.cogHeadBox = self.head.attachNewNode(CollisionNode('cogHeadBox'))
		self.cogHeadBox.node().addSolid(CollisionBox(self.head.getBounds().getCenter(), 
										(self.headSize.getX() / 2),
										(self.headSize.getY() / 2),
										(self.headSize.getZ() / 2)
										))
		self.cogHeadBox.node().setFromCollideMask(self.ENEMY_MASK)
		self.cogHeadBox.node().setIntoCollideMask(self.ENEMY_MASK)
		#self.cogHeadBox.show()
		
		#Set up box collider for cog torso
		self.cogTorsoBox = self.cog.find('**/torso').attachNewNode(CollisionNode('cogTorsoBox'))
		self.cogTorsoBox.node().addSolid(CollisionBox(self.cog.find('**/torso').getBounds().getCenter(), 
										(self.torsoSize.getX() / 2) + (self.torsoSize.getX() / 5),
										(self.torsoSize.getY() / 2),
										(self.torsoSize.getZ() / 2)
										))
		self.cogTorsoBox.node().setFromCollideMask(self.WALL_MASK)
		self.cogTorsoBox.node().setIntoCollideMask(self.WALL_MASK)
		#self.cogTorsoBox.show()
		
		#Set up box collider for cog legs
		self.cogLegsBox = self.cog.find('**/torso').attachNewNode(CollisionNode('cogLegsBox'))
		self.cogLegsBox.node().addSolid(CollisionBox(self.cog.find('**/legs').getBounds().getCenter(), 
										(self.legSize.getX() / 2),
										(self.legSize.getY() / 2),
										(self.legSize.getZ() / 2)
										))
		self.cogLegsBox.node().setFromCollideMask(self.ENEMY_MASK)
		self.cogLegsBox.node().setIntoCollideMask(self.ENEMY_MASK)
		#self.cogLegsBox.show()
		
		#Set up propeller
		self.propeller = Actor(self.pandaDirectory + '/resources/cogs/models/propeller-mod.bam', {
								'fly':self.pandaDirectory + '/resources/cogs/models/propeller-chan.bam'})
		self.propeller.loop('fly', fromFrame=0, toFrame=5)
		self.propeller.setP(5)
		self.propeller.reparentTo(self.head)
		
		#Put the cog in a random position on the map
		self.cog.setPos(5, 5, 20)
		
		#Establish the flying movement
		self.cog.pose('landing', 0)
		self.flyDown = LerpPosInterval(self.cog, duration=4, pos=(self.cog.getX(), self.cog.getY(), 2))
		self.land = LerpPosInterval(self.cog, duration=1, pos=(self.cog.getX(), self.cog.getY(), 0))
		self.entranceAnim = Sequence(self.flyDown,
							Func(self.cog.play, ['landing']),
							Func(self.propeller.play, ['fly']),
							self.land,
							Wait(2.8),
							Func(self.startWalk))
							
		#Start flying down!
		self.entranceAnim.start()
	
	def startWalk(self):
		#Set the cog to walk, then call the task manager to have the cog walk towards the player
		self.cog.loop('walk')
		
		self.walkingTask = self.taskMgr.add(self.walkingCog, 'walking cog')
		
		#Establish the hit, then walk animation
		self.hitThenWalk = Sequence(Func(self.taskMgr.remove, [self.walkingTask]),
							Func(self.cog.play, ['hit']),
							Wait(2.5),
							Func(self.startWalk))
		
		#Establish the hit, then destruct animation
		self.hitThenDestroy = Sequence(Func(self.taskMgr.remove, [self.walkingTask]),
							Func(self.cog.play, ['hit']),
							Wait(2.5),
							Func(self.destruct))
		
	def walkingCog(self, task):
		#Make the cog look at the toon...
		self.cog.lookAt(self.player.toon)
		
		#Then walk towards them!
		self.cog.setY(self.cog, self.speed)
		
		return task.cont
		
	def updateHealth(self):
		#Update the life meter, depending on the cog's health
		if (self.currentHealth / self.maxHealth) >= 0.95:
			self.lifeMeter.setColor(0, 1, 0)
		elif (self.currentHealth / self.maxHealth) >= 0.65:
			self.lifeMeter.setColor(1, 1, 0)
		elif (self.currentHealth / self.maxHealth) >= 0.35:
			self.lifeMeter.setColor(1, 0.5, 0)
		elif (self.currentHealth / self.maxHealth) >= 0.05:
			self.lifeMeter.setColor(1, 0, 0)
		elif (self.currentHealth / self.maxHealth) > 0:
			self.taskMgr.add(self.blink, 'blink', extraArgs=[1.0], appendTask=True)
		else:
			#Destroy cog
			self.taskMgr.add(self.blink, 'blink', extraArgs=[0.5], appendTask=True)
			self.hitThenDestroy.start()
			return
		
		#If the cog is still alive, have him get hit then walk
		self.hitThenWalk.start()
			
		
	def blink(self, delayTime, task):
		#If the current color is red... (getColor need to be compared to an LColor)
		if self.lifeMeter.getColor() == LColor(1, 0, 0, 1):
			#Change color to grey and set delay time
			self.lifeMeter.setColor(0.45, 0.45, 0.45)
			self.lifeMeterGlow.hide()
			task.delayTime = 0.1
		else:
			#Change color to red and set delay time
			self.lifeMeter.setColor(1, 0, 0)
			self.lifeMeterGlow.show()
			task.delayTime = delayTime
			
		return task.again
	
	def destruct(self):
		#Remove the light animation from the task manager
		self.taskMgr.remove(self.walkingTask)
		self.taskMgr.remove('blink')
		self.lifeMeter.hide()
		
		#Play the destruction animation, then remove the model
		print('BOOM!')
		
	def pickRandomCog(self):
		#Generate a random number between 0 and 31 inclusive to select a cog
		self.randomNumber = random.randint(0, 31)
		
		#Num cogs in suits
		#A - 14
		#B - 9
		#C - 9
		
		#Determine which cog the random number generator picked and set its properties
		if self.randomNumber <= 13:
			#Render the suit A type cogs
			self.cog = Actor(self.pandaDirectory + '/resources/cogs/models/tt_a_ene_cga_zero.bam',{
						'neutral':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cga_neutral.bam'),
						'walk':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cga_walk.bam'),
						'finger wag':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cga_finger-wag.bam'),
						'landing':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cga_landing.bam'),
						'hit':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cga_pie-small.bam')
						})
			
			self.headList = loader.loadModel(self.pandaDirectory + '/resources/cogs/models/suitA-heads.bam')
			
			if self.randomNumber == 0:
				self.head = self.headList.find('**/backstabber')
				self.cog.find('**/hands').setColorScale(0.75,0.75,0.95,1)
				self.scale = 0.9
				self.setLawTexture()
				
			elif self.randomNumber == 1:
				self.head = self.headList.find('**/bigcheese')
				self.cog.find('**/hands').setColor(0.65,0.95,0.85,1)
				self.scale = 1.3
				self.setBossTexture()
				
			elif self.randomNumber == 2:
				self.head = self.headList.find('**/bigwig')
				self.cog.find('**/hands').setColor(0.75,0.75,0.95,1)
				self.scale = 1.3
				self.setLawTexture()
				
			elif self.randomNumber == 3:
				self.head = self.headList.find('**/headhunter')
				self.cog.find('**/hands').setColor(0.95,0.75,0.75,1)
				self.scale = 1.2
				self.setBossTexture()
				
			elif self.randomNumber == 4:
				self.head = self.headList.find('**/legaleagle')
				self.cog.find('**/hands').setColor(0.3,0.3,0.55,1)
				self.scale = 1.3
				self.setLawTexture()
				
			elif self.randomNumber == 5:
				self.head = self.headList.find('**/numbercruncher')
				self.cog.find('**/hands').setColor(0.65,0.95,0.85,1)
				self.scale = 1
				self.setCashTexture()
				
			elif self.randomNumber == 6:
				#name dropper
				self.head = self.headList.find('**/numbercruncher')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/name-dropper.jpg'), 1)
				self.cog.find('**/hands').setColor(0.95,0.75,0.95,1)
				self.scale = 0.9
				self.setSellTexture()
				
			elif self.randomNumber == 7:
				self.head = self.headList.find('**/pennypincher')
				self.cog.find('**/hands').setColor(0.98,0.55,0.56,1)
				self.scale = 0.8
				self.setCashTexture()
				
			elif self.randomNumber == 8:
				self.head = self.headList.find('**/yesman')
				self.cog.find('**/hands').setColor(0.95,0.75,0.75,1)
				self.scale = 0.9
				self.setBossTexture()
				
			elif self.randomNumber == 9:
				#robber baron
				self.head = self.headList.find('**/yesman')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/robber-baron.jpg'), 1)
				self.cog.find('**/hands').setColor(0.65,0.95,0.85,1)
				self.scale = 1.3
				self.setCashTexture()
				
			elif self.randomNumber == 10:
				#mr. hollywood
				self.head = self.headList.find('**/yesman')
				self.cog.find('**/hands').setColor(0.95,0.75,0.95,1)
				self.scale = 1.3
				self.setSellTexture()
				
			elif self.randomNumber == 11:
				self.head = self.headList.find('**/twoface')
				self.cog.find('**/hands').setColor(0.95,0.75,0.95,1)
				self.scale = 1
				self.setSellTexture()
				
			elif self.randomNumber == 12:
				#mingler
				self.head = self.headList.find('**/twoface')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/mingler.jpg'), 1)
				self.cog.find('**/hands').setColor(0.95,0.75,0.95,1)
				self.scale = 1.1
				self.setSellTexture()
				
			else:
				#double talker
				self.head = self.headList.find('**/twoface')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/double-talker.jpg'), 1)
				self.cog.find('**/hands').setColor(0.75,0.75,0.95,1)
				self.scale = 0.9
				self.setLawTexture()
				
		elif self.randomNumber <= 22:
			#Render the suit B type cogs
			self.cog = Actor(self.pandaDirectory + '/resources/cogs/models/tt_a_ene_cgb_zero.bam',{
						'neutral':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgb_neutral.bam'),
						'walk':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgb_walk.bam'),
						'finger wag':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgb_finger-wag.bam'),
						'landing':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgb_landing.bam'),
						'hit':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgb_pie-small.bam')
						})
						
			self.headList = loader.loadModel(self.pandaDirectory + '/resources/cogs/models/suitB-heads.bam')
			
			if self.randomNumber == 14:
				self.head = self.headList.find('**/ambulancechaser')
				self.cog.find('**/hands').setColor(0.75,0.75,0.95,1)
				self.scale = 1
				self.setLawTexture()
				
			elif self.randomNumber == 15:
				self.head = self.headList.find('**/beancounter')
				self.cog.find('**/hands').setColor(0.65,0.95,0.85,1)
				self.scale = 0.9
				self.setCashTexture()
			
			elif self.randomNumber == 16:
				#downsizer
				self.head = self.headList.find('**/beancounter')
				self.cog.find('**/hands').setColor(0.95,0.75,0.75,1)
				self.scale = 0.9
				self.setBossTexture()
				
			elif self.randomNumber == 17:
				self.head = self.headList.find('**/loanshark')
				self.cog.find('**/hands').setColor(0.65,0.95,0.85,1)
				self.scale = 1.3
				self.setCashTexture()
				
			elif self.randomNumber == 18:
				self.head = self.headList.find('**/movershaker')
				self.cog.find('**/hands').setColor(0.95,0.75,0.95,1)
				self.scale = 1
				self.setSellTexture()
				
			elif self.randomNumber == 19:
				#bloodsucker
				self.head = self.headList.find('**/movershaker')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/blood-sucker.jpg'), 1)
				self.scale = 0.8
				self.setLawTexture()
				
			elif self.randomNumber == 20:
				self.head = self.headList.find('**/pencilpusher')
				self.cog.find('**/hands').setColor(0.95,0.75,0.75,1)
				self.scale = 0.8
				self.setBossTexture()
				
			elif self.randomNumber == 21:
				self.head = self.headList.find('**/telemarketer')
				self.cog.find('**/hands').setColor(0.95,0.75,0.95,1)
				self.scale = 0.8
				self.setSellTexture()
				
			else:
				#spin doctor
				self.head = self.headList.find('**/telemarketer')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/spin-doctor.jpg'), 1)
				self.cog.find('**/hands').setColor(0.65,0.95,0.85,1)
				self.scale = 1.1
				self.setLawTexture()
			
		elif self.randomNumber <= 31:
			#Render the suit C type cogs
			self.cog = Actor(self.pandaDirectory + '/resources/cogs/models/tt_a_ene_cgc_zero.bam',{
						'neutral':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgc_neutral.bam'),
						'walk':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgc_walk.bam'),
						'finger wag':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgc_finger-wag.bam'),
						'landing':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgc_landing.bam'),
						'hit':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgc_pie-small.bam')
						})
						
			self.headList = loader.loadModel(self.pandaDirectory + '/resources/cogs/models/suitC-heads.bam')
			
			if self.randomNumber == 23:
				#actually a short change
				self.head = self.headList.find('**/coldcaller')
				self.cog.find('**/hands').setColor(0.65,0.95,0.85,1)
				self.scale = 1.1
				self.setCashTexture()
				
			elif self.randomNumber == 24:
				#cold caller needs to be recolored
				self.head = self.headList.find('**/coldcaller')
				self.head.setColor(0, 0, 255, 1)
				self.cog.find('**/hands').setColor(0.09,0.48,0.95,1)
				self.scale = 1.1
				self.setSellTexture()
				
			elif self.randomNumber == 25:
				self.head = self.headList.find('**/flunky')
				self.glasses = self.headList.find('**/glasses')
				self.glasses.reparentTo(self.head)
				self.cog.find('**/hands').setColor(0.95,0.75,0.75,1)
				self.scale = 1.1
				self.setBossTexture()
				
			elif self.randomNumber == 26:
				#corporate raider
				self.head = self.headList.find('**/flunky')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/corporate-raider.jpg'), 1)
				self.cog.find('**/hands').setColor(0.98,0.55,0.56,1)
				self.scale = 1.7
				self.setBossTexture()
				
			elif self.randomNumber == 27:
				self.head = self.headList.find('**/gladhander')
				self.cog.find('**/hands').setColor(0.95,0.75,0.95,1)
				self.scale = 1.2
				self.setSellTexture()
				
			elif self.randomNumber == 28:
				self.head = self.headList.find('**/micromanager')
				self.cog.find('**/hands').setColor(0.95,0.75,0.75,1)
				self.scale = 0.7
				self.setBossTexture()
				
			elif self.randomNumber == 29:
				self.head = self.headList.find('**/moneybags')
				self.cog.find('**/hands').setColor(0.65,0.95,0.85,1)
				self.scale = 1.5
				self.setCashTexture()
				
			elif self.randomNumber == 30:
				self.head = self.headList.find('**/tightwad')
				self.cog.find('**/hands').setColor(0.65,0.95,0.85,1)
				self.scale = 1.3
				self.setCashTexture()
				
			else:
				#bottom feeder
				self.head = self.headList.find('**/tightwad')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/bottom-feeder.jpg'), 1)
				self.cog.find('**/hands').setColor(0.75,0.75,0.95,1)
				self.scale = 1.1
				self.setLawTexture()
		else:
			raise Exception('UH OH! randomNumber is not between 0 and 31! The value of randomNumber is {}'.format(self.randomNumber))

	def setSellTexture(self):
		#Set the suit texture to the Sellbot texture
		self.cog.findAllMatches('**/torso').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/s_blazer.jpg'), 1)
		
		self.cog.findAllMatches('**/arms').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/s_sleeve.jpg'), 1)
		
		self.cog.findAllMatches('**/legs').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/s_leg.jpg'), 1)
	
	def setCashTexture(self):
		#Set the suit texture to the Cashbot texture
		self.cog.findAllMatches('**/torso').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/m_blazer.jpg'), 1)
		
		self.cog.findAllMatches('**/arms').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/m_sleeve.jpg'), 1)
		
		self.cog.findAllMatches('**/legs').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/m_leg.jpg'), 1)
		
	def setLawTexture(self):
		#Set the suit texture to the Lawbot texture
		self.cog.findAllMatches('**/torso').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/l_blazer.jpg'), 1)
		
		self.cog.findAllMatches('**/arms').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/l_sleeve.jpg'), 1)
		
		self.cog.findAllMatches('**/legs').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/l_leg.jpg'), 1)
	
	def setBossTexture(self):
		#Set the suit texture to the Bossbot texture
		self.cog.findAllMatches('**/torso').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/c_blazer.jpg'), 1)
		
		self.cog.findAllMatches('**/arms').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/c_sleeve.jpg'), 1)
		
		self.cog.findAllMatches('**/legs').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/c_leg.jpg'), 1)
