import pygame
import pygame_gui
import math
import time
import random

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Relógio com Ponteiros Customizados")

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

FONT = pygame.font.SysFont("Arial", 18)

CLOCK_CENTER = (400, 400)
CLOCK_RADIUS = 350
FPS = 60

def get_default_pointers():
    now = 0.0
    return {
        "Segundos": {"rpm": 1/60, "color": (255, 0, 0), "length": 300, "visible": True,
                     "angle_offset": 0.0, "time_at_change": now},
        "Minutos": {"rpm": 1/3600, "color": (0, 255, 0), "length": 280, "visible": True,
                    "angle_offset": 0.0, "time_at_change": now},
        "Horas": {"rpm": 1/43200, "color": (0, 0, 255), "length": 200, "visible": True,
                  "angle_offset": 0.0, "time_at_change": now},
    }

default_pointers = get_default_pointers()
extra_pointers = []

simulated_seconds = 0.0
start_real_time = time.time()
paused = False

pause_button = pygame_gui.elements.UIButton(pygame.Rect((820, 20), (180, 40)), 'Pausar/Continuar', manager)
add_pointer_button = pygame_gui.elements.UIButton(pygame.Rect((1010, 20), (160, 40)), 'Adicionar Ponteiro', manager)
reset_button = pygame_gui.elements.UIButton(pygame.Rect((820, 70), (350, 30)), 'Resetar Relógio', manager)

rpm_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((820, 160), (350, 30)),
    manager=manager
)

hide_button = pygame_gui.elements.UIButton(pygame.Rect((820, 200), (100, 30)), 'Esconder', manager)
delete_button = pygame_gui.elements.UIButton(pygame.Rect((930, 200), (100, 30)), 'Excluir', manager)

pointer_dropdown = None

def recreate_dropdown(selected="Segundos"):
    global pointer_dropdown
    if pointer_dropdown is not None:
        pointer_dropdown.kill()

    pointer_dropdown = pygame_gui.elements.UIDropDownMenu(
        options_list=list(default_pointers.keys()) + [p[0] for p in extra_pointers],
        starting_option=selected,
        relative_rect=pygame.Rect((820, 110), (350, 40)),
        manager=manager
    )

recreate_dropdown("Segundos")
rpm_input.set_text(str(default_pointers["Segundos"]["rpm"]))

def draw_clock():
    pygame.draw.circle(screen, (200, 200, 200), CLOCK_CENTER, CLOCK_RADIUS, 5)
    font = pygame.font.SysFont("Arial", 40, bold=True)
    for number in range(1, 13):
        angle = math.radians(number * 30 - 90)
        distance = CLOCK_RADIUS - 50
        x = CLOCK_CENTER[0] + distance * math.cos(angle)
        y = CLOCK_CENTER[1] + distance * math.sin(angle)
        text = font.render(str(number), True, (0, 0, 0))
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)
    for minute in range(0, 60):
        angle = math.radians(minute * 6 - 90)
        inner_radius = CLOCK_RADIUS - 20
        if minute % 5 == 0:
            outer_radius = CLOCK_RADIUS - 10
            thickness = 4
        else:
            outer_radius = CLOCK_RADIUS - 5
            thickness = 2
        start_pos = (
            CLOCK_CENTER[0] + inner_radius * math.cos(angle),
            CLOCK_CENTER[1] + inner_radius * math.sin(angle))
        end_pos = (
            CLOCK_CENTER[0] + outer_radius * math.cos(angle),
            CLOCK_CENTER[1] + outer_radius * math.sin(angle))
        pygame.draw.line(screen, (180, 180, 180), start_pos, end_pos, thickness)

def draw_hand(angle_deg, length, color):
    angle_rad = math.radians(angle_deg - 90)
    end_x = CLOCK_CENTER[0] + length * math.cos(angle_rad)
    end_y = CLOCK_CENTER[1] + length * math.sin(angle_rad)
    pygame.draw.line(screen, color, CLOCK_CENTER, (end_x, end_y), 4)

def get_pointer_angle(pointer, current_time):
    elapsed = current_time - pointer["time_at_change"]
    angle = pointer["angle_offset"] + elapsed * pointer["rpm"] * 360
    return angle % 360

def format_time_verbose(seconds):
    millennia = int(seconds // (1000 * 365.25 * 24 * 3600))
    seconds %= 1000 * 365.25 * 24 * 3600
    centuries = int(seconds // (100 * 365.25 * 24 * 3600))
    seconds %= 100 * 365.25 * 24 * 3600
    decades = int(seconds // (10 * 365.25 * 24 * 3600))
    seconds %= 10 * 365.25 * 24 * 3600
    years = int(seconds // (365.25 * 24 * 3600))
    seconds %= 365.25 * 24 * 3600
    days = int(seconds // (24 * 3600))
    seconds %= 24 * 3600
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    whole_seconds = int(seconds)
    ms = int((seconds % 1) * 1000)
    ns = int((seconds % (1/1000)) * 1_000_000)
    ps = int((seconds % (1/1_000_000)) * 1_000_000_000_000)
    return [
        f"Milênios: {millennia}",
        f"Séculos: {centuries}",
        f"Décadas: {decades}",
        f"Anos: {years}",
        f"Dias: {days}",
        f"Horas: {hours}",
        f"Minutos: {minutes}",
        f"Segundos: {whole_seconds}",
        f"Milissegundos: {ms}",
        f"Nanosegundos: {ns}",
        f"Picosegundos: {ps}"
    ]

def update_pointer_rpm(name, new_rpm):
    now = simulated_seconds
    def update_pointer(pointer):
        current_angle = get_pointer_angle(pointer, now)
        pointer["angle_offset"] = current_angle
        pointer["time_at_change"] = now
        pointer["rpm"] = new_rpm

    if name in default_pointers:
        update_pointer(default_pointers[name])
        if name == "Horas":
            update_pointer(default_pointers["Minutos"])
            default_pointers["Minutos"]["rpm"] = new_rpm * 60
            update_pointer(default_pointers["Segundos"])
            default_pointers["Segundos"]["rpm"] = new_rpm * 3600
        elif name == "Minutos":
            update_pointer(default_pointers["Horas"])
            default_pointers["Horas"]["rpm"] = new_rpm / 60
            update_pointer(default_pointers["Segundos"])
            default_pointers["Segundos"]["rpm"] = new_rpm * 60
        elif name == "Segundos":
            update_pointer(default_pointers["Horas"])
            default_pointers["Horas"]["rpm"] = new_rpm / 3600
            update_pointer(default_pointers["Minutos"])
            default_pointers["Minutos"]["rpm"] = new_rpm / 60
    else:
        for idx, (pname, pointer) in enumerate(extra_pointers):
            if pname == name:
                update_pointer(pointer)
                break

selected_pointer_name = "Segundos"
clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == pause_button:
                paused = not paused
                if not paused:
                    start_real_time = time.time()
            elif event.ui_element == add_pointer_button:
                name = f"Custom{len(extra_pointers)+1}"
                new_pointer = {"rpm": 1.0, "color": [random.randint(50,255) for _ in range(3)],
                               "length": 250, "visible": True, "angle_offset": 0.0,
                               "time_at_change": simulated_seconds}
                extra_pointers.append((name, new_pointer))
                recreate_dropdown(name)
            elif event.ui_element == reset_button:
                default_pointers = get_default_pointers()
                extra_pointers.clear()
                simulated_seconds = 0.0
                recreate_dropdown("Segundos")
                rpm_input.set_text(str(default_pointers["Segundos"]["rpm"]))
            elif event.ui_element == hide_button:
                if selected_pointer_name in default_pointers:
                    default_pointers[selected_pointer_name]["visible"] = False
                else:
                    for i, (name, pointer) in enumerate(extra_pointers):
                        if name == selected_pointer_name:
                            pointer["visible"] = False
            elif event.ui_element == delete_button:
                extra_pointers = [p for p in extra_pointers if p[0] != selected_pointer_name]
                recreate_dropdown("Segundos")

        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            selected_pointer_name = event.text
            if selected_pointer_name in default_pointers:
                rpm_input.set_text(str(default_pointers[selected_pointer_name]["rpm"]))
            else:
                for name, pointer in extra_pointers:
                    if name == selected_pointer_name:
                        rpm_input.set_text(str(pointer["rpm"]))
                        break

        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_element == rpm_input:
            try:
                val = float(rpm_input.get_text())
                if 0 <= val <= 100000:
                    update_pointer_rpm(selected_pointer_name, val)
            except ValueError:
                pass

        manager.process_events(event)

    if not paused:
        real_elapsed = time.time() - start_real_time
        start_real_time = time.time()
        simulated_seconds += real_elapsed * default_pointers["Segundos"]["rpm"] * 60

    manager.update(time_delta)
    screen.fill((30, 30, 30))

    draw_clock()

    for name, data in default_pointers.items():
        if data["visible"]:
            angle = get_pointer_angle(data, simulated_seconds)
            draw_hand(angle, data["length"], data["color"])

    for name, pointer in extra_pointers:
        if pointer["visible"]:
            angle = get_pointer_angle(pointer, simulated_seconds)
            draw_hand(angle, pointer["length"], pointer["color"])

    y_offset = 260
    pygame.draw.rect(screen, (50, 50, 70), pygame.Rect(810, y_offset - 10, 370, 330), border_radius=12)
    screen.blit(FONT.render("Tempo Simulado:", True, (255, 255, 255)), (820, y_offset))
    time_lines = format_time_verbose(simulated_seconds)
    for i, line in enumerate(time_lines):
        screen.blit(FONT.render(line, True, (200, 200, 0)), (830, y_offset + 30 + i * 25))

    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()