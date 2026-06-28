import pygame
import json
import os
import sys
import math
import random

# Inicialização do Pygame
pygame.init()

# --- CONSTANTES ---
FPS = 60
TILE_SIZE = 64
UI_WIDTH = 250
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Cores
C_BG = (30, 30, 30)
C_GRID = (50, 50, 50)
C_UI_BG = (40, 40, 45)
C_UI_PANEL = (60, 60, 65)
C_TEXT = (220, 220, 220)
C_HIGHLIGHT = (100, 150, 255)
C_ERROR = (255, 100, 100)

# Estados do Jogo
MODO_CONSTRUCAO = 0
MODO_JOGAR = 1
MODO_AUTO = 2

# Direções: 0=Cima, 1=Direita, 2=Baixo, 3=Esquerda
# Define quais bordas do tile são "abertas" na rotação 0
PECAS_DEF = {
    'inicio':     {'conexoes': [0, 1, 2, 3], 'cor': (50, 200, 50)},
    'fim':        {'conexoes': [0, 1, 2, 3], 'cor': (200, 50, 50)},
    'reta':       {'conexoes': [0, 2],       'cor': (150, 150, 150)},
    'curva':      {'conexoes': [1, 2],       'cor': (150, 150, 150)},
    'bifurcacao': {'conexoes': [1, 2, 3],    'cor': (150, 150, 150)},
    'portal':     {'conexoes': [0, 1, 2, 3], 'cor': (150, 50, 200)},
    'chave':      {'conexoes': [0, 1, 2, 3], 'cor': (255, 215, 0)},
    'porta':      {'conexoes': [0, 2],       'cor': (139, 69, 19)},
    'laser':      {'conexoes': [1, 3],       'cor': (255, 0, 0)},
    'botao':      {'conexoes': [0, 1, 2, 3], 'cor': (50, 150, 255)},
}

# --- CLASSES AUXILIARES ---
class Peca:
    def __init__(self, tipo, rotacao=0):
        self.tipo = tipo
        self.rotacao = rotacao # 0, 1, 2, 3 (x 90 graus)
        self.ativa = True # Para chaves e portas
        
    def get_conexoes(self):
        conexoes_originais = PECAS_DEF[self.tipo]['conexoes']
        return [(c + self.rotacao) % 4 for c in conexoes_originais]
        
    def to_dict(self):
        return {'tipo': self.tipo, 'rotacao': self.rotacao}
        
    @classmethod
    def from_dict(cls, data):
        return cls(data['tipo'], data['rotacao'])

class Personagem:
    def __init__(self, x, y, tipo_animal, is_auto=False):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.tipo = tipo_animal # 'gato' ou 'cachorro'
        self.chaves = 0
        self.is_auto = is_auto
        self.movendo = False
        self.dir_x = 0
        self.dir_y = 0
        self.velocidade = 4
        self.vivo = True
        self.ganhou = False
        
        # IA simples para modo auto
        self.ultima_pos = None

    def update(self, jogo):
        if not self.vivo or self.ganhou: return

        # Interpolação de movimento contínuo
        if self.movendo:
            alvo_x = self.grid_x * TILE_SIZE
            alvo_y = self.grid_y * TILE_SIZE
            
            dx = alvo_x - self.pixel_x
            dy = alvo_y - self.pixel_y
            
            dist = math.hypot(dx, dy)
            if dist < self.velocidade:
                self.pixel_x = alvo_x
                self.pixel_y = alvo_y
                self.movendo = False
                jogo.verificar_interacoes(self)
            else:
                self.pixel_x += (dx / dist) * self.velocidade
                self.pixel_y += (dy / dist) * self.velocidade
        
        elif self.is_auto:
            self.pensar_ia(jogo)

    def pensar_ia(self, jogo):
        direcoes = [(0, -1, 0), (1, 0, 1), (0, 1, 2), (-1, 0, 3)] # dx, dy, direcao_padrao
        possiveis = []
        
        for dx, dy, d_out in direcoes:
            if jogo.pode_mover(self.grid_x, self.grid_y, dx, dy):
                nx, ny = self.grid_x + dx, self.grid_y + dy
                if (nx, ny) != self.ultima_pos:
                    possiveis.append((dx, dy))
        
        if not possiveis: # Beco sem saída, volta
            for dx, dy, d_out in direcoes:
                if jogo.pode_mover(self.grid_x, self.grid_y, dx, dy):
                    possiveis.append((dx, dy))
                    
        if possiveis:
            escolha = random.choice(possiveis)
            self.ultima_pos = (self.grid_x, self.grid_y)
            self.mover(escolha[0], escolha[1], jogo)

    def mover(self, dx, dy, jogo):
        if self.movendo or not self.vivo or self.ganhou: return
        if jogo.pode_mover(self.grid_x, self.grid_y, dx, dy, self):
            self.grid_x += dx
            self.grid_y += dy
            self.movendo = True

    def desenhar(self, surface, camera_x, camera_y):
        if not self.vivo: return
        px = self.pixel_x - camera_x
        py = self.pixel_y - camera_y
        
        centro = (int(px + TILE_SIZE//2), int(py + TILE_SIZE//2))
        
        if self.tipo == 'gato':
            pygame.draw.circle(surface, (255, 140, 0), centro, TILE_SIZE//3)
            # Orelhas
            pygame.draw.polygon(surface, (255, 140, 0), [
                (centro[0]-15, centro[1]-10), (centro[0]-5, centro[1]-25), (centro[0], centro[1]-15)
            ])
            pygame.draw.polygon(surface, (255, 140, 0), [
                (centro[0]+15, centro[1]-10), (centro[0]+5, centro[1]-25), (centro[0], centro[1]-15)
            ])
        else: # Cachorro
            pygame.draw.circle(surface, (139, 69, 19), centro, TILE_SIZE//3)
            # Orelhas caídas
            pygame.draw.ellipse(surface, (100, 50, 10), (centro[0]-20, centro[1]-10, 15, 25))
            pygame.draw.ellipse(surface, (100, 50, 10), (centro[0]+5, centro[1]-10, 15, 25))

# --- UI SIMPLES ---
class Botao:
    def __init__(self, x, y, w, h, texto, valor=None, toggle=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.valor = valor
        self.toggle = toggle
        self.ativo = False
        
    def desenhar(self, surface, fonte):
        cor = C_HIGHLIGHT if self.ativo else C_UI_PANEL
        pygame.draw.rect(surface, cor, self.rect, border_radius=5)
        pygame.draw.rect(surface, (200,200,200), self.rect, 2, border_radius=5)
        
        txt_surf = fonte.render(self.texto, True, C_TEXT)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

# --- CLASSE PRINCIPAL DO JOGO ---
class JogoLabirinto:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Criador de Labirintos")
        self.clock = pygame.time.Clock()
        self.fonte = pygame.font.SysFont("Arial", 16, bold=True)
        self.fonte_grande = pygame.font.SysFont("Arial", 32, bold=True)
        
        self.fullscreen = False
        
        # Matriz Infinita
        self.grid = {} # {(x, y): Peca}
        
        # Centralizar a câmera inicialmente no bloco (0, 0) da área jogável
        target_x = UI_WIDTH + (SCREEN_WIDTH - UI_WIDTH) // 2 - TILE_SIZE // 2
        target_y = SCREEN_HEIGHT // 2 - TILE_SIZE // 2
        self.cam_x = 0 - target_x
        self.cam_y = 0 - target_y
        
        # Estado
        self.modo = MODO_CONSTRUCAO
        self.peca_selecionada = 'reta'
        self.rotacao_atual = 0
        self.modo_exclusao = False
        self.animal_selecionado = 'gato'
        self.mensagem_erro = ""
        self.tempo_erro = 0
        
        # Elementos de Jogo
        self.personagens = []
        self.portais = [] # Lista de posições de portais
        self.lasers = []
        self.botoes = []
        
        self.setup_ui()

    def setup_ui(self):
        self.botoes_ui = []
        y = 20
        # Ações Gerais
        self.btn_salvar = Botao(20, y, 210, 30, "Salvar JSON"); y+=40
        self.btn_carregar = Botao(20, y, 210, 30, "Carregar JSON"); y+=50
        
        # Modos
        self.btn_jogar = Botao(20, y, 100, 40, "JOGAR", toggle=True); 
        self.btn_auto = Botao(130, y, 100, 40, "AUTO", toggle=True); y+=50
        self.btn_parar = Botao(20, y, 210, 30, "PARAR / EDITAR"); y+=50
        
        # Personagem
        y += 10
        self.btn_gato = Botao(20, y, 100, 30, "Gato", toggle=True); self.btn_gato.ativo = True
        self.btn_cachorro = Botao(130, y, 100, 30, "Cachorro", toggle=True); y+=50
        
        # Ferramentas
        y += 10
        self.btn_inserir = Botao(20, y, 100, 30, "Inserir", toggle=True); self.btn_inserir.ativo = True
        self.btn_apagar = Botao(130, y, 100, 30, "Apagar", toggle=True); y+=50
        
        # Peças
        self.botoes_pecas = []
        px, py = 20, y
        for chave in PECAS_DEF.keys():
            btn = Botao(px, py, 100, 30, chave.capitalize(), valor=chave, toggle=True)
            if chave == 'reta': btn.ativo = True
            self.botoes_pecas.append(btn)
            px += 110
            if px > 150:
                px = 20
                py += 40

        # Controles de Câmera UI (Setas e Centro)
        py += 15 # Espaçamento após os blocos
        self.btn_cam_up = Botao(105, py, 40, 40, "^")
        self.btn_cam_left = Botao(60, py + 45, 40, 40, "<")
        self.btn_cam_center = Botao(105, py + 45, 40, 40, "O")
        self.btn_cam_right = Botao(150, py + 45, 40, 40, ">")
        self.btn_cam_down = Botao(105, py + 90, 40, 40, "v")

    def mostrar_erro(self, msg):
        self.mensagem_erro = msg
        self.tempo_erro = pygame.time.get_ticks() + 3000

    def validar_labirinto(self):
        inicios = 0
        finais = 0
        portais = 0
        
        self.portais = []
        self.lasers = []
        self.botoes = []
        
        # Coletar dados
        for pos, peca in self.grid.items():
            if peca.tipo == 'inicio': inicios += 1
            if peca.tipo == 'fim': finais += 1
            if peca.tipo == 'portal': 
                portais += 1
                self.portais.append(pos)
            if peca.tipo == 'laser': self.lasers.append(pos)
            if peca.tipo == 'botao': self.botoes.append(pos)
            
            # Resetar estados (portas, etc)
            peca.ativa = True
            
        # Ordenar para garantir pareamento previsível (topo para baixo, esq para dir)
        self.portais.sort(key=lambda p: (p[1], p[0]))
        self.lasers.sort(key=lambda p: (p[1], p[0]))
        self.botoes.sort(key=lambda p: (p[1], p[0]))

        if inicios != 1:
            self.mostrar_erro("Erro: Deve haver EXATAMENTE 1 Início!")
            return False
        if finais < 1:
            self.mostrar_erro("Erro: Deve haver pelo menos 1 Fim!")
            return False
        if portais % 2 != 0:
            self.mostrar_erro("Erro: Número de portais deve ser par!")
            return False
            
        return True
        
    def centralizar_camera(self):
        # Encontra o centro da área visual do labirinto
        target_x = UI_WIDTH + (SCREEN_WIDTH - UI_WIDTH) // 2 - TILE_SIZE // 2
        target_y = SCREEN_HEIGHT // 2 - TILE_SIZE // 2
        
        # Tenta encontrar a peça de início
        for pos, peca in self.grid.items():
            if peca.tipo == 'inicio':
                self.cam_x = (pos[0] * TILE_SIZE) - target_x
                self.cam_y = (pos[1] * TILE_SIZE) - target_y
                return
                
        # Se não houver início, volta para o (0,0) original
        self.cam_x = 0 - target_x
        self.cam_y = 0 - target_y

    def iniciar_jogo(self, automatico=False):
        if not self.validar_labirinto(): return
        
        self.modo = MODO_AUTO if automatico else MODO_JOGAR
        self.personagens = []
        
        # Achar inicio
        pos_inicio = None
        for pos, peca in self.grid.items():
            if peca.tipo == 'inicio':
                pos_inicio = pos
                break
                
        if automatico:
            # Spawna 5 bots para testar caminhos
            for _ in range(5):
                self.personagens.append(Personagem(pos_inicio[0], pos_inicio[1], self.animal_selecionado, is_auto=True))
        else:
            self.personagens.append(Personagem(pos_inicio[0], pos_inicio[1], self.animal_selecionado))

    def parar_jogo(self):
        self.modo = MODO_CONSTRUCAO
        self.personagens = []
        for peca in self.grid.values():
            peca.ativa = True # Reseta portas e chaves

    def pode_mover(self, x, y, dx, dy, personagem=None):
        pos_atual = (x, y)
        pos_alvo = (x + dx, y + dy)
        
        if pos_atual not in self.grid or pos_alvo not in self.grid:
            return False
            
        peca_atual = self.grid[pos_atual]
        peca_alvo = self.grid[pos_alvo]
        
        dir_saida = -1
        if dy == -1: dir_saida = 0
        elif dx == 1: dir_saida = 1
        elif dy == 1: dir_saida = 2
        elif dx == -1: dir_saida = 3
        
        dir_entrada = (dir_saida + 2) % 4
        
        # Verifica se o tile atual permite sair e o alvo permite entrar
        if dir_saida not in peca_atual.get_conexoes() or dir_entrada not in peca_alvo.get_conexoes():
            return False
            
        # Lógica de Portas
        if peca_alvo.tipo == 'porta' and peca_alvo.ativa:
            if personagem and personagem.chaves > 0:
                return True # Vai consumir chave no 'verificar_interacoes'
            return False # Porta trancada
            
        return True

    def verificar_interacoes(self, personagem):
        pos = (personagem.grid_x, personagem.grid_y)
        if pos not in self.grid: return
        
        peca = self.grid[pos]
        
        if peca.tipo == 'chave' and peca.ativa:
            personagem.chaves += 1
            peca.ativa = False
            
        elif peca.tipo == 'porta' and peca.ativa:
            if personagem.chaves > 0:
                personagem.chaves -= 1
                peca.ativa = False
                
        elif peca.tipo == 'laser' and peca.ativa:
            # Mata/Reseta
            personagem.vivo = False
            if not personagem.is_auto:
                self.iniciar_jogo() # Reinicia se for o jogador
                
        elif peca.tipo == 'botao':
            # Acha o index deste botão
            try:
                idx = self.botoes.index(pos)
                if idx < len(self.lasers):
                    pos_laser = self.lasers[idx]
                    self.grid[pos_laser].ativa = False
            except ValueError: pass
            
        elif peca.tipo == 'portal':
            try:
                idx = self.portais.index(pos)
                par_idx = idx + 1 if idx % 2 == 0 else idx - 1
                destino = self.portais[par_idx]
                personagem.grid_x = destino[0]
                personagem.grid_y = destino[1]
                personagem.pixel_x = destino[0] * TILE_SIZE
                personagem.pixel_y = destino[1] * TILE_SIZE
            except ValueError: pass
            
        elif peca.tipo == 'fim':
            personagem.ganhou = True

    def salvar(self):
        dados = []
        for (x, y), peca in self.grid.items():
            d = peca.to_dict()
            d['x'] = x
            d['y'] = y
            dados.append(d)
        with open('labirinto_save.json', 'w') as f:
            json.dump(dados, f)
        self.mostrar_erro("Salvo com sucesso!") # Usando a função de erro como alerta
            
    def carregar(self):
        if not os.path.exists('labirinto_save.json'):
            self.mostrar_erro("Arquivo não encontrado!")
            return
        with open('labirinto_save.json', 'r') as f:
            dados = json.load(f)
        self.grid = {}
        for d in dados:
            self.grid[(d['x'], d['y'])] = Peca(d['tipo'], d['rotacao'])
        self.mostrar_erro("Carregado com sucesso!")

    def desenhar_peca_processual(self, surface, peca, rect):
        cx, cy = rect.center
        t = TILE_SIZE
        mt = t // 2
        espessura = 10
        
        cor_base = PECAS_DEF[peca.tipo]['cor']
        
        # Fundo padrão
        pygame.draw.rect(surface, (40, 40, 40), rect)
        pygame.draw.rect(surface, (60, 60, 60), rect, 1)

        conexoes = peca.get_conexoes()
        
        # Desenha os caminhos (retângulos ligando o centro à borda)
        caminho_cor = (200, 200, 200)
        
        # Pinta o centro
        if conexoes and peca.tipo not in ['inicio', 'fim', 'portal']:
            pygame.draw.rect(surface, caminho_cor, (cx - espessura, cy - espessura, espessura*2, espessura*2))

        for c in conexoes:
            if c == 0: pygame.draw.rect(surface, caminho_cor, (cx - espessura, rect.top, espessura*2, mt))
            if c == 1: pygame.draw.rect(surface, caminho_cor, (cx, cy - espessura, mt, espessura*2))
            if c == 2: pygame.draw.rect(surface, caminho_cor, (cx - espessura, cy, espessura*2, mt))
            if c == 3: pygame.draw.rect(surface, caminho_cor, (rect.left, cy - espessura, mt, espessura*2))

        # Detalhes específicos
        if peca.tipo == 'inicio':
            pygame.draw.rect(surface, cor_base, rect.inflate(-10, -10))
            txt = self.fonte.render("IN", True, (255,255,255))
            surface.blit(txt, txt.get_rect(center=rect.center))
            
        elif peca.tipo == 'fim':
            pygame.draw.rect(surface, cor_base, rect.inflate(-10, -10))
            txt = self.fonte.render("FIM", True, (255,255,255))
            surface.blit(txt, txt.get_rect(center=rect.center))
            
        elif peca.tipo == 'portal':
            pygame.draw.circle(surface, cor_base, (cx, cy), mt - 10)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), mt - 15, 2)
            
        elif peca.tipo == 'chave':
            if peca.ativa:
                pygame.draw.circle(surface, cor_base, (cx, cy - 5), 8)
                pygame.draw.rect(surface, cor_base, (cx - 2, cy - 5, 4, 15))
                pygame.draw.rect(surface, cor_base, (cx + 2, cy + 5, 6, 4))
                
        elif peca.tipo == 'porta':
            if peca.ativa:
                # Desenha porta fechada (bloqueia o caminho horizontal/vertical dependendo da rotação)
                if 0 in peca.get_conexoes(): # Vertical
                    pygame.draw.rect(surface, cor_base, (rect.left, cy - 5, t, 10))
                else: # Horizontal
                    pygame.draw.rect(surface, cor_base, (cx - 5, rect.top, 10, t))
            else:
                # Porta aberta (cinza transparente)
                s = pygame.Surface((t, t), pygame.SRCALPHA)
                s.fill((139, 69, 19, 50))
                surface.blit(s, rect)
                
        elif peca.tipo == 'laser':
            if peca.ativa:
                if 1 in peca.get_conexoes(): # Horizontal
                    pygame.draw.rect(surface, cor_base, (rect.left, cy - 3, t, 6))
                else: # Vertical
                    pygame.draw.rect(surface, cor_base, (cx - 3, rect.top, 6, t))
                    
        elif peca.tipo == 'botao':
            cor_btn = cor_base if peca.ativa else (100, 100, 100)
            pygame.draw.circle(surface, cor_btn, (cx, cy), 12)
            pygame.draw.circle(surface, (20,20,20), (cx, cy), 12, 2)

    def draw(self):
        self.screen.fill(C_BG)
        
        # --- ÁREA DO LABIRINTO ---
        area_labirinto = pygame.Rect(UI_WIDTH, 0, SCREEN_WIDTH - UI_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, C_BG, area_labirinto)
        
        # Desenhar Grid de fundo (Opcional, ajuda a ver o movimento)
        offset_x = -self.cam_x % TILE_SIZE
        offset_y = -self.cam_y % TILE_SIZE
        for x in range(int(offset_x) + UI_WIDTH, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, C_GRID, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(int(offset_y), SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, C_GRID, (UI_WIDTH, y), (SCREEN_WIDTH, y))

        # Desenhar Peças
        for (gx, gy), peca in self.grid.items():
            px = gx * TILE_SIZE - self.cam_x
            py = gy * TILE_SIZE - self.cam_y
            
            # Culling simples (só desenha o que tá na tela)
            if px > SCREEN_WIDTH or px + TILE_SIZE < UI_WIDTH or py > SCREEN_HEIGHT or py + TILE_SIZE < 0:
                continue
                
            rect = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)
            self.desenhar_peca_processual(self.screen, peca, rect)
            
        # Preview no mouse se estiver no modo construção
        m_x, m_y = pygame.mouse.get_pos()
        if self.modo == MODO_CONSTRUCAO and m_x > UI_WIDTH:
            gx = int((m_x + self.cam_x) // TILE_SIZE)
            gy = int((m_y + self.cam_y) // TILE_SIZE)
            px = gx * TILE_SIZE - self.cam_x
            py = gy * TILE_SIZE - self.cam_y
            rect = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)
            
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            if self.modo_exclusao:
                s.fill((255, 0, 0, 100))
            else:
                s.fill((0, 255, 0, 100))
                # Preview da peca
                peca_temp = Peca(self.peca_selecionada, self.rotacao_atual)
                self.desenhar_peca_processual(s, peca_temp, s.get_rect())
            self.screen.blit(s, rect.topleft)

        # Desenhar Personagens
        for p in self.personagens:
            p.desenhar(self.screen, self.cam_x, self.cam_y)

        # --- UI LATERAL ---
        pygame.draw.rect(self.screen, C_UI_BG, (0, 0, UI_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, (100,100,100), (UI_WIDTH, 0), (UI_WIDTH, SCREEN_HEIGHT), 2)
        
        # Titulo
        txt = self.fonte_grande.render("Labirinto", True, C_TEXT)
        self.screen.blit(txt, (20, 10))
        
        # Botões
        self.btn_salvar.desenhar(self.screen, self.fonte)
        self.btn_carregar.desenhar(self.screen, self.fonte)
        self.btn_jogar.desenhar(self.screen, self.fonte)
        self.btn_auto.desenhar(self.screen, self.fonte)
        self.btn_parar.desenhar(self.screen, self.fonte)
        self.btn_gato.desenhar(self.screen, self.fonte)
        self.btn_cachorro.desenhar(self.screen, self.fonte)
        self.btn_inserir.desenhar(self.screen, self.fonte)
        self.btn_apagar.desenhar(self.screen, self.fonte)
        
        for btn in self.botoes_pecas:
            btn.desenhar(self.screen, self.fonte)
            
        # Botões da Câmera
        self.btn_cam_up.desenhar(self.screen, self.fonte)
        self.btn_cam_left.desenhar(self.screen, self.fonte)
        self.btn_cam_center.desenhar(self.screen, self.fonte)
        self.btn_cam_right.desenhar(self.screen, self.fonte)
        self.btn_cam_down.desenhar(self.screen, self.fonte)

        # Status
        txt_rot = self.fonte.render(f"Rotação: {self.rotacao_atual * 90}° (Click Dir)", True, (200,200,100))
        self.screen.blit(txt_rot, (20, SCREEN_HEIGHT - 60))
        
        # Info Jogador (se estiver jogando)
        if self.modo == MODO_JOGAR and self.personagens:
            txt_chaves = self.fonte.render(f"Chaves: {self.personagens[0].chaves}", True, (255, 215, 0))
            self.screen.blit(txt_chaves, (SCREEN_WIDTH - 120, 20))
            if self.personagens[0].ganhou:
                txt_win = self.fonte_grande.render("VOCÊ VENCEU!", True, (50, 255, 50))
                self.screen.blit(txt_win, (SCREEN_WIDTH//2, 50))

        # Mensagem de Erro
        if pygame.time.get_ticks() < self.tempo_erro:
            cor = (50, 255, 50) if "sucesso" in self.mensagem_erro.lower() else C_ERROR
            txt_err = self.fonte.render(self.mensagem_erro, True, cor)
            self.screen.blit(txt_err, (UI_WIDTH + 20, 20))

        pygame.display.flip()

    def update(self):
        # Atualiza personagens
        if self.modo in [MODO_JOGAR, MODO_AUTO]:
            for p in self.personagens:
                p.update(self)
                
            # Câmera segue jogador no modo manual
            if self.modo == MODO_JOGAR and self.personagens:
                p = self.personagens[0]
                alvo_cam_x = p.pixel_x - (SCREEN_WIDTH + UI_WIDTH)//2 + TILE_SIZE//2
                alvo_cam_y = p.pixel_y - SCREEN_HEIGHT//2 + TILE_SIZE//2
                self.cam_x += (alvo_cam_x - self.cam_x) * 0.1
                self.cam_y += (alvo_cam_y - self.cam_y) * 0.1

    def handle_events(self):
        global SCREEN_WIDTH, SCREEN_HEIGHT
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                SCREEN_WIDTH = event.w
                SCREEN_HEIGHT = event.h
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        info = pygame.display.Info()
                        SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
                    else:
                        SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
                        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                        
                # Movimento Jogador
                if self.modo == MODO_JOGAR and self.personagens:
                    p = self.personagens[0]
                    if event.key == pygame.K_UP: p.mover(0, -1, self)
                    elif event.key == pygame.K_DOWN: p.mover(0, 1, self)
                    elif event.key == pygame.K_LEFT: p.mover(-1, 0, self)
                    elif event.key == pygame.K_RIGHT: p.mover(1, 0, self)
                    
                # Rotação com tecla
                if event.key == pygame.K_r and self.modo == MODO_CONSTRUCAO:
                    self.rotacao_atual = (self.rotacao_atual + 1) % 4

            elif event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = event.pos
                
                # Clique na UI
                if m_x <= UI_WIDTH:
                    if event.button == 1:
                        if self.btn_salvar.check_click(event.pos): self.salvar()
                        elif self.btn_carregar.check_click(event.pos): self.carregar()
                        elif self.btn_parar.check_click(event.pos): 
                            self.parar_jogo()
                            self.btn_jogar.ativo = False
                            self.btn_auto.ativo = False
                        elif self.btn_jogar.check_click(event.pos):
                            self.iniciar_jogo(automatico=False)
                            if self.modo == MODO_JOGAR:
                                self.btn_jogar.ativo = True
                                self.btn_auto.ativo = False
                        elif self.btn_auto.check_click(event.pos):
                            self.iniciar_jogo(automatico=True)
                            if self.modo == MODO_AUTO:
                                self.btn_auto.ativo = True
                                self.btn_jogar.ativo = False
                                
                        elif self.btn_gato.check_click(event.pos):
                            self.animal_selecionado = 'gato'
                            self.btn_gato.ativo = True
                            self.btn_cachorro.ativo = False
                        elif self.btn_cachorro.check_click(event.pos):
                            self.animal_selecionado = 'cachorro'
                            self.btn_cachorro.ativo = True
                            self.btn_gato.ativo = False
                            
                        elif self.btn_inserir.check_click(event.pos):
                            self.modo_exclusao = False
                            self.btn_inserir.ativo = True
                            self.btn_apagar.ativo = False
                        elif self.btn_apagar.check_click(event.pos):
                            self.modo_exclusao = True
                            self.btn_apagar.ativo = True
                            self.btn_inserir.ativo = False
                            
                        elif self.btn_cam_center.check_click(event.pos):
                            self.centralizar_camera()
                            
                        else:
                            for btn in self.botoes_pecas:
                                if btn.check_click(event.pos):
                                    self.peca_selecionada = btn.valor
                                    for b in self.botoes_pecas: b.ativo = False
                                    btn.ativo = True
                                    self.modo_exclusao = False
                                    self.btn_inserir.ativo = True
                                    self.btn_apagar.ativo = False
                
                # Clique no Labirinto
                elif m_x > UI_WIDTH:
                    if self.modo == MODO_CONSTRUCAO:
                        # Convertido explicitamente para int para evitar incompatibilidades no dicionário
                        gx = int((m_x + self.cam_x) // TILE_SIZE)
                        gy = int((m_y + self.cam_y) // TILE_SIZE)
                        
                        if event.button == 1: # Esquerdo: Colocar/Apagar (Um clique)
                            if self.modo_exclusao:
                                if (gx, gy) in self.grid:
                                    del self.grid[(gx, gy)]
                            else:
                                self.grid[(gx, gy)] = Peca(self.peca_selecionada, self.rotacao_atual)
                        elif event.button == 3: # Direito: Girar
                            self.rotacao_atual = (self.rotacao_atual + 1) % 4
                            
            # Suporte para Arrastar e Desenhar/Apagar
            elif event.type == pygame.MOUSEMOTION:
                m_x, m_y = event.pos
                
                # event.buttons[0] significa que o botão esquerdo do rato está a ser mantido premido
                if event.buttons[0] and m_x > UI_WIDTH and self.modo == MODO_CONSTRUCAO:
                    gx = int((m_x + self.cam_x) // TILE_SIZE)
                    gy = int((m_y + self.cam_y) // TILE_SIZE)
                    
                    if self.modo_exclusao:
                        if (gx, gy) in self.grid:
                            del self.grid[(gx, gy)]
                    else:
                        self.grid[(gx, gy)] = Peca(self.peca_selecionada, self.rotacao_atual)

        # Controle contínuo de rolamento de câmera
        keys = pygame.key.get_pressed()
        mouse_btns = pygame.mouse.get_pressed()
        m_pos = pygame.mouse.get_pos()
        
        if self.modo == MODO_CONSTRUCAO or self.modo == MODO_AUTO:
            cam_speed = 10
            
            # WASD ou Setas do Teclado
            if keys[pygame.K_w] or keys[pygame.K_UP]: self.cam_y -= cam_speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.cam_y += cam_speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.cam_x -= cam_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.cam_x += cam_speed
            
            # Botões Direcionais da UI (quando mantidos pressionados)
            if mouse_btns[0] and m_pos[0] <= UI_WIDTH:
                if self.btn_cam_up.check_click(m_pos): self.cam_y -= cam_speed
                if self.btn_cam_down.check_click(m_pos): self.cam_y += cam_speed
                if self.btn_cam_left.check_click(m_pos): self.cam_x -= cam_speed
                if self.btn_cam_right.check_click(m_pos): self.cam_x += cam_speed
            
            # Rolagem pelo meio do mouse (mantém existente)
            if mouse_btns[1]: 
                rel_x, rel_y = pygame.mouse.get_rel()
                self.cam_x -= rel_x
                self.cam_y -= rel_y
            else:
                pygame.mouse.get_rel() # Limpa o relativo caso não esteja arrastando

        return True

    def run(self):
        rodando = True
        while rodando:
            rodando = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    jogo = JogoLabirinto()
    jogo.run()