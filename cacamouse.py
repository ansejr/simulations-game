import pygame
import sys
import random
import math
from pygame.locals import *

# Inicialização
pygame.init()
LARGURA, ALTURA = 1000, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Fuja dos Círculos!")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
CINZA = (200, 200, 200)
AMARELO = (255, 255, 0)

# Configurações do jogo
NUM_PERGUIDORES =2  # Quantidade de círculos perseguidores

class Perseguidor:
    def __init__(self, x, y):
        self.raio = 30
        self.x = x
        self.y = y
        self.velocidade = random.uniform(2, 4)  # Velocidade variada
        self.cor = (
            random.randint(200, 255),
            random.randint(0, 100),
            random.randint(0, 100)
        )
        self.ativo = True
    
    def atualizar(self, alvo_x, alvo_y):
        if not self.ativo:
            return False
        
        # Calcula direção ao alvo com suavização
        dx = alvo_x - self.x
        dy = alvo_y - self.y
        distancia = max(1, math.sqrt(dx*dx + dy*dy))
        
        # Move-se com velocidade variável
        self.x += dx * 0.05 * self.velocidade
        self.y += dy * 0.05 * self.velocidade
        
        # Verifica colisão com o mouse
        if distancia < self.raio:
            self.ativo = False
            return True  # Indica que deve explodir
        return False
    
    def desenhar(self):
        if self.ativo:
            pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.raio)
            # Detalhes nos perseguidores
            pygame.draw.circle(tela, BRANCO, (int(self.x - 10), int(self.y - 8)), 8)
            pygame.draw.circle(tela, BRANCO, (int(self.x + 10), int(self.y - 8)), 8)
            pygame.draw.circle(tela, PRETO, (int(self.x - 10), int(self.y - 8)), 3)
            pygame.draw.circle(tela, PRETO, (int(self.x + 10), int(self.y - 8)), 3)
            # Boca
            pygame.draw.arc(tela, PRETO, 
                           (self.x - 15, self.y + 5, 30, 20), 
                           math.pi, 2*math.pi, 2)

class Bolinha:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.raio = random.randint(5, 10)
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-8, 8)
        self.cor = (
            random.randint(150, 255),
            random.randint(0, 100),
            random.randint(0, 100)
        )
        self.tempo_vida = 180  # 3 segundos a 60 FPS
    
    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.tempo_vida -= 1
        
        # Colisão com as paredes
        if self.x < self.raio or self.x > LARGURA - self.raio:
            self.vx *= -0.8
        if self.y < self.raio or self.y > ALTURA - self.raio:
            self.vy *= -0.8
        
        # Mantém dentro da tela
        self.x = max(self.raio, min(LARGURA - self.raio, self.x))
        self.y = max(self.raio, min(ALTURA - self.raio, self.y))
        
        return self.tempo_vida > 0
    
    def desenhar(self):
        alpha = min(255, self.tempo_vida * 2)  # Efeito de fade out
        cor = (*self.cor[:3], alpha)
        surface = pygame.Surface((self.raio*2, self.raio*2), pygame.SRCALPHA)
        pygame.draw.circle(surface, cor, (self.raio, self.raio), self.raio)
        tela.blit(surface, (self.x - self.raio, self.y - self.raio))

class Botao:
    def __init__(self, x, y, largura, altura, texto):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor_normal = VERDE
        self.cor_hover = (100, 255, 100)
        self.texto = texto
    
    def desenhar(self, mouse_pos):
        hover = self.rect.collidepoint(mouse_pos)
        cor = self.cor_hover if hover else self.cor_normal
        
        pygame.draw.rect(tela, cor, self.rect)
        pygame.draw.rect(tela, PRETO, self.rect, 2)
        
        fonte = pygame.font.SysFont("Arial", 30)
        texto = fonte.render(self.texto, True, PRETO)
        tela.blit(texto, (
            self.rect.centerx - texto.get_width() // 2,
            self.rect.centery - texto.get_height() // 2
        ))
    
    def esta_sobre(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def criar_perseguidores(quantidade):
    return [Perseguidor(
        random.randint(50, LARGURA - 50),
        random.randint(50, ALTURA - 50)
    ) for _ in range(quantidade)]

def criar_explosao(x, y):
    return [Bolinha(x, y) for _ in range(30)]  # Menos bolinhas por explosão

def inicializar_jogo():
    global perseguidores, bolinhas, estado, mouse_visivel, vidas
    perseguidores = criar_perseguidores(NUM_PERGUIDORES)
    bolinhas = []
    estado = "jogando"  # "jogando", "perdeu" ou "venceu"
    vidas = NUM_PERGUIDORES

# Inicializa o jogo
inicializar_jogo()
botao_reset = Botao(LARGURA//2 - 100, ALTURA//2 - 30, 200, 60, "Jogar Novamente")

# Fonte para texto
fonte_info = pygame.font.SysFont("Arial", 24)

# Loop principal
relogio = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for evento in pygame.event.get():
        if evento.type == QUIT:
            running = False
        elif evento.type == MOUSEBUTTONDOWN:
            if estado != "jogando" and botao_reset.esta_sobre(mouse_pos):
                inicializar_jogo()
    
    # Atualizações
    if estado == "jogando":
        # Atualiza perseguidores
        for perseguidor in perseguidores:
            if perseguidor.ativo and perseguidor.atualizar(*mouse_pos):
                bolinhas.extend(criar_explosao(perseguidor.x, perseguidor.y))
                vidas -= 1
        
        # Verifica condição de vitória/derrota
        if vidas <= 0:
            estado = "perdeu"
        
        # Atualiza bolinhas da explosão
        bolinhas = [b for b in bolinhas if b.atualizar()]
    
    # Desenho
    tela.fill(BRANCO)
    
    # Desenha bolinhas primeiro (como fundo)
    for bolinha in bolinhas:
        bolinha.desenhar()
    
    if estado == "jogando":
        # Desenha perseguidores
        for perseguidor in perseguidores:
            if perseguidor.ativo:
                perseguidor.desenhar()
        
        # Desenha cursor personalizado
        pygame.draw.circle(tela, AZUL, mouse_pos, 10)
        pygame.draw.circle(tela, PRETO, mouse_pos, 10, 2)
        
        # Mostra vidas restantes
        texto_vidas = fonte_info.render(f"Perseguidores restantes: {vidas}", True, PRETO)
        tela.blit(texto_vidas, (20, 20))
    
    elif estado == "perdeu":
        # Mensagem de derrota
        texto_derrota = fonte_info.render("Você foi pego por todos os perseguidores!", True, VERMELHO)
        tela.blit(texto_derrota, (LARGURA//2 - texto_derrota.get_width()//2, ALTURA//2 - 80))
        botao_reset.desenhar(mouse_pos)
    
    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
sys.exit()