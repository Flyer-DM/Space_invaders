import pygame
import pygame_menu
import csv
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from random import randint, choice
from os import listdir
from time import time, strftime, gmtime

pygame.init()
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
# text rendering before positioning
health_word = font.render("Health:", False, GREEN)
score_word = font.render("Score:", False, BLUE)
timer_word = font.render("Time:", False, BLUE)
get_ready_text = font.render("Get ready!", False, WHITE)
lose_text = font.render("YOU LOST!", False, WHITE)
win_text = font.render("YOU WON!", False, WHITE)


class Spaceship(pygame.sprite.Sprite):
    """Player class"""

    def __init__(self, x: int, y: int):
        pygame.sprite.Sprite.__init__(self)
        self.mask = None
        self.last_shot = pygame.time.get_ticks()
        self.image = pygame.image.load("Starfighter.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = 3
        self.cooldown = 500
        self.ful_health = 100
        self.remaining_health = self.ful_health
        self.shots_made = 0
        self.shots_reached = 0

    def reset(self, x, y):
        self.__init__(x, y)

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
        if key[pygame.K_SPACE] and time_now - self.last_shot > self.cooldown:
            bullet = Bullet(self.rect.centerx, self.rect.top)
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
            explosion_group.add(explosion)
            self.kill()
            alive = -1
        return alive


class Bullet(pygame.sprite.Sprite):
    """Player`s bullet class"""

    def __init__(self, x: int, y: int):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < WINDOW_HEIGHT - BG_IMAGE.get_height():
            self.kill()
        enemy_shot = pygame.sprite.spritecollide(self, alien_group, False)
        player.shots_reached += 1
        if enemy_shot:
            self.kill()
            enemy_shot[0].health -= 20
            health_remaining = enemy_shot[0].health
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
            if health_remaining == 0:
                enemy_shot[0].kill()


class Alien(pygame.sprite.Sprite):
    """Alien (player`s enemy) class"""

    @classmethod
    def health_creator(cls, alien_type: int):
        return 60 if alien_type == 1 else 40 if alien_type == 3 else 20

    def __init__(self, x: int, y: int):
        pygame.sprite.Sprite.__init__(self)
        self.type = randint(1, 4)
        self.health = Alien.health_creator(self.type)
        alien_name = f"alien{self.type}.png"
        self.image = pygame.image.load(alien_name)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= self.move_direction


class AlienBullet(pygame.sprite.Sprite):
    """Aliens`s bullet class"""

    @classmethod
    def get_speed(cls, alien_type: int):
        return 6 if alien_type == 2 else 2 if alien_type == 1 else 3

    def __init__(self, x: int, y: int, alien_type: int):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = AlienBullet.get_speed(alien_type)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            if self.speed == 6:
                player.remaining_health -= 10
            elif self.speed == 2:
                player.remaining_health -= 50
            else:
                player.remaining_health -= 20
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)


class Explosion(pygame.sprite.Sprite):
    """Explosion for aliens and ship class"""

    @classmethod
    def get_image(cls, explosion_type: int):
        if explosion_type == 1:
            return pygame.image.load("explosion.png")
        elif explosion_type == 2:
            return pygame.image.load("ship_explosion.png")
        return pygame.transform.scale(pygame.image.load("ship_explosion.png"), EXPLOSION_SHAPE)

    def __init__(self, x: int, y: int, exp_type: int):
        pygame.sprite.Sprite.__init__(self)
        self.image = Explosion.get_image(exp_type)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        speed = 8
        if self.counter >= speed:
            self.kill()
        else:
            self.counter += 1


def statistics_page() -> None:
    """Opens tkinter window with game statistics for player"""

    def check_keys(event: tk.Event):
        """Checking if users tries to input or paste text into text fields"""
        if event.char.isalpha() or (event.state & 4 and event.keysym == "v"):
            return "break"

    # creating and setting main window of tkinter
    root = tk.Tk()
    root.geometry(f'{WINDOW_WIDTH + 300}x{WINDOW_HEIGHT}')
    root.resizable(False, False)
    root.title("Game Statistics")
    root.iconbitmap(icon)
    # making scrollbar for text label
    text = tk.Text(root, height=50, width=WINDOW_WIDTH)
    text.grid(row=0, column=0, sticky=tk.EW)
    scrollbar = ttk.Scrollbar(root, orient='vertical', command=text.yview)
    scrollbar.grid(row=0, column=1, sticky=tk.NS)
    text.yscrollcommand = scrollbar.set
    # binding not allowing input and pasting into text fields
    text.bind("<Key>", check_keys)
    # adding text
    with open("game_statistics.csv", "r", encoding="windows-1251") as file:
        reader = csv.reader(file, delimiter=';')
        for index, row in enumerate(reader, 1):
            row_format = "{:^16} | {:^6} | {:^16} | {:^5} | {:^12} | {:^6} | {:^8} | {:^26}\n".format(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            text.insert(float(index), row_format)
    root.mainloop()


def save_statistics(player_name: str, result: str, remaining_health: int, score: int,
                    time_played: str, shots_made: int, accuracy: float):
    """Saving game statistics after every game of the player into csv file"""
    filename = "game_statistics.csv"
    fields = ["name", "result", "remaining_health", "score", "time_played", "shots", "accuracy", "date"]
    row = {"name": player_name, "result": result, "remaining_health": remaining_health, "score": score,
           "time_played": time_played, "shots": shots_made, "accuracy": accuracy,
           "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
    if filename in listdir():  # file exists and user adds new game statistics row
        with open("game_statistics.csv", 'a', newline='', encoding='windows-1251') as file:
            writer = csv.DictWriter(file, delimiter=';', fieldnames=fields)
            writer.writerow(row)
            file.close()
    else:  # file does not already exist for statistics (first initialization)
        with open("game_statistics.csv", 'w', newline='', encoding='windows-1251') as file:
            writer = csv.DictWriter(file, delimiter=';', fieldnames=fields)
            writer.writeheader()
            writer.writerow(row)
            file.close()


def quit_handler() -> None:
    """End of the program handler for main loop"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()


def end_handler() -> bool:
    """Handling end of the game by losing or winning the game"""
    global gameover, end_countdown, last_count
    count_timer = pygame.time.get_ticks()
    if gameover == -1:
        SCREEN.blit(lose_text, GET_READY_POS)
    else:
        SCREEN.blit(win_text, GET_READY_POS)
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
        alien_bullet_group.add(bullet)
        last_alien_shot = time_now


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


# player class initialization
player = Spaceship(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)


def main(player_name: pygame_menu.widgets.widget.textinput.TextInput) -> None:
    """main class handling all events"""
    global START_TIME, countdown, gameover, end_countdown
    # resetting gameover variable just in case
    gameover = 0
    # restarting timer and countdown
    countdown = 4
    end_countdown = 4
    START_TIME = time()
    # clearing  groups if not empty after last game
    alien_group.empty()
    explosion_group.empty()
    bullet_group.empty()
    # alien positioning on screen
    create_aliens()
    # resetting player to default options
    player.reset(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)
    spaceship_group.add(player)
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
            # gameover not equals to 0
            if not gameover:
                # create random alien bullets
                alien_shooting(alien_group)
                # handing with player movement and shooting on WASD and SPACE buttons
                gameover = player.update()
                # updating sprites except for explosion
                bullet_group.update()
                alien_group.update()
                alien_bullet_group.update()
                # timer handling
                timer_handling()
                # score updating
                score_handling()
            else:
                if end_handler():
                    save_statistics(player_name.get_value(),
                                    "WIN" if gameover == 1 else "LOSE",
                                    player.remaining_health if player.remaining_health > 0 else 0,
                                    score_handling(),
                                    timer_handling(),
                                    player.shots_made,
                                    player.get_accuracy())
                    break
        if countdown > 0:
            get_ready()
        # updating explosion
        explosion_group.update()
        # drawing objects on screen
        spaceship_group.draw(SCREEN)
        bullet_group.draw(SCREEN)
        alien_group.draw(SCREEN)
        alien_bullet_group.draw(SCREEN)
        explosion_group.draw(SCREEN)
        # handling the end of the game
        quit_handler()
        # updating screen after positioning all the objects every frap
        pygame.display.update()


def menu() -> None:
    """start menu handling function"""
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
