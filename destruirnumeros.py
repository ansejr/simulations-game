import pygame
import pygame_gui
import random
import math

# Inicializando o Pygame e Pygame_GUI
pygame.init()

# --- Configurações da tela ---
largura_tela = 1400
altura_tela = 800
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Queda de Números Gigantes")

# --- Cores ---
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)

# --- Fonte ---
fonte_gigante = pygame.font.Font(None, 150)
fonte_explosao = pygame.font.Font(None, 24)
fonte_pequena = pygame.font.Font(None, 24)

# --- Chão ---
posicao_chao = altura_tela - 50

# --- Pygame_GUI Manager ---
# O UIManager é necessário para gerenciar eventos e o desenho de elementos da GUI
manager = pygame_gui.UIManager((largura_tela, altura_tela))

# --- Elementos de UI ---
# Caixa de texto para a gravidade
gravity_text_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 10), (150, 30)),
    text="Gravidade (0.0-1.0):",
    manager=manager
)

gravity_text_box = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((170, 10), (80, 30)),
    manager=manager
)
gravity_text_box.set_text("0.5")

# Caixas de texto para o mínimo e o máximo dos números
min_text_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((270, 10), (80, 30)),
    text="Mínimo:",
    manager=manager
)
min_text_box = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((360, 10), (80, 30)),
    manager=manager
)
min_text_box.set_text("1")

max_text_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((460, 10), (80, 30)),
    text="Máximo:",
    manager=manager
)
max_text_box = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((550, 10), (80, 30)),
    manager=manager
)
max_text_box.set_text("10")


# Valores iniciais
gravity_value = 0.5
min_value = 1
max_value = 10
current_number = min_value

# --- Classes ---
class Number:
    """Representa um número que cai com a gravidade."""
    def __init__(self, x, y, valor, gravity):
        self.valor = str(valor)
        self.x = x
        self.y = y
        self.velocidade_y = 0
        self.aceleracao_gravidade = gravity
        self.explodiu = False

    def atualizar(self):
        """Atualiza a posição do número baseada na gravidade."""
        self.velocidade_y += self.aceleracao_gravidade
        self.y += self.velocidade_y

        # Colisão com o chão
        if self.y >= posicao_chao - 75:  # Considera a altura do texto
            self.y = posicao_chao - 75
            self.velocidade_y = 0
            self.explodiu = True
            return True  # Retorna True para indicar que deve ser removido

        return False

    def desenhar(self):
        """Desenha o número na tela."""
        texto_superficie = fonte_gigante.render(self.valor, True, BRANCO)
        tela.blit(texto_superficie, (self.x - texto_superficie.get_width() // 2, self.y))

class Explosion:
    """Representa a animação de explosão de um número."""
    def __init__(self, x, y, valor):
        self.particulas = []
        for i in range(20):  # Cria 20 estilhaços
            angulo = random.uniform(0, 2 * math.pi)
            velocidade_x = random.uniform(-5, 5) + math.cos(angulo) * 5
            velocidade_y = random.uniform(-10, -5) + math.sin(angulo) * 5
            self.particulas.append({
                'texto': random.choice(valor),
                'x': x,
                'y': y,
                'vel_x': velocidade_x,
                'vel_y': velocidade_y,
                'tempo_vida': random.randint(30, 60)
            })
    
    def atualizar(self):
        """Atualiza a posição e o tempo de vida das partículas."""
        for particula in self.particulas:
            particula['vel_y'] += 0.3  # Gravidade nos estilhaços
            particula['x'] += particula['vel_x']
            particula['y'] += particula['vel_y']
            particula['tempo_vida'] -= 1
        
        # Remove partículas com tempo de vida esgotado
        self.particulas = [p for p in self.particulas if p['tempo_vida'] > 0]
        return not self.particulas  # Retorna True quando não há mais partículas

    def desenhar(self):
        """Desenha as partículas da explosão na tela."""
        for particula in self.particulas:
            texto_superficie = fonte_explosao.render(particula['texto'], True, VERMELHO)
            tela.blit(texto_superficie, (particula['x'], particula['y']))

# --- Main loop ---
numeros = []
explosoes = []
clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60)/1000.0  # Usado pelo Pygame_GUI
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Adiciona um novo número ao clicar com o mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Passa o valor atual e a gravidade para o novo número
            numeros.append(Number(x, y, current_number, gravity_value))
            
            # Incrementa o número para o próximo clique
            current_number += 1
            if current_number > max_value:
                current_number = min_value

        # Trata os eventos de finalização da edição das caixas de texto
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == gravity_text_box:
                try:
                    new_gravity = float(event.text)
                    gravity_value = new_gravity
                except ValueError:
                    print("Valor de gravidade inválido. Usando o valor anterior.")
            
            elif event.ui_element == min_text_box:
                try:
                    new_min = int(event.text)
                    if new_min <= max_value:
                        min_value = new_min
                        current_number = min_value  # Reinicia a sequência
                    else:
                        print("Valor mínimo deve ser menor ou igual ao máximo.")
                except ValueError:
                    print("Valor mínimo inválido. Usando o valor anterior.")
            
            elif event.ui_element == max_text_box:
                try:
                    # Se o valor for 0, trata como infinito
                    if event.text == '0':
                        max_value = float('inf')
                        current_number = min_value # Reinicia a sequência
                    else:
                        new_max = int(event.text)
                        if new_max >= min_value:
                            max_value = new_max
                            current_number = min_value # Reinicia a sequência
                        else:
                            print("Valor máximo deve ser maior ou igual ao mínimo.")
                except ValueError:
                    print("Valor máximo inválido. Usando o valor anterior.")
                
        # Passa o evento para o UIManager
        manager.process_events(event)

    # --- Atualizar ---
    # Atualiza o UIManager com o tempo passado
    manager.update(time_delta)

    # Atualiza os números e gerencia as explosões
    numeros_a_remover = []
    for num in numeros:
        if num.atualizar():
            numeros_a_remover.append(num)
            # Cria a explosão quando o número "explode"
            explosoes.append(Explosion(num.x, num.y, num.valor))

    for num in numeros_a_remover:
        numeros.remove(num)

    explosoes_a_remover = []
    for exp in explosoes:
        if exp.atualizar():
            explosoes_a_remover.append(exp)
            
    for exp in explosoes_a_remover:
        explosoes.remove(exp)

    # --- Desenhar ---
    tela.fill(PRETO)

    # Desenha o chão
    pygame.draw.rect(tela, (50, 50, 50), (0, posicao_chao, largura_tela, altura_tela - posicao_chao))

    for num in numeros:
        num.desenhar()

    for exp in explosoes:
        exp.desenhar()

    # Desenha a interface do Pygame_GUI
    manager.draw_ui(tela)

    pygame.display.flip()

# Saindo do Pygame
pygame.quit()