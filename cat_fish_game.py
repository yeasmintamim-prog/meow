import pygame
import sys
import math
import random
import time

pygame.init()
pygame.mixer.init()

# ─── Background Music ───
import os
_music_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meow.mp3")
if os.path.exists(_music_path):
    pygame.mixer.music.load(_music_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # loop forever

# ─── Constants ───
WIDTH, HEIGHT = 900, 650
FPS = 60
TILE = 40

# Colors — refined palette
BG_TOP = (12, 12, 35)
BG_BOT = (25, 45, 80)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
GOLD_LIGHT = (255, 235, 120)
RED = (220, 50, 50)
RED_GLOW = (255, 80, 80)
GREEN = (80, 200, 120)
GREEN_LIGHT = (140, 255, 180)
ORANGE = (255, 160, 50)
CYAN = (0, 200, 220)
CYAN_GLOW = (80, 240, 255)
PINK = (255, 130, 170)
DARK = (10, 10, 25)
PANEL_BG = (20, 20, 50, 160)
PURPLE = (150, 80, 220)
PURPLE_GLOW = (180, 120, 255)
SOFT_WHITE = (220, 225, 240)
MUTED_BLUE = (100, 120, 180)

# ─── Helper Drawing Functions ───

def draw_gradient_bg(surf):
    """Premium multi-stop gradient background."""
    for y in range(HEIGHT):
        t = y / HEIGHT
        # Three-stop gradient: dark blue -> deep purple -> dark teal
        if t < 0.5:
            t2 = t * 2
            r = int(12 * (1 - t2) + 30 * t2)
            g = int(12 * (1 - t2) + 20 * t2)
            b = int(35 * (1 - t2) + 65 * t2)
        else:
            t2 = (t - 0.5) * 2
            r = int(30 * (1 - t2) + 18 * t2)
            g = int(20 * (1 - t2) + 50 * t2)
            b = int(65 * (1 - t2) + 85 * t2)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))


# Pre-render background
BG_SURFACE = pygame.Surface((WIDTH, HEIGHT))
draw_gradient_bg(BG_SURFACE)


def draw_glow(surf, x, y, radius, color, alpha=60):
    """Draw a soft radial glow."""
    glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    for i in range(6):
        r = radius * (1 + i * 0.5)
        a = max(0, alpha - i * 12)
        pygame.draw.circle(glow_surf, (*color[:3], a), (radius * 2, radius * 2), int(r))
    surf.blit(glow_surf, (int(x) - radius * 2, int(y) - radius * 2))


def draw_rounded_rect(surf, rect, color, radius=12, alpha=255):
    """Draw a rounded rectangle with alpha."""
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    c = (*color[:3], alpha) if len(color) == 3 else color
    pygame.draw.rect(s, c, (0, 0, rect[2], rect[3]), border_radius=radius)
    surf.blit(s, (rect[0], rect[1]))


def draw_glass_panel(surf, rect, base_color=(30, 30, 70), alpha=160, border_color=(80, 80, 140), border_alpha=80):
    """Draw a glassmorphism panel."""
    # Main panel
    draw_rounded_rect(surf, rect, base_color, radius=16, alpha=alpha)
    # Top highlight
    highlight = pygame.Surface((rect[2] - 8, 2), pygame.SRCALPHA)
    highlight.fill((255, 255, 255, 30))
    surf.blit(highlight, (rect[0] + 4, rect[1] + 4))
    # Border
    border_surf = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (*border_color[:3], border_alpha), (0, 0, rect[2], rect[3]), width=1, border_radius=16)
    surf.blit(border_surf, (rect[0], rect[1]))


def draw_star(surf, x, y, size, alpha_val):
    s = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
    c = (255, 255, 220, alpha_val)
    pygame.draw.circle(s, c, (size + 1, size + 1), size)
    # Cross sparkle for larger stars
    if size >= 2 and alpha_val > 150:
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            pygame.draw.line(s, (255, 255, 255, alpha_val // 2),
                             (size + 1, size + 1),
                             (size + 1 + dx * size * 2, size + 1 + dy * size * 2), 1)
    surf.blit(s, (x - size - 1, y - size - 1))


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT - 100)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 2.0)
        self.phase = random.uniform(0, math.pi * 2)

    def draw(self, surf, t):
        alpha = int(120 + 100 * math.sin(t * self.speed + self.phase))
        draw_star(surf, self.x, self.y, self.size, max(0, min(255, alpha)))


# ─── Nebula / Background Decoration ───

class Nebula:
    """Soft floating nebula blobs for atmospheric depth."""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = random.randint(80, 200)
        self.color = random.choice([
            (40, 20, 80), (20, 40, 70), (50, 15, 60), (15, 35, 55)
        ])
        self.drift_x = random.uniform(-0.1, 0.1)
        self.drift_y = random.uniform(-0.05, 0.05)
        self.phase = random.uniform(0, math.pi * 2)

    def draw(self, surf, t):
        alpha = int(18 + 8 * math.sin(t * 0.3 + self.phase))
        x = self.x + math.sin(t * 0.2 + self.phase) * 15
        y = self.y + math.cos(t * 0.15 + self.phase) * 10
        glow_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        for i in range(5):
            r = self.radius * (1 - i * 0.15)
            a = max(0, alpha - i * 4)
            pygame.draw.circle(glow_surf, (*self.color, a), (self.radius, self.radius), int(r))
        surf.blit(glow_surf, (int(x) - self.radius, int(y) - self.radius))


def draw_cat(surf, x, y, size, angle, frame, boosted):
    """Draw a cute cat facing `angle` direction with glow when boosted."""
    # Glow effect when boosted
    if boosted:
        draw_glow(surf, x, y, size, (200, 100, 255), alpha=40)

    s = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
    cx, cy = size + 2, size + 2

    # Shadow
    shadow_s = pygame.Surface((size * 2, int(size * 0.6)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_s, (0, 0, 0, 40), (0, 0, size * 2, int(size * 0.6)))
    surf.blit(shadow_s, (x - size, y + size - int(size * 0.1)))

    # body color
    if boosted:
        pulse = 0.8 + 0.2 * math.sin(frame * 0.15)
        body_col = (
            int(255 * pulse),
            int(100 * pulse),
            int(255 * pulse)
        )
    else:
        body_col = ORANGE
    dark_col = (body_col[0] // 2, body_col[1] // 2, body_col[2] // 2)

    # Tail wave
    tail_angle = math.sin(frame * 0.15) * 0.5
    tx = cx - int(math.cos(angle) * size * 0.7)
    ty = cy - int(math.sin(angle) * size * 0.7)
    tx2 = tx - int(math.cos(angle + tail_angle) * size * 0.5)
    ty2 = ty - int(math.sin(angle + tail_angle) * size * 0.5)
    tx3 = tx2 - int(math.cos(angle + tail_angle * 1.5) * size * 0.3)
    ty3 = ty2 - int(math.sin(angle + tail_angle * 1.5) * size * 0.3)
    pygame.draw.lines(s, dark_col, False, [(tx, ty), (tx2, ty2), (tx3, ty3)], max(3, size // 6))

    # Body
    pygame.draw.circle(s, body_col, (cx, cy), int(size * 0.55))
    # Body highlight
    highlight_x = cx - int(size * 0.15)
    highlight_y = cy - int(size * 0.15)
    pygame.draw.circle(s, (min(255, body_col[0] + 40), min(255, body_col[1] + 40), min(255, body_col[2] + 40), 80),
                        (highlight_x, highlight_y), int(size * 0.25))

    # Head position
    hx = cx + int(math.cos(angle) * size * 0.45)
    hy = cy + int(math.sin(angle) * size * 0.45)
    head_r = int(size * 0.4)
    pygame.draw.circle(s, body_col, (hx, hy), head_r)

    # Ears
    for side in [-1, 1]:
        ear_a = angle - math.pi / 2 * side + (math.pi * 0.15 * side)
        ex = hx + int(math.cos(angle) * head_r * 0.5) + int(math.cos(ear_a) * head_r * 0.6)
        ey = hy + int(math.sin(angle) * head_r * 0.5) + int(math.sin(ear_a) * head_r * 0.6)
        # Ear outline
        pygame.draw.polygon(s, dark_col, [
            (hx + int(math.cos(ear_a - 0.3) * head_r * 0.3), hy + int(math.sin(ear_a - 0.3) * head_r * 0.3)),
            (hx + int(math.cos(ear_a + 0.3) * head_r * 0.3), hy + int(math.sin(ear_a + 0.3) * head_r * 0.3)),
            (ex, ey)
        ])
        # Inner ear (pink)
        inner_scale = 0.6
        ix = hx + int(math.cos(angle) * head_r * 0.5 * inner_scale) + int(math.cos(ear_a) * head_r * 0.6 * inner_scale)
        iy = hy + int(math.sin(angle) * head_r * 0.5 * inner_scale) + int(math.sin(ear_a) * head_r * 0.6 * inner_scale)
        pygame.draw.polygon(s, (255, 150, 180, 120), [
            (hx + int(math.cos(ear_a - 0.2) * head_r * 0.2), hy + int(math.sin(ear_a - 0.2) * head_r * 0.2)),
            (hx + int(math.cos(ear_a + 0.2) * head_r * 0.2), hy + int(math.sin(ear_a + 0.2) * head_r * 0.2)),
            (ix, iy)
        ])

    # Eyes with shine
    for side in [-1, 1]:
        perp = angle + math.pi / 2 * side
        eye_x = hx + int(math.cos(angle) * head_r * 0.25) + int(math.cos(perp) * head_r * 0.25)
        eye_y = hy + int(math.sin(angle) * head_r * 0.25) + int(math.sin(perp) * head_r * 0.25)
        eye_r = max(2, head_r // 4)
        pygame.draw.circle(s, (240, 240, 200), (eye_x, eye_y), eye_r)
        pygame.draw.circle(s, DARK, (eye_x, eye_y), max(1, head_r // 6))
        # Eye shine
        shine_x = eye_x - 1
        shine_y = eye_y - 1
        pygame.draw.circle(s, (255, 255, 255, 200), (shine_x, shine_y), max(1, eye_r // 3))

    # Nose
    nx = hx + int(math.cos(angle) * head_r * 0.55)
    ny = hy + int(math.sin(angle) * head_r * 0.55)
    pygame.draw.circle(s, PINK, (nx, ny), max(1, head_r // 6))

    # Whiskers
    for side in [-1, 1]:
        perp = angle + math.pi / 2 * side
        wx1 = nx + int(math.cos(perp) * head_r * 0.3)
        wy1 = ny + int(math.sin(perp) * head_r * 0.3)
        for whisker_offset in [-0.15, 0, 0.15]:
            wx2 = wx1 + int(math.cos(perp + whisker_offset) * head_r * 0.6)
            wy2 = wy1 + int(math.sin(perp + whisker_offset) * head_r * 0.6)
            pygame.draw.line(s, (200, 200, 200, 120), (wx1, wy1), (wx2, wy2), 1)

    # Legs bob
    for side in [-1, 1]:
        perp = angle + math.pi / 2 * side
        bob = math.sin(frame * 0.3 + side) * size * 0.1
        lx = cx + int(math.cos(perp) * size * 0.35) + int(math.cos(angle) * bob)
        ly = cy + int(math.sin(perp) * size * 0.35) + int(math.sin(angle) * bob)
        pygame.draw.circle(s, dark_col, (lx, ly), max(2, size // 8))

    surf.blit(s, (int(x) - size - 2, int(y) - size - 2))


def draw_fish(surf, x, y, size, frame, color=CYAN):
    """Draw a cute animated fish with glow halo."""
    # Subtle glow
    draw_glow(surf, x, y, size, color, alpha=25)

    s = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
    cx, cy = size + 2, size + 2
    wobble = math.sin(frame * 0.12 + x) * 3

    # Body ellipse
    body_rect = pygame.Rect(cx - size // 2, cy - size // 3 + int(wobble), size, size * 2 // 3)
    pygame.draw.ellipse(s, color, body_rect)
    # Body highlight
    highlight_rect = pygame.Rect(cx - size // 4, cy - size // 4 + int(wobble), size // 2, size // 4)
    highlight_col = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60), 80)
    pygame.draw.ellipse(s, highlight_col, highlight_rect)

    # Tail
    tail_wave = math.sin(frame * 0.18 + x) * 2
    tail_pts = [
        (cx - size // 2, cy + int(wobble)),
        (cx - size // 2 - size // 3, cy - size // 4 + int(wobble + tail_wave)),
        (cx - size // 2 - size // 3, cy + size // 4 + int(wobble + tail_wave)),
    ]
    pygame.draw.polygon(s, (color[0] // 2, color[1] // 2, color[2]), tail_pts)

    # Dorsal fin
    fin_pts = [
        (cx, cy - size // 3 + int(wobble)),
        (cx - size // 6, cy - size // 2 + int(wobble)),
        (cx + size // 6, cy - size // 3 + int(wobble)),
    ]
    pygame.draw.polygon(s, (color[0] // 2, color[1], color[2] // 2, 150), fin_pts)

    # Eye
    pygame.draw.circle(s, WHITE, (cx + size // 5, cy - size // 10 + int(wobble)), max(2, size // 8))
    pygame.draw.circle(s, DARK, (cx + size // 5 + 1, cy - size // 10 + int(wobble)), max(1, size // 14))
    # Eye shine
    pygame.draw.circle(s, (255, 255, 255, 200), (cx + size // 5 - 1, cy - size // 10 + int(wobble) - 1), max(1, size // 16))

    # Scales pattern (subtle)
    for i in range(3):
        sx = cx - size // 6 + i * size // 6
        sy = cy + int(wobble)
        pygame.draw.arc(s, (*color[:3],), (sx - 3, sy - 3, 6, 6), 0, math.pi, 1)

    surf.blit(s, (int(x) - size - 2, int(y) - size - 2))


def draw_dog(surf, x, y, size, frame):
    """Draw a simple dog obstacle with red warning glow."""
    # Red warning glow
    draw_glow(surf, x, y, size, (200, 60, 60), alpha=30)

    s = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
    cx, cy = size + 2, size + 2
    col = (160, 100, 60)
    dark = (100, 60, 30)

    # Shadow
    shadow_s = pygame.Surface((size * 2, int(size * 0.5)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_s, (0, 0, 0, 35), (0, 0, size * 2, int(size * 0.5)))
    surf.blit(shadow_s, (int(x) - size, int(y) + size - int(size * 0.1)))

    # Body
    pygame.draw.circle(s, col, (cx, cy), int(size * 0.5))
    # Head
    hx, hy = cx + int(size * 0.35), cy - int(size * 0.2)
    pygame.draw.circle(s, col, (hx, hy), int(size * 0.35))
    # Ears
    pygame.draw.ellipse(s, dark, (hx - size // 2, hy - size // 3, size // 4, size // 3))
    pygame.draw.ellipse(s, dark, (hx + size // 5, hy - size // 3, size // 4, size // 3))
    # Eyes (angry red)
    pygame.draw.circle(s, WHITE, (hx - 3, hy - 2), max(2, size // 8))
    pygame.draw.circle(s, RED, (hx - 3, hy - 2), max(1, size // 14))
    # Eyebrow (angry)
    pygame.draw.line(s, dark, (hx - 6, hy - 6), (hx - 1, hy - 4), 2)
    # Nose
    pygame.draw.circle(s, DARK, (hx + int(size * 0.2), hy + 2), max(2, size // 10))
    # Tail wag
    ta = math.sin(frame * 0.2) * 0.6
    tx = cx - int(size * 0.5)
    ty = cy
    pygame.draw.line(s, dark, (tx, ty), (tx - int(math.cos(ta) * size * 0.4), ty - int(math.sin(ta + 1) * size * 0.4)), 3)

    # Collar
    collar_y = cy - int(size * 0.05)
    pygame.draw.arc(s, RED, (cx - int(size * 0.3), collar_y - 3, int(size * 0.6), 8), 0, math.pi, 2)

    surf.blit(s, (int(x) - size - 2, int(y) - size - 2))


def draw_catnip(surf, x, y, size, frame):
    """Draw a catnip power-up with pulsing glow."""
    pulse = 0.8 + 0.2 * math.sin(frame * 0.1)
    # Glow
    draw_glow(surf, x, y, int(size * pulse * 1.5), GREEN, alpha=35)

    s = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
    cx, cy = size + 2, size + 2
    r = int(size * 0.4 * pulse)

    # Outer ring
    pygame.draw.circle(s, (80, 255, 120, 50), (cx, cy), int(r * 1.8))
    # Main circle
    pygame.draw.circle(s, GREEN, (cx, cy), r)
    # Inner highlight
    pygame.draw.circle(s, (120, 255, 160), (cx - 2, cy - 2), r // 2)
    # Leaf shape
    leaf_pts = [
        (cx, cy - r),
        (cx + r // 2, cy - r - r // 2),
        (cx, cy - r - r),
        (cx - r // 2, cy - r - r // 2),
    ]
    pygame.draw.polygon(s, (60, 180, 80, 180), leaf_pts)

    # Sparkle
    for i in range(6):
        a = frame * 0.05 + i * math.pi / 3
        sparkle_r = r * 1.6 + math.sin(frame * 0.08 + i) * 4
        sx = cx + int(math.cos(a) * sparkle_r)
        sy = cy + int(math.sin(a) * sparkle_r)
        sparkle_alpha = int(150 + 80 * math.sin(frame * 0.1 + i))
        pygame.draw.circle(s, (200, 255, 200, min(255, sparkle_alpha)), (sx, sy), 2)
    surf.blit(s, (int(x) - size - 2, int(y) - size - 2))


class Particle:
    def __init__(self, x, y, color, size_range=(2, 5)):
        self.x, self.y = x, y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.randint(15, 35)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(size_range[0], size_range[1])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.vx *= 0.98
        self.life -= 1

    def draw(self, surf):
        alpha = int(255 * (self.life / self.max_life) ** 1.5)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], alpha), (self.size, self.size), self.size)
        surf.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


class ScorePopup:
    """Floating score text that rises and fades."""
    def __init__(self, x, y, text, color=GOLD):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 50
        self.max_life = 50

    def update(self):
        self.y -= 1.2
        self.life -= 1

    def draw(self, surf, font):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        scale = 0.8 + 0.4 * (self.life / self.max_life)
        txt = font.render(self.text, True, self.color)
        txt_s = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
        txt_s.blit(txt, (0, 0))
        txt_s.set_alpha(alpha)
        surf.blit(txt_s, (int(self.x) - txt.get_width() // 2, int(self.y) - txt.get_height() // 2))


class LevelUpBanner:
    """Animated level-up notification."""
    def __init__(self, level):
        self.level = level
        self.life = 120
        self.max_life = 120

    def update(self):
        self.life -= 1

    def draw(self, surf, font):
        if self.life <= 0:
            return
        progress = 1 - (self.life / self.max_life)
        # Slide in from top, then slide out
        if progress < 0.2:
            y = int(-40 + (80 + 40) * (progress / 0.2))
        elif progress > 0.8:
            fade = (progress - 0.8) / 0.2
            y = 80
            alpha = int(255 * (1 - fade))
        else:
            y = 80
            alpha = 255

        if progress <= 0.8:
            alpha = 255

        # Panel
        panel_w = 280
        panel_h = 50
        px = WIDTH // 2 - panel_w // 2
        draw_glass_panel(surf, (px, y, panel_w, panel_h), base_color=(50, 30, 80), alpha=min(200, alpha),
                         border_color=(150, 100, 255), border_alpha=min(120, alpha))

        # Text
        txt = font.render(f"⭐ Level {self.level}!", True, GOLD_LIGHT)
        txt_s = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
        txt_s.blit(txt, (0, 0))
        txt_s.set_alpha(min(255, alpha))
        surf.blit(txt_s, (WIDTH // 2 - txt.get_width() // 2, y + panel_h // 2 - txt.get_height() // 2))


class ComboCounter:
    """Tracks rapid fish eating for combo bonuses."""
    def __init__(self):
        self.count = 0
        self.timer = 0
        self.display_timer = 0

    def add(self):
        if self.timer > 0:
            self.count += 1
        else:
            self.count = 1
        self.timer = 120  # 2 seconds to keep combo alive
        self.display_timer = 80

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.count = 0
        if self.display_timer > 0:
            self.display_timer -= 1

    def get_multiplier(self):
        if self.count >= 5:
            return 3
        elif self.count >= 3:
            return 2
        return 1

    def draw(self, surf, font):
        if self.count >= 2 and self.display_timer > 0:
            alpha = int(255 * min(1, self.display_timer / 20))
            colors = [(255, 200, 50), (255, 150, 50), (255, 100, 50)]
            col = colors[min(len(colors) - 1, self.count - 2)]
            text = f"Combo x{self.count}!"
            if self.count >= 5:
                text = f"🔥 MEGA Combo x{self.count}!"
            elif self.count >= 3:
                text = f"⚡ Combo x{self.count}!"
            txt = font.render(text, True, col)
            txt_s = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
            txt_s.blit(txt, (0, 0))
            txt_s.set_alpha(alpha)
            # Pulsing effect
            pulse = 1 + 0.05 * math.sin(self.display_timer * 0.3)
            surf.blit(txt_s, (WIDTH // 2 - txt.get_width() // 2, 100))


# ─── Game Classes ───

class Cat:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.angle = 0
        self.speed = 3.0
        self.base_speed = 3.0
        self.size = 28
        self.boost_timer = 0
        self.lives = 3
        self.invincible = 0

    @property
    def boosted(self):
        return self.boost_timer > 0

    def update(self, keys):
        turn = 0.065
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= turn
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += turn

        spd = self.speed * (1.6 if self.boosted else 1.0)
        self.x += math.cos(self.angle) * spd
        self.y += math.sin(self.angle) * spd

        # Wrap around
        if self.x < -self.size: self.x = WIDTH + self.size
        if self.x > WIDTH + self.size: self.x = -self.size
        if self.y < -self.size: self.y = HEIGHT + self.size
        if self.y > HEIGHT + self.size: self.y = -self.size

        if self.boost_timer > 0:
            self.boost_timer -= 1
        if self.invincible > 0:
            self.invincible -= 1

    def draw(self, surf, frame):
        if self.invincible > 0 and (frame // 4) % 2 == 0:
            return  # blink effect
        draw_cat(surf, self.x, self.y, self.size, self.angle, frame, self.boosted)


class Fish:
    def __init__(self):
        self.respawn()
        self.size = 20

    def respawn(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(80, HEIGHT - 50)
        self.color = random.choice([CYAN, (100, 180, 255), (255, 200, 80), PINK])

    def draw(self, surf, frame):
        draw_fish(surf, self.x, self.y, self.size, frame, self.color)


class Dog:
    def __init__(self):
        self.respawn()
        self.size = 26
        self.vx = random.choice([-1.5, -1, 1, 1.5])
        self.vy = random.choice([-1.5, -1, 1, 1.5])

    def respawn(self):
        side = random.randint(0, 3)
        if side == 0: self.x, self.y = random.randint(0, WIDTH), -30
        elif side == 1: self.x, self.y = random.randint(0, WIDTH), HEIGHT + 30
        elif side == 2: self.x, self.y = -30, random.randint(0, HEIGHT)
        else: self.x, self.y = WIDTH + 30, random.randint(0, HEIGHT)
        self.vx = random.choice([-1.8, -1, 1, 1.8])
        self.vy = random.choice([-1.8, -1, 1, 1.8])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < -60 or self.x > WIDTH + 60 or self.y < -60 or self.y > HEIGHT + 60:
            self.respawn()

    def draw(self, surf, frame):
        draw_dog(surf, self.x, self.y, self.size, frame)


class Catnip:
    def __init__(self):
        self.x = random.randint(60, WIDTH - 60)
        self.y = random.randint(100, HEIGHT - 60)
        self.size = 18
        self.active = True
        self.timer = 600  # frames until despawn

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.active = False

    def draw(self, surf, frame):
        if self.active:
            draw_catnip(surf, self.x, self.y, self.size, frame)


# ─── Screen Shake ───
class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0

    def trigger(self, intensity=8, duration=15):
        self.intensity = intensity
        self.duration = duration

    def update(self):
        if self.duration > 0:
            self.duration -= 1
        else:
            self.intensity = 0

    def get_offset(self):
        if self.duration > 0:
            decay = self.duration / 15
            return (
                random.randint(-int(self.intensity * decay), int(self.intensity * decay)),
                random.randint(-int(self.intensity * decay), int(self.intensity * decay))
            )
        return (0, 0)


# ─── Main Game ───

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🐱 Kitty Fish Rush!")
    clock = pygame.time.Clock()

    # Fonts
    try:
        font_big = pygame.font.SysFont("Segoe UI", 56, bold=True)
        font_med = pygame.font.SysFont("Segoe UI", 28, bold=True)
        font_sm = pygame.font.SysFont("Segoe UI", 20)
        font_xs = pygame.font.SysFont("Segoe UI", 16)
        font_title = pygame.font.SysFont("Segoe UI", 64, bold=True)
    except Exception:
        font_big = pygame.font.Font(None, 56)
        font_med = pygame.font.Font(None, 28)
        font_sm = pygame.font.Font(None, 20)
        font_xs = pygame.font.Font(None, 16)
        font_title = pygame.font.Font(None, 64)

    stars = [Star() for _ in range(80)]
    nebulae = [Nebula() for _ in range(5)]

    # Game state
    STATE_MENU = 0
    STATE_PLAY = 1
    STATE_OVER = 2
    state = STATE_MENU

    cat = Cat()
    fishes = [Fish() for _ in range(3)]
    dogs = []
    catnips = []
    particles = []
    score = 0
    display_score = 0  # Animated score display
    high_score = 0
    level = 1
    frame = 0
    fish_eaten = 0
    score_popups = []
    level_banner = None
    combo = ComboCounter()
    shake = ScreenShake()
    game_over_frame = 0  # tracks when game over started

    def reset_game():
        nonlocal cat, fishes, dogs, catnips, particles, score, display_score, level, fish_eaten, frame
        nonlocal score_popups, level_banner, combo
        cat = Cat()
        fishes = [Fish() for _ in range(3)]
        dogs = [Dog()]
        catnips = []
        particles = []
        score = 0
        display_score = 0
        level = 1
        fish_eaten = 0
        frame = 0
        score_popups = []
        level_banner = None
        combo = ComboCounter()

    def spawn_particles(x, y, color, count=12):
        for _ in range(count):
            particles.append(Particle(x, y, color))

    def draw_heart(surf, x, y, size, filled=True):
        """Draw a proper heart shape."""
        pts = []
        for i in range(50):
            t = i / 50 * math.pi * 2
            hx = size * 0.5 * (16 * math.sin(t) ** 3) / 16
            hy = -size * 0.5 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16
            pts.append((x + int(hx), y + int(hy)))
        if filled:
            if len(pts) >= 3:
                pygame.draw.polygon(surf, RED, pts)
                # Highlight
                pygame.draw.polygon(surf, (255, 100, 100, 80), pts[:len(pts) // 3 + 2] + [pts[0]])
        else:
            if len(pts) >= 3:
                pygame.draw.polygon(surf, (80, 30, 30), pts, 1)

    def draw_hud(surf):
        nonlocal display_score
        # Animate score counting
        if display_score < score:
            display_score = min(score, display_score + max(1, (score - display_score) // 8))
        elif display_score > score:
            display_score = score

        # Top panel — glassmorphism
        draw_glass_panel(surf, (0, 0, WIDTH, 65), base_color=(15, 15, 40), alpha=180,
                         border_color=(60, 60, 120), border_alpha=60)

        # Score section
        score_icon = font_xs.render("SCORE", True, MUTED_BLUE)
        surf.blit(score_icon, (20, 6))
        score_val = font_med.render(f"{display_score:,}", True, GOLD)
        surf.blit(score_val, (20, 24))

        # High score
        hs_icon = font_xs.render("BEST", True, MUTED_BLUE)
        surf.blit(hs_icon, (180, 6))
        hs_val = font_sm.render(f"{high_score:,}", True, SOFT_WHITE)
        surf.blit(hs_val, (180, 26))

        # Level — centered
        level_text = font_xs.render("LEVEL", True, MUTED_BLUE)
        surf.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 6))
        level_val = font_med.render(str(level), True, PURPLE_GLOW)
        surf.blit(level_val, (WIDTH // 2 - level_val.get_width() // 2, 24))

        # Fish progress (next level)
        fish_to_next = 5 - (fish_eaten % 5)
        progress = (fish_eaten % 5) / 5
        bar_width = 80
        bar_x = WIDTH // 2 + 40
        bar_y = 35
        # Background bar
        draw_rounded_rect(surf, (bar_x, bar_y, bar_width, 8), (40, 40, 70), radius=4, alpha=150)
        # Fill bar
        fill_w = max(2, int(bar_width * progress))
        draw_rounded_rect(surf, (bar_x, bar_y, fill_w, 8), CYAN, radius=4, alpha=200)
        # Label
        fish_label = font_xs.render(f"{fish_to_next} to next", True, (120, 150, 180))
        surf.blit(fish_label, (bar_x + bar_width + 8, bar_y - 2))

        # Lives (hearts) — right side
        for i in range(cat.lives):
            hx = WIDTH - 30 - i * 30
            draw_heart(surf, hx, 30, 12, filled=True)

        # Lost lives (empty hearts)
        for i in range(3 - cat.lives):
            hx = WIDTH - 30 - (cat.lives + i) * 30
            draw_heart(surf, hx, 30, 12, filled=False)

        # Boost indicator bar
        if cat.boosted:
            boost_progress = cat.boost_timer / 300
            boost_bar_w = 200
            boost_bar_x = WIDTH // 2 - boost_bar_w // 2
            boost_bar_y = 70
            draw_rounded_rect(surf, (boost_bar_x, boost_bar_y, boost_bar_w, 6), (40, 20, 60), radius=3, alpha=150)
            fill_w = max(2, int(boost_bar_w * boost_progress))
            # Gradual color from green to yellow
            r = int(80 + (255 - 80) * (1 - boost_progress))
            g = int(200 * boost_progress + 100 * (1 - boost_progress))
            draw_rounded_rect(surf, (boost_bar_x, boost_bar_y, fill_w, 6), (r, g, 80), radius=3, alpha=220)
            txt = font_xs.render("⚡ CATNIP BOOST", True, GREEN_LIGHT)
            surf.blit(txt, (WIDTH // 2 - txt.get_width() // 2, boost_bar_y + 8))

    # ─── Menu animations ───
    menu_fish_positions = [(random.randint(100, WIDTH - 100), random.randint(200, 500)) for _ in range(5)]
    menu_fish_colors = [random.choice([CYAN, (100, 180, 255), (255, 200, 80), PINK]) for _ in range(5)]

    running = True
    while running:
        dt = clock.tick(FPS)
        frame += 1
        t = frame / FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if state == STATE_MENU and event.key == pygame.K_SPACE:
                    reset_game()
                    state = STATE_PLAY
                elif state == STATE_OVER and event.key == pygame.K_SPACE:
                    state = STATE_MENU
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # ─── RENDER TO BUFFER ───
        buffer = pygame.Surface((WIDTH, HEIGHT))

        # ─── DRAW BACKGROUND ───
        buffer.blit(BG_SURFACE, (0, 0))

        # Nebulae (behind everything)
        for neb in nebulae:
            neb.draw(buffer, t)

        for star in stars:
            star.draw(buffer, t)

        # ─── MENU STATE ───
        if state == STATE_MENU:
            # Floating fish in background
            for i, (fx, fy) in enumerate(menu_fish_positions):
                bob_x = fx + math.sin(t * 0.5 + i) * 30
                bob_y = fy + math.cos(t * 0.7 + i * 0.5) * 15
                draw_fish(buffer, bob_x, bob_y, 18, frame, menu_fish_colors[i])

            # Title panel
            title_y = 120 + math.sin(t * 0.8) * 5
            draw_glass_panel(buffer, (WIDTH // 2 - 240, int(title_y) - 15, 480, 80),
                             base_color=(30, 20, 60), alpha=180,
                             border_color=(255, 200, 50), border_alpha=60)

            # Title text with shadow
            title_shadow = font_title.render("Kitty Fish Rush!", True, (40, 30, 10))
            buffer.blit(title_shadow, (WIDTH // 2 - title_shadow.get_width() // 2 + 2, int(title_y) + 2))
            title = font_title.render("Kitty Fish Rush!", True, GOLD)
            buffer.blit(title, (WIDTH // 2 - title.get_width() // 2, int(title_y)))

            # Subtitle
            sub = font_sm.render("A Purrfect Adventure", True, MUTED_BLUE)
            buffer.blit(sub, (WIDTH // 2 - sub.get_width() // 2, int(title_y) + 70))

            # Animated cat preview — figure-8 motion
            cat_preview_x = WIDTH // 2 - 80 + math.sin(t * 0.6) * 50
            cat_preview_y = 300 + math.sin(t * 1.2) * 20
            draw_cat(buffer, cat_preview_x, cat_preview_y, 40, math.sin(t) * 0.5 + math.pi * 0.25, frame, False)

            # Fish preview — bobbing
            fish_preview_x = WIDTH // 2 + 80 + math.cos(t * 0.5) * 20
            fish_preview_y = 300 + math.sin(t * 0.8) * 15
            draw_fish(buffer, fish_preview_x, fish_preview_y, 30, frame, CYAN)

            # Instructions panel
            inst_panel_y = 380
            draw_glass_panel(buffer, (WIDTH // 2 - 200, inst_panel_y - 10, 400, 200),
                             base_color=(20, 20, 50), alpha=160,
                             border_color=(80, 80, 140), border_alpha=50)

            instructions = [
                ("🎮", "Arrow Keys / A-D : Steer the cat", WHITE),
                ("🐟", "Eat fish to score points!", CYAN_GLOW),
                ("🐕", "Avoid dogs — they bite!", RED_GLOW),
                ("🌿", "Grab catnip for speed boost!", GREEN_LIGHT),
            ]
            for i, (emoji, line, col) in enumerate(instructions):
                txt = font_sm.render(f"  {emoji}  {line}", True, col)
                buffer.blit(txt, (WIDTH // 2 - txt.get_width() // 2, inst_panel_y + 15 + i * 35))

            # Start button — pulsing
            btn_pulse = 0.9 + 0.1 * math.sin(t * 3)
            btn_w = int(220 * btn_pulse)
            btn_h = int(45 * btn_pulse)
            btn_x = WIDTH // 2 - btn_w // 2
            btn_y = 590
            draw_glass_panel(buffer, (btn_x, btn_y, btn_w, btn_h),
                             base_color=(60, 180, 100), alpha=200,
                             border_color=(120, 255, 160), border_alpha=120)
            start_txt = font_med.render("Press SPACE", True, WHITE)
            buffer.blit(start_txt, (WIDTH // 2 - start_txt.get_width() // 2,
                                    btn_y + btn_h // 2 - start_txt.get_height() // 2))

        # ─── PLAY STATE ───
        elif state == STATE_PLAY:
            keys = pygame.key.get_pressed()
            cat.update(keys)
            combo.update()
            shake.update()

            # Dogs
            for dog in dogs:
                dog.update()
                dog.draw(buffer, frame)
                # Collision with cat
                dist = math.hypot(cat.x - dog.x, cat.y - dog.y)
                if dist < cat.size + dog.size - 8 and cat.invincible <= 0:
                    cat.lives -= 1
                    cat.invincible = 90
                    spawn_particles(cat.x, cat.y, RED, 25)
                    shake.trigger(10, 20)
                    if cat.lives <= 0:
                        high_score = max(high_score, score)
                        state = STATE_OVER
                        game_over_frame = frame  # record when game over started

            # Fish
            for fish in fishes:
                fish.draw(buffer, frame)
                dist = math.hypot(cat.x - fish.x, cat.y - fish.y)
                if dist < cat.size + fish.size:
                    combo.add()
                    multiplier = combo.get_multiplier()
                    points = 10 * level * multiplier
                    score += points
                    fish_eaten += 1
                    spawn_particles(fish.x, fish.y, fish.color, 18)
                    # Score popup
                    popup_text = f"+{points}"
                    if multiplier > 1:
                        popup_text += f" x{multiplier}"
                    score_popups.append(ScorePopup(fish.x, fish.y - 20, popup_text, GOLD_LIGHT))
                    fish.respawn()

                    # Level up every 5 fish
                    if fish_eaten % 5 == 0:
                        level += 1
                        cat.speed = cat.base_speed + level * 0.3
                        level_banner = LevelUpBanner(level)
                        # Big level-up particle burst
                        for _ in range(30):
                            particles.append(Particle(WIDTH // 2, 80, random.choice([GOLD, CYAN, PURPLE_GLOW]), (3, 7)))
                        if len(dogs) < 3 + level:
                            dogs.append(Dog())
                        if len(fishes) < 5 + level // 2:
                            fishes.append(Fish())

            # Catnip spawning
            if random.random() < 0.003 and len(catnips) < 2:
                catnips.append(Catnip())

            for cn in catnips:
                cn.update()
                cn.draw(buffer, frame)
                dist = math.hypot(cat.x - cn.x, cat.y - cn.y)
                if dist < cat.size + cn.size and cn.active:
                    cat.boost_timer = 300
                    cn.active = False
                    spawn_particles(cn.x, cn.y, GREEN, 25)
                    score += 25
                    score_popups.append(ScorePopup(cn.x, cn.y - 20, "+25 ⚡", GREEN_LIGHT))

            catnips = [c for c in catnips if c.active]

            # Particles
            for p in particles:
                p.update()
                p.draw(buffer)
            particles = [p for p in particles if p.life > 0]

            # Cat trail when boosted
            if cat.boosted and frame % 2 == 0:
                trail_col = random.choice([(100, 255, 100), (200, 100, 255), (255, 200, 100)])
                particles.append(Particle(cat.x + random.uniform(-5, 5),
                                          cat.y + random.uniform(-5, 5),
                                          trail_col, (1, 4)))

            # Score popups
            for popup in score_popups:
                popup.update()
                popup.draw(buffer, font_med)
            score_popups = [p for p in score_popups if p.life > 0]

            # Level banner
            if level_banner:
                level_banner.update()
                level_banner.draw(buffer, font_med)
                if level_banner.life <= 0:
                    level_banner = None

            # Combo display
            combo.draw(buffer, font_med)

            cat.draw(buffer, frame)
            draw_hud(buffer)

        # ─── GAME OVER STATE ───
        elif state == STATE_OVER:
            # Dim overlay with gradient
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for y in range(HEIGHT):
                alpha_val = int(120 + 60 * (y / HEIGHT))
                pygame.draw.line(overlay, (0, 0, 0, alpha_val), (0, y), (WIDTH, y))
            buffer.blit(overlay, (0, 0))

            # Game Over panel
            panel_w, panel_h = 420, 340
            panel_x = WIDTH // 2 - panel_w // 2
            panel_y = 140
            draw_glass_panel(buffer, (panel_x, panel_y, panel_w, panel_h),
                             base_color=(25, 15, 45), alpha=220,
                             border_color=(220, 50, 50), border_alpha=100)

            # Title
            go_shadow = font_big.render("Game Over!", True, (80, 20, 20))
            buffer.blit(go_shadow, (WIDTH // 2 - go_shadow.get_width() // 2 + 2, panel_y + 22))
            go_txt = font_big.render("Game Over!", True, RED_GLOW)
            buffer.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, panel_y + 20))

            # Divider line
            div_y = panel_y + 90
            div_surf = pygame.Surface((panel_w - 40, 1), pygame.SRCALPHA)
            for x in range(panel_w - 40):
                a = int(60 * (1 - abs(x / (panel_w - 40) - 0.5) * 2))
                div_surf.set_at((x, 0), (150, 100, 100, a))
            buffer.blit(div_surf, (panel_x + 20, div_y))

            # Stats
            stats_y = div_y + 20
            # Score
            lbl = font_xs.render("FINAL SCORE", True, MUTED_BLUE)
            buffer.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, stats_y))
            val = font_big.render(f"{score:,}", True, GOLD)
            buffer.blit(val, (WIDTH // 2 - val.get_width() // 2, stats_y + 18))

            # High score & level
            row_y = stats_y + 85
            # High score
            lbl = font_xs.render("HIGH SCORE", True, MUTED_BLUE)
            buffer.blit(lbl, (panel_x + 60, row_y))
            val = font_med.render(f"{high_score:,}", True, SOFT_WHITE)
            buffer.blit(val, (panel_x + 60, row_y + 18))

            # Level
            lbl = font_xs.render("LEVEL", True, MUTED_BLUE)
            buffer.blit(lbl, (panel_x + panel_w - 140, row_y))
            val = font_med.render(str(level), True, CYAN_GLOW)
            buffer.blit(val, (panel_x + panel_w - 140, row_y + 18))

            # Fish eaten
            lbl = font_xs.render("FISH EATEN", True, MUTED_BLUE)
            buffer.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, row_y + 60))
            val = font_med.render(str(fish_eaten), True, PINK)
            buffer.blit(val, (WIDTH // 2 - val.get_width() // 2, row_y + 78))

            # Buttons
            btn_y = panel_y + panel_h + 20
            # Menu button
            btn_pulse = 0.9 + 0.1 * math.sin(t * 3)
            btn_w = int(280 * btn_pulse)
            btn_h = int(45 * btn_pulse)
            btn_x = WIDTH // 2 - btn_w // 2
            draw_glass_panel(buffer, (btn_x, btn_y, btn_w, btn_h),
                             base_color=(50, 50, 100), alpha=200,
                             border_color=(120, 120, 200), border_alpha=120)
            btn_txt = font_sm.render("Press SPACE for menu  |  ESC to quit", True, SOFT_WHITE)
            buffer.blit(btn_txt, (WIDTH // 2 - btn_txt.get_width() // 2,
                                  btn_y + btn_h // 2 - btn_txt.get_height() // 2))

            # Decorative floating particles on game over screen
            if frame % 8 == 0:
                px = random.randint(panel_x, panel_x + panel_w)
                particles.append(Particle(px, panel_y + panel_h, random.choice([GOLD, RED, PURPLE]), (1, 3)))
                particles[-1].vy = random.uniform(-2, -0.5)
                particles[-1].vx = random.uniform(-0.5, 0.5)

            for p in particles:
                p.update()
                p.draw(buffer)
            particles = [p for p in particles if p.life > 0]

        # ─── Apply screen shake and draw ───
        # Shake only during play, and carry over into game over for max 3 seconds (180 frames)
        if state == STATE_PLAY:
            offset = shake.get_offset()
        elif state == STATE_OVER and (frame - game_over_frame) < 180:
            shake.update()
            offset = shake.get_offset()
        else:
            offset = (0, 0)

        screen.fill(DARK)
        screen.blit(buffer, offset)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
