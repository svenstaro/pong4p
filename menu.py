#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
import subprocess
from tools import *
from menu_classes import *

pygame.init()
pygame.font.init()
pygame.key.set_repeat(500,50)

screenwidth = str(pygame.display.Info().current_w)
screenheight = str(pygame.display.Info().current_h)

cl = Config_Loader('.pong4p')

try:
	fontname = cl.getString("menu_font")
	fontsize = cl.getInteger("menu_fontsize")
	fontbold = cl.getBoolean("menu_fontbold")
except ValueError: 
	print "Error in Config File at Font Entry. Unsing default."
	fontname = "Verdana"
	fontsize = 12
	fontbold = True 

men_font=pygame.font.SysFont(fontname,fontsize,fontbold)

styles = []
style_elements = ["button"]
poses = ["back","font","border"]
states = ["normal","active","hover"]

for style_element in style_elements:
	act_style=[]
	for pos in poses:
		row=[]
		for state in states:
			entry=style_element+"_"+pos+"_"+state
			color = cl.getString(entry).split(",")
			try: row.append((int(color[0]),int(color[1]),int(color[2])))
			except ValueError: 
				print "Error in Config File at Entry \""+entry+"\". Using default."
				if pos=="back": row.append((255,255,255))
				elif pos=="font" or pos=="border": row.append((0,0,0))
				else: row.append((128,128,128))
			
		act_style.append(row)
	styles.append(act_style)	

styles[0].append(cl.getInteger("button_border_width"))
styles[0].append(men_font)

try:
	color = cl.getString("menu_background").split(",")
	col = (int(color[0]),int(color[1]),int(color[2]))
	border = cl.getString("menu_border").split(",")
	bor = (int(border[0]),int(border[1]),int(border[2]))
	b_size = cl.getInteger("menu_border_size")
except ValueError: 
	print "Error in Config File at Menu Background Entry. Using default."
	col=(240,240,240)
	bor=(0,0,0)
	b_size=1
finally:
	styles.append([col,bor,b_size,10])	

try: 
	color = cl.getString("main_background").split(",")
	BACKGROUND_COLOR = (int(color[0]),int(color[1]),int(color[2]))	
except ValueError: 
	print "Error in Config File at \"main_background\". Using default."
	BACKGROUND_COLOR = (0,0,0)
	

#globals
RES=(600,600)
clock=pygame.time.Clock()
FPS=25
sondertasten = [pygame.K_BACKSPACE,pygame.K_TAB,pygame.K_CLEAR,pygame.K_RETURN,pygame.K_ESCAPE]

screen=pygame.display.set_mode(RES)
pygame.display.set_caption("::pong4p:: - Main Menu")

	
try:
	img = cl.getString("main_background_image")
	BACKGROUND_IMAGE = pygame.image.load(img).convert_alpha()
except:
	BACKGROUND_IMAGE = None


# menu creating and ...
menu = GameMenu(20,20,styles[1])

spmenu= GameMenu(220,20+50,styles[1])
spmenu.add_button(MenuButton(styles[0],"Play now!",105,0,95,40))
spmenu.add_button(MenuButton(styles[0],"Cancel",0,0,95,40))

start_server=GameMenu(220,70+50,styles[1])
start_server.add_button(MenuButton(styles[0],"Start Server",0,0,200,30))
start_server.add_button(MenuButton(styles[0],"Start Server in Background",0,40,200,30))
start_server.add_button(MenuButton(styles[0],"Cancel",0,80,200,30))

exit_menu =GameMenu(220,220+50,styles[1])
exit_menu.add_button(MenuButton(styles[0],"Yes, Exit",105,0,95,40))
exit_menu.add_button(MenuButton(styles[0],"Cancel",0,0,95,40))

client_menu=GameMenu(220,120+50,styles[1])
client_menu.add_field(TextField(styles[0],"host","localhost"))
client_menu.add_field(TextField(styles[0],"port","13258",0,30))
client_menu.add_button(MenuButton(styles[0],"join now",105,60,95,30))
client_menu.add_button(MenuButton(styles[0],"Cancel",0,60,95,30))

try: FPS_saved = cl.getString("FPS")
except:
	FPS_saved = "60"
	print "Error in Config File at \"FPS\". Using default."

try: fullscreen = cl.getBoolean("fullscreen")
except:
	fullscreen = True
	print "Error in Config File at \"fullscreen\". Using default."

if fullscreen == True: fs = "yes"
elif fullscreen == False: fs = "no"


try: res_auto = cl.getString("res_auto")
except:
	res_auto = "yes"
	print "Error in Config File at \"res_auto\". Using default."

if res_auto == "yes": res_saved = "auto"
else:
	try:
		res_saved = cl.getString("width")+"x"+cl.getString("height")
	except:
		res_saved = "auto"
		print "Error in Config File at \"width\" or \"height\". Using auto configuration."

actres = (pygame.display.Info().current_w,pygame.display.Info().current_h)


options = GameMenu(220,140+50, styles[1])
options.add_field(PullDownMenu(styles[0],"FPS",FPS_saved,["30","60","90"],0,0))
options.add_field(PullDownMenu(styles[0],"fullscreen",fs,["yes","no"],0,60))
options.add_field(PullDownMenu(styles[0],"resolution",res_saved,["auto","800x600","1024x768","1280x800","1440x900","1440x1050","1680x1050"],0,30))
options.add_button(MenuButton(styles[0],"Cancel",0,90,95,30))
options.add_button(MenuButton(styles[0],"Apply",105,90,95,30))

name = "unset"
try:
	name = cl.getString("name")
except: pass
if name=="unset":
	name = ""
menu.add_field(TextField(styles[0],"Name",name,0,0,170,20))
menu.add_button(MenuButton(styles[0],"Singleplayer",0,0+50,170,40, spmenu))
menu.add_button(MenuButton(styles[0],"Multiplayer Server",0,50+50,170,40,start_server))
menu.add_button(MenuButton(styles[0],"Multiplayer Client",0,100+50,170,40,client_menu))
menu.add_button(MenuButton(styles[0],"Options",0,150+50,170,40,options))
menu.add_button(MenuButton(styles[0],"Exit",0,200+50,170,40,exit_menu))


# menu loop
next_frame = pygame.time.get_ticks()
loop=True
host_ip="127.0.0.1"
frame=0
restart=False
while loop:
	clock.tick(FPS)
	frame+=1
	last_button=""
	if frame%FPS==0:
		menu.toggle_fields()
		
	mouse = pygame.mouse.get_pos()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			loop=False
		elif event.type == pygame.MOUSEBUTTONDOWN:
			last_button=menu.check_buttons((mouse[0],mouse[1]))
			menu.click_fields(mouse)
		elif event.type==pygame.KEYDOWN:
			if not event.key in sondertasten:
				text = str(event.unicode)
				menu.key_down(text)
			elif event.key== pygame.K_BACKSPACE:
				menu.key_down("","back")
				
			if event.key == pygame.K_ESCAPE:
				iwasoffn=False
				for button in menu.get_buttons():
					if button.submenu_status: iwasoffn = True
					button.set_submenu_stat(False)
				if not iwasoffn:
					loop=False
			elif event.key == pygame.K_r:
				loop=False
				restart=True
			elif event.key == pygame.K_q:
				loop=False
				
	screen.fill(BACKGROUND_COLOR)
	if BACKGROUND_IMAGE!= None: screen.blit(BACKGROUND_IMAGE,(0,0))		
	menu.draw(screen,mouse)   
	pygame.display.flip()
	
	#namen speichern
	name = menu.fields[0].text
	if name !="": cl.setString("name",name)
	else: cl.setString("name","unset")

	if last_button=='Play now!' or last_button=='join now' or last_button=='Start Server' or last_button=='Start Server in Background' or last_button=='Yes, Exit':
		loop=False
	elif last_button == "Apply":
		#try:
		if True:
			FPSs = options.fields[0].text
			fullscreens = options.fields[1].text
			name = menu.fields[0].text
			RESs = options.fields[2].text
			cl.setString("FPS",FPSs)
			cl.setString("fullscreen",fullscreens)
			if RESs != "auto": 
				cl.setString("res_auto","no")
				cl.setString("width",str(RESs.split("x")[0]))
				cl.setString("height",str(RESs.split("x")[1]))
			else: 
				cl.setString("res_auto","yes")
				cl.setString("width",screenwidth)
				cl.setString("height",screenheight)
			if name !="": cl.setString("name",name)
			else: cl.setString("name","unset")
			
			
		#except:
		#	print "Error saving Config File. Please retry."
		for button in menu.get_buttons():
			button.set_submenu_stat(False)
	elif last_button=="Cancel":
		for button in menu.get_buttons():
			button.set_submenu_stat(False)

pygame.quit()
                
if last_button=='Play now!':
	server = subprocess.Popen(["python", "server.py", "--daemon"])
	client = subprocess.Popen(["python", "client.py","localhost"])
	client.wait()
	server.terminate()
elif last_button == 'Start Server':
	server = subprocess.Popen(["python", "server.py"])
elif last_button == 'Start Server in Background':
	server = subprocess.Popen(["python", "server.py", "--daemon"])
elif last_button == 'join now':
	client = subprocess.Popen(["python", "client.py","--ip",client_menu.fields[0].text, "--port", client_menu.fields[1].text])

if restart: menu = subprocess.Popen(["python menu.py"],shell=True)
