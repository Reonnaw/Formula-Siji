import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 600, 400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Praktikum PBO - Pygame")

WHITE = (0, 255, 0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)
    pygame.display.flip()

pygame.quit()
sys.exit()


#    clock.tick(60)
#clock = pygame.time.Clock()