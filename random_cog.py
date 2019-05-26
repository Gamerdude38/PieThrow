'''
John Maurer

Description: A class that generates a random cog model, renders it, and
defines its animations
'''

from direct.actor.Actor import Actor
from direct.interval.LerpInterval import LerpPosInterval,LerpHprInterval
from direct.interval.ActorInterval import ActorInterval
from direct.interval.IntervalGlobal import *
from panda3d.core import *
import sys,os
import random

class RandomCog():
	def __init__(self):
		#Define variables for the cog's health and speed
		self.health = 5
		self.speed = 1
		
		#Establish current file path location
		self.currentDirectory = os.path.abspath(sys.path[0])
		self.pandaDirectory = Filename.fromOsSpecific(self.currentDirectory).getFullpath()
		
		#Generate a random number between 0 and 31 inclusive to select a cog
		self.randomNumber = random.randint(0, 32)
		
		#Num cogs in suits
		#A - 14
		#B - 9
		#C - 9
		
		#Define boolean for flunky glasses
		self.hasGlasses = False
		
		if self.randomNumber <= 13:
			#Render the suit A type cogs
			self.cog = Actor(self.pandaDirectory + '/resources/cogs/models/tt_a_ene_cga_zero.bam',{
						'neutral':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cga_neutral.bam'),
						'walk':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cga_walk.bam'),
						'finger wag':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cga_finger-wag.bam'),
						'landing':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cga_landing.bam')
						})
			
			self.headList = loader.loadModel(self.pandaDirectory + '/resources/cogs/models/suitA-heads.bam')
			
			if self.randomNumber == 0:
				self.head = self.headList.find('**/backstabber')
				self.cog.find('**/hands').setColor(223,193,231)
				self.cog.setScale(0.7)
				self.setLawTexture()
				
			elif self.randomNumber == 1:
				self.head = self.headList.find('**/bigcheese')
				self.cog.find('**/hands').setColor(180,249,164)
				self.cog.setScale(1)
				self.setBossTexture()
				
			elif self.randomNumber == 2:
				self.head = self.headList.find('**/bigwig')
				self.cog.find('**/hands').setColor(223,193,231)
				self.cog.setScale(1)
				self.setLawTexture()
				
			elif self.randomNumber == 3:
				self.head = self.headList.find('**/headhunter')
				self.cog.find('**/hands').setColor(253,172,173)
				self.cog.setScale(0.85)
				self.setBossTexture()
				
			elif self.randomNumber == 4:
				self.head = self.headList.find('**/legaleagle')
				self.cog.find('**/hands').setColor(89,54,123)
				self.cog.setScale(0.9)
				self.setLawTexture()
				
			elif self.randomNumber == 5:
				self.head = self.headList.find('**/numbercruncher')
				self.cog.find('**/hands').setColor(133,244,180)
				self.cog.setScale(0.8)
				self.setCashTexture()
				
			elif self.randomNumber == 6:
				#name dropper
				self.head = self.headList.find('**/numbercruncher')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/name-dropper.jpg'), 1)
				self.cog.find('**/hands').setColor(248,176,216)
				self.cog.setScale(0.7)
				self.setSellTexture()
				
			elif self.randomNumber == 7:
				self.head = self.headList.find('**/pennypincher')
				self.cog.find('**/hands').setColor(251,140,144)
				self.cog.setScale(0.6)
				self.setCashTexture()
				
			elif self.randomNumber == 8:
				self.head = self.headList.find('**/yesman')
				self.cog.find('**/hands').setColor(253,172,173)
				self.cog.setScale(0.7)
				self.setBossTexture()
				
			elif self.randomNumber == 9:
				#robber baron
				self.head = self.headList.find('**/yesman')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/robber-baron.jpg'), 1)
				self.cog.find('**/hands').setColor(133,244,180)
				self.cog.setScale(1)
				self.setCashTexture()
				
			elif self.randomNumber == 10:
				#mr. hollywood
				self.head = self.headList.find('**/yesman')
				self.cog.find('**/hands').setColor(248,176,216)
				self.cog.setScale(1)
				self.setSellTexture()
				
			elif self.randomNumber == 11:
				self.head = self.headList.find('**/twoface')
				self.cog.find('**/hands').setColor(248,176,216)
				self.cog.setScale(0.8)
				self.setSellTexture()
				
			elif self.randomNumber == 12:
				#mingler
				self.head = self.headList.find('**/twoface')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/mingler.jpg'), 1)
				self.cog.find('**/hands').setColor(248,176,216)
				self.cog.setScale(0.85)
				self.setSellTexture()
				
			else:
				#double talker
				self.head = self.headList.find('**/twoface')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/double-talker.jpg'), 1)
				self.cog.find('**/hands').setColor(223,193,231)
				self.cog.setScale(0.7)
				self.setLawTexture()
				
				
		elif self.randomNumber <= 22:
			#Render the suit B type cogs
			self.cog = Actor(self.pandaDirectory + '/resources/cogs/models/tt_a_ene_cgb_zero.bam',{
						'neutral':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgb_neutral.bam'),
						'walk':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgb_walk.bam'),
						'finger wag':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgb_finger-wag.bam'),
						'landing':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgb_landing.bam')
						})
						
			self.headList = loader.loadModel(self.pandaDirectory + '/resources/cogs/models/suitB-heads.bam')
			
			if self.randomNumber == 14:
				self.head = self.headList.find('**/ambulancechaser')
				self.cog.find('**/hands').setColor(223,193,231)
				self.cog.setScale(0.8)
				self.setLawTexture()
				
			elif self.randomNumber == 15:
				self.head = self.headList.find('**/beancounter')
				self.cog.find('**/hands').setColor(133,244,180)
				self.cog.setScale(0.7)
				self.setCashTexture()
			
			elif self.randomNumber == 16:
				self.head = self.headList.find('**/beancounter')
				self.cog.find('**/hands').setColor(253,172,173)
				self.cog.setScale(0.8)
				self.setBossTexture()
				
			elif self.randomNumber == 17:
				self.head = self.headList.find('**/loanshark')
				self.cog.find('**/hands').setColor(133,244,180)
				self.cog.setScale(1)
				self.setCashTexture()
				
			elif self.randomNumber == 18:
				self.head = self.headList.find('**/movershaker')
				self.cog.find('**/hands').setColor(248,176,216)
				self.cog.setScale(0.8)
				self.setSellTexture()
				
			elif self.randomNumber == 19:
				#bloodsucker
				self.head = self.headList.find('**/movershaker')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/blood-sucker.jpg'), 1)
				self.cog.setScale(0.6)
				self.setLawTexture()
				
			elif self.randomNumber == 20:
				self.head = self.headList.find('**/pencilpusher')
				self.cog.find('**/hands').setColor(253,172,173)
				self.cog.setScale(0.6)
				self.setBossTexture()
				
			elif self.randomNumber == 21:
				self.head = self.headList.find('**/telemarketer')
				self.cog.find('**/hands').setColor(248,176,216)
				self.cog.setScale(0.6)
				self.setSellTexture()
				
			else:
				#spin doctor
				self.head = self.headList.find('**/telemarketer')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/spin-doctor.jpg'), 1)
				self.cog.find('**/hands').setColor(133,244,180)
				self.cog.setScale(0.9)
				self.setLawTexture()
			
		elif self.randomNumber <= 31:
			#Render the suit C type cogs
			self.cog = Actor(self.pandaDirectory + '/resources/cogs/models/tt_a_ene_cgc_zero.bam',{
						'neutral':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgc_neutral.bam'),
						'walk':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgc_walk.bam'),
						'finger wag':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgc_finger-wag.bam'),
						'landing':(self.pandaDirectory + '/resources/cogs/animations/tt_a_ene_cgc_landing.bam')
						})
						
			self.headList = loader.loadModel(self.pandaDirectory + '/resources/cogs/models/suitC-heads.bam')
			
			if self.randomNumber == 23:
				#actually a short change
				self.head = self.headList.find('**/coldcaller')
				self.cog.find('**/hands').setColor(133,244,180)
				self.cog.setScale(0.8)
				self.setCashTexture()
				
			elif self.randomNumber == 24:
				#cold caller needs to be recolored
				self.head = self.headList.find('**/coldcaller')
				self.head.setColor(0, 0, 255, 1)
				self.cog.find('**/hands').setColor(22,123,241)
				self.cog.setScale(0.8)
				self.setSellTexture()
				
			elif self.randomNumber == 25:
				self.head = self.headList.find('**/flunky')
				hasGlasses = True
				self.cog.find('**/hands').setColor(253,172,173)
				self.cog.setScale(0.8)
				self.setBossTexture()
				
			elif self.randomNumber == 26:
				#corporate raider
				self.head = self.headList.find('**/flunky')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/corporate-raider.jpg'), 1)
				self.cog.find('**/hands').setColor(253,152,153)
				self.cog.setScale(1.2)
				self.setBossTexture()
				
			elif self.randomNumber == 27:
				self.head = self.headList.find('**/gladhander')
				self.cog.find('**/hands').setColor(248,176,216)
				self.cog.setScale(1)
				self.setSellTexture()
				
			elif self.randomNumber == 28:
				self.head = self.headList.find('**/micromanager')
				self.cog.find('**/hands').setColor(253,172,173)
				self.cog.setScale(0.5)
				self.setBossTexture()
				
			elif self.randomNumber == 29:
				self.head = self.headList.find('**/moneybags')
				self.cog.find('**/hands').setColor(133,244,180)
				self.cog.setScale(1.1)
				self.setCashTexture()
				
			elif self.randomNumber == 30:
				self.head = self.headList.find('**/tightwad')
				self.cog.find('**/hands').setColor(133,244,180)
				self.cog.setScale(0.9)
				self.setCashTexture()
				
			else:
				#bottom feeder
				self.head = self.headList.find('**/tightwad')
				self.head.setTexture(loader.loadTexture(self.pandaDirectory + \
									'/resources/cogs/textures/bottom-feeder.jpg'), 1)
				self.cog.find('**/hands').setColor(223,193,231)
				self.cog.setScale(0.8)
				self.setLawTexture()
		else:
			raise Exception('UH OH! randomNumber is not between 0 and 31! The value of randomNumber is {}'.format(self.randomNumber))
		
		#Render the head and actor
		self.cog.reparentTo(render)
		self.head.reparentTo(self.cog.find('**/def_head'))
		
		if self.hasGlasses:
			self.glasses = self.headList.find('**/glasses')
			self.glasses.reparentTo(self.head)
		
		self.lifeMeter = loader.loadModel(self.pandaDirectory + '/resources/cogs/models/cog_life_meter.bam')
		self.lifeMeter.reparentTo(self.cog.find('**/def_joint_attachMeter'))
		self.lifeMeter.setHpr(180, 0, 0)
		self.lifeMeter.setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/cog-life-meter-big.png'))
		
		self.cog.loop('neutral')
		
		
	def setSellTexture(self):
		self.cog.findAllMatches('**/torso').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/s_blazer.jpg'), 1)
		
		self.cog.findAllMatches('**/arms').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/s_sleeve.jpg'), 1)
		
		self.cog.findAllMatches('**/legs').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/s_leg.jpg'), 1)
	
	def setCashTexture(self):
		self.cog.findAllMatches('**/torso').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/m_blazer.jpg'), 1)
		
		self.cog.findAllMatches('**/arms').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/m_sleeve.jpg'), 1)
		
		self.cog.findAllMatches('**/legs').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/m_leg.jpg'), 1)
		
	def setLawTexture(self):
		self.cog.findAllMatches('**/torso').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/l_blazer.jpg'), 1)
		
		self.cog.findAllMatches('**/arms').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/l_sleeve.jpg'), 1)
		
		self.cog.findAllMatches('**/legs').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/l_leg.jpg'), 1)
	
	def setBossTexture(self):
		self.cog.findAllMatches('**/torso').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/c_blazer.jpg'), 1)
		
		self.cog.findAllMatches('**/arms').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/c_sleeve.jpg'), 1)
		
		self.cog.findAllMatches('**/legs').setTexture(loader.loadTexture(self.pandaDirectory + '/resources/cogs/textures/c_leg.jpg'), 1)
