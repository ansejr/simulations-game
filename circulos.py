import pygame
import pygame_gui
import math

# Inicialização do Pygame
pygame.init()
pygame.display.set_caption("Spirograph Creator")
min_window_size = (800, 600)
window_size = (1000, 700)
window_surface = pygame.display.set_mode(window_size, pygame.RESIZABLE)
clock = pygame.time.Clock()

class Pivot:
    def __init__(self, circle, index, angle_offset):
        self.circle = circle
        self.index = index
        self.angle_offset = angle_offset
        self.connection = None
        self.world_x = 0.0
        self.world_y = 0.0

class Circle:
    def __init__(self, x, y, r, cid):
        self.id = cid
        self.center = (x, y)
        self.r = r
        # Velocidade padrão: 90 graus por segundo (em radianos)
        self.speed = math.radians(90)
        self.angle = 0.0
        # Cada círculo tem dois pivôs nas bordas (0 e 180 graus)
        self.pivots = [Pivot(self, 0, 0), Pivot(self, 1, math.pi)]
        self.parent_pivot = None 

class Trail:
    def __init__(self):
        self.points = []
        self.persistent_surface = pygame.Surface(window_size, pygame.SRCALPHA)
        self.hue = 0.0

    def resize(self, size):
        new_surf = pygame.Surface(size, pygame.SRCALPHA)
        new_surf.blit(self.persistent_surface, (0, 0))
        self.persistent_surface = new_surf

    def add_point(self, pos, is_break=False):
        color = pygame.Color(0)
        color.hsva = (self.hue, 100, 100, 100)
        self.points.append((pos[0], pos[1], color, is_break))
        self.hue = (self.hue + 0.5) % 360

    def draw(self, screen, max_dist):
        if len(self.points) < 2:
            screen.blit(self.persistent_surface, (0, 0))
            return

        # Desenho infinito (0 apaga apenas se limpar, persiste na tela)
        if max_dist == 0:
            for i in range(len(self.points) - 1):
                p1 = self.points[i]
                p2 = self.points[i+1]
                if not p2[3]: # Se não for uma quebra de rastro
                    pygame.draw.line(self.persistent_surface, p1[2], p1[:2], p2[:2], 3)
            # Mantém apenas o último ponto para continuar conectando
            self.points = [self.points[-1]]
            screen.blit(self.persistent_surface, (0, 0))
        else:
            # Rastro de tamanho finito
            self.persistent_surface.fill((0,0,0,0))
            
            # Poda de pontos antigos que ultrapassam a distância
            total_dist = 0
            prune_idx = 0
            for i in range(len(self.points)-1, 0, -1):
                p1 = self.points[i]
                p2 = self.points[i-1]
                if not p1[3]:
                    dist = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
                    total_dist += dist
                if total_dist > max_dist:
                    prune_idx = i - 1
                    break
            if prune_idx > 0:
                self.points = self.points[prune_idx:]

            # Desenho com transparência gradiente
            temp_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            dist_from_newest = 0
            for i in range(len(self.points)-1, 0, -1):
                p1 = self.points[i]
                p2 = self.points[i-1]
                
                if not p1[3]:
                    dist = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
                    # Calcula o alpha baseado na distância desde o ponto mais novo
                    alpha = int(255 * (1.0 - (dist_from_newest / max_dist)))
                    alpha = max(0, min(255, alpha))
                    color = pygame.Color(p1[2].r, p1[2].g, p1[2].b, alpha)
                    pygame.draw.line(temp_surf, color, p1[:2], p2[:2], 3)
                    dist_from_newest += dist
            
            screen.blit(temp_surf, (0, 0))
            
    def clear(self):
        self.points.clear()
        self.persistent_surface.fill((0,0,0,0))

manager = pygame_gui.UIManager(window_size)

main_panel = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect(0, 0, 250, window_size[1]), manager=manager)
play_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(10, 10, 100, 30), text="Play", manager=manager, container=main_panel)
clear_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(120, 10, 100, 30), text="Limpar Rastro", manager=manager, container=main_panel)

pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 50, 80, 30), text="Rastro (px):", manager=manager, container=main_panel)
trail_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(100, 50, 110, 30), manager=manager, container=main_panel)
trail_entry.set_text("0")

scroll_container = pygame_gui.elements.UIScrollingContainer(relative_rect=pygame.Rect(10, 90, 230, window_size[1] - 100), manager=manager, container=main_panel)

class CircleUI:
    def __init__(self, circle, manager, container, y_pos):
        self.circle = circle
        self.label = pygame_gui.elements.UILabel(
            pygame.Rect(5, y_pos, 70, 30), f"Circ {circle.id}", manager, container=container)
        self.speed_entry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect(80, y_pos, 60, 30), manager, container=container)
        self.speed_entry.set_text(str(int(math.degrees(circle.speed))))
        self.delete_btn = pygame_gui.elements.UIButton(
            pygame.Rect(145, y_pos, 30, 30), "X", manager, container=container)
        
    def kill(self):
        self.label.kill()
        self.speed_entry.kill()
        self.delete_btn.kill()

circles = []
circle_uis = []
trail = Trail()
next_circle_id = 1
playing = False
max_trail_dist = 0.0

is_creating = False
new_circle_center = (0,0)
new_circle_radius = 0
dragging_circle = None

def relayout_circle_uis():
    y = 5
    for ui in circle_uis:
        ui.label.set_relative_position((5, y))
        ui.speed_entry.set_relative_position((80, y))
        ui.delete_btn.set_relative_position((145, y))
        y += 35
    scroll_container.set_scrollable_area_dimensions((200, max(y, scroll_container.rect.height)))

def delete_circle(c):
    # Desconecta os filhos
    for p in c.pivots:
        if p.connection and p.connection.circle.parent_pivot == p.connection:
            child = p.connection.circle
            child.parent_pivot = None
            p.connection.connection = None
            p.connection = None
    # Desconecta do pai
    if c.parent_pivot:
        c.parent_pivot.connection.connection = None
        c.parent_pivot.connection = None
        c.parent_pivot = None
        
    circles.remove(c)
    ui_to_remove = next((ui for ui in circle_uis if ui.circle == c), None)
    if ui_to_remove:
        ui_to_remove.kill()
        circle_uis.remove(ui_to_remove)
    relayout_circle_uis()

def is_in_subtree(target, root):
    if target == root: return True
    for p in root.pivots:
        if p.connection and p.connection.circle.parent_pivot == p.connection:
            if is_in_subtree(target, p.connection.circle):
                return True
    return False

def update_circle_tree(c, dt):
    # Calcula a posição dos pivôs no mundo
    c.pivots[0].world_x = c.center[0] + c.r * math.cos(c.angle + c.pivots[0].angle_offset)
    c.pivots[0].world_y = c.center[1] + c.r * math.sin(c.angle + c.pivots[0].angle_offset)
    c.pivots[1].world_x = c.center[0] + c.r * math.cos(c.angle + c.pivots[1].angle_offset)
    c.pivots[1].world_y = c.center[1] + c.r * math.sin(c.angle + c.pivots[1].angle_offset)
    
    # Atualiza as posições de todos os filhos pendurados nos pivôs
    for p in c.pivots:
        if p.connection and p.connection.circle.parent_pivot == p.connection:
            child = p.connection.circle
            if playing:
                child.angle += child.speed * dt
            # O centro do filho é forçado a girar ao redor da conexão com o pai
            child.center = (
                p.world_x - child.r * math.cos(child.angle + p.connection.angle_offset),
                p.world_y - child.r * math.sin(child.angle + p.connection.angle_offset)
            )
            update_circle_tree(child, dt)

def update_positions(dt):
    # Inicia a atualização por todos os círculos "raiz" (que não tem pais)
    roots = [c for c in circles if c.parent_pivot is None]
    for r in roots:
        if playing:
            r.angle += r.speed * dt
        update_circle_tree(r, dt)

is_running = True
while is_running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        manager.process_events(event)
        
        if event.type == pygame.QUIT:
            is_running = False
            
        elif event.type == pygame.VIDEORESIZE:
            # Trava tamanho mínimo
            w = max(min_window_size[0], event.w)
            h = max(min_window_size[1], event.h)
            if w != event.w or h != event.h:
                window_surface = pygame.display.set_mode((w, h), pygame.RESIZABLE)
            else:
                window_size = (w, h)
                manager.set_window_resolution(window_size)
                main_panel.set_dimensions((250, window_size[1]))
                scroll_container.set_dimensions((230, window_size[1] - 100))
                trail.resize(window_size)
                
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == play_btn:
                playing = not playing
                play_btn.set_text("Stop" if playing else "Play")
            elif event.ui_element == clear_btn:
                trail.clear()
            else:
                for ui in circle_uis:
                    if event.ui_element == ui.delete_btn:
                        delete_circle(ui.circle)
                        break
                        
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_element == trail_entry:
                try:
                    val = float(event.text)
                    max_trail_dist = max(0.0, val)
                except ValueError:
                    pass
            else:
                for ui in circle_uis:
                    if event.ui_element == ui.speed_entry:
                        try:
                            ui.circle.speed = math.radians(float(event.text))
                        except ValueError:
                            pass

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = event.pos
                if pos[0] >= 250: # Fora do painel de UI
                    clicked_circle = None
                    for c in reversed(circles):
                        if math.hypot(c.center[0] - pos[0], c.center[1] - pos[1]) <= c.r:
                            clicked_circle = c
                            break
                    
                    if clicked_circle:
                        # Coloca o círculo interagido por cima
                        circles.remove(clicked_circle)
                        circles.append(clicked_circle)
                        dragging_circle = clicked_circle
                        # Se tiver pai, desconecta para mover de forma livre
                        if dragging_circle.parent_pivot:
                            dragging_circle.parent_pivot.connection.connection = None
                            dragging_circle.parent_pivot.connection = None
                            dragging_circle.parent_pivot = None
                    else:
                        is_creating = True
                        new_circle_center = pos
                        new_circle_radius = 0

        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos
            if is_creating:
                new_circle_radius = math.hypot(pos[0] - new_circle_center[0], pos[1] - new_circle_center[1])
            elif dragging_circle:
                dragging_circle.center = pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if is_creating:
                    if new_circle_radius >= 10:
                        c = Circle(new_circle_center[0], new_circle_center[1], new_circle_radius, next_circle_id)
                        next_circle_id += 1
                        circles.append(c)
                        ui = CircleUI(c, manager, scroll_container, len(circle_uis)*35 + 5)
                        circle_uis.append(ui)
                        relayout_circle_uis()
                    is_creating = False
                
                if dragging_circle:
                    # Lógica para "Snapping" / Junção de pivôs
                    snapped = False
                    for p_drag in dragging_circle.pivots:
                        if p_drag.connection is not None: continue
                        
                        for c_other in circles:
                            if c_other == dragging_circle or is_in_subtree(c_other, dragging_circle):
                                continue
                            for p_other in c_other.pivots:
                                if p_other.connection is None:
                                    # Se chegar próximo (20px) ele junta automaticamente
                                    if math.hypot(p_drag.world_x - p_other.world_x, p_drag.world_y - p_other.world_y) < 20:
                                        p_drag.connection = p_other
                                        p_other.connection = p_drag
                                        dragging_circle.parent_pivot = p_drag
                                        snapped = True
                                        break
                            if snapped: break
                        if snapped: break
                    dragging_circle = None

    manager.update(dt)
    update_positions(dt)

    # Pegar o último círculo livre para desenhar o rastro
    drawing_pivot = None
    for c in reversed(circles):
        free_pivots = [p for p in c.pivots if p.connection is None]
        if free_pivots:
            drawing_pivot = free_pivots[0]
            break
            
    if playing and drawing_pivot:
        pos = (drawing_pivot.world_x, drawing_pivot.world_y)
        is_break = False
        if trail.points:
            last_pos = trail.points[-1][:2]
            # Se deu um pulo grande (mudou de posição manualmente), quebra a linha contínua
            if math.hypot(pos[0]-last_pos[0], pos[1]-last_pos[1]) > 50:
                is_break = True
        trail.add_point(pos, is_break)

    window_surface.fill((30, 30, 35))
    
    # Desenho do rastro
    trail.draw(window_surface, max_trail_dist)

    # Desenho dos círculos e pivôs
    for c in circles:
        pygame.draw.circle(window_surface, (200, 200, 220), (int(c.center[0]), int(c.center[1])), int(c.r), 2)
        for p in c.pivots:
            px, py = int(p.world_x), int(p.world_y)
            if p.connection is None:
                color = (255, 80, 80) # Vermelho indica pivô solto/livre
            else:
                color = (80, 255, 80) # Verde indica pivô conectado
            pygame.draw.circle(window_surface, color, (px, py), 6)
            pygame.draw.circle(window_surface, (0, 0, 0), (px, py), 2)

    # Desenho temporário ao criar
    if is_creating and new_circle_radius > 0:
        pygame.draw.circle(window_surface, (150, 150, 150), (int(new_circle_center[0]), int(new_circle_center[1])), int(new_circle_radius), 1)

    manager.draw_ui(window_surface)
    pygame.display.flip()

pygame.quit()