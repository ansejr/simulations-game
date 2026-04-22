# display_panel_polygons.py
import pygame
import pygame_gui
import math
import time
import string
import random

pygame.init()

# ---------------- Screen / UI layout ----------------
WIDTH, HEIGHT = 1200, 600
UI_HEIGHT = 110   # zona reservada para UI no topo
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Displays 7 segmentos (polígonos)")
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ---------------- UI elements ----------------
display_type_dropdown = pygame_gui.elements.UIDropDownMenu(
    options_list=['7-seg', '7-seg'],
    starting_option='7-seg',
    relative_rect=pygame.Rect((20, 12), (100, 30)),
    manager=manager
)

num_displays_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((140, 12), (70, 30)), manager=manager)
num_displays_input.set_text("10")

text_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((230, 12), (420, 30)), manager=manager)
text_input.set_text("HELLO")

apply_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((660, 12), (100, 30)), text="Aplicar", manager=manager)

# Counter UI (speed in Hz up to 10_000_000)
counter_start_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((780, 12), (80, 30)), manager=manager)
counter_start_input.set_text("0")
counter_speed_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((870, 12), (120, 30)), manager=manager)
counter_speed_input.set_text("1.0")  # Hz (increments per second)
counter_toggle = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((1000, 12), (160, 30)), text="Iniciar Contador", manager=manager)

info_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 52), (800, 40)),
    text="Clique em um segmento para acender/apagar somente naquele display. Use 'Aplicar' para recriar displays.",
    manager=manager)

# ---------------- Helper geometry functions ----------------
def rotate_point(px, py, ang):
    """Rotate point (px,py) by ang radians around origin"""
    ca = math.cos(ang)
    sa = math.sin(ang)
    return px * ca - py * sa, px * sa + py * ca

def make_segment_polygon(cx, cy, length, thickness, orientation_deg, cap):
    """
    Cria um polígono aproximando um 'stick' com triângulos isósceles nas pontas.
    center (cx,cy), length (medida do eixo principal), thickness (espessura),
    orientation_deg em graus, cap = tamanho do triângulo na ponta.
    Retorna lista de pontos (global coords).
    """
    # pontos em sistema local (centro no (0,0), segmento ao longo do eixo x)
    L = length
    t = thickness
    c = cap
    # polígono em ordem (anti-horária)
    # left triangle apex, left triangle base top, rect top right, right triangle apex,
    # right triangle base bottom, rect bottom left
    local = [
        (-L/2 - c, 0.0),
        (-L/2, -t/2),
        ( L/2, -t/2),
        ( L/2 + c, 0.0),
        ( L/2,  t/2),
        (-L/2,  t/2)
    ]
    # rotate and translate
    ang = math.radians(orientation_deg)
    pts = []
    for (px, py) in local:
        rx, ry = rotate_point(px, py, ang)
        pts.append((cx + rx, cy + ry))
    return pts

# ponto em polígono - winding or ray casting
def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside

# ---------------- Segment mapping tables ----------------
# 7-seg labels: 'A','B','C','D','E','F','G' (A top, then clockwise)
SEG7_MAP = {
    '0': set("ABCDEF"), '1': set("BC"), '2': set("ABGED"), '3': set("ABCGD"),
    '4': set("FGB C".replace(" ", "")), # we'll replace bad spaces below
}
# Fix accidental formatting for 4
SEG7_MAP['4'] = set(list("FGB C".replace(" ", "")))  # actually will remap below properly

# Let's define a complete 7-seg table (expanded, more reliable)
SEG7_MAP = {
    '0': set("ABCDEF"),
    '1': set("BC"),
    '2': set("ABGED"),
    '3': set("ABCGD"),
    '4': set("FGB C".replace(" ", "")),  # placeholder, fix below
}

# Proper full 7-seg mapping (human-desired)
SEG7_TABLE = {
    '0': set('ABCDEF'),
    '1': set('BC'),
    '2': set('ABGED'),
    '3': set('ABCGD'),
    '4': set('FGB C'.replace(" ", "")),
}

# We'll build a correct and reasonably complete 7-seg mapping (explicit)
SEG7 = {
    '0': {'A','B','C','D','E','F'},
    '1': {'B','C'},
    '2': {'A','B','G','E','D'},
    '3': {'A','B','C','D','G'},
    '4': {'F','G','B','C'},
    '5': {'A','F','G','C','D'},
    '6': {'A','F','E','D','C','G'},
    '7': {'A','B','C'},
    '8': {'A','B','C','D','E','F','G'},
    '9': {'A','B','C','D','F','G'},
    'A': {'A','B','C','E','F','G'},
    'B': {'C','D','E','F','G'},
    'C': {'A','D','E','F'},
    'D': {'B','C','D','E','G'},
    'E': {'A','D','E','F','G'},
    'F': {'A','E','F','G'},
    '-': {'G'},
    ' ': set(),
}

# 16-seg: we'll use a more complete set of segment labels:
# labels: A (top), B (upper right vertical), C (lower right vertical),
# D (bottom), E (lower left vertical), F (upper left vertical),
# G1 (center horizontal left), G2 (center horizontal right),
# H (upper-left diagonal), I (upper-right diagonal),
# J (lower-right diagonal), K (lower-left diagonal),
# L (center vertical left), M (center vertical right), N (top-left small), O (top-right small)
# (This is an approximate labeling but richer than earlier.)
SEG16 = {
    # digits
    '0': {'A','B','C','D','E','F','H','I','J','K'},
    '1': {'B','C'},
    '2': {'A','B','G2','G1','E','D'},
    '3': {'A','B','C','D','G1','G2'},
    '4': {'F','G1','G2','B','C'},
    '5': {'A','F','G1','G2','C','D'},
    '6': {'A','F','E','D','C','G1','G2'},
    '7': {'A','B','C'},
    '8': set(['A','B','C','D','E','F','G1','G2','H','I','J','K','L','M']),
    '9': {'A','B','C','D','F','G1','G2'},
    # letters (approx)
    'A': {'A','B','C','E','F','G1','G2'},
    'B': {'F','E','G1','G2','C','D'},  # approximation
    'C': {'A','F','E','D'},
    'D': {'A','B','C','D','E','F'},
    'E': {'A','F','E','D','G1','G2'},
    'F': {'A','F','E','G1','G2'},
    'G': {'A','F','E','D','C'},
    'H': {'F','E','B','C','G1','G2'},
    'I': {'A','D','L','M'},
    'J': {'B','C','D'},
    'K': {'F','E','G1','G2','H','K'},
    'L': {'F','E','D'},
    'M': {'F','B','L','M'},
    'N': {'F','B','L','K'},
    'O': {'A','B','C','D','E','F'},
    'P': {'A','B','F','E','G1','G2'},
    'Q': {'A','B','C','D','E','F','M'},
    'R': {'A','B','F','E','G1','G2','M'},
    'S': {'A','F','G1','G2','C','D'},
    'T': {'A','L','M'},
    'U': {'F','B','C','D','E'},
    'V': {'H','K','J','I'},
    'W': {'F','E','C','B'},
    'X': {'H','I','J','K'},
    'Y': {'H','I','G2','B','C'},
    'Z': {'A','I','J','D'},
    ' ': set(),
    '-': {'G1','G2'},
    '_': {'D'},
}

# Normalize keys to uppercase
SEG7 = {k.upper():v for k,v in SEG7.items()}
SEG16 = {k.upper():v for k,v in SEG16.items()}

# ---------------- Display classes (7 and 16) ----------------
class Display7:
    def __init__(self, cx, cy, cell_w, cell_h):
        # cell_w is the width allocated for the whole digit, cell_h the height
        self.cx = cx
        self.cy = cy
        self.w = cell_w
        self.h = cell_h
        # thickness of the bar (in pixels)
        self.th = max(6, int(min(self.w, self.h) * 0.12))
        self.cap = max(3, int(self.th * 0.9))  # triangle cap
        self.segs = {}    # label -> polygon points
        self.manual_toggles = set()  # segments toggled by user (XOR behavior)
        self.auto_on = set()
        self._build_segments()

    def _build_segments(self):
        cx,cy,w,h,th,cap = self.cx,self.cy,self.w,self.h,self.th,self.cap
        # horizontal length should fit between vertical bars
        hlen = w - 2*th - 2  # small gap to try about 1px
        vlen = (h/2) - th - 2
        # A top horizontal
        Ax = cx
        Ay = cy - h/2 + th/2 + 1
        self.segs['A'] = make_segment_polygon(Ax, Ay, hlen, th, 0, cap)
        # D bottom horizontal
        Dx = cx
        Dy = cy + h/2 - th/2 - 1
        self.segs['D'] = make_segment_polygon(Dx, Dy, hlen, th, 0, cap)
        # G middle horizontal
        Gx = cx
        Gy = cy
        self.segs['G'] = make_segment_polygon(Gx, Gy, hlen*0.88, th, 0, int(cap*0.8))
        # B top-right vertical
        Bx = cx + w/2 - th/2 - 1
        By = cy - h/4
        self.segs['B'] = make_segment_polygon(Bx, By, vlen, th, 90, cap)
        # C bottom-right vertical
        Cx = cx + w/2 - th/2 - 1
        Cy = cy + h/4
        self.segs['C'] = make_segment_polygon(Cx, Cy, vlen, th, 90, cap)
        # F top-left vertical
        Fx = cx - w/2 + th/2 + 1
        Fy = cy - h/4
        self.segs['F'] = make_segment_polygon(Fx, Fy, vlen, th, 90, cap)
        # E bottom-left vertical
        Ex = cx - w/2 + th/2 + 1
        Ey = cy + h/4
        self.segs['E'] = make_segment_polygon(Ex, Ey, vlen, th, 90, cap)

    def set_char(self, ch):
        ch = ch.upper()
        self.auto_on = set()
        if ch in SEG7:
            self.auto_on = set(SEG7[ch])

    def draw(self, surf):
        # draw each segment with XOR of auto_on and manual toggles
        for seg,label_poly in self.segs.items():
            on = (seg in self.auto_on) ^ (seg in self.manual_toggles)
            color = (255, 80, 0) if on else (40, 30, 30)
            pygame.draw.polygon(surf, color, label_poly)
            # optional outline
            pygame.draw.polygon(surf, (20,20,20), label_poly, 1)

    def handle_click(self, pos):
        for seg, poly in self.segs.items():
            if point_in_poly(pos, poly):
                # toggle manual
                if seg in self.manual_toggles:
                    self.manual_toggles.remove(seg)
                else:
                    self.manual_toggles.add(seg)
                return True
        return False

class Display16:
    def __init__(self, cx, cy, cell_w, cell_h):
        self.cx = cx
        self.cy = cy
        self.w = cell_w
        self.h = cell_h
        self.th = max(6, int(min(self.w, self.h) * 0.10))
        self.cap = max(3, int(self.th * 0.9))
        self.segs = {}
        self.manual_toggles = set()
        self.auto_on = set()
        self._build_segments()

    def _build_segments(self):
        cx,cy,w,h,th,cap = self.cx,self.cy,self.w,self.h,self.th,self.cap
        # we'll create 16 segments placed around the glyph box:
        # horizontals: A (top), G1 (upper-mid), G2 (lower-mid), D (bottom)
        # verticals: F (upper-left), E (lower-left), B (upper-right), C (lower-right)
        # diagonals: H (upper-left diag), I (upper-right diag), J (lower-right diag), K (lower-left diag)
        # small center verticals: L (mid-left), M (mid-right)
        hlen_long = w - 2*th - 2
        hlen_mid = w*0.6
        vlen_long = (h/2) - th - 4
        vlen_mid = (h/4)
        # top A
        self.segs['A'] = make_segment_polygon(cx, cy - h/2 + th/2 + 1, hlen_long, th, 0, cap)
        # upper-mid G1 (left part of center horizontal)
        self.segs['G1'] = make_segment_polygon(cx - (w*0.18), cy - th*0.6, hlen_mid, th, 0, int(cap*0.7))
        # upper-mid G2 (right part)
        self.segs['G2'] = make_segment_polygon(cx + (w*0.18), cy - th*0.6, hlen_mid, th, 0, int(cap*0.7))
        # lower-mid H1/H2 use G parts mirrored down
        self.segs['G3'] = make_segment_polygon(cx - (w*0.18), cy + th*0.6, hlen_mid, th, 0, int(cap*0.7))
        self.segs['G4'] = make_segment_polygon(cx + (w*0.18), cy + th*0.6, hlen_mid, th, 0, int(cap*0.7))
        # bottom D
        self.segs['D'] = make_segment_polygon(cx, cy + h/2 - th/2 - 1, hlen_long, th, 0, cap)
        # verticals outer
        self.segs['B'] = make_segment_polygon(cx + w/2 - th/2 - 1, cy - h/4, vlen_long, th, 90, cap)
        self.segs['C'] = make_segment_polygon(cx + w/2 - th/2 - 1, cy + h/4, vlen_long, th, 90, cap)
        self.segs['E'] = make_segment_polygon(cx - w/2 + th/2 + 1, cy + h/4, vlen_long, th, 90, cap)
        self.segs['F'] = make_segment_polygon(cx - w/2 + th/2 + 1, cy - h/4, vlen_long, th, 90, cap)
        # center small verticals
        self.segs['L'] = make_segment_polygon(cx - w*0.12, cy, vlen_mid, th//1 or 4, 90, int(cap*0.5))
        self.segs['M'] = make_segment_polygon(cx + w*0.12, cy, vlen_mid, th//1 or 4, 90, int(cap*0.5))
        # diagonals (approx positions)
        self.segs['H'] = make_segment_polygon(cx - w*0.3, cy - h*0.25, math.hypot(w*0.25, h*0.18), int(th*0.85), -35, int(cap*0.7))
        self.segs['I'] = make_segment_polygon(cx + w*0.3, cy - h*0.25, math.hypot(w*0.25, h*0.18), int(th*0.85), 35, int(cap*0.7))
        self.segs['J'] = make_segment_polygon(cx + w*0.3, cy + h*0.25, math.hypot(w*0.25, h*0.18), int(th*0.85), 35, int(cap*0.7))
        self.segs['K'] = make_segment_polygon(cx - w*0.3, cy + h*0.25, math.hypot(w*0.25, h*0.18), int(th*0.85), -35, int(cap*0.7))
        # small top caps to complete 16-ish
        self.segs['N'] = make_segment_polygon(cx - w*0.22, cy - h/2 + th, w*0.12, th//2 or 3, 0, int(cap*0.4))
        self.segs['O'] = make_segment_polygon(cx + w*0.22, cy - h/2 + th, w*0.12, th//2 or 3, 0, int(cap*0.4))

        # Keep only 16 keys (if more, we'll use up to these)
        # final segment keys reliability:
        # expected keys include: A,B,C,D,E,F,G1,G2,G3,G4,L,M,H,I,J,K,N,O  (~17) - we will accept this.

    def set_char(self, ch):
        ch = ch.upper()
        self.auto_on = set()
        if ch in SEG16:
            self.auto_on = set(SEG16[ch])
        else:
            # fallback: choose the representable mask with closest segment-count
            # (simple heuristic)
            target = 6
            best = set()
            best_diff = 1e9
            for v in SEG16.values():
                d = abs(len(v) - target)
                if d < best_diff:
                    best_diff = d
                    best = v
            self.auto_on = set(best)

    def draw(self, surf):
        for seg, poly in self.segs.items():
            on = (seg in self.auto_on) ^ (seg in self.manual_toggles)
            color = (40, 220, 255) if on else (18, 30, 30)
            pygame.draw.polygon(surf, color, poly)
            pygame.draw.polygon(surf, (10,10,10), poly, 1)

    def handle_click(self, pos):
        for seg, poly in self.segs.items():
            if point_in_poly(pos, poly):
                if seg in self.manual_toggles:
                    self.manual_toggles.remove(seg)
                else:
                    self.manual_toggles.add(seg)
                return True
        return False

# ---------------- Panel management ----------------
class Panel:
    def __init__(self):
        self.kind = '7-seg'
        self.count = 6
        self.displays = []
        self.text = ''
        self.build(self.kind, self.count)

    def build(self, kind, count):
        self.kind = kind
        self.count = max(1, min(40, int(count)))  # cap max 40
        self.displays.clear()
        # compute per-cell width/height to fit neatly
        margin = 20
        available_w = WIDTH - 2*margin
        spacing = 10
        per_w = (available_w - (self.count-1)*spacing)/self.count
        per_w = max(40, per_w)
        per_h = UI_HEIGHT + (HEIGHT - UI_HEIGHT - 40) * 0.85 / 1.0  # large enough
        # center Y a bit below UI
        base_y = UI_HEIGHT + (HEIGHT - UI_HEIGHT)//2 - 20
        for i in range(self.count):
            cx = margin + i*(per_w + spacing) + per_w/2
            cy = base_y
            # choose cell_h relative to per_w
            cell_w = per_w*0.92
            cell_h = per_w * 2.0
            if kind == '7-seg':
                d = Display7(cx, cy, cell_w, cell_h)
            else:
                d = Display16(cx, cy, cell_w, cell_h)
            self.displays.append(d)

    def apply_text(self, txt):
        # limit to count
        txt = txt[:self.count].ljust(self.count, ' ')
        self.text = txt
        for i,ch in enumerate(txt):
            self.displays[i].set_char(ch)

    def clear_manual(self):
        for d in self.displays:
            d.manual_toggles.clear()

panel = Panel()
panel.build('7-seg', int(num_displays_input.get_text()))
panel.apply_text(text_input.get_text())

# ---------------- Counter state ----------------
counter_running = False
counter_value = int(counter_start_input.get_text())
counter_speed_hz = float(counter_speed_input.get_text())  # increments per second
counter_accumulator = 0.0  # accumulate fractional increments

# ---------------- Main loop ----------------
running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Allow pygame_gui to process events first (so clicks on UI are not treated as clicks on segments)
        manager.process_events(event)

        # GUI button events
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == apply_button:
                # rebuild displays with current settings
                kind = display_type_dropdown.selected_option
                try:
                    cnt = int(num_displays_input.get_text())
                except:
                    cnt = 6
                cnt = max(1, min(40, cnt))
                panel.build(kind, cnt)
                panel.apply_text(text_input.get_text())
            elif event.ui_element == counter_toggle:
                counter_running = not counter_running
                if counter_running:
                    counter_toggle.set_text("Parar Contador")
                    try:
                        counter_value = int(counter_start_input.get_text())
                    except:
                        counter_value = 0
                    try:
                        counter_speed_hz = float(counter_speed_input.get_text())
                    except:
                        counter_speed_hz = 1.0
                    # clamp speed_hz to allowed maximum (10 million)
                    if counter_speed_hz < 0:
                        counter_speed_hz = 0.0
                    if counter_speed_hz > 10_000_000:
                        counter_speed_hz = 10_000_000.0
                    counter_accumulator = 0.0
                else:
                    counter_toggle.set_text("Iniciar Contador")

        # Mouse clicks for segments (avoid clicks inside UI area)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx,my = event.pos
            if my > UI_HEIGHT:  # only allow clicking segments below UI region
                # check displays in order
                for d in panel.displays:
                    if d.handle_click((mx,my)):
                        break

    # Counter update by accumulation (supports large Hz)
    if counter_running and counter_speed_hz > 0:
        # accumulate increments
        counter_accumulator += counter_speed_hz * dt
        if counter_accumulator >= 1.0:
            increments = int(counter_accumulator)
            counter_accumulator -= increments
            counter_value += increments
            # update displays to show decimal representation (rightmost digits)
            s = str(counter_value)
            if len(s) > panel.count:
                s = s[-panel.count:]
            else:
                s = s.rjust(panel.count, ' ')
            panel.apply_text(s)

    # redraw
    manager.update(dt)
    screen.fill((12,12,12))
    # draw displays
    for d in panel.displays:
        d.draw(screen)

    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
