import pygame
import math
import json
import os
import sys

# --- CONFIGURAÇÕES GERAIS ---
WIDTH, HEIGHT = 1200, 800
FPS = 60
PANEL_WIDTH = 450
BG_COLOR = (5, 5, 12)
PANEL_COLOR = (18, 18, 28)
TEXT_COLOR = (220, 220, 230)

# --- CARREGAR DADOS DO JSON ---
json_path = 'dados_celestes.json'
if not os.path.exists(json_path):
    print(f"Erro: O arquivo '{json_path}' não foi encontrado.")
    sys.exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    dados_celestes = json.load(f)

STARS_DATA = dados_celestes['categorias']
SPECIFIC_STARS = dados_celestes['corpos']

class StarApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Planetário Estelar e Extremo Completo")
        self.clock = pygame.time.Clock()
        self.f_s = pygame.font.SysFont("Segoe UI", 16)
        self.f_m = pygame.font.SysFont("Segoe UI", 20)
        self.f_b = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.f_h = pygame.font.SysFont("Segoe UI", 32, bold=True)
        
        self.cat_idx = 0
        self.star_idx = 0
        self.zoom = 1.0
        self.scroll_y = 0
        self.cat_open = False
        self.star_open = False
        self.pulse = 0
        self.running = True
        
        self.load_star()

    def load_star(self):
        cat_name = STARS_DATA[self.cat_idx]["nome"]
        try:
            self.curr_data = SPECIFIC_STARS[cat_name][self.star_idx]
        except (KeyError, IndexError):
            self.curr_data = {"nome": "Sem dados", "temp": "N/A", "cur": "Registro ausente.", "planetas": []}
            
        self.planets = []
        for p in self.curr_data.get("planetas", []):
            self.planets.append({
                "n": p["n"], "d": p["d"], "s": p["s"], "r": p["r"],
                "a": math.pi * 2 * (p["d"] * 0.05)
            })
        self.scroll_y = 0

    def draw_glow_surface(self, x, y, radius, color, layers=5):
        """Helper para desenhar um brilho circular difuso sob o objeto"""
        for i in range(layers, 0, -1):
            alpha = int(25 // i)
            s = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (radius * 2, radius * 2), radius + (i * 15))
            self.screen.blit(s, (x - radius * 2, y - radius * 2))

    def draw_black_hole(self, x, y, r, disk_color):
        disk_color = tuple(disk_color)
        p_val = (math.sin(self.pulse) + 1) / 2 # Pulsação 0-1
        
        # 1. Brilho Difuso (Glow) de fundo para o sistema
        self.draw_glow_surface(x, y, int(r * 2), disk_color, layers=8)

        # 2. Halo da Lente Gravitacional (Traseiro)
        halo_r = int(r * (2.5 + p_val * 0.2))
        halo_rect = pygame.Rect(x - halo_r, y - halo_r, halo_r * 2, halo_r * 2)
        pygame.draw.ellipse(self.screen, disk_color, halo_rect, max(2, int(r * 0.3)))
        
        # Dimensões do disco
        front_w = int(r * 6.5)
        front_h = int(r * (0.8 + p_val * 0.15))
        front_rect = pygame.Rect(x - front_w // 2, y - front_h // 2, front_w, front_h)
        core_w = int(r * 5.5)
        core_h = int(r * (0.4 + p_val * 0.05))
        core_rect = pygame.Rect(x - core_w // 2, y - core_h // 2, core_w, core_h)
        
        # 3. Parte traseira do disco de acreção
        pygame.draw.ellipse(self.screen, disk_color, front_rect, max(2, int(r * 0.15)))
        pygame.draw.ellipse(self.screen, (255, 255, 255), core_rect, max(1, int(r * 0.08)))
        
        # 4. Horizonte de Eventos
        pygame.draw.circle(self.screen, (0, 0, 0), (x, y), int(r))
        pygame.draw.circle(self.screen, disk_color, (x, y), int(r), 1)
        
        # 5. Parte frontal do disco de acreção (com Clip)
        orig_clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(0, int(y), WIDTH, HEIGHT - int(y)))
        pygame.draw.ellipse(self.screen, disk_color, front_rect, max(2, int(r * 0.15)))
        pygame.draw.ellipse(self.screen, (255, 255, 255), core_rect, max(1, int(r * 0.08)))
        self.screen.set_clip(orig_clip)

    def draw_supernova(self, x, y, r, base_color, seed):
        base_color = tuple(base_color)
        p_glow = (math.sin(self.pulse * 0.5) + 1) / 2
        
        # 1. Brilho Difuso (Glow) de fundo
        self.draw_glow_surface(x, y, int(r * 2.5), base_color, layers=10)

        s = pygame.Surface((r*8, r*8), pygame.SRCALPHA)
        center = (r*4, r*4)
        
        # Camadas amorfas
        layers = [
            (int(30 + 40 * p_glow), 2.2), 
            (int(60 + 50 * p_glow), 1.6), 
            (int(120 + 60 * p_glow), 1.1), 
            (230, 0.6) 
        ]

        for alpha, scale in layers:
            points = []
            for angle in range(0, 360, 10):
                rad = math.radians(angle)
                noise = math.sin(rad * (3 + seed % 4)) * 0.3 + math.cos(rad * (5 + seed % 3)) * 0.2
                current_r = r * scale * (1 + noise)
                points.append((center[0] + math.cos(rad)*current_r, center[1] + math.sin(rad)*current_r))
            pygame.draw.polygon(s, (*base_color, alpha), points)
            
        self.screen.blit(s, (x - r*4, y - r*4))

    def draw_star_visual(self, x, y):
        self.pulse += 0.05
        cat = STARS_DATA[self.cat_idx]
        r = cat["tamanho_rel"] * self.zoom
        cor_base = tuple(cat["cor"])
        
        if "Buraco Negro" in cat["nome"]:
            disk_color = self.curr_data.get("cor_disco", [200, 150, 255])
            self.draw_black_hole(x, y, r, disk_color)
            
        elif cat["nome"] == "Supernova":
            sn_color = self.curr_data.get("cor_base", [255, 200, 100])
            seed = self.curr_data.get("seed", 1)
            self.draw_supernova(x, y, r, sn_color, seed)
            
        else: # Estrelas Normais
            dynamic_r = r + math.sin(self.pulse) * (r * 0.04)
            self.draw_glow_surface(x, y, dynamic_r, cor_base, layers=7)
            pygame.draw.circle(self.screen, cor_base, (x, y), int(dynamic_r))

    def draw_scene(self):
        cx, cy = (WIDTH + PANEL_WIDTH) // 2, HEIGHT // 2
        y_mod = 0.3
        
        for p in self.planets:
            r_rect = pygame.Rect(cx - p["d"]*self.zoom, cy - p["d"]*y_mod*self.zoom, p["d"]*2*self.zoom, p["d"]*2*y_mod*self.zoom)
            pygame.draw.ellipse(self.screen, (45, 45, 70), r_rect, 1)

        for p in self.planets:
            p["a"] += p["s"]
            px = cx + math.cos(p["a"]) * p["d"] * self.zoom
            py = cy + math.sin(p["a"]) * p["d"] * y_mod * self.zoom
            if math.sin(p["a"]) < 0:
                pygame.draw.circle(self.screen, (140, 140, 150), (int(px), int(py)), p["r"])

        self.draw_star_visual(cx, cy)

        for p in self.planets:
            px = cx + math.cos(p["a"]) * p["d"] * self.zoom
            py = cy + math.sin(p["a"]) * p["d"] * y_mod * self.zoom
            if math.sin(p["a"]) >= 0:
                pygame.draw.circle(self.screen, (210, 210, 220), (int(px), int(py)), p["r"])
                lbl = self.f_s.render(p["n"], True, (255, 255, 255))
                txt_bg = pygame.Surface((lbl.get_width() + 4, lbl.get_height()), pygame.SRCALPHA)
                txt_bg.fill((0, 0, 0, 150))
                self.screen.blit(txt_bg, (px + 8, py - 8))
                self.screen.blit(lbl, (px + 10, py - 8))

    def draw_ui(self):
        pygame.draw.rect(self.screen, PANEL_COLOR, (0, 0, PANEL_WIDTH, HEIGHT))
        self.draw_dd(20, 20, "CATEGORIA", STARS_DATA[self.cat_idx]["nome"], self.cat_open)
        self.draw_dd(20, 80, "OBJETO", self.curr_data["nome"], self.star_open)
        y_n = 140
        self.draw_btn("<<", 20, y_n, 55)
        self.draw_btn("<", 85, y_n, 55)
        self.draw_btn(">", 150, y_n, 55)
        self.draw_btn(">>", 215, y_n, 55)
        self.draw_btn("+ Zoom", 300, y_n, 65)
        self.draw_btn("- Zoom", 375, y_n, 65)
        
        area = pygame.Rect(20, 210, PANEL_WIDTH - 40, HEIGHT - 230)
        surf = pygame.Surface((area.width, 1800), pygame.SRCALPHA)
        y_p = 0
        lines = [
            (f"{STARS_DATA[self.cat_idx]['nome']}", self.f_h, (120, 180, 255)),
            (STARS_DATA[self.cat_idx]["info"], self.f_m, TEXT_COLOR),
            ("", self.f_s, TEXT_COLOR),
            (f"Objeto: {self.curr_data['nome']}", self.f_b, (255, 230, 120)),
            (f"Temperatura: {self.curr_data['temp']}", self.f_m, TEXT_COLOR),
            ("Nota:", self.f_b, TEXT_COLOR),
            (self.curr_data["cur"], self.f_m, TEXT_COLOR),
            ("", self.f_s, TEXT_COLOR),
            ("CORPO(S) EM ÓRBITA:", self.f_b, (140, 255, 140))
        ]
        if not self.planets: lines.append(("Nenhum corpo significativo em órbita.", self.f_m, (150, 150, 160)))
        else:
            for p in self.planets: lines.append((f"• {p['n']}", self.f_m, TEXT_COLOR))

        for text, font, col in lines:
            words = text.split(' ')
            line = ""
            for w in words:
                if font.size(line + w)[0] < area.width: line += w + " "
                else:
                    surf.blit(font.render(line, True, col), (0, y_p)); y_p += 28; line = w + " "
            surf.blit(font.render(line, True, col), (0, y_p)); y_p += 32
        self.screen.blit(surf, (20, 210), (0, self.scroll_y, area.width, area.height))

        if self.cat_open: self.draw_list(20, 60, [s["nome"] for s in STARS_DATA])
        cat_name = STARS_DATA[self.cat_idx]["nome"]
        if self.star_open and cat_name in SPECIFIC_STARS:
            self.draw_list(20, 120, [s["nome"] for s in SPECIFIC_STARS[cat_name]])

    def draw_dd(self, x, y, lbl, val, open):
        pygame.draw.rect(self.screen, (45, 45, 65), (x, y, 400, 40))
        pygame.draw.rect(self.screen, (100, 100, 160), (x, y, 400, 40), 1)
        self.screen.blit(self.f_m.render(f"{lbl}: {val}", True, (255, 255, 255)), (x+10, y+8))

    def draw_btn(self, t, x, y, w):
        pygame.draw.rect(self.screen, (60, 60, 90), (x, y, w, 35))
        txt = self.f_s.render(t, True, (255, 255, 255))
        self.screen.blit(txt, (x + (w - txt.get_width())//2, y+7))

    def draw_list(self, x, y, items):
        h = len(items) * 30
        pygame.draw.rect(self.screen, (30, 30, 45), (x, y, 400, h))
        for i, item in enumerate(items):
            rect = pygame.Rect(x, y + i*30, 400, 30)
            if rect.collidepoint(pygame.mouse.get_pos()): pygame.draw.rect(self.screen, (70, 70, 110), rect)
            self.screen.blit(self.f_s.render(item, True, (255, 255, 255)), (x+10, y+i*30+5))

    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: self.running = False
                if e.type == pygame.MOUSEWHEEL: self.scroll_y = max(0, self.scroll_y - e.y * 30)
                if e.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = e.pos
                    handled = False
                    if self.cat_open:
                        for i in range(len(STARS_DATA)):
                            if pygame.Rect(20, 60 + i * 30, 400, 30).collidepoint(mx, my):
                                self.cat_idx, self.star_idx, self.cat_open = i, 0, False
                                self.load_star(); handled = True; break
                        if not handled: 
                            self.cat_open = False
                            if pygame.Rect(20, 20, 400, 40).collidepoint(mx, my): handled = True
                    elif self.star_open:
                        cat_name = STARS_DATA[self.cat_idx]["nome"]
                        if cat_name in SPECIFIC_STARS:
                            items = SPECIFIC_STARS[cat_name]
                            for i in range(len(items)):
                                if pygame.Rect(20, 120 + i * 30, 400, 30).collidepoint(mx, my):
                                    self.star_idx, self.star_open = i, False
                                    self.load_star(); handled = True; break
                        if not handled:
                            self.star_open = False
                            if pygame.Rect(20, 80, 400, 40).collidepoint(mx, my): handled = True
                    if not handled:
                        if pygame.Rect(20, 20, 400, 40).collidepoint(mx, my): self.cat_open, self.star_open = True, False
                        elif pygame.Rect(20, 80, 400, 40).collidepoint(mx, my): self.star_open, self.cat_open = True, False
                        elif 140 <= my <= 175:
                            if 20 <= mx <= 75: self.cat_idx = max(0, self.cat_idx - 5)
                            elif 85 <= mx <= 140: self.cat_idx = max(0, self.cat_idx - 1)
                            elif 150 <= mx <= 205: self.cat_idx = min(len(STARS_DATA)-1, self.cat_idx + 1)
                            elif 215 <= mx <= 270: self.cat_idx = min(len(STARS_DATA)-1, self.cat_idx + 5)
                            elif 300 <= mx <= 365: self.zoom *= 1.2
                            elif 375 <= mx <= 440: self.zoom /= 1.2
                            self.star_idx = 0; self.load_star()

            self.screen.fill(BG_COLOR)
            self.draw_scene()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    StarApp().run()