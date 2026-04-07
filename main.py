import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game PBO")
clock = pygame.time.Clock()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.speed = 2
        self.color = (0, 0, 255)

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed
        if self.x<0:
            self.x = 0
        if self.y<0:
            self.y = 0
        if self.x + self.width > WIDTH:
            self.x = WIDTH - self.width
        if self.y + self.height > HEIGHT:
            self.y = HEIGHT - self.height

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

    def gantimerah(self, keys):
        if keys[pygame.K_1]:
            self.color = (255, 0, 0)

    def warnaawal(self, keys):
        if keys[pygame.K_2]:
            self.color = (0, 0, 255)

    def tambahukuran(self, keys):
        if keys[pygame.K_p]:
            self.width += 5
            self.height += 5

    def kurangiukuran(self, keys):
        if keys[pygame.K_o]:
            self.width -= 5
            self.height -= 5

player = Player(375, 275)
bg_color = (0, 255, 0)
change_bg_event = pygame.USEREVENT + 1

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == change_bg_event:
            bg_color = (0, 255, 0)

    keys = pygame.key.get_pressed()

    player.move(keys)
    player.gantimerah(keys)
    player.warnaawal(keys)
    player.kurangiukuran(keys)
    player.tambahukuran(keys)
    screen.fill(bg_color)
    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()