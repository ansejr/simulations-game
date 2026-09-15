import cmath
import math

import pygame
import pygame_gui


PANEL_WIDTH = 250
MIN_WINDOW_SIZE = (900, 600)
WINDOW_SIZE = (1200, 760)
BACKGROUND = (0, 0, 0)
AXIS_COLOR = (145, 145, 145)
DRAW_COLOR = (255, 255, 255)
RECONSTRUCTION_COLOR = (255, 230, 120)


def canvas_center(size):
    return PANEL_WIDTH + (size[0] - PANEL_WIDTH) / 2, size[1] / 2


def points_to_coefficients(points):
    """Converte pontos complexos em coeficientes da DFT, ordenados por amplitude."""
    sample_count = len(points)
    coefficients = []

    for index in range(sample_count):
        frequency = index if index <= sample_count // 2 else index - sample_count
        coefficient = sum(
            point * cmath.exp(-2j * math.pi * frequency * sample_index / sample_count)
            for sample_index, point in enumerate(points)
        ) / sample_count
        coefficients.append((frequency, abs(coefficient), cmath.phase(coefficient), coefficient))

    coefficients.sort(key=lambda item: item[1], reverse=True)
    return coefficients


def make_color(index):
    color = pygame.Color(0)
    color.hsva = ((index * 137.5) % 360, 88, 96, 100)
    return color


def complex_to_screen(value, center):
    return int(center[0] + value.real), int(center[1] - value.imag)


def draw_axes(surface, center):
    pygame.draw.line(surface, AXIS_COLOR, (PANEL_WIDTH, int(center[1])), (surface.get_width(), int(center[1])), 1)
    pygame.draw.line(surface, AXIS_COLOR, (int(center[0]), 0), (int(center[0]), surface.get_height()), 1)


def draw_fourier(surface, coefficients, time, center, trail_points):
    current = 0j
    previous_screen = complex_to_screen(current, center)

    for index, (frequency, radius, phase, _) in enumerate(coefficients):
        previous = current
        current += radius * cmath.exp(1j * (2 * math.pi * frequency * time + phase))
        previous_screen = complex_to_screen(previous, center)
        current_screen = complex_to_screen(current, center)
        color = make_color(index)

        if radius >= 1:
            pygame.draw.circle(surface, color, previous_screen, max(1, int(radius)), 1)
        pygame.draw.line(surface, color, previous_screen, current_screen, 2)

    endpoint = complex_to_screen(current, center)
    if not trail_points or math.dist(endpoint, trail_points[-1]) > 1:
        trail_points.append(endpoint)
    return endpoint


pygame.init()
pygame.display.set_caption("Desenho por Transformada de Fourier")
window_surface = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
clock = pygame.time.Clock()
manager = pygame_gui.UIManager(WINDOW_SIZE)

main_panel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(0, 0, PANEL_WIDTH, WINDOW_SIZE[1]),
    manager=manager,
)

title_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(18, 18, 210, 32),
    text="Transformada de Fourier",
    manager=manager,
    container=main_panel,
)
play_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(18, 62, 98, 34),
    text="Play",
    manager=manager,
    container=main_panel,
)
clear_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(126, 62, 98, 34),
    text="Limpar",
    manager=manager,
    container=main_panel,
)
slower_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(18, 108, 98, 34),
    text="- Velocidade",
    manager=manager,
    container=main_panel,
)
faster_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(126, 108, 98, 34),
    text="+ Velocidade",
    manager=manager,
    container=main_panel,
)
speed_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(18, 151, 206, 28),
    text="Velocidade: 1.0x",
    manager=manager,
    container=main_panel,
)
repeat_checkbox = pygame_gui.elements.UICheckBox(
    relative_rect=pygame.Rect(18, 190, 206, 32),
    text="Repetir ao finalizar",
    manager=manager,
    container=main_panel,
)
status_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(18, 236, 206, 70),
    text="Desenhe no canvas branco.",
    manager=manager,
    container=main_panel,
)

input_points = []
coefficients = []
reconstruction_trail = []
is_drawing = False
is_playing = False
animation_time = 0.0
speed = 1.0

running = True
while running:
    dt = clock.tick(60) / 1000.0
    window_size = window_surface.get_size()
    center = canvas_center(window_size)

    for event in pygame.event.get():
        manager.process_events(event)

        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            new_size = (max(MIN_WINDOW_SIZE[0], event.w), max(MIN_WINDOW_SIZE[1], event.h))
            window_surface = pygame.display.set_mode(new_size, pygame.RESIZABLE)
            manager.set_window_resolution(new_size)
            main_panel.set_dimensions((PANEL_WIDTH, new_size[1]))
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == play_button:
                if coefficients:
                    is_playing = not is_playing
                    play_button.set_text("Pausa" if is_playing else "Play")
            elif event.ui_element == clear_button:
                input_points.clear()
                coefficients.clear()
                reconstruction_trail.clear()
                animation_time = 0.0
                is_playing = False
                play_button.set_text("Play")
                status_label.set_text("Desenhe no canvas branco.")
            elif event.ui_element == slower_button:
                speed = max(0.125, speed / 2)
                speed_label.set_text(f"Velocidade: {speed:g}x")
            elif event.ui_element == faster_button:
                speed = min(16.0, speed * 2)
                speed_label.set_text(f"Velocidade: {speed:g}x")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if event.pos[0] >= PANEL_WIDTH:
                is_drawing = True
                is_playing = False
                play_button.set_text("Play")
                input_points.clear()
                coefficients.clear()
                reconstruction_trail.clear()
                animation_time = 0.0
                input_points.append(complex(event.pos[0] - center[0], center[1] - event.pos[1]))
        elif event.type == pygame.MOUSEMOTION and is_drawing:
            if event.pos[0] >= PANEL_WIDTH:
                point = complex(event.pos[0] - center[0], center[1] - event.pos[1])
                if not input_points or abs(point - input_points[-1]) >= 2:
                    input_points.append(point)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and is_drawing:
            is_drawing = False
            if len(input_points) >= 8:
                coefficients = points_to_coefficients(input_points)
                reconstruction_trail.clear()
                animation_time = 0.0
                status_label.set_text(f"{len(input_points)} pontos, {len(coefficients)} vetores.")
            else:
                input_points.clear()
                status_label.set_text("Desenho muito curto.")

    if is_playing and coefficients:
        animation_time += dt * speed
        if animation_time >= 1.0:
            if repeat_checkbox.get_state():
                animation_time %= 1.0
                reconstruction_trail.clear()
            else:
                animation_time = 1.0
                is_playing = False
                play_button.set_text("Play")

    window_surface.fill(BACKGROUND)
    center = canvas_center(window_surface.get_size())
    draw_axes(window_surface, center)

    if len(input_points) > 1:
        original_points = [complex_to_screen(point, center) for point in input_points]
        pygame.draw.lines(window_surface, DRAW_COLOR, False, original_points, 2)

    if coefficients:
        draw_fourier(window_surface, coefficients, animation_time, center, reconstruction_trail)
        if len(reconstruction_trail) > 1:
            pygame.draw.lines(window_surface, RECONSTRUCTION_COLOR, False, reconstruction_trail, 2)

    manager.update(dt)
    manager.draw_ui(window_surface)
    pygame.display.flip()

pygame.quit()
