import pygame
import random
import math

pygame.init()
pygame.font.init()    #init
pygame.mixer.init()

WIDTH, HEIGHT = 1780, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))    #WIN size(background)
pygame.display.set_caption("Spaceship and Survival")

# Background Music Files
bg_opening = "spaceship_opening_screen.mp3"
bg_start_game = "spaceship-door-opening-43604.mp3"
bg_gameover_01 = "gameover_01.mp3"
bg_gameover_02 = "game-over_02.mp3"
bg_continue = "game_continue.mp3"

# Game Stats
game_attempts = 0

# Sound Effects
# Sound Effects
enemy_sounds = [
    pygame.mixer.Sound("alien_scary_atmosphere.mp3"),
    pygame.mixer.Sound("alien-scary.mp3")
]

# Set volume lower for alien scary sounds
for sound in enemy_sounds:
    sound.set_volume(0.3)  # Lower background alien scary sounds to 30% volume

green_laser_sound = pygame.mixer.Sound("green_laser.mp3")
darkblue_laser_sound = pygame.mixer.Sound("darkblue_laser.mp3")
red_laser_sound = pygame.mixer.Sound("red_laser.mp3")
hero_explode_sound = pygame.mixer.Sound("blue_laser.mp3")
trap_warning_sound = pygame.mixer.Sound("blue_laser.mp3")  

enemy_explode_sounds = [
    pygame.mixer.Sound("explode_01.mp3"),
    pygame.mixer.Sound("explode_02.mp3"),
    pygame.mixer.Sound("explode_03.mp3")
]

pygame.mixer.set_num_channels(64)

# Set full volume for important game sounds
green_laser_sound.set_volume(1.0)
darkblue_laser_sound.set_volume(1.0)
red_laser_sound.set_volume(1.0)
hero_explode_sound.set_volume(1.0)
trap_warning_sound.set_volume(1.0)
for sound in enemy_explode_sounds:
    sound.set_volume(1.0)




# Load images
myShip_1 = pygame.transform.scale(pygame.image.load("hero01.png"), (50, 50))
myShip_2 = pygame.transform.scale(pygame.image.load("hero02.png"), (50, 50))
myShip_3 = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("hero03.png"), (50, 50)), 90)
laser_1 = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("laser01.png"), (80, 10)), 268)
laser_2 = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("laser02.png"), (50, 50)), -43)
laser_4 = pygame.transform.scale(pygame.image.load("laser04.png"), (50, 50))
myEnemy_1 = pygame.transform.scale(pygame.image.load("enemy01.png"), (50, 50))
myEnemy_2 = pygame.transform.scale(pygame.image.load("enemy02.png"), (50, 50))
myEnemy_3 = pygame.transform.scale(pygame.image.load("enemy03.png"), (50, 50))

blackHole01 = {
    "image": pygame.transform.scale(pygame.image.load("enemy_laser01.png"), (50, 50)),
    "name": "enemy_laser01.png"
}
blackHole02 = {
    "image": pygame.transform.scale(pygame.image.load("enemy_laser02.png"), (50, 50)),
    "name": "enemy_laser02.png"
}
blackHole03 = {
    "image": pygame.transform.scale(pygame.image.load("enemy_laser03.png"), (50, 50)),
    "name": "enemy_laser03.png"
}
trap_warning_sound = pygame.mixer.Sound("blue_laser.mp3")  # add a simple trap warning sound file

# Rotation angles for black holes
blackhole_rotation_angles = {
    "enemy_laser01.png": 0,
    "enemy_laser02.png": 0,
    "enemy_laser03.png": 0
}

BG = pygame.transform.scale(pygame.image.load("gameplay_background.jpg"), (WIDTH, HEIGHT))  #image use for WIN


#ship for class enemy and player
class Ship:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.cooldown_counter = 0

    def draw(self, window):
        window.blit(self.ship_image, (self.x, self.y))  

    def get_width(self):
        return self.ship_image.get_width()

    def get_height(self):
        return self.ship_image.get_height()

#laser movement
class Laser:
    def __init__(self, x, y, dir_x, dir_y, color=(255, 0, 0), speed=5, image=None):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = speed
        self.color = color
        self.radius = 4
        self.image = image

    def move(self):
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed

    def draw(self, window):
        if self.image:
            if isinstance(self.image, dict):  # enemy laser (blackhole)
                image = self.image["image"]
                image_name = self.image["name"]
                angle = blackhole_rotation_angles.get(image_name, math.degrees(math.atan2(-self.dir_y, self.dir_x)) - 90)
            else:  # player laser
                image = self.image
                angle = math.degrees(math.atan2(-self.dir_y, self.dir_x)) - 90

            rotated_image = pygame.transform.rotate(image, angle)
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            window.blit(rotated_image, rect.topleft)
        else:
            pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)



    def off_screen(self):
        return not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT)

    def collide(self, target): 
        return target.x < self.x < target.x + target.get_width() and target.y < self.y < target.y + target.get_height()
    
class Trap:
    def __init__(self, direction, delay=120):
        self.direction = direction
        self.delay = delay  # Frames to show warning before real attack
        self.timer = 0
        self.warning_shown = True
        self.hit_registered = False  # To avoid double damage
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)

    def update(self):
        self.timer += 1
        if self.timer >= self.delay:
            self.warning_shown = False  # After delay, fire real laser

    def draw(self, window):
        if self.warning_shown:
            color = (255, 255, 255)  # white warning
        else:
            color = (255, 0, 0)  # red attack

        if self.direction == "top" or self.direction == "bottom":
            start = (self.x, 0)
            end = (self.x, HEIGHT)
        else:  # left or right
            start = (0, self.y)
            end = (WIDTH, self.y)

        pygame.draw.line(window, color, start, end, 5 if not self.warning_shown else 2)

    def check_collision(self, player):
        if not self.warning_shown and not self.hit_registered:
            if self.direction in ["top", "bottom"]:
                if abs(player.x + player.get_width()//2 - self.x) < 10:
                    self.hit_registered = True
                    return True
            else:
                if abs(player.y + player.get_height()//2 - self.y) < 10:
                    self.hit_registered = True
                    return True
        return False


class Player(Ship):
    def __init__(self, x, y, health=5):
        super().__init__(x, y, health)
        self.ship_image = myShip_1
        self.laser_image = laser_4
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health
    def draw(self, window):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (self.x + self.get_width() // 2)
        dy = mouse_y - (self.y + self.get_height() // 2)
        angle = math.degrees(math.atan2(-dy, dx)) - 90
        rotated_ship = pygame.transform.rotate(self.ship_image, angle)
        new_rect = rotated_ship.get_rect(center=(self.x + self.get_width() // 2, self.y + self.get_height() // 2))
        window.blit(rotated_ship, new_rect.topleft)
    def shoot(self, target_pos):
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        dist = math.hypot(dx, dy) or 1
        dir_x = dx / dist
        dir_y = dy / dist

        ship_center_x = self.x + self.get_width() // 2
        ship_center_y = self.y + self.get_height() // 2
        laser = Laser(ship_center_x, ship_center_y, dir_x, dir_y, color=(0, 0, 255), image=self.laser_image)
        self.lasers.append(laser)

        if self.laser_image == laser_4:
            green_laser_sound.play()
        elif self.laser_image == laser_2:
            darkblue_laser_sound.play()
        elif self.laser_image == laser_1:
            red_laser_sound.play()


class Enemy(Ship):
    def __init__(self, x, y, enemy_type):
        super().__init__(x, y)
        self.type = enemy_type
        if enemy_type == 1:
            self.ship_image = myEnemy_1
            self.laser_image = blackHole01
            self.speed = 1
        elif enemy_type == 2:
            self.ship_image = myEnemy_2
            self.laser_image = random.choice([blackHole02, blackHole03])
            self.speed = 1
        else:
            self.ship_image = myEnemy_3
            self.laser_image = None
            self.speed = 2
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.shoot_cooldown = random.randint(30, 90)

    def move(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy) or 1
        self.x += self.speed * dx / dist
        self.y += self.speed * dy / dist

    def shoot(self, player):
        if self.laser_image:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.hypot(dx, dy) or 1
            dir_x = dx / dist
            dir_y = dy / dist
            ship_center_x = self.x + self.get_width() // 2
            ship_center_y = self.y + self.get_height() // 2
            laser = Laser(ship_center_x, ship_center_y, dir_x, dir_y, image=self.laser_image)
            self.lasers.append(laser)

    def move_laser(self, player):
        for laser in self.lasers[:]:
            laser.move()
            if laser.collide(player):
                player.health -= 2
                hero_explode_sound.play()
                self.lasers.remove(laser)
            elif laser.off_screen():
                self.lasers.remove(laser)

def choose_player_ship():
    ships = [(myShip_1, laser_4), (myShip_2, laser_2), (myShip_3, laser_1)]
    labels = ["Ship 1", "Ship 2", "Ship 3"]
    BG_opening = pygame.transform.scale(pygame.image.load("gamestarter_background.jpg"), (WIDTH, HEIGHT))
    title_font = pygame.font.SysFont("comicsans", 60)

    while True:
        WIN.blit(BG_opening, (0, 0))
        WIN.blit(title_font.render("Choose Your Ship", True, (255, 255, 255)), (WIDTH//2 - 200, 50))

        for i, (ship, _) in enumerate(ships):
            x = 200 + i * 450
            y = HEIGHT//2 - 100
            WIN.blit(ship, (x, y))
            label = title_font.render(labels[i], True, (255, 255, 255))
            WIN.blit(label, (x, y + 70))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i in range(len(ships)):
                    x = 200 + i * 450
                    y = HEIGHT//2 - 100
                    if x <= mx <= x + 50 and y <= my <= y + 50:
                        return ships[i]
# Music Control Functions
def play_opening_music():
    pygame.mixer.music.load(bg_opening)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

def play_start_game_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.load(bg_start_game)
    pygame.mixer.music.play()

def play_gameover_music():
    global game_attempts
    game_attempts += 1
    if game_attempts >= 3:
        pygame.mixer.music.load(bg_gameover_02)
    else:
        pygame.mixer.music.load(bg_gameover_01)
    pygame.mixer.music.play()

def play_continue_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.load(bg_continue)
    pygame.mixer.music.play()

def play_enemy_entry_sound():
    global enemy_sound_played
    if not enemy_sound_played:
        sound_path = random.choice(["alien_scary_atmosphere.mp3", "alien-scary.mp3"])
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)  # Loop scary sound
        enemy_sound_played = True

def wave1_boss_logic(active_boss, player):
    # Random movement
    active_boss.x += random.choice([-1, 0, 1]) * 3
    active_boss.y += random.choice([-1, 0, 1]) * 2
    active_boss.x = max(0, min(active_boss.x, WIDTH - active_boss.get_width()))
    active_boss.y = max(0, min(active_boss.y, HEIGHT - active_boss.get_height()))

    # Shoot blackholes
    active_boss.shoot_cooldown -= 1
    if active_boss.shoot_cooldown <= 0:
        active_boss.shoot(player)
        active_boss.shoot_cooldown = random.randint(30, 70)

    for laser in active_boss.lasers[:]:
        laser.move()
        laser.draw(WIN)
        if laser.collide(player):
            player.health -= 2
            hero_explode_sound.play()
            active_boss.lasers.remove(laser)
        elif laser.off_screen():
            active_boss.lasers.remove(laser)

def wave2_boss_logic(active_boss, player):
    # Chase player
    dx = player.x - active_boss.x
    dy = player.y - active_boss.y
    dist = math.hypot(dx, dy) or 1
    active_boss.x += 3 * dx / dist
    active_boss.y += 3 * dy / dist

    active_boss.x = max(0, min(active_boss.x, WIDTH - active_boss.get_width()))
    active_boss.y = max(0, min(active_boss.y, HEIGHT - active_boss.get_height()))

    # Shoot blackholes
    active_boss.shoot_cooldown -= 1
    if active_boss.shoot_cooldown <= 0:
        active_boss.shoot(player)
        active_boss.shoot_cooldown = random.randint(30, 70)

    for laser in active_boss.lasers[:]:
        laser.move()
        laser.radius = 10
        laser.draw(WIN)
        if laser.collide(player):
            player.health -= 2
            hero_explode_sound.play()
            active_boss.lasers.remove(laser)
        elif laser.off_screen():
            active_boss.lasers.remove(laser)

    # Touch player
    if player.x < active_boss.x + active_boss.get_width() and player.x + player.get_width() > active_boss.x and \
       player.y < active_boss.y + active_boss.get_height() and player.y + player.get_height() > active_boss.y:
        player.health -= 20
        active_boss.health += 5

def wave3_boss_logic(active_boss, player):
    # Shoot and chase
    active_boss.shoot_cooldown -= 1
    if active_boss.shoot_cooldown <= 0:
        active_boss.shoot(player)
        active_boss.shoot_cooldown = random.randint(30, 70)

    dx = player.x - active_boss.x
    dy = player.y - active_boss.y
    dist = math.hypot(dx, dy) or 1
    active_boss.x += 2 * dx / dist
    active_boss.y += 2 * dy / dist

    active_boss.x = max(0, min(active_boss.x, WIDTH - active_boss.get_width()))
    active_boss.y = max(0, min(active_boss.y, HEIGHT - active_boss.get_height()))

    for laser in active_boss.lasers[:]:
        laser.move()
        laser.draw(WIN)
        if laser.collide(player):
            player.health -= 2
            active_boss.health += 1
            hero_explode_sound.play()
            active_boss.lasers.remove(laser)
        elif laser.off_screen():
            active_boss.lasers.remove(laser)



# Game Music Screens
def game_start_screen():
    play_opening_music()
    BG_opening = pygame.transform.scale(pygame.image.load("gamestarter_background.jpg"), (WIDTH, HEIGHT))
    waiting = True
    while waiting:
        WIN.blit(BG_opening, (0, 0))
        title_font = pygame.font.SysFont("comicsans", 80)
        start_text = title_font.render("Click Anywhere to Start", 1, (255, 255, 255))
        WIN.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                play_start_game_music()
                waiting = False

def game_over_screen(score): 
    play_gameover_music()
    BG_gameOver = pygame.transform.scale(pygame.image.load("gameover_background.jpg"), (WIDTH, HEIGHT))
    font = pygame.font.SysFont("comicsans", 100)
    small_font = pygame.font.SysFont("comicsans", 50)
    waiting = True
    while waiting:
        WIN.blit(BG_gameOver, (0, 0))
        over_text = font.render("Game Over", 1, (255, 255, 255))
        total_end = small_font.render(f"your total score you reach is: {score}", True, (255, 255, 255))
        restart_text = font.render("Click to Restart", 1, (255, 255, 255))
        WIN.blit(total_end, (WIDTH//2 - over_text.get_width()//10, HEIGHT//10))
        WIN.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//3))
        WIN.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                play_continue_music()
                main()
                return


game_start_screen()

global boss_mode, bosses, boss_intro_done, boss_trap_mode, boss_small_enemies_mode, you_did_it
boss_mode = False
bosses = []
boss_intro_done = False
boss_trap_mode = False
boss_small_enemies_mode = False
you_did_it = False
current_boss_index = 0
enemy_sound_played = False


def main():
    global boss_mode, bosses, boss_intro_done, boss_trap_mode, boss_small_enemies_mode, you_did_it, current_boss_index
    boss_healths = [30, 40, 50]  # Health for each boss

    run = True
    FPS = 60
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("comicsans", 50)

    ship_image, laser_image = choose_player_ship()
    player = Player(875, 500)
    player.ship_image = ship_image
    player.laser_image = laser_image
    player.mask = pygame.mask.from_surface(ship_image)

    trap_list = []
    trap_event_triggered = False
    trap_warning_played = False

    
    max_enemies = 3
    enemy_speed = 1
    player_speed = 5
    laser_speed_multiplier = 1
    score = 0
    enemies = []

    def redraw_window():
        global boss_mode, bosses, boss_intro_done, boss_trap_mode, boss_small_enemies_mode, you_did_it
        global current_boss_index

        WIN.blit(BG, (0, 0))

        # Draw Player Stats (Lives, Score)
        lives_label = main_font.render(f"Lives: {player.health}", True, (255, 255, 255))
        score_label = main_font.render(f"Score: {score}", True, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(score_label, (WIDTH - score_label.get_width() - 10, 10))

        # Draw Traps
        for trap in trap_list:
            trap.draw(WIN)

        # Draw Enemies and their Lasers
        for enemy in enemies:
            enemy.draw(WIN)
            for laser in enemy.lasers:
                laser.draw(WIN)

        # Draw Player and Player Lasers
        player.draw(WIN)
        for laser in player.lasers:
            laser.draw(WIN)

        # Draw Bosses if Active
        if boss_mode and bosses:
            active_boss = bosses[current_boss_index]

            if active_boss.health > 0:
                active_boss.draw(WIN)

                # Boss random slight movement
                active_boss.x += random.choice([-1, 0, 1]) * 3
                active_boss.y += random.choice([-1, 0, 1]) * 2

                # Keep boss within screen bounds
                active_boss.x = max(0, min(active_boss.x, WIDTH - active_boss.get_width()))
                active_boss.y = max(0, min(active_boss.y, HEIGHT // 2))

                # Boss shooting
                active_boss.shoot_cooldown -= 1
                if active_boss.shoot_cooldown <= 0:
                    active_boss.shoot(player)
                    active_boss.shoot_cooldown = random.randint(30, 70)

                # Move and check boss lasers
                for laser in active_boss.lasers[:]:
                    laser.move()
                    if boss_mode and bosses:
                        active_boss = bosses[current_boss_index]
                        if current_boss_index == 0:
                            wave1_boss_logic(active_boss, player)
                        elif current_boss_index == 1:
                            wave2_boss_logic(active_boss, player)
                        elif current_boss_index == 2:
                            wave3_boss_logic(active_boss, player)


                # Display Boss Health
                boss_health_label = main_font.render(f"Boss Lives: {active_boss.health}", True, (255, 0, 0))
                WIN.blit(boss_health_label, (20, 80))

        # Draw Wave Title at Top Center
        if boss_mode and bosses:
            wave_font = pygame.font.SysFont("comicsans", 80)
            if current_boss_index == 0:
                wave_text = wave_font.render("Wave 1", True, (255, 255, 0))
            elif current_boss_index == 1:
                wave_text = wave_font.render("Wave 2", True, (255, 0, 255))
            else:
                wave_text = wave_font.render("Wave 3", True, (0, 255, 255))
            WIN.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, 30))

        # Update Display
        pygame.display.update()



    while run:
        clock.tick(FPS)
            # Trap event at score 1020
        if score >= 1020 and not trap_event_triggered:
            trap_event_triggered = True
            enemy_speed = 1  # slow back down
            max_enemies = 6
            enemies.clear()  # optional: clear current enemies
            trap_list = []
            directions = ["top", "left", "right", "bottom"]
            for _ in range(5):  # spawn 5 initial traps
                trap_list.append(Trap(random.choice(directions)))
            if not trap_warning_played:
                trap_warning_sound.play()
                trap_warning_played = True

        
            # Check if it's time for boss
        if score >= 1200 and not boss_mode:
            boss_mode = True
            enemies.clear()
            trap_list.clear()
            enemy_speed = 1  # slow down
            laser_speed_multiplier = 1  # reset to normal

            bosses.clear()  # Add this too to clear old bosses
            boss_images = [myEnemy_1, myEnemy_2, myEnemy_3]
            for img in boss_images:
                boss = Enemy(WIDTH//2 - 60, HEIGHT//6, 1)
                boss.ship_image = pygame.transform.scale(img, (120, 120))
                boss.mask = pygame.mask.from_surface(boss.ship_image)
                boss.laser_image = random.choice([blackHole01, blackHole02, blackHole03])
                boss.speed = 0  # Boss moves randomly
                boss.health = boss_healths[len(bosses)]  # 30 -> 40 -> 50
                bosses.append(boss)
            if boss_mode and bosses:
                active_boss = bosses[current_boss_index]
                if laser.collide(active_boss) and active_boss.health > 0:
                    active_boss.health -= 1

        for i in range(1, len(bosses)):
            bosses[i].health = 0  # Hide other bosses until previous dies

            # Update and draw traps
        for trap in trap_list[:]:
            trap.update()
            if trap.check_collision(player):
                player.health -= 1
                trap_list.remove(trap)
                trap_list.append(Trap(random.choice(["top", "left", "right", "bottom"])))
            elif not trap.warning_shown and trap.timer >= trap.delay + 30:
                trap_list.remove(trap)
                trap_list.append(Trap(random.choice(["top", "left", "right", "bottom"])))

        # Update Boss Fight
        if boss_mode and bosses:
            active_boss = bosses[current_boss_index]
            if current_boss_index == 0:
                wave1_boss_logic(active_boss, player)
            elif current_boss_index == 1:
                wave2_boss_logic(active_boss, player)
            elif current_boss_index == 2:
                wave3_boss_logic(active_boss, player)


                
                # Shooting blackholes
                active_boss.shoot_cooldown -= 1
                if active_boss.shoot_cooldown <= 0:
                    active_boss.shoot(player)
                    active_boss.shoot_cooldown = random.randint(30, 70)

                # Blackhole collision
                for laser in active_boss.lasers[:]:
                    laser.move()
                    if laser.collide(player):
                        player.health -= 2
                        hero_explode_sound.play()
                        active_boss.lasers.remove(laser)
                    elif laser.off_screen():
                        active_boss.lasers.remove(laser)

                # Touching player
                if player.x < active_boss.x + active_boss.get_width() and player.x + player.get_width() > active_boss.x and \
                   player.y < active_boss.y + active_boss.get_height() and player.y + player.get_height() > active_boss.y:
                    if active_boss.health > 6:
                        player.health -= 15
                    else:
                        player.health -= 30

            # Boss 2 behavior (Wave 2)
            elif current_boss_index == 1:
                # Chase player
                dx = player.x - active_boss.x
                dy = player.y - active_boss.y
                dist = math.hypot(dx, dy) or 1
                active_boss.x += 3 * dx / dist
                active_boss.y += 3 * dy / dist

                # Stay inside screen
                active_boss.x = max(0, min(active_boss.x, WIDTH - active_boss.get_width()))
                active_boss.y = max(0, min(active_boss.y, HEIGHT - active_boss.get_height()))

                # Touching player
                if player.x < active_boss.x + active_boss.get_width() and player.x + player.get_width() > active_boss.x and \
                   player.y < active_boss.y + active_boss.get_height() and player.y + player.get_height() > active_boss.y:
                    player.health -= 20
                    active_boss.health += 5  # Boss 2 heals

            # Boss 3 behavior (Wave 3)
            elif current_boss_index == 2:
                # Shoot blackholes + Chase player
                active_boss.shoot_cooldown -= 1
                if active_boss.shoot_cooldown <= 0:
                    active_boss.shoot(player)
                    active_boss.shoot_cooldown = random.randint(30, 70)

                # Chase
                dx = player.x - active_boss.x
                dy = player.y - active_boss.y
                dist = math.hypot(dx, dy) or 1
                active_boss.x += 2 * dx / dist
                active_boss.y += 2 * dy / dist

                active_boss.x = max(0, min(active_boss.x, WIDTH - active_boss.get_width()))
                active_boss.y = max(0, min(active_boss.y, HEIGHT - active_boss.get_height()))

                # Blackhole collision (heal boss)
                for laser in active_boss.lasers[:]:
                    laser.move()
                    if laser.collide(player):
                        player.health -= 2
                        active_boss.health += 1
                        hero_explode_sound.play()
                        active_boss.lasers.remove(laser)
                    elif laser.off_screen():
                        active_boss.lasers.remove(laser)

        # Update rotation angles
        for key in blackhole_rotation_angles:
            blackhole_rotation_angles[key] = (blackhole_rotation_angles[key] + 2) % 360
        # Scale difficulty
        if score // 200 + 3 > max_enemies:
            max_enemies = min(15, score // 100 + 3)
        if not boss_mode:
            if score % 50 == 0:
                enemy_speed = 1 + (score // 50) * 0.5
                player_speed = 5 + (score // 100)
            if score == 450:
                player_speed += 3
            
            laser_speed_multiplier = 1 + (score // 100) * 0.2


        if not boss_mode and len(enemies) == 0:
            wave_length = min(max_enemies, 15)
            for _ in range(wave_length):
                edge = random.choice(["top", "bottom", "left", "right"])
                if edge == "top":
                    x, y = random.randint(0, WIDTH), -60
                elif edge == "bottom":
                    x, y = random.randint(0, WIDTH), HEIGHT + 60
                elif edge == "left":
                    x, y = -60, random.randint(0, HEIGHT)
                else:  # right
                    x, y = WIDTH + 60, random.randint(0, HEIGHT)

                enemy_type = random.choice([1, 2, 3])
                enemy = Enemy(x, y, enemy_type)
                enemy.speed = enemy_speed
                enemies.append(enemy)

            enemy_sound_played = False  # Reset the flag for a new wave
            play_enemy_entry_sound()     # Play sound once

        for event in pygame.event.get():
            ENEMY_SOUND_EVENT = pygame.USEREVENT + 1
            pygame.time.set_timer(ENEMY_SOUND_EVENT, 8000)  # play every 8 seconds

            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot(pygame.mouse.get_pos())

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_speed > 0:
            player.x -= player_speed
        if keys[pygame.K_d] and player.x + player_speed + player.get_width() < WIDTH:
            player.x += player_speed
        if keys[pygame.K_w] and player.y - player_speed > 0:
            player.y -= player_speed
        if keys[pygame.K_s] and player.y + player_speed + player.get_height() < HEIGHT:
            player.y += player_speed


        to_remove = []

        for enemy in enemies[:]:
            if score >= 300:
                side_juke = random.uniform(-1, 1)
                perp_angle = math.atan2(player.y - enemy.y, player.x - enemy.x) + math.pi / 2
                side_dx = math.cos(perp_angle) * side_juke
                side_dy = math.sin(perp_angle) * side_juke
                target_x = player.x + side_dx * 50
                target_y = player.y + side_dy * 50
                enemy.move(target_x, target_y)
            else:
                enemy.move(player.x, player.y)

            for laser in enemy.lasers[:]:
                laser.x += laser.dir_x * laser.speed * laser_speed_multiplier
                laser.y += laser.dir_y * laser.speed * laser_speed_multiplier
                if laser.collide(player):
                    player.health -= 2
                    hero_explode_sound.play()
                    enemy.lasers.remove(laser)
                elif laser.off_screen():
                    enemy.lasers.remove(laser)

            enemy.shoot_cooldown -= 1
            if enemy.shoot_cooldown <= 0:
                enemy.shoot(player)
                base_cooldown = random.randint(60, 120)
                difficulty_modifier = max(10, base_cooldown - (score // 20))
                enemy.shoot_cooldown = difficulty_modifier

            # Check if enemy collided with player
            if player.x < enemy.x + enemy.get_width() and player.x + player.get_width() > enemy.x and  player.y < enemy.y + enemy.get_height() and player.y + player.get_height() > enemy.y:
                player.health -= 3
                explode_sound = random.choice(enemy_explode_sounds)
                explode_sound.play()
                to_remove.append(enemy)

        # Remove enemies AFTER the loop
                # Move lasers
        for laser in player.lasers[:]:
            laser.move()
            for enemy in enemies[:]:
                if laser.collide(enemy):
                    if enemy in enemies:
                        enemies.remove(enemy)
                    if laser in player.lasers:
                        player.lasers.remove(laser)
                    score += 10
                    player.health += 1
                    random.choice(enemy_explode_sounds).play()
                    break
            else:
                if laser.off_screen() and laser in player.lasers:
                    player.lasers.remove(laser)
            # After enemy check, also check boss hit
        if boss_mode and bosses:
            active_boss = bosses[current_boss_index]
            if laser.collide(active_boss) and active_boss.health > 0:
                active_boss.health -= 1
                if laser in player.lasers:
                    player.lasers.remove(laser)

                if active_boss.health <= 0:
                    explode_sound = random.choice(enemy_explode_sounds)
                    explode_sound.play()

                    if current_boss_index == 0:
                        player.health += 30
                        score += 300
                        current_boss_index += 1
                    elif current_boss_index == 1:
                        player.health += 40
                        score += 400
                        current_boss_index += 1
                    else:
                        you_did_it = True
                        pygame.mixer.music.stop()



        # Remove enemies AFTER the loop
        for enemy in to_remove:
            if enemy in enemies:
                enemies.remove(enemy)

        if player.health <= 0:
            run = False
            game_over_screen(score)

        redraw_window()
    if you_did_it:
        pygame.mixer.music.stop()
        final_screen_font = pygame.font.SysFont("comicsans", 120)
        click_font = pygame.font.SysFont("comicsans", 50)
        waiting = True
        while waiting:
            WIN.blit(BG, (0, 0))
            text = final_screen_font.render("YOU DID IT!", 1, (255, 255, 0))
            click_text = click_font.render("Click Anywhere to Return Home", 1, (255, 255, 255))
            WIN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//3))
            WIN.blit(click_text, (WIDTH//2 - click_text.get_width()//2, HEIGHT//2))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    main()
                    return

main()
