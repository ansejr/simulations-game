import pygame
import pygame_gui
import math
import random
import numpy as np
from collections import defaultdict
import time

# Inicialização do Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Configurações da tela
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BACKGROUND_COLOR = (20, 20, 30)

# Cores
NODE_COLOR = (100, 200, 255)
EDGE_COLOR = (150, 150, 150)
NEW_NODE_COLOR = (255, 200, 100)
HIGHLIGHT_COLOR = (255, 100, 100)
TEXT_COLOR = (255, 255, 255)

# Configurações do grafo
NODE_RADIUS = 25
MIN_DISTANCE = 100  # Distância mínima entre nós
ATTRACTION_STRENGTH = 0.01  # Força de atração para centralizar
REPULSION_STRENGTH = 1000  # Força de repulsão entre nós
DAMPING = 0.9  # Amortecimento do movimento

class CollatzNode:
    def __init__(self, value, position):
        self.value = value
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(0, 0)
        self.connections = []
        self.visible = False
        self.highlighted = False
        self.created_time = time.time()
        
    def add_connection(self, node):
        if node not in self.connections:
            self.connections.append(node)
    
    def apply_force(self, force):
        self.velocity += force
    
    def update_position(self):
        self.position += self.velocity
        self.velocity *= DAMPING
        
        # Manter dentro da tela com margem
        margin = NODE_RADIUS * 2
        self.position.x = max(margin, min(SCREEN_WIDTH - margin, self.position.x))
        self.position.y = max(margin + 100, min(SCREEN_HEIGHT - margin, self.position.y))

class CollatzVisualizer:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Visualizador da Conjectura de Collatz - Grafo Elástico")
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Variáveis de controle
        self.nodes = {}
        self.sequence = []
        self.current_index = 0
        self.is_paused = False
        self.is_playing = True
        self.generating = False
        self.last_node_time = 0
        self.input_value = ""
        self.new_nodes = []
        self.simulation_active = True
        
        # Sons
        self.drop_sound = self.create_drop_sound()
        
        # Fontes
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        
        # Configuração da interface
        self.setup_ui()
        
    def create_drop_sound(self):
        """Cria um som simples de gota"""
        try:
            sample_rate = 22050
            duration = 0.15
            samples = int(sample_rate * duration)
            
            sound_array = []
            for i in range(samples):
                t = float(i) / sample_rate
                freq = 1000 * math.exp(-t * 15)
                amplitude = 0.5 * math.exp(-t * 20)
                
                left = int(amplitude * math.sin(2 * math.pi * freq * t) * 32767)
                right = int(amplitude * math.sin(2 * math.pi * freq * t * 1.01) * 32767)
                
                sound_array.append([left, right])
            
            sound_array = np.array(sound_array, dtype=np.int16)
            sound = pygame.sndarray.make_sound(sound_array)
            return sound
        except Exception as e:
            print(f"Erro ao criar som: {e}")
            return pygame.mixer.Sound(buffer=bytes(44))
    
    def setup_ui(self):
        # Caixa de texto para input
        self.input_box = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((20, 20), (200, 40)),
            manager=self.manager,
            placeholder_text="Digite um número"
        )
        
        # Botões
        self.generate_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((230, 20), (100, 40)),
            text='Gerar',
            manager=self.manager
        )
        
        self.clear_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((340, 20), (100, 40)),
            text='Limpar',
            manager=self.manager
        )
        
        self.pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((450, 20), (80, 40)),
            text='⏸️',
            manager=self.manager,
            tool_tip_text="Pausar/Continuar animação"
        )
        
        self.prev_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((540, 20), (40, 40)),
            text='←',
            manager=self.manager,
            tool_tip_text="Passo anterior"
        )
        
        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((590, 20), (40, 40)),
            text='→',
            manager=self.manager,
            tool_tip_text="Próximo passo"
        )
        
        # Botão para pausar simulação física
        self.sim_pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((640, 20), (120, 40)),
            text='⏸️ Física',
            manager=self.manager,
            tool_tip_text="Pausar movimento dos nós"
        )
        
        # Label de status
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((770, 20), (250, 40)),
            text='Status: Pronto',
            manager=self.manager
        )
        
        # Informações adicionais
        self.info_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((1030, 20), (230, 40)),
            text='Nós: 0',
            manager=self.manager
        )
        
    def get_random_position(self):
        """Gera uma posição aleatória dentro da área visível"""
        margin = 150
        return pygame.Vector2(
            random.randint(margin, SCREEN_WIDTH - margin),
            random.randint(margin + 100, SCREEN_HEIGHT - margin)
        )
    
    def calculate_forces(self):
        """Calcula as forças entre os nós para criar o efeito elástico"""
        if not self.simulation_active:
            return
            
        # Forças de repulsão entre todos os nós
        nodes_list = list(self.nodes.values())
        for i, node1 in enumerate(nodes_list):
            if not node1.visible:
                continue
                
            for j, node2 in enumerate(nodes_list[i+1:], i+1):
                if not node2.visible:
                    continue
                    
                # Calcular vetor entre nós
                delta = node1.position - node2.position
                distance = delta.length()
                
                if distance < MIN_DISTANCE and distance > 0:
                    # Força de repulsão (inversamente proporcional à distância)
                    force = REPULSION_STRENGTH / (distance * distance)
                    direction = delta.normalize()
                    
                    # Aplicar força em direções opostas
                    node1.apply_force(direction * force * 0.5)
                    node2.apply_force(-direction * force * 0.5)
        
        # Força de atração para o centro (mantém o grafo na tela)
        center = pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        for node in nodes_list:
            if node.visible:
                to_center = center - node.position
                distance = to_center.length()
                if distance > 100:
                    force = to_center.normalize() * ATTRACTION_STRENGTH * distance
                    node.apply_force(force)
        
        # Força das conexões (molas)
        for node in nodes_list:
            if not node.visible:
                continue
            for connected_node in node.connections:
                if not connected_node.visible:
                    continue
                    
                # Calcular força da mola
                delta = connected_node.position - node.position
                distance = delta.length()
                
                if distance > 0:
                    # Força proporcional à distância (lei de Hooke)
                    spring_force = delta.normalize() * (distance - MIN_DISTANCE) * 0.01
                    node.apply_force(spring_force)
                    connected_node.apply_force(-spring_force)
    
    def update_positions(self):
        """Atualiza as posições de todos os nós"""
        for node in self.nodes.values():
            if node.visible:
                node.update_position()
    
    def collatz_next(self, n):
        """Calcula o próximo número na sequência de Collatz"""
        if n % 2 == 0:
            return n // 2
        else:
            return 3 * n + 1
            
    def generate_sequence(self, start_num):
        """Gera a sequência completa de Collatz"""
        sequence = []
        current = start_num
        visited = set()
        
        while current != 1 and current not in visited:
            visited.add(current)
            sequence.append(current)
            
            if current in self.nodes:
                break
                
            current = self.collatz_next(current)
        
        if current == 1 and 1 not in sequence and 1 not in visited:
            sequence.append(1)
            
        return sequence
        
    def add_sequence_to_graph(self, sequence):
        """Adiciona uma sequência ao grafo com posições aleatórias"""
        new_nodes = []
        
        for num in sequence:
            if num not in self.nodes:
                # Posição aleatória para novos nós
                position = self.get_random_position()
                
                # Se já existe um nó próximo, ajustar um pouco
                for existing_node in self.nodes.values():
                    if existing_node.visible:
                        dist = position.distance_to(existing_node.position)
                        if dist < MIN_DISTANCE:
                            # Afastar do nó existente
                            direction = (position - existing_node.position).normalize()
                            position = existing_node.position + direction * MIN_DISTANCE * 1.5
                            # Garantir que ainda está dentro da tela
                            position.x = max(100, min(SCREEN_WIDTH - 100, position.x))
                            position.y = max(150, min(SCREEN_HEIGHT - 100, position.y))
                
                node = CollatzNode(num, position)
                self.nodes[num] = node
                new_nodes.append(node)
        
        # Criar conexões
        for i in range(len(sequence) - 1):
            current_num = sequence[i]
            next_num = sequence[i + 1]
            
            if current_num in self.nodes and next_num in self.nodes:
                self.nodes[current_num].add_connection(self.nodes[next_num])
                
        return new_nodes
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.generate_button:
                    try:
                        start_num = int(self.input_box.get_text())
                        if start_num > 0:
                            self.start_generation(start_num)
                    except ValueError:
                        self.status_label.set_text('Status: Erro - Número inválido!')
                        
                elif event.ui_element == self.clear_button:
                    self.clear_graph()
                    
                elif event.ui_element == self.pause_button:
                    self.is_paused = not self.is_paused
                    self.is_playing = not self.is_paused
                    self.pause_button.set_text('▶️' if self.is_paused else '⏸️')
                    
                elif event.ui_element == self.sim_pause_button:
                    self.simulation_active = not self.simulation_active
                    self.sim_pause_button.set_text('▶️ Física' if not self.simulation_active else '⏸️ Física')
                    
                elif event.ui_element == self.prev_button:
                    self.go_previous()
                    
                elif event.ui_element == self.next_button:
                    self.go_next()
                    
            # Restringir entrada a números
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == self.input_box:
                    text = event.text
                    if text and not text.isdigit():
                        new_text = ''.join(filter(str.isdigit, text))
                        self.input_box.set_text(new_text)
                        
            self.manager.process_events(event)
            
        return True
        
    def start_generation(self, start_num):
        """Inicia a geração de uma nova sequência"""
        self.sequence = self.generate_sequence(start_num)
        self.new_nodes = self.add_sequence_to_graph(self.sequence)
        self.current_index = 0
        self.generating = True
        self.last_node_time = time.time()
        self.status_label.set_text(f'Status: Gerando {start_num}')
        
        # Esconder todos os novos nós inicialmente
        for node in self.new_nodes:
            node.visible = False
            
    def clear_graph(self):
        """Limpa todo o grafo"""
        self.nodes.clear()
        self.sequence = []
        self.current_index = 0
        self.generating = False
        self.new_nodes = []
        self.status_label.set_text('Status: Limpo')
        self.update_info_label()
        
    def go_previous(self):
        """Volta um passo na sequência"""
        if self.sequence and self.current_index > 0:
            self.current_index -= 1
            if self.current_index < len(self.sequence):
                node_value = self.sequence[self.current_index]
                if node_value in self.nodes:
                    self.highlight_node(node_value)
                    
    def go_next(self):
        """Avança um passo na sequência"""
        if self.sequence and self.current_index < len(self.sequence):
            node_value = self.sequence[self.current_index]
            if node_value in self.nodes:
                self.highlight_node(node_value)
            self.current_index += 1
            
    def highlight_node(self, value):
        """Destaca um nó específico"""
        for node in self.nodes.values():
            node.highlighted = False
            
        if value in self.nodes:
            self.nodes[value].highlighted = True
            
    def update_info_label(self):
        """Atualiza a label de informações"""
        sequence_str = f"{self.sequence[0] if self.sequence else '-'}"
        if len(self.sequence) > 1:
            sequence_str += f" → ... → {self.sequence[-1]}"
            
        self.info_label.set_text(f'Nós: {len(self.nodes)}')
            
    def update(self):
        time_delta = self.clock.tick(60) / 1000.0
        self.manager.update(time_delta)
        
        # Calcular forças e atualizar posições
        self.calculate_forces()
        self.update_positions()
        
        # Lógica de geração automática
        current_time = time.time()
        if self.generating and not self.is_paused and self.is_playing:
            if current_time - self.last_node_time >= 1.0:
                if self.current_index < len(self.new_nodes):
                    node = self.new_nodes[self.current_index]
                    node.visible = True
                    
                    try:
                        self.drop_sound.play()
                    except:
                        pass
                    
                    self.highlight_node(node.value)
                    
                    self.current_index += 1
                    self.last_node_time = current_time
                    
                    remaining = len(self.new_nodes) - self.current_index
                    self.status_label.set_text(f'Status: Gerando... ({remaining} restantes)')
                else:
                    self.generating = False
                    self.status_label.set_text('Status: Completo')
                    
        self.update_info_label()
    
    def draw_elastic_edge(self, start_pos, end_pos):
        """Desenha uma borda elástica (curva) entre dois nós"""
        start = pygame.Vector2(start_pos)
        end = pygame.Vector2(end_pos)
        
        # Calcular pontos de controle para a curva
        mid = (start + end) / 2
        direction = (end - start).normalize()
        perpendicular = pygame.Vector2(-direction.y, direction.x)
        
        # Adicionar curvatura baseada na distância
        distance = start.distance_to(end)
        curvature = distance * 0.2  # Curvatura proporcional à distância
        
        # Ponto de controle para curva bezier
        control = mid + perpendicular * curvature
        
        # Desenhar curva bezier
        points = []
        for t in range(21):
            t = t / 20
            # Curva quadrática de Bezier
            point = (1-t)**2 * start + 2*(1-t)*t * control + t**2 * end
            points.append((int(point.x), int(point.y)))
        
        # Desenhar a curva
        if len(points) > 1:
            pygame.draw.lines(self.screen, EDGE_COLOR, False, points, 2)
            
            # Desenhar seta no final
            if len(points) > 2:
                arrow_pos = points[-2]
                arrow_dir = (end - pygame.Vector2(arrow_pos)).normalize()
                
                arrow_size = 10
                arrow_angle = math.atan2(arrow_dir.y, arrow_dir.x)
                
                arrow_tip = end
                arrow_left = (arrow_tip[0] - arrow_size * math.cos(arrow_angle - 0.3),
                            arrow_tip[1] - arrow_size * math.sin(arrow_angle - 0.3))
                arrow_right = (arrow_tip[0] - arrow_size * math.cos(arrow_angle + 0.3),
                             arrow_tip[1] - arrow_size * math.sin(arrow_angle + 0.3))
                
                pygame.draw.polygon(self.screen, EDGE_COLOR, [arrow_tip, arrow_left, arrow_right])
        
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Desenhar título e instruções
        title_surface = self.title_font.render("Conjectura de Collatz - Grafo Elástico", True, TEXT_COLOR)
        self.screen.blit(title_surface, (20, 70))
        
        # Desenhar arestas elásticas
        for node in self.nodes.values():
            if node.visible:
                for connection in node.connections:
                    if connection.visible:
                        # Calcular pontos na borda dos círculos
                        start_pos = node.position
                        end_pos = connection.position
                        
                        dx = end_pos.x - start_pos.x
                        dy = end_pos.y - start_pos.y
                        dist = math.sqrt(dx**2 + dy**2)
                        
                        if dist > 0:
                            dx, dy = dx/dist, dy/dist
                            
                            start_point = (start_pos.x + dx * NODE_RADIUS, 
                                         start_pos.y + dy * NODE_RADIUS)
                            end_point = (end_pos.x - dx * NODE_RADIUS, 
                                       end_pos.y - dy * NODE_RADIUS)
                            
                            self.draw_elastic_edge(start_point, end_point)
        
        # Desenhar nós
        for node in self.nodes.values():
            if node.visible:
                # Escolher cor baseado no estado
                if node.highlighted:
                    color = HIGHLIGHT_COLOR
                elif node in self.new_nodes and self.generating:
                    progress = min(1.0, (time.time() - node.created_time) / 2.0)
                    color = (
                        int(NODE_COLOR[0] + (NEW_NODE_COLOR[0] - NODE_COLOR[0]) * progress),
                        int(NODE_COLOR[1] + (NEW_NODE_COLOR[1] - NODE_COLOR[1]) * progress),
                        int(NODE_COLOR[2] + (NEW_NODE_COLOR[2] - NODE_COLOR[2]) * progress)
                    )
                else:
                    color = NODE_COLOR
                
                # Desenhar círculo principal
                pygame.draw.circle(self.screen, color, 
                                 (int(node.position.x), int(node.position.y)), 
                                 NODE_RADIUS)
                
                # Desenhar borda
                border_color = (255, 255, 255) if node.highlighted else (200, 200, 200)
                pygame.draw.circle(self.screen, border_color, 
                                 (int(node.position.x), int(node.position.y)), 
                                 NODE_RADIUS, 2)
                
                # Desenhar número
                text = self.font.render(str(node.value), True, (255, 255, 255))
                text_rect = text.get_rect(center=(int(node.position.x), int(node.position.y)))
                
                # Sombra
                shadow_rect = text_rect.copy()
                shadow_rect.x += 2
                shadow_rect.y += 2
                shadow_text = self.font.render(str(node.value), True, (50, 50, 50))
                self.screen.blit(shadow_text, shadow_rect)
                
                self.screen.blit(text, text_rect)
        
        # Indicador de simulação física
        if self.simulation_active:
            sim_text = self.font.render("⚡ Física Ativa", True, (100, 255, 100))
        else:
            sim_text = self.font.render("⏸️ Física Pausada", True, (255, 100, 100))
        self.screen.blit(sim_text, (SCREEN_WIDTH - 150, 75))
        
        self.manager.draw_ui(self.screen)
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            
        pygame.quit()

if __name__ == "__main__":
    try:
        import numpy as np
    except ImportError:
        print("Instalando numpy...")
        import subprocess
        subprocess.check_call(["pip", "install", "numpy"])
        import numpy as np
    
    visualizer = CollatzVisualizer()
    visualizer.run()