import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
MIN_WIDTH, MIN_HEIGHT = 1000, 1000
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
MACHINE_COLOR = (30, 30, 30)  # Genio S Plus is often black/dark grey
RING_COLOR = (60, 60, 60)
LIGHT_GRAY = (150, 150, 150)
GREEN = (0, 255, 0)
RED_TEMP = (255, 50, 50)
ORANGE_TEMP = (255, 150, 50)
YELLOW_TEMP = (255, 220, 50)
BLUE_TEMP = (50, 150, 255)
COFFEE_COLOR = (75, 45, 25)
MILK_COLOR = (245, 245, 230)
TRANSPARENT = (0, 0, 0, 0)
SILVER = (200, 200, 210)
LED_GREEN = (0, 255, 120)
LED_DARK = (30, 60, 30)

# Set up the display
screen = pygame.display.set_mode((MIN_WIDTH, MIN_HEIGHT), pygame.RESIZABLE | pygame.FULLSCREEN)
pygame.display.set_caption("Nescafé Dolce Gusto Genio S Plus Simulator")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 48)


def draw_text_center(surface, text, font, color, center_pos):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_pos)
    surface.blit(text_surface, text_rect)

class SplashParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-6, -2)
        self.color = color
        self.life = 255
        self.size = random.uniform(2, 5)

    def update(self):
        self.vy += 0.4  # Gravidade
        self.x += self.vx
        self.y += self.vy
        self.life -= 8  # Desaparece aos poucos

    def draw(self, surface):
        if self.life > 0:
            # Superfície com suporte a transparência (Alpha)
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, max(0, int(self.life))), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class Capsule:
    def __init__(self, name, color, x, y, required_level, drink_color=COFFEE_COLOR):
        self.name = name
        self.color = color
        self.drink_color = drink_color
        self.original_x = x
        self.original_y = y
        self.rect = pygame.Rect(x - 30, y - 20, 60, 40)
        self.is_dragging = False
        self.required_level = required_level

    def draw(self, surface):
        # Draw capsule shape (top wide, bottom narrow)
        points = [
            (self.rect.left, self.rect.top),
            (self.rect.right, self.rect.top),
            (self.rect.right - 10, self.rect.bottom),
            (self.rect.left + 10, self.rect.bottom)
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
        # Draw the top lid
        pygame.draw.ellipse(surface, WHITE, (self.rect.left, self.rect.top - 5, self.rect.width, 10))
        pygame.draw.ellipse(surface, BLACK, (self.rect.left, self.rect.top - 5, self.rect.width, 10), 1)
        
        # Display required level
        draw_text_center(surface, str(self.required_level), font, BLACK, self.rect.center)
        draw_text_center(surface, self.name, pygame.font.SysFont(None, 16), BLACK, (self.rect.centerx, self.rect.bottom + 10))

    def update_pos(self, pos):
        if self.is_dragging:
            self.rect.center = pos

    def reset_pos(self):
        self.rect.center = (self.original_x, self.original_y)


class Cup:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 40, y - 60, 80, 80)
        self.is_dragging = False
        self.fill_level = 0.0 # 0.0 to 1.0 (100% full)
        self.contents = [] # List of tuples (color, amount)

    def draw(self, surface):
        # Draw contents (Liquid inside)
        if self.fill_level > 0:
            liquid_height = self.fill_level * (self.rect.height - 6)
            content_rect = pygame.Rect(self.rect.left + 3, self.rect.bottom - liquid_height - 3, 
                                       self.rect.width - 6, liquid_height)
            
            if self.contents:
                draw_color = self.contents[-1][0] # Usa a cor do topo
                pygame.draw.rect(surface, draw_color, content_rect, border_bottom_left_radius=8, border_bottom_right_radius=8)
                
                # Brilho na superfície do líquido
                pygame.draw.ellipse(surface, (min(255, draw_color[0]+30), min(255, draw_color[1]+30), min(255, draw_color[2]+30)), 
                                    (content_rect.left, content_rect.top - 3, content_rect.width, 6))

        # Handle (Alça da xícara) - Desenhada mais robusta e visível
        handle_outer_rect = pygame.Rect(self.rect.right - 10, self.rect.top + 15, 35, 50)
        pygame.draw.arc(surface, (200, 200, 210), handle_outer_rect, -math.pi/2, math.pi/2, 6)
        pygame.draw.arc(surface, (150, 150, 160), handle_outer_rect, -math.pi/2, math.pi/2, 2) # Sombra interna da alça

        # Draw glass cup (Contornos simulando vidro transparente)
        pygame.draw.rect(surface, (220, 220, 230, 180), self.rect, 3, border_radius=10) # Borda externa
        
        # Reflexo de vidro (Brilho do lado esquerdo)
        reflex_rect = pygame.Rect(self.rect.left + 6, self.rect.top + 10, 5, self.rect.height - 25)
        s = pygame.Surface((5, self.rect.height - 25), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 100), s.get_rect(), border_radius=3)
        surface.blit(s, reflex_rect.topleft)
        
        # Borda de cima (abertura da xícara)
        pygame.draw.ellipse(surface, (200, 200, 210), (self.rect.left, self.rect.top - 4, self.rect.width, 8), 2)

    def update_pos(self, pos):
        if self.is_dragging:
            self.rect.center = pos

    def empty(self):
        self.fill_level = 0.0
        self.contents = []


class CoffeeMachine:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.inserted_capsule = None
        
        # UI State
        self.volume_level = 1 # 1 to 7, plus XL (8)
        self.temperature_state = 3 # 0: Blue, 1: Yellow, 2: Orange, 3: Red
        self.temperatures = [BLUE_TEMP, YELLOW_TEMP, ORANGE_TEMP, RED_TEMP]
        self.espresso_boost = False
        
        self.is_brewing = False
        self.brew_progress = 0
        
        self.update_position(x, y)

    def update_position(self, x, y):
        self.x = x
        self.y = y
        
        # Geometry for Hitboxes and UI components
        self.capsule_slot_rect = pygame.Rect(self.x - 50, self.y + 90, 100, 45)
        self.drip_tray_rect = pygame.Rect(self.x - 70, self.y + 260, 140, 30)
        
        # Interface screen center is self.x, self.y
        self.temp_button_rect = pygame.Rect(self.x - 50, self.y - 15, 30, 30)
        self.boost_button_rect = pygame.Rect(self.x + 20, self.y - 15, 30, 30)
        self.brew_button_rect = pygame.Rect(self.x - 20, self.y + 30, 40, 30)
        
        self.trash_rect = pygame.Rect(self.x + 180, self.y - 120, 50, 50)

    def draw(self, surface):
        # Draw Machine Back (Water Tank Area)
        tank_rect = pygame.Rect(self.x - 65, self.y - 90, 130, 380)
        pygame.draw.rect(surface, (180, 180, 185), tank_rect, border_radius=40)
        pygame.draw.rect(surface, (140, 140, 145), tank_rect, 2, border_radius=40)
        
        # Draw Main Body
        body_rect = pygame.Rect(self.x - 60, self.y - 50, 120, 340)
        pygame.draw.rect(surface, MACHINE_COLOR, body_rect, border_radius=30)
        
        # Draw Capsule Drawer
        pygame.draw.rect(surface, (20, 20, 22), self.capsule_slot_rect, border_radius=15)
        pygame.draw.rect(surface, (50, 50, 55), self.capsule_slot_rect, 2, border_radius=15)
        # Drawer handle indent
        pygame.draw.rect(surface, (10, 10, 10), (self.x - 20, self.y + 115, 40, 8), border_radius=4)

        if self.inserted_capsule:
            pygame.draw.rect(surface, self.inserted_capsule.color, (self.x - 15, self.y + 95, 30, 15), border_radius=5)
            draw_text_center(surface, self.inserted_capsule.name, pygame.font.SysFont(None, 14), WHITE, (self.x, self.y + 102))
        else:
            draw_text_center(surface, "Vazio", font, WHITE, self.capsule_slot_rect.center)

        # Draw Drip Tray
        pygame.draw.rect(surface, (30, 30, 30), self.drip_tray_rect, border_radius=10)
        # Draw Metal Grid on Tray
        grid_rect = pygame.Rect(self.drip_tray_rect.left + 10, self.drip_tray_rect.top, self.drip_tray_rect.width - 20, 10)
        pygame.draw.rect(surface, SILVER, grid_rect, border_radius=3)
        for i in range(1, 10):
            line_x = grid_rect.left + (grid_rect.width / 10) * i
            pygame.draw.line(surface, (120, 120, 120), (line_x, grid_rect.top), (line_x, grid_rect.bottom), 2)

        # Draw Machine Head (Round part)
        pygame.draw.circle(surface, MACHINE_COLOR, (self.x, self.y), 110)
        pygame.draw.circle(surface, BLACK, (self.x, self.y), 110, 3)

        # -- DRAW UI INTERFACE (Genio S Plus Style) --
        
        # Silver Ring
        pygame.draw.circle(surface, SILVER, (self.x, self.y), 85)
        pygame.draw.circle(surface, (150, 150, 160), (self.x, self.y), 85, 3) # Outer border
        
        # Black Screen Panel
        pygame.draw.circle(surface, (15, 15, 15), (self.x, self.y), 65)

        # Draw Volume Bars (Vertical LEDs)
        for i in range(1, 8):
            bar_y = self.y + 15 - (i * 10)
            color = LED_GREEN if self.volume_level >= i else LED_DARK
            pygame.draw.rect(surface, color, (self.x - 8, bar_y, 16, 5), border_radius=2)
            
        # Draw XL indicator
        xl_color = LED_GREEN if self.volume_level == 8 else LED_DARK
        draw_text_center(surface, "XL", pygame.font.SysFont(None, 22, bold=True), xl_color, (self.x, self.y - 70))

        # Temperature Button (Thermometer)
        t_color = self.temperatures[self.temperature_state]
        pygame.draw.circle(surface, t_color, self.temp_button_rect.center, 12)
        # Thermometer icon lines
        pygame.draw.line(surface, WHITE, (self.temp_button_rect.centerx, self.temp_button_rect.centery - 6), 
                                         (self.temp_button_rect.centerx, self.temp_button_rect.centery + 2), 2)
        pygame.draw.circle(surface, WHITE, (self.temp_button_rect.centerx, self.temp_button_rect.centery + 4), 4)

        # Espresso Boost Button
        b_color = LED_GREEN if self.espresso_boost else (80, 80, 80)
        pygame.draw.circle(surface, (30, 30, 30), self.boost_button_rect.center, 12)
        pygame.draw.circle(surface, b_color, self.boost_button_rect.center, 12, 2)
        draw_text_center(surface, "E+", pygame.font.SysFont(None, 16, bold=True), b_color, self.boost_button_rect.center)
        
        # Brew Button (Cup Icon)
        brew_color = self.temperatures[self.temperature_state] if self.is_brewing else (WHITE if self.inserted_capsule else (100, 100, 100))
        cup_rect = pygame.Rect(self.x - 12, self.y + 35, 24, 18)
        pygame.draw.rect(surface, brew_color, cup_rect, border_radius=4)
        pygame.draw.rect(surface, brew_color, (self.x + 12, self.y + 38, 6, 10), border_radius=2) # Handle

        # Draw Trash Button
        pygame.draw.rect(surface, RED_TEMP, self.trash_rect, border_radius=8)
        draw_text_center(surface, "Lixo", font, WHITE, self.trash_rect.center)

        # Draw Spout & Pouring Coffee
        spout_rect = pygame.Rect(self.x - 10, self.capsule_slot_rect.bottom, 20, 10)
        pygame.draw.rect(surface, (10, 10, 10), spout_rect, border_radius=4)
        
        if self.is_brewing and self.inserted_capsule:
            stream_w = 6
            stream_x = self.x - stream_w // 2
            stream_y = spout_rect.bottom
            stream_h = self.drip_tray_rect.top - stream_y
            pygame.draw.rect(surface, self.inserted_capsule.drink_color, (stream_x, stream_y, stream_w, stream_h))

    def handle_click(self, pos):
        if self.temp_button_rect.collidepoint(pos) and not self.is_brewing:
            self.temperature_state = (self.temperature_state + 1) % 4
            return True
            
        if self.boost_button_rect.collidepoint(pos) and not self.is_brewing:
            self.espresso_boost = not self.espresso_boost
            return True
        
        if self.brew_button_rect.collidepoint(pos):
            if not self.is_brewing and self.inserted_capsule:
                self.is_brewing = True
                self.brew_progress = 0
            elif self.is_brewing:
                self.is_brewing = False # Manual stop
            return True
            
        if self.trash_rect.collidepoint(pos) and not self.is_brewing:
            self.inserted_capsule = None
            self.espresso_boost = False
            return True

        # Handle click on the UI Screen to adjust volume
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        dist = math.hypot(dx, dy)
        
        if dist <= 85 and not self.is_brewing:
            # Map Y position to volume level (from y-70 down to y+15)
            if -75 <= dy <= 25:
                # Calculate level 8 at top to 1 at bottom
                normalized_y = (dy + 75) / 100.0 
                level = 8 - int(normalized_y * 8)
                self.volume_level = max(1, min(8, level))
            return True
            
        return False

    def insert_capsule(self, capsule):
        if not self.is_brewing:
            self.inserted_capsule = capsule
            self.volume_level = capsule.required_level # Auto-set volume
            self.espresso_boost = False # Reset boost

    def update_brewing(self, cup, particles_list):
        if self.is_brewing:
            self.brew_progress += 1
            
            # Duration depends on volume level + Espresso Boost mode takes slightly longer
            boost_multiplier = 1.3 if self.espresso_boost else 1.0
            max_progress = int((self.volume_level * 30) * boost_multiplier)
            
            # Check if cup is underneath the spout
            cup_underneath = cup.rect.colliderect(pygame.Rect(self.x - 20, self.drip_tray_rect.top - 60, 40, 60))
            
            # Cálculo de quanto encher com base no nível selecionado (8 = ~95% da xícara)
            target_total_fill = (self.volume_level / 8.0) * 0.95 
            fill_amount_per_frame = target_total_fill / max_progress

            color = self.inserted_capsule.drink_color
            if self.espresso_boost:
                # Café fica mais forte (escuro) no modo boost
                color = (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30))

            if cup_underneath:
                # Enche a xícara
                if cup.fill_level < 1.0:
                    cup.fill_level = min(1.0, cup.fill_level + fill_amount_per_frame)
                    if self.inserted_capsule:
                        cup.contents.append((color, fill_amount_per_frame))
            else:
                # Não tem xícara! Faz a animação de espirrar (spill) na bandeja a cada 2 frames
                if self.brew_progress % 2 == 0:
                    stream_y = self.drip_tray_rect.top
                    particles_list.append(SplashParticle(self.x, stream_y, color))
                    particles_list.append(SplashParticle(self.x + random.uniform(-5, 5), stream_y, color))

            if self.brew_progress >= max_progress:
                self.is_brewing = False


def main():
    machine = CoffeeMachine(MIN_WIDTH // 2, MIN_HEIGHT // 2)
    cup = Cup(MIN_WIDTH // 2, MIN_HEIGHT // 2 + 180)
    
    # Create some capsules
    capsules = [
        Capsule("Espresso", (200, 50, 50), 100, 100, 2, (30, 15, 5)),
        Capsule("Lungo", (255, 100, 0), 200, 100, 4, (60, 30, 10)),
        Capsule("Cappuccino", (255, 255, 255), 100, 200, 6, (180, 140, 100)),
        Capsule("Chococino", (139, 69, 19), 200, 200, 5, (90, 45, 20)),
        Capsule("Cold Brew", (100, 200, 255), 100, 300, 6, (40, 20, 10))
    ]

    running = True
    dragging_obj = None
    splashes = [] # Lista para guardar as partículas de líquido espirrando

    while running:
        screen.fill(LIGHT_GRAY)
        
        # Get current window size to keep things centered if resized
        w, h = pygame.display.get_surface().get_size()
        machine.update_position(w // 2, h // 2)

        # Definir retângulo do Botão Tomar se a xícara tiver conteúdo
        tomar_rect = None
        if cup.fill_level > 0:
            tomar_rect = pygame.Rect(cup.rect.centerx - 40, cup.rect.bottom + 15, 80, 35)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEWHEEL:
                # Allow using scroll wheel to change volume if hovering near the machine head
                mouse_pos = pygame.mouse.get_pos()
                dist = math.hypot(mouse_pos[0] - machine.x, mouse_pos[1] - machine.y)
                if dist < 120 and not machine.is_brewing:
                    if event.y > 0: # Scroll up
                        machine.volume_level = min(8, machine.volume_level + 1)
                    elif event.y < 0: # Scroll down
                        machine.volume_level = max(1, machine.volume_level - 1)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    pos = event.pos
                    
                    # Checar clique no botão Tomar
                    if tomar_rect and tomar_rect.collidepoint(pos):
                        cup.empty()
                        continue

                    # Check machine UI clicks
                    if machine.handle_click(pos):
                        continue

                    # Check Cup click (verificação corrigida que permite o arraste)
                    if cup.rect.collidepoint(pos):
                        cup.is_dragging = True
                        dragging_obj = cup
                        continue
                    
                    # Check Capsule dragging
                    for cap in capsules:
                        if cap.rect.collidepoint(pos):
                            cap.is_dragging = True
                            dragging_obj = cap
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if dragging_obj:
                        dragging_obj.is_dragging = False
                        
                        # If it's a capsule, check if dropped in machine
                        if isinstance(dragging_obj, Capsule):
                            if machine.capsule_slot_rect.colliderect(dragging_obj.rect):
                                machine.insert_capsule(dragging_obj)
                            dragging_obj.reset_pos() # Always snap back to inventory
                            
                        dragging_obj = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging_obj:
                    dragging_obj.update_pos(event.pos)


        # Atualiza a máquina e passa a lista de partículas
        machine.update_brewing(cup, splashes)

        # Atualiza e limpa as partículas de respingo
        for p in splashes[:]:
            p.update()
            if p.life <= 0:
                splashes.remove(p)

        # Draw UI texts
        draw_text_center(screen, "Arraste as cápsulas para a máquina", font, BLACK, (w//2, 30))
        draw_text_center(screen, "Role a Roda do Mouse ou Clique nos LEDs para ajustar a água", font, BLACK, (w//2, 60))

        # Draw Machine
        machine.draw(screen)
        
        # Desenha as partículas de respingo na frente da máquina
        for p in splashes:
            p.draw(screen)

        # Draw Cup
        cup.draw(screen)

        # Desenha o botão Tomar se aplicável
        if tomar_rect:
            pygame.draw.rect(screen, (30, 180, 80), tomar_rect, border_radius=15)
            pygame.draw.rect(screen, (20, 120, 50), tomar_rect, 2, border_radius=15)
            draw_text_center(screen, "Tomar", font, WHITE, tomar_rect.center)

        # Draw Capsules
        for cap in capsules:
            cap.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()