#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
import sys
import random
import math
import subprocess
from tools import *
from pong_classes import *
from menu_classes import *
#import net
import socket

VERSION = 0.1
CLIENT_PORT = 13258
CLIENT_FPS = 60
DEBUG = False


class Client(object):
	def __init__(self, port=13258, dest_ip="localhost", fps=60, debug=False):
		self.port = port
		self.dest_ip = dest_ip
		self.fps = fps
		self.debug = debug
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setblocking(0)
		self.player = []
		self.cl_uuid = 0 # entspricht der playerpos
		self.pedal_lag=4.0
		self.player_size = 0.15
		self.player_thickness = 0.012
		self.lasttext = ""
		self.msid = 0
		self.show_text = False
		self.lastbounce = 0
		self.newbounce = 0

	def handshake(self,name):
		""" 
		Exchange initial information with the server:
		PADEL_LAG:VALUE,
		PLAYER_SIZE:VALUE,
		PLAYER_THICKNESS:VALUE
		PLAYER_UUID:VALUE
		MESSAGHE_ID:VALUE
		FINISH:VALUE
		"""
		self.sock.sendto(str(self.cl_uuid)+":"+name,(self.dest_ip, self.port))
		timeout = pygame.time.get_ticks()
		while True:
			if pygame.time.get_ticks() - timeout > 2000:
				sys.exit("ERROR: connection timed out")
			try:
				result = self.sock.recvfrom(1024)
				result = result[0].split(":")
			except:
				continue
			if result[0] == 'PADEL_LAG':
				self.pedal_lag = float(result[1])
			elif result[0] == 'PLAYER_SIZE':
				self.player_size = float(result[1])
			elif result[0] == 'PLAYER_THICKNESS':
				self.player_thickness = float(result[1])
			elif result[0] == 'PLAYER_UUID':
				self.cl_uuid = int(result[1])
			elif result[0] == 'MESSAGE_ID':
				self.msid = int(result[1])
			elif result[0] == 'FINISH':
				return self.cl_uuid, self.pedal_lag, self.player_size, self.player_thickness
			elif result[0] == 'ERROR':
				if result[1] == 'SERVER_FULL':
					sys.exit("The Server is full. Please try again later!")

	def send_own_dist(self, dist):
		self.sock.sendto(str(self.cl_uuid)+":%1.4f" % dist,(self.dest_ip, self.port))
	def send_text(self,text):
		self.sock.sendto(str(self.cl_uuid)+":"+text,(self.dest_ip, self.port))
	def get_text(self):
		if self.show_text:
			self.show_text = False 
			return self.lasttext
		else: return -1
	def retr_dist(self,players,ball):
		try:
			retr = self.sock.recvfrom(1024)[0]
			dists, balldists, text = retr.split(":",2)
			dists = dists.split(",")
			
			for i in xrange(4):
				if i+1!= self.cl_uuid: players[i].distance = float(dists[i])
				
			balldists = balldists.split(",")
			ball.x = float(balldists[0])
			ball.y = float(balldists[1])
			ball.speedx = float(balldists[2])
			ball.speedy = float(balldists[3])
			self.newbounce = int(balldists[4]) #hier data["ball"][3] rein
			msid, text = text.split(",",1)
			self.lasttext = text
			if text[:5] == ".kick":
				if text[-1:] == str(self.cl_uuid): 
					return "kickme"
				else:
					self.lasttext = "Player #"+text[-1:]+" has been kicked from Server!"+str(self.cl_uuid)			
			if msid != self.msid:
				self.show_text = True
				self.msid = msid
		except:
			return -1
	def __del__(self):
		self.sock.sendto(str(self.cl_uuid)+":bye",(self.dest_ip, self.port)) #say goodbye
		self.sock.close()
		del(self.sock)


def calc_position(relmouse,player,playerpos,SIZE,PEDAL_LAG):
	if playerpos>=3: mousedist=(relmouse[0]*1.0)/SIZE
	else: mousedist=(relmouse[1]*1.0)/SIZE
	mousedist-=player.size/2.0
	mousefac=4.0
	player.distance+=(mousedist-player.distance)/PEDAL_LAG
	player.range_check()

def usage(port, clname, destip, debug):
	"""
	This function receives the default values as arguments
	"""
	if "-h" in sys.argv or "--help" in sys.argv:
		print "pong4p",VERSION,"(client), a networked 4-player pong clone."
		print "usage:",sys.argv[0],"[option] ..."
		print "options:"
		print "  -h, --help		this help"
		print "  -p, --port		port for the connection to the server"
		print "  -i, --ip		ip-adress for the connection to the server"
		print "  -n, --name     enter your name"
		print "  -w, --debug	display diagnostic messages"
		
		if debug:
			sys.exit("SUCCESS: server exited cleanly")
		else:
			sys.exit(0)
	if "-p" in sys.argv or "--port" in sys.argv:
		if "-p" in sys.argv:
			port_index = sys.argv.index("-p") + 1
		elif "--port" in sys.argv:
			port_index = sys.argv.index("--port") + 1
		try:
			# see if we were given a valid port
			if int(sys.argv[port_index]) in xrange(1,65535):
				port = int(sys.argv[port_index])
			else: 
				sys.exit("ERROR: invalid port")
		except ValueError:
			sys.exit("ERROR: invalid port")

	if "-n" in sys.argv or "--name" in sys.argv:
		if "-n" in sys.argv:
			clname_index = sys.argv.index("-n") + 1
		if "--name" in sys.argv:
			clname_index = sys.argv.index("--name") + 1
		try:
			# see if we have a valid name
			clname = sys.argv[clname_index][:10]
		except ValueError:
			sys.exit("ERROR: invalid name")
	else:	
		clname = "unset"
		try:
			clname = Config_Loader('.pong4p').getString("name")
		except: pass
		if clname=="unset":
			clname = 'Player'+str(random.randint(1000,9999))
	if "-i" in sys.argv or "--ip" in sys.argv:
		if "-i" in sys.argv:
			destip_index = sys.argv.index("-i") + 1
		if "--ip" in sys.argv:
			destip_index = sys.argv.index("--ip") + 1
		try:
			# see if we were given a valid IP
			tryip = sys.argv[destip_index]
			if valid_ip(tryip) or tryip == "localhost":
				destip = tryip
			else:
				sys.exit("ERROR: invalid ip")
		except ValueError:
			sys.exit("ERROR: invalid ip")
	if "-w" in sys.argv or "--debug" in sys.argv:
		debug = True
		
	Config = Config_Loader('.pong4p')
		
	try: 
		fps = Config.getInteger("FPS")
	except:
		fps = 60
		print "Error in Config File at \"FPS\". Using default."
	try: 
		fullscreen = Config.getBoolean("fullscreen")
	except:
		fullscreen = True
		print "Error in Config File at \"fullscreen\". Using default."
	try: 
		resolution_auto=Config.getBoolean("res_auto")
		if resolution_auto=="auto": resolution = (pygame.display.Info().current_w,pygame.display.Info().current_h)
		else: resolution = (Config.getInteger("width"),Config.getInteger("height"))
	except:
		resolution=(800,600)
		print "Error in Config File at \"fullscreen\". Using default."
	scale=min(resolution[0],resolution[1])-20.0 #float! 
	
	return port, clname, destip, debug, fullscreen, resolution, scale, fps

def create_help(helpsize,helpoffset):
	HELPFONT = pygame.font.Font(pygame.font.match_font("COURIERNEW"), 12)
	helptext = [
	"HILFE",
	"[line]",
	"Chat:",
	".reset     Resets ball and gives it a new speed.",
	".kick <n>  Kicks Player on position <n> from game.",
	".help      Shows this help.",
	"",
	"Credits:",
	"",
	"pong4p client - version "+str(VERSION)
	]
	
	
	helpwindow = pygame.Surface(helpsize)
	helpwindow.fill((0,0,0))
	pygame.draw.rect(helpwindow,(255,255,255),(0,0,helpsize[0],helpsize[1]),3)
	line = 0
	for help in helptext:
		if help == "[line]":
			y = (h+5)*line + 34
			pygame.draw.line(helpwindow, (255,255,255), (20,y) , (helpsize[0]-20,y) , 2)
		else:
			w,h = HELPFONT.size(help)
			helpwindow.blit(HELPFONT.render(help,True,(255,255,255)),(20,(h+5)*line + 30))
		line += 1
	helpwindow.set_alpha(160)
	return helpwindow
	
	

##### INIT CLIENT #####
def init_client():
	port, CLIENT_NAME, cl_host_ip, debug, fullscreen, RES, SIZE, FPS = \
	usage(13258, "player", "localhost", True)
	
	print "Hello",CLIENT_NAME
	
	pygame.init()
	random.seed()

	MAINFONT = pygame.font.Font(pygame.font.match_font("VERDANA"), 10)
	MAINFONT.set_bold(True)

	helpsize = (RES[0]-300,RES[1]-200)
	helpoffset = 150,100
	helpwindow = create_help(helpsize,helpoffset)
	showhelp = False


	log = log_queue()
	log_offset=0

	showmouse = False
	pygame.mouse.set_visible(showmouse)	

	if fullscreen: screen = pygame.display.set_mode(RES, pygame.FULLSCREEN)
	else: screen = pygame.display.set_mode(RES)
	
	done = False
	Client_Pong = Client(port, cl_host_ip, FPS, debug)
	playerpos, PEDAL_LAG, PLAYER_SIZE, PLAYER_THICKNESS = Client_Pong.handshake(CLIENT_NAME)
	players = []
	paddles = []
	funken = []
	
	BALL_DIAMETER = 1.0/60.0
	
	for i in xrange(1,5):
		players.append(Player(i,(1 if not i==playerpos-1 else 0),PLAYER_SIZE,PLAYER_THICKNESS))
		paddles.append(pygame.image.load("img/paddle"+str(i)+".png").convert_alpha())
		if i<=2: paddles[i-1]=pygame.transform.smoothscale(paddles[i-1], (int(PLAYER_THICKNESS*SIZE),int(PLAYER_SIZE*SIZE)))
		else: paddles[i-1]=pygame.transform.smoothscale(paddles[i-1], (int(PLAYER_SIZE*SIZE),int(PLAYER_THICKNESS*SIZE)))

	### Set timers ###
	CLIENT_CLOCK=pygame.time.Clock() # fps object
	pygame.time.set_timer(25, 500) # event for data display
	pygame.time.set_timer(26, 30) # event for outgoing data

	if (cl_host_ip=="localhost") or (cl_host_ip=="127.0.0.1"): pygame.display.set_caption("::pong4p:: - Host/Singelplayer")
	else: pygame.display.set_caption("::pong4p:: - Multiplayer")

	helvetica = pygame.font.Font(pygame.font.match_font("helvetica"), 12)
	helvetica.set_bold(True)

	buttonstyle = [[(180, 180, 180), (30, 30, 30), (200, 200, 200)], 
			[(0, 0, 0), (160, 160, 160), (0, 0, 160)], 
			[(0, 0, 0), (50, 50, 255), (220, 0, 0)], 
			1, helvetica]
	menustyle = [(240, 240, 240), (0, 0, 0), 1,4]

	chat = GameMenu(RES[0]/2-154,RES[1]-140,menustyle)
	chat.add_field(TextField(buttonstyle,"Eingabe","",0,0,300,20))
	showchat = False
		
	mouse_pic=pygame.image.load("img/mouse.png").convert_alpha()
	square = pygame.Surface((SIZE,SIZE)).convert()
	rahmen = pygame.Surface((SIZE+4,SIZE+4)).convert()
	rahmen.fill((255,255,255))
	bg_old=pygame.image.load("img/stars.png").convert_alpha()
	BACKGROUND=pygame.transform.smoothscale(bg_old, (int(SIZE),int(SIZE)))
	dots =    [pygame.image.load("img/funk.png").convert_alpha(),
						pygame.image.load("img/funk2.png").convert_alpha(),
						pygame.image.load("img/funk3.png").convert_alpha(),
						pygame.image.load("img/funk4.png").convert_alpha()]
	
	ballpic=pygame.image.load("img/ball1.png").convert_alpha()
	ballpic=pygame.transform.smoothscale(ballpic, (int(BALL_DIAMETER*SIZE),int(BALL_DIAMETER*SIZE)))
	
	ball = Ball(BALL_DIAMETER)
	ballspeed = [0,0]
	lastballpos = [0.5,0.5]
	lastballget = 0.0
	
	sondertasten = [pygame.K_BACKSPACE,pygame.K_TAB,pygame.K_CLEAR,pygame.K_RETURN,pygame.K_ESCAPE]
	
	print "------------------"
	log.append("Spiel gestartet...",3*FPS,(1*FPS+pygame.time.get_ticks()/1000 *FPS))
	fps = str(0) # current fps saved in this variable
	game_over = False
	bounced = False
	##### GAME LOOP #####
	while not game_over:

		CLIENT_CLOCK.tick(FPS)
		
		lastballget += 1
		screen.fill((0,0,0))
		square.fill((0,0,0))
		square.blit(BACKGROUND,(0,0))
		
		for event in pygame.event.get():
			if event.type == 25: # event for data display
				fps = "FPS: %3.2f" % CLIENT_CLOCK.get_fps()
			if event.type == 26:
				Client_Pong.send_own_dist(players[playerpos-1].distance)
				retr = Client_Pong.retr_dist(players, ball)				
				if retr == "kickme":
					print "lol"
					game_over = True
					sys.exit("You have been kicked")
				#else:
			#		if lastballget != 0:
			#			ballspeed[0] = int( (ball.x-lastballpos[0]) / lastballget )
			#			ballspeed[1] = int( (ball.y-lastballpos[1]) / lastballget )
			#		lastballget = 0.0
				else:
					ball.move() #benutzt eigene speed um lags zu vertuschen
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					if not showhelp: game_over = True
					else: showhelp = False
				if event.key == pygame.K_F1:
					showhelp = not showhelp					
				if showchat:
					if not event.key in sondertasten:
						text = str(event.unicode)
						chat.key_down(text)
					elif event.key == pygame.K_BACKSPACE:
						chat.key_down("","back")
				elif event.key == pygame.K_r:
					Client_Pong.send_text(".reset")
				elif event.key == pygame.K_PLUS:
					Client_Pong.send_text(".chspeed=0.0002")
				elif event.key == pygame.K_MINUS:
					Client_Pong.send_text(".chspeed=-0.0002")
				if event.key == pygame.K_RETURN:
					if not showchat:
						chat.fields[0].active=True
					else:
						text = chat.fields[0].text
						chat.fields[0].text = ""
						if text != "":
							if text==".help":
								showhelp = True
							else:
								if text[0]!=".": text = "<"+CLIENT_NAME+"> "+text
								Client_Pong.send_text(text)
						
					showchat = not showchat
			
			if event.type == pygame.QUIT:
				game_over = True
			if event.type == pygame.MOUSEBUTTONDOWN:
				showmouse = not showmouse
		size=MAINFONT.size(fps)
		screen.blit(MAINFONT.render(fps, True,(255,255,255),(0,0,0)),(RES[0]-size[0]-10,10))

		#hier wird die eigene "distance" durch mausposition errechnet
		mouse = pygame.mouse.get_pos()
		relmouse=(mouse[0]-(RES[0]-SIZE)/2,mouse[1]-(RES[1]-SIZE)/2)
		calc_position(relmouse,players[playerpos-1],playerpos,SIZE,PEDAL_LAG)
		
		#hier die neue distance an den server senden
#		sock.sendto("setdist-"+str(playerpos-1)+"="+str(players[playerpos-1].distance),host_addr)
		
		

		for player in players:
			player.draw(square,paddles[player.position-1],SIZE)

		for funk in funken:
			funk.action(square)

		ball_pos=(ball.x*SIZE,ball.y*SIZE)
		
		bounced = ball.bounce([players[0].distance,players[1].distance,players[2].distance,players[3].distance], False)
		if Client_Pong.lastbounce != Client_Pong.newbounce:
			erg = Client_Pong.newbounce
			toright, totop,	toleft, tobottom = 0, 0, 0, 0
			if erg==1: toleft, toright, totop, tobottom = 0,  200, -100, 100
			if erg==2: toleft, toright, totop, tobottom = -200, 0, -100, 100
			if erg==3: toleft, toright, totop, tobottom = -100, 100,  0, 200
			if erg==4: toleft, toright, totop, tobottom = -100, 100, -200, 0
			speed=math.sqrt(2.0)
			
			for i in xrange(10):
				life = random.randint(20,100)
				dot = dots[random.randint(0,3)]
				x_s = random.randint(toleft,toright)/100.0*speed
				y_s = random.randint(totop,tobottom)/100.0*speed
				funken.append(Particle(ball_pos,(x_s,y_s),dot,life))
				
			Client_Pong.lastbounce=erg 
		
		
		x_off=int((RES[0]-SIZE)/2)
		y_off=int((RES[1]-SIZE)/2)
		square.blit(ballpic,ball_pos)
		screen.blit(rahmen,(x_off-2,y_off-2))
		screen.blit(square,(x_off,y_off))

		if (mouse[0]<x_off): pygame.mouse.set_pos(x_off,mouse[1])
		elif (mouse[0]>x_off+SIZE): pygame.mouse.set_pos(x_off+SIZE,mouse[1])
		
		if (mouse[1]<y_off): pygame.mouse.set_pos(mouse[1],y_off)
		elif (mouse[1]>y_off+SIZE): pygame.mouse.set_pos(mouse[1],y_off+SIZE)
		
		# Abfrage von Textnachrichten vom dem Server
		
		newtext = Client_Pong.get_text()
		if newtext != -1: log.append(newtext,6*FPS,(3*FPS+pygame.time.get_ticks()/1000 *FPS))

		log.action(pygame.time.get_ticks()/1000*FPS,MAINFONT,screen)
		
		
		if showchat: chat.draw(screen, mouse)
		if showmouse: screen.blit(mouse_pic,(mouse[0]-4,mouse[1]-4))
		
		if showhelp: screen.blit(helpwindow,helpoffset)
		
		
		pygame.display.update()

#finally:
	pygame.quit()
	print "Spiel beendet"
	del(Client_Pong)
	#menue = subprocess.Popen(["python","menu.py"])

if __name__ == '__main__':
	init_client()
