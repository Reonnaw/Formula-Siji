"""
Formula Siji - Pseudo-3D Racing Game
======================================
Konsep OOP yang diterapkan:
  - Class & Object  : GameObject, WorldObject, Car, Player, EnemyCar,
                      Obstacle, FuelPickup, Tree, HUD, Road, Game
  - Inheritance     :
      WorldObject  → (induk semua objek dunia)
          ├── Tree         (pohon tepi jalan)
          ├── Obstacle     (rintangan: cone, oil)
          ├── FuelPickup   (item bensin)
          └── EnemyCar     (mobil NPC)
      Player       → (karakter utama, bukan WorldObject karena kamera = player)
"""

import pygame as pg
import sys
import math
import random

# ─────────────────────────────────────────────────────────
#  KONSTANTA GLOBAL
# ─────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 320, 180
FPS          = 60
TITLE        = "Formula Siji"

# Warna HUD
C_BLACK      = (0,   0,   0)
C_WHITE      = (255, 255, 255)
C_RED        = (220, 40,  40)
C_YELLOW     = (240, 210, 30)
C_GREEN      = (40,  200, 80)
C_CYAN       = (40,  210, 220)
C_ORANGE     = (230, 130, 20)
C_GRAY       = (120, 120, 130)
C_DARK       = (15,  15,  25)

# Road / world constants
DRAW_DIST_MAX = 120
HORIZON_Y     = 60
ROAD_WIDTH    = 500    # pixel width at scale=1 (close up)


# ─────────────────────────────────────────────────────────
#  FUNGSI BANTU PERHITUNGAN JALAN (tidak berubah dari asli)
# ─────────────────────────────────────────────────────────
def calc_z(x: float) -> float:
    """Ketinggian jalan (sumbu Z = vertikal dunia) di posisi x."""
    return 200 + 80 * math.sin(x / 13) - 120 * math.sin(x / 7)


def calc_y(x: float) -> float:
    """Lebar kurva jalan (sumbu Y = horizontal dunia) di posisi x."""
    return 200 * math.sin(x / 17) + 170 * math.sin(x / 8)


# ─────────────────────────────────────────────────────────
#  FUNGSI RENDER ELEMEN (dipakai WorldObject & Road)
# ─────────────────────────────────────────────────────────
def render_element(screen, sprite, width, height, scale,
                   x, player, y, z_buffer):
    """
    Proyeksikan objek dunia ke layar menggunakan z-buffer.
    Logika pseudo-3D dipertahankan persis dari kode asli.
    """
    y_offset = calc_y(x) - y
    z        = calc_z(x) - player.z

    vertical = int(HORIZON_Y + 160 * scale + z * scale)
    if 1 <= vertical < SCREEN_H and z_buffer[vertical - 1] > 1 / scale - 10:
        horizontal = (160 - (160 - y_offset) * scale
                      + player.angle * (vertical - 150))
        scaled = pg.transform.scale(sprite, (max(1, int(width)),
                                             max(1, int(height))))
        screen.blit(scaled, (int(horizontal), vertical - int(height) + 1))


# ─────────────────────────────────────────────────────────
#  BASE CLASS — WorldObject
# ─────────────────────────────────────────────────────────
class WorldObject:
    """
    Kelas induk untuk semua objek yang hidup di dunia jalan.
    Menyimpan posisi dunia (x, y), sprite, dan status hidup.
    Semua subkelas wajib memanggil super().__init__().
    """
    def __init__(self, x: float, y: float, sprite: pg.Surface = None):
        self.x      = x        # posisi sepanjang jalan
        self.y      = y        # offset lateral dari tengah jalan
        self.sprite = sprite
        self.alive  = True

    def update(self, delta: float, player_x: float):
        """Override di subkelas untuk logika per-frame."""
        pass

    def render(self, screen: pg.Surface, player, z_buffer: list):
        """Render objek menggunakan proyeksi pseudo-3D."""
        if self.sprite is None:
            return
        scale = max(0.0001, 1 / (self.x - player.x))
        render_element(
            screen, self.sprite,
            self.sprite_w(scale), self.sprite_h(scale),
            scale, self.x, player, self.y + player.y, z_buffer
        )

    def sprite_w(self, scale: float) -> float:
        return 100 * scale

    def sprite_h(self, scale: float) -> float:
        return 100 * scale


# ─────────────────────────────────────────────────────────
#  TREE  (child of WorldObject)
# ─────────────────────────────────────────────────────────
class Tree(WorldObject):
    """
    Pohon di tepi jalan.
    Mewarisi WorldObject — hanya perlu tahu x, y, dan sprite.
    """
    SPAWN_GAP = (10, 20)

    def __init__(self, prev_x: float, sprite: pg.Surface):
        x = prev_x + random.randint(*self.SPAWN_GAP) + 0.5
        y = random.randint(500, 1500) * random.choice([-1, 1])
        super().__init__(x, y, sprite)

    def sprite_w(self, scale): return 200 * scale
    def sprite_h(self, scale): return 300 * scale

    def update(self, delta: float, player_x: float):
        if self.x < player_x + 1:
            self.alive = False


# ─────────────────────────────────────────────────────────
#  OBSTACLE  (child of WorldObject)
# ─────────────────────────────────────────────────────────
class Obstacle(WorldObject):
    """
    Rintangan di tengah jalan: cone atau oil spill.
    Dibuat secara prosedural (tidak butuh sprite gambar).
    Mewarisi WorldObject.
    """
    KINDS      = ["cone", "oil"]
    DAMAGE_MAP = {"cone": 15.0, "oil": 25.0}

    def __init__(self, x: float):
        # Lateral acak di area jalan (-200 s/d 200)
        y = random.randint(-200, 200)
        super().__init__(x, y, sprite=None)
        self.kind   = random.choice(self.KINDS)
        self.sprite = self._make_surface()

    def _make_surface(self) -> pg.Surface:
        """Buat sprite sederhana secara prosedural."""
        if self.kind == "cone":
            surf = pg.Surface((16, 24), pg.SRCALPHA)
            pts = [(8, 0), (0, 24), (16, 24)]
            pg.draw.polygon(surf, C_ORANGE, pts)
            pg.draw.line(surf, C_WHITE, (3, 16), (13, 16), 2)
            pg.draw.circle(surf, C_WHITE, (8, 0), 2)
        else:
            surf = pg.Surface((30, 16), pg.SRCALPHA)
            pg.draw.ellipse(surf, (20, 20, 50, 180), (0, 0, 30, 16))
            pg.draw.ellipse(surf, (100, 80, 200, 80), (5, 4, 14, 8))
        return surf

    @property
    def damage(self) -> float:
        return self.DAMAGE_MAP[self.kind]

    def sprite_w(self, scale):
        return (16 if self.kind == "cone" else 30) * scale * 6
    def sprite_h(self, scale):
        return (24 if self.kind == "cone" else 16) * scale * 6

    def update(self, delta: float, player_x: float):
        if self.x < player_x - 5:
            self.alive = False


# ─────────────────────────────────────────────────────────
#  FUEL PICKUP  (child of WorldObject)
# ─────────────────────────────────────────────────────────
class FuelPickup(WorldObject):
    """
    Item bensin yang bisa dipungut pemain.
    Mewarisi WorldObject.
    """
    RESTORE = 35.0

    def __init__(self, x: float):
        y = random.randint(-150, 150)
        surf = self._make_surface()
        super().__init__(x, y, surf)

    def _make_surface(self) -> pg.Surface:
        surf = pg.Surface((14, 20), pg.SRCALPHA)
        pg.draw.rect(surf, (220, 160, 20), (1, 4, 12, 16), border_radius=2)
        pg.draw.rect(surf, (255, 210, 60), (3, 6, 8, 10), border_radius=1)
        pg.draw.rect(surf, (180, 120, 10), (4, 0, 6, 6), border_radius=1)
        return surf

    def sprite_w(self, scale): return 14 * scale * 8
    def sprite_h(self, scale): return 20 * scale * 8

    def update(self, delta: float, player_x: float):
        if self.x < player_x - 5:
            self.alive = False


# ─────────────────────────────────────────────────────────
#  ENEMY CAR  (child of WorldObject)
# ─────────────────────────────────────────────────────────
class EnemyCar(WorldObject):
    """
    Mobil NPC yang bergerak di jalan.
    Mewarisi WorldObject + logika gerak sendiri.
    """
    SPEED_RANGE = (5, 12)

    def __init__(self, x: float, sprite: pg.Surface):
        y = random.randint(-150, 150)
        super().__init__(x, y, sprite)
        self.speed = random.uniform(*self.SPEED_RANGE)

    def sprite_w(self, scale): return 100 * scale
    def sprite_h(self, scale): return 80  * scale

    def update(self, delta: float, player_x: float):
        self.x -= self.speed * delta
        if self.x < player_x - 5:
            self.alive = False


# ─────────────────────────────────────────────────────────
#  PLAYER  (kelas mandiri — kamera = player)
# ─────────────────────────────────────────────────────────
class Player:
    """
    Karakter utama. Tidak mewarisi WorldObject karena player
    IS the camera — posisinya mendefinisikan dunia yang terlihat.
    Atribut tambahan: fuel, damage, score.
    """
    MAX_FUEL   = 100.0
    FUEL_BURN  = 2.5       # per detik saat bergerak
    MAX_DAMAGE = 100.0
    INVINCIBLE = 1.5       # detik kebal setelah nabrak

    def __init__(self):
        self.x            = 0.0
        self.y            = 300.0
        self.z            = 0.0
        self.angle        = 0.0
        self.velocity     = 0.0
        self.acceleration = 0.0
        self.fuel         = self.MAX_FUEL
        self.damage       = 0.0
        self.score        = 0
        self.distance     = 0.0
        self.inv_timer    = 0.0

    @property
    def speed_display(self) -> int:
        """Kecepatan dalam km/h untuk HUD."""
        return int(abs(self.velocity) * 17)

    def is_dead(self) -> bool:
        return self.damage >= self.MAX_DAMAGE

    def take_damage(self, amount: float):
        if self.inv_timer <= 0:
            self.damage    = min(self.damage + amount, self.MAX_DAMAGE)
            self.velocity *= 0.4
            self.inv_timer = self.INVINCIBLE

    def controls(self, delta: float):
        keys = pg.key.get_pressed()

        self.acceleration += -0.5 * self.acceleration * delta
        self.velocity     += -0.5 * self.velocity * delta

        if keys[pg.K_UP] or keys[pg.K_w]:
            if self.velocity > -1:
                self.acceleration += 4 * delta
            else:
                self.acceleration  = 0
                self.velocity += -self.velocity * delta
        elif keys[pg.K_DOWN] or keys[pg.K_s]:
            if self.velocity < 1:
                self.acceleration -= delta
            else:
                self.acceleration  = 0
                self.velocity += -self.velocity * delta

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.angle -= delta * self.velocity / 10
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.angle += delta * self.velocity / 10

        self.velocity = max(-10, min(self.velocity, 20))
        self.angle    = max(-0.8, min(0.8, self.angle))
        self.velocity += self.acceleration * delta
        self.x        += self.velocity * delta * math.cos(self.angle)
        self.y        += self.velocity * math.sin(self.angle) * delta * 100

        # Fuel burn
        if self.fuel > 0 and self.velocity > 0:
            self.fuel -= self.FUEL_BURN * (abs(self.velocity) / 20) * delta
            self.fuel  = max(0.0, self.fuel)
        elif self.fuel <= 0:
            self.velocity += -self.velocity * delta * 2

        # Invincibility countdown
        if self.inv_timer > 0:
            self.inv_timer -= delta

        # Score & distance
        self.distance += abs(self.velocity) * delta * 10
        self.score     = int(self.distance)


# ─────────────────────────────────────────────────────────
#  HUD
# ─────────────────────────────────────────────────────────
class HUD:
    """
    Menggambar informasi pemain di atas layar.
    Bukan WorldObject — menempel ke layar, bukan ke dunia.
    """
    def __init__(self):
        self.font_big   = pg.font.SysFont("Consolas", 9, bold=True)
        self.font_small = pg.font.SysFont("Consolas", 7)

    def _bar(self, surf, x, y, w, h, value, max_val, color, warn_color, label):
        lbl = self.font_small.render(label, True, C_WHITE)
        surf.blit(lbl, (x, y - 8))
        pg.draw.rect(surf, (30, 30, 40), (x, y, w, h), border_radius=2)
        ratio  = max(0.0, value / max_val)
        col    = warn_color if ratio < 0.3 else color
        fill_w = max(1, int(w * ratio))
        pg.draw.rect(surf, col, (x, y, fill_w, h), border_radius=2)
        pg.draw.rect(surf, C_GRAY, (x, y, w, h), 1, border_radius=2)

    def draw(self, screen: pg.Surface, player: Player):
        # Speed — kiri bawah
        spd = self.font_big.render(f"{player.speed_display} km/h", True, C_YELLOW)
        screen.blit(spd, (4, SCREEN_H - 12))

        # Score — kanan atas
        sc = self.font_big.render(f"SCORE {player.score}", True, C_CYAN)
        screen.blit(sc, (SCREEN_W - sc.get_width() - 4, 4))

        # Panel fuel & damage — kiri atas
        panel = pg.Surface((82, 32), pg.SRCALPHA)
        panel.fill((10, 10, 20, 185))
        screen.blit(panel, (2, 2))

        self._bar(screen, 4, 14, 76, 5,
                  player.fuel, Player.MAX_FUEL, C_GREEN, C_RED, "FUEL")
        self._bar(screen, 4, 26, 76, 5,
                  player.damage, Player.MAX_DAMAGE, C_ORANGE, C_RED, "DMG")

        # Warnings
        tick = pg.time.get_ticks()
        if player.fuel < 20 and tick % 600 < 300:
            w = self.font_big.render("LOW FUEL!", True, C_RED)
            screen.blit(w, (SCREEN_W // 2 - w.get_width() // 2, SCREEN_H - 20))
        if player.damage > 70 and tick % 400 < 200:
            d = self.font_big.render("DANGER!", True, C_RED)
            screen.blit(d, (SCREEN_W // 2 - d.get_width() // 2, SCREEN_H - 30))


# ─────────────────────────────────────────────────────────
#  ROAD
# ─────────────────────────────────────────────────────────
class Road:
    """
    Mengelola rendering jalan pseudo-3D + langit/gunung.
    Memisahkan logika visual jalan dari kelas Game.
    """
    def __init__(self, road_tex: pg.Surface, mountains_tex: pg.Surface):
        self.road_tex      = road_tex
        self.mountains_tex = mountains_tex

    def draw(self, screen: pg.Surface, player: Player) -> list:
        """
        Gambar langit, gunung, dan jalan.
        Kembalikan z_buffer untuk render WorldObjects.
        """
        screen.blit(self.mountains_tex, (-65 - player.angle * 82, 0))

        z_buffer      = [999] * SCREEN_H
        vertical      = SCREEN_H
        draw_distance = 1.0
        player.z      = calc_z(player.x)

        while draw_distance < DRAW_DIST_MAX:
            last_vertical = vertical
            while vertical >= last_vertical and draw_distance < DRAW_DIST_MAX:
                draw_distance += draw_distance / 150
                x              = player.x + draw_distance
                scale          = 1 / draw_distance
                z              = calc_z(x) - player.z
                vertical       = int(HORIZON_Y + 160 * scale + z * scale)

            if draw_distance < DRAW_DIST_MAX:
                z_buffer[int(vertical)] = draw_distance
                road_slice = self.road_tex.subsurface(
                    (0, int(10 * x) % 360, SCREEN_W, 1))
                color = (
                    max(0, int(50  - draw_distance / 3)),
                    max(0, int(130 - draw_distance)),
                    max(0, int(50  - z / 20 + 30 * math.sin(x)))
                )
                pg.draw.rect(screen, color, (0, vertical, SCREEN_W, 1))
                render_element(screen, road_slice,
                               ROAD_WIDTH * scale, 1, scale,
                               x, player, player.y, z_buffer)

        return z_buffer


# ─────────────────────────────────────────────────────────
#  GAME  (controller utama)
# ─────────────────────────────────────────────────────────
class Game:
    """
    Kelas utama — mengelola state, objek, dan loop permainan.
    State: 'menu' → 'playing' → 'game_over' → kembali ke 'menu'
    """
    ENEMY_INTERVAL    = 35
    OBSTACLE_INTERVAL = 20
    FUEL_INTERVAL     = 60
    COLLISION_DIST    = 3.5
    COLLISION_LAT     = 200

    def __init__(self):
        pg.init()
        pg.display.set_caption(TITLE)
        self.screen = pg.display.set_mode((SCREEN_W, SCREEN_H), pg.SCALED)
        self.clock  = pg.time.Clock()

        self.font_title = pg.font.SysFont("Impact", 24)
        self.font_big   = pg.font.SysFont("Consolas", 11, bold=True)
        self.font_med   = pg.font.SysFont("Consolas", 8)

        self._load_assets()
        self.hud        = HUD()
        self.high_score = 0
        self.state      = "menu"
        self.total_time = 0.0

        self.player    = None
        self.road      = None
        self.trees     = []
        self.enemies   = []
        self.obstacles = []
        self.fuels     = []

        self._next_enemy    = self.ENEMY_INTERVAL
        self._next_obstacle = self.OBSTACLE_INTERVAL
        self._next_fuel     = self.FUEL_INTERVAL

    # ── Asset Loading ────────────────────────────────────
    def _load_assets(self):
        def load(path, colorkey=None):
            img = pg.image.load(path).convert()
            if colorkey:
                img.set_colorkey(colorkey)
            return img

        self.road_tex    = load("assets/road.png")
        self.mtn_tex     = load("assets/mountains.png")
        self.car_sprite  = load("assets/car.png",  (255, 0, 255))
        self.car2_sprite = load("assets/car2.png", (255, 0, 255))
        self.tree_sprite = load("assets/tree.png", (255, 0, 255))

    # ── Inisialisasi Permainan Baru ───────────────────────
    def start_game(self):
        self.player = Player()
        self.road   = Road(self.road_tex, self.mtn_tex)

        self.trees = [Tree(-67 + i * 12, self.tree_sprite) for i in range(7)]
        self.enemies = [EnemyCar(-23 + i * 30, self.car2_sprite) for i in range(3)]
        self.obstacles = []
        self.fuels     = []

        px = self.player.x
        self._next_enemy    = px + self.ENEMY_INTERVAL
        self._next_obstacle = px + self.OBSTACLE_INTERVAL
        self._next_fuel     = px + self.FUEL_INTERVAL

        self.total_time = 0.0
        self.state      = "playing"

    # ── Spawn Logic ──────────────────────────────────────
    def _manage_spawns(self):
        px = self.player.x

        # Trees
        if self.trees and self.trees[0].x < px + 1:
            self.trees.pop(0)
            self.trees.append(Tree(self.trees[-1].x, self.tree_sprite))

        # Enemies
        if px + DRAW_DIST_MAX > self._next_enemy:
            self.enemies.append(EnemyCar(px + DRAW_DIST_MAX + 5, self.car2_sprite))
            self._next_enemy = px + DRAW_DIST_MAX + random.randint(
                self.ENEMY_INTERVAL, self.ENEMY_INTERVAL * 2)

        # Obstacles
        if px + DRAW_DIST_MAX > self._next_obstacle:
            self.obstacles.append(Obstacle(px + DRAW_DIST_MAX + 5))
            self._next_obstacle = px + DRAW_DIST_MAX + random.randint(
                self.OBSTACLE_INTERVAL, self.OBSTACLE_INTERVAL * 2)

        # Fuel
        if px + DRAW_DIST_MAX > self._next_fuel:
            self.fuels.append(FuelPickup(px + DRAW_DIST_MAX + 5))
            self._next_fuel = px + DRAW_DIST_MAX + random.randint(
                self.FUEL_INTERVAL, self.FUEL_INTERVAL * 2)

    # ── Collision Detection ──────────────────────────────
    def _check_collisions(self):
        px, py = self.player.x, self.player.y

        def near(obj) -> bool:
            return (abs(obj.x - px) < self.COLLISION_DIST and
                    abs(obj.y - py) < self.COLLISION_LAT)

        for e in self.enemies:
            if near(e):
                self.player.take_damage(20.0)
                e.alive = False

        for o in self.obstacles:
            if near(o):
                self.player.take_damage(o.damage)
                o.alive = False

        for f in self.fuels:
            if near(f):
                self.player.fuel = min(Player.MAX_FUEL,
                                       self.player.fuel + FuelPickup.RESTORE)
                f.alive = False

    # ── Update ───────────────────────────────────────────
    def update(self, delta: float):
        if self.state != "playing":
            return

        self.total_time += delta
        self.player.controls(delta)
        self.player.z = calc_z(self.player.x)

        self._manage_spawns()
        self._check_collisions()

        for group in (self.trees, self.enemies, self.obstacles, self.fuels):
            for obj in group:
                obj.update(delta, self.player.x)

        self.trees     = [t for t in self.trees     if t.alive]
        self.enemies   = [e for e in self.enemies   if e.alive]
        self.obstacles = [o for o in self.obstacles if o.alive]
        self.fuels     = [f for f in self.fuels     if f.alive]

        # Off-road speed penalty (dari kode asli)
        if (abs(self.player.y - calc_y(self.player.x + 2) - 100) > 280
                and self.player.velocity > 5):
            self.player.velocity     += -self.player.velocity * delta
            self.player.acceleration += -self.player.acceleration * delta

        if self.player.is_dead():
            self.high_score = max(self.high_score, self.player.score)
            self.state = "game_over"

    # ── Draw ─────────────────────────────────────────────
    def draw(self):
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "playing":
            self._draw_game()
        elif self.state == "game_over":
            self._draw_game_over()
        pg.display.update()

    def _draw_game(self):
        z_buffer = self.road.draw(self.screen, self.player)

        for t in reversed(self.trees):
            t.render(self.screen, self.player, z_buffer)
        for e in reversed(self.enemies):
            e.render(self.screen, self.player, z_buffer)
        for o in reversed(self.obstacles):
            o.render(self.screen, self.player, z_buffer)
        for f in reversed(self.fuels):
            f.render(self.screen, self.player, z_buffer)

        # Sprite player (posisi tetap di layar)
        bob = math.sin(self.total_time * self.player.velocity)
        self.screen.blit(self.car_sprite, (120, 120 + bob))

        # Off-road indicator
        if (abs(self.player.y - calc_y(self.player.x + 2) - 100) > 280
                and self.player.velocity > 5):
            pg.draw.circle(self.screen, C_RED, (300, 170), 3)

        self.hud.draw(self.screen, self.player)

        # Flash merah saat kebal
        if 0 < self.player.inv_timer < Player.INVINCIBLE:
            if int(self.total_time * 10) % 2 == 0:
                flash = pg.Surface((SCREEN_W, SCREEN_H), pg.SRCALPHA)
                flash.fill((255, 60, 60, 55))
                self.screen.blit(flash, (0, 0))

    def _draw_menu(self):
        self.screen.fill((10, 10, 20))

        title = self.font_title.render(TITLE, True, C_YELLOW)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 18))

        sub = self.font_med.render("Pseudo-3D Racing  |  PBO Pygame", True, C_CYAN)
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 46))

        lines = [
            ("W / UP",   "Gas"),
            ("S / DOWN", "Rem"),
            ("A / LEFT", "Belok Kiri"),
            ("D / RIGHT","Belok Kanan"),
            ("",         ""),
            ("Kuning",   "Ambil bensin sebelum habis!"),
            ("Merah",    "Hindari mobil & rintangan"),
        ]
        y = 66
        for key, desc in lines:
            if not key:
                y += 4
                continue
            ks = self.font_med.render(key,  True, C_YELLOW)
            ds = self.font_med.render(desc, True, C_WHITE)
            self.screen.blit(ks, (20, y))
            self.screen.blit(ds, (95, y))
            y += 11

        if pg.time.get_ticks() % 900 < 600:
            s = self.font_big.render("[ ENTER ] MULAI", True, C_GREEN)
            self.screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, 148))

        if self.high_score > 0:
            hs = self.font_med.render(f"High Score: {self.high_score}", True, C_YELLOW)
            self.screen.blit(hs, (SCREEN_W // 2 - hs.get_width() // 2, 168))

    def _draw_game_over(self):
        overlay = pg.Surface((SCREEN_W, SCREEN_H), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 195))
        self.screen.blit(overlay, (0, 0))

        go = self.font_title.render("GAME OVER", True, C_RED)
        self.screen.blit(go, (SCREEN_W // 2 - go.get_width() // 2, 28))

        sc = self.font_big.render(f"Skor: {self.player.score}", True, C_WHITE)
        self.screen.blit(sc, (SCREEN_W // 2 - sc.get_width() // 2, 72))

        hs = self.font_big.render(f"High Score: {self.high_score}", True, C_YELLOW)
        self.screen.blit(hs, (SCREEN_W // 2 - hs.get_width() // 2, 88))

        dist = self.font_med.render(f"Jarak: {int(self.player.distance)} m", True, C_CYAN)
        self.screen.blit(dist, (SCREEN_W // 2 - dist.get_width() // 2, 108))

        if pg.time.get_ticks() % 900 < 600:
            r = self.font_big.render("[ ENTER ] Coba Lagi", True, C_GREEN)
            self.screen.blit(r, (SCREEN_W // 2 - r.get_width() // 2, 134))

        m = self.font_med.render("[ ESC ] Menu", True, C_GRAY)
        self.screen.blit(m, (SCREEN_W // 2 - m.get_width() // 2, 154))

    # ── Main Loop ────────────────────────────────────────
    def run(self):
        self.clock.tick()
        pg.time.wait(16)

        while True:
            delta = max(self.clock.tick(FPS) / 1000.0, 0.0001)
            delta = min(delta, 0.05)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        if self.state in ("menu", "game_over"):
                            self.start_game()
                    if event.key == pg.K_ESCAPE:
                        if self.state in ("playing", "game_over"):
                            self.state = "menu"

            self.update(delta)
            self.draw()


# ─────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    game = Game()
    game.run()
    pg.quit()