import socket, time
import random
import sys
import pygame
pygame.init
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)
clock = pygame.time.Clock()
try:
	ip = sys.argv[1]
except:
	ip = "127.0.0.1"
try:
	uuid = sys.argv[2]
except:
	uuid = 1
curr = 0.001
try:
	while True:
		clock.tick(30)
		sock.sendto(str(uuid)+":"+str(curr),(ip,13258))
		curr += 0.001
		if curr >= 0.849:
			curr = 0.001
		try:
			result = sock.recvfrom(1024)[0]
			if result == 'bye':
				sys.exit("server has been shut down")
			else:
				print result
		except: continue
finally:
	sock.sendto(str(uuid)+":bye",(ip,13258))
	sock.close()
	
