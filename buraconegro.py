import pygame
import sys
import random
import math
from collections import deque

# Inicialização
pygame.init()
LARGURA, ALTURA = 1000, 800  # Largura aumentada para 1000
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Bolas e Buraco Negro com Gráfico")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA = (50, 50, 50)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)

# Parâmetros do círculo
centro = (400, ALTURA // 2)  # Ajustado para a nova largura
raio_circulo = 350

# Configurações do gráfico
GRAFICO_LARGURA = 200
GRAFICO_ALTURA = 200
GRAFICO_X = LARGURA - GRAFICO_LARGURA - 20
GRAFICO_Y = 20
MAX_HISTORICO = 100  # Quantidade máxima de pontos no histórico

class Bola:
    def __init__(self, x=None, y=None):
        if x is None or y is None:
            # Posição aleatória dentro do círculo
            angulo = random.uniform(0, 2 * math.pi)
            distancia = random.uniform(0, raio_circulo - 20)
            self.x = centro[0] + distancia * math.cos(angulo)
            self.y = centro[1] + distancia * math.sin(angulo)
        else:
            self.x = x
            self.y = y
            
        self.raio = 15
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.cor = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.ativa = True

    def mover(self, objetos):
        if not self.ativa:
            return
            
        # Movimento
        self.x += self.vx
        self.y += self.vy
        
        # Colisão com as paredes do círculo
        distancia = math.sqrt((self.x - centro[0])**2 + (self.y - centro[1])**2)
        if distancia + self.raio > raio_circulo:
            # Reflexão
            normal_x = (self.x - centro[0]) / distancia
            normal_y = (self.y - centro[1]) / distancia
            dot = self.vx * normal_x + self.vy * normal_y
            self.vx -= 2 * dot * normal_x
            self.vy -= 2 * dot * normal_y
            
            # Reposiciona para evitar ficar preso na borda
            self.x = centro[0] + (raio_circulo - self.raio) * normal_x
            self.y = centro[1] + (raio_circulo - self.raio) * normal_y

        # Colisão com outros objetos
        for obj in objetos:
            if obj != self and obj.ativa:
                distancia_objs = math.sqrt((self.x - obj.x)**2 + (self.y - obj.y)**2)
                if distancia_objs < self.raio + obj.raio:
                    if isinstance(obj, BuracoNegro):
                        self.ativa = False  # Bola é engolida
                    else:
                        # Colisão elástica entre bolas
                        self.vx, obj.vx = obj.vx, self.vx
                        self.vy, obj.vy = obj.vy, self.vy
                        
                        # Afasta as bolas
                        overlap = (self.raio + obj.raio) - distancia_objs
                        dir_x = (self.x - obj.x) / distancia_objs
                        dir_y = (self.y - obj.y) / distancia_objs
                        self.x += dir_x * overlap / 2
                        self.y += dir_y * overlap / 2
                        obj.x -= dir_x * overlap / 2
                        obj.y -= dir_y * overlap / 2

    def desenhar(self):
        if self.ativa:
            pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.raio)

class BuracoNegro(Bola):
    def __init__(self):
        super().__init__(centro[0], centro[1])
        self.raio = 30
        self.cor = PRETO
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        
    def mover(self, objetos):
        # Movimento independente
        self.x += self.vx
        self.y += self.vy
        
        # Colisão com as paredes do círculo
        distancia = math.sqrt((self.x - centro[0])**2 + (self.y - centro[1])**2)
        if distancia + self.raio > raio_circulo:
            normal_x = (self.x - centro[0]) / distancia
            normal_y = (self.y - centro[1]) / distancia
            
            # Adiciona aleatoriedade ao ângulo de reflexão (~±20 graus)
            angulo_aleatorio = random.uniform(-0.35, 0.35)
            cos_ang = math.cos(angulo_aleatorio)
            sin_ang = math.sin(angulo_aleatorio)
            nova_normal_x = normal_x * cos_ang - normal_y * sin_ang
            nova_normal_y = normal_x * sin_ang + normal_y * cos_ang
            
            # Reflexão com a nova normal
            dot = self.vx * nova_normal_x + self.vy * nova_normal_y
            self.vx -= 2 * dot * nova_normal_x
            self.vy -= 2 * dot * nova_normal_y
            
            # Reposiciona
            self.x = centro[0] + (raio_circulo - self.raio) * normal_x
            self.y = centro[1] + (raio_circulo - self.raio) * normal_y

def desenhar_grafico(historico):
    if len(historico) < 2:
        return
    
    # Desenha o fundo do gráfico
    pygame.draw.rect(tela, BRANCO, (GRAFICO_X, GRAFICO_Y, GRAFICO_LARGURA, GRAFICO_ALTURA))
    pygame.draw.rect(tela, PRETO, (GRAFICO_X, GRAFICO_Y, GRAFICO_LARGURA, GRAFICO_ALTURA), 2)
    
    # Encontra o valor máximo para escalar o gráfico
    max_bolas = max(historico) if max(historico) > 0 else 1
    
    # Desenha as linhas do gráfico
    pontos = []
    for i, valor in enumerate(historico):
        x = GRAFICO_X + (i / (len(historico)-1)) * GRAFICO_LARGURA
        y = GRAFICO_Y + GRAFICO_ALTURA - (valor / max_bolas) * GRAFICO_ALTURA
        pontos.append((x, y))
    
    if len(pontos) > 1:
        pygame.draw.lines(tela, VERMELHO, False, pontos, 2)
    
    # Desenha os rótulos
    fonte_pequena = pygame.font.SysFont("Arial", 14)
    texto_max = fonte_pequena.render(f"Max: {max_bolas}", True, PRETO)
    texto_atual = fonte_pequena.render(f"Atual: {historico[-1]}", True, PRETO)
    tela.blit(texto_max, (GRAFICO_X + 10, GRAFICO_Y + 10))
    tela.blit(texto_atual, (GRAFICO_X + 10, GRAFICO_Y + 30))

# Criação dos objetos
bolas = [Bola() for _ in range(0)]
buraco_negro = BuracoNegro()

# Controle de tempo e histórico
tempo_ultima_bola = 0
tempo_ultimo_registro = 0
intervalo_novas_bolas = 100  # 1 segundo
intervalo_registro = 500  # 0.5 segundos
quantidade_maxima_bolas = 500
historico_bolas = deque(maxlen=MAX_HISTORICO)

# Fonte para texto
fonte = pygame.font.SysFont("Arial", 30)

# Loop principal
relogio = pygame.time.Clock()
running = True

while running:
    tempo_atual = pygame.time.get_ticks()
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False

    # Adiciona novas bolas periodicamente
    if tempo_atual - tempo_ultima_bola > intervalo_novas_bolas and len([b for b in bolas if b.ativa]) < quantidade_maxima_bolas:
        bolas.append(Bola())
        tempo_ultima_bola = tempo_atual

    # Registra a quantidade de bolas no histórico
    if tempo_atual - tempo_ultimo_registro > intervalo_registro:
        bolas_ativas = len([b for b in bolas if b.ativa])
        historico_bolas.append(bolas_ativas)
        tempo_ultimo_registro = tempo_atual

    # Atualiza física
    buraco_negro.mover([])
    for bola in bolas:
        if bola.ativa:
            bola.mover([b for b in bolas if b.ativa and b != bola] + [buraco_negro])

    # Remove bolas desativadas
    bolas = [b for b in bolas if b.ativa]

    # Desenho
    tela.fill(BRANCO)
    
    # Desenha o círculo principal
    pygame.draw.circle(tela, CINZA, centro, raio_circulo, 2)
    
    # Desenha o buraco negro
    pygame.draw.circle(tela, (30, 0, 0), (int(buraco_negro.x), int(buraco_negro.y)), buraco_negro.raio + 5)
    pygame.draw.circle(tela, PRETO, (int(buraco_negro.x), int(buraco_negro.y)), buraco_negro.raio)
    
    # Desenha as bolas
    for bola in bolas:
        bola.desenhar()

    # Desenha o gráfico
    desenhar_grafico(historico_bolas)

    # Contador de bolas
    bolas_ativas = len([b for b in bolas if b.ativa])
    texto = fonte.render(f"Bolas: {bolas_ativas}", True, PRETO)
    tela.blit(texto, (20, 20))

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
sys.exit()