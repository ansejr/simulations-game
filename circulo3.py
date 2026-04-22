import pygame
import pygame_gui
import os
import math
import random

pygame.init()

# Tela
WIDTH, HEIGHT = 1400, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Círculos de Für Elise")

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Botão Reset
reset_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - 120, 20), (100, 40)),
    text="Resetar",
    manager=manager
)

# Label contador
counter_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 20), (300, 40)),
    text="Criadas: 0 | Explodidas: 0",
    manager=manager
)

# Gravidade
GRAVITY = 0.5

# Sons
sound_folder = "sounds/fur_elise_intro"
notes = []
for i in range(1, 1000):
    path = os.path.join(sound_folder, f"fur{i}.wav")
    if os.path.exists(path):
        notes.append(pygame.mixer.Sound(path))

note_index = 0
balls_created = 0
balls_exploded = 0


class OuterCircle:
    def __init__(self):
        self.center = (WIDTH // 2, HEIGHT // 2)
        self.radius = min(WIDTH, HEIGHT) // 2 - 10
        self.width = 2

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255), self.center, self.radius, self.width)

    def inside(self, x, y):
        dx = x - self.center[0]
        dy = y - self.center[1]
        return math.hypot(dx, dy) < self.radius


class ExplosionParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = random.randint(15, 30)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, (255, 200, 0), (int(self.x), int(self.y)), 2)


class InnerCircle:
    def __init__(self, x, y, radius=2):
        self.x, self.y = x, y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.radius = radius
        self.active = True
        self.exploding = False
        self.particles = []

    def update(self, outer_circle, others):
        global note_index, balls_exploded
        if self.exploding:
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]
            return

        if not self.active:
            return

        # Movimento com gravidade
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        exploded = False

        # Colisão com o círculo externo
        dx = self.x - outer_circle.center[0]
        dy = self.y - outer_circle.center[1]
        dist = math.hypot(dx, dy)
        if dist + self.radius >= outer_circle.radius:
            nx, ny = dx / dist, dy / dist
            dot = self.vx * nx + self.vy * ny
            self.vx -= 2 * dot * nx
            self.vy -= 2 * dot * ny
            self.vx *= 1.05
            self.vy *= 1.05
            self.vx += random.uniform(-0.5, 0.5)
            self.vy += random.uniform(-0.5, 0.5)
            overlap = dist + self.radius - outer_circle.radius
            self.x -= nx * overlap
            self.y -= ny * overlap
            self.radius += 1
            if notes:
                notes[note_index % len(notes)].play()
                note_index += 1
            if self.radius >= outer_circle.radius - 2:
                exploded = True

        # Colisão com outras bolas
        for other in others:
            if other == self or other.exploding:
                continue
            dx = other.x - self.x
            dy = other.y - self.y
            d = math.hypot(dx, dy)
            if d < self.radius + other.radius:
                # Reflexão simples
                nx, ny = dx / d, dy / d
                dot = (self.vx - other.vx) * nx + (self.vy - other.vy) * ny
                self.vx -= dot * nx
                self.vy -= dot * ny
                other.vx += dot * nx
                other.vy += dot * ny
                self.radius += 1
                if notes:
                    notes[note_index % len(notes)].play()
                    note_index += 1
                # Se está muito apertada → explode
                if self.radius + other.radius >= d:
                    exploded = True

        if exploded:
            self.active = False
            self.exploding = True
            for _ in range(40):
                self.particles.append(ExplosionParticle(self.x, self.y))
            balls_exploded += 1

    def draw(self, surface):
        if self.exploding:
            for p in self.particles:
                p.draw(surface)
        else:
            pygame.draw.circle(surface, (0, 255, 0), (int(self.x), int(self.y)), self.radius, 2)


def main():
    global balls_created, balls_exploded, note_index
    clock = pygame.time.Clock()
    running = True
    outer = OuterCircle()
    circles = []

    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == reset_button:
                        circles.clear()
                        balls_created = 0
                        balls_exploded = 0
                        note_index = 0
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if outer.inside(mx, my):
                    # Checar se clique está fora de todas as bolas
                    inside_any = False
                    for c in circles:
                        if not c.exploding and math.hypot(mx - c.x, my - c.y) <= c.radius:
                            inside_any = True
                            break
                    if not inside_any:
                        circles.append(InnerCircle(mx, my))
                        balls_created += 1
            manager.process_events(event)

        manager.update(time_delta)
        window.fill((0, 0, 0))
        outer.draw(window)

        # Atualizar bolas
        to_remove = []
        for c in circles:
            c.update(outer, circles)
            c.draw(window)
            if c.exploding and not c.particles:
                to_remove.append(c)

        for c in to_remove:
            circles.remove(c)

        # Atualizar label contador
        counter_label.set_text(f"Criadas: {balls_created} | Explodidas: {balls_exploded}")

        manager.draw_ui(window)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
