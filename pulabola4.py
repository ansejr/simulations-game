import pygame
import pygame_gui
import random
import os

class ExplosionParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-200, 200)
        self.vy = random.uniform(-200, 200)
        self.life = 0.5
        self.color = color
        self.radius = random.randint(2, 4)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            alpha = max(0, int(255 * (self.life / 0.5)))
            surface_color = (*self.color, alpha)
            surface_particle = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surface_particle, surface_color, (self.radius, self.radius), self.radius)
            surface.blit(surface_particle, (self.x - self.radius, self.y - self.radius))

    def is_alive(self):
        return self.life > 0

pygame.init()

WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulação de Bolas com Gravidade e Elasticidade")

manager = pygame_gui.UIManager((WIDTH, HEIGHT))
clock = pygame.time.Clock()

GROUND_HEIGHT = 60
GROUND_Y = HEIGHT - GROUND_HEIGHT

balls = []
explosions = []
eliminated_balls = []
numerobola = 0

BACKGROUND_COLOR = (30, 30, 30)
GROUND_COLOR = (100, 100, 100)

# Sons
ode_sounds = []
for i in range(15):
    path = os.path.join("sounds\\joy", f"ode_note_{i}.wav")
    if os.path.exists(path):
        ode_sounds.append(pygame.mixer.Sound(path))
sound_index = 0

font = pygame.font.SysFont("Arial", 16)

# ================= UI =================
# Labels e Inputs reorganizados
pygame_gui.elements.UILabel(pygame.Rect((20, 5), (100, 20)), "Gravidade", manager)
gravity_input = pygame_gui.elements.UITextEntryLine(
    pygame.Rect((20, 25), (100, 30)), manager)
gravity_input.set_text("500")

pygame_gui.elements.UILabel(pygame.Rect((130, 5), (100, 20)), "Elasticidade", manager)
elasticity_input = pygame_gui.elements.UITextEntryLine(
    pygame.Rect((130, 25), (100, 30)), manager)
elasticity_input.set_text("0.7")

pygame_gui.elements.UILabel(pygame.Rect((240, 5), (100, 20)), "Max Quiques", manager)
max_bounces_input = pygame_gui.elements.UITextEntryLine(
    pygame.Rect((240, 25), (100, 30)), manager)
max_bounces_input.set_text("0")  # 0 = infinito

pygame_gui.elements.UILabel(pygame.Rect((350, 5), (100, 20)), "Soma Quique", manager)
adiciona_input = pygame_gui.elements.UITextEntryLine(
    pygame.Rect((350, 25), (100, 30)), manager)
adiciona_input.set_text("1")

pygame_gui.elements.UILabel(pygame.Rect((460, 5), (100, 20)), "Qtd. Bolas", manager)
num_balls_input = pygame_gui.elements.UITextEntryLine(
    pygame.Rect((460, 25), (100, 30)), manager)
num_balls_input.set_text("1")

add_button = pygame_gui.elements.UIButton(
    pygame.Rect((570, 25), (130, 30)), "Adicionar Bolas", manager)

clear_button = pygame_gui.elements.UIButton(
    pygame.Rect((710, 25), (150, 30)), "Remover Todas", manager)
# ======================================

def intdef(value, default_value=0):
    try:
        return int(value)
    except ValueError:
        return default_value

class Ball:
    def __init__(self, x, y, radius, color, gravity, elasticity, numero, max_bounces):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = random.uniform(-100, 100)
        self.vy = random.uniform(-200, 0)
        self.gravity = gravity
        self.elasticity = elasticity
        self.bounce_count = 0
        self.numero = numero
        self.max_bounces = max_bounces
        self.on_ground = False

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Colisão com o chão
        if self.y + self.radius >= GROUND_Y:
            prev_vy = self.vy
            self.y = GROUND_Y - self.radius
            self.vy *= -self.elasticity

            # Só conta se for um "quique real"
            if abs(prev_vy) > 50:
                self.bounce_count += intdef(adiciona_input.get_text())
                self.play_bounce_sound()

            self.on_ground = True
        else:
            self.on_ground = False

        # Teto
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy *= -self.elasticity

        # Laterais
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx *= -self.elasticity
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -self.elasticity

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        text = font.render(str(self.bounce_count), True, (255, 255, 255))
        n = font.render(str(self.numero), True, (255, 255, 255))
        surface.blit(text, (self.x - text.get_width() // 2, self.y - self.radius - 20))
        surface.blit(n, (self.x - n.get_width() // 2, self.y - self.radius + 10))

    def play_bounce_sound(self):
        global sound_index
        if ode_sounds:
            ode_sounds[sound_index % len(ode_sounds)].play()
            sound_index += 1

    def is_clicked(self, pos):
        return (self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2 <= self.radius ** 2

def handle_ball_collisions():
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            a, b = balls[i], balls[j]
            dx = b.x - a.x
            dy = b.y - a.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < a.radius + b.radius and dist > 0:
                overlap = 0.5 * (a.radius + b.radius - dist)
                nx, ny = dx / dist, dy / dist

                a.x -= overlap * nx
                a.y -= overlap * ny
                b.x += overlap * nx
                b.y += overlap * ny

                tx, ty = -ny, nx
                dpTanA = a.vx * tx + a.vy * ty
                dpTanB = b.vx * tx + b.vy * ty

                dpNormA = a.vx * nx + a.vy * ny
                dpNormB = b.vx * nx + b.vy * ny

                m1 = dpNormB
                m2 = dpNormA

                a.vx = tx * dpTanA + nx * m1
                a.vy = ty * dpTanA + ny * m1
                b.vx = tx * dpTanB + nx * m2
                b.vy = ty * dpTanB + ny * m2

# Configurações do painel de eliminados
PANEL_WIDTH = 100
PANEL_HEIGHT = 600
PANEL_X = 0
PANEL_Y = 80
ITEM_HEIGHT = 40
MAX_VISIBLE_ITEMS = PANEL_HEIGHT // ITEM_HEIGHT
scroll_position = 0

running = True
while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # Verifica se o clique foi no painel de eliminados para rolagem
            if PANEL_X <= pos[0] <= PANEL_X + PANEL_WIDTH and PANEL_Y <= pos[1] <= PANEL_Y + PANEL_HEIGHT:
                if event.button == 4:  # Roda do mouse para cima
                    scroll_position = max(0, scroll_position - 1)
                elif event.button == 5:  # Roda do mouse para baixo
                    scroll_position = min(len(eliminated_balls) - MAX_VISIBLE_ITEMS, scroll_position + 1)
            else:
                for ball in balls[:]:
                    if ball.is_clicked(pos):
                        speed_multiplier = 200
                        direction = (ball.vx, ball.vy)
                        ball.vx += direction[0] * (speed_multiplier - 1)
                        ball.vy += direction[1] * (speed_multiplier - 1)
                        for _ in range(20):
                            explosions.append(ExplosionParticle(ball.x, ball.y, ball.color))

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == add_button:
                try:
                    g = float(gravity_input.get_text())
                    e = float(elasticity_input.get_text())
                    mb = intdef(max_bounces_input.get_text())
                    
                    # Lê, limita (clamp) entre 1 e 1000, e atualiza o texto na interface
                    qtd = intdef(num_balls_input.get_text(), 1)
                    qtd = max(1, min(1000, qtd))
                    num_balls_input.set_text(str(qtd))
                    
                    for _ in range(qtd):
                        color = [random.randint(50, 255) for _ in range(3)]
                        numerobola += 1
                        new_ball = Ball(random.randint(200, WIDTH - 50), 100, 20, color, g, e, numerobola, mb)
                        balls.append(new_ball)
                except ValueError:
                    pass
            elif event.ui_element == clear_button:
                balls.clear()
                eliminated_balls.clear()
                numerobola = 0
                scroll_position = 0

        manager.process_events(event)

    for ball in balls[:]:
        ball.update(time_delta)

        # Verifica eliminação por rebatidas
        if ball.max_bounces > 0 and ball.bounce_count >= ball.max_bounces:
            eliminated_balls.append((ball.numero, ball.color))
            for _ in range(30):
                explosions.append(ExplosionParticle(ball.x, ball.y, ball.color))
            balls.remove(ball)
            # Ajusta a posição de scroll se necessário
            if len(eliminated_balls) > MAX_VISIBLE_ITEMS:
                scroll_position = len(eliminated_balls) - MAX_VISIBLE_ITEMS

    handle_ball_collisions()
    for particle in explosions[:]:
        particle.update(time_delta)
        if not particle.is_alive():
            explosions.remove(particle)

    manager.update(time_delta)

    # Desenha fundo e chão
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, GROUND_HEIGHT))

    # Painel de eliminados
    pygame.draw.rect(screen, (50, 50, 50), (PANEL_X, PANEL_Y, PANEL_WIDTH, PANEL_HEIGHT))
    
    # Área de conteúdo com clipping
    content_area = pygame.Rect(PANEL_X, PANEL_Y, PANEL_WIDTH, PANEL_HEIGHT)
    old_clip = screen.get_clip()
    screen.set_clip(content_area)
    
    # Desenha apenas os itens visíveis
    start_idx = scroll_position
    end_idx = min(start_idx + MAX_VISIBLE_ITEMS, len(eliminated_balls))
    
    for idx in range(start_idx, end_idx):
        num, color = eliminated_balls[idx]
        y_pos = PANEL_Y + (idx - start_idx) * ITEM_HEIGHT
        pygame.draw.circle(screen, color, (PANEL_X + 40, y_pos + 20), 10)
        rank_text = font.render(f"{idx+1}º", True, (255, 255, 255))
        num_text = font.render(str(num), True, (255, 255, 255))
        screen.blit(rank_text, (PANEL_X + 5, y_pos + 12))
        screen.blit(num_text, (PANEL_X + 55, y_pos + 12))
    
    screen.set_clip(old_clip)
    
    # Barra de scroll se necessário
    if len(eliminated_balls) > MAX_VISIBLE_ITEMS:
        scrollbar_height = PANEL_HEIGHT * (MAX_VISIBLE_ITEMS / len(eliminated_balls))
        scrollbar_pos = PANEL_HEIGHT * (scroll_position / len(eliminated_balls))
        pygame.draw.rect(screen, (100, 100, 100), 
                        (PANEL_X + PANEL_WIDTH - 5, PANEL_Y + scrollbar_pos, 5, scrollbar_height))

    # Bolas
    for ball in balls:
        ball.draw(screen)

    # Partículas
    for particle in explosions:
        particle.draw(screen)

    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()