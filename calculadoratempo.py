import pygame
import pygame_gui
from pygame.locals import *
import math

# Configuração da tela
WIDTH, HEIGHT = 1000, 600
pygame.init()
pygame.display.set_caption("Calculadora de Tempo para Contagem")
window_surface = pygame.display.set_mode((WIDTH, HEIGHT))

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Campos de input
input_number = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(50, 50, 300, 40),
    manager=manager
)
input_number.set_text("1000000")

input_interval = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(400, 50, 200, 40),
    manager=manager
)
input_interval.set_text("1")  # segundos

# Botão calcular
button_calc = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(650, 50, 120, 40),
    text="Calcular",
    manager=manager
)

# Label para resultado
result_label = pygame_gui.elements.UITextBox(
    relative_rect=pygame.Rect(50, 120, 900, 200),
    html_text="Insira um número e intervalo, depois clique em Calcular.",
    manager=manager
)

# Fonte grande para mostrar a contagem
big_font = pygame.font.SysFont("Arial", 100, bold=True)

# Estado da contagem
counting = False
current_value = 0
target_value = 0
interval = 1.0
time_accum = 0.0

clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button_calc:
                # Pegar número e intervalo
                try:
                    target_value = int(input_number.get_text())
                    interval = float(input_interval.get_text())
                    counting = True
                    current_value = 0
                    time_accum = 0.0

                    total_seconds = target_value * interval
                    days = total_seconds / 86400
                    years = days / 365
                    decades = years / 10
                    centuries = years / 100
                    millennia = years / 1000

                    result_label.set_text(
                        f"Para contar até <b>{target_value:,}</b> "
                        f"com intervalo de <b>{interval}</b> s:<br>"
                        f"- Milênios: {millennia:.2f}<br>"
                        f"- Séculos: {centuries:.2f}<br>"
                        f"- Décadas: {decades:.2f}<br>"
                        f"- Anos: {years:.2f}<br>"
                        f"- Dias: {days:.2f}"
                    )
                except ValueError:
                    result_label.set_text("Erro: insira valores válidos.")

        manager.process_events(event)

    manager.update(time_delta)

    # Atualização da contagem
    if counting:
        time_accum += time_delta
        while time_accum >= interval and current_value < target_value:
            current_value += 1
            time_accum -= interval
        if current_value >= target_value:
            counting = False

    # Renderização
    window_surface.fill((30, 30, 30))
    manager.draw_ui(window_surface)

    # Mostrar contagem em fonte grande
    if counting or current_value > 0:
        text_surface = big_font.render(str(current_value), True, (0, 255, 0))
        rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 150))
        window_surface.blit(text_surface, rect)

    pygame.display.update()

pygame.quit()
