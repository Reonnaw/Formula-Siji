import pygame as pg
import sys
import math
import random

WIDTH, HEIGHT = 320, 180
WINDOW_WIDTH, WINDOW_HEIGHT = 960, 540
SCALE = WINDOW_WIDTH // WIDTH
FPS = 60
TITLE = "Formula Siji"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (240, 40, 40)
YELLOW = (246, 216, 21)
GREEN = (40, 200, 80)
whiteish = (255, 255, 204)
OREN = (230, 130, 20)
GRAY = (120, 120, 130)
GELAP = (15, 15, 15)
BG = (204, 0, 0)
REDWARNING = (255, 60, 60, 55)
GAMEOVER = (0, 0, 0, 195)

JARAKMAX = 120
LANGIT = 60
LEBARJALAN = 500
SCREEN_CENTER_X = WIDTH // 2
JARAKMINOBJEK = 15
BATASJALANNPC = 120

MAX_CACHE_SIZE = 64

def S(v):
    return int(v * SCALE)

def calc_z(x: float) -> float:
    return 200 + 80 * math.sin(x / 13) - 120 * math.sin(x / 7)

def calc_y(x: float) -> float:
    return 200 * math.sin(x / 17) + 170 * math.sin(x / 8)

def elemen(layar, sprite, width, height, skala, x, player, y, z_buffer):
    y_offset = calc_y(x) - y
    z = calc_z(x) - player.z
    vertical = int(LANGIT + 160 * skala + z * skala)
    if 1 <= vertical < HEIGHT and z_buffer[vertical - 1] > 1 / skala - 10:
        horizontal = (SCREEN_CENTER_X - (SCREEN_CENTER_X - y_offset) * skala
                      + player.angle * (vertical - 150))
        w = max(1, int(width))
        h = max(1, int(height))
        sw, sh = sprite.get_size()
        if sw == w and sh == h:
            scaled = sprite
        else:
            scaled = pg.transform.scale(sprite, (w, h))
        layar.blit(scaled, (int(horizontal), vertical - h + 1))


class ScaleCache:
    def __init__(self, sprite: pg.Surface, max_size: int = MAX_CACHE_SIZE):
        self._sprite = sprite
        self._cache: dict = {}
        self._max = max_size

    def get(self, w: int, h: int) -> pg.Surface:
        key = (w, h)
        if key in self._cache:
            return self._cache[key]
        scaled = pg.transform.scale(self._sprite, (w, h))
        if len(self._cache) >= self._max:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = scaled
        return scaled

    @property
    def surface(self) -> pg.Surface:
        return self._sprite

class Objek:
    def __init__(self, x: float, y: float, sprite: pg.Surface = None):
        self.x = x
        self.y = y
        self._raw_sprite = sprite
        self._cache: ScaleCache | None = ScaleCache(sprite) if sprite is not None else None
        self.alive = True

    @property
    def sprite(self):
        return self._raw_sprite

    @sprite.setter
    def sprite(self, s: pg.Surface):
        self._raw_sprite = s
        self._cache = ScaleCache(s) if s is not None else None

    def update(self, delta: float, player_x: float):
        pass

    def render(self, layar: pg.Surface, player, z_buffer: list):
        if self._cache is None:
            return

        diff = self.x - player.x
        if diff <= 0.001:
            return

        skala = 1 / diff
        w = max(1, int(self.sprite_w(skala)))
        h = max(1, int(self.sprite_h(skala)))

        y_offset = calc_y(self.x) - (self.y + player.y)
        z = calc_z(self.x) - player.z
        vertical = int(LANGIT + 160 * skala + z * skala)
        if 1 <= vertical < HEIGHT and z_buffer[vertical - 1] > 1 / skala - 10:
            horizontal = (SCREEN_CENTER_X - (SCREEN_CENTER_X - y_offset) * skala
                          + player.angle * (vertical - 150))
            scaled = self._cache.get(w, h)
            layar.blit(scaled, (int(horizontal), vertical - h + 1))

    def sprite_w(self, skala: float) -> float:
        return 100 * skala

    def sprite_h(self, skala: float) -> float:
        return 100 * skala

class Pohon(Objek):
    JARAKMUNCUL = (10, 20)

    def __init__(self, prev_x: float, sprite: pg.Surface):
        x = prev_x + random.randint(*self.JARAKMUNCUL) + 0.5
        y = random.randint(500, 1500) * random.choice([-1, 1])
        super().__init__(x, y, sprite)

    def sprite_w(self, skala): return 200 * skala

    def sprite_h(self, skala): return 300 * skala

    def update(self, delta: float, player_x: float):
        if self.x < player_x + 1:
            self.alive = False

class Rintangan(Objek):
    JENIS = ["cone", "oil"]
    DAMAGE_MAP = {"cone": 15.0, "oil": 25.0}

    def __init__(self, x: float):
        self.kind = random.choice(self.JENIS)

        if self.kind == "cone":
            y = random.randint(-60, 60)
        else:
            y = random.randint(-40, 40)

        super().__init__(x, y, sprite=None)
        self.sprite = self._make_surface()

    def _make_surface(self) -> pg.Surface:
        if self.kind == "cone":
            surf = pg.Surface((16, 24), pg.SRCALPHA)
            pts = [(8, 0), (0, 24), (16, 24)]
            pg.draw.polygon(surf, OREN, pts)
            pg.draw.line(surf, WHITE, (3, 16), (13, 16), 2)
            pg.draw.circle(surf, WHITE, (8, 0), 2)
        else:
            surf = pg.Surface((40, 8), pg.SRCALPHA)
            pg.draw.ellipse(surf, (10, 10, 15, 200), (0, 8, 40, 16))
            pg.draw.ellipse(surf, (20, 20, 30, 180), (4, 4, 32, 16))
            pg.draw.ellipse(surf, (40, 40, 50, 120), (8, 6, 16, 6))
            pg.draw.ellipse(surf, (60, 60, 70, 80), (18, 10, 10, 4))
        return surf

    @property
    def damage(self) -> float:
        return self.DAMAGE_MAP[self.kind]

    def sprite_w(self, skala):
        return (16 if self.kind == "cone" else 60) * skala * 4

    def sprite_h(self, skala):
        return (24 if self.kind == "cone" else 8) * skala * 4

    def update(self, delta: float, player_x: float):
        if self.x < player_x - 5:
            self.alive = False


class Pertamini(Objek):
    BENSIN = 35.0

    def __init__(self, x: float):
        y = random.randint(-80, 80)
        surf = self._make_surface()
        super().__init__(x, y, surf)

    def _make_surface(self) -> pg.Surface:
        surf = pg.Surface((14, 20), pg.SRCALPHA)
        pg.draw.rect(surf, (220, 160, 20), (1, 4, 12, 16), border_radius=2)
        pg.draw.rect(surf, (255, 210, 60), (3, 6, 8, 10), border_radius=1)
        pg.draw.rect(surf, (180, 120, 10), (4, 0, 6, 6), border_radius=1)
        return surf

    def sprite_w(self, skala): return 14 * skala * 3

    def sprite_h(self, skala): return 20 * skala * 3

    def update(self, delta: float, player_x: float):
        if self.x < player_x - 5:
            self.alive = False

class mobilNPC(Objek):
    RKECEPATAN = (5, 12)

    def __init__(self, x: float, sprite: pg.Surface):
        y = random.uniform(-BATASJALANNPC, BATASJALANNPC)
        super().__init__(x, y, sprite)
        self.speed = random.uniform(*self.RKECEPATAN)
        self.sway_offset = random.uniform(-0.3, 0.3)
        self.sway_timer = 0.0

    def sprite_w(self, skala): return 100 * skala

    def sprite_h(self, skala): return 80 * skala

    def update(self, delta: float, player_x: float):
        self.x -= self.speed * delta

        self.sway_timer += delta * 2.0
        sway = math.sin(self.sway_timer) * 0.8

        self.y = self.sway_offset + sway
        self.y = max(-BATASJALANNPC, min(BATASJALANNPC, self.y))

        if self.x < player_x - 5:
            self.alive = False


class Player:
    BENSINMAX = 100.0
    BENSINKURANG = 2.5
    DAMAGEMAX = 100.0

    def __init__(self):
        self.x = 0.0
        self.y = calc_y(0.0)
        self.z = 0.0
        self.angle = 0.0
        self.velocity = 0.0
        self.acceleration = 0.0
        self.bensin = self.BENSINMAX
        self.damage = 0.0
        self.skor = 0
        self.jarak = 0.0
        self.timer = 0.0

    @property
    def speeddisplay(self) -> int:
        return int(abs(self.velocity) * 17)

    def isdead(self) -> bool:
        return self.damage >= self.DAMAGEMAX

    def kenadamage(self, amount: float):
        self.damage = min(self.damage + amount, self.DAMAGEMAX)
        self.velocity *= 0.4

    def kontrol(self, delta: float):
        keys = pg.key.get_pressed()

        self.acceleration += -0.5 * self.acceleration * delta
        self.velocity += -0.5 * self.velocity * delta

        if keys[pg.K_UP] or keys[pg.K_w]:
            if self.velocity > -1:
                self.acceleration += 4 * delta
            else:
                self.acceleration = 0
                self.velocity += -self.velocity * delta
        elif keys[pg.K_DOWN] or keys[pg.K_s]:
            if self.velocity < 1:
                self.acceleration -= delta
            else:
                self.acceleration = 0
                self.velocity += -self.velocity * delta

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.angle -= delta * self.velocity / 10
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.angle += delta * self.velocity / 10

        self.velocity = max(-10, min(self.velocity, 20))
        self.angle = max(-0.8, min(0.8, self.angle))
        self.velocity += self.acceleration * delta
        self.x += self.velocity * delta * math.cos(self.angle)
        self.y += self.velocity * math.sin(self.angle) * delta * 100

        if self.bensin > 0 and self.velocity > 0:
            self.bensin -= self.BENSINKURANG * (abs(self.velocity) / 20) * delta
            self.bensin = max(0.0, self.bensin)
        elif self.bensin <= 0:
            self.velocity += -self.velocity * delta * 2

        if self.timer > 0:
            self.timer -= delta

        self.jarak += abs(self.velocity) * delta * 10
        self.skor = int(self.jarak)

class HUD:
    def __init__(self):
        self.font_big   = pg.font.SysFont("Consolas", 11 * SCALE, bold=True)
        self.font_small = pg.font.SysFont("Consolas",  9 * SCALE)

    def _bar(self, surf, x, y, w, h, nilai, nilaimax, warna, warnawarning, label):
        lbl = self.font_small.render(label, True, WHITE)
        surf.blit(lbl, (x, y - S(10)))
        pg.draw.rect(surf, (30, 30, 40), (x, y, w, h), border_radius=S(2))
        rasio = max(0.0, nilai / nilaimax)
        warn = warnawarning if rasio < 0.3 else warna
        fill_w = max(1, int(w * rasio))
        pg.draw.rect(surf, warn, (x, y, fill_w, h), border_radius=S(2))
        pg.draw.rect(surf, GRAY, (x, y, w, h), 1, border_radius=S(2))

    def draw(self, screen: pg.Surface, player: Player):
        CX = WINDOW_WIDTH // 2

        kec = self.font_big.render(f"{player.speeddisplay} km/h", True, YELLOW)
        screen.blit(kec, (S(4), WINDOW_HEIGHT - S(20)))

        sc = self.font_big.render(f"SKOR {player.skor}", True, whiteish)
        screen.blit(sc, (WINDOW_WIDTH - sc.get_width() - S(4), S(4)))

        panel = pg.Surface((S(100), S(38)), pg.SRCALPHA)
        panel.fill((10, 10, 20, 185))
        screen.blit(panel, (S(2), S(2)))

        self._bar(screen, S(4), S(16), S(92), S(6),
                  player.bensin, Player.BENSINMAX, GREEN, RED, "BENSIN")
        self._bar(screen, S(4), S(30), S(92), S(6),
                  player.damage, Player.DAMAGEMAX, OREN, RED, "DAMAGE")

        tick = pg.time.get_ticks()
        if player.bensin < 20 and tick % 600 < 300:
            w = self.font_big.render("BENSIN KURANG!", True, RED)
            screen.blit(w, (CX - w.get_width() // 2, WINDOW_HEIGHT - S(30)))
        if player.damage > 70 and tick % 400 < 200:
            d = self.font_big.render("BAHAYA!", True, RED)
            screen.blit(d, (CX - d.get_width() // 2, WINDOW_HEIGHT - S(44)))


class Jalan:
    ROAD_ROW_CACHE_SIZE = 256

    def __init__(self, teksturjalan: pg.Surface, teksturgunung: pg.Surface):
        self.teksturjalan = teksturjalan
        self.teksturgunung = teksturgunung
        self._road_row_cache: dict = {}

    def _get_road_row(self, road_x: int, x: float) -> pg.Surface:
        road_width = self.teksturjalan.get_width()
        key = (road_x, int(10 * x) % 360)
        if key in self._road_row_cache:
            return self._road_row_cache[key]
        row = self.teksturjalan.subsurface(
            (road_x, int(10 * x) % 360, min(WIDTH, road_width), 1))
        if len(self._road_row_cache) >= self.ROAD_ROW_CACHE_SIZE:
            self._road_row_cache.pop(next(iter(self._road_row_cache)))
        self._road_row_cache[key] = row
        return row

    def draw(self, layar: pg.Surface, player: Player) -> list:
        layar.blit(self.teksturgunung, (-65 - player.angle * 82, 0))

        z_buffer = [999] * HEIGHT
        vertical = HEIGHT
        draw_distance = 1.0
        player.z = calc_z(player.x)

        road_width = self.teksturjalan.get_width()

        while draw_distance < JARAKMAX:
            last_vertical = vertical
            while vertical >= last_vertical and draw_distance < JARAKMAX:
                draw_distance += draw_distance / 150
                x = player.x + draw_distance
                skala = 1 / draw_distance
                z = calc_z(x) - player.z
                vertical = int(LANGIT + 160 * skala + z * skala)

            if draw_distance < JARAKMAX:
                if 0 <= int(vertical) < HEIGHT:
                    z_buffer[int(vertical)] = draw_distance
                    road_x = int(10 * x) % 360
                    if road_x + WIDTH > road_width:
                        road_x = road_x % max(1, road_width - WIDTH)

                warna = (
                    max(0, int(50 - draw_distance / 3)),
                    max(0, int(130 - draw_distance)),
                    max(0, int(50 - z / 20 + 30 * math.sin(x)))
                )
                pg.draw.rect(layar, warna, (0, vertical, WIDTH, 1))

                barisjalan = self._get_road_row(road_x, x)

                y_offset = calc_y(x) - player.y
                horizontal = (SCREEN_CENTER_X - (SCREEN_CENTER_X - y_offset) * skala
                              + player.angle * (vertical - 150))
                scaled_w = max(1, int(WIDTH * skala))
                if scaled_w != barisjalan.get_width():
                    row_scaled = pg.transform.scale(barisjalan, (scaled_w, 1))
                else:
                    row_scaled = barisjalan
                layar.blit(row_scaled, (int(horizontal), vertical))

        return z_buffer


class Game:
    INTERVALNPC = 35
    INTERVALRINTANGAN = 20
    INTERVALBENSIN = 60
    JARAKNABRAK = 1.5
    BATASAMPING = 80

    def __init__(self):
        pg.init()
        pg.mixer.pre_init(44100, -16, 2, 512)
        pg.display.set_caption(TITLE)

        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.layar = pg.Surface((WIDTH, HEIGHT))

        if sys.platform == "emscripten":
            import platform
            platform.window.canvas.style.imageRendering = "pixelated"

        self.clock = pg.time.Clock()

        self.font_title = pg.font.SysFont("Impact",   24 * SCALE)
        self.font_big   = pg.font.SysFont("Consolas", 12 * SCALE, bold=True)
        self.font_med   = pg.font.SysFont("Impact",  9 * SCALE)

        self.assets()
        self.hud = HUD()
        self.skortertinggi = 0
        self.state = "menu"
        self.waktutotal = 0.0

        self.player = None
        self.jalan = None
        self.pohon = []
        self.npc = []
        self.rintangan = []
        self.bensin = []

        self._next_npc = self.INTERVALNPC
        self._next_rintangan = self.INTERVALRINTANGAN
        self._next_bensin = self.INTERVALBENSIN

    def assets(self):
        def load(path, colorkey=None):
            if colorkey:
                img = pg.image.load(path).convert()
                img.set_colorkey(colorkey, pg.RLEACCEL)
                return img
            else:
                return pg.image.load(path).convert_alpha()

        self.teksturjalan = load("assets/road.png")
        self.teksturgunung = load("assets/mountains.png")
        self.mobilsprite = load("assets/car.png")

        self.mobilnpcsprite = load("assets/car2.png", (255, 0, 255))
        self.pohonsprite = load("assets/tree.png", (255, 0, 255))

        self.musikmenu = "assets/backgroundmusic.mp3"
        self.musikjalan = "assets/mobiljalan.mp3"
        self.musikgameover = "assets/gameover.mp3"
        self.musik_sekarang = None

    def musikmuter(self, track: str, loop: int = -1, volume: float = 0.5):
        if self.musik_sekarang == track:
            return
        pg.mixer.music.stop()
        pg.mixer.music.load(track)
        pg.mixer.music.set_volume(volume)
        pg.mixer.music.play(loop)
        self.musik_sekarang = track

    def mulaigame(self):
        self.player = Player()
        self.jalan  = Jalan(self.teksturjalan, self.teksturgunung)

        self.pohon     = [Pohon(-67 + i * 12, self.pohonsprite) for i in range(7)]
        self.npc       = []
        self.rintangan = []
        self.bensin    = []

        px = self.player.x
        self._next_npc        = px + self.INTERVALNPC
        self._next_rintangan  = px + self.INTERVALRINTANGAN
        self._next_bensin     = px + self.INTERVALBENSIN

        self.waktutotal = 0.0
        self.state = "playing"

    def _x_spawn(self) -> float:
        return self.player.x + JARAKMAX + 5

    def dorong(self, bukan: str, dari_x: float):
        min_x = dari_x + JARAKMINOBJEK
        if bukan != "rintangan" and self._next_rintangan < min_x:
            self._next_rintangan = min_x
        if bukan != "bensin" and self._next_bensin < min_x:
            self._next_bensin = min_x
        if bukan != "npc" and self._next_npc < min_x:
            self._next_npc = min_x

    def cekspawn(self):
        px = self.player.x

        if self.pohon and self.pohon[0].x < px + 1:
            last_tree_x = self.pohon[-1].x
            self.pohon.pop(0)
            self.pohon.append(Pohon(last_tree_x, self.pohonsprite))

        if px + JARAKMAX > self._next_npc and self.waktutotal > 1:
            spawn_x = self._x_spawn()
            self.npc.append(mobilNPC(spawn_x, self.mobilnpcsprite))
            self._next_npc = spawn_x + random.randint(
                self.INTERVALNPC, self.INTERVALNPC * 2)
            self.dorong("npc", spawn_x)

        if px + JARAKMAX > self._next_rintangan:
            spawn_x = self._x_spawn()
            self.rintangan.append(Rintangan(spawn_x))
            self._next_rintangan = spawn_x + random.randint(
                self.INTERVALRINTANGAN, self.INTERVALRINTANGAN * 2)
            self.dorong("rintangan", spawn_x)

        if px + JARAKMAX > self._next_bensin:
            spawn_x = self._x_spawn()
            self.bensin.append(Pertamini(spawn_x))
            self._next_bensin = spawn_x + random.randint(
                self.INTERVALBENSIN, self.INTERVALBENSIN * 2)
            self.dorong("bensin", spawn_x)

    def cektabrak(self):
        px = self.player.x
        player_lateral = self.player.y - calc_y(px)

        BOXSAMPING = 55
        BOXDEPAN = 1.8
        BOXBELAKANG = 0.3

        def deteksi(obj):
            jarak_z = obj.x - px
            if -BOXBELAKANG < jarak_z < BOXDEPAN:
                obj_lateral = obj.y
                kurva_drift = calc_y(obj.x) - calc_y(px)
                obj_lateral_normalized = obj_lateral + kurva_drift

                jarak_samping = abs(player_lateral - obj_lateral_normalized)
                return jarak_samping < BOXSAMPING
            return False

        for n in self.npc:
            if deteksi(n):
                self.player.kenadamage(20.0)
                n.alive = False

        for r in self.rintangan:
            if deteksi(r):
                self.player.kenadamage(r.damage)
                r.alive = False

        for b in self.bensin:
            if deteksi(b):
                self.player.bensin = min(Player.BENSINMAX, self.player.bensin + Pertamini.BENSIN)
                b.alive = False

    def update(self, delta: float):
        if self.state != "playing":
            return
        self.musikmuter(self.musikjalan, loop=-1, volume=0.5)
        self.waktutotal += delta
        self.player.kontrol(delta)
        self.player.z = calc_z(self.player.x)

        self.cekspawn()
        self.cektabrak()

        for group in (self.pohon, self.npc, self.rintangan, self.bensin):
            for obj in group:
                obj.update(delta, self.player.x)

        self.pohon     = [p for p in self.pohon     if p.alive]
        self.npc       = [n for n in self.npc       if n.alive]
        self.rintangan = [r for r in self.rintangan if r.alive]
        self.bensin    = [b for b in self.bensin    if b.alive]

        if (abs(self.player.y - calc_y(self.player.x + 2) - 100) > 280
                and self.player.velocity > 5):
            self.player.velocity    += -self.player.velocity    * delta
            self.player.acceleration += -self.player.acceleration * delta

        if self.player.isdead():
            self.skortertinggi = max(self.skortertinggi, self.player.skor)
            self.state = "game_over"

    def draw(self):
        if self.state == "menu":
            self._gambarMenu()
        elif self.state == "playing":
            self._gambarGame()
        elif self.state == "game_over":
            self._gambarGameOver()

        pg.display.update()

    def _gambarGame(self):
        self.layar.fill(BG)

        z_buffer = self.jalan.draw(self.layar, self.player)

        for p in reversed(self.pohon):
            p.render(self.layar, self.player, z_buffer)
        for n in reversed(self.npc):
            n.render(self.layar, self.player, z_buffer)
        for r in reversed(self.rintangan):
            r.render(self.layar, self.player, z_buffer)
        for b in reversed(self.bensin):
            b.render(self.layar, self.player, z_buffer)

        goyang = math.sin(self.waktutotal * self.player.velocity)
        mobil_x = SCREEN_CENTER_X - self.mobilsprite.get_width() // 2
        self.layar.blit(self.mobilsprite, (mobil_x, 120 + goyang))

        if (abs(self.player.y - calc_y(self.player.x + 2) - 100) > 280
                and self.player.velocity > 5):
            pg.draw.circle(self.layar, RED, (SCREEN_CENTER_X, 85), 3)

        scaled = pg.transform.scale(self.layar, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen.blit(scaled, (0, 0))

        if 0 < self.player.timer < 0.15:
            if int(self.waktutotal * 10) % 2 == 0:
                warning = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pg.SRCALPHA)
                warning.fill(REDWARNING)
                self.screen.blit(warning, (0, 0))

        self.hud.draw(self.screen, self.player)

    def _gambarMenu(self):
        self.musikmuter(self.musikmenu, loop=-1, volume=0.4)
        self.screen.fill(BG)
        CX = WINDOW_WIDTH // 2

        title = self.font_title.render(TITLE, True, YELLOW)
        self.screen.blit(title, (CX - title.get_width() // 2, S(10)))

        titlekecil = self.font_med.render("Better Than Efwan", True, whiteish)
        self.screen.blit(titlekecil, (CX - titlekecil.get_width() // 2, S(38)))

        kontrol = [
            ("W / UP",    "Gas"),
            ("S / DOWN",  "Rem"),
            ("A / LEFT",  "Kiri"),
            ("D / RIGHT", "Kanan"),
            ("", ""),
            ("Kuning", "Ambil bensin sebelum habis"),
            ("Merah",  "Hindari mobil & rintangan"),
        ]
        posisi_y = S(55)
        for tombol, keterangan in kontrol:
            if not tombol:
                posisi_y += S(5)
                continue
            teks_tombol      = self.font_med.render(tombol,      True, YELLOW)
            teks_keterangan  = self.font_med.render(keterangan,  True, WHITE)
            self.screen.blit(teks_tombol,     (CX - S(100), posisi_y))
            self.screen.blit(teks_keterangan, (CX + S(10),  posisi_y))
            posisi_y += S(14)

        if pg.time.get_ticks() % 900 < 600:
            s = self.font_big.render("[ ENTER ] MULAI", True, GREEN)
            self.screen.blit(s, (CX - s.get_width() // 2, S(150)))

        if self.skortertinggi > 0:
            st = self.font_med.render(
                f"SKOR TERTINGGI: {self.skortertinggi}", True, YELLOW)
            self.screen.blit(st, (CX - st.get_width() // 2, S(162)))

    def _gambarGameOver(self):
        self.musikmuter(self.musikgameover, loop=0, volume=0.6)
        scaled = pg.transform.scale(self.layar, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen.blit(scaled, (0, 0))

        CX = WINDOW_WIDTH // 2

        overlay = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pg.SRCALPHA)
        overlay.fill(GAMEOVER)
        self.screen.blit(overlay, (0, 0))

        go = self.font_title.render("GAME OVER", True, RED)
        self.screen.blit(go, (CX - go.get_width() // 2, S(25)))

        sk = self.font_big.render(f"Skor: {self.player.skor}", True, WHITE)
        self.screen.blit(sk, (CX - sk.get_width() // 2, S(60)))

        st = self.font_big.render(
            f"Skor Tertinggi: {self.skortertinggi}", True, YELLOW)
        self.screen.blit(st, (CX - st.get_width() // 2, S(78)))

        jar = self.font_med.render(
            f"Jarak: {int(self.player.jarak)} m", True, whiteish)
        self.screen.blit(jar, (CX - jar.get_width() // 2, S(96)))

        if pg.time.get_ticks() % 900 < 600:
            u = self.font_big.render("[ ENTER ] Coba Lagi", True, GREEN)
            self.screen.blit(u, (CX - u.get_width() // 2, S(118)))

        m = self.font_med.render("[ ESC ] Menu", True, GRAY)
        self.screen.blit(m, (CX - m.get_width() // 2, S(138)))

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
                            self.mulaigame()
                    if event.key == pg.K_ESCAPE:
                        if self.state in ("playing", "game_over"):
                            self.state = "menu"

            self.update(delta)
            self.draw()

if __name__ == "__main__":
    game = Game()
    game.run()
    pg.quit()