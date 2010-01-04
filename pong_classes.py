# -*- coding: utf-8 -*-
# Class definitions
import math, socket, random

## kommt in den server!!1111oenoenone


class log_queue(object):
	def __init__(self):
		self.items=[] # item=[text,duration,age,begin]
		self.log_offset = 0
	
	def append(self,text,duration,begin):
		self.items.append([text,duration,0,begin])
	
	def age_up(self):
		for item in self.items:
			if item[2]+1<=item[1]: item[2]+=1
			else: del(item)
		
	def action(self,frame,font,surface):
		self.age_up()
		anz=0				
		if self.log_offset>0: self.log_offset-=1
		for item in self.items:
			if item[3]<=frame:
				item[2]+=1
			if item[3]+item[1]>=frame:
				al=int((1.0-(item[2]*1.0/item[1]))*255)
				if al<0:
					al=0			
				text=font.render(item[0], True,(255,255,255),(0,0,0))
				text.set_alpha(al)
				surface.blit(text,(10,10+anz*20+self.log_offset))
				anz+=1
				if al==0:
					self.log_offset=font.size("Hallo")[1]
					anz-=1
					del(item)


class Particle(object):
	def __init__(self,pos,speed,surface,life):
		self.x=pos[0]
		self.y=pos[1]
		self.xs=speed[0]
		self.ys=speed[1]
		self.surface=surface#.copy()
		self.life=life
        
	def paint(self,surface):
		surface.blit(self.surface,(self.x,self.y))
		return surface

	def slower(self,fac):
		self.xs*=(1-fac)
		self.ys*=(1-fac)
		return (self.xs,self.ys)

	def fall(self,fac):
		self.ys=self.ys+fac
		return self.ys

	def move(self):
		self.x+=self.xs
		self.y+=self.ys

	def altern(self,zeit=1):
		self.life-=zeit
		return self.life

	def action(self,surface):
		if self.life>0:
			self.altern()
			self.slower(0.01)
			self.fall(0)#.1
			self.move()
			self.paint(surface)


class Ball(object):
	"""There should only be one ball in the game at any given time."""
	def __init__(self,d):
		self.x=0.5
		self.y=0.5
		self.d=d
		self.speedx=0
		self.speedy=0
		self.raus = True
		self.lastbounce = 0
		self.nextbounce = 0
	
	def set_speed(self, speedx, speedy):
		self.speedx = speedx
		self.speedy = speedy
	
	def change_speed(self, fac):
		if self.speedx > 0: self.speedx += fac
		elif self.speedx < 0: self.speedx -= fac
		if self.speedy > 0: self.speedy += fac
		elif self.speedy < 0: self.speedy -= fac
		return (self.speedx, self.speedy)
	

	def move(self):
		self.x += self.speedx
		self.y += self.speedy
	
	def check_out(self):
		erg = 0
		if  self.x < 0.01: erg = 1
		elif self.y < 0.01: erg = 3
		elif self.x+self.d > 0.99: erg = 2
		elif self.y+self.d > 0.99: erg = 4
		if erg!=0 and self.nextbounce!=erg and self.nextbounce == 0: self.reset()
		return erg
		
	def reset(self):
		self.x = 0.5
		self.y = 0.5
		self.speedx = 0.006
		self.speedy = 0.006
		self.rotate(random.randint(0,359))
		self.lastbounce = 0
		self.nextbounce = 0
		
		
	def rotate(self, angle_degrees):
		radians = math.radians(angle_degrees)
		cos = math.cos(radians)
		sin = math.sin(radians)
		x = self.speedx*cos - self.speedy*sin
		y = self.speedx*sin + self.speedy*cos
		self.speedx = x
		self.speedy = y	
	
	
	def bounce(self,pposes, do=True):
		posi = 1
		erg = 0
		
		if self.nextbounce != 0:
			self.lastbounce = self.nextbounce
			self.nextbounce = 0
			return self.lastbounce
		else:
			for ppos in pposes:
				if pposes != None and self.lastbounce!=posi and self.speedx*self.speedy!=0:					
					if posi == 1:
						cut_y = self.y + (self.speedx * self.x)/self.speedy
						if cut_y >= ppos and cut_y <= ppos+0.15 and self.x<=0.02:
							self.nextbounce = 1
							self.speedx=-self.speedx
					
					if posi == 2:

						cut_y = self.y + self.speedy * (1-self.x)/self.speedy
						if cut_y >= ppos and cut_y <= ppos+0.15 and self.x+self.d>=0.98:
							self.nextbounce = 2
							self.speedx=-self.speedx
					
					
					if posi == 3:
						cut_x = self.x + (self.speedy * self.y)/self.speedx# + self.x
						if cut_x >= ppos and cut_x <= ppos+0.15 and self.y<=0.02:
							self.nextbounce = 3
							self.speedy=-self.speedy
					
					if posi == 4:
						cut_x = self.x + (self.speedy * (1-self.y))/self.speedx# + self.x
						if cut_x >= ppos and cut_x <= ppos+0.15 and self.y+self.d>=0.98:
							self.nextbounce = 4
							self.speedy=-self.speedy		
					
					#drehen
					if posi <3: bdis = self.x
					else: bdis = self.y
					dif = bdis-ppos+0.75
					if self.nextbounce != 0:
						self.rotate(dif)
					
				posi+=1
			
			return False

# end class 'Ball'


class Player(object):
	"""There are four players"""
	def __init__(self,position=1, typ=1, width=0.1, thickness=0.01):
		self.position=position  # 1=links 2=rechts 3=0ben 4=unten
		self.size=width
		self.distance=0.5-width/2.0
		self.typ=typ #typ: 0-Player 1-Bot 2-Wall
		self.thickness=thickness
			
		# abstand zum ran_d=0.01
		# größe des pedals: size
		# breite des pedals: 0.01

	
	def move(self,direction=0):
		if self.position<=2:
			self.y+=direction
		else:
			self.x+=direction
			
		self.range_check()

	def range_check(self):
		if self.distance<0: 
			self.distance=0
		if self.distance+self.size>1: 
			self.distance=1.0-self.size
			
	def draw(self,surface,paddle,SIZE):
		pos=self.position
		dist=self.distance
		x=0
		y=0
		if pos==1:
			x=0.01*SIZE
			y=dist*SIZE
		elif pos==2:
			x=0.98*SIZE
			y=dist*SIZE
		elif pos==3:
			x=dist*SIZE
			y=0.01*SIZE
		elif pos==4:
			x=dist*SIZE
			y=0.98*SIZE
		surface.blit(paddle,(x,y))

# end class 'Player'
