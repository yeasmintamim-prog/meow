import pygame
import sys
import math
import random
import time

pygame.init()

# ─── Constants ───
WIDTH, HEIGHT = 900, 650
FPS = 60
TILE = 40

# Colors
BG_TOP = (20, 20, 45)
BG_BOT = (40, 60, 90)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
RED = (220, 50, 50)
GREEN = (80, 200, 120)
ORANGE = (255, 160, 50)
CYAN = (0, 200, 220)
PINK = (255, 130, 170)
DARK = (15, 15, 30)
PANEL_BG = (30, 30, 60, 200)

# ─── Helper Drawing Functions ───

def draw_gradient_bg(surf):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

# Pre-render background
BG_SURFACE = pygame.Surface((WIDTH, HEIGHT))
draw_gradient_bg(BG_SURFACE)

def draw_star(surf, x, y, size, alpha_val):
    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    c = (255, 255, 220, alpha_val)
    pygame.draw.circle(s, c, (size, size), size)
    surf.blit(s, (x - size, y - size))

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


def draw_cat(surf, x, y, size, angle, frame, boosted):
    """Draw a cute cat facing `angle` direction."""
    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx, cy = size, size

    # body color
    body_col = ORANGE if not boosted else (255, 100, 255)
    dark_col = (body_col[0] // 2, body_col[1] // 2, body_col[2] // 2)

    # Tail wave
    tail_angle = math.sin(frame * 0.15) * 0.5
    tx = cx - int(math.cos(angle) * size * 0.7)
    ty = cy - int(math.sin(angle) * size * 0.7)
    tx2 = tx - int(math.cos(angle + tail_angle) * size * 0.5)
    ty2 = ty - int(math.sin(angle + tail_angle) * size * 0.5)
    pygame.draw.line(s, dark_col, (tx, ty), (tx2, ty2), max(3, size // 6))

    # Body
    pygame.draw.circle(s, body_col, (cx, cy), int(size * 0.55))

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
        pygame.draw.polygon(s, dark_col, [
            (hx + int(math.cos(ear_a - 0.3) * head_r * 0.3), hy + int(math.sin(ear_a - 0.3) * head_r * 0.3)),
            (hx + int(math.cos(ear_a + 0.3) * head_r * 0.3), hy + int(math.sin(ear_a + 0.3) * head_r * 0.3)),
            (ex, ey)
        ])

    # Eyes
    for side in [-1, 1]:
        perp = angle + math.pi / 2 * side
        eye_x = hx + int(math.cos(angle) * head_r * 0.25) + int(math.cos(perp) * head_r * 0.25)
        eye_y = hy + int(math.sin(angle) * head_r * 0.25) + int(math.sin(perp) * head_r * 0.25)
        pygame.draw.circle(s, (240, 240, 200), (eye_x, eye_y), max(2, head_r // 4))
        pygame.draw.circle(s, DARK, (eye_x, eye_y), max(1, head_r // 6))

    # Nose
    nx = hx + int(math.cos(angle) * head_r * 0.55)
    ny = hy + int(math.sin(angle) * head_r * 0.55)
    pygame.draw.circle(s, PINK, (nx, ny), max(1, head_r // 6))

    # Legs bob
    for side in [-1, 1]:
        perp = angle + math.pi / 2 * side
        bob = math.sin(frame * 0.3 + side) * size * 0.1
        lx = cx + int(math.cos(perp) * size * 0.35) + int(math.cos(angle) * bob)
        ly = cy + int(math.sin(perp) * size * 0.35) + int(math.sin(angle) * bob)
        pygame.draw.circle(s, dark_col, (lx, ly), max(2, size // 8))

    surf.blit(s, (x - size, y - size))


def draw_fish(surf, x, y, size, frame, color=CYAN):
    """Draw a cute animated fish."""
    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx, cy = size, size
    wobble = math.sin(frame * 0.12 + x) * 3

    # Body ellipse
    body_rect = pygame.Rect(cx - size // 2, cy - size // 3 + wobble, size, size * 2 // 3)
    pygame.draw.ellipse(s, color, body_rect)

    # Tail
    tail_pts = [
        (cx - size // 2, cy + wobble),
        (cx - size // 2 - size // 3, cy - size // 4 + wobble),
        (cx - size // 2 - size // 3, cy + size // 4 + wobble),
    ]
    pygame.draw.polygon(s, (color[0] // 2, color[1] // 2, color[2]), tail_pts)

    # Eye
    pygame.draw.circle(s, WHITE, (cx + size // 5, cy - size // 10 + wobble), max(2, size // 8))
    pygame.draw.circle(s, DARK, (cx + size // 5 + 1, cy - size // 10 + wobble), max(1, size // 14))

    surf.blit(s, (x - size, y - size))


def draw_dog(surf, x, y, size, frame):
    """Draw a simple dog obstacle."""
    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx, cy = size, size
    col = (160, 100, 60)
    dark = (100, 60, 30)

    # Body
    pygame.draw.circle(s, col, (cx, cy), int(size * 0.5))
    # Head
    hx, hy = cx + int(size * 0.35), cy - int(size * 0.2)
    pygame.draw.circle(s, col, (hx, hy), int(size * 0.35))
    # Ears
    pygame.draw.ellipse(s, dark, (hx - size // 2, hy - size // 3, size // 4, size // 3))
    pygame.draw.ellipse(s, dark, (hx + size // 5, hy - size // 3, size // 4, size // 3))
    # Eyes
    pygame.draw.circle(s, WHITE, (hx - 3, hy - 2), max(2, size // 8))
    pygame.draw.circle(s, RED, (hx - 3, hy - 2), max(1, size // 14))
    # Nose
    pygame.draw.circle(s, DARK, (hx + int(size * 0.2), hy + 2), max(2, size // 10))
    # Tail wag
    ta = math.sin(frame * 0.2) * 0.6
    tx = cx - int(size * 0.5)
    ty = cy
    pygame.draw.line(s, dark, (tx, ty), (tx - int(math.cos(ta) * size * 0.4), ty - int(math.sin(ta + 1) * size * 0.4)), 3)

    surf.blit(s, (x - size, y - size))


def draw_catnip(surf, x, y, size, frame):
    """Draw a catnip power-up (green leaf)."""
    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx, cy = size, size
    pulse = 0.8 + 0.2 * math.sin(frame * 0.1)
    r = int(size * 0.4 * pulse)
    pygame.draw.circle(s, GREEN, (cx, cy), r)
    pygame.draw.circle(s, (120, 255, 160), (cx - 2, cy - 2), r // 2)
    # Sparkle
    for i in range(4):
        a = frame * 0.05 + i * math.pi / 2
        sx = cx + int(math.cos(a) * r * 1.4)
        sy = cy + int(math.sin(a) * r * 1.4)
        pygame.draw.circle(s, (200, 255, 200, 180), (sx, sy), 2)
    surf.blit(s, (x - size, y - size))


class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.randint(15, 35)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1

    def draw(self, surf):
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surf.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


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


# ─── Main Game ───

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🐱 Kitty Fish Rush!")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("Segoe UI", 52, bold=True)
    font_med = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_sm = pygame.font.SysFont("Segoe UI", 20)

    stars = [Star() for _ in range(60)]

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
    high_score = 0
    level = 1
    frame = 0
    fish_eaten = 0

    def reset_game():
        nonlocal cat, fishes, dogs, catnips, particles, score, level, fish_eaten, frame
        cat = Cat()
        fishes = [Fish() for _ in range(3)]
        dogs = [Dog()]
        catnips = []
        particles = []
        score = 0
        level = 1
        fish_eaten = 0
        frame = 0

    def spawn_particles(x, y, color, count=12):
        for _ in range(count):
            particles.append(Particle(x, y, color))

    def draw_hud(surf):
        # Top panel
        panel = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
        panel.fill((15, 15, 40, 180))
        surf.blit(panel, (0, 0))

        # Score
        txt = font_med.render(f"Score: {score}", True, GOLD)
        surf.blit(txt, (20, 15))

        # Level
        txt = font_sm.render(f"Level {level}", True, WHITE)
        surf.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 20))

        # Lives (hearts)
        for i in range(cat.lives):
            hx = WIDTH - 40 - i * 35
            pygame.draw.polygon(surf, RED, [
                (hx, 28), (hx - 8, 18), (hx - 12, 22), (hx - 10, 32),
                (hx, 38), (hx + 10, 32), (hx + 12, 22), (hx + 8, 18)
            ])

        # Boost indicator
        if cat.boosted:
            txt = font_sm.render("⚡ CATNIP BOOST!", True, GREEN)
            surf.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 42))

        # High score
        txt = font_sm.render(f"Best: {high_score}", True, (150, 150, 180))
        surf.blit(txt, (200, 20))

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

        # ─── DRAW BACKGROUND ───
        screen.blit(BG_SURFACE, (0, 0))
        for star in stars:
            star.draw(screen, t)

        # ─── MENU STATE ───
        if state == STATE_MENU:
            # Title
            title = font_big.render("Kitty Fish Rush!", True, GOLD)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 160))

            # Animated cat preview
            draw_cat(screen, WIDTH // 2 - 80, 320, 40, math.sin(t) * 0.5, frame, False)
            draw_fish(screen, WIDTH // 2 + 80, 320, 30, frame, CYAN)

            # Instructions
            lines = [
                "Arrow Keys / A-D : Steer the cat",
                "Eat fish to score points!",
                "Avoid dogs - they bite!",
                "Grab green catnip for speed boost!",
                "",
                "Press SPACE to start"
            ]
            for i, line in enumerate(lines):
                col = WHITE if i < 4 else GREEN
                txt = font_sm.render(line, True, col)
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 400 + i * 30))

        # ─── PLAY STATE ───
        elif state == STATE_PLAY:
            keys = pygame.key.get_pressed()
            cat.update(keys)

            # Dogs
            for dog in dogs:
                dog.update()
                dog.draw(screen, frame)
                # Collision with cat
                dist = math.hypot(cat.x - dog.x, cat.y - dog.y)
                if dist < cat.size + dog.size - 8 and cat.invincible <= 0:
                    cat.lives -= 1
                    cat.invincible = 90
                    spawn_particles(cat.x, cat.y, RED, 20)
                    if cat.lives <= 0:
                        high_score = max(high_score, score)
                        state = STATE_OVER

            # Fish
            for fish in fishes:
                fish.draw(screen, frame)
                dist = math.hypot(cat.x - fish.x, cat.y - fish.y)
                if dist < cat.size + fish.size:
                    score += 10 * level
                    fish_eaten += 1
                    spawn_particles(fish.x, fish.y, fish.color, 15)
                    fish.respawn()

                    # Level up every 5 fish
                    if fish_eaten % 5 == 0:
                        level += 1
                        cat.speed = cat.base_speed + level * 0.3
                        if len(dogs) < 3 + level:
                            dogs.append(Dog())
                        if len(fishes) < 5 + level // 2:
                            fishes.append(Fish())

            # Catnip spawning
            if random.random() < 0.003 and len(catnips) < 2:
                catnips.append(Catnip())

            for cn in catnips:
                cn.update()
                cn.draw(screen, frame)
                dist = math.hypot(cat.x - cn.x, cat.y - cn.y)
                if dist < cat.size + cn.size and cn.active:
                    cat.boost_timer = 300
                    cn.active = False
                    spawn_particles(cn.x, cn.y, GREEN, 20)
                    score += 25

            catnips = [c for c in catnips if c.active]

            # Particles
            for p in particles:
                p.update()
                p.draw(screen)
            particles = [p for p in particles if p.life > 0]

            # Cat trail particles when boosted
            if cat.boosted and frame % 3 == 0:
                particles.append(Particle(cat.x, cat.y, (100, 255, 100)))

            cat.draw(screen, frame)
            draw_hud(screen)

        # ─── GAME OVER STATE ───
        elif state == STATE_OVER:
            # Dim overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            txt = font_big.render("Game Over!", True, RED)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 180))

            txt = font_med.render(f"Score: {score}", True, GOLD)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 270))

            txt = font_med.render(f"High Score: {high_score}", True, WHITE)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 320))

            txt = font_med.render(f"Level Reached: {level}", True, CYAN)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 370))

            txt = font_sm.render("Press SPACE for menu  |  ESC to quit", True, (180, 180, 200))
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 450))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
