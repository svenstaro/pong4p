# -*- coding: utf-8 -*-

import pygame 
pygame.font.init()
MENUFONT=pygame.font.SysFont("Verdana",12,True)


class GameMenu(object):
	"""This class defines all methods and attributes used to create a game menu."""
	def __init__(self,x=0,y=0,style=None):
		self.buttons=[]
		self.fields=[]
		self.x=x
		self.y=y
		self.style=style

	def check_buttons(self,mouse,checkSubs=True):
		do = True
		for f in self.fields:
			if f.active:
				do = False
		
		if do:
			lastbutton='nobuttonpressed'
			for button in self.get_buttons():
				if button.check_over(mouse[0]-self.x,mouse[1]-self.y):
					lastbutton=button.label
					for button2 in self.get_buttons():
						if button2 is not button:
							button2.set_submenu_stat(False)
					button.set_submenu_stat(True)			
				elif checkSubs and button.get_submenu_stat():
					zwischen=button.submenu.check_buttons(mouse)
					if zwischen!='nobuttonpressed':
						lastbutton=zwischen
						break
			return lastbutton
		else:
			return -1
			
			
	def click_fields(self,mouse):
		x=self.x
		y=self.y
		act = False
		for f in self.fields:
			if f.active:
				act = True
		
		for f in self.fields:
			if f.active and f.type=="pulldown":
				f.click_subs(mouse,(x,y))
			
			if not act:
				if mouse[0]>f.x+x and mouse[0]<f.x+x+f.width and mouse[1]>f.y+y and mouse[1]<f.y+f.height+y:
					f.setActive(not f.active)
				else:
					f.setActive(False)
			else:
				f.setActive(False)
					

		for b in self.buttons:
			if b.get_submenu_stat():
				b.submenu.click_fields(mouse)

	def toggle_fields(self):
		for f in self.fields:
                        if f is TextField:
                                f.toggleCursor()
		for b in self.buttons:
			b.submenu.toggle_fields()

	def key_down(self,uc,extra=None):
		for f in self.fields:
			if f.active:
				f.write(uc,extra)
		for b in self.buttons:
			if b.get_submenu_stat():
				b.submenu.key_down(uc,extra)

	def set_pos(self, pos=(0,0)):
		self.x=pos[0]
		self.y=pos[1]

	def add_button(self,button):
		self.buttons.append(button)

	def add_field(self,field):
		self.fields.append(field)

	def get_buttons(self):
		return self.buttons

	def get_fields(self):
		return self.fields

	def get_size(self,rand=10):
		width = 0
		height = 0
		for f in self.fields:
			if f.width + f.x +2*rand > width: width = f.width + f.x +2*rand
			if f.height + f.y +2*rand > height: height = f.height + f.y +2*rand
		
		for b in self.buttons:
			if b.width + b.x +2*rand > width: width = b.width + b.x +2*rand
			if b.height + b.y +2*rand > height: height = b.height + b.y +2*rand
		
		return (width,height)

	def draw(self, surface, mouse=(0,0)):
		x=self.x
		y=self.y
		if not(self.style==None):
			border = self.style[2]
			w, h = self.get_size(self.style[3]) 
			bbox = pygame.Surface((w,h)).convert()
			box = pygame.Surface((w-2*border,h-2*border)).convert()
			bbox.fill(self.style[1])
			box.fill(self.style[0])
			bbox.blit(box,(border,border))
			surface.blit(bbox,(x-self.style[3],y-self.style[3]))
		
		for button in self.buttons:
			hover = True
			for f in self.fields:
				if f.active:
					hover = False
			box=button.draw((mouse[0]-self.x,mouse[1]-self.y),hover)
			surface.blit(box,(button.x+x,button.y+y))
#mit hover: if (button.check_over(mouse[0]-self.x,mouse[1]-self.y) or button.get_submenu_stat()) and button.submenu!=0:
			if button.get_submenu_stat():
				button.draw_submenu(surface,mouse)

		for field in self.fields:
			m=mouse
			for f in self.fields:
				if f.active:
					m=(-100,-100)
			field.draw(surface,m,(x,y))

		for f in self.fields:
			if f.active and f.type=="pulldown":
				f.draw_choice(surface,mouse,(x,y))
			
			
		return surface
# end class 'GameMenu'


class MenuButton(object):
	"""This class is used to create a single instance of a menu button."""
	def __init__(self, style, label, x=0, y=0,  width=170, height=40, submenu=0):
		self.label = label
		self.style = style
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.submenu=submenu
		self.nosub=False
		if self.submenu==0:
			self.submenu=GameMenu()
			self.nosub=True
		self.submenu_status=False

	def check_over(self,mouseX,mouseY):
		erg=False
		if self.x <= mouseX and self.x+self.width>=mouseX and self.y <=mouseY and self.y+self.height>=mouseY:
			erg=True
		return erg

	def set_submenu_stat(self, status=False):
		self.submenu_status=status
		if status==False:
			for button in self.submenu.get_buttons():
				button.set_submenu_stat(False)
		return self.submenu_status

	def get_submenu_stat(self):
		return self.submenu_status

	def draw(self, mouse, hover):	
		w=self.width
		s = self.style
		border = self.style[3]
		if (self.submenu_status and not self.nosub): state = 1		#active
		elif self.check_over(mouse[0],mouse[1]) and hover: state = 2	#hover
		else: state = 0							#normal

		box = pygame.Surface((w-2*border,self.height-2*border)).convert()
		bigbox = pygame.Surface((w,self.height)).convert()
		box.fill(s[0][state])
		bigbox.fill(s[2][state])
		fontcolor=s[1][state]
		
		box.blit(s[4].render(self.label, True, fontcolor),(10,(self.height-2*border)/2-s[4].size("lol")[1]/2+border))
		bigbox.blit(box,(border,border))

		return bigbox

	def draw_submenu(self, surface,mouse=(0,0)):
		surface=self.submenu.draw(surface,mouse)
		return surface
# end class 'MenuButton'


class TextField(object):
	def __init__(self,style,label,text,x=0,y=0,width=200,height=20):
		self.label=label
		self.style=style
		self.text=text
		self.x=x
		self.y=y
		self.width=width
		self.height=height
		self.font=style[4]
		self.active=False
		self.cursor="_"
		self.type="text"

	def setActive(self,state=True):
		self.active=state
	
	def check_over(self,surf,mouse,move=(0,0)):	
		return self.x+move[0] < mouse[0] and self.x+self.width+move[0]>mouse[0] and self.y+move[1] <mouse[1] and self.y+self.height+move[1]>=mouse[1]

	def toggleCursor(self):
		if self.cursor=="_": self.cursor=""
		else: self.cursor="_"

	def write(self,text,extra=None):
		if extra==None: self.text+=text
		elif extra == "back":
			self.text=self.text[:-1]
		
	
	def draw(self,surf,mouse,move=(0,0)):
		s = self.style
		border = s[3]
		bbox=pygame.Surface((self.width,self.height)).convert()
		box=pygame.Surface((self.width-2*border,self.height-2*border)).convert()

		if self.active: state = 1
		elif self.check_over(mouse,move): state = 2
		else: state = 0
		
		c = ""
		if self.active: c = self.cursor
		
		box.fill(s[0][state])
		bbox.fill(s[2][state])
		
		box.blit(self.style[4].render(self.label+": "+self.text+c,True,s[1][state]),(10,(self.height)/2-s[4].size("lol")[1]/2))
		bbox.blit(box,(border,border))
		surf.blit(bbox,(self.x+move[0],self.y+move[1]))
		return surf

	def draw_choice(self,surf,mouse,move=(0,0)):
		pass

class PullDownMenu(object):
	def __init__(self,style,label,text,items=[],x=0,y=0,width=200,height=20):
		self.label=label
		self.style=style
		self.text=text
		self.x=x
		self.y=y
		self.width=width
		self.height=height
		self.font=style[4]
		self.items=items
		self.active=True
		self.type="pulldown"
	
	def check_over(self,mouse,move):
		return self.x+move[0] < mouse[0] and self.x+self.width+move[0]>mouse[0] and self.y+move[1] <mouse[1] and self.y+self.height+move[1]>=mouse[1]

	def setActive(self,state=True):
		self.active=state
	
	def get_Size_All(self):
		size_all=[0,0]
		for item in self.items:
			size=self.font.size(item)
			size_all[1]+=size[1]+2*self.style[3]
		size_all[0] = self.width - self.font.size(self.label+": ")[0] -10
		return size_all
	
	def draw(self,surf,mouse,move=(0,0)):
		s = self.style
		border = s[3]
		bbox=pygame.Surface((self.width,self.height)).convert()
		box=pygame.Surface((self.width-2*border,self.height-2*border)).convert()
		if self.active: state=1
		elif self.check_over(mouse,move): state = 2
		else: state = 0
		box.fill(s[0][state])
		bbox.fill(s[2][state])
		box.blit(self.font.render(self.label+": "+self.text,True,s[1][state]),(10,(self.height)/2-s[4].size("lol")[1]/2))
		bbox.blit(box,(border,border))
		surf.blit(bbox,(self.x+move[0],self.y+move[1]))


	def draw_choice(self,surf,mouse,move=(0,0)):				
		s = self.style
		border = s[3]
		if self.active:
			size_all=self.get_Size_All()
			rand=pygame.Surface((size_all[0]+2*border,size_all[1]+2*border)).convert()
			rand.fill(s[2][0])
			box2=pygame.Surface((size_all[0],size_all[1])).convert()
			box2.fill(s[0][0])
			i=0
			height=self.font.size("Empty")[1]
			x_off=self.font.size(self.label+": ")[0]+10
			for item in self.items:
				size=self.font.size(item)
				if mouse[0]>self.x+move[0]+x_off-10 and mouse[0]<self.x+move[0]+x_off-10+size_all[0] and mouse[1]>self.y+move[1]+self.height+i*(height+2*border) and mouse[1]<self.y+move[1]+self.height+i*(height+2*border)+size[1]+border:
					cl=s[1][2]
					bg=s[0][2]
					backgr = pygame.Surface((size_all[0],size[1]+2*border)).convert()
					backgr.fill(bg)
					box2.blit(backgr,(0,i*(height+2*border)))
				else:
					cl=s[1][0]
					bg=s[0][0]
				box2.blit(self.font.render(item,True,cl),(10,i*(height+2*border)+border))
				i+=1
			
			surf.blit(rand,(self.x+move[0]+x_off-2*border,self.y+move[1]+self.height))
			surf.blit(box2,(self.x+move[0]+x_off-border,self.y+move[1]+self.height+border))
		
		return surf
		
	def click_subs(self,mouse,move=(0,0)):
		border = self.style[3]
		if self.active:
			size_all=self.get_Size_All()
			i=0
			height=self.font.size("Empty")[1]
			x_off=self.font.size(self.label+": ")[0]
			for item in self.items:
				size=self.font.size(item)
				if mouse[0]>self.x+move[0]+x_off-10 and mouse[0]<self.x+move[0]+x_off-10+size_all[0] and mouse[1]>self.y+move[1]+self.height+i*(height+2*border) and mouse[1]<self.y+move[1]+self.height+i*(height+2*border)+size[1]+border:
					
					self.active=False
					self.text = item
					
				i+=1




class JpgAnimation(object):
	def __init__(self,url,anz,format="jpg",digits = None):
		self.url = url
		self.anz = anz
		self.format = format
		self.images = [None]*anz
		self.digits = digits
	
	def load(self, num):
		num = str(num)
		if digits != None and len(num)<self.digits:
			num = "0"*(self.digits - len(num)) +num
		self.images[num] = pygame.image.load(self.url+num+"."+format).convert_alpha()
	
	def load_all(self,scale = True):
		i=0
		for img in self.images:
			self.load(i)
			i+=1
		
	def scale(self,RES=(800,620)):
		for i in xrange(len(self.images)):
			self.images[i] = pygame.transform.smoothscale(self.images[i],RES)


