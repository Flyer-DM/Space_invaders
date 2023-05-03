import pygame
import pygame_menu
from random import randint, choice
from time import time, strftime, gmtime
from statistics import statistics_page, save_statistics
from abstract import AbstractObject

pygame.init()
pygame.mixer.init()
# gameover variable meaning the reason of gameover or resuming the game (0 - play, 1 - win, -1 - lose)
gameover = 0
# window options
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800
# speed of the game
FPS = 120
CLOCK = pygame.time.Clock()
countdown = 4
end_countdown = 4
last_count = pygame.time.get_ticks()
# starting timer of the game
START_TIME = time()
# alien cooldown
ALIEN_COOLDOWN = 1000
last_alien_shot = pygame.time.get_ticks()
# asteroids cooldown
last_asteroid_spawn = pygame.time.get_ticks()
# explosion cooldown in milliseconds
EXPLOSION_COOLDOWN = 500
# alien group length that mean player`s score
last_alien_group_length = 0
# positions for objects
H_S_T_POS_X = 90
BG_POS = (0, 0)
HEALTH_WORD_POS = (10, 10)
SCORE_WORD_POS = (10, 40)
SCORE_NUMBER_POS = (H_S_T_POS_X, 40)
TIMER_WORD_POS = (10, 70)
TIMER_POS = (H_S_T_POS_X, 70)
EXPLOSION_SHAPE = (150, 150)
GET_READY_POS = (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 100)
COUNTDOWN_WORD_POS = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 150)
# colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
# font option
pygame.font.init()
font = pygame.font.SysFont("Pixeleum 48", 32)
# main window options
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space invaders", )
# images
icon = "icon.png"
ICON = pygame.image.load(icon)
BG_IMAGE = pygame.image.load("bg.png")
pygame.display.set_icon(ICON)
# groups definition
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
spaceship_fire_group = pygame.sprite.Group()
gift_group = pygame.sprite.Group()
asteroid_group = pygame.sprite.Group()
# adding all groups in list
all_groups = [asteroid_group, spaceship_group, bullet_group, alien_group, alien_bullet_group,
              explosion_group, spaceship_fire_group, gift_group]
# text rendering before positioning
health_word = font.render("Health:", False, GREEN)
score_word = font.render("Score:", False, BLUE)
timer_word = font.render("Time:", False, BLUE)
get_ready_text = font.render("Get ready!", False, WHITE)
lose_text = font.render("YOU LOST!", False, WHITE)
win_text = font.render("YOU WON!", False, WHITE)
# sound effects
alien_hit_fx = pygame.mixer.Sound('alien_hit.mp3')
alien_hit_fx.set_volume(0.25)
spaceship_hit_fx = pygame.mixer.Sound('spaceship_hit.mp3')
spaceship_hit_fx.set_volume(0.25)
alien_laser_fx = pygame.mixer.Sound('alien_laser.mp3')
alien_laser_fx.set_volume(0.25)
spaceship_laser_fx = pygame.mixer.Sound('spaceship_laser.mp3')
spaceship_laser_fx.set_volume(0.25)
spaceship_explosion_fx = pygame.mixer.Sound('spaceship_explosion.mp3')
win_fx = pygame.mixer.Sound('win.mp3')
win_fx.set_volume(0.5)
# bg music playing continuesly
pygame.mixer.music.load('bg_music.mp3')
pygame.mixer.music.play(-1)


class Spaceship(AbstractObject):
    """Player class"""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, "Starfighter.png")
        self.mask = None
        self.last_shot = pygame.time.get_ticks()
        self.speed = 3
        self.cooldown = 500
        self.increase_cooldown = 3000
        self.increase_cooldown_start = None
        self.ful_health = 100
        self.remaining_health = self.ful_health
        self.shots_made = 0
        self.shots_reached = 0

    def get_accuracy(self) -> float:
        try:
            return round(self.shots_reached / self.shots_made, 2)
        except ZeroDivisionError:
            return 0.00

    def update(self) -> int:
        key = pygame.key.get_pressed()
        # alive variable equals to gameover variable (0 means player is still alive, -1 - player is dead)
        alive = 0

        # player movement
        if key[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if key[pygame.K_d] and self.rect.left < WINDOW_WIDTH - self.image.get_width():
            self.rect.x += self.speed
        if key[pygame.K_w] and self.rect.top > WINDOW_HEIGHT // 2 + 100:
            self.rect.y -= self.speed
        if key[pygame.K_s] and self.rect.bottom < WINDOW_HEIGHT:
            self.rect.y += self.speed

        # player shooting
        time_now = pygame.time.get_ticks()
        # increasing firing speed for 3 secs after getting a gift
        if self.increase_cooldown_start is not None:
            if time_now - self.increase_cooldown_start > self.increase_cooldown:
                self.cooldown = 500
                self.increase_cooldown_start = None

        if key[pygame.K_SPACE] and time_now - self.last_shot > self.cooldown:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            spaceship_laser_fx.play()
            bullet_group.add(bullet)
            self.shots_made += 1
            self.last_shot = time_now

        self.mask = pygame.mask.from_surface(self.image)

        # health bar drawing
        pygame.draw.rect(SCREEN, RED, (H_S_T_POS_X, 15, self.ful_health, 15))
        if self.remaining_health > 0:
            pygame.draw.rect(SCREEN, GREEN, (H_S_T_POS_X, 15, self.remaining_health, 15))
        else:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            spaceship_explosion_fx.play()
            explosion_group.add(explosion)
            self.kill()
            alive = -1
        return alive


class SpaceshipFire(pygame.sprite.Sprite):
    """Player`s fire when moving"""

    @classmethod
    def load_images(cls) -> list:
        images = []
        for i in range(1, 5):
            image = pygame.image.load(f"fire_{i}.png")
            images.append(image)
        return images

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = SpaceshipFire.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self) -> None:
        self.image = self.images[self.index]
        self.rect.x = player.rect.x + 13
        self.rect.y = player.rect.bottom
        self.index += 1
        if self.index == 4:
            self.index = 0
        if player.remaining_health <= 0:
            self.kill()


class Bullet(AbstractObject):
    """Player`s bullet class"""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, "bullet.png")

    def update(self) -> None:
        self.rect.y -= 5
        if self.rect.bottom < WINDOW_HEIGHT - BG_IMAGE.get_height():
            self.kill()
        enemy_shot = pygame.sprite.spritecollide(self, alien_group, False)
        player.shots_reached += 1
        if enemy_shot:
            self.kill()
            alien_hit_fx.play()
            enemy_shot[0].health -= 20
            health_remaining = enemy_shot[0].health
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
            if health_remaining == 0:
                explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
                explosion_group.add(explosion)
                if randint(1, 10) == 1:
                    gift = Gift(enemy_shot[0].rect.centerx, enemy_shot[0].rect.bottom)
                    gift_group.add(gift)
                enemy_shot[0].kill()


class Gift(AbstractObject):
    """Gift class randomly dropping from Aliens"""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, "gift.png")
        self.type = randint(1, 2)

    def update(self) -> None:
        self.rect.y += 3
        if self.rect.bottom < WINDOW_HEIGHT - BG_IMAGE.get_height():
            self.kill()
        player_reached = pygame.sprite.spritecollide(self, spaceship_group, False)

        if player_reached:
            self.kill()
            if self.type == 1 and player.remaining_health <= 90:
                player.remaining_health += 10
            else:
                player.cooldown = 250
                player.increase_cooldown_start = pygame.time.get_ticks()


class Alien(AbstractObject):
    """Alien (player`s enemy) class"""

    @classmethod
    def health_creator(cls, alien_type: int) -> int:
        return 60 if alien_type == 1 else 40 if alien_type == 3 else 20

    def __init__(self, x: int, y: int):
        self.type = randint(1, 4)
        alien_name = f"alien{self.type}.png"
        super().__init__(x, y, alien_name)
        self.health = Alien.health_creator(self.type)
        self.move_direction = 1
        self.move_counter = 0

    def update(self) -> None:
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= self.move_direction


class AlienBullet(AbstractObject):
    """Aliens`s bullet class"""

    @classmethod
    def get_speed(cls, alien_type: int) -> int:
        return 6 if alien_type == 2 else 2 if alien_type == 1 else 3

    def __init__(self, x: int, y: int, alien_type: int):
        super().__init__(x, y, "alien_bullet.png")
        self.speed = AlienBullet.get_speed(alien_type)

    def update(self) -> None:
        self.rect.y += self.speed
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            spaceship_hit_fx.play()
            player.remaining_health -= 10 if self.speed == 6 else 50 if self.speed == 2 else 20
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)


class Explosion(AbstractObject):
    """Explosion for aliens and ship class"""

    @classmethod
    def get_image(cls, explosion_type: int) -> pygame.SurfaceType:
        if explosion_type == 1:
            return pygame.image.load("explosion.png")
        elif explosion_type == 2:
            return pygame.image.load("ship_explosion.png")
        return pygame.transform.scale(pygame.image.load("ship_explosion.png"), EXPLOSION_SHAPE)

    def __init__(self, x: int, y: int, exp_type: int):
        super().__init__(x, y, Explosion.get_image(exp_type))
        self.counter = 0

    def update(self) -> None:
        speed = 8
        if self.counter >= speed:
            self.kill()
        else:
            self.counter += 1


class Asteroid(AbstractObject):

    @classmethod
    def get_image(cls, explosion_type: int) -> pygame.SurfaceType:
        if explosion_type == 1:
            return pygame.transform.scale(pygame.image.load("asteroid.png"), (50, 30))
        elif explosion_type == 2:
            return pygame.transform.scale(pygame.image.load("asteroid.png"), (40, 20))
        return pygame.transform.scale(pygame.image.load("asteroid.png"), (20, 10))

    @classmethod
    def get_speed(cls, explosion_type: int) -> int:
        return 5 if explosion_type == 1 else 3 if explosion_type == 2 else 1

    def __init__(self, x: int, y: int, type: int):
        super().__init__(x, y, Asteroid.get_image(type))
        self.speed = Asteroid.get_speed(type)

    def update(self) -> None:
        self.rect.y += self.speed
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


def quit_handler() -> None:
    """End of the program handler for main loop"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()


def end_handler() -> bool:
    """Handling end of the game by losing or winning the game"""
    global gameover, end_countdown, last_count
    count_timer = pygame.time.get_ticks()
    SCREEN.blit(lose_text, GET_READY_POS) if gameover == -1 else SCREEN.blit(win_text, GET_READY_POS)
    if count_timer - last_count > 1000:
        end_countdown -= 1
        last_count = count_timer
    return not end_countdown


def get_ready() -> None:
    global last_count, countdown
    """making sign on screen before game starts"""
    SCREEN.blit(get_ready_text, GET_READY_POS)
    SCREEN.blit(font.render(str(countdown), False, WHITE), COUNTDOWN_WORD_POS)
    count_timer = pygame.time.get_ticks()
    if count_timer - last_count > 1000:
        countdown -= 1
        last_count = count_timer


def create_aliens() -> None:
    """Creating and positioning number of aliens on screen"""
    global last_alien_group_length
    for i in range(5):
        for j in range(10):
            alien = Alien(70 + j * 50, 200 + i * 70)
            alien_group.add(alien)
    last_alien_group_length = len(alien_group)


def alien_shooting(group: pygame.sprite.Group) -> None:
    """Handling with aliens shooting at player"""
    global last_alien_shot
    time_now = pygame.time.get_ticks()
    if time_now - last_alien_shot > ALIEN_COOLDOWN:
        attacking = choice(group.sprites())
        bullet = AlienBullet(attacking.rect.centerx, attacking.rect.bottom, attacking.type)
        alien_laser_fx.play()
        alien_bullet_group.add(bullet)
        last_alien_shot = time_now


def asteroids() -> None:
    """Randomly spawning asteroid on background through game"""
    global last_asteroid_spawn
    time_now = pygame.time.get_ticks()
    if time_now - last_asteroid_spawn > EXPLOSION_COOLDOWN:
        position_x = randint(20, WINDOW_WIDTH - 20)
        asteroid = Asteroid(position_x, 0, randint(1, 3))
        asteroid_group.add(asteroid)
        last_asteroid_spawn = time_now


def score_handling() -> int:
    """Handling with changing player`s score after destroying an enemy"""
    global last_alien_group_length
    if len(alien_group) < last_alien_group_length:
        last_alien_group_length = len(alien_group)
    score = 100 - last_alien_group_length * 2
    score_number = font.render(f"{score}/100", True, BLUE)
    SCREEN.blit(score_number, SCORE_NUMBER_POS)
    return score


def timer_handling() -> str:
    """Working timer"""
    global START_TIME
    time_now = time() - START_TIME
    time_played = strftime("%M:%S", gmtime(time_now))
    timer = font.render(time_played, True, BLUE)
    SCREEN.blit(timer, TIMER_POS)
    return time_played


def main(player_name: pygame_menu.widgets.widget.textinput.TextInput) -> None:
    """main class handling all events"""
    global START_TIME, countdown, gameover, end_countdown
    pygame.mixer.music.set_volume(0.15)
    # resetting gameover variable just in case
    gameover = 0
    # restarting timer and countdown
    countdown = 4
    end_countdown = 4
    START_TIME = time()
    # clearing  groups if not empty after last game (deleting all objects from screen)
    for group in all_groups:
        group.empty()
    # alien positioning on screen
    create_aliens()
    # player class and spaceship_fire class initialization
    global player, spaceship_fire
    player = Spaceship(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)
    spaceship_fire = SpaceshipFire(player.rect.x + 13, player.rect.bottom)
    spaceship_group.add(player)
    spaceship_fire_group.add(spaceship_fire)
    while True:
        # setting FPS for game
        CLOCK.tick(FPS)
        # placing all static objects
        SCREEN.blit(BG_IMAGE, BG_POS)
        SCREEN.blit(health_word, HEALTH_WORD_POS)
        SCREEN.blit(score_word, SCORE_WORD_POS)
        SCREEN.blit(timer_word, TIMER_WORD_POS)
        # countdown
        if countdown == 0:
            if len(alien_group) == 0:
                gameover = 1
                win_fx.play()
            # gameover not equals to 0
            if not gameover:
                # create random alien bullets
                alien_shooting(alien_group)
                # spawning asteroids in the background
                asteroids()
                # handing with player movement and shooting on WASD and SPACE buttons
                gameover = player.update()
                # updating sprites except for explosion
                asteroid_group.update()
                spaceship_fire_group.update()
                bullet_group.update()
                alien_group.update()
                alien_bullet_group.update()
                gift_group.update()
                # timer handling
                timer_handling()
                # score updating
                score_handling()
            else:
                player.kill()
                spaceship_fire.kill()
                if end_handler():
                    save_statistics(player_name.get_value(),
                                    "WIN" if gameover == 1 else "LOSE",
                                    player.remaining_health if player.remaining_health > 0 else 0,
                                    score_handling(),
                                    timer_handling(),
                                    player.shots_made,
                                    player.get_accuracy())
                    pygame.mixer.music.set_volume(0.05)
                    break
        if countdown > 0:
            get_ready()
        # updating explosion
        explosion_group.update()
        # drawing objects on screen
        for group in all_groups:
            group.draw(SCREEN)
        # handling the end of the game
        quit_handler()
        # updating screen after positioning all the objects every frap
        pygame.display.update()


def menu() -> None:
    """start menu handling function"""
    pygame.mixer.music.set_volume(0.05)
    # initializing my theme for future menu (changing default options for default theme)
    my_theme = pygame_menu.themes.THEME_DARK.copy()
    my_theme.widget_font = pygame_menu.font.FONT_MUNRO
    my_theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
    # initializing start menu with buttons
    my_menu = pygame_menu.Menu('', WINDOW_WIDTH, WINDOW_HEIGHT, theme=my_theme)
    name_box = my_menu.add.text_input('Name:', default="noname", maxchar=16)
    my_menu.add.button('Play', main, name_box)
    my_menu.add.button('Statistics', statistics_page)
    my_menu.add.button('Quit', pygame_menu.events.EXIT)
    my_menu.mainloop(SCREEN)


if __name__ == "__main__":
    menu()
