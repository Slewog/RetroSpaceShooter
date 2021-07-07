#!/usr/bin/python3
import os  # Import of python modules.
import sys
import random

try:
    import pygame
except ImportError:
    from subprocess import call
    call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

# Center window on screen.
os.environ['SDL_VIDEO_CENTERED'] = '1'
# File of best score.
SCORE_FILE = os.path.join("data", "best_score.txt")

pygame.init()
pygame.font.init()
pygame.mixer.init()

# Window setting.
WIDTH, HEIGHT = 750, 750  # Window size.
GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))  # Generate the game window.
pygame.display.set_caption("Retro Space Shooter")  # Window title.
if sys.platform == 'win32':  # Logo application if is microsoft operating system.
    pygame.display.set_icon(pygame.image.load(os.path.join("assets/img", "icon.jpg")))

# Background.
GAME_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets/img", "background-black.png")), (WIDTH, HEIGHT))

# Logo.
LOGO = pygame.image.load(os.path.join("assets/img", "logo.png"))

# Font.
FONT = os.path.join("assets/font", "Pixeled.ttf")
SCORE_FONT = pygame.font.Font(FONT, 15)
GAME_FONT = pygame.font.Font(FONT, 18)
LOST_FONT = pygame.font.Font(FONT, 45)

# Sound.
MUSIC = pygame.mixer.Sound(os.path.join("assets/sound", "space_invaders_1.wav"))
MUSIC.set_volume(0.3)

SHOOTING = pygame.mixer.Sound(os.path.join("assets/sound", "shoot.wav"))
SHOOTING.set_volume(0.01)

EXPLOSION = pygame.mixer.Sound(os.path.join("assets/sound", "explosion.wav"))
EXPLOSION.set_volume(0.1)

INVADER_KILL = pygame.mixer.Sound(os.path.join("assets/sound", "invader_killed.wav"))
INVADER_KILL.set_volume(0.2)

INVADER_DESPAWN = pygame.mixer.Sound(os.path.join("assets/sound", "fast_invader_1.wav"))
INVADER_DESPAWN.set_volume(0.6)

LASER_IMPACT = pygame.mixer.Sound(os.path.join("assets/sound", "ufo_highpitch.wav"))
LASER_IMPACT.set_volume(0.1)

GAME_OVER = pygame.mixer.Sound(os.path.join("assets/sound", "game_over.wav"))
GAME_OVER.set_volume(0.3)

LEVEL_UP = pygame.mixer.Sound(os.path.join("assets/sound", "level_up.wav"))
LEVEL_UP.set_volume(0.5)

NEW_RECORDS = pygame.mixer.Sound(os.path.join("assets/sound", "new_records.wav"))
NEW_RECORDS.set_volume(0.4)

# Images spaceship and laser for the IA.
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets/img", "pixel_ship_red_small.png"))
RED_LASER = pygame.image.load(os.path.join("assets/img", "pixel_laser_red.png"))

GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets/img", "pixel_ship_green_small.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets/img", "pixel_laser_green.png"))

BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets/img", "pixel_ship_blue_small.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets/img", "pixel_laser_blue.png"))

# Images spaceship and laser for the player.
PLAYER_SHIP = pygame.image.load(os.path.join("assets/img", "pixel_ship_yellow.png"))
PLAYER_LASER = pygame.image.load(os.path.join("assets/img", "pixel_laser_yellow.png"))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, velocity):
        self.y += velocity

    def off_screen(self, height):
        return not (height >= self.y >= 0)  # return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOL_DOWNS = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, velocity, obj):
        self.cool_down()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                LASER_IMPACT.play()
                obj.health -= 10
                self.lasers.remove(laser)

    def cool_down(self):
        if self.cool_down_counter >= self.COOL_DOWNS:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.max_health = health
        self.ship_img = PLAYER_SHIP
        self.laser_img = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)

    def movement(self, pressed_key, velocity):
        if pressed_key[pygame.K_q] and self.x - velocity > 0:  # Left.
            self.x -= velocity
        if pressed_key[pygame.K_d] and self.x + velocity + self.get_width() < WIDTH:  # Right.
            self.x += velocity
        if pressed_key[pygame.K_z] and self.y - velocity > 0:  # Up.
            self.y -= velocity
        if pressed_key[pygame.K_s] and self.y + velocity + self.get_height() + 30 < HEIGHT:  # Down.
            self.y += velocity
        if pressed_key[pygame.K_SPACE]:
            SHOOTING.play()
            self.shoot()

    def move_lasers(self, vel, objs):
        self.cool_down()
        for laser in self.lasers:
            laser.move(- vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        INVADER_KILL.play()
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        self.score += 100

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, round(self.ship_img.get_width() * (self.health / self.max_health)), 10))


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def movement(self, velocity):
        self.y += velocity

    def shoot(self):
        if self.cool_down_counter == 0:
            if self.ship_img == BLUE_SPACE_SHIP:
                laser = Laser(round(self.x - 25), self.y, self.laser_img)
            else:
                laser = Laser(round(self.x - 15), self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def read_score_save(file):
    if not os.path.exists("./data"):
            os.mkdir("./data")
    if os.path.exists('data/best_score.txt'):
        with open(file, encoding='utf-8') as score_file:
            score = int(score_file.readline())
        return score
    else:
        return 0


def save_best_score(file, new_best_score):
    f = open(file, "w")
    f.write(str(new_best_score))
    f.close()


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def quit_game():
    pygame.quit()  # Close the game.
    # Add this if you have the error : pygame.key.get_pressed() pygame.error: video system not initialized.
    sys.exit()


def main():
    FPS = 60
    player_is_playing = True
    enemies = []
    enemies_velocity = 1
    wave_length = 5
    player_velocity = 5
    player_records = False
    laser_velocity = 4
    lost = False
    lost_count = 0
    player = Player(325, 625)
    clock = pygame.time.Clock()

    def draw_score(window, current_player):
        score_label = SCORE_FONT.render(f"Score: {current_player.score}", True, (255, 255, 255))
        window.blit(score_label, (round(WIDTH / 2 - score_label.get_width() / 2), -10))

        best_score_label = SCORE_FONT.render(f"Best score: {read_score_save(SCORE_FILE)}", True, (255, 255, 255))
        window.blit(best_score_label, (round(WIDTH / 2 - best_score_label.get_width() / 2), 20))

        lives_label = GAME_FONT.render(f"Lives: {current_player.lives}", True, (255, 255, 255))
        window.blit(lives_label, (10, -10))

        level_label = GAME_FONT.render(f"Level: {current_player.level}", True, (255, 255, 255))
        window.blit(level_label, (WIDTH - level_label.get_width() - 10, -10))

    def window_refresh(window):
        window.blit(GAME_BACKGROUND, (0, 0))  # Background draw.
        draw_score(window, player)

        for enemy in enemies:
            enemy.draw(window)
        player.draw(window)

        if lost and player_records:
            lost_label = LOST_FONT.render("Game Over !!!", True, (255, 255, 255))
            window.blit(lost_label, (round(WIDTH / 2 - lost_label.get_width() / 2), round(HEIGHT / 3 - lost_label.get_height() / 2)))

            score_label = LOST_FONT.render(f"Score: {player.score}", True, (255, 255, 255))
            window.blit(score_label, (round((WIDTH - window.get_width() / 2) - (score_label.get_width() / 2)), round(HEIGHT / 2 - score_label.get_height() / 2)))

            records_label = LOST_FONT.render("NEW RECORDS !!!", True, (255, 247, 0))
            window.blit(records_label, (round((WIDTH - window.get_width() / 1.65) - (score_label.get_width() / 2)), round(HEIGHT / 1.5 - score_label.get_height() / 2)))
        elif lost:
            lost_label = LOST_FONT.render("Game Over !!!", True, (255, 255, 255))
            window.blit(lost_label, (round(WIDTH / 2 - lost_label.get_width() / 2), round(HEIGHT / 2.5 - lost_label.get_height() / 2)))

            score_label = LOST_FONT.render(f"Score: {player.score}", True, (255, 255, 255))
            window.blit(score_label, (round((WIDTH - window.get_width() / 2) - (score_label.get_width() / 2)), round(HEIGHT / 1.7 - score_label.get_height() / 2)))
        pygame.display.update()

    while player_is_playing:
        clock.tick(FPS)
        window_refresh(GAME_WINDOW)

        if player.lives <= 0 or player.health <= 0:
            if lost_count == 0:
                if player.score > int(read_score_save(SCORE_FILE)):
                    player_records = True
                    save_best_score(SCORE_FILE, player.score)
                    MUSIC.stop()
                    NEW_RECORDS.play()
                else:
                    MUSIC.stop()
                    GAME_OVER.play()
                lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                player_is_playing = False
                MUSIC.play()
            else:
                continue

        if len(enemies) == 0:
            LEVEL_UP.play()
            player.level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        player.movement(pygame.key.get_pressed(), player_velocity)

        for enemy in enemies[:]:
            enemy.movement(enemies_velocity)
            enemy.move_lasers(laser_velocity, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                EXPLOSION.play()
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                INVADER_DESPAWN.play()
                player.lives -= 1
                enemies.remove(enemy)

        player.move_lasers(laser_velocity, enemies)


def main_menu():
    game_is_running = True
    MUSIC.play()

    def draw_launch_menu(window):
        window.blit(GAME_BACKGROUND, (0, 0))
        window.blit(LOGO, (round(WIDTH / 2 - LOGO.get_width() / 2), round(HEIGHT / 2 - LOGO.get_height() / 2)))

        title = pygame.font.Font(FONT, 38).render("Retro Space Shooter", True, (255, 255, 255))
        window.blit(title, (round(WIDTH / 2 - title.get_width() / 2), round(HEIGHT / 2.1 - title.get_height() / 2)))

        label = pygame.font.Font(FONT, 23).render("Press the mouse to begin...", True, (255, 255, 255))
        window.blit(label, (round(WIDTH / 2 - label.get_width() / 2), round(HEIGHT / 1.7 - label.get_height() / 2)))

        copyright_label = pygame.font.Font(FONT, 15).render("Copyright - SLEWOG", True, (255, 255, 255))
        window.blit(copyright_label, (round(WIDTH / 2 - copyright_label.get_width() / 2), round(HEIGHT / 1.05 - copyright_label.get_height() / 2)))

    while game_is_running:
        draw_launch_menu(GAME_WINDOW)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_is_running = False
                MUSIC.stop()
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    quit_game()


if __name__ == '__main__':
    main_menu()
