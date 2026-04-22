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

# Gravidade
GRAVITY = 0.5

# Sons das notas (assumindo que fur1.wav, fur2.wav... estão em "fur_elise_intro_wav")
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
        self.radius = min(WIDTH, HEIGHT) // 2 - 10  # margem
        self.width = 2

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255), self.center, self.radius, self.width)


class InnerCircle:
    def __init__(self, parent=None, radius=2):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        # velocidade inicial aleatória
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.radius = radius
        self.active = True
        self.parent = parent

    def update(self, outer_circle):
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
            # Normal da colisão
            nx, ny = dx / dist, dy / dist
            dot = self.vx * nx + self.vy * ny
            # Reflexão
            self.vx -= 2 * dot * nx
            self.vy -= 2 * dot * ny

            # Aumenta velocidade
            self.vx *= 1.01
            self.vy *= 1.01

            # Adiciona ruído aleatório
            self.vx += random.uniform(-0.5, 0.5)
            self.vy += random.uniform(-0.5, 0.5)

            # Corrige sobreposição
            overlap = dist + self.radius - outer_circle.radius
            self.x -= nx * overlap
            self.y -= ny * overlap

            # Cresce a cada batida
            self.radius += 2

            # Toca próxima nota
            global note_index
            if notes:
                notes[note_index % len(notes)].play()
                note_index += 1

            # Chegou no tamanho máximo
            if self.radius >= outer_circle.radius - 2:
                self.active = False
                return "new"

        return None

    def draw(self, surface):
        pygame.draw.circle(surface, (0, 255, 0), (int(self.x), int(self.y)), self.radius, 2)


def main():
    clock = pygame.time.Clock()
    running = True

    outer = OuterCircle()
    circles = [InnerCircle()]

    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)

        manager.update(time_delta)
        window.fill((0, 0, 0))

        # Desenhar círculo externo
        outer.draw(window)

        # Atualizar círculos
        for circle in circles:
            result = circle.update(outer)
            circle.draw(window)
            if result == "new":
                circles.append(InnerCircle(parent=circle))

        manager.draw_ui(window)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
