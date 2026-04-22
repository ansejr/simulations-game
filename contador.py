import pygame
import sys
import time
from pygame.locals import *

# Inicialização
pygame.init()
pygame.font.init()
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Contador com Aceleração")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
CINZA = (200, 200, 200)
CINZA_ESCURO = (100, 100, 100)
AMARELO = (255, 255, 0)

# Fontes
fonte_grande = pygame.font.SysFont("Arial", 80)
fonte_media = pygame.font.SysFont("Arial", 30)
fonte_pequena = pygame.font.SysFont("Arial", 24)

class Botao:
    def __init__(self, x, y, largura, altura, texto, cor_normal=VERDE, cor_hover=CINZA):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor_normal = cor_normal
        self.cor_hover = cor_hover
        self.cor_atual = cor_normal
        self.ativo = True
    
    def desenhar(self, superficie):
        pygame.draw.rect(superficie, self.cor_atual, self.rect)
        pygame.draw.rect(superficie, PRETO, self.rect, 2)
        
        texto_render = fonte_media.render(self.texto, True, PRETO)
        superficie.blit(texto_render, (
            self.rect.centerx - texto_render.get_width() // 2,
            self.rect.centery - texto_render.get_height() // 2
        ))
    
    def verificar_clique(self, pos):
        return self.ativo and self.rect.collidepoint(pos)
    
    def atualizar_hover(self, pos):
        self.cor_atual = self.cor_hover if self.rect.collidepoint(pos) else self.cor_normal

class ContadorAcelerado:
    def __init__(self):
        self.valor = 0
        self.velocidade = 1.0  # segundos entre incrementos
        self.velocidade_base = 1.0
        self.velocidade_minima = 0.05  # velocidade máxima (20 incrementos/segundo)
        self.fator_aceleracao = 0.9  # reduz 10% do tempo a cada clique
        self.contando = False
        self.ultimo_tempo = 0
        self.incremento = 1
    
    def atualizar(self):
        agora = time.time()
        if self.contando and agora - self.ultimo_tempo >= self.velocidade:
            self.valor += self.incremento
            self.ultimo_tempo = agora
    
    def iniciar(self):
        if not self.contando:
            self.contando = True
            self.ultimo_tempo = time.time()
            self.velocidade = self.velocidade_base  # Reseta para velocidade inicial
    
    def parar(self):
        self.contando = False
    
    def resetar(self):
        self.valor = 0
        self.contando = False
        self.velocidade = self.velocidade_base
    
    def acelerar(self):
        nova_velocidade = self.velocidade * self.fator_aceleracao
        if nova_velocidade >= self.velocidade_minima:
            self.velocidade = nova_velocidade
        else:
            self.velocidade = self.velocidade_minima
    
    def definir_velocidade_base(self, nova_velocidade):
        if 0.05 <= nova_velocidade <= 10:
            self.velocidade_base = nova_velocidade
            if not self.contando:
                self.velocidade = nova_velocidade
    
    def definir_incremento(self, valor):
        self.incremento = valor

# Criação dos elementos
contador = ContadorAcelerado()

# Botões
botao_start = Botao(100, 400, 150, 60, "Start")
botao_stop = Botao(300, 400, 150, 60, "Stop", VERMELHO)
botao_reset = Botao(500, 400, 150, 60, "Reset", CINZA_ESCURO)
botao_acelerar = Botao(300, 500, 200, 60, "Acelerar!", AMARELO)

# Caixa de texto para velocidade inicial
caixa_velocidade = pygame.Rect(250, 300, 100, 40)
texto_velocidade = ""
editando_velocidade = False

# Caixa de texto para incremento
caixa_incremento = pygame.Rect(250, 200, 100, 40)
texto_incremento = "1"
editando_incremento = False

# Loop principal
relogio = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for evento in pygame.event.get():
        if evento.type == QUIT:
            running = False
        
        if evento.type == MOUSEBUTTONDOWN:
            # Verifica cliques nos botões
            if botao_start.verificar_clique(evento.pos):
                contador.iniciar()
            elif botao_stop.verificar_clique(evento.pos):
                contador.parar()
            elif botao_reset.verificar_clique(evento.pos):
                contador.resetar()
            elif botao_acelerar.verificar_clique(evento.pos) and contador.contando:
                contador.acelerar()
            
            # Verifica cliques nas caixas de texto
            editando_velocidade = caixa_velocidade.collidepoint(evento.pos)
            editando_incremento = caixa_incremento.collidepoint(evento.pos)
            
            # Se clicou fora, para de editar
            if not (caixa_velocidade.collidepoint(evento.pos) or 
                   caixa_incremento.collidepoint(evento.pos)):
                editando_velocidade = False
                editando_incremento = False
        
        if evento.type == KEYDOWN:
            if editando_velocidade:
                if evento.key == K_RETURN:
                    try:
                        nova_velocidade = float(texto_velocidade)
                        contador.definir_velocidade_base(nova_velocidade)
                        editando_velocidade = False
                    except ValueError:
                        pass
                elif evento.key == K_BACKSPACE:
                    texto_velocidade = texto_velocidade[:-1]
                elif evento.unicode.isdigit() or evento.unicode in ('.', '-'):
                    texto_velocidade += evento.unicode
            
            elif editando_incremento:
                if evento.key == K_RETURN:
                    try:
                        novo_incremento = int(texto_incremento)
                        contador.definir_incremento(novo_incremento)
                        editando_incremento = False
                    except ValueError:
                        pass
                elif evento.key == K_BACKSPACE:
                    texto_incremento = texto_incremento[:-1]
                elif evento.unicode.isdigit() or evento.unicode == '-':
                    texto_incremento += evento.unicode
    
    # Atualiza o contador
    contador.atualizar()
    
    # Atualiza estado dos botões
    botao_start.atualizar_hover(mouse_pos)
    botao_stop.atualizar_hover(mouse_pos)
    botao_reset.atualizar_hover(mouse_pos)
    botao_acelerar.atualizar_hover(mouse_pos)
    
    # Desenho
    tela.fill(BRANCO)
    
    # Desenha o valor do contador
    texto_contador = fonte_grande.render(str(contador.valor), True, PRETO)
    tela.blit(texto_contador, (
        LARGURA // 2 - texto_contador.get_width() // 2,
        50
    ))
    
    # Desenha botões
    botao_start.desenhar(tela)
    botao_stop.desenhar(tela)
    botao_reset.desenhar(tela)
    botao_acelerar.desenhar(tela)
    
    # Desenha caixa de velocidade
    pygame.draw.rect(tela, BRANCO, caixa_velocidade)
    pygame.draw.rect(tela, PRETO, caixa_velocidade, 2)
    if editando_velocidade:
        texto_caixa = fonte_media.render(texto_velocidade, True, PRETO)
        # Cursor piscante
        if int(time.time() * 2) % 2 == 0:
            pygame.draw.line(tela, PRETO, 
                           (caixa_velocidade.x + 10 + texto_caixa.get_width(), caixa_velocidade.y + 10),
                           (caixa_velocidade.x + 10 + texto_caixa.get_width(), caixa_velocidade.y + 30), 2)
    else:
        texto_caixa = fonte_media.render(f"{contador.velocidade_base:.1f}", True, PRETO)
    tela.blit(texto_caixa, (caixa_velocidade.x + 10, caixa_velocidade.y + 5))
    
    # Rótulo velocidade
    texto_rotulo_vel = fonte_pequena.render("Velocidade Inicial (segundos):", True, PRETO)
    tela.blit(texto_rotulo_vel, (50, 310))
    
    # Desenha caixa de incremento
    pygame.draw.rect(tela, BRANCO, caixa_incremento)
    pygame.draw.rect(tela, PRETO, caixa_incremento, 2)
    if editando_incremento:
        texto_caixa_inc = fonte_media.render(texto_incremento, True, PRETO)
        # Cursor piscante
        if int(time.time() * 2) % 2 == 0:
            pygame.draw.line(tela, PRETO, 
                           (caixa_incremento.x + 10 + texto_caixa_inc.get_width(), caixa_incremento.y + 10),
                           (caixa_incremento.x + 10 + texto_caixa_inc.get_width(), caixa_incremento.y + 30), 2)
    else:
        texto_caixa_inc = fonte_media.render(str(contador.incremento), True, PRETO)
    tela.blit(texto_caixa_inc, (caixa_incremento.x + 10, caixa_incremento.y + 5))
    
    # Rótulo incremento
    texto_rotulo_inc = fonte_pequena.render("Incremento:", True, PRETO)
    tela.blit(texto_rotulo_inc, (50, 210))
    
    # Mostra velocidade atual
    texto_vel_atual = fonte_pequena.render(
        f"Velocidade atual: {1/contador.velocidade:.1f} incrementos/segundo" if contador.velocidade > 0 else "Velocidade máxima",
        True, PRETO)
    tela.blit(texto_vel_atual, (400, 350))
    
    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
sys.exit()