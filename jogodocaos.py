import pygame
import pygame_gui
import random
import math

# Configurações da tela
WIDTH, HEIGHT = 1400, 800
pygame.init()
pygame.display.set_caption("Jogo do Caos - Fractal de Sierpinski")
window_surface = pygame.display.set_mode((WIDTH, HEIGHT))

# Gerenciador da interface
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Slider para pontos por segundo
slider_rect = pygame.Rect(50, HEIGHT - 80, 400, 30)
slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=slider_rect,
    start_value=100,
    value_range=(0, 9999999),
    manager=manager
)

# Rótulo
slider_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(50, HEIGHT - 110, 400, 25),
    text="Pontos por segundo: 100",
    manager=manager
)

# Botão reset
reset_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(500, HEIGHT - 90, 100, 40),
    text="Resetar",
    manager=manager
)

# Triângulo equilátero (quase altura inteira)
margin = 50
side = HEIGHT - 2 * margin
h = side * (math.sqrt(3) / 2)

v1 = (WIDTH // 2, margin)  # topo
v2 = (WIDTH // 2 - side // 2, margin + h)  # canto esquerdo
v3 = (WIDTH // 2 + side // 2, margin + h)  # canto direito
vertices = [v1, v2, v3]

# Estado do caos game
def reset_points():
    global current_point, points
    current_point = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
    points = []

reset_points()

# Transformação para zoom/pan
scale = 1.0
offset_x, offset_y = 0.0, 0.0

def world_to_screen(x, y):
    return int((x + offset_x) * scale), int((y + offset_y) * scale)

def screen_to_world(x, y):
    return (x / scale - offset_x), (y / scale - offset_y)

# Controle de arrastar
dragging = False
last_mouse_pos = (0, 0)

clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Scroll para zoom
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            wx, wy = screen_to_world(mx, my)  # ponto do mundo sob o mouse
            if event.y > 0:  # zoom in
                scale *= 1.1
            elif event.y < 0:  # zoom out
                scale /= 1.1
            # Ajustar offset para manter (wx, wy) fixo na tela
            offset_x = mx / scale - wx
            offset_y = my / scale - wy

        # Início do drag
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # botão esquerdo
                dragging = True
                last_mouse_pos = pygame.mouse.get_pos()

        # Fim do drag
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        # Arrastar
        elif event.type == pygame.MOUSEMOTION and dragging:
            mx, my = event.pos
            dx = (mx - last_mouse_pos[0]) / scale
            dy = (my - last_mouse_pos[1]) / scale
            offset_x += dx
            offset_y += dy
            last_mouse_pos = (mx, my)

        # Botão reset
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == reset_button:
                reset_points()

        manager.process_events(event)

    manager.update(time_delta)

    # Atualizar texto do slider
    pps = int(slider.get_current_value())
    slider_label.set_text(f"Pontos por segundo: {pps}")

    # Gerar pontos
    if pps > 0:
        for _ in range(max(1, pps // 60)):
            chosen_vertex = random.choice(vertices)
            current_point = (
                (current_point[0] + chosen_vertex[0]) / 2,
                (current_point[1] + chosen_vertex[1]) / 2
            )
            points.append(current_point)

    # Renderização
    window_surface.fill((0, 0, 0))

    # Desenhar vértices
    for v in vertices:
        sx, sy = world_to_screen(*v)
        pygame.draw.circle(window_surface, (255, 0, 0), (sx, sy), 5)

    # Desenhar pontos
    for p in points:
        sx, sy = world_to_screen(*p)
        if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
            window_surface.set_at((sx, sy), (0, 255, 0))

    manager.draw_ui(window_surface)
    pygame.display.update()

pygame.quit()
