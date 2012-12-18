#PyFighter by Iron Hand
#-------------------

import pygame, sys, time, random, math, string
import pygame.locals
import pygame.gfxdraw
import copy 

# set up pygame
pygame.init()
joysticks = pygame.joystick.get_count()
if joysticks > 0:
	joy = pygame.joystick.Joystick(0)
	joy.init()
mainClock = pygame.time.Clock()

#Load Wave File
wave_file = open("wave1.txt", "r")
wave_list = wave_file.readlines()
wave_file.close()
wave_len = len(wave_list)

#User config Datas
#Defaults
#Stars in the Background
user_stars = 100
WINDOWWIDTH = 800
WINDOWHEIGHT = 600
user_input = "keyboard"
try:
	#Load Config File
	conf_file = open("pfconfig.txt", "r")
	conf_list = conf_file.readlines()
	conf_file.close()
except:
	pass
for fa in conf_list:
	if "#" not in fa:
		if "screen" in fa:
			temp = fa.replace("screen ","").replace("\n","").split("x")
			WINDOWWIDTH = int(temp[0])
			WINDOWHEIGHT = int(temp[1])
		if "fullscr" in fa:
			windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.FULLSCREEN, 32)
		if "stars" in fa:
			temp = fa.replace("stars ","").replace("\n","")
			user_stars = int(temp)
		if "input" in fa:
			temp = fa.replace("input ","").replace("\n","")
			user_input = temp
			print temp

#Fenster Setup pygame.FULLSCREEN|pygame.HWSURFACE
if globals().has_key('windowSurface') == False:
	windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('PyFighter')
			
# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# set up keyboard variables
moveLeft = False
moveRight = False
moveUp = False
moveDown = False
keyboard_shoot = False

MOVESPEED = 10
FIRESPEED = 20

#Global Variables
gegneraufkommen = 100
wave_number = 0
wave_pause = 0
rise_from_dead_count = 250
musik_enable = True
sound_enable = True

#Game Variables
lives = 3
points = 0

#Init Sound
#if sound_enable == True:
try:
	pygame.mixer.init(22050, -16, 2, 4096)
	shoot_sound = pygame.mixer.Sound("pfsound/shoot.wav")
	shoot2_sound = pygame.mixer.Sound("pfsound/shoot2.wav")
	shoot2_sound.set_volume(0.5)
	expl1_sound = pygame.mixer.Sound("pfsound/expl1.wav")
	expl2_sound = pygame.mixer.Sound("pfsound/expl2.wav")
	expl3_sound = pygame.mixer.Sound("pfsound/expl3.wav")
	expl4_sound = pygame.mixer.Sound("pfsound/expl4.wav")
	expl6_sound = pygame.mixer.Sound("pfsound/expl6.wav")
	laser_sound = pygame.mixer.Sound("pfsound/laser.wav")
	laser_sound.set_volume(0.5)
except:
	print "Fehlende Sound Dateien"

#Init Musik
if musik_enable == True:
	pygame.mixer.music.load("ultraman/titel.ogg")
	#pygame.mixer.music.load("mrgspnv2.xm")
	#pygame.mixer.music.load("Iron_Fist.ogg")
	#pygame.mixer.music.load("Track 1.ogg")
	pygame.mixer.music.play(0, 0.0)
	pygame.mixer.music.set_volume(1.0)
	
#Game Fonts
basicFont = pygame.font.SysFont(None, 20)
points_text = basicFont.render('Points: ' + str(points), True, WHITE)
points_textRect = points_text.get_rect()
points_textRect.center = 30, WINDOWHEIGHT - 10

lives_text = basicFont.render('Lives: ' + str(lives), True, WHITE)
lives_textRect = points_text.get_rect()
lives_textRect.center = WINDOWWIDTH - 30, WINDOWHEIGHT - 10

#Objekte Setup
player = {'rect':pygame.Rect(WINDOWWIDTH/2 - 25, WINDOWHEIGHT - 100, 20, 20), 'status':"dead", 'max_shoot_delay':5, 'shoot_delay':0}
shoots = []
player_shoot = {'rect':pygame.Rect(player['rect'].centerx, player['rect'].centery, 5, 5)}
enemys = []
enemy1 = {'rect':pygame.Rect(random.randint(0, WINDOWWIDTH), 0, 20, 20), 'type':1, 'speed':5}
enemys_shoots = []
e_shoot1 = {'rect':pygame.Rect(0, 0, 10, 10), 'speed':5}
back_stars = []
for i in range(user_stars):
	back_stars.append([random.randint(0, WINDOWWIDTH),random.randint(0, WINDOWHEIGHT), random.randint(100,255)])
explosions = []
shock_waves = []
nova_waves = []
partikel_effekts = []
truemmer = []
onscreen_text = []

#Komplex Polygons
m1_poly = ((-49, -1), (-47, -24), (-42, -28), (-37, -42), (-28, -49), (-22, -47), (-16, -46), (-12, -45), (-6, -45), (0, -43), (7, -43), (12, -43), (20, -46), (28, -37), (35, -31), (38, -25), (42, -15), (47, -10), (49, 9), (47, 27), (41, 35), (35, 36), (30, 39), (23, 39), (10, 43), (0, 45), (-10, 46), (-14, 46), (-20, 46), (-28, 44), (-38, 34), (-47, 21), (-49, 15), (-49, 10), (-49, 6), (-48, 1))

m2_poly = ((-24, -1), (-20, -8), (-15, -16), (-7, -17), (-1, -17), (5, -20), (11, -16), (19, -12), (20, -4), (16, 1), (19, 6), (15, 13), (6, 17), (-3, 14), (-7, 17), (-14, 16), (-20, 12), (-23, 6), (-24, 0))

m3_poly = ((-8, -8), (5, -9), (10, -7), (11, -3), (9, 2), (10, 5), (6, 9), (1, 10), (-4, 10), (-8, 7), (-10, 5), (-8, 1), (-9, -3), (-9, -7))

#((-48, 0, -46, -23), (-42, -27, -36, -46), (-28, -49, -23, -49), (-15, -45, -8, -45), (1, -42, 9, -44), (15, -44, 21, -43), (27, -37, 36, -30), (42, -15, 49, 6), (46, 30, 34, 39), (23, 39, 1, 45), (-14, 45, -21, 47), (-37, 34, -47, 18), (-50, 8, -48, 1))

#SoundFunktion
def play_sound(sound, loop, maxtime, fade_ms, volume, fade_out):
	if sound_enable == True:
		exec("sound.play(loop ,maxtime , fade_ms)")
	if volume > 0:
		exec("sound.set_volume(volume)")
	if fade_out > 0:
		exec("sound.fadeout(fade_out)")
	
	#exec("sound.set_volume(1.0)")

#Create new Explosion
def new_explosion(pixels, x, y):
	global explosions
	single_exp = []
	for p in range(pixels):
		single_exp.append([x, y, random.randint(100, 255)])
	explosions.append(single_exp)
	
#Create Truemmer
def new_truemmer(parts, x, y, part_speed):
	global truemmer
	single_part = []
	for p in range(parts):
		single_part.append([x, y, 255, random.randint(0, 90), random.randint(-part_speed, part_speed), random.randint(-part_speed, part_speed)])
	truemmer.append(single_part)

#Create On-Screen Text
def new_text(text, x, y, font_size, time_to_live, fading_speed):
	global onscreen_text
	onscreen_text.append({'text':text, 'font':pygame.font.SysFont(None, font_size), 'color':[255,255,255], 'x':x, 'y':y, 'time':time_to_live, 'fading':fading_speed})
	
#Create new Shockwave
def new_shockwave(x, y, waves):
	global shock_waves
	for p in range(waves):
		shock_waves.append([x, y, 20, p+1, 100])
		
#Create new Novawave
def new_novawave(x, y, radius):
	global nova_waves
	temp_rec = pygame.Rect(0, 0, radius, radius)
	temp_rec.centerx = x
	temp_rec.centery = y
	nova_waves.append([temp_rec, 40])

#Create new Partikel Effekt
def new_partikeleffekt(x, y, w, h, speed_x, speed_y, partikel, time_to_life):
	global partikel_effekts
	temp_rect = pygame.Rect(0, 0, w, h)
	temp_rect.centerx = x
	temp_rect.centery = y
	single_part = []
	for p in range(partikel):
		single_part.append([x+random.randint(-(w/2),w/2), y+random.randint(-(h/2),h/2), random.randint(100, 255)])
	partikel_effekts.append([temp_rect, single_part, speed_x, speed_y, time_to_life])
	
def add_points(points_to_add):
	global points, points_text
	points += points_to_add
	points_text = basicFont.render('Points: ' + str(points), True, WHITE, BLACK)
	
def add_lives(lives_to_add):
	global lives, lives_text
	lives += lives_to_add
	lives_text = basicFont.render('Lives: ' + str(lives), True, WHITE, BLACK)
	
#Pointlist with 2 arguments
def polygon_pointlist(start_x,start_y, point_list):
	out_list = []
	for point in point_list:
		out_list.append((start_x + point[0], start_y + point[1]))
	return out_list

#Pointlist with 4 arguments
def polygon_pointlist_rot(start_x,start_y, angle, point_list):
	out_list = []
	for point in point_list:
		out_list.append((start_x + point[0]*math.sin(angle), start_y + point[1]*math.cos(angle)))
		out_list.append((start_x + point[2]*math.cos(angle), start_y + point[3]*math.sin(angle)))
	return out_list

#Pointlist with 4 arguments
def polygon_pointlist_rot2(start_x,start_y, angle, point_list):
	out_list = []
	for point in point_list:
		#out_list.append((start_x + point[0]*math.sin(angle), start_y + point[1]*math.cos(angle)))
		#out_list.append((start_x - point[3]*math.sin(angle), start_y + point[2]*math.cos(angle)))	
		x = ( (point[0] * math.cos(angle)) + (point[1] * math.sin(angle)) )
		y = ( (point[1] * math.cos(angle)) - (point[0] * math.sin(angle)) )
		out_list.append((x + start_x,y + start_y)) 
	return out_list

def poly_oval(x0,y0, x1,y1, steps=5, rotation=0): 

	# x0,y0,x1,y1 are as create_oval
	
	# rotation is in degrees anti-clockwise, convert to radians 
	#rotation = rotation * math.pi / 180.0
	
	# major and minor axes 
	a = (x1 - x0) / 2.0 
	b = (y1 - y0) / 2.0
	
	# center 
	xc = x0 + a 
	yc = y0 + b
	
	point_list = []
	
	# create the oval as a list of points 
	for i in range(steps):
	# Calculate the angle for this step # 360 degrees == 2 pi radians 
		theta = (math.pi * 2) * (float(i) / steps)
		x1 = a * math.cos(theta) 
		y1 = b * math.sin(theta)
		# rotate x, y 
		x = (x1 * math.cos(rotation)) + (y1 * math.sin(rotation)) 
		y = (y1 * math.cos(rotation)) - (x1 * math.sin(rotation))
		point_list.append((round(x + xc),round(y + yc))) 
		#point_list.append(round(y + yc))
	
	return point_list

e4_del_rect = 0

def enemy_destroyed(e, i, hit_power):
	global e4_del_rect
	new_explosion(10, i['rect'].centerx, i['rect'].centery)
					
	if e['type'] == 1 or e['type'] == 2:
		play_sound(expl2_sound, 0, 0, 0, 0, 0)
		new_truemmer(4, e['rect'].centerx, e['rect'].centery, 5)
	elif e['type'] == 3:
		play_sound(expl2_sound, 0, 0, 0, 0, 0)
		new_truemmer(8, e['rect'].centerx, e['rect'].centery, 5)			
	if e['type'] == 7:
		play_sound(expl3_sound, 0, 0, 0, 0, 1500)
		new_truemmer(4, e['rect'].centerx, e['rect'].centery, 5)
		
	if e.has_key('live'):
		if e['live'] > 0:
			e['live'] -= hit_power
		if e['live'] <= 0:
			if e['type'] == 4:
				play_sound(expl1_sound, 0, 0, 0, 0, 0)
				new_truemmer(15, e['rect'].centerx, e['rect'].centery, 5)
				e4_del_rect = pygame.Rect( e['rect'].left - 20,  e['rect'].bottom + 15, 80, 100)
				#pygame.draw.rect(windowSurface, WHITE, e4_del_rect, 1)
				new_shockwave(e['rect'].centerx, e['rect'].centery, 3)
			if e['type'] == 5:
				play_sound(expl3_sound, 0, 0, 0, 0, 1500)
				new_truemmer(10, e['rect'].centerx, e['rect'].centery, 3)
				for nm in range(4):
					new_speed_x = 0
					new_speed_y = 0
					while (new_speed_x == 0) or (new_speed_y == 0):
						new_speed_x = random.randint(-(abs(e['speed_x'])+abs(e['speed_y'])), abs(e['speed_x'])+abs(e['speed_y']))
						new_speed_y = random.randint(-(abs(e['speed_x'])+abs(e['speed_y'])), abs(e['speed_x'])+abs(e['speed_y']))
					new_rot = 0
					while new_rot == 0:
						new_rot = random.randint(-e['shoot_rate']*2,e['shoot_rate']*2)
					
					if nm == 0:
						enemys.append({'type':6, 'rect':pygame.Rect(e['rect'].centerx-50, e['rect'].centery-50, 50, 50), 'speed_x':new_speed_x, 'speed_y':new_speed_y, 'live':5, 'angle':0,'shoot_type':0, 'shoot_rate':new_rot, 'shoot_aktivat':0, 'points':25})
					if nm == 1:
						enemys.append({'type':6, 'rect':pygame.Rect(e['rect'].centerx, e['rect'].centery-50, 50, 50), 'speed_x':new_speed_x, 'speed_y':new_speed_y, 'live':5, 'angle':0,'shoot_type':0, 'shoot_rate':new_rot, 'shoot_aktivat':0, 'points':25})
					if nm == 2:
						enemys.append({'type':6, 'rect':pygame.Rect(e['rect'].centerx-50, e['rect'].centery, 50, 50), 'speed_x':new_speed_x, 'speed_y':new_speed_y, 'live':5, 'angle':0,'shoot_type':0, 'shoot_rate':new_rot, 'shoot_aktivat':0, 'points':25})
					if nm == 3:
						enemys.append({'type':6, 'rect':pygame.Rect(e['rect'].centerx, e['rect'].centery, 50, 50), 'speed_x':new_speed_x, 'speed_y':new_speed_y, 'live':5, 'angle':0,'shoot_type':0, 'shoot_rate':new_rot, 'shoot_aktivat':0, 'points':25})
			if e['type'] == 6:
				play_sound(expl3_sound, 0, 0, 0, 0, 1500)
				new_truemmer(5, e['rect'].centerx, e['rect'].centery, 3)
				for nm in range(2):
					new_speed_x = 0
					new_speed_y = 0
					while (new_speed_x == 0) or (new_speed_y == 0):
						new_speed_x = random.randint(-(abs(e['speed_x'])+abs(e['speed_y'])), abs(e['speed_x'])+abs(e['speed_y']))
						new_speed_y = random.randint(-(abs(e['speed_x'])+abs(e['speed_y'])), abs(e['speed_x'])+abs(e['speed_y']))
					enemys.append({'type':7, 'rect':pygame.Rect(e['rect'].centerx+25*nm, e['rect'].centery, 25, 25), 'speed_x':new_speed_y, 'speed_y':new_speed_y, 'live':1, 'angle':0,'shoot_type':0, 'shoot_rate':e['shoot_rate'], 'shoot_aktivat':0, 'points':10})
			new_explosion(50, e['rect'].centerx, e['rect'].centery)
			new_text(str(e['points']), e['rect'].centerx, e['rect'].centery, 20, 0, 10)
			enemys.remove(e)
			add_points(e['points'])
	else:
		new_explosion(50, e['rect'].centerx, e['rect'].centery)
		new_text(str(e['points']), e['rect'].centerx, e['rect'].centery, 20, 0, 10)
		enemys.remove(e)
		add_points(e['points'])

def player_shoot():
	play_sound(shoot2_sound, 0, 0, 0, 0, 0)
	shoots.append({'rect':pygame.Rect(player['rect'].centerx - 2, player['rect'].centery - 15, 5, 5)})
	player['shoot_delay'] = player['max_shoot_delay']

#Game Loop
while True:
	
	for event in pygame.event.get():
		#Quit Event
		if event.type == pygame.locals.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.locals.KEYDOWN:
			#change the keyboard variables
			if user_input == "keyboard":
				if event.key == pygame.locals.K_LEFT or event.key == ord('a'):
					moveRight = False
					moveLeft = True
				if event.key == pygame.locals.K_RIGHT or event.key == ord('d'):
					moveLeft = False
					moveRight = True
				if event.key == pygame.locals.K_UP or event.key == ord('w'):
					moveDown = False
					moveUp = True
				if event.key == pygame.locals.K_DOWN or event.key == ord('s'):
					moveUp = False
					moveDown = True
			if user_input == "keyboard" or user_input == "mouse":
				if event.key == pygame.locals.K_SPACE or event.key == ord(' '):
					keyboard_shoot = True
		if event.type == pygame.locals.KEYUP:
			if event.key == pygame.locals.K_ESCAPE:
				pygame.quit()
				sys.exit()
			if user_input == "keyboard":
				if event.key == pygame.locals.K_LEFT or event.key == ord('a'):
					moveLeft = False
				if event.key == pygame.locals.K_RIGHT or event.key == ord('d'):
					moveRight = False
				if event.key == pygame.locals.K_UP or event.key == ord('w'):
					moveUp = False
				if event.key == pygame.locals.K_DOWN or event.key == ord('s'):
					moveDown = False
			if user_input == "keyboard" or user_input == "mouse":
				if event.key == pygame.locals.K_SPACE or event.key == ord(' '):
					keyboard_shoot = False
		if user_input == "mouse":
			pygame.mouse.set_visible(False)
			if event.type == pygame.MOUSEMOTION:
				player['rect'].center = pygame.mouse.get_pos()
			if (event.type == pygame.MOUSEBUTTONDOWN) and (player['shoot_delay'] == 0):
				if event.button == 1:
					keyboard_shoot = True
			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					keyboard_shoot = False
	
	if (keyboard_shoot == True) and (player['shoot_delay'] == 0) and player['status'] != "dead":
		play_sound(shoot2_sound, 0, 0, 0, 0, 0)
		shoots.append({'rect':pygame.Rect(player['rect'].centerx - 2, player['rect'].centery - 15, 5, 5)})
		player['shoot_delay'] = player['max_shoot_delay']
	
	if user_input == "joystick":			
		if joysticks > 0 and player['status'] != "dead":
			if joy.get_axis(0) > 0.5:
				moveLeft = False
				moveRight = True
			elif joy.get_axis(0) < -0.5:
				moveRight = False
				moveLeft = True
			elif (joy.get_axis(0) > -0.01) and (joy.get_axis(0) < 0.01):
				moveRight = False
				moveLeft = False
			if joy.get_axis(1) > 0.5:
				moveUp = False
				moveDown = True
			elif joy.get_axis(1) < -0.5:
				moveDown = False
				moveUp = True
			elif (joy.get_axis(1) > -0.01) and (joy.get_axis(0) < 0.01):
				moveUp = False
				moveDown = False
	
			#Create Shoot
			if joy.get_button(0) == True:
				if player['shoot_delay'] == 0:
					play_sound(shoot2_sound, 0, 0, 0, 0, 0)
					shoots.append({'rect':pygame.Rect(player['rect'].centerx - 2, player['rect'].centery - 15, 5, 5)})
					player['shoot_delay'] = player['max_shoot_delay']
	
	if player['shoot_delay'] > 0:
		player['shoot_delay'] -= 1
	
	#Arbeite Wave Liste ab
	if (wave_number < wave_len) and (wave_pause == 0):
		
		wave_zeile = wave_list[wave_number]
					
		if ("pause" not in wave_zeile) and ("#" not in wave_zeile):
			wave_elements = wave_zeile.split(',')			
			print wave_elements
			for element in wave_elements:
				#Random Creator
				if "randw" in element:
					element = element.replace("randw", str(random.randint(0,WINDOWWIDTH)))
				if "screenw" in element:
					element = element.replace("screenw", WINDOWWIDTH)
				if "screenh" in element:
					element = element.replace("screenh", WINDOWHEIGHT)
					
				attributes = element.split(':')
				if "e1" in attributes[0]:
					enemys.append({'type':1, 'rect':pygame.Rect(int(attributes[1]), int(attributes[2]), 20, 20), 'speed_x':int(attributes[3]), 'speed_y':int(attributes[4]), 'shoot_type':int(attributes[5]), 'shoot_rate':int(attributes[6]), 'shoot_aktivat':-int(attributes[6]), 'angle':int(attributes[7]), 'points':100})
				elif "e2" in attributes[0]:
					enemys.append({'type':2, 'rect':pygame.Rect(int(attributes[1]), int(attributes[2]), 20, 20), 'speed_x':int(attributes[3]), 'speed_y':int(attributes[4]), 'shoot_type':int(attributes[5]), 'shoot_rate':int(attributes[6]), 'shoot_aktivat':-int(attributes[6]), 'angle':0, 'spin_speed':int(attributes[7]), 'points':200})
				elif "e3" in attributes[0]:
					enemys.append({'type':3, 'rect':pygame.Rect(int(attributes[1]), int(attributes[2]), 20, 20), 'speed_x':int(attributes[3]), 'speed_y':int(attributes[4]), 'shoot_type':int(attributes[5]), 'shoot_rate':int(attributes[6]), 'shoot_aktivat':-int(attributes[6]), 'angle':int(attributes[7]), 'amplitude_x':int(attributes[8]), 'amplitude_y':int(attributes[9]), 'frequenzy':int(attributes[10]), 'angle2':85, 'points':300})
				elif "e4" in attributes[0]:
					enemys.append({'type':4, 'rect':pygame.Rect(int(attributes[1]), int(attributes[2]), 40, 40), 'speed_x':int(attributes[3]), 'speed_y':int(attributes[4]), 'shoot_type':5, 'shoot_rate':int(attributes[5]), 'shoot_aktivat':-int(attributes[5]), 'shoot_on_time':int(attributes[6]), 'shoot_on_time_save':int(attributes[6]), 'live':int(attributes[7]), 'points':500})
				elif "m1" in attributes[0]:
					enemys.append({'type':5, 'rect':pygame.Rect(int(attributes[1]), int(attributes[2]), 100, 100), 'speed_x':int(attributes[3]), 'speed_y':int(attributes[4]), 'live':int(attributes[5]), 'angle':0,'shoot_type':0, 'shoot_rate':int(attributes[6]), 'shoot_aktivat':0, 'points':50})
				elif "m2" in attributes[0]:
					enemys.append({'type':6, 'rect':pygame.Rect(int(attributes[1]), int(attributes[2]), 50, 50), 'speed_x':int(attributes[3]), 'speed_y':int(attributes[4]), 'live':int(attributes[5]), 'angle':0,'shoot_type':0, 'shoot_rate':int(attributes[6]), 'shoot_aktivat':0, 'points':25})
				elif "m3" in attributes[0]:
					enemys.append({'type':7, 'rect':pygame.Rect(int(attributes[1]), int(attributes[2]), 25, 25), 'speed_x':int(attributes[3]), 'speed_y':int(attributes[4]), 'live':int(attributes[5]), 'angle':0,'shoot_type':0, 'shoot_rate':int(attributes[6]), 'shoot_aktivat':0, 'points':10})
				elif "playsound" in attributes[0]:
					try:
						user_sound = pygame.mixer.Sound(attributes[0].replace("playsound ","").replace("\n",""))
						play_sound(user_sound, 0, 0, 0, 0, 0)
					except:
						pass
		elif ("pause" in wave_zeile):
			wave_pause = int(wave_zeile.replace("pause ", "").replace("\n",""))
			print wave_pause
			
		wave_number += 1
	
	#Count the Wave Pause
	if wave_pause > 0:
		wave_pause -= 1
			
	# draw the black background onto the surface
	windowSurface.fill(BLACK)
	
	#Print Stars
	for s in back_stars:
		s[1] += random.randint(1,2)
		#s[1] += s[2]
		pygame.gfxdraw.pixel(windowSurface, s[0], s[1], (s[2], s[2], s[2]))
		if s[1] > WINDOWHEIGHT:
			s[1] = 0
	
	#Draw Shoot
	for i in shoots:	
			i['rect'].top -= FIRESPEED
			pygame.draw.ellipse(windowSurface, WHITE, i['rect'], 0)
			if i['rect'].top < 0:
				shoots.remove(i)
			#Hit an enemy
			for e in enemys:
				if e['rect'].colliderect(i['rect']):	
					enemy_destroyed(e, i, 1)					
					try:
						shoots.remove(i)
					except:
						pass
						
	#Draw Enemys Shoots
	for es in enemys_shoots:	
		if es['type'] == 1:
			es['rect'].move_ip(es['speed']*math.sin(es['angle']), es['speed']*math.cos(es['angle']))
			pygame.draw.ellipse(windowSurface, WHITE, es['rect'], 0)
		elif es['type'] == 2:	#Laser
			es['rect'].move_ip(es['speed_x'], es['speed_y'])		
			for ls in range(5):
				rand_color = random.randint(100,255)
				pygame.draw.line(windowSurface, (rand_color,rand_color,rand_color), (es['rect'].left  + random.randint(0, es['rect'].w), es['rect'].top), (es['rect'].left  + random.randint(0, es['rect'].w), es['rect'].bottom), 1)
			if es['on_time'] == 0:			
				enemys_shoots.remove(es)
			else:
				es['on_time'] -= 1
			try:
				if es['rect'].colliderect(e4_del_rect):
					enemys_shoots.remove(es)
					enemys_shoots.remove(enemys_shoots[enemys_shoots.index(es)])
					#del e4_del_rect
			except:
				pass
		elif es['type'] == 3:	#Bomb
			pygame.draw.ellipse(windowSurface, WHITE, es['rect'], 1)
			for bp in range(8):
				pygame.gfxdraw.pixel(windowSurface, int(es['rect'].centerx+7*math.sin(math.radians(bp*45))), int(es['rect'].centery+7*math.cos(math.radians(bp*45))), WHITE)
			if es['live_time'] == 0:
				play_sound(expl4_sound, 0, 0, 0, 0, 0)
				new_explosion(50, es['rect'].centerx, es['rect'].centery)
				enemys_shoots.remove(es)
			else:
				es['live_time'] -= 1	
		elif es['type'] == 4:	#Shipfinder		
			es['rect'].move_ip(es['speed']*math.sin(es['angle']), es['speed']*math.cos(es['angle']))
			pygame.draw.ellipse(windowSurface, WHITE, es['rect'], 1)
			pygame.gfxdraw.pixel(windowSurface, es['rect'].centerx, es['rect'].centery, WHITE)
		if (es['rect'].top > WINDOWHEIGHT) or (es['rect'].bottom < 0) or (es['rect'].left < 0) or (es['rect'].right > WINDOWWIDTH):
			enemys_shoots.remove(es)
		if es['rect'].colliderect(player['rect']):
			#Create Explosion
			if player['status'] == "normal":
				player['status'] = "dead"
				add_lives(-1)
				try:
					enemys_shoots.remove(es)
				except:
					pass
				play_sound(expl6_sound, 0, 0, 0, 0, 0)
				new_novawave(player['rect'].centerx, player['rect'].centery, 25)
				new_explosion(50, player['rect'].centerx, player['rect'].centery)
				new_truemmer(3, player['rect'].centerx, player['rect'].centery, 5)
			
	#Move and Draw Enemys and Create Shoots
	for e in enemys:	
		if e['type'] == 1:
			e['rect'].move_ip(e['speed_x'], e['speed_y'])
			pygame.draw.rect(windowSurface, WHITE, e['rect'], 1)
		elif e['type'] == 2:
			e['rect'].move_ip(e['speed_x'], e['speed_y'])
			e['angle'] += e['spin_speed']
			if e['angle'] > 360:
				e['angle'] = 0
			angle = (e['angle']*math.pi)/180
			pygame.gfxdraw.pixel(windowSurface, e['rect'].centerx, e['rect'].centery, WHITE)
			pl = polygon_pointlist_rot(e['rect'].centerx, e['rect'].centery, angle, ((-12,-12,12,-12),(12,12,-12,12)))
			pygame.draw.polygon(windowSurface, WHITE,  pl, 1)
		elif e['type'] == 3:
			e['angle2'] += e['frequenzy']
			angle = math.radians(e['angle2'])
			e['rect'].move_ip(e['speed_x'], e['speed_y'])
			e['rect'].move_ip(e['amplitude_x']*math.sin(angle), e['amplitude_y']*math.sin(angle))
			pl = polygon_pointlist(e['rect'].centerx, e['rect'].centery, ((-12,0),(0,-12),(12,0),(0,12)))
			pygame.draw.polygon(windowSurface, WHITE, pl, 1)
			pl = polygon_pointlist(e['rect'].centerx, e['rect'].centery, ((-8,0),(0,-8),(8,0),(0,8)))
			pygame.draw.polygon(windowSurface, WHITE, pl, 1)
		elif e['type'] == 4:
			e['rect'].move_ip(e['speed_x'], e['speed_y'])
			pl = polygon_pointlist(e['rect'].centerx, e['rect'].centery, ((-20,-5),(-10,-20),(10,-20),(20,-5),(20,5),(10,20),(-10,20),(-20,5)))
			pygame.draw.polygon(windowSurface, WHITE, pl, 1)
			#pygame.draw.arc(windowSurface, WHITE, (e['rect'].left-20, e['rect'].top-10, 20, 20), 0, 3.3, 1)
			pygame.draw.ellipse(windowSurface, WHITE, (e['rect'].left-20, e['rect'].top, 20, 60), 1)
			pygame.draw.ellipse(windowSurface, WHITE, (e['rect'].right, e['rect'].top, 20, 60), 1)
		elif e['type'] == 5:
			e['angle'] += e['shoot_rate']
			angle = math.radians(e['angle'])
			e['rect'].move_ip(e['speed_x'], e['speed_y'])
			pl = polygon_pointlist_rot2(e['rect'].centerx, e['rect'].centery, angle, m1_poly)
			pygame.draw.polygon(windowSurface, WHITE, pl, 1)
		elif e['type'] == 6:
			e['angle'] += e['shoot_rate']
			angle = math.radians(e['angle'])
			e['rect'].move_ip(e['speed_x'], e['speed_y'])
			pl = polygon_pointlist_rot2(e['rect'].centerx, e['rect'].centery, angle, m2_poly)
			pygame.draw.polygon(windowSurface, WHITE, pl, 1)
		elif e['type'] == 7:
			e['angle'] += e['shoot_rate']
			angle = math.radians(e['angle'])
			e['rect'].move_ip(e['speed_x'], e['speed_y'])
			pl = polygon_pointlist_rot2(e['rect'].centerx, e['rect'].centery, angle, m3_poly)
			pygame.draw.polygon(windowSurface, WHITE, pl, 1)
		#Delete Enemy if over Screen
		if (e['rect'].top > WINDOWHEIGHT*2) or (e['rect'].bottom < -WINDOWHEIGHT) or (e['rect'].left < -WINDOWWIDTH) or (e['rect'].right > WINDOWWIDTH*2):
			enemys.remove(e)
		#Player Collide
		if e['rect'].colliderect(player['rect']):
			#Create Explosion
			if player['status'] == "normal":
				player['status'] = "dead"
				add_lives(-1)
				enemy_destroyed(e,player, 10)
				#if sound_enable == True:
					#expl6_sound.play(0,0,0)
				play_sound(expl6_sound, 0, 0, 0, 0, 0)
				new_novawave(player['rect'].centerx, player['rect'].centery, 25)
				new_explosion(50, player['rect'].centerx, player['rect'].centery)
				new_truemmer(3, player['rect'].centerx, player['rect'].centery, 5)
		#Create the Shoots random
		if e['shoot_rate'] > 0:	
			if random.randint(0, e['shoot_rate']) == 0:
				if e['shoot_type'] == 1:
					enemys_shoots.append({'rect':pygame.Rect( e['rect'].left + 5,  e['rect'].top + 5, 10, 10), 'type':1, 'angle':(e['angle']*math.pi)/180, 'speed':4})
				elif e['shoot_type'] == 2:
					enemys_shoots.append({'rect':pygame.Rect( e['rect'].left + 5,  e['rect'].top + 5, 10, 10), 'type':1, 'angle':(e['angle']*math.pi)/180, 'speed':8})
				elif e['shoot_type'] == 3:
					enemys_shoots.append({'rect':pygame.Rect( e['rect'].left + 5,  e['rect'].top + 5, 10, 10), 'type':1, 'angle':(e['angle']*math.pi)/180, 'speed':16})
				elif e['shoot_type'] == 4:
					enemys_shoots.append({'rect':pygame.Rect( e['rect'].left + 5,  e['rect'].top + 5, 10, 10), 'type':3, 'angle':(e['angle']*math.pi)/180, 'speed':0})	
				elif e['shoot_type'] == 6:
					s_b = e['rect'].centerx - player['rect'].centerx
					s_a = e['rect'].centery - player['rect'].centery
					try:
						s_betta = math.atan(float(s_b)/float(s_a))
					except:
						pass
					enemys_shoots.append({'rect':pygame.Rect( e['rect'].left + 5,  e['rect'].top + 5, 10, 10), 'type':4, 'angle':s_betta, 'speed':6})
		#Create Shoots continus			
		elif e['shoot_aktivat'] == 0:
			e['shoot_aktivat'] = e['shoot_rate']*(-1)
			if e['shoot_type'] == 1:
				enemys_shoots.append({'rect':pygame.Rect( e['rect'].left + 5,  e['rect'].top + 5, 10, 10), 'type':1, 'angle':(e['angle']*math.pi)/180, 'speed':4})
			elif e['shoot_type'] == 2:
				enemys_shoots.append({'rect':pygame.Rect( e['rect'].left + 5,  e['rect'].top + 5, 10, 10), 'type':1, 'angle':(e['angle']*math.pi)/180, 'speed':8})
			elif e['shoot_type'] == 3:
				enemys_shoots.append({'rect':pygame.Rect( e['rect'].left + 5,  e['rect'].top + 5, 10, 10), 'type':1, 'angle':(e['angle']*math.pi)/180, 'speed':16})
			elif e['shoot_type'] == 4:
				enemys_shoots.append({'rect':pygame.Rect( e['rect'].left + 5,  e['rect'].top + 5, 10, 10), 'type':3, 'live_time':100})
			elif (e['shoot_type'] == 5) and (e['shoot_on_time'] == e['shoot_on_time_save']):				
					enemys_shoots.append({'rect':pygame.Rect( e['rect'].left - 13,  e['rect'].bottom + 18, 5, WINDOWHEIGHT), 'type':2, 'on_time':e['shoot_on_time'], 'speed_x':e['speed_x'], 'speed_y':e['speed_y']})
					new_partikeleffekt(e['rect'].left - 9, e['rect'].bottom+WINDOWHEIGHT/2 + 5, 20, WINDOWHEIGHT, e['speed_x'], e['speed_y'], 200, e['shoot_on_time_save'])
					enemys_shoots.append({'rect':pygame.Rect( e['rect'].right + 7,  e['rect'].bottom + 18, 5, WINDOWHEIGHT), 'type':2, 'on_time':e['shoot_on_time'], 'speed_x':e['speed_x'], 'speed_y':e['speed_y']})
					new_partikeleffekt(e['rect'].right + 9, e['rect'].bottom+WINDOWHEIGHT/2 + 5, 20, WINDOWHEIGHT, e['speed_x'], e['speed_y'], 200, e['shoot_on_time_save'])
					e['shoot_on_time'] = 0
					e['shoot_aktivat'] += e['shoot_on_time_save']	
					play_sound(laser_sound, 0, 0, 0, 0, 2400)
		#elif (e['shoot_type'] == 5) and (e['shoot_aktivat'] == 15):
				#if sound_enable == True:
						#laser_sound.play(0,0,0)
			elif e['shoot_type'] == 6:
					s_b = e['rect'].centerx - player['rect'].centerx
					s_a = e['rect'].centery - player['rect'].centery
					try:
						s_betta = math.atan(float(s_b)/float(s_a))
					except:
						pass
					enemys_shoots.append({'rect':pygame.Rect( e['rect'].left + 5,  e['rect'].top + 5, 10, 10), 'type':4, 'angle':s_betta, 'speed':6})
		try:
			if e['shoot_on_time'] < e['shoot_on_time_save']:
				e['shoot_on_time'] += 1
		except:
			pass
		e['shoot_aktivat'] -= 1
						
	#Draw Player
	if player['status'] == "normal":
		pygame.gfxdraw.trigon(windowSurface, player['rect'].left, player['rect'].bottom, player['rect'].right, player['rect'].bottom, player['rect'].left + player['rect'].width/2, player['rect'].top, WHITE)
	elif player['status'] == "dead":
		player['rect'].center = WINDOWWIDTH/2, WINDOWHEIGHT - 100
		rise_from_dead_count -= 10
	elif player['status'] == "rising":
		rise_from_dead_count += 5
		pygame.gfxdraw.trigon(windowSurface, player['rect'].left, player['rect'].bottom, player['rect'].right, player['rect'].bottom, player['rect'].left + player['rect'].width/2, player['rect'].top, (rise_from_dead_count,rise_from_dead_count,rise_from_dead_count))
		
	if (rise_from_dead_count == 0) and (lives > 0):
		player['status'] = "rising"
		new_text("READY?", WINDOWWIDTH/2, WINDOWHEIGHT/2, 40, 50, 250)
	elif (rise_from_dead_count == 250) and (player['status'] == "rising"):
		player['status'] = "normal"
		new_text("GO!", WINDOWWIDTH/2, WINDOWHEIGHT/2, 40, 50, 10)
		
	#Draw Explosions
	for ex in explosions:
		for se in ex:
			se[0] += random.randint(-10, 10)
			se[1] += random.randint(-10, 10)
			se[2] -= 5
			if se[2] >= 0:
				pygame.gfxdraw.pixel(windowSurface, se[0], se[1], (se[2], se[2], se[2]))
			else:
				ex.remove(se)
			if len(ex) == 0:	
				explosions.remove(ex)
				
	#Draw Trummer
	for ex in truemmer:
		for se in ex:
			se[0] += se[4]
			se[1] += se[5]
			se[2] -= 5
			if se[2] >= 0:
				se[3] -= 20
				tangle = (se[3]*math.pi)/180
				pygame.draw.line(windowSurface, (se[2], se[2], se[2]), (se[0]+5*math.sin(tangle), se[1]+5*math.cos(tangle)), (se[0]-5*math.sin(tangle), se[1]-5*math.cos(tangle)), 1)
			else:
				ex.remove(se)
			if len(ex) == 0:	
				truemmer.remove(ex)
				
	# draw the text onto the surface
	windowSurface.blit(points_text, points_textRect)
	windowSurface.blit(lives_text, lives_textRect)
	
	for tex in onscreen_text:
		temp = tex['font'].render(tex['text'], True, tex['color'])
		tempRect = temp.get_rect()
		tempRect.center = tex['x'], tex['y']
		windowSurface.blit(temp, tempRect)
		
		if tex['time'] == 0:
			tex['color'][1] -= tex['fading']
			tex['color'][2] -= tex['fading']
			tex['color'][0] -= tex['fading']
		else:
			tex['time'] -= 1
		if tex['color'][0] < tex['fading']:
			onscreen_text.remove(tex)
		
	#Draw Shock Waves
	for wa in shock_waves:
		if wa[4] > 7:
			wa[4] -= 3
		pygame.draw.circle(windowSurface, (25*wa[3],25*wa[3],25*wa[3]), (wa[0],wa[1]), wa[2], wa[4]/5)
		
		wa[2] += 15*wa[3]
		
		if wa[2] > 1000:
			shock_waves.remove(wa)
	
	#Draw Nova Waves
	for nw in nova_waves:			
		if (nw[0].h > 1):
			nw[0].inflate_ip(nw[1], -1)
		else:
			nova_waves.remove(nw)
			
		if nw[0].h%2 == 0:	
			nw[0].move_ip(0, 1)
			
		if nw[0].h*10 < 255:
			color = nw[0].h*10
		else:
			color = 255
			
		nw[1] -= 2
		
		try:
			pygame.draw.ellipse(windowSurface, (color,color,color), nw[0], 0)
		except:
			nova_waves.remove(nw)
	
	#Draw Partikel Effekts
	for pe in partikel_effekts:
		pe[0].move_ip(pe[2], pe[3])
		for par in pe[1]:
			if pe[0].centerx-par[0] > 0:
				par[0] += 1+pe[2]
			elif pe[0].centerx-par[0] < 0:
				par[0] -= 1-pe[2]
			elif pe[0].centerx-par[0] == 0:
				par[0] = pe[0].centerx + random.randint(-(pe[0].w/2),pe[0].w/2)
			if pe[0].centery-par[1] > 0:
				par[1] += 1+pe[3]
			elif pe[0].centery-par[1] < 0:
				par[1] -= 1-pe[3]
			elif pe[0].centery-par[1] == 0:
				par[1] = pe[0].centery + random.randint(-(pe[0].h/2),pe[0].h/2)
			pygame.gfxdraw.pixel(windowSurface, par[0], par[1], (par[2],par[2],par[2]))
		if pe[4] > 0:
			pe[4] -= 1
		else:
			partikel_effekts.remove(pe)
			
		try:
			if es['rect'].colliderect(e4_del_rect):
				partikel_effekts.remove(pe)
				partikel_effekts.remove(partikel_effekts[partikel_effekts.index(pe)])
				del e4_del_rect	#also for the Beam of the e4 special weapon
		except:
			pass

	# move the player
	if moveDown and player['rect'].bottom < WINDOWHEIGHT - 25:
		player['rect'].top += MOVESPEED
	if moveUp and player['rect'].top > 0:
		player['rect'].top -= MOVESPEED
	if moveLeft and player['rect'].left > 0:
		player['rect'].left -= MOVESPEED
	if moveRight and player['rect'].right < WINDOWWIDTH:
		player['rect'].right += MOVESPEED
	
	#Zeiche alles auf den Schirm
	pygame.display.update()
	mainClock.tick(25)