import pygame


class AbstractObject(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int, image: (str, pygame.SurfaceType)):
        super().__init__()
        self.image = pygame.image.load(image) if isinstance(image, str) else image
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
