#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, sys, os, random, string, pygame, socket, curses, math
from pong_classes import *

VERSION = 0.1
SERVER_PORT = 13258
SERVER_FPS = 400
DEBUG = False

# Note: Server uses floats to address all positions, sizes and movement
PEDAL_LAG = 4.0
PLAYER_SIZE = 0.15
PLAYER_THICKNESS = 0.012
BALL_DIAMETER = 1.0/60.0


class Server(object):
	def __init__(self, port, fps, debug, screen, version=VERSION):
		self.port = port
		self.fps = fps
		self.debug = debug
		self.screen = screen
		self.version = version
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(("",port))
		self.sock.setblocking(0)
		self.clients = [None,None,None,None] # address-tupels # e.g.: ("123.123.123.123",13258)
		self.client_names = ["","","",""]
		self.data = {} # siehe Ueberlegungen
		self.data["ball"] = [0.5,0.5,[0.0,0.0],0]
		for i in xrange(1,5):
			self.data[i] = [0.5,0,3,""]
		self.players = [] # player class instances
		for i in xrange(1,5):
			self.players.append(Player(i-1, 1))
			
		self.nextclid = 0
		self.send_text = "Welcome on Gameserver"
		self.message_id = 0

		curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
		
		if self.debug: 
			print "pong4p",VERSION,"server started on port",SERVER_PORT,"at",SERVER_FPS,"FPS"
			print "[debug mode]"
	
	def show_data(self, clear=False):
		### INFO ###
		try:
			if clear:
				self.screen.clear()
			self.screen.addstr(1, 40, "pong4p (server)", curses.color_pair(1))
			self.screen.addstr(2, 40, "running at:", curses.color_pair(1))
			self.screen.addstr(3, 40, "%s:%d" % (socket.gethostbyname(socket.gethostname()),self.port), curses.color_pair(1) + curses.A_BOLD)
			self.screen.addstr(4, 40, 'FPS', curses.color_pair(1))
			self.screen.addstr(4, 49, '/', curses.color_pair(1))
			self.screen.addstr(4, 45, "%3.0f" % SERVER_CLOCK.get_fps(), curses.color_pair(2) + curses.A_BOLD)
			self.screen.addstr(4, 51, str(self.fps), curses.color_pair(2))
			self.screen.addstr(5, 40, "Ver. "+str(self.version), curses.color_pair(1))
			for i in xrange(4):
				self.screen.addstr(i+1, 1, "Player #%d - dist:" % (i+1), curses.color_pair(1))
				self.screen.addstr(i+1, 19, "%1.4f" % self.data[i+1][0], curses.color_pair(2) + curses.A_BOLD)
			self.screen.addstr(5, 1, 'Ball-X', curses.color_pair(1))
			self.screen.addstr(5, 17, ':', curses.color_pair(1))
			self.screen.addstr(5, 19, "%1.4f" % self.data["ball"][0], curses.color_pair(2) + curses.A_BOLD)
			self.screen.addstr(6, 1, 'Ball-Y', curses.color_pair(1))
			self.screen.addstr(6, 17, ':', curses.color_pair(1))
			self.screen.addstr(6, 19, "%1.4f" % self.data["ball"][1], curses.color_pair(2) + curses.A_BOLD)
			self.screen.addstr(7, 1,  'Ball-Speed', curses.color_pair(1))
			self.screen.addstr(7, 17, ':', curses.color_pair(1))
			self.ball_speed_vec = math.sqrt(self.data["ball"][2][0]**2 + self.data["ball"][2][1]**2)*100
			self.screen.addstr(7, 19, "%1.4f" % self.ball_speed_vec, curses.color_pair(2) + curses.A_BOLD)
			self.screen.addstr(9, 1, "Connected clients:", curses.color_pair(1) + curses.A_BOLD)
			for c in xrange(4):
				self.screen.addstr(c+11, 1, 'Client #%d:' % (c+1), curses.color_pair(1))
				try:
					self.screen.addstr(c+11, 12, self.clients[c][0], curses.color_pair(2))
				except:
					self.screen.addstr(c+11, 12, 'No client connected', curses.color_pair(3))
			self.screen.addstr(16, 1, "Last sent text: ["+str(self.message_id)+"] ", curses.color_pair(1))
			self.screen.addstr(16,22, self.send_text, curses.color_pair(2) + curses.A_BOLD)
			self.screen.addstr(18, 1, "Press 'q' to quit the server", curses.color_pair(1))
			
			self.screen.refresh()
		except:
			sys.exit("ERROR: terminal too small")

	def send_all(self):
		send_data = str("%1.4f" % self.data[1][0])+","+ \
					str("%1.4f" % self.data[2][0])+","+ \
					str("%1.4f" % self.data[3][0])+","+ \
					str("%1.4f" % self.data[4][0])+":"+ \
					str("%1.4f" % self.data["ball"][0])+","+ \
					str("%1.4f" % self.data["ball"][1])+","+ \
					str("%1.4f" % self.data["ball"][2][0])+","+ \
					str("%1.4f" % self.data["ball"][2][1])+","+ \
					str("%d" % self.data["ball"][3])+":"+ \
					str(self.message_id)+","+self.send_text
		for c in self.clients:
			if c is not None:
				self.sock.sendto(send_data, c)
				
	def request(self):
		try:
			result, addr = self.sock.recvfrom(1024)
			posid, dist = result.split(":")
			posid = int(posid)
			if addr not in self.clients: # means a new client has connected
				#self.nextclid+=1
				clid = 1
				name = dist
				while True:
					if clid<4:
						if self.clients[clid-1]==None:
							break
					else:
						self.sock.sendto("ERROR:SERVER_FULL",addr)
						break
					clid+=1
				self.clients[clid-1] = addr
				self.client_names[clid-1] = name
				self.sock.sendto("PLAYER_UUID:"+str(clid),addr)
				self.sock.sendto("MESSAGE_ID:"+str(self.message_id),addr)
				self.sock.sendto("FINISH:",addr)
				self.show_data(True)
				self.send_text = "\""+name+"\" has been added to game! Welcome."
				self.message_id += 1
				return "add,"+str(posid)
			else:
				if dist == 'bye':
					self.clients[posid-1] = None
					self.show_data(True)
					return "del,"+str(posid)
				elif dist[0] != "0":
					if dist[0]!=".": #kein befehl
						self.send_text = dist
						self.message_id += 1						
						return "text,"+self.send_text						
					else:
						return "command,"+dist
				self.data[posid][0] = dist
				return str(posid)+","+str(dist)
		except:
			return False
	def __del__(self):
		for c in self.clients:
			self.sock.sendto("bye",c)
		self.sock.close()
		

def usage(port, fps, debug):
	"""
	This function receives the default values as arguments
	"""
	if "-h" in sys.argv or "--help" in sys.argv:
		print "pong4p",VERSION,"(server), a networked 4-player pong clone."
		print "usage:",sys.argv[0],"[option] ..."
		print "options:"
		print "  -h, --help		this help"
		print "  -p, --port		port for players to connect to"
		print "  -f, --fps		frames-per-second the server should try to calculate"
		print "  -d, --daemon		put server to background"
		print "  -w, --debug		display diagnostic messages"
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
	if "-f" in sys.argv or "--fps" in sys.argv:
		if "-f" in sys.argv:
			fps_index = sys.argv.index("-f") + 1
		if "--fps" in sys.argv:
			fps_index = sys.argv.index("--fps") + 1
		try:
			# see if we were given a valid number
			if int(sys.argv[fps_index]) in xrange (50,5000):
				fps = int(sys.argv[fps_index])
			else:
				sys.exit("ERROR: invalid fps")
		except ValueError:
			sys.exit("ERROR: invalid fps")
	if "-d" in sys.argv or "--daemon" in sys.argv:
		argv_no_d = sys.argv[1:]
		if "-d" in argv_no_d:
			argv_no_d.remove("-d")
		elif "--daemon" in argv_no_d:
			argv_no_d.remove("--daemon")
		daemon_args = string.join(argv_no_d, ' ')
		daemon = subprocess.Popen(["python",sys.argv[0],daemon_args])
		sys.exit("server daemon PID is" + str(daemon.pid))
	if "-w" in sys.argv or "--debug" in sys.argv:
		debug = True

	return port, fps, debug

##### INIT SERVER #####
def init_server(screen):
	global SERVER_CLOCK
	port, fps, debug = usage(SERVER_PORT, SERVER_FPS, DEBUG)
	pygame.init()

	done = False
	Server_Pong = Server(port, fps, debug, screen)
	ball = Ball(BALL_DIAMETER)
	players = []
	#for botnb in xrange(3):
	#	players.append(Player(botnb+1,1,0.1,0.01,botnb))

	SERVER_CLOCK = pygame.time.Clock() # fps object
	pygame.time.set_timer(25, 500) # event for data display
	pygame.time.set_timer(26, 30) # event for outgoing data 30
	pygame.time.set_timer(27, 30) # event for the ball 10
	
	ball.reset()
	
	#### MAIN LOOP ####
	while not done:
		SERVER_CLOCK.tick(fps)
		for event in pygame.event.get():
			if event.type == 25:
				Server_Pong.show_data()
			if event.type == 26:
				Server_Pong.send_all()
			if event.type == 27:
				ball.move()
				Server_Pong.data["ball"][0] = ball.x
				Server_Pong.data["ball"][1] = ball.y
				Server_Pong.data["ball"][2][0] = ball.speedx
				Server_Pong.data["ball"][2][1] = ball.speedy
				
				erg = ball.bounce([Server_Pong.data[1][0],Server_Pong.data[2][0],Server_Pong.data[3][0],Server_Pong.data[4][0]]) #distances
				ball.check_out()
				if erg != False:
					Server_Pong.data["ball"][3] = ball.lastbounce
					ball.change_speed(0.0006)
				
				for i in xrange(1,5): # move bots
					if Server_Pong.clients[i-1] == None:
						pedal_lag = 4.0 ##
						if i>=3: dist=ball.x
						else: dist=ball.y
						dist-=0.075
						nd=Server_Pong.data[i][0]
						nd+=(dist-nd)/pedal_lag
						if nd<0: nd=0
						if nd+0.15>1: nd=0.85
						Server_Pong.data[i][0] = nd
					
		screen.nodelay(1)
		c = screen.getch()
		if c == ord('q'): 
			pygame.quit()
			done = True
		
		### networking ###		
		result = Server_Pong.request()
		
		if result:
			if result.split(",")[0] == "add":
				pass # playeradd with playerpos: int(result.split(",")[1])
			elif result.split(",")[0] == "del":
				pass # playerdel
			elif result.split(",")[0] == "text":
				pass
			elif result.split(",")[0] == "command":
				com = result.split(",")[1].lower()
				if com == ".reset":
					ball.reset()
				elif com[:5] == ".kick":
					Server_Pong.message_id +=1
					Server_Pong.send_text = com
				elif com.split("=")[0]==".chspeed": #change speed
					ball.change_speed(float(com.split("=")[1]))
					
			else:
				Server_Pong.data[int(result.split(",")[0])][0] = \
				float(result.split(",")[1]) # set distance in Server_Pong.data

if __name__ == '__main__':
	curses.wrapper(init_server)
