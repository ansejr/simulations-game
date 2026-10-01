import pygame
import pygame_gui
import math
import random
import sys

# Inicialização do Pygame
pygame.init()

# Configurações Iniciais da Tela
MIN_WIDTH, MIN_HEIGHT = 1000, 1000
screen = pygame.display.set_mode((MIN_WIDTH, MIN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Beltex Clone - Pygame")

COLOR_BG = (70, 130, 180)        # #4682B4 SteelBlue
COLOR_HEX = (173, 216, 230)      # LightBlue
COLOR_MINER = (255, 50, 50)      # Vermelho
COLOR_BELT = (100, 100, 100)     # Cinza escuro
COLOR_MATH = (255, 255, 50)      # Amarelo
COLOR_MATH_INPUT = (200, 200, 0) # Amarelo escuro
COLOR_ACCUMULATOR = (50, 255, 50)# Verde
COLOR_TUNNEL = (150, 50, 150)    # Roxo
COLOR_TEXT = (0, 0, 0)
COLOR_RESOURCE = (200, 200, 255) # Azul claro para recursos

# Direções em coordenadas axiais (q, r):
# 0: Direita, 1: Baixo-Dir, 2: Baixo-Esq, 3: Esquerda, 4: Cima-Esq, 5: Cima-Dir
HEX_DIRS = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]

manager = pygame_gui.UIManager((MIN_WIDTH, MIN_HEIGHT))
font = pygame.font.SysFont(None, 24)
small_font = pygame.font.SysFont(None, 18)

top_panel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(0, 0, MIN_WIDTH, 70),
    starting_height=0, manager=manager
)

tools = [
    ('Miner', 'MINER'), ('Belt', 'BELT'), ('Add (+)', 'ADD'), 
    ('Sub (-)', 'SUB'), ('Mul (*)', 'MUL'), ('Div (/)', 'DIV'), 
    ('Exp (^)', 'EXP'), ('Tunnel', 'TUNNEL'), ('Delete', 'DELETE'),
    ('Center', 'CENTER'), ('Zoom+', 'ZOOM_IN'), ('Zoom-', 'ZOOM_OUT')
]
buttons = {}
btn_width = 75
for i, (label, tool_id) in enumerate(tools):
    buttons[tool_id] = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(5 + i * (btn_width + 4), 10, btn_width, 45),
        text=label, manager=manager, container=top_panel
    )

def hex_to_pixel(q, r, size):
    x = size * math.sqrt(3) * (q + r / 2)
    y = size * 3 / 2 * r
    return x, y

def pixel_to_hex(x, y, size):
    q = (math.sqrt(3)/3 * x - 1/3 * y) / size
    r = (2/3 * y) / size
    return axial_round(q, r)

def axial_round(q, r):
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    q_diff, r_diff, s_diff = abs(rq - q), abs(rr - r), abs(rs - s)
    if q_diff > r_diff and q_diff > s_diff:
        rq = -rr - rs
    elif r_diff > s_diff:
        rr = -rq - rs
    return int(rq), int(rr)

def hex_distance(q1, r1, q2, r2):
    return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

def get_neighbor(q, r, direction_idx):
    dq, dr = HEX_DIRS[direction_idx]
    return q + dq, r + dr

def get_direction_index(q1, r1, q2, r2):
    dq, dr = q2 - q1, r2 - r1
    for i, d in enumerate(HEX_DIRS):
        if d == (dq, dr):
            return i
    return -1

class Item:
    def __init__(self, value):
        self.value = value

class Building:
    def __init__(self, q, r, b_type):
        self.q = q
        self.r = r
        self.b_type = b_type
        self.item = None
        self.progress = 0.0

    def accept_item(self, item):
        return False # Por padrão não aceita
        
    def update(self, dt, buildings_dict):
        pass

class Belt(Building):
    def __init__(self, q, r, direction, in_direction=None):
        super().__init__(q, r, 'BELT')
        self.direction = direction
        # Se in_direction não for passado, assume o oposto da saída (linha reta)
        self.in_direction = in_direction if in_direction is not None else (direction + 3) % 6
        self.speed = 1.5 # Hexágonos por segundo

    def accept_item(self, item):
        if self.item is None:
            self.item = item
            self.progress = 0.0
            return True
        return False

    def update(self, dt, buildings_dict):
        if self.item:
            self.progress += dt * self.speed
            if self.progress >= 1.0:
                next_q, next_r = get_neighbor(self.q, self.r, self.direction)
                next_b = buildings_dict.get((next_q, next_r))
                if next_b and next_b.accept_item(self.item):
                    self.item = None
                    self.progress = 0.0
                else:
                    self.progress = 1.0 # Fica preso na esteira (Fila)

class Miner(Building):
    def __init__(self, q, r, resource_val):
        super().__init__(q, r, 'MINER')
        self.resource_val = resource_val
        self.timer = 0.0
        self.production_rate = 1.0 # 1 item por segundo
        self.out_dir = 0 # Default Right

    def update(self, dt, buildings_dict):
        self.timer += dt
        if self.timer >= self.production_rate:
            # Tenta ejetar para todas as direções até achar uma esteira livre
            ejected = False
            for d in range(6):
                nq, nr = get_neighbor(self.q, self.r, d)
                next_b = buildings_dict.get((nq, nr))
                if next_b and isinstance(next_b, Belt) and next_b.accept_item(Item(self.resource_val)):
                    ejected = True
                    self.out_dir = d
                    break
            if ejected:
                self.timer = 0.0

class MathInput(Building):
    def __init__(self, q, r, core_q, core_r, slot_id):
        super().__init__(q, r, 'MATH_IN')
        self.core_q = core_q
        self.core_r = core_r
        self.slot_id = slot_id # 1 para dividendo/base, 2 para divisor/expoente

    def accept_item(self, item):
        if self.item is None:
            self.item = item
            self.progress = 0.0
            return True
        return False
        
    def update(self, dt, buildings_dict):
        if self.item:
            core = buildings_dict.get((self.core_q, self.core_r))
            if core and core.accept_input(self.item, self.slot_id):
                self.item = None

class MathCore(Building):
    def __init__(self, q, r, op_type):
        super().__init__(q, r, op_type)
        self.val1 = None # Slot 1 (Esq)
        self.val2 = None # Slot 2 (Dir)
        self.item_ready = None
        self.out_dir = 1 # Saída aponta para Baixo-Direita por padrão
        self.speed = 1.5

    def accept_input(self, item, slot_id):
        if slot_id == 1 and self.val1 is None:
            self.val1 = item.value
            return True
        if slot_id == 2 and self.val2 is None:
            self.val2 = item.value
            return True
        return False

    def update(self, dt, buildings_dict):
        # Processar conta se tiver os dois valores
        if self.val1 is not None and self.val2 is not None and self.item_ready is None:
            res = 0
            if self.b_type == 'ADD': res = self.val1 + self.val2
            elif self.b_type == 'SUB': res = self.val1 - self.val2
            elif self.b_type == 'MUL': res = self.val1 * self.val2
            elif self.b_type == 'DIV': res = self.val1 // self.val2 if self.val2 != 0 else 0
            elif self.b_type == 'EXP': res = self.val1 ** min(self.val2, 10) # Limite para não travar o jogo
            
            self.item_ready = Item(int(res))
            self.val1, self.val2 = None, None
            self.progress = 0.0

        # Ejetar resultado
        if self.item_ready:
            self.progress += dt * self.speed
            if self.progress >= 1.0:
                nq, nr = get_neighbor(self.q, self.r, self.out_dir)
                next_b = buildings_dict.get((nq, nr))
                if next_b and next_b.accept_item(self.item_ready):
                    self.item_ready = None
                    self.progress = 0.0
                else:
                    self.progress = 1.0

class Tunnel(Building):
    def __init__(self, q, r, direction):
        super().__init__(q, r, 'TUNNEL')
        self.direction = direction
        self.speed = 3.0 # Mais rápido por baixo da terra

    def accept_item(self, item):
        if self.item is None:
            self.item = item
            self.progress = 0.0
            return True
        return False

    def update(self, dt, buildings_dict):
        if self.item:
            self.progress += dt * self.speed
            if self.progress >= 1.0:
                # Pula 1 hexágono na direção
                dq, dr = HEX_DIRS[self.direction]
                out_q, out_r = self.q + dq * 2, self.r + dr * 2
                next_b = buildings_dict.get((out_q, out_r))
                if next_b and next_b.accept_item(self.item):
                    self.item = None
                    self.progress = 0.0
                else:
                    self.progress = 1.0

class Accumulator(Building):
    def __init__(self, q, r):
        super().__init__(q, r, 'ACCUMULATOR')
    def accept_item(self, item):
        global score
        score += item.value
        return True # Destrói o item absorvendo-o

world_map = {} # (q, r) -> resource_value (0 if empty)
buildings = {} # (q, r) -> Building instance
score = 0
camera = {'x': 0.0, 'y': 0.0, 'zoom': 15.0} # Zoom começa em 15px
selected_tool = 'MINER'

# Acumulador sempre no (0,0)
buildings[(0,0)] = Accumulator(0, 0)

def generate_chunk(cam_q, cam_r, radius):
    for dq in range(-radius, radius + 1):
        for dr in range(-radius, radius + 1):
            if abs(dq + dr) <= radius:
                q, r = cam_q + dq, cam_r + dr
                if (q, r) not in world_map:
                    random.seed(hash((q, r)))
                    if random.random() < 0.015 and hex_distance(q, r, 0, 0) > 3:
                        val = random.randint(1, 9)
                        world_map[(q, r)] = val
                        # Cluster pequeno
                        for ddir in HEX_DIRS:
                            if random.random() < 0.5:
                                world_map[(q+ddir[0], r+ddir[1])] = val
                    else:
                        if (q, r) not in world_map:
                            world_map[(q, r)] = 0

def draw_hex(surface, color, x, y, size, width=0):
    points = []
    for i in range(6):
        angle_rad = math.pi / 180 * (60 * i - 30)
        points.append((x + size * math.cos(angle_rad), y + size * math.sin(angle_rad)))
    pygame.draw.polygon(surface, color, points, width)
    if width == 0: pygame.draw.aalines(surface, (120,150,190), True, points)

is_dragging = False
last_drag_hex = None
last_build_hex = None # Memoriza o último bloco interagido para conexões contínuas ao clicar

clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.VIDEORESIZE:
            manager.set_window_resolution((event.w, event.h))
            top_panel.set_dimensions((event.w, 70))
            
        manager.process_events(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for tool_id, btn in buttons.items():
                if event.ui_element == btn:
                    if tool_id == 'CENTER':
                        camera['x'], camera['y'] = 0, 0
                    elif tool_id == 'ZOOM_IN':
                        camera['zoom'] = min(60.0, camera['zoom'] * 1.3)
                    elif tool_id == 'ZOOM_OUT':
                        camera['zoom'] = max(3.0, camera['zoom'] / 1.3)
                    else:
                        selected_tool = tool_id
                        last_build_hex = None # Reseta a memória ao trocar de ferramenta
                        pygame.display.set_caption(f"Beltex Clone - Ferramenta: {selected_tool}")
                        
        # Lógica do Mouse para Construção
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and event.pos[1] > 70:
            is_dragging = True
            mx, my = event.pos
            wx = mx - screen.get_width()/2 - camera['x']
            wy = my - screen.get_height()/2 - camera['y']
            hq, hr = pixel_to_hex(wx, wy, camera['zoom'])
            last_drag_hex = (hq, hr)
            
            # Construções instantâneas (Sem arrasto contínuo)
            if selected_tool == 'DELETE':
                if (hq, hr) in buildings and not isinstance(buildings[(hq, hr)], Accumulator):
                    b = buildings[(hq, hr)]
                    if b.b_type == 'MATH_IN':
                        if (b.core_q, b.core_r) in buildings: del buildings[(b.core_q, b.core_r)]
                    elif b.b_type in ['ADD','SUB','MUL','DIV','EXP']:
                        # Deleta os inputs associados a este core
                        keys_to_del = [k for k, v in buildings.items() if v.b_type == 'MATH_IN' and v.core_q == hq and v.core_r == hr]
                        for k in keys_to_del: del buildings[k]
                    del buildings[(hq, hr)]
                last_build_hex = None # Quebra a corrente ao deletar
                    
            elif selected_tool == 'MINER':
                if (hq, hr) not in buildings:
                    res_val = world_map.get((hq, hr), 0)
                    if res_val > 0: buildings[(hq, hr)] = Miner(hq, hr, res_val)
                if (hq, hr) in buildings:
                    last_build_hex = (hq, hr) # Salva o mineirador para puxar a esteira a partir dele
                
            elif selected_tool == 'BELT':
                # Conecta automaticamente com a última peça clicada (se for vizinha)
                if last_build_hex and hex_distance(hq, hr, last_build_hex[0], last_build_hex[1]) == 1:
                    direction_idx = get_direction_index(last_build_hex[0], last_build_hex[1], hq, hr)
                    
                    # Alinha a esteira anterior para apontar pra cá
                    if last_build_hex in buildings and isinstance(buildings[last_build_hex], Belt):
                        buildings[last_build_hex].direction = direction_idx
                        
                    # Cria ou atualiza a nova esteira para receber da anterior
                    in_dir = (direction_idx + 3) % 6
                    if (hq, hr) not in buildings:
                        buildings[(hq, hr)] = Belt(hq, hr, direction_idx, in_dir)
                    elif isinstance(buildings[(hq, hr)], Belt):
                        buildings[(hq, hr)].in_direction = in_dir
                        
                # Ou inicia uma esteira isolada
                elif (hq, hr) not in buildings:
                    buildings[(hq, hr)] = Belt(hq, hr, direction=0, in_direction=3)
                
                # Salva esse clique como ponto de partida para o próximo
                if (hq, hr) in buildings:
                    last_build_hex = (hq, hr)
                
            elif selected_tool in ['ADD', 'SUB', 'MUL', 'DIV', 'EXP']:
                # Ocupa 3 Hex: Core no centro, Inputs nas direções Top-Left(4) e Top-Right(5)
                q1, r1 = get_neighbor(hq, hr, 4)
                q2, r2 = get_neighbor(hq, hr, 5)
                if (hq,hr) not in buildings and (q1,r1) not in buildings and (q2,r2) not in buildings:
                    buildings[(hq, hr)] = MathCore(hq, hr, selected_tool)
                    buildings[(q1, r1)] = MathInput(q1, r1, hq, hr, 1) # Slot 1 (Esq)
                    buildings[(q2, r2)] = MathInput(q2, r2, hq, hr, 2) # Slot 2 (Dir)
                last_build_hex = None

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            is_dragging = False
            last_drag_hex = None
            
        elif event.type == pygame.MOUSEMOTION and is_dragging:
            # Lógica de Arrasto Contínuo (Esteiras e Túneis)
            mx, my = event.pos
            wx = mx - screen.get_width()/2 - camera['x']
            wy = my - screen.get_height()/2 - camera['y']
            hq, hr = pixel_to_hex(wx, wy, camera['zoom'])
            
            if (hq, hr) != last_drag_hex and hex_distance(hq, hr, last_drag_hex[0], last_drag_hex[1]) == 1:
                direction_idx = get_direction_index(last_drag_hex[0], last_drag_hex[1], hq, hr)
                
                if selected_tool == 'BELT':
                    # Aproveita a mesma lógica robusta do clique em sequência para o arrasto
                    if last_build_hex and hex_distance(hq, hr, last_build_hex[0], last_build_hex[1]) == 1:
                        direction_idx = get_direction_index(last_build_hex[0], last_build_hex[1], hq, hr)
                        
                        if last_build_hex in buildings and isinstance(buildings[last_build_hex], Belt):
                            buildings[last_build_hex].direction = direction_idx
                            
                        in_dir = (direction_idx + 3) % 6
                        if (hq, hr) not in buildings:
                            buildings[(hq, hr)] = Belt(hq, hr, direction_idx, in_dir)
                        elif isinstance(buildings[(hq, hr)], Belt):
                            buildings[(hq, hr)].in_direction = in_dir
                    else:
                        # Fallback (caso pule um frame)
                        if last_drag_hex in buildings and isinstance(buildings[last_drag_hex], Belt):
                            buildings[last_drag_hex].direction = direction_idx
                        elif last_drag_hex not in buildings:
                            buildings[last_drag_hex] = Belt(last_drag_hex[0], last_drag_hex[1], direction_idx, (direction_idx+3)%6)
                            
                        in_dir = (direction_idx + 3) % 6
                        if (hq, hr) not in buildings:
                            buildings[(hq, hr)] = Belt(hq, hr, direction_idx, in_dir)
                        elif isinstance(buildings[(hq, hr)], Belt):
                            buildings[(hq, hr)].in_direction = in_dir
                            
                    last_build_hex = (hq, hr)
                        
                elif selected_tool == 'TUNNEL':
                    if last_drag_hex not in buildings:
                        buildings[last_drag_hex] = Tunnel(last_drag_hex[0], last_drag_hex[1], direction_idx)
                
                last_drag_hex = (hq, hr)

    keys = pygame.key.get_pressed()
    speed = 400 * time_delta
    if keys[pygame.K_LEFT]: camera['x'] += speed
    if keys[pygame.K_RIGHT]: camera['x'] -= speed
    if keys[pygame.K_UP]: camera['y'] += speed
    if keys[pygame.K_DOWN]: camera['y'] -= speed

    # Atualiza as construções (Itens, Mineração, Matemática)
    for b in list(buildings.values()):
        b.update(time_delta, buildings)

    # Geração Dinâmica de Chunk
    center_q, center_r = pixel_to_hex(-camera['x'], -camera['y'], camera['zoom'])
    generate_chunk(center_q, center_r, radius=int(max(MIN_WIDTH, MIN_HEIGHT) / (camera['zoom'] * 2)) + 2)

    screen.fill(COLOR_BG)
    cx, cy = screen.get_width()/2 + camera['x'], screen.get_height()/2 + camera['y']
    
    # Desenhar Chão e Recursos
    for (q, r), val in world_map.items():
        px, py = hex_to_pixel(q, r, camera['zoom'])
        sc_x, sc_y = cx + px, cy + py
        
        if -50 < sc_x < screen.get_width()+50 and -50 < sc_y < screen.get_height()+50:
            color = COLOR_RESOURCE if val > 0 else COLOR_HEX
            draw_hex(screen, color, sc_x, sc_y, camera['zoom'] - 0.5)
            if val > 0 and camera['zoom'] > 12:
                txt = font.render(str(val), True, (100,100,100))
                screen.blit(txt, (sc_x - txt.get_width()/2, sc_y - txt.get_height()/2))

    # Desenhar Construções e Itens
    for (q, r), b in buildings.items():
        px, py = hex_to_pixel(q, r, camera['zoom'])
        sc_x, sc_y = cx + px, cy + py
        
        if not (-50 < sc_x < screen.get_width()+50 and -50 < sc_y < screen.get_height()+50):
            continue

        if isinstance(b, Accumulator):
            draw_hex(screen, COLOR_ACCUMULATOR, sc_x, sc_y, camera['zoom'])
            txt = font.render(f"SCORE: {score}", True, COLOR_TEXT)
            screen.blit(txt, (sc_x - txt.get_width()/2, sc_y - txt.get_height()/2))
            
        elif isinstance(b, Miner):
            draw_hex(screen, COLOR_MINER, sc_x, sc_y, camera['zoom'])
            if camera['zoom'] > 15:
                txt = small_font.render("MINER", True, (255,255,255))
                screen.blit(txt, (sc_x - txt.get_width()/2, sc_y - txt.get_height()/2))
            
        elif isinstance(b, Belt):
            # Fundo da esteira
            draw_hex(screen, COLOR_BELT, sc_x, sc_y, camera['zoom'])
            
            # Cálculo da Curva Bezier para o Trilho
            d_in = HEX_DIRS[b.in_direction]
            d_out = HEX_DIRS[b.direction]
            Ax, Ay = hex_to_pixel(d_in[0]*0.5, d_in[1]*0.5, camera['zoom'])
            Cx, Cy = hex_to_pixel(d_out[0]*0.5, d_out[1]*0.5, camera['zoom'])
            
            track_w = max(2, int(camera['zoom'] / 2.5))
            
            # Gerar pontos da curva
            curve_pts = []
            for i in range(11):
                t = i / 10.0
                px = ((1-t)**2) * Ax + (t**2) * Cx
                py = ((1-t)**2) * Ay + (t**2) * Cy
                curve_pts.append((sc_x + px, sc_y + py))
                
            pygame.draw.lines(screen, (40, 40, 40), False, curve_pts, track_w)
                             
            # Setas de indicação de fluxo ao longo da curva
            if camera['zoom'] > 10:
                t = 0.5
                px = ((1-t)**2) * Ax + (t**2) * Cx
                py = ((1-t)**2) * Ay + (t**2) * Cy
                
                # Derivada da Bezier para obter a tangente exata da curva
                dx = -2*(1-t)*Ax + 2*t*Cx
                dy = -2*(1-t)*Ay + 2*t*Cy
                angle = math.atan2(dy, dx)
                
                a_size = camera['zoom'] * 0.3
                p1 = (sc_x + px, sc_y + py)
                p2 = (p1[0] - math.cos(angle - 0.6) * a_size, p1[1] - math.sin(angle - 0.6) * a_size)
                p3 = (p1[0] - math.cos(angle + 0.6) * a_size, p1[1] - math.sin(angle + 0.6) * a_size)
                pygame.draw.lines(screen, (200, 200, 200), False, [p2, p1, p3], max(2, int(camera['zoom']/8)))
            
        elif isinstance(b, MathCore):
            draw_hex(screen, COLOR_MATH, sc_x, sc_y, camera['zoom'])
            sym = {'ADD':'+', 'SUB':'-', 'MUL':'x', 'DIV':'/', 'EXP':'^'}.get(b.b_type, '?')
            txt = font.render(sym, True, COLOR_TEXT)
            screen.blit(txt, (sc_x - txt.get_width()/2, sc_y - txt.get_height()/2))
            
        elif isinstance(b, MathInput):
            draw_hex(screen, COLOR_MATH_INPUT, sc_x, sc_y, camera['zoom'])
            if camera['zoom'] > 15:
                label = "1" if b.slot_id == 1 else "2"
                txt = small_font.render(label, True, (100,100,0))
                screen.blit(txt, (sc_x - txt.get_width()/2, sc_y - txt.get_height()/2))

        elif isinstance(b, Tunnel):
            draw_hex(screen, COLOR_TUNNEL, sc_x, sc_y, camera['zoom'])
            d = HEX_DIRS[b.direction]
            nx, ny = hex_to_pixel(d[0]*0.4, d[1]*0.4, camera['zoom'])
            pygame.draw.line(screen, (0,0,0), (sc_x, sc_y), (sc_x + nx, sc_y + ny), 3)

        # Desenho do Item animando
        if getattr(b, 'item', None) or (isinstance(b, MathCore) and b.item_ready):
            active_item = b.item_ready if isinstance(b, MathCore) else b.item
            item_prog = b.progress
            
            ix, iy = sc_x, sc_y
            if isinstance(b, Belt):
                # Movimentação acompanha perfeitamente a Curva Bezier
                d_in = HEX_DIRS[b.in_direction]
                d_out = HEX_DIRS[b.direction]
                Ax, Ay = hex_to_pixel(d_in[0]*0.5, d_in[1]*0.5, camera['zoom'])
                Cx, Cy = hex_to_pixel(d_out[0]*0.5, d_out[1]*0.5, camera['zoom'])
                
                t = item_prog
                px = ((1-t)**2) * Ax + (t**2) * Cx
                py = ((1-t)**2) * Ay + (t**2) * Cy
                ix += px
                iy += py
            elif hasattr(b, 'direction') or isinstance(b, MathCore):
                dir_idx = getattr(b, 'direction', getattr(b, 'out_dir', 1))
                d = HEX_DIRS[dir_idx]
                # Outras construções animam do centro(0) à borda de saída(0.5)
                tx, ty = hex_to_pixel(d[0]*0.5, d[1]*0.5, camera['zoom'])
                ix += tx * item_prog
                iy += ty * item_prog
                
            pygame.draw.circle(screen, (255, 255, 255), (int(ix), int(iy)), max(3, int(camera['zoom']/2.5)))
            if camera['zoom'] > 12:
                txt = small_font.render(str(active_item.value), True, COLOR_TEXT)
                screen.blit(txt, (ix - txt.get_width()/2, iy - txt.get_height()/2))

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()