import pygame
import pygame_gui
import math
import random

# Initialize Pygame
pygame.init()

# Constants
MIN_WIDTH, MIN_HEIGHT = 1400, 800  # Aumentei um pouco a altura para a nova UI
FPS = 60
BACKGROUND_COLOR = (10, 10, 20)
UI_PANEL_COLOR = (30, 30, 40)
SEPARATOR_COLOR = (100, 100, 100)

# --- HELPER FUNCTIONS ---

def clean_radius(val):
    try:
        if isinstance(val, str):
            val = float(val.replace('~', '').replace('<', '').replace('>', ''))
    except:
        val = 1.0
    
    # Se o valor for muito grande, assume-se km ou terra e converte grosseiramente para escala jupiter
    if val > 1000: 
        return val / 70000.0 # Aproximado km para Jupiter Radii
    if val > 10:
        return val / 11.0 # Aproximado Earth Radii para Jupiter Radii
        
    return val

def get_color_from_desc(color_desc):
    color_desc_lower = color_desc.lower()
    rgb = (200, 200, 200) # Default grey
    if "red" in color_desc_lower: rgb = (200, 50, 50)
    elif "orange" in color_desc_lower: rgb = (255, 140, 0)
    elif "blue" in color_desc_lower: rgb = (100, 100, 255)
    elif "cyan" in color_desc_lower: rgb = (0, 255, 255)
    elif "yellow" in color_desc_lower: rgb = (255, 255, 0)
    elif "green" in color_desc_lower: rgb = (50, 200, 50)
    elif "white" in color_desc_lower: rgb = (240, 240, 240)
    elif "black" in color_desc_lower or "dark" in color_desc_lower: rgb = (50, 50, 50)
    elif "brown" in color_desc_lower: rgb = (139, 69, 19)
    elif "purple" in color_desc_lower: rgb = (128, 0, 128)
    elif "pink" in color_desc_lower: rgb = (255, 192, 203)
    elif "beige" in color_desc_lower: rgb = (245, 245, 220)
    elif "gold" in color_desc_lower: rgb = (255, 215, 0)
    elif "grey" in color_desc_lower or "gray" in color_desc_lower: rgb = (128, 128, 128)
    return rgb

def process_planet_raw(raw_tuple):
    """Converte a tupla crua em dicionário utilizável"""
    rank, name, rad_raw, mass, color_desc, grav = raw_tuple
    radius_rj = clean_radius(rad_raw)
    rgb = get_color_from_desc(color_desc)
    
    return {
        "rank": rank,
        "name": name,
        "radius_rj": radius_rj, 
        "mass_mj": mass,
        "color_desc": color_desc,
        "rgb": rgb,
        "gravity": grav
    }

# --- DATA SECTION ---

STAR_DATA = [
    {"rank": 1, "name": "Stephenson 2-18", "radius": 2150.0, "color_name": "Red", "rgb": (255, 50, 50), "gravity": "0.001 m/s²"},
    {"rank": 2, "name": "UY Scuti", "radius": 1708.0, "color_name": "Red", "rgb": (255, 60, 60), "gravity": "0.001 m/s²"},
    {"rank": 3, "name": "WOH G64", "radius": 1540.0, "color_name": "Red", "rgb": (255, 70, 70), "gravity": "0.002 m/s²"},
    {"rank": 4, "name": "RW Cephei", "radius": 1535.0, "color_name": "Orange-Red", "rgb": (255, 69, 0), "gravity": "0.002 m/s²"},
    {"rank": 5, "name": "VY Canis Majoris", "radius": 1420.0, "color_name": "Red", "rgb": (220, 20, 60), "gravity": "0.002 m/s²"},
    {"rank": 6, "name": "KY Cygni", "radius": 1420.0, "color_name": "Red", "rgb": (220, 20, 60), "gravity": "0.002 m/s²"},
    {"rank": 7, "name": "AH Scorpii", "radius": 1411.0, "color_name": "Red", "rgb": (200, 0, 0), "gravity": "0.002 m/s²"},
    {"rank": 8, "name": "VX Sagittarii", "radius": 1356.0, "color_name": "Red", "rgb": (180, 0, 0), "gravity": "0.003 m/s²"},
    {"rank": 9, "name": "HR 5171 A", "radius": 1315.0, "color_name": "Yellow", "rgb": (255, 255, 0), "gravity": "0.004 m/s²"},
    {"rank": 10, "name": "Mu Cephei", "radius": 1260.0, "color_name": "Red", "rgb": (160, 0, 0), "gravity": "0.003 m/s²"},
    {"rank": 11, "name": "S Persei", "radius": 1212.0, "color_name": "Red", "rgb": (150, 0, 0), "gravity": "0.004 m/s²"},
    {"rank": 12, "name": "NML Cygni", "radius": 1183.0, "color_name": "Red", "rgb": (140, 0, 0), "gravity": "0.004 m/s²"},
    {"rank": 13, "name": "Betelgeuse", "radius": 764.0, "color_name": "Red", "rgb": (255, 80, 80), "gravity": "0.007 m/s²"},
    {"rank": 14, "name": "Antares", "radius": 680.0, "color_name": "Red", "rgb": (255, 90, 90), "gravity": "0.012 m/s²"},
    {"rank": 15, "name": "Rho Cassiopeiae", "radius": 450.0, "color_name": "Yellow-White", "rgb": (255, 255, 200), "gravity": "0.05 m/s²"},
    {"rank": 16, "name": "Pistol Star", "radius": 306.0, "color_name": "Blue", "rgb": (100, 100, 255), "gravity": "0.04 m/s²"},
    {"rank": 17, "name": "La Superba", "radius": 300.0, "color_name": "Deep Red", "rgb": (139, 0, 0), "gravity": "0.08 m/s²"},
    {"rank": 18, "name": "Deneb", "radius": 203.0, "color_name": "White", "rgb": (240, 240, 255), "gravity": "0.20 m/s²"},
    {"rank": 19, "name": "Enif", "radius": 185.0, "color_name": "Orange", "rgb": (255, 165, 0), "gravity": "0.15 m/s²"},
    {"rank": 20, "name": "Gacrux", "radius": 84.0, "color_name": "Red", "rgb": (255, 100, 100), "gravity": "0.35 m/s²"},
    {"rank": 21, "name": "Rigel", "radius": 78.0, "color_name": "Blue-White", "rgb": (200, 200, 255), "gravity": "0.94 m/s²"},
    {"rank": 22, "name": "Aldebaran", "radius": 44.0, "color_name": "Orange", "rgb": (255, 140, 0), "gravity": "0.16 m/s²"},
    {"rank": 23, "name": "Polaris", "radius": 37.0, "color_name": "Yellow", "rgb": (255, 255, 100), "gravity": "0.22 m/s²"},
    {"rank": 24, "name": "Arcturus", "radius": 25.0, "color_name": "Orange", "rgb": (255, 120, 0), "gravity": "0.48 m/s²"},
    {"rank": 25, "name": "Pollux", "radius": 8.8, "color_name": "Orange", "rgb": (255, 150, 50), "gravity": "6.7 m/s²"},
    {"rank": 26, "name": "Vega", "radius": 2.3, "color_name": "Blue-White", "rgb": (220, 220, 255), "gravity": "108 m/s²"},
    {"rank": 27, "name": "Procyon A", "radius": 2.0, "color_name": "White", "rgb": (250, 250, 250), "gravity": "125 m/s²"},
    {"rank": 28, "name": "Altair", "radius": 1.8, "color_name": "White", "rgb": (255, 255, 255), "gravity": "115 m/s²"},
    {"rank": 29, "name": "Sirius A", "radius": 1.7, "color_name": "Blue-White", "rgb": (230, 230, 255), "gravity": "190 m/s²"},
    {"rank": 30, "name": "The Sun", "radius": 1.0, "color_name": "White/Yellow", "rgb": (255, 255, 224), "gravity": "274 m/s²"},
]

# Raw Planet Data
# Rank, Name, Radius (RJ), Mass (MJ), Color Desc, Gravity
PLANET_RAW_INIT = [
    (1, "HD 100546 b", 6.90, 20.0, "Orange-Red (Glowing)", "100"),
    (2, "GQ Lupi b", 3.50, 20.0, "Dark Red", "400"),
    (3, "CT Chamaeleontis b", 2.20, 17.0, "Brown/Red", "850"),
    (4, "HAT-P-67 b", 2.08, 0.34, "Cloudy Grey", "1.9"),
    (5, "WASP-17 b", 1.99, 0.48, "White (Reflective)", "3.1"),
    (6, "KELT-9 b", 1.89, 2.88, "Glowing Blue-White", "19.8"),
    (7, "WASP-12 b", 1.79, 1.41, "Pitch Black (Asphalt)", "11.0"),
    (8, "TrES-4 b", 1.79, 0.91, "Puffy Grey", "7.0"),
    (9, "WASP-79 b", 1.70, 0.90, "Yellow-White", "7.7"),
    (10, "WASP-127 b", 1.37, 0.18, "Pinkish-Blue", "2.4"),
    (11, "HAT-P-1 b", 1.32, 0.52, "Yellowish", "7.4"),
    (12, "TrES-2 b", 1.27, 1.20, "Dark Black (<1% Albedo)", "18.3"),
    (13, "WASP-19 b", 1.39, 1.15, "Reddish-Brown", "14.9"),
    (14, "HAT-P-32 b", 1.79, 0.68, "Hazy Grey", "5.3"),
    (15, "Kepler-7 b", 1.48, 0.43, "Bright White", "4.9"),
    (16, "WASP-76 b", 1.83, 0.92, "Dark/Grey (Iron Rain)", "6.8"),
    (17, "WASP-121 b", 1.86, 1.18, "Glowing Orange", "8.4"),
    (18, "HD 209458 b", 1.35, 0.69, "Dark Blue (Osiris)", "9.4"),
    (19, "KELT-11 b", 1.37, 0.19, "Puffy Yellow", "2.5"),
    (20, "WASP-39 b", 1.27, 0.28, "Blue-ish (H2O clouds)", "4.3"),
    (21, "WASP-31 b", 1.54, 0.48, "Cloudless/Dark", "5.0"),
    (22, "WASP-107 b", 0.94, 0.12, "Pale Yellow", "3.3"),
    (23, "HAT-P-7 b", 1.42, 1.80, "Corundum (Ruby) Clouds", "22.0"),
    (24, "KELT-1 b", 1.11, 27.2, "Brown Dwarf Color", "545"),
    (25, "CoRoT-1 b", 1.49, 1.03, "Dark Orange", "11.5"),
    (26, "XO-1 b", 1.21, 0.90, "Yellow", "15.2"),
    (27, "WASP-6 b", 1.22, 0.50, "Hazy", "8.3"),
    (28, "WASP-43 b", 1.03, 2.03, "Orange (Night) / White (Day)", "47.0"),
    (29, "HD 189733 b", 1.13, 1.14, "Deep Cobalt Blue", "21.9"),
    (30, "55 Cancri f", 1.00, 0.14, "Unknown", "3.5"),
    (31, "Jupiter", 1.00, 1.00, "Banded Beige/Red", "24.79"),
    (32, "51 Pegasi b", 1.90, 0.47, "Weathered/Grey", "3.2"),
    (33, "HAT-P-11 b", 0.42, 0.08, "Clear/Blueish", "11.0"),
    (34, "Kepler-452 b", 0.14, 0.02, "Likely Rocky/Grey", "18"),
    (35, "Kepler-1647 b", 1.06, 1.52, "Beige", "33.0"),
    (36, "Kepler-22 b", 0.21, 0.03, "Blue (Ocean World?)", "16.0"),
    (37, "Saturn", 0.83, 0.29, "Pale Gold", "10.44"),
    (38, "WASP-62 b", 1.39, 0.57, "Clear Atmosphere", "7.3"),
    (39, "WASP-104 b", 1.13, 1.27, "Dark", "24.5"),
    (40, "WASP-52 b", 1.27, 0.46, "Dark", "7.1"),
    (41, "HATS-6 b", 0.99, 0.32, "Orange Dwarf Light", "8.0"),
    (42, "WASP-80 b", 0.95, 0.55, "Hazy Red", "15.0"),
    (43, "Kepler-16 b", 0.75, 0.33, "Purple (Binary Sunset)", "14.5"),
    (44, "Gliese 436 b", 0.37, 0.07, "Grey/White (Hot Ice)", "12.0"),
    (45, "Uranus", 0.35, 0.04, "Pale Cyan", "8.69"),
    (46, "Neptune", 0.34, 0.05, "Vivid Blue", "11.15"),
    (47, "Gliese 1214 b", 0.24, 0.02, "Steamy/Hazy", "8.5"),
    (48, "K2-18 b", 0.23, 0.02, "Blue (Water Vapor)", "11.0"),
    (49, "Kepler-10 c", 0.21, 0.05, "Rocky Grey", "30.0"),
    (50, "55 Cancri e", 0.17, 0.02, "Lava (Red/Black)", "22.0"),
    (51, "CoRoT-7 b", 0.14, 0.01, "Molten Rock", "19.0"),
    (52, "Kepler-186 f", 0.10, 5, "Reddish (Vegetation?)", "~9.8"),
    (53, "Kepler-442 b", 0.12, 7, "Rocky/Ocean", "12.0"),
    (54, "Kepler-62 f", 0.12, 8, "Blue/White (Ice)", "13.0"),
    (55, "TRAPPIST-1 b", 99, 4, "Rocky/Hazy", "10.0"),
    (56, "Earth", 89, 3, "Blue/White/Green", "9.80"),
    (57, "Venus", 84, 2, "Yellowish-White", "8.87"),
    (58, "TRAPPIST-1 c", 98, 4, "Rocky", "11.5"),
    (59, "Kepler-20 e", 77, 3, "Rocky", "10"),
    (60, "Proxima Centauri b", 96, 4, "Unknown", "11"),
    (61, "Mars", 47, 3, "Red (Rust)", "3.71"),
    (62, "TRAPPIST-1 d", 69, 1, "Rocky", "~6.0"),
    (63, "TRAPPIST-1 e", 81, 2, "Rocky (Earth-like?)", "~9.0"),
    (64, "TRAPPIST-1 f", 93, 3, "Rocky/Ice", "~8.0"),
    (65, "TRAPPIST-1 g", 100, 4, "Rocky/Ice", "~9.5"),
    (66, "TRAPPIST-1 h", 69, 1, "Ice", "~5.0"),
    (67, "Kepler-37 b", 27, 3, "Rocky Grey", "~3.0"),
    (68, "Mercury", 34, 1, "Dark Grey", "3.70"),
    (69, "Kepler-42 d", 51, 3, "Rocky", "~4.0"),
    (70, "Teegarden b", 92, 3, "Rocky", "10"),
    (71, "Ross 128 b", 98, 4, "Rocky", "11"),
    (72, "LHS 1140 b", 150, 0.02, "Rocky/Iron", "24.0"),
    (73, "WASP-18 b", 1.10, 10.4, "Glowing", "210"),
    (74, "WASP-14 b", 1.28, 7.30, "Dense/Dark", "110"),
    (75, "XO-3 b", 1.21, 11.7, "Dense", "195"),
    (76, "HATS-18 b", 1.34, 1.98, "Orange", "27.0"),
    (77, "WASP-103 b", 1.53, 1.49, "Tidal/Football Shape", "15.0"),
    (78, "KELT-4 Ab", 1.70, 0.90, "Triple Sun Sky", "7.5"),
    (79, "Kepler-13 Ab", 1.51, 9.28, "Hot/Bright", "100"),
    (80, "Kepler-421 b", 0.70, 0.20, "Frost Line (White)", "10.0"),
    (81, "WASP-8 b", 1.04, 2.24, "Yellow", "51.0"),
    (82, "WASP-69 b", 1.05, 0.26, "Escaping Helium (Blue)", "5.9"),
    (83, "Luyten b", 110, 9, "Rocky", "14"),
    (84, "Wolf 1061 c", 140, 13, "Rocky", "15"),
    (85, "Kapteyn b", 140, 15, "Cold Rock", "18"),
    (86, "Gliese 667 Cc", 130, 12, "Reddish Illumination", "16"),
    (87, "Kepler-69 c", 150, 18, "Venus-like White", "17"),
    (88, "Kepler-10 b", 130, 14, "Lava World", "20.0"),
    (89, "Corot-7 b", 140, 15, "Lava World", "18.0"),
    (90, "Kepler-90 h", 1.00, 1.20, "Jupiter Twin", "29.0"),
    (91, "HR 8799 e", 1.17, 7.00, "Red (Young/Warm)", "125"),
    (92, "HR 8799 d", 1.20, 10.0, "Red (Young/Warm)", "170"),
    (93, "HR 8799 c", 1.30, 10.0, "Red (Young/Warm)", "145"),
    (94, "HR 8799 b", 1.10, 7.00, "Red (Young/Warm)", "140"),
    (95, "Beta Pictoris b", 1.65, 11.0, "Grey/Dusty", "100"),
    (96, "Fomalhaut b", 1.1, 3.00, "Disputed (Dust Cloud)", "?"),
    (97, "Pollux b", 1.10, 2.30, "Orange Illuminated", "46.0"),
    (98, "Gamma Cephei Ab", 1.20, 1.85, "Yellow Illuminated", "31.0"),
    (99, "Eris (Dwarf)", 16, 1, "White", "0.82"),
    (100, "Pluto", 16, 1, "Brown/Red/White", "0.62")
]

# Inicializa PLANET_DATA com os dados iniciais
PLANET_DATA = [process_planet_raw(p) for p in PLANET_RAW_INIT]

# --- PRESET SYSTEMS DATA (10 SYSTEMS) ---
# Formato: Name, StarDict, List of Planet Tuples
# Se a estrela ou planeta já existir pelo nome, o sistema usa o existente.

PRESET_SYSTEMS = [
    {
        "sys_name": "Sistema Solar",
        "star": {"rank": 30, "name": "The Sun", "radius": 1.0, "color_name": "White/Yellow", "rgb": (255, 255, 224), "gravity": "274 m/s²"},
        "planets": [
            (68, "Mercury", "0.034", 1, "Dark Grey", "3.70"),
            (57, "Venus", "0.084", 2, "Yellowish-White", "8.87"),
            (56, "Earth", "0.089", 3, "Blue/White/Green", "9.80"),
            (61, "Mars", "0.047", 3, "Red (Rust)", "3.71"),
            (31, "Jupiter", "1.00", 1.00, "Banded Beige/Red", "24.79"),
            (37, "Saturn", "0.83", 0.29, "Pale Gold", "10.44"),
            (45, "Uranus", "0.35", 0.04, "Pale Cyan", "8.69"),
            (46, "Neptune", "0.34", 0.05, "Vivid Blue", "11.15"),
            (100, "Pluto", "0.016", 1, "Brown/Red/White", "0.62")
        ]
    },
    {
        "sys_name": "TRAPPIST-1 System",
        "star": {"rank": 99, "name": "TRAPPIST-1", "radius": 0.12, "color_name": "Ultra Cool Red", "rgb": (255, 30, 30), "gravity": "High"},
        "planets": [
            (55, "TRAPPIST-1 b", "0.099", 4, "Rocky/Hazy", "10.0"),
            (58, "TRAPPIST-1 c", "0.098", 4, "Rocky", "11.5"),
            (62, "TRAPPIST-1 d", "0.069", 1, "Rocky", "~6.0"),
            (63, "TRAPPIST-1 e", "0.081", 2, "Rocky (Earth-like?)", "~9.0"),
            (64, "TRAPPIST-1 f", "0.093", 3, "Rocky/Ice", "~8.0"),
            (65, "TRAPPIST-1 g", "0.100", 4, "Rocky/Ice", "~9.5"),
            (66, "TRAPPIST-1 h", "0.069", 1, "Ice", "~5.0")
        ]
    },
    {
        "sys_name": "Kepler-90 System",
        "star": {"rank": 98, "name": "Kepler-90", "radius": 1.2, "color_name": "Yellow-White", "rgb": (255, 250, 200), "gravity": "Similar to Sun"},
        "planets": [
             (201, "Kepler-90 b", "0.11", 0, "Rocky", "?"),
             (202, "Kepler-90 c", "0.13", 0, "Rocky", "?"),
             (203, "Kepler-90 i", "0.11", 0, "Rocky Hot", "?"),
             (204, "Kepler-90 d", "0.25", 0, "Gas Dwarf", "?"),
             (205, "Kepler-90 e", "0.23", 0, "Gas Dwarf", "?"),
             (206, "Kepler-90 f", "0.25", 0, "Gas Dwarf", "?"),
             (207, "Kepler-90 g", "0.72", 0, "Gas Giant", "?"),
             (90, "Kepler-90 h", "1.00", 1.20, "Jupiter Twin", "29.0")
        ]
    },
    {
        "sys_name": "55 Cancri System",
        "star": {"rank": 97, "name": "55 Cancri A", "radius": 0.94, "color_name": "Yellow-Orange", "rgb": (255, 200, 100), "gravity": "High"},
        "planets": [
            (50, "55 Cancri e", "0.17", 0.02, "Lava (Red/Black)", "22.0"),
            (210, "55 Cancri b", "0.7", 0.8, "Gas Giant", "?"),
            (211, "55 Cancri c", "0.7", 0.16, "Gas Giant", "?"),
            (30, "55 Cancri f", "1.00", 0.14, "Water World?", "3.5"),
            (212, "55 Cancri d", "0.9", 3.8, "Gas Giant", "?")
        ]
    },
    {
        "sys_name": "HR 8799 System",
        "star": {"rank": 96, "name": "HR 8799", "radius": 1.44, "color_name": "White A-Type", "rgb": (240, 240, 255), "gravity": "?"},
        "planets": [
            (91, "HR 8799 e", "1.17", 7.00, "Red (Young/Warm)", "125"),
            (92, "HR 8799 d", "1.20", 10.0, "Red (Young/Warm)", "170"),
            (93, "HR 8799 c", "1.30", 10.0, "Red (Young/Warm)", "145"),
            (94, "HR 8799 b", "1.10", 7.00, "Red (Young/Warm)", "140")
        ]
    },
    {
        "sys_name": "Kepler-11 System",
        "star": {"rank": 95, "name": "Kepler-11", "radius": 1.06, "color_name": "Sun-like", "rgb": (255, 255, 220), "gravity": "?"},
        "planets": [
            (220, "Kepler-11 b", "0.17", 0, "Hot puffy", "?"),
            (221, "Kepler-11 c", "0.28", 0, "Gas Dwarf", "?"),
            (222, "Kepler-11 d", "0.30", 0, "Gas Dwarf", "?"),
            (223, "Kepler-11 e", "0.40", 0, "Gas Dwarf", "?"),
            (224, "Kepler-11 f", "0.23", 0, "Gas Dwarf", "?"),
            (225, "Kepler-11 g", "0.32", 0, "Gas Dwarf", "?")
        ]
    },
    {
        "sys_name": "Gliese 667 C System",
        "star": {"rank": 94, "name": "Gliese 667 C", "radius": 0.42, "color_name": "Red Dwarf", "rgb": (200, 50, 0), "gravity": "?"},
        "planets": [
            (230, "Gliese 667 Cb", "0.15", 0, "Rocky", "?"),
            (86, "Gliese 667 Cc", "0.13", 12, "Reddish Illumination", "16"),
            (231, "Gliese 667 Cd", "0.18", 0, "Super-Earth", "?"), # Candidates usually included in sims
        ]
    },
     {
        "sys_name": "Kepler-62 System",
        "star": {"rank": 93, "name": "Kepler-62", "radius": 0.64, "color_name": "Orange Dwarf", "rgb": (255, 160, 50), "gravity": "?"},
        "planets": [
            (240, "Kepler-62 b", "0.11", 0, "Hot Rock", "?"),
            (241, "Kepler-62 c", "0.04", 0, "Tiny Rock", "?"),
            (242, "Kepler-62 d", "0.17", 0, "Gas Dwarf", "?"),
            (243, "Kepler-62 e", "0.14", 0, "Ocean World", "?"),
            (54, "Kepler-62 f", "0.12", 8, "Blue/White (Ice)", "13.0")
        ]
    },
    {
        "sys_name": "Tau Ceti System",
        "star": {"rank": 92, "name": "Tau Ceti", "radius": 0.79, "color_name": "Yellow G-Type", "rgb": (255, 240, 150), "gravity": "?"},
        "planets": [
            (250, "Tau Ceti g", "0.15", 0, "Rocky", "?"),
            (251, "Tau Ceti h", "0.15", 0, "Rocky", "?"),
            (252, "Tau Ceti e", "0.17", 0, "Super Earth", "?"),
            (253, "Tau Ceti f", "0.17", 0, "Super Earth", "?")
        ]
    },
    {
        "sys_name": "HD 10180 System",
        "star": {"rank": 91, "name": "HD 10180", "radius": 1.20, "color_name": "Sun-like", "rgb": (255, 255, 240), "gravity": "?"},
        "planets": [
             (260, "HD 10180 c", "0.3", 0, "Hot Neptune", "?"),
             (261, "HD 10180 d", "0.3", 0, "Hot Neptune", "?"),
             (262, "HD 10180 e", "0.5", 0, "Gas Giant", "?"),
             (263, "HD 10180 f", "0.5", 0, "Gas Giant", "?"),
             (264, "HD 10180 g", "0.5", 0, "Gas Giant", "?"),
             (265, "HD 10180 h", "1.0", 0, "Saturn-like", "?")
        ]
    }
]

class StarSimulation:
    def __init__(self):
        # Initial window size
        self.width = MIN_WIDTH
        self.height = MIN_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Solar System Creator & Explorer")
        
        self.manager = pygame_gui.UIManager((self.width, self.height))
        self.clock = pygame.time.Clock()
        
        # UI Constants
        self.ui_width = 350
        self.update_layout_rects()

        # State
        self.current_star = STAR_DATA[-1] # Default to Sun
        self.current_planet_selection = PLANET_DATA[0] 
        self.added_planets = [] 
        # Explicitly track selected preset to ensure button works
        self.selected_preset_name = PRESET_SYSTEMS[0]['sys_name']
        
        # View Controls
        self.scale = 0.5 
        self.reset_view()
        self.is_dragging = False
        self.last_mouse_pos = (0, 0)
        
        self.init_ui_elements()
        self.generate_texture_features()
        self.update_info_label()

    def update_layout_rects(self):
        self.ui_rect = pygame.Rect(0, 0, self.ui_width, self.height)
        self.sim_rect = pygame.Rect(self.ui_width, 0, self.width - self.ui_width, self.height)

    def init_ui_elements(self):
        # --- NEW: SYSTEM GENERATOR SECTION ---
        self.lbl_presets = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 10), (310, 20)),
            text="--- PRESET SYSTEMS ---",
            manager=self.manager
        )
        
        self.preset_options = [s['sys_name'] for s in PRESET_SYSTEMS]
        self.preset_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.preset_options,
            starting_option=self.preset_options[0],
            relative_rect=pygame.Rect((20, 35), (310, 30)),
            manager=self.manager
        )
        
        self.btn_generate_sys = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 70), (310, 30)),
            text='GERAR SISTEMA COMPLETO',
            manager=self.manager
        )

        # --- EXISTING: MANUAL CONTROLS ---
        y_offset = 120
        self.lbl_manual = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, y_offset), (310, 20)),
            text="--- MANUAL EDIT ---",
            manager=self.manager
        )

        self.star_options = [f"{s['name']}" for s in STAR_DATA]
        self.star_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.star_options,
            starting_option=self.current_star['name'],
            relative_rect=pygame.Rect((20, y_offset + 25), (310, 30)),
            manager=self.manager
        )
        
        self.info_label = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect((20, y_offset + 60), (310, 180)),
            manager=self.manager
        )

        # Planet Selection
        self.planet_options = [f"{p['name']}" for p in PLANET_DATA]
        self.planet_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.planet_options,
            starting_option=self.planet_options[0],
            relative_rect=pygame.Rect((20, y_offset + 250), (310, 30)),
            manager=self.manager
        )
        
        self.btn_add_planet = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, y_offset + 290), (145, 40)),
            text='Add Planet',
            manager=self.manager
        )
        
        self.btn_remove_planet = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((185, y_offset + 290), (145, 40)),
            text='Remove Planet',
            manager=self.manager
        )
        
        # Speed Slider
        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((20, y_offset + 340), (310, 30)),
            start_value=1.0,
            value_range=(0.0, 10.0),
            manager=self.manager
        )
        self.speed_label = pygame_gui.elements.UILabel(
             relative_rect=pygame.Rect((20, y_offset + 370), (310, 20)),
             text="Orbit Speed: 1.0x",
             manager=self.manager
        )
        
        # ZOOM Buttons
        self.btn_zoom_out = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, y_offset + 400), (145, 40)),
            text='Zoom -',
            manager=self.manager
        )
        
        self.btn_zoom_in = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((185, y_offset + 400), (145, 40)),
            text='Zoom +',
            manager=self.manager
        )

    def refresh_dropdowns(self):
        # Update Star Dropdown options
        current_selection = self.current_star['name']
        self.star_options = [f"{s['name']}" for s in STAR_DATA]
        
        # Hacky way to update options in pygame_gui < 0.6.x (recreating element)
        # Using a safer approach: set options_list if available or recreate
        self.star_dropdown.kill()
        self.star_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.star_options,
            starting_option=current_selection,
            relative_rect=pygame.Rect((20, 145), (310, 30)), # Must match init pos
            manager=self.manager
        )

        # Update Planet Dropdown
        current_p_sel = self.planet_options[0] if not self.current_planet_selection else self.current_planet_selection['name']
        self.planet_options = [f"{p['name']}" for p in PLANET_DATA]
        
        self.planet_dropdown.kill()
        self.planet_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.planet_options,
            starting_option=current_p_sel,
            relative_rect=pygame.Rect((20, 370), (310, 30)), # Must match init pos
            manager=self.manager
        )

    def reset_view(self):
        center_x = self.sim_rect.x + self.sim_rect.width // 2
        center_y = self.sim_rect.y + self.sim_rect.height // 2
        self.offset = [center_x, center_y]

    def generate_texture_features(self):
        random.seed(self.current_star['name'])
        self.features = []
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            r = math.sqrt(random.uniform(0, 1))
            size = random.uniform(0.1, 0.3)
            color_var = random.randint(-30, 30)
            self.features.append({
                'x': r * math.cos(angle),
                'y': r * math.sin(angle),
                'size': size,
                'color_var': color_var
            })

    def update_info_label(self):
        star = self.current_star
        text = (f"<b>{star['name']}</b><br>"
                f"Rank: {star['rank']}<br>"
                f"Diameter: {star['radius']} Sun Radii<br>"
                f"Color: {star['color_name']}<br>"
                f"Gravity: {star['gravity']}<br><br>"
                f"Planets: {len(self.added_planets)}<br>"
                f"Scale: {self.scale:.2f}")
        self.info_label.set_text(text)

    def add_selected_planet(self, planet_data=None):
        p_data = planet_data if planet_data else self.current_planet_selection
        star_r = self.current_star['radius']
        current_count = len(self.added_planets)
        
        if current_count == 0:
            orbit_dist_sun_radii = star_r * 2.0 + 10 # Little more spacing
        else:
            prev_dist = self.added_planets[-1]['orbit_dist']
            # Dynamic spacing based on previous planet size to avoid overlap
            prev_rad = self.added_planets[-1]['data']['radius_rj'] * 0.1
            curr_rad = p_data['radius_rj'] * 0.1
            min_gap = (prev_rad + curr_rad) * 1.5 + (star_r * 0.2) + 15
            orbit_dist_sun_radii = prev_dist + min_gap
        
        base_speed = 1.0 / math.sqrt(max(1, orbit_dist_sun_radii/10)) # Keplerish
        
        planet_obj = {
            'data': p_data,
            'orbit_dist': orbit_dist_sun_radii, 
            'angle': random.uniform(0, 6.28),
            'base_speed': base_speed
        }
        self.added_planets.append(planet_obj)
        self.update_info_label()

    def generate_system_from_preset(self):
        # Use the tracked variable
        selected_name = self.selected_preset_name
        preset = next((s for s in PRESET_SYSTEMS if s['sys_name'] == selected_name), None)
        
        if not preset: return

        # 1. Handle Star
        p_star = preset['star']
        # Check if star exists in global list by name
        existing_star = next((s for s in STAR_DATA if s['name'] == p_star['name']), None)
        
        if existing_star:
            self.current_star = existing_star
        else:
            # Add new star
            STAR_DATA.append(p_star)
            self.current_star = p_star
        
        # 2. Reset current planets
        self.added_planets = []
        
        # 3. Handle Planets
        for p_raw in preset['planets']:
            # Check if planet exists in global list by name
            p_name = p_raw[1]
            existing_planet = next((p for p in PLANET_DATA if p['name'] == p_name), None)
            
            if existing_planet:
                self.add_selected_planet(existing_planet)
            else:
                # Create new planet data
                new_planet_data = process_planet_raw(p_raw)
                PLANET_DATA.append(new_planet_data)
                self.add_selected_planet(new_planet_data)
        
        # 4. Refresh UI to show new stars/planets in dropdowns
        self.refresh_dropdowns()
        self.generate_texture_features()
        self.update_info_label()

    def remove_last_planet(self):
        if self.added_planets:
            self.added_planets.pop()
            self.update_info_label()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.VIDEORESIZE:
                new_w = max(MIN_WIDTH, event.w)
                new_h = max(MIN_HEIGHT, event.h)
                self.width, self.height = new_w, new_h
                self.screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
                self.manager.set_window_resolution((new_w, new_h))
                self.update_layout_rects()
            
            self.manager.process_events(event)
            
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.star_dropdown:
                    name = event.text
                    for s in STAR_DATA:
                        if s['name'] == name:
                            self.current_star = s
                            self.added_planets = [] 
                            self.generate_texture_features()
                            self.update_info_label()
                            break
                elif event.ui_element == self.planet_dropdown:
                    name = event.text
                    for p in PLANET_DATA:
                        if p['name'] == name:
                            self.current_planet_selection = p
                            break
                elif event.ui_element == self.preset_dropdown:
                    # Update explicit tracking variable
                    self.selected_preset_name = event.text

            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.speed_slider:
                    val = self.speed_slider.get_current_value()
                    self.speed_label.set_text(f"Orbit Speed: {val:.1f}x")
                            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.btn_add_planet:
                    self.add_selected_planet()
                elif event.ui_element == self.btn_remove_planet:
                    self.remove_last_planet()
                elif event.ui_element == self.btn_generate_sys:
                    self.generate_system_from_preset()
                elif event.ui_element == self.btn_zoom_in:
                    self.scale *= 1.1
                    self.update_info_label()
                elif event.ui_element == self.btn_zoom_out:
                    self.scale /= 1.1
                    self.update_info_label()
            
            # Interaction Logic
            mouse_pos = pygame.mouse.get_pos()
            in_sim_rect = self.sim_rect.collidepoint(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_sim_rect:
                    if event.button == 1: 
                         self.is_dragging = True
                         self.last_mouse_pos = event.pos
                    # Scroll zoom removed (buttons 4 and 5)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.offset[0] += dx
                    self.offset[1] += dy
                    self.last_mouse_pos = event.pos
                    
        return True

    def draw_star_and_planets(self):
        self.screen.set_clip(self.sim_rect)
        
        cx, cy = self.offset
        star_radius_px = self.current_star['radius'] * self.scale
        speed_mult = self.speed_slider.get_current_value()
        
        # 1. Draw Orbits
        for p in self.added_planets:
            dist_px = p['orbit_dist'] * self.scale
            if dist_px < 2: continue
            
            orbit_rect = pygame.Rect(cx - dist_px, cy - dist_px, dist_px*2, dist_px*2)
            if not self.sim_rect.colliderect(orbit_rect):
                continue

            try:
                pygame.draw.circle(self.screen, (30, 30, 50), (int(cx), int(cy)), int(dist_px), 1)
            except: pass 

        # 2. Draw Star
        draw_star_r = max(2, int(star_radius_px))
        star_rect = pygame.Rect(cx - draw_star_r, cy - draw_star_r, draw_star_r*2, draw_star_r*2)
        
        if self.sim_rect.colliderect(star_rect):
            pygame.draw.circle(self.screen, self.current_star['rgb'], (int(cx), int(cy)), draw_star_r)
            
            if draw_star_r > 5:
               for feat in self.features:
                   fx = cx + feat['x'] * star_radius_px
                   fy = cy + feat['y'] * star_radius_px
                   f_rad = feat['size'] * star_radius_px
                   r, g, b = self.current_star['rgb']
                   var = feat['color_var']
                   f_color = (max(0, min(255, r+var)), max(0, min(255, g+var)), max(0, min(255, b+var)))
                   try:
                       pygame.draw.circle(self.screen, f_color, (int(fx), int(fy)), max(1, int(f_rad)))
                   except: pass

            # Star Name
            font = pygame.font.SysFont("Arial", 24, bold=True)
            text_s = font.render(self.current_star['name'], True, (255, 255, 255))
            t_rect = text_s.get_rect(center=(int(cx), int(cy - draw_star_r - 20)))
            self.screen.blit(text_s, t_rect)

        # 3. Draw Planets
        for p in self.added_planets:
            p['angle'] += p['base_speed'] * speed_mult * 0.01 
            dist_px = p['orbit_dist'] * self.scale
            px = cx + math.cos(p['angle']) * dist_px
            py = cy + math.sin(p['angle']) * dist_px
            
            # Ajuste visual do raio do planeta
            p_rad_sun = p['data']['radius_rj'] * 0.1
            p_rad_px = p_rad_sun * self.scale
            
            # Se for muito pequeno, desenha minimo 2px pra ver
            draw_rad = max(3, int(p_rad_px))
            
            p_rect = pygame.Rect(px - draw_rad, py - draw_rad, draw_rad*2, draw_rad*2)
            if not self.sim_rect.colliderect(p_rect):
                continue
            
            pygame.draw.circle(self.screen, p['data']['rgb'], (int(px), int(py)), draw_rad)
            
            if self.scale > 0.3: # Só mostra nome se zoom permitir
                p_font = pygame.font.SysFont("Arial", 12)
                p_text = p_font.render(p['data']['name'], True, (200, 200, 200))
                self.screen.blit(p_text, (px + draw_rad + 2, py))

        self.screen.set_clip(None)

    def run(self):
        running = True
        while running:
            time_delta = self.clock.tick(FPS) / 1000.0
            
            running = self.handle_events()
            
            self.manager.update(time_delta)
            
            self.screen.fill(BACKGROUND_COLOR)
            
            pygame.draw.rect(self.screen, UI_PANEL_COLOR, self.ui_rect)
            pygame.draw.line(self.screen, SEPARATOR_COLOR, (self.ui_width, 0), (self.ui_width, self.height), 2)
            
            self.draw_star_and_planets()
            self.manager.draw_ui(self.screen)
            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    sim = StarSimulation()
    sim.run()