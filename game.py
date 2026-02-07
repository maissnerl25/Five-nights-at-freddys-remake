import pygame, random, sys, time

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
cam_images = {
    0: pygame.transform.scale(pygame.image.load("assets/cam0.png"), (width, height)),
    1: pygame.transform.scale(pygame.image.load("assets/cam1.png"), (width, height)),
    2: pygame.transform.scale(pygame.image.load("assets/cam2.png"), (width, height)),
    3: pygame.transform.scale(pygame.image.load("assets/cam3.png"), (width, height)),
}

fred_img = pygame.image.load("assets/fred.png").convert_alpha()

jumpscare_img = pygame.transform.scale(
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
# ===== Barvy ====
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
# ===== Menu ====
button_rect = pygame.Rect(100, 250, 200, 60)

def draw_menu():
    screen.fill(BLACK)

    title = font.render("Five Nights at Freddy's", True, WHITE)
    screen.blit(menu_img, (0, 0))
    screen.blit(title, (100, 150))

    # Tlačítko
    pygame.draw.rect(screen, BLACK, button_rect)
    text = font.render("New Game", True, WHITE)
    screen.blit(text, (button_rect.x + 30, button_rect.y + 10))

# ===== Energie =====
power = 100.0

# ===== ČAS =====
current_time = pygame.time.get_ticks()
last_switch = 0
hour = 12
time_counter = 0
TIME_PER_HOUR = 20 + (10 * night)  # kolik sekund trvá 1 hodina ve hře

# ===== Dveře a světlo =====
left_door_closed = False
light_on = False

# ===== Freddy =====
fred_rooms = [1, 2, 3, "door"]
fred_pos = 0
fred_loc = fred_pos
#======= Movement Freddyho ====
movement_oppurtunity_fred = 0
fred_AI = random.randint(1, 4)

def fred_move():
    global movement_oppurtunity_fred, fred_AI, fred_AI, fred_pos

    movement_oppurtunity_fred = random.randint(1, 20)
    if movement_oppurtunity_fred <= fred_AI:
        fred_pos += 1
        if fred_pos > len(fred_rooms):
            fred_pos -= 1

def jumpscare():
    screen.blit(jumpscare_img, (0, 0))
    sound_jumpscare.play()

def win():
    global game_state, night
    game_state = "win"
    night += 1

def game_over():
    global game_state
    game_state = "gameover"
    jumpscare()

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



def get_night_settings(night):
    if night == 1:
        return 0.002, 0.01 # movement oppurtunity, drain
    elif night == 2:
        return 0.003, 0.015
    elif night == 3:
        return 0.004, 0.02
    elif night == 4:
        return 0.005, 0.025
    elif night == 5:
        return 0.007, 0.03

while True:
    dt = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                game_state = "loading"
                loading_start_time = pygame.time.get_ticks()
                

        if event.type == pygame.KEYDOWN and (game_state == "office" or game_state == "camera"):

            # Kamery
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

            # Dveře
            if event.key == pygame.K_d and game_state == "office":
                left_door_closed = not left_door_closed
                if left_door_closed:
                    sound_door.play()
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
    # ====== Freddy movement ====¨
    if fred_loc != fred_pos:
        sound_step.play()
        fred_loc = fred_pos

    #====== Drain ====
    if game_state != "menu":
        drain = 0.01
        if game_state == "camera":
            drain += 0.03
        if left_door_closed:
            drain += 0.05
        if light_on:
            drain += 0.2
    # ===== LOADING SCREEN ====
    if game_state == "loading":
        current_time = pygame.time.get_ticks()
        if current_time - loading_start_time > 3000: 
            game_state = "office"

    # ===== Vykreslení =====
    screen.fill((0, 0, 0))

    if game_state == "menu":
        draw_menu()
    
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
        screen.blit(cam_images[current_camera], (0, 0))

        fred_loc = fred_rooms[fred_pos]
        if fred_loc == current_camera:
            if fred_loc == 1:
                screen.blit(fred_img, (width / 2.67, height / 2))

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
                if night < max_nights:
                    night += 1
                    reset_night()
                elif night == 7:
                    game_state = "custom_night"
                
        
    elif game_state == "gameover":
        screen.blit(jumpscare_img, (0, 0))
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
