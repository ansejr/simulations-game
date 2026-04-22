import pygame
import pygame_gui
import os
import math
import random

pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 1400, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Círculos de Für Elise")

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Botão de reset
reset_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - 120, 20), (100, 40)),
    text="Resetar",
    manager=manager
)

# Gravidade
GRAVITY = 0.5

# Sons das notas (agora em sounds/fur_elise_intro)
sound_folder = "sounds/fur_elise_intro"
notes = []
for i in range(1, 1000):  # pode ter muitas notas
    path = os.path.join(sound_folder, f"fur{i}.wav")
    if os.path.exists(path):
        notes.append(pygame.mixer.Sound(path))

note_index = 0


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

    def update(self, outer_circle):
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

        # Distância até o centro do círculo externo
        dx = self.x - outer_circle.center[0]
        dy = self.y - outer_circle.center[1]
        dist = math.hypot(dx, dy)

        # Colisão com a borda
        if dist + self.radius >= outer_circle.radius:
            nx, ny = dx / dist, dy / dist
            dot = self.vx * nx + self.vy * ny
            self.vx -= 2 * dot * nx
            self.vy -= 2 * dot * ny

            # Aumenta velocidade
            self.vx *= 1.05
            self.vy *= 1.05

            # Adiciona ruído aleatório
            self.vx += random.uniform(-0.5, 0.5)
            self.vy += random.uniform(-0.5, 0.5)

            # Corrige sobreposição
            overlap = dist + self.radius - outer_circle.radius
            self.x -= nx * overlap
            self.y -= ny * overlap

            # Cresce devagar
            self.radius += 1

            # Toca próxima nota
            global note_index
            if notes:
                notes[note_index % len(notes)].play()
                note_index += 1

            # Chegou no tamanho máximo → explode
            if self.radius >= outer_circle.radius - 2:
                self.active = False
                self.exploding = True
                for _ in range(40):
                    self.particles.append(ExplosionParticle(self.x, self.y))

    def draw(self, surface):
        if self.exploding:
            for p in self.particles:
                p.draw(surface)
        else:
            pygame.draw.circle(surface, (0, 255, 0), (int(self.x), int(self.y)), self.radius, 2)


def main():
    global note_index
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
                        note_index = 0

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                # Só cria se estiver dentro do círculo externo e fora de todas as bolas
                if outer.inside(mx, my):
                    inside_any = False
                    for c in circles:
                        if math.hypot(mx - c.x, my - c.y) <= c.radius:
                            inside_any = True
                            break
                    if not inside_any:
                        circles.append(InnerCircle(mx, my))

            manager.process_events(event)

        manager.update(time_delta)
        window.fill((0, 0, 0))

        outer.draw(window)

        # Atualizar círculos
        to_remove = []
        for circle in circles:
            circle.update(outer)
            circle.draw(window)
            if circle.exploding and not circle.particles:
                to_remove.append(circle)

        for c in to_remove:
            circles.remove(c)

        manager.draw_ui(window)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
