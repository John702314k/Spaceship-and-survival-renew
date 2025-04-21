import pygame
import random
import math

pygame.init()
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1780, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
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
enemy_sounds = [
    pygame.mixer.Sound("alien_scary_atmosphere.mp3"),
    pygame.mixer.Sound("alien-scary.mp3")
]

green_laser_sound = pygame.mixer.Sound("green_laser.mp3")
darkblue_laser_sound = pygame.mixer.Sound("darkblue_laser.mp3")
red_laser_sound = pygame.mixer.Sound("red_laser.mp3")

hero_explode_sound = pygame.mixer.Sound("blue_laser.mp3")

enemy_explode_sounds = [
    pygame.mixer.Sound("explode_01.mp3"),
    pygame.mixer.Sound("explode_02.mp3"),
    pygame.mixer.Sound("explode_03.mp3")
]

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

# Rotation angles for black holes
blackhole_rotation_angles = {
    "enemy_laser01.png": 0,
    "enemy_laser02.png": 0,
    "enemy_laser03.png": 0
}

BG = pygame.transform.scale(pygame.image.load("gameplay_background.jpg"), (WIDTH, HEIGHT))

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
            if isinstance(self.image, dict):  # enemy laser
                image = self.image["image"]
                image_name = self.image["name"]
                if image_name in blackhole_rotation_angles:
                    angle = blackhole_rotation_angles[image_name]
                else:
                    angle = math.degrees(math.atan2(-self.dir_y, self.dir_x)) - 90
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
    if not pygame.mixer.get_busy():
        sound = random.choice(enemy_sounds)
        sound.play()

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

def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("comicsans", 50)

    ship_image, laser_image = choose_player_ship()
    player = Player(875, 500)
    player.ship_image = ship_image
    player.laser_image = laser_image
    player.mask = pygame.mask.from_surface(ship_image)
    
    max_enemies = 3
    enemy_speed = 1
    player_speed = 5
    score = 0
    enemies = []


    def redraw_window():
        WIN.blit(BG, (0, 0))
        lives_label = main_font.render(f"Lives: {player.health}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score: {score}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(score_label, (WIDTH - score_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)
            for laser in enemy.lasers:
                laser.draw(WIN)

        player.draw(WIN)
        for laser in player.lasers:
            laser.draw(WIN)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        # Update rotation angles
        for key in blackhole_rotation_angles:
            blackhole_rotation_angles[key] = (blackhole_rotation_angles[key] + 2) % 360
        # Scale difficulty
        if score // 200 + 3 > max_enemies:
            max_enemies = min(15, score // 100 + 3)

        if score % 50 == 0:
            enemy_speed = 1 + (score // 50) * 0.5
            player_speed = 5 + (score // 100)
        if score == 450:
            player_speed + 3


        if len(enemies) == 0:
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
                play_enemy_entry_sound()

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

            enemy.shoot_cooldown -= 1
            if enemy.shoot_cooldown <= 0:
                enemy.shoot(player)
                enemy.shoot_cooldown = random.randint(60, 120)
            enemy.move_laser(player)

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

        # Remove enemies AFTER the loop
        for enemy in to_remove:
            if enemy in enemies:
                enemies.remove(enemy)

        if player.health <= 0:
            run = False
            game_over_screen(score)

        redraw_window()
main()
