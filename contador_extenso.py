import os
import pygame
import pygame_gui
import sys
import random
import math

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1400, 780
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Contador Extenso com Bolhas")
CLOCK = pygame.time.Clock()
UI_MANAGER = pygame_gui.UIManager((WIDTH, HEIGHT))

FONT_LARGE = pygame.font.SysFont("Segoe UI", 56, bold=True)
FONT_MEDIUM = pygame.font.SysFont("Segoe UI", 26)
FONT_SMALL = pygame.font.SysFont("Segoe UI", 20)
FONT_BUBBLE = pygame.font.SysFont("Segoe UI", 22, bold=True)

BG_COLOR = (18, 22, 38)
CARD_COLOR = (26, 33, 61)
LINE_COLOR = (120, 175, 255)
TEXT_COLOR = (230, 230, 240)
BUBBLE_COLOR = (76, 137, 255)
BUBBLE_POP_COLOR = (255, 120, 120)
INPUT_BG = (34, 44, 73)

START_FIELD = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 70), (200, 40)),
    manager=UI_MANAGER,
)
START_FIELD.set_text("0")

LABEL_START = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((50, 30), (200, 30)),
    text="Número inicial:",
    manager=UI_MANAGER,
)

TARGET_FIELD = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((280, 70), (200, 40)),
    manager=UI_MANAGER,
)
TARGET_FIELD.set_text("5000")

LABEL_TARGET = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((280, 30), (200, 30)),
    text="Número destino:",
    manager=UI_MANAGER,
)

SLIDER_LABEL = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((510, 30), (240, 30)),
    text="Intervalo: 0.5 s",
    manager=UI_MANAGER,
)

SPEED_SLIDER = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((510, 70), (320, 40)),
    start_value=500,
    value_range=(0.01, 2000),
    manager=UI_MANAGER,
)

BUTTON_PLAY = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((860, 70), (120, 40)),
    text="Play",
    manager=UI_MANAGER,
)
BUTTON_PAUSE = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((1000, 70), (120, 40)),
    text="Pausa",
    manager=UI_MANAGER,
)
BUTTON_RESET = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((1140, 70), (120, 40)),
    text="Reset",
    manager=UI_MANAGER,
)

INFO_LABEL = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((50, 240), (1290, 30)),
    text="Digite um início e um destino e clique em Play para contar. Use Pause para pausar.",
    manager=UI_MANAGER,
)


def numero_para_bubbles(valor: int):
    if valor == 0:
        return ["Zero"]

    def unid_text(n):
        return [
            "zero", "um", "dois", "três", "quatro", "cinco",
            "seis", "sete", "oito", "nove", "dez", "onze",
            "doze", "treze", "quatorze", "quinze", "dezesseis",
            "dezessete", "dezoito", "dezenove",
        ][n]

    def dez_text(n):
        return [
            "", "dez", "vinte", "trinta", "quarenta", "cinquenta",
            "sessenta", "setenta", "oitenta", "noventa",
        ][n]

    def cem_text(n, valorTotal):
        if valorTotal == 100:
            return "cem"
        return ["", "cento", "duzentos", "trezentos", "quatrocentos",
                "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"][n]

    def segmento_ate_999(n):
        partes = []
        centenas = n // 100
        resto = n % 100
        dezenas = resto // 10
        unidades = resto % 10

        if centenas > 0:
            partes.append(cem_text(centenas, n))

        if resto > 0:
            if centenas > 0:
                partes.append("e")
            if resto < 20:
                partes.append(unid_text(resto))
            else:
                if dezenas > 0:
                    partes.append(dez_text(dezenas))
                if unidades > 0:
                    partes.append(unid_text(unidades))

        return partes

    def anotar_grupo(valor, label):
        if valor == 0:
            return []
        if label == "mil" and valor == 1:
            return ["mil"]
        if label == "milhão":
            if valor == 1:
                return ["um milhão"]
            return segmento_ate_999(valor)[:-1] + [segmento_ate_999(valor)[-1] + " milhão" ] if segmento_ate_999(valor) else ["um milhão"]
        if label == "milhões":
            if valor == 1:
                return ["um milhão"]
            result = segmento_ate_999(valor)
            if result:
                result[-1] = result[-1] + " milhões"
            return result
        partes = segmento_ate_999(valor)
        if partes:
            partes[-1] = partes[-1] + f" {label}"
        return partes

    negativo = valor < 0
    absoluto = abs(valor)

    partes = []
    if negativo:
        partes.append("menos")

    millions = absoluto // 1_000_000
    milhares = (absoluto // 1000) % 1000
    resto = absoluto % 1000

    if millions > 0:
        partes += anotar_grupo(millions, "milhões")
    if milhares > 0:
        partes += anotar_grupo(milhares, "mil")

    if resto > 0:
        if milhares > 0 and resto < 100:
            partes.append("e")
        partes += segmento_ate_999(resto)

    if not partes:
        partes = ["zero"]
    return [p.capitalize() for p in partes]


class Bubble:
    def __init__(self, text, x, y):
        self.text = text
        self.target_x = x
        self.target_y = y
        self.x = x + random.uniform(-80, 80)
        self.y = y + random.uniform(-40, 40)
        self.vx = random.uniform(-60, 60)
        self.vy = random.uniform(-40, 40)
        self.radius = max(48, FONT_BUBBLE.size(text)[0] // 2 + 24)
        self.scale = 0.0
        self.state = "appearing"
        self.pop_timer = 0.0
        self.color = BUBBLE_COLOR

    def update(self, dt, idx, bubbles):
        if self.state == "appearing":
            self.scale += dt * 4.0
            if self.scale >= 1.0:
                self.scale = 1.0
                self.state = "steady"

        elif self.state == "popping":
            self.scale -= dt * 5.0
            self.pop_timer += dt
            self.x += self.vx * dt
            self.y += self.vy * dt
            if self.scale <= 0:
                self.scale = 0

        springs = 10.0
        damping = 0.80

        if self.state != "popping":
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            self.vx += dx * springs * dt
            self.vy += dy * springs * dt

            if idx > 0:
                left = bubbles[idx - 1]
                if left is not self:
                    distance_x = left.x - self.x
                    distance_y = left.y - self.y
                    dist = math.hypot(distance_x, distance_y)
                    rest = self.radius + left.radius + 18
                    if dist > 0:
                        force = (dist - rest) * 1.8
                        self.vx += (distance_x / dist) * force * dt
                        self.vy += (distance_y / dist) * force * dt
            if idx < len(bubbles) - 1:
                right = bubbles[idx + 1]
                if right is not self:
                    distance_x = right.x - self.x
                    distance_y = right.y - self.y
                    dist = math.hypot(distance_x, distance_y)
                    rest = self.radius + right.radius + 18
                    if dist > 0:
                        force = (dist - rest) * 1.8
                        self.vx += (distance_x / dist) * force * dt
                        self.vy += (distance_y / dist) * force * dt

            self.vx *= damping
            self.vy *= damping
            self.x += self.vx * dt
            self.y += self.vy * dt

    def draw(self, surface):
        if self.scale <= 0:
            return

        radius = int(self.radius * self.scale)
        if radius <= 0:
            return

        bubble_color = self.color if self.state != "popping" else BUBBLE_POP_COLOR
        pygame.draw.circle(surface, bubble_color, (int(self.x), int(self.y)), radius)
        pygame.draw.circle(surface, (250, 250, 255), (int(self.x), int(self.y)), radius, 3)

        rendered = FONT_BUBBLE.render(self.text, True, (20, 20, 40))
        surface.blit(
            rendered,
            (
                int(self.x - rendered.get_width() / 2),
                int(self.y - rendered.get_height() / 2),
            ),
        )

    def pop(self):
        if self.state != "popping":
            self.state = "popping"
            self.vx = random.uniform(-250, 250)
            self.vy = random.uniform(-120, 120)
            self.color = BUBBLE_POP_COLOR


class BubbleManager:
    def __init__(self):
        self.bubbles = []
        self.current_words = []

    def set_words(self, words):
        if words == self.current_words:
            return
        old_bubbles = list(self.bubbles)
        self.current_words = list(words)

        target_area_x = WIDTH // 2
        base_y = 480
        widths = [max(60, FONT_BUBBLE.size(word)[0] + 36) for word in words]
        total_width = sum(widths) + max(0, len(widths) - 1) * 20
        start_x = target_area_x - total_width // 2

        new_bubbles = []
        x = start_x
        for i, (word, w) in enumerate(zip(words, widths)):
            target_x = x + w // 2
            if i < len(old_bubbles) and old_bubbles[i].text == word and old_bubbles[i].state != "popping":
                bubble = old_bubbles[i]
                bubble.target_x = target_x
                bubble.target_y = base_y
                bubble.radius = max(48, FONT_BUBBLE.size(word)[0] // 2 + 24)
                new_bubbles.append(bubble)
            else:
                if i < len(old_bubbles):
                    old_bubbles[i].pop()
                bubble = Bubble(word, target_x, base_y)
                new_bubbles.append(bubble)
            x += w + 20

        for bubble in old_bubbles[len(words):]:
            bubble.pop()

        self.bubbles = [bubble for bubble in old_bubbles if bubble.state == "popping" and bubble not in new_bubbles]
        self.bubbles.extend(new_bubbles)

    def update(self, dt):
        active = []
        for idx, bubble in enumerate(self.bubbles):
            bubble.update(dt, idx, self.bubbles)
            if bubble.scale > 0:
                active.append(bubble)
        self.bubbles = active

    def draw(self, surface):
        for i in range(len(self.bubbles) - 1):
            start = self.bubbles[i]
            end = self.bubbles[i + 1]
            pygame.draw.line(
                surface,
                LINE_COLOR,
                (int(start.x), int(start.y)),
                (int(end.x), int(end.y)),
                6,
            )
        for bubble in self.bubbles:
            bubble.draw(surface)


class CounterApp:
    def __init__(self):
        self.target = 5000
        self.current_value = 0
        self.is_counting = False
        self.direction = 1
        self.interval_ms = 500
        self.elapsed = 0.0
        self.bubble_manager = BubbleManager()
        self.number_words = numero_para_bubbles(self.current_value)
        self.bubble_manager.set_words(self.number_words)

    def reset(self):
        self.current_value = self.parse_input(START_FIELD.get_text())
        self.target = self.parse_input(TARGET_FIELD.get_text())
        self.direction = 1 if self.target >= self.current_value else -1
        self.is_counting = False
        self.elapsed = 0.0
        self.number_words = numero_para_bubbles(self.current_value)
        self.bubble_manager.set_words(self.number_words)

    def start(self):
        self.current_value = self.parse_input(START_FIELD.get_text())
        self.target = self.parse_input(TARGET_FIELD.get_text())
        self.direction = 1 if self.target >= self.current_value else -1
        self.is_counting = self.current_value != self.target
        self.elapsed = 0.0
        self.number_words = numero_para_bubbles(self.current_value)
        self.bubble_manager.set_words(self.number_words)

    def pause(self):
        self.is_counting = False

    def parse_input(self, text: str):
        try:
            return int(text.strip())
        except ValueError:
            return 0

    def update(self, dt):
        self.interval_ms = SPEED_SLIDER.get_current_value()
        SLIDER_LABEL.set_text(f"Intervalo: {self.interval_ms / 1000:.1f} s")

        if not self.is_counting:
            return

        if self.current_value == self.target:
            self.is_counting = False
            return

        self.elapsed += dt * 1000
        while self.elapsed >= self.interval_ms and self.current_value != self.target:
            self.elapsed -= self.interval_ms
            self.current_value += self.direction

        new_words = numero_para_bubbles(self.current_value)
        self.bubble_manager.set_words(new_words)

    def draw(self, surface):
        surface.fill(BG_COLOR)

        pygame.draw.rect(surface, CARD_COLOR, pygame.Rect(40, 20, WIDTH - 80, 160), border_radius=16)
        pygame.draw.rect(surface, CARD_COLOR, pygame.Rect(40, 200, WIDTH - 80, 520), border_radius=16)

        title = FONT_LARGE.render("Contador por Extenso", True, TEXT_COLOR)
        surface.blit(title, (50, 210))

        current_label = FONT_MEDIUM.render(
            f"Valor atual: {self.current_value}", True, (235, 235, 250)
        )
        surface.blit(current_label, (50, 290))

        phrase = "  ".join(self.number_words)
        wrapped = self.wrap_text(phrase, FONT_SMALL, WIDTH - 120)
        for i, line in enumerate(wrapped):
            text_render = FONT_SMALL.render(line, True, (220, 220, 240))
            surface.blit(text_render, (50, 620 + 28 * i))

        self.bubble_manager.draw(surface)

    @staticmethod
    def wrap_text(text, font, max_width):
        words = text.split(" ")
        lines = []
        current_line = words[0]
        for word in words[1:]:
            test_line = current_line + " " + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines


app = CounterApp()

running = True
while running:
    time_delta = CLOCK.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == BUTTON_PLAY:
                    app.start()
                elif event.ui_element == BUTTON_PAUSE:
                    app.pause()
                elif event.ui_element == BUTTON_RESET:
                    app.reset()

        UI_MANAGER.process_events(event)

    UI_MANAGER.update(time_delta)
    app.update(time_delta)
    app.bubble_manager.update(time_delta)

    app.draw(SCREEN)
    UI_MANAGER.draw_ui(SCREEN)
    pygame.display.update()

pygame.quit()
sys.exit()
