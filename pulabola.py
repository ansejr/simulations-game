
import pygame
import pygame_gui
import random
import math
import os

pygame.init()

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulação de Bolas com Gravidade e Elasticidade")

manager = pygame_gui.UIManager((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

GROUND_Y = HEIGHT - 50
balls = []

# UI
gravity_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((820, 20), (150, 30)), text="Gravidade", manager=manager)
gravity_input = pygame_gui.elements.UITextEntryLine(pygame.Rect((820, 50), (150, 30)), manager)
gravity_input.set_text("500")

elasticity_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((820, 90), (150, 30)), text="Elasticidade", manager=manager)
elasticity_input = pygame_gui.elements.UITextEntryLine(pygame.Rect((820, 120), (150, 30)), manager)
elasticity_input.set_text("0.7")

add_button = pygame_gui.elements.UIButton(pygame.Rect((820, 160), (150, 40)), text="Adicionar Bola", manager=manager)
clear_button = pygame_gui.elements.UIButton(pygame.Rect((820, 210), (150, 40)), text="Deletar Todas", manager=manager)

# Carrega os sons
SOUND_PATHS = [
    "sounds/note_0.wav",
    "sounds/note_1.wav",
    "sounds/note_2.wav",
    "sounds/note_3.wav",
    "sounds/note_4.wav",
]
SOUNDS = [pygame.mixer.Sound(path) for path in SOUND_PATHS]

class Ball:
    def __init__(self, x, y, radius, color, gravity, elasticity):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = random.uniform(-100, 100)
        self.vy = random.uniform(-200, 0)
        self.gravity = gravity
        self.elasticity = elasticity

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.y + self.radius >= GROUND_Y:
            self.y = GROUND_Y - self.radius
            self.vy = -self.vy * self.elasticity
            random.choice(SOUNDS).play()

        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.vx = -self.vx

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def is_clicked(self, pos):
        dx = self.x - pos[0]
        dy = self.y - pos[1]
        return math.hypot(dx, dy) <= self.radius

def handle_collisions():
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            a, b = balls[i], balls[j]
            dx = b.x - a.x
            dy = b.y - a.y
            dist = math.hypot(dx, dy)
            if dist < a.radius + b.radius:
                overlap = 0.5 * (a.radius + b.radius - dist)
                if dist == 0:
                    dx, dy = 1, 0
                    dist = 1
                nx, ny = dx / dist, dy / dist
                a.x -= overlap * nx
                a.y -= overlap * ny
                b.x += overlap * nx
                b.y += overlap * ny

                kx = a.vx - b.vx
                ky = a.vy - b.vy
                p = 2 * (nx * kx + ny * ky) / 2
                a.vx -= p * nx
                a.vy -= p * ny
                b.vx += p * nx
                b.vy += p * ny

running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            balls = [b for b in balls if not b.is_clicked(mouse_pos)]

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == add_button:
                try:
                    g = float(gravity_input.get_text())
                    e = float(elasticity_input.get_text())
                    ball = Ball(random.randint(100, 700), 100, 20, [random.randint(50, 255) for _ in range(3)], g, e)
                    balls.append(ball)
                except ValueError:
                    pass
            elif event.ui_element == clear_button:
                balls.clear()

        manager.process_events(event)

    for ball in balls:
        ball.update(dt)
    handle_collisions()

    manager.update(dt)

    screen.fill((30, 30, 30))
    pygame.draw.rect(screen, (100, 100, 100), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

    for ball in balls:
        ball.draw(screen)

    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
