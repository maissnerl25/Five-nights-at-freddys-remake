import pygame, random, sys, os

pygame.init()

width, height = 1200, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("FNAF Prototype")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 30)
big_font = pygame.font.SysFont(None, 80)

# ===== Načtení obrázků =====
menu_img = pygame.transform.scale(
    pygame.image.load("assets/menu.png"), (width, height)
)
office_img = pygame.transform.scale(
    pygame.image.load("assets/office.png"), (width, height)
)
office_door = pygame.transform.scale(
    pygame.image.load("assets/office.door.png"), (width, height)
)
office_light = pygame.transform.scale(
    pygame.image.load("assets/office.light.png"), (width, height)
)
loading_img = pygame.transform.scale(
    pygame.image.load("assets/newspaper.png"), (width, height)
)
office_fred_door = pygame.transform.scale(
    pygame.image.load("assets/office.fred2.png"), (width, height)
)
power_out_img = pygame.transform.scale(
    pygame.image.load("assets/power_out.png"), (width, height)
)
cam_images = {
    0: pygame.transform.scale(pygame.image.load("assets/cam0.png"), (width, height)),
    1: pygame.transform.scale(pygame.image.load("assets/cam1.png"), (width, height)),
    2: pygame.transform.scale(pygame.image.load("assets/cam2.png"), (width, height)),
    3: pygame.transform.scale(pygame.image.load("assets/cam3.png"), (width, height)),
    4: pygame.transform.scale(pygame.image.load("assets/cam4.png"), (width, height)),
}

fred_imgs = {
    1: pygame.image.load("assets/eps1.png"),
    2: pygame.image.load("assets/eps2.png").convert_alpha(),
    3: pygame.image.load("assets/eps3.png")         
}          
bon_imgs = { 
    1: pygame.image.load("assets/bonnie.png").convert_alpha()
}

chica_imgs = {
    1: pygame.image.load("assets/chirk1.png").convert_alpha(),
}  
jumpscare_freddy_img = pygame.transform.scale(
    pygame.image.load("assets/jumpscare.png"), (width, height)
)
# ===== Zvuky =====
sound_cam = pygame.mixer.Sound("assets/sound_cam.wav")
sound_door = pygame.mixer.Sound("assets/sound_door.wav")
sound_step = pygame.mixer.Sound("assets/sound_step.wav")
sound_jumpscare = pygame.mixer.Sound("assets/sound_jumpscare.wav")

# ===== Stav hry =====
game_state = "menu"   # office / camera / win / gameover / menu
current_camera = 1
in_camera = False
night = 1
max_nights = 6
power_out = False
power_out_start = 0
# ===== Barvy ====
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
# ===== Kamery buttony ====
cam_buttons = {
    1: pygame.Rect(950, 500, 80, 60),
    2: pygame.Rect(1030, 450, 80, 60),
    3: pygame.Rect(1030, 550, 80, 60),
    4: pygame.Rect(1100, 500, 80, 60),
}
# ===== Nights buttony ====
night_buttons = {
    1: pygame.Rect(100, 250, 200, 50),
    2: pygame.Rect(100, 310, 200, 50),
    3: pygame.Rect(100, 370, 200, 50),
    4: pygame.Rect(100, 430, 200, 50),
    5: pygame.Rect(100, 490, 200, 50),
    6: pygame.Rect(100, 550, 200, 50),
}
reset_button = pygame.Rect(100, 610, 200, 50)

custom_button = pygame.Rect(100, 700, 200, 50)
# ===== Custom night buttony ====
freddy_left = pygame.Rect(250,400,40,40)
freddy_right = pygame.Rect(350,400,40,40)

bonnie_left = pygame.Rect(550,400,40,40)
bonnie_right = pygame.Rect(650,400,40,40)

chica_left = pygame.Rect(850,400,40,40)
chica_right = pygame.Rect(950,400,40,40)

foxy_left = pygame.Rect(1150,400,40,40)
foxy_right = pygame.Rect(1250,400,40,40)

# ===== Cutom night ====
custom_freddy_ai = 1
custom_bonnie_ai = 1
custom_chica_ai = 1

# ===== Menu ====

def draw_menu():
    screen.fill(BLACK)

    title = font.render("Five Nights at Freddy's", True, WHITE)
    screen.blit(menu_img, (0, 0))
    screen.blit(title, (100, 150))

    #Reset night
def get_night_settings(night):
    if night == 1:
        return random.randint(0, 3),random.randint(2, 6),random.randint(1, 5), 0.01 # freddy AI, bonnie AI, chica AI, drain
    elif night == 2:
        return random.randint(3, 5),random.randint(6, 8),random.randint(6, 8), 0.015
    elif night == 3:
        return random.randint(5, 8),random.randint(9, 12),random.randint(9, 11), 0.02
    elif night == 4:
        return random.randint(9, 10),random.randint(13, 15),random.randint(12, 14), 0.025
    elif night == 5:
        return random.randint(11, 15),random.randint(16, 18),random.randint(15, 18), 0.03

# ===== Energie =====
power = 100.0

# ===== ČAS =====
current_time = pygame.time.get_ticks()
last_switch = 0
hour = 12
time_counter = 0
TIME_PER_HOUR = 20 + (10 * night)  # kolik sekund trvá 1 hodina ve hře
wait_start_time = 0
wait_start_time_bon = 0
loading_start_time = 0
fred_door_timer = None
fred_AI, bonnie_AI, chica_AI, drain_base = get_night_settings(night)
# ===== Dveře a světlo =====
left_door_closed = False
light_on = False

# ===== Freddy =====
fred_rooms = [1, 2, 3, "door"]
fred_pos = 0
fred_loc = fred_rooms[fred_pos]
fred_pr_loc = fred_loc
#======= Movement Freddyho ====
movement_oppurtunity_fred = 0

def fred_move():
    if game_state != "menu":
        if game_state != "loading":
        
            global movement_oppurtunity_fred, fred_AI, fred_pos, wait_start_time    
#====== ATTACK CHECK ====
        
            fred_loc = fred_rooms[fred_pos]
            if fred_loc == "door":
                if left_door_closed:
                    fred_pos = 0
                    wait_start_time = pygame.time.get_ticks()
                else:
                    game_over()

            if wait_start_time == 0:
                    wait_start_time = pygame.time.get_ticks()

            wait_fred = pygame.time.get_ticks() - wait_start_time

            if wait_fred > 7000:
                wait_start_time = pygame.time.get_ticks()

                movement_oppurtunity_fred = random.randint(1, 20)
                print(movement_oppurtunity_fred, fred_AI)
                print(fred_pos)

                if movement_oppurtunity_fred <= fred_AI:
                    fred_pos += 1

                    if fred_pos >= len(fred_rooms):
                        fred_pos -= 1
                    wait_start_time = pygame.time.get_ticks()  # RESET TIMERU
# ======= BONNIE ====
bon_rooms = [1, 2, 3, "door"]
bon_pos = 0
bon_loc = bon_rooms[bon_pos]
bon_pr_loc = bon_loc
# ======= MOVEMENT BONNIE ====
movement_oppurtunity_bon = 0


def bon_move():
    global bon_pos, wait_start_time_bon

    bon_loc = bon_rooms[bon_pos]

    if bon_loc == "door":
        if left_door_closed:
            bon_pos = 0
        else:
            game_over()

    if wait_start_time_bon == 0:
        wait_start_time_bon = pygame.time.get_ticks()

    wait = pygame.time.get_ticks() - wait_start_time_bon

    if wait > 5000:   
        wait_start_time_bon = pygame.time.get_ticks()

        movement_oppurtunity_bon = random.randint(1,20)

        if movement_oppurtunity_bon <= bonnie_AI:
            bon_pos += 1

            if bon_pos >= len(bon_rooms):
                bon_pos = len(bon_rooms)-1

            sound_step.play()
# ====== Chirk ====
chica_rooms = [1, 2, 3, "door"]
chica_pos = 0
chica_loc = chica_rooms[chica_pos]
chica_pr_loc = chica_loc

# ===== Movement Chirk ====
wait_start_time_chica = 0

def chica_move():
    global chica_pos, wait_start_time_chica

    chica_loc = chica_rooms[chica_pos]

    if chica_loc == "door":
        if left_door_closed:
            chica_pos = 0
        else:
            game_over()

    if wait_start_time_chica == 0:
        wait_start_time_chica = pygame.time.get_ticks()

    wait = pygame.time.get_ticks() - wait_start_time_chica

    if wait > 6000:
        wait_start_time_chica = pygame.time.get_ticks()

        movement_oppurtunity_chica = random.randint(1,20)

        if movement_oppurtunity_chica <= chica_AI:
            chica_pos += 1

            if chica_pos >= len(chica_rooms):
                chica_pos = len(chica_rooms)-1

            sound_step.play()



def jumpscare_fred():
    screen.blit(jumpscare_freddy_img, (0, 0))
    sound_jumpscare.play()

def win():
    global game_state, night, max_unlocked_night
    game_state = "win"
    if night == max_unlocked_night and max_unlocked_night < 6:
        max_unlocked_night += 1
    save_progress(max_unlocked_night)

def game_over():
    global game_state
    game_state = "gameover"
    jumpscare_fred()

def draw_static():

    # noise pixely
    for i in range(2000):
        x = random.randint(0,width)
        y = random.randint(0,height)

        c = random.randint(150,255)
        screen.set_at((x,y),(c,c,c))

    # scan lines
    for y in range(0,height,4):
        pygame.draw.line(screen,(30,30,30),(0,y),(width,y),1)

def reset_night():
    global power, hour, time_counter, anim_pos
    global left_door_closed, light_on, current_camera, game_state

    power = 100.0
    hour = 12
    time_counter = 0

    anim_pos = 0
    left_door_closed = False
    light_on = False
    current_camera = 1

    game_state = "office"

def load_progress():
    if os.path.exists("save.txt"):
        with open("save.txt", "r") as f:
            return int(f.read())
    return 1

def save_progress(max_night):
    with open("save.txt", "w") as f:
        f.write(str(max_night))

def reset_progress():
    global max_unlocked_night
    
    max_unlocked_night = 1
    
    if os.path.exists("save.txt"):
        os.remove("save.txt")

# Nights
max_unlocked_night = load_progress()

while True:
    dt = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == "camera" and event.type == pygame.MOUSEBUTTONDOWN:
            for cam, rect in cam_buttons.items():
                  if rect.collidepoint(event.pos):
                    current_camera = cam
                    sound_cam.play()

        if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            for n, rect in night_buttons.items():
                if rect.collidepoint(event.pos) and n <= max_unlocked_night:
                    night = n
                    fred_AI,bonnie_AI, chica_AI, drain_base = get_night_settings(night)

                    game_state = "loading"
                    loading_start_time = pygame.time.get_ticks()

        if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            if reset_button.collidepoint(event.pos):
                reset_progress()
            if custom_button.collidepoint(event.pos):
                game_state = "custom"

        if game_state == "custom" and event.type == pygame.MOUSEBUTTONDOWN:

            if freddy_left.collidepoint(event.pos):
                freddy_ai = max(0, custom_freddy_ai-1)

            if freddy_right.collidepoint(event.pos):
                freddy_ai = min(20, freddy_ai+1)


            if bonnie_left.collidepoint(event.pos):
                bonnie_ai = max(0, bonnie_ai-1)

            if bonnie_right.collidepoint(event.pos):
                bonnie_ai = min(20, bonnie_ai+1)


            if chica_left.collidepoint(event.pos):
                chica_ai = max(0, chica_ai-1)

            if chica_right.collidepoint(event.pos):
                chica_ai = min(20, chica_ai+1)


            if foxy_left.collidepoint(event.pos):
                foxy_ai = max(0, foxy_ai-1)

            if foxy_right.collidepoint(event.pos):
                foxy_ai = min(20, foxy_ai+1)
                
        if event.type == pygame.KEYDOWN and (game_state == "office" or game_state == "camera"):

            #Kamery
            if event.key == pygame.K_c:
                game_state = "camera" if game_state == "office" else "office"
            # Přepínání kamer
            if game_state == "camera":
                if event.key == pygame.K_1:
                    current_camera = 1
                    sound_cam.play()
                if event.key == pygame.K_2:
                    current_camera = 2
                    sound_cam.play()
                if event.key == pygame.K_3:
                    current_camera = 3
                    sound_cam.play()
                if event.key == pygame.K_4:
                    current_camera = 4

            # Dveře
            if event.key == pygame.K_d and game_state == "office":
                left_door_closed = not left_door_closed
                if left_door_closed:
                    sound_door.play()
                    print()
                if light_on == True:
                    light_on = not light_on

            # Světlo
            if event.key == pygame.K_l and game_state == "office":
                light_on = not light_on
                

            #secret
            if event.key == pygame.K_o:
                win()
            if event.key == pygame.K_p:
                game_over()
            if event.key == pygame.K_i:
                fred_pos += 1
                print(fred_pos)
                if fred_pos > 3:
                    if left_door_closed == True:
                        fred_pos = 0
                    else:
                        game_over()
            if event.key == pygame.K_u:
                fred_AI = 20
            if event.key == pygame.K_z:
                power = 0
    # ====== Freddy movement ====
    fred_move()
    fred_new_loc = fred_rooms[fred_pos]
    if fred_new_loc != fred_loc:
        sound_step.play()
        fred_loc = fred_new_loc
    bon_move()
    bon_new_loc = bon_rooms[bon_pos]
    if bon_new_loc != bon_loc:
        sound_step.play()
        bon_loc = bon_new_loc
    chica_move()
    chica_new_loc = chica_rooms[chica_pos]
    if chica_new_loc != chica_loc:
        sound_step.play()
        chica_loc = chica_new_loc

    #====== Drain ====
    if game_state != "menu":
        drain = drain_base
        if game_state == "camera":
            drain += 0.03
        if left_door_closed:
            drain += 0.05
        if light_on:
            drain += 0.2


    #power -= drain * dt * 60

    if power <= 0 and not power_out:
        power = 0
        power_out = True
        game_state = "power_out"
        left_door_closed = False
        light_on = False
        power_out_start = pygame.time.get_ticks()

    # ===== LOADING SCREEN ====
    if game_state == "loading":
        current_time = pygame.time.get_ticks()
        if current_time - loading_start_time > 3000: 
            game_state = "office"

    # ===== Vykreslení =====
    screen.fill((0, 0, 0))

    if game_state == "menu":
        draw_menu()
        font = pygame.font.SysFont(None, 40)

        font = pygame.font.SysFont(None, 40)
        pygame.draw.rect(screen,(80,20,20),reset_button)
        pygame.draw.rect(screen,(255,255,255),reset_button,2)

        pygame.draw.rect(screen,(40,40,40),custom_button)
        pygame.draw.rect(screen,(255,255,255),custom_button,2)

        text = font.render("CUSTOM NIGHT", True,(255,255,255))
        screen.blit(text,(custom_button.x+10, custom_button.y+10))

        reset_text = font.render("      RESET", True,(255,255,255))
        screen.blit(reset_text,(reset_button.x+10, reset_button.y+10))
        
    for n, rect in night_buttons.items():

        if n <= max_unlocked_night:
            color = (50,50,50)
            text = f"Night {n}"
        else:
            color = (30,30,30)
            text = f"Night {n} 🔒"

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen,(255,255,255),rect,2)

        txt = font.render(text, True, (255,255,255))
        screen.blit(txt,(rect.x + 40, rect.y + 10))
    
    if game_state == "loading":
        screen.blit(loading_img, (0, 0))

    if game_state == "office" and not left_door_closed:
        screen.blit(office_img, (0, 0))
        if light_on:
            if fred_pos == 3:
                screen.blit(office_fred_door, (0, 0))
            else:
                screen.blit(office_light, (0, 0))
            

    elif game_state == "office" and left_door_closed:
        screen.blit(office_door, (0, 0))
        

    elif game_state == "camera":
        screen.blit(cam_images[current_camera], (0,0))
        # Freddy kamery
        fred_loc = fred_rooms[fred_pos]
        if fred_pos >= len(fred_rooms):
            fred_pos -= 1
        if fred_loc == current_camera:
            if fred_loc == 1:
                screen.blit(fred_imgs[1], (width / 3.67, height / 2))
            if fred_loc == 2:
                screen.blit(fred_imgs[2], (width / 3, height / 3))
            if fred_loc == 3:
                screen.blit(fred_imgs[3], (width / 2.67, height / 3))
        # Bonnie kamery
        bon_loc = bon_rooms[bon_pos]
        if bon_pos >= len(bon_rooms):
            bon_pos -= 1
        if bon_loc == current_camera:
            if bon_loc == 1:
                screen.blit(bon_imgs[1], (width / 2.67, height / 2))
            if bon_loc == 2:
                screen.blit(bon_imgs[1], (width / 1, height / 1))
            if bon_loc == 3:
                screen.blit(bon_imgs[1], (width / 2.67, height / 2))
        # Chica kamery
        chica_loc = chica_rooms[chica_pos]

        if chica_pos >= len(chica_rooms):
            chica_pos -= 1

        if chica_loc == current_camera:
            if chica_loc == 1:
                screen.blit(chica_imgs[1], (width / 3, height / 2))
            if chica_loc == 2:
                screen.blit(chica_imgs[1], (width / 2.5, height / 2.5))
            if chica_loc == 3:
                screen.blit(chica_imgs[1], (width / 2, height / 2))

                # Camera mapa
        for cam, rect in cam_buttons.items():
            pygame.draw.rect(screen, (0,150,0), rect, 2)
            text = font.render(str(cam), True, (0,255,0))
            screen.blit(text, (rect.x + 30, rect.y + 20))
        draw_static()
        screen.blit(font.render(f"CAMERA {current_camera}", True, (0, 255, 0)), (20, 40))

    elif game_state == "win":
        if 'win_start_time' not in globals():
            win_start_time = pygame.time.get_ticks()
        elapsed = pygame.time.get_ticks() - win_start_time
        if elapsed < 1000:
            time_win = big_font.render("5 AM", True, (WHITE))
            time_win_rect = time_win.get_rect(center=(width / 2, height / 2))
            screen.blit(time_win, time_win_rect)
        else:
            time_win = big_font.render("6 AM", True, (WHITE))
            time_win_rect = time_win.get_rect(center=(width / 2, height / 2))
            screen.blit(time_win, time_win_rect)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                reset_night()
                
    elif game_state == "power_out":
        screen.fill((0,0,0))

        text = big_font.render("POWER OUT", True, (255,0,0))
        screen.blit(text, (width/2 - 200, height/2 - 50))

        if pygame.time.get_ticks() - power_out_start > 5000:
            game_over()           
        
    elif game_state == "gameover":
        screen.blit(jumpscare_freddy_img, (0, 0))
        text = big_font.render("GAME OVER", True, (255, 0, 0))
        #screen.blit(text, (200, 250))

    # HUD
    if game_state != "menu":
        if game_state != "loading":
            if game_state != "gameover":
                power_text = font.render(f"POWER: {int(power)}%", True, (255, 255, 0))
                time_text = font.render(f"TIME: {hour} AM", True, (0, 200, 255))
                night_text = font.render(f"{night}. NIGHT", True, (255, 255, 255))
                screen.blit(power_text, (20, 20))
                screen.blit(time_text, (width - 200, 20))
                screen.blit(night_text, (width - 200, 60))

    pygame.display.flip()
