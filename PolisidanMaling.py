import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 600, 400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Kejar Maling")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLUE = (50, 120, 220)
RED = (210, 50, 50)
BLACK = (0, 0, 0)
GREEN = (34, 107, 94)
GREEN_HOVER = (22, 163, 74)
BG_COLOR = (45, 52, 75)
GRID_COLOR = (55, 63, 88)

class Character:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = color
        self.speed = 6

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, [self.x, self.y, self.width, self.height])

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Polisi(Character):
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

class Maling(Character):
    def move(self, keys):
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if self.x<0:
            self.x = 0
        if self.y<0:
            self.y = 0
        if self.x + self.width > WIDTH:
            self.x = WIDTH - self.width
        if self.y + self.height > HEIGHT:
            self.y = HEIGHT - self.height

def resetgame():
    polisi = Polisi(100, 200, BLUE)
    maling = Maling(400, 200, RED)
    return polisi, maling, False

def draw_bg(surface):
    surface.fill(BG_COLOR)
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))

polisi, maling, game_over = resetgame()

font_large = pygame.font.SysFont(None, 58)
font_medium = pygame.font.SysFont(None, 34)
font_small = pygame.font.SysFont(None, 38)

btn_width, btn_height = 160, 50
btn_x = WIDTH // 2 - btn_width // 2
btn_y = 280
btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over and btn_rect.collidepoint(mouse_pos):
                polisi, maling, game_over = resetgame()

    keys = pygame.key.get_pressed()

    if not game_over:
        polisi.move(keys)
        maling.move(keys)

        if polisi.get_rect().colliderect(maling.get_rect()):
            game_over = True

    draw_bg(screen)

    polisi.draw(screen)
    maling.draw(screen)

    if game_over:
        panel = pygame.Surface((420, 120), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 160), (0, 0, 420, 120), border_radius=12)
        screen.blit(panel, (WIDTH//2 - 210, 150))

        line1 = font_large.render("Maling Tertangkap!", True, (255, 220, 50))
        line2 = font_medium.render("Polisi berhasil mengamankan situasi.", True, (200, 200, 200))
        screen.blit(line1, (WIDTH//2 - line1.get_width()//2, 162))
        screen.blit(line2, (WIDTH//2 - line2.get_width()//2, 218))

        is_hover = btn_rect.collidepoint(mouse_pos)
        btn_color = GREEN_HOVER if is_hover else GREEN
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=10)

        label = font_small.render("Ulangi", True, WHITE)
        screen.blit(label, (btn_rect.centerx - label.get_width()//2, btn_rect.centery - label.get_height()//2))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()