import pygame
import sys
import math
import json
import random

# Inicialização do Pygame
pygame.init()

# Configurações iniciais da janela
MIN_WIDTH, MIN_HEIGHT = 1000, 800
screen = pygame.display.set_mode((MIN_WIDTH, MIN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Simulador de Átomos - Tabela Periódica Interativa")
clock = pygame.time.Clock()

# Cores
COLOR_BG = (20, 24, 30)
COLOR_MENU_BG = (35, 40, 48)
COLOR_TEXT = (220, 225, 230)
COLOR_TEXT_DIM = (150, 160, 170)
COLOR_PROTON = (40, 200, 60)
COLOR_NEUTRON = (240, 240, 240)
COLOR_ELECTRON = (60, 150, 255)
COLOR_ORBIT = (80, 90, 100)
COLOR_UI_BG = (50, 55, 65)
COLOR_UI_HOVER = (70, 75, 85)
COLOR_UI_BORDER = (100, 110, 120)

# Dataset completo com todos os 118 elementos da Tabela Periódica atualizada.
def gerar_dados_elementos():
    elementos_base = [
        {"z": 1, "s": "H", "n": "Hidrogênio", "m": 1, "desc": "Não-metal. O elemento mais abundante do universo, fundamental em estrelas e na água."},
        {"z": 2, "s": "He", "n": "Hélio", "m": 4, "desc": "Gás nobre incolor e leve. Usado em balões e ressonância magnética."},
        {"z": 3, "s": "Li", "n": "Lítio", "m": 7, "desc": "Metal alcalino. Muito leve e altamente reativo. Vital em baterias recarregáveis."},
        {"z": 4, "s": "Be", "n": "Berílio", "m": 9, "desc": "Metal alcalinoterroso. Usado em ligas leves e fortes para uso aeroespacial."},
        {"z": 5, "s": "B", "n": "Boro", "m": 11, "desc": "Metaloide. Usado na criação de fibras de vidro e detergentes."},
        {"z": 6, "s": "C", "n": "Carbono", "m": 12, "desc": "Não-metal. Base de toda a vida na Terra, forma grafite, diamante e compostos orgânicos."},
        {"z": 7, "s": "N", "n": "Nitrogênio", "m": 14, "desc": "Não-metal. Compõe cerca de 78% da atmosfera terrestre. Essencial em fertilizantes."},
        {"z": 8, "s": "O", "n": "Oxigênio", "m": 16, "desc": "Não-metal. Gás vital para a respiração celular e o grande responsável pela combustão."},
        {"z": 9, "s": "F", "n": "Flúor", "m": 19, "desc": "Halogênio. O elemento mais eletronegativo e reativo. Usado na proteção dental."},
        {"z": 10, "s": "Ne", "n": "Neônio", "m": 20, "desc": "Gás nobre. Famoso por seu brilho vermelho-alaranjado em letreiros luminosos."},
        {"z": 11, "s": "Na", "n": "Sódio", "m": 23, "desc": "Metal alcalino. Altamente reativo com água, compõe o sal de cozinha (NaCl)."},
        {"z": 12, "s": "Mg", "n": "Magnésio", "m": 24, "desc": "Metal alcalinoterroso. Leve, essencial biologicamente; inflama com uma luz branca ofuscante."},
        {"z": 13, "s": "Al", "n": "Alumínio", "m": 27, "desc": "Metal pós-transição. Leve, resistente à corrosão e amplamente reciclável no cotidiano."},
        {"z": 14, "s": "Si", "n": "Silício", "m": 28, "desc": "Metaloide. A base estrutural da indústria de semicondutores e da era da informação."},
        {"z": 15, "s": "P", "n": "Fósforo", "m": 31, "desc": "Não-metal. Essencial para a vida (DNA, ATP), e amplamente usado na agricultura."},
        {"z": 16, "s": "S", "n": "Enxofre", "m": 32, "desc": "Não-metal. Sólido amarelo com odor característico, essencial na indústria de ácido sulfúrico."},
        {"z": 17, "s": "Cl", "n": "Cloro", "m": 35, "desc": "Halogênio. Gás esverdeado e tóxico, vital para a desinfecção de águas potáveis."},
        {"z": 18, "s": "Ar", "n": "Argônio", "m": 40, "desc": "Gás nobre. Usado em soldagem e para proteger os filamentos de lâmpadas incandescentes."},
        {"z": 19, "s": "K", "n": "Potássio", "m": 39, "desc": "Metal alcalino. Extremamente reativo, vital para as funções nervosas e fisiológicas."},
        {"z": 20, "s": "Ca", "n": "Cálcio", "m": 40, "desc": "Metal alcalinoterroso. Principal componente dos ossos, dentes e conchas na natureza."},
        {"z": 21, "s": "Sc", "n": "Escândio", "m": 45, "desc": "Metal de transição. Usado na criação de ligas de alumínio de alta resistência aeroespacial."},
        {"z": 22, "s": "Ti", "n": "Titânio", "m": 48, "desc": "Metal de transição. Extremamente forte, leve e não corrosivo. Usado em implantes médicos."},
        {"z": 23, "s": "V", "n": "Vanádio", "m": 51, "desc": "Metal de transição. Adicionado ao aço para criar ligas de grande resistência estrutural."},
        {"z": 24, "s": "Cr", "n": "Cromo", "m": 52, "desc": "Metal de transição. Responsável pelo brilho característico e resistência do aço inoxidável."},
        {"z": 25, "s": "Mn", "n": "Manganês", "m": 55, "desc": "Metal de transição. Atua como um endurecedor fundamental na produção e pureza do aço."},
        {"z": 26, "s": "Fe", "n": "Ferro", "m": 56, "desc": "Metal de transição. O metal mais utilizado pela humanidade. Vital para transportar oxigênio no sangue."},
        {"z": 27, "s": "Co", "n": "Cobalto", "m": 59, "desc": "Metal de transição. Magnético, crucial na fabricação de ligas e baterias super resistentes."},
        {"z": 28, "s": "Ni", "n": "Níquel", "m": 59, "desc": "Metal de transição. Resistente à oxidação, amplamente usado em moedas e aço inoxidável."},
        {"z": 29, "s": "Cu", "n": "Cobre", "m": 64, "desc": "Metal de transição. Um dos melhores condutores de eletricidade; a base das redes elétricas mundiais."},
        {"z": 30, "s": "Zn", "n": "Zinco", "m": 65, "desc": "Metal de transição. Usado extensivamente para galvanizar e proteger o ferro e aço da ferrugem."},
        {"z": 31, "s": "Ga", "n": "Gálio", "m": 70, "desc": "Metal pós-transição. Um metal que derrete no calor da mão. Vital em LEDs e eletrônicos."},
        {"z": 32, "s": "Ge", "n": "Germânio", "m": 73, "desc": "Metaloide. Um dos primeiros semicondutores; hoje crítico em fibra óptica e óptica infravermelha."},
        {"z": 33, "s": "As", "n": "Arsênio", "m": 75, "desc": "Metaloide. Historicamente famoso como veneno, possui utilidades modernas em alguns LEDs."},
        {"z": 34, "s": "Se", "n": "Selênio", "m": 79, "desc": "Não-metal. Fotocondutor; sua condutividade elétrica aumenta vertiginosamente quando iluminado."},
        {"z": 35, "s": "Br", "n": "Bromo", "m": 80, "desc": "Halogênio. O único não-metal naturalmente líquido à temperatura ambiente (vermelho-escuro)."},
        {"z": 36, "s": "Kr", "n": "Criptônio", "m": 84, "desc": "Gás nobre. Gás denso usado em iluminação fluorescente potente e lasers fotográficos."},
        {"z": 37, "s": "Rb", "n": "Rubídio", "m": 85, "desc": "Metal alcalino. Sofre ignição espontânea no ar, sendo usado em pesquisas de relógios atômicos."},
        {"z": 38, "s": "Sr", "n": "Estrôncio", "m": 88, "desc": "Metal alcalinoterroso. Dá o vibrante tom de vermelho aos fogos de artifício e sinalizadores."},
        {"z": 39, "s": "Y", "n": "Ítrio", "m": 89, "desc": "Metal de transição. Presente nos fósforos das antigas TVs a cores e em supercondutores."},
        {"z": 40, "s": "Zr", "n": "Zircônio", "m": 91, "desc": "Metal de transição. Altamente resistente à corrosão; usado nas hastes de reatores nucleares."},
        {"z": 41, "s": "Nb", "n": "Nióbio", "m": 93, "desc": "Metal de transição. O Brasil abriga quase toda a sua reserva global; fortalece ligas de aço."},
        {"z": 42, "s": "Mo", "n": "Molibdênio", "m": 96, "desc": "Metal de transição. Capaz de suportar altíssimas temperaturas em peças de motores industriais."},
        {"z": 43, "s": "Tc", "n": "Tecnécio", "m": 98, "desc": "Metal de transição. O primeiro elemento artificial criado pelo homem. Inestimável na medicina nuclear."},
        {"z": 44, "s": "Ru", "n": "Rutênio", "m": 101, "desc": "Metal de transição. Duro e prateado, usado para endurecer ligas de platina de alta precisão."},
        {"z": 45, "s": "Rh", "n": "Ródio", "m": 103, "desc": "Metal de transição. Extremamente raro e reflexivo. A essência dos conversores catalíticos veiculares."},
        {"z": 46, "s": "Pd", "n": "Paládio", "m": 106, "desc": "Metal de transição. Possui a assombrosa capacidade de absorver hidrogênio feito uma 'esponja' atômica."},
        {"z": 47, "s": "Ag", "n": "Prata", "m": 108, "desc": "Metal de transição. Possui a maior condutividade elétrica e térmica dentre os metais."},
        {"z": 48, "s": "Cd", "n": "Cádmio", "m": 112, "desc": "Metal de transição. Elemento tóxico usado amplamente nas antigas baterias recarregáveis (Ni-Cd)."},
        {"z": 49, "s": "In", "n": "Índio", "m": 115, "desc": "Metal pós-transição. Um metal prateado macio, o pilar de todas as telas sensíveis ao toque (touchscreens)."},
        {"z": 50, "s": "Sn", "n": "Estanho", "m": 119, "desc": "Metal pós-transição. Resistente; protege latas de alimentos contra corrosão e compõe o bronze."},
        {"z": 51, "s": "Sb", "n": "Antimônio", "m": 122, "desc": "Metaloide. Endurece as baterias de chumbo-ácido automotivas e serve como retardante de chama."},
        {"z": 52, "s": "Te", "n": "Telúrio", "m": 128, "desc": "Metaloide. Importante formador de ligas e crucial no desenvolvimento de novos painéis solares."},
        {"z": 53, "s": "I", "n": "Iodo", "m": 127, "desc": "Halogênio. Sólido cristalino roxo-escuro, cuja ingestão em traços é essencial para a saúde da tireoide."},
        {"z": 54, "s": "Xe", "n": "Xenônio", "m": 131, "desc": "Gás nobre. Usado nos intensos faróis brilhantes de carros de luxo e propulsores iônicos espaciais."},
        {"z": 55, "s": "Cs", "n": "Césio", "m": 133, "desc": "Metal alcalino. É o núcleo pulsante dos relógios atômicos e que dita os padrões exatos de tempo da humanidade."},
        {"z": 56, "s": "Ba", "n": "Bário", "m": 137, "desc": "Metal alcalinoterroso. Usado clinicamente como agente de contraste radiológico nos diagnósticos de Raio-X."},
        {"z": 57, "s": "La", "n": "Lantânio", "m": 139, "desc": "Lantanídeo. Dá nome à série dos Lantanídeos. É usado em vidro óptico (como o das câmeras) de alto padrão."},
        {"z": 58, "s": "Ce", "n": "Cério", "m": 140, "desc": "Lantanídeo. O lantanídeo mais abundante no planeta. Usado ativamente em pedras de isqueiros cotidianos."},
        {"z": 59, "s": "Pr", "n": "Praseodímio", "m": 141, "desc": "Lantanídeo. Usado, junto ao neodímio, para fabricar os óculos protetores que salvam os olhos dos soldadores."},
        {"z": 60, "s": "Nd", "n": "Neodímio", "m": 144, "desc": "Lantanídeo. Famoso globalmente pelos imãs permanentes mais potentes do mundo. Vital para fones de ouvido e turbinas."},
        {"z": 61, "s": "Pm", "n": "Promécio", "m": 145, "desc": "Lantanídeo. Completamente radioativo e fabricado apenas sinteticamente, não sendo encontrado de forma natural."},
        {"z": 62, "s": "Sm", "n": "Samário", "m": 150, "desc": "Lantanídeo. Forma ímãs (junto ao cobalto) que operam em temperaturas absurdamente elevadas sem perder suas propriedades."},
        {"z": 63, "s": "Eu", "n": "Európio", "m": 152, "desc": "Lantanídeo. O reativo metal da Terra Rara usado intensivamente na geração das cores vermelhas/azuis das antigas TVs tubulares."},
        {"z": 64, "s": "Gd", "n": "Gadolínio", "m": 157, "desc": "Lantanídeo. Um metal notável e altamente magnético. Funciona perfeitamente como agente de contraste na medicina avançada (Ressonância)."},
        {"z": 65, "s": "Tb", "n": "Térbio", "m": 159, "desc": "Lantanídeo. Muito valioso em telas de alta definição pelo seu papel incansável de ser o emissor de fótons para a cor verde."},
        {"z": 66, "s": "Dy", "n": "Disprósio", "m": 163, "desc": "Lantanídeo. Elemento altamente magnetizável, aplicado em motores verdes e armazenadores magnéticos como discos rígidos."},
        {"z": 67, "s": "Ho", "n": "Hólmio", "m": 165, "desc": "Lantanídeo. Detém o assombroso recorde do maior momento magnético entre os elementos que ocorrem no cosmos."},
        {"z": 68, "s": "Er", "n": "Érbio", "m": 167, "desc": "Lantanídeo. Atua secretamente no fundo dos oceanos para amplificar os sinais da internet nos colossais cabos de fibra óptica intercontinentais."},
        {"z": 69, "s": "Tm", "n": "Túlio", "m": 169, "desc": "Lantanídeo. De extrema raridade em escala global. Encontra-se como dopante precioso na alta precisão de bisturis a laser na medicina."},
        {"z": 70, "s": "Yb", "n": "Itérbio", "m": 173, "desc": "Lantanídeo. Amplamente incorporado nos novos, compactos e complexos relógios atômicos ópticos, revolucionando a área do tempo."},
        {"z": 71, "s": "Lu", "n": "Lutécio", "m": 175, "desc": "Lantanídeo. O lutécio é o ponto final, o ápice da densidade e dureza das Terras Raras, excelente para detectores em tomógrafos PET."},
        {"z": 72, "s": "Hf", "n": "Háfnio", "m": 178, "desc": "Metal de transição. Excelente absorvedor da emissão letal de nêutrons; controla com eficiência o processo dentro de um núcleo de reator atômico."},
        {"z": 73, "s": "Ta", "n": "Tântalo", "m": 181, "desc": "Metal de transição. Um dos principais facilitadores tecnológicos do celular que está hoje no seu bolso através da fabricação de finíssimos capacitores."},
        {"z": 74, "s": "W", "n": "Tungstênio", "m": 184, "desc": "Metal de transição. Coroado com o maior de todos os pontos de fusão. Resistente, acendeu o mundo via filamentos de lâmpadas velhas."},
        {"z": 75, "s": "Re", "n": "Rênio", "m": 186, "desc": "Metal de transição. Extraído com avidez para endurecer e super aquecer as turbinas gigantescas acopladas às asas das rotas de jatos espaciais."},
        {"z": 76, "s": "Os", "n": "Ósmio", "m": 190, "desc": "Metal de transição. Densidade assustadora; simplesmente o elemento químico estrutural mais denso, massivo e comprimido gerado de toda a Terra natural."},
        {"z": 77, "s": "Ir", "n": "Irídio", "m": 192, "desc": "Metal de transição. Encontrado na fina crosta de impacto onde o meteoro extinguiu os grandiosos dinossauros; não oxida sob pretexto algum."},
        {"z": 78, "s": "Pt", "n": "Platina", "m": 195, "desc": "Metal de transição. Tido frequentemente por ainda mais esplêndido e durável que o ouro. O pilar indissolúvel dos grandes catalisadores da química moderna."},
        {"z": 79, "s": "Au", "n": "Ouro", "m": 197, "desc": "Metal de transição. Incrivelmente valioso pela sua perenidade. Ele absolutamente recusa se desintegrar. Por séculos, o verdadeiro dinheiro do mundo civilizado."},
        {"z": 80, "s": "Hg", "n": "Mercúrio", "m": 201, "desc": "Metal de transição. Único, perigoso e magnético por natureza para o olhar. Ele balança em forma líquida metálica até no frio do inverno."},
        {"z": 81, "s": "Tl", "n": "Tálio", "m": 204, "desc": "Metal pós-transição. A 'sombra do assassino', invisível e insípido para nós. Foi o principal agente banido no extermínio de ratazanas pelo mundo moderno."},
        {"z": 82, "s": "Pb", "n": "Chumbo", "m": 207, "desc": "Metal pós-transição. Invariavelmente pesado, maleável e abafado. Sua finalidade sublime reside em deter até as mais duras radiações desprendidas do cosmos."},
        {"z": 83, "s": "Bi", "n": "Bismuto", "m": 209, "desc": "Metal pós-transição. Um paradoxo visual e químico: um escudo que derrete num reator, mas ao mesmo tempo cuida do seu estômago por trás das prateleiras de farmácias."},
        {"z": 84, "s": "Po", "n": "Polônio", "m": 209, "desc": "Metaloide. O pesadelo isolado com as próprias mãos por Marie Curie; ele destila letal radioatividade silenciosamente onde quer que decaia."},
        {"z": 85, "s": "At", "n": "Ástato", "m": 210, "desc": "Halogênio. Incrivelmente sombrio. Raríssimo, efêmero, tão impossível de coletar que sua totalidade sob os continentes jamais somaria muito mais do que gramas."},
        {"z": 86, "s": "Rn", "n": "Radônio", "m": 222, "desc": "Gás nobre. Escondido no decaimento atômico. Pesado que se arrasta sorrateiro por subterrâneos sem avisar, emitindo rádio num perigo persistente, inodoro e gasoso."},
        {"z": 87, "s": "Fr", "n": "Frâncio", "m": 223, "desc": "Metal alcalino. Um espasmo na história periódica. Apenas um lampejo de estabilidade com míseros e parcos 22 minutos no seu melhor e mais isolado formato existente natural."},
        {"z": 88, "s": "Ra", "n": "Rádio", "m": 226, "desc": "Metal alcalinoterroso. A descoberta que iluminou mostruários de relógios em tons ameaçadoramente esverdeados; radioativo com um brilho natural em sua face maligna."},
        {"z": 89, "s": "Ac", "n": "Actínio", "m": 227, "desc": "Actinídeo. Denomina em essência toda a linha subsequente da fronteira final natural; azul incandescente pelo rastro feroz na radioatividade que esmaga os vizinhos."},
        {"z": 90, "s": "Th", "n": "Tório", "m": 232, "desc": "Actinídeo. O gigante dormente; estocado nas montanhas em promessa latente aguardando a fusão e fissão pacífica dos potentes geradores de uma aurora nuclear verde e limpa."},
        {"z": 91, "s": "Pa", "n": "Protactínio", "m": 231, "desc": "Actinídeo. Extramente restrito ao domínio isolado da curiosidade; desprendido entre subprodutos na desintegração rumo à estabilidade atômica nunca de fato consumada perfeitamente."},
        {"z": 92, "s": "U", "n": "Urânio", "m": 238, "desc": "Actinídeo. O combustível, o gigante, a arma formidável natural. Sustenta desde cidades inteiras perante ao inverno em reatores, aos abalos colossais de armamentos na história."},
        {"z": 93, "s": "Np", "n": "Netúnio", "m": 237, "desc": "Actinídeo. Ultrapassa Urano nos confins astronômicos, ultrapassa o Urânio no núcleo; a essência primordial nascida de experimentos nucleares no laboratório artificial pela humanidade."},
        {"z": 94, "s": "Pu", "n": "Plutônio", "m": 244, "desc": "Actinídeo. O poder de extermínio isolado pela corrida atômica; letal, mas essencial como a longa bateria durável no calor nuclear sustentando a vida solitária nas mais distantes sondas fora daqui."},
        {"z": 95, "s": "Am", "n": "Amerício", "m": 243, "desc": "Actinídeo. Seu detector microscópico salva a sua casa; as partículas alfa sentinelas rastreiam a fumaça de um princípio de fogo doméstico pelo bem da sociedade de consumo."},
        {"z": 96, "s": "Cm", "n": "Cúrio", "m": 247, "desc": "Actinídeo. A herança atômica para honrar o casal Marie e Pierre, fundadores da matéria radiológica moderna. Emite tanta radiação pura que emite luz em cor arroxeada radiante perante os detritos."},
        {"z": 97, "s": "Bk", "n": "Berquélio", "m": 247, "desc": "Actinídeo. Nomeado numa sincera saudação aos esforços intelectuais intensos nas colinas científicas de Berkeley, onde muitos grandes superpesados pela primeira vez nasceram nas sombras aceleradas de suas paredes."},
        {"z": 98, "s": "Cf", "n": "Califórnio", "m": 251, "desc": "Actinídeo. Tão intenso, caro e radioativo que um naco invisível metralha vastidões de nêutrons detectores até raspar e visualizar as bacias do fundo mais escondido de petróleo pelas sondas terrestres atuais."},
        {"z": 99, "s": "Es", "n": "Einstêinio", "m": 252, "desc": "Actinídeo. Nascido inicialmente dos detritos colossais do primeiro apocalíptico teste global no atol da coroa H; esculpido pelo calor incandescente em honra final de Albert Einstein."},
        {"z": 100, "s": "Fm", "n": "Férmio", "m": 257, "desc": "Actinídeo. A divisa de um horizonte. O ponto técnico máximo alcançável de fabricação atômica onde o puro e simples bombardeio em linha de nêutrons na matéria termina; Fermi eternizado pelo legado."},
        {"z": 101, "s": "Md", "n": "Mendelévio", "m": 258, "desc": "Actinídeo. Se Mendelévio pôde construir o panteão visual dos elementos do universo e ver os fantasmas antes deles preencherem as tabelas nas paredes, isso era o mínimo que a síntese atômica devia a ele."},
        {"z": 102, "s": "No", "n": "Nobélio", "m": 259, "desc": "Actinídeo. Carrega consigo o testamento intelectual do criador da dinamite para prêmios da glória eterna. Um espasmo da ciência moderna fundida temporariamente perante um complexo feixe num ciclotron fechado."},
        {"z": 103, "s": "Lr", "n": "Laurêncio", "m": 266, "desc": "Actinídeo. A derradeira encarnação entre as poeiras do mundo 'Actinídeo'. O selo onde as séries terminam e o oceano desconhecido de transição brutal recomeça num pilar instável rumo a limites massivos celestes."},
        {"z": 104, "s": "Rf", "n": "Rutherfórdio", "m": 267, "desc": "Metal de transição (Superpesado). A aurora da colisão gigantesca; marca a entrada no panteão pós-actinídeo na linha final sintética. Homenagem justa e exata ao brilhantismo do grande pioneiro neo-zelandês atômico, Rutherford."},
        {"z": 105, "s": "Db", "n": "Dúbnio", "m": 268, "desc": "Metal de transição (Superpesado). Celebra o centro de pesquisa nas gélidas paragens atômicas da Rússia em Dubna, de onde tantos choques massivos e revelações profundas ao abismo periódico super pesado jorraram ao longo da história secreta e partilhada."},
        {"z": 106, "s": "Sg", "n": "Seabórgio", "m": 269, "desc": "Metal de transição (Superpesado). Quando Glenn Seaborg respirou o ar vital e o nome do elemento foi estampado. Uma rara apoteose. Primeiro bloco a coroar e eternizar nominalmente no selo atômico global a glória científica final e total de um pesquisador ativamente respirando na Terra."},
        {"z": 107, "s": "Bh", "n": "Bóhrio", "m": 270, "desc": "Metal de transição (Superpesado). Homenagem àquele que entendeu de forma visionária os níveis eletrônicos quantificados orbitando no espaço de todo o universo; Niels Bohr é cravado junto no fundo massivo da tabela."},
        {"z": 108, "s": "Hs", "n": "Hássio", "m": 277, "desc": "Metal de transição (Superpesado). Forjado nas complexas instalações aceleradas de GSI da pequena e prolífica Darmstadt, Alemanha; batizado nas letras originais do imponente estado moderno Hesse."},
        {"z": 109, "s": "Mt", "n": "Meitnério", "m": 278, "desc": "Metal de transição (Superpesado). A glória para resgatar na matéria a dívida científica e intelectual e nomear nos anais temporais perante as estrelas o gênio incansável na fissão por Lise Meitner em sua contribuição monumental à física pesada."},
        {"z": 110, "s": "Ds", "n": "Darmstádio", "m": 281, "desc": "Metal de transição (Superpesado). Um efêmero gigante que atesta o pioneirismo exaustivo atômico do laboratório germânico GSI, que isolou perfeitamente nos ruídos estatísticos este titã e assinou o próprio nome geográfico na fundação básica da matéria moderna científica."},
        {"z": 111, "s": "Rg", "n": "Roentgênio", "m": 282, "desc": "Metal de transição (Superpesado). Em 1895, os misteriosos raios do desconhecido expuseram ossos através de mãos, virando a medicina e o entendimento global; cem anos depois um feixe exótico formava o centésimo décimo primeiro, reverenciando Röntgen permanentemente no panteão."},
        {"z": 112, "s": "Cn", "n": "Copernício", "m": 285, "desc": "Metal de transição (Superpesado). Os astros massivos obedecem a uma ordem, e o renascimento provou sua esfericidade no eixo solar; Nicolau Copérnico agora possui até seu monumental gigante girando rápido no micro universo quântico sob o peso opressor final instável artificial dos elementos de decaimento veloz."},
        {"z": 113, "s": "Nh", "n": "Nihônio", "m": 286, "desc": "Metal pós-transição (Superpesado). A tenacidade japonesa corou as ilhas nipônicas de suor científico; o Nihônio consolida formalmente as longas campanhas dedicadas pela RIKEN no Japão. O elemento que traz nas terras asiáticas a 'terra do sol nascente'."},
        {"z": 114, "s": "Fl", "n": "Fleróvio", "m": 289, "desc": "Metal pós-transição (Superpesado). Ponto chave da famigerada 'Ilha de Estabilidade' teórica nos oceanos quânticos superpesados; as portas do instituto russo Flerov provaram por meio destes isótopos exóticos as vidas mais longas em zonas que se acreditava intocáveis pela fissão."},
        {"z": 115, "s": "Mc", "n": "Moscóvio", "m": 290, "desc": "Metal pós-transição (Superpesado). Um testamento final geográfico entrelaçado da contínua e massiva expansão russo-norte americana nos fundos acelerados nucleares do planeta, cravando a província de Moscou para todo o sempre."},
        {"z": 116, "s": "Lv", "n": "Livermório", "m": 293, "desc": "Metal pós-transição (Superpesado). A grandiosa coautoria estadunidense e suas máquinas incansáveis no Lawrence Livermore National Lab. Estreitou mares e distâncias junto à Dubna para erguer o que apenas as fúrias caóticas estelares tentam fabricar sozinhas nas piores nebulosas da galáxia de forma volátil."},
        {"z": 117, "s": "Ts", "n": "Tenesso", "m": 294, "desc": "Halogênio (Superpesado). Sintetizando no apagar contínuo de flashes radiológicos incansáveis; exalta a terra americana do Tennessee na fundação colaborativa atômica com alvo e choque em escalas colossais que rasga as fronteiras estritamente conhecidas pela força universal."},
        {"z": 118, "s": "Og", "n": "Oganessônio", "m": 294, "desc": "Gás nobre (Superpesado). O cume. A fronteira limite onde a Tabela encerra seu ciclo visual provado em nosso século atual. Um titã instável. Coroando eternamente com júbilo o vivo formador atômico visionário Yuri Oganessian."}
    ]
    
    # Criando JSON complexo com variantes
    tabela = []
    for el in elementos_base:
        z = el["z"]
        neutrons_padrao = max(0, el["m"] - z)
        
        variantes = []
        # Variante comum (padrao)
        variantes.append({
            "nome_variante": f"Isótopo Comum ({el['s']}-{el['m']})",
            "p": z, "n": neutrons_padrao, "e": z,
            "info": el["desc"] + f"\n\nEste é o isótopo mais estável e abundante na natureza. Possui {z} prótons e {neutrons_padrao} nêutrons."
        })
        
        # Gerar mais 1 ou 2 isótopos fictícios/reais variando nêutrons
        if z == 1:
            variantes[0]["nome_variante"] = "Prótio"
            variantes.append({"nome_variante": "Deutério", "p": 1, "n": 1, "e": 1, "info": "O deutério é um isótopo estável do hidrogênio contendo um próton e um nêutron, usado na fabricação de água pesada para reatores nucleares."})
            variantes.append({"nome_variante": "Trítio", "p": 1, "n": 2, "e": 1, "info": "O trítio é o isótopo radioativo do hidrogênio. Muito raro na natureza, possui meia-vida de cerca de 12 anos e é usado em mostradores luminosos."})
        elif z == 6:
            variantes[0]["nome_variante"] = "Carbono-12"
            variantes.append({"nome_variante": "Carbono-13", "p": 6, "n": 7, "e": 6, "info": "Isótopo estável e mais pesado, usado frequentemente em pesquisas de ressonância magnética nuclear."})
            variantes.append({"nome_variante": "Carbono-14", "p": 6, "n": 8, "e": 6, "info": "Isótopo radioativo gerado na atmosfera por raios cósmicos. É amplamente utilizado na datação por radiocarbono de artefatos arqueológicos."})
        elif z == 92:
            variantes[0]["nome_variante"] = "Urânio-238"
            variantes.append({"nome_variante": "Urânio-235", "p": 92, "n": 143, "e": 92, "info": "Único isótopo físsil natural. Capaz de sustentar uma reação em cadeia de fissão nuclear, essencial para reatores e armas nucleares."})
        else:
            # Genérico para outros isótopos
            variantes.append({
                "nome_variante": f"Isótopo Mais Leve ({el['s']}-{el['m']-1})",
                "p": z, "n": max(0, neutrons_padrao - 1), "e": z,
                "info": f"Variante isotópica menos comum do {el['n']} contendo um nêutron a menos que a versão mais estável."
            })
            variantes.append({
                "nome_variante": f"Isótopo Mais Pesado ({el['s']}-{el['m']+1})",
                "p": z, "n": neutrons_padrao + 1, "e": z,
                "info": f"Isótopo mais pesado do {el['n']}, muitas vezes instável ou radioativo na natureza, comumente gerado em laboratório."
            })

        tabela.append({
            "nome": el["n"],
            "simbolo": el["s"],
            "z": z,
            "variantes": variantes
        })
    return json.dumps(tabela)

raw_data = gerar_dados_elementos()
database = json.loads(raw_data)

def configuracao_linus_pauling(eletrons):
    """
    Distribui os elétrons nas camadas K, L, M, N, O, P, Q 
    de acordo com a ordem energética de Linus Pauling.
    """
    # Ordem: (Camada 1-7, subnível, capacidade máxima)
    ordem_energetica = [
        (1, 2),   # 1s
        (2, 2),   # 2s
        (2, 6),   # 2p
        (3, 2),   # 3s
        (3, 6),   # 3p
        (4, 2),   # 4s
        (3, 10),  # 3d
        (4, 6),   # 4p
        (5, 2),   # 5s
        (4, 10),  # 4d
        (5, 6),   # 5p
        (6, 2),   # 6s
        (4, 14),  # 4f
        (5, 10),  # 5d
        (6, 6),   # 6p
        (7, 2),   # 7s
        (5, 14),  # 5f
        (6, 10),  # 6d
        (7, 6)    # 7p
    ]
    
    camadas = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    restantes = eletrons
    
    for camada, capacidade in ordem_energetica:
        if restantes <= 0:
            break
        alocados = min(restantes, capacidade)
        camadas[camada] += alocados
        restantes -= alocados
        
    # Retorna uma lista apenas com as camadas que possuem elétrons
    resultado = []
    for c in range(1, 8):
        if camadas[c] > 0:
            resultado.append(camadas[c])
    return resultado

def render_wrapped_text(surface, text, font, color, rect):
    """Renderiza texto quebrando as linhas para caber num Retângulo (Rect)"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        fw, fh = font.size(' '.join(current_line))
        if fw > rect.width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    y = rect.top
    for line in lines:
        if y + font.get_linesize() > rect.bottom:
            break # Evita desenhar fora do container
        text_surf = font.render(line, True, color)
        surface.blit(text_surf, (rect.left, y))
        y += font.get_linesize()

class Button:
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        color = COLOR_UI_HOVER if self.is_hovered else COLOR_UI_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLOR_UI_BORDER, self.rect, 1, border_radius=5)
        
        txt_surf = self.font.render(self.text, True, COLOR_TEXT)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

class Dropdown:
    def __init__(self, x, y, w, h, options, font, max_visible_items=8):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.selected_index = 0
        self.is_open = False
        self.font = font
        self.max_visible = max_visible_items
        self.scroll_offset = 0
        self.hovered_index = -1
        self.is_hovered = False

    def get_list_rect(self):
        visible = min(len(self.options), self.max_visible)
        return pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, self.rect.height * visible)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_open:
            list_rect = self.get_list_rect()
            if list_rect.collidepoint(mouse_pos):
                rel_y = mouse_pos[1] - self.rect.bottom
                idx = (rel_y // self.rect.height) + self.scroll_offset
                if 0 <= idx < len(self.options):
                    self.hovered_index = idx
                else:
                    self.hovered_index = -1
            else:
                self.hovered_index = -1

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Clique Esquerdo
                if self.is_hovered:
                    self.is_open = not self.is_open
                    return True
                elif self.is_open:
                    list_rect = self.get_list_rect()
                    if list_rect.collidepoint(event.pos):
                        if self.hovered_index != -1:
                            self.selected_index = self.hovered_index
                            self.is_open = False
                            return True
                    else:
                        self.is_open = False # Clicou fora, fecha o dropdown
            
            elif self.is_open and (event.button == 4 or event.button == 5): # Scroll do mouse
                list_rect = self.get_list_rect()
                if list_rect.collidepoint(event.pos):
                    if event.button == 4: # Scroll Up
                        self.scroll_offset = max(0, self.scroll_offset - 1)
                    elif event.button == 5: # Scroll Down
                        max_scroll = max(0, len(self.options) - self.max_visible)
                        self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
                    return True
        return False

    def draw(self, surface):
        # Caixa principal
        color = COLOR_UI_HOVER if (self.is_hovered or self.is_open) else COLOR_UI_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_UI_BORDER, self.rect, 1, border_radius=4)
        
        text_disp = self.font.render(self.options[self.selected_index], True, COLOR_TEXT)
        surface.blit(text_disp, (self.rect.x + 10, self.rect.y + (self.rect.height - text_disp.get_height())//2))
        
        # Desenha a lista se estiver aberto (geralmente chamado depois do resto da UI)
    
    def draw_list(self, surface):
        if not self.is_open:
            return
            
        list_rect = self.get_list_rect()
        pygame.draw.rect(surface, (45, 50, 60), list_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_UI_BORDER, list_rect, 1, border_radius=4)
        
        visible_options = min(len(self.options), self.max_visible)
        
        for i in range(visible_options):
            idx = self.scroll_offset + i
            if idx >= len(self.options):
                break
                
            item_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.height, self.rect.width, self.rect.height)
            
            if idx == self.hovered_index:
                pygame.draw.rect(surface, COLOR_UI_HOVER, item_rect)
            
            txt_surf = self.font.render(self.options[idx], True, COLOR_TEXT)
            surface.blit(txt_surf, (item_rect.x + 10, item_rect.y + (item_rect.height - txt_surf.get_height())//2))

class AtomRenderer:
    def __init__(self):
        self.zoom = 1.0
        self.time_passed = 0.0
        
        # Cache para partículas do núcleo
        self.cached_z = -1
        self.cached_n = -1
        self.nucleus_particles = [] 
        
        # Cache visual
        self.electron_glow = self.create_glow_surface(8, COLOR_ELECTRON)
        
    def create_glow_surface(self, radius, color):
        """Gera a superfície com efeito de brilho (alpha gradiente) para o elétron"""
        surf = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
        r, g, b = color
        for i in range(radius*2, 0, -1):
            alpha = int((1 - i/(radius*2)) * 180)
            pygame.draw.circle(surf, (r, g, b, alpha), (radius*2, radius*2), i)
        pygame.draw.circle(surf, (255, 255, 255, 255), (radius*2, radius*2), radius//2) # Núcleo do elétron super brilhante
        return surf

    def precompute_nucleus(self, p, n):
        """Usa a Espiral de Fermat para empacotar os prótons e nêutrons num círculo concêntrico perfeito"""
        if self.cached_z == p and self.cached_n == n:
            return # Já calculado
            
        self.nucleus_particles = []
        total_particles = p + n
        
        # Cria uma lista de tipos (True = Proton, False = Neutron)
        types = [True]*p + [False]*n
        random.seed(42) # Usando seed fixa para a aparência não piscar entre frames se recomputar
        random.shuffle(types)
        
        c = 4.5 # Fator de espaçamento
        
        for i in range(total_particles):
            # Espiral matemática:
            r = c * math.sqrt(i)
            theta = i * 137.508 * (math.pi / 180.0) # Golden angle
            
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            
            self.nucleus_particles.append({
                "x": x, "y": y, "is_proton": types[i]
            })
            
        self.cached_z = p
        self.cached_n = n

    def draw(self, surface, rect, variante, dt):
        self.time_passed += dt * 0.001 # dt em segundos
        
        center_x, center_y = rect.center
        
        p = variante["p"]
        n = variante["n"]
        e = variante["e"]
        
        self.precompute_nucleus(p, n)
        
        # --- DESENHO DAS ÓRBITAS E ELÉTRONS ---
        shells = configuracao_linus_pauling(e)
        base_orbit_radius = 50 # Raio inicial
        orbit_spacing = 35 # Espaço entre camadas
        
        for i, count in enumerate(shells):
            # Ajuste de escala para o zoom
            radius = (base_orbit_radius + i * orbit_spacing) * self.zoom
            
            # Desenhar linha da órbita
            pygame.draw.circle(surface, COLOR_ORBIT, (center_x, center_y), int(radius), 1)
            
            # Desenhar elétrons distribuídos pela órbita
            # Velocidade varia de acordo com a camada (mais próximas mais rápidas)
            speed = 1.5 / (i + 1)
            direction = 1 if i % 2 == 0 else -1 # Intercalar sentido da rotação
            
            angle_offset = self.time_passed * speed * direction
            
            for j in range(count):
                angle = angle_offset + (j * (2 * math.pi / count))
                ex = center_x + math.cos(angle) * radius
                ey = center_y + math.sin(angle) * radius
                
                # Renderiza elétron com brilho
                glow_rect = self.electron_glow.get_rect(center=(int(ex), int(ey)))
                surface.blit(self.electron_glow, glow_rect)
        
        # --- DESENHO DO NÚCLEO ---
        nucleus_scale = self.zoom
        particle_radius = max(2, int(3 * nucleus_scale))
        
        for part in self.nucleus_particles:
            px = center_x + part["x"] * nucleus_scale
            py = center_y + part["y"] * nucleus_scale
            
            color = COLOR_PROTON if part["is_proton"] else COLOR_NEUTRON
            pygame.draw.circle(surface, color, (int(px), int(py)), particle_radius)
            # Bordas escuras para profundidade
            pygame.draw.circle(surface, (10, 10, 15), (int(px), int(py)), particle_radius, 1)

def main():
    font_large = pygame.font.SysFont("segoeui, arial", 24, bold=True)
    font_medium = pygame.font.SysFont("segoeui, arial", 18)
    font_small = pygame.font.SysFont("segoeui, arial", 14)
    
    menu_width = 320
    
    # Preparando as opções do Dropdown de Elementos
    opcoes_elementos = [f"{el['z']} - {el['nome']} ({el['simbolo']})" for el in database]
    
    dropdown_elementos = Dropdown(20, 50, menu_width - 40, 40, opcoes_elementos, font_medium, max_visible_items=12)
    dropdown_variantes = Dropdown(20, 130, menu_width - 40, 40, [], font_medium)
    
    # Botões de Zoom
    btn_zoom_in = Button(0, 0, 40, 40, "+", font_large)
    btn_zoom_out = Button(0, 0, 40, 40, "-", font_large)
    
    atom_renderer = AtomRenderer()
    
    element_index = 0
    variant_index = 0
    
    def atualizar_variantes():
        nonlocal variant_index
        el = database[element_index]
        ops = [v["nome_variante"] for v in el["variantes"]]
        dropdown_variantes.options = ops
        dropdown_variantes.selected_index = 0
        dropdown_variantes.scroll_offset = 0
        variant_index = 0

    atualizar_variantes()
    
    running = True
    while running:
        dt = clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        w, h = screen.get_size()
        
        # Posiciona botões de zoom dinamicamente na tela da direita
        btn_zoom_in.rect.topleft = (w - 110, 20)
        btn_zoom_out.rect.topleft = (w - 60, 20)
        
        # Processamento de Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Atualiza Dropdowns (Atenção a ordem para impedir clique duplo.
            # O que desenha na frente recebe evento primeiro)
            handled = False
            if dropdown_variantes.is_open:
                handled = dropdown_variantes.handle_event(event)
                
            if not handled and dropdown_elementos.is_open:
                handled = dropdown_elementos.handle_event(event)
                if handled and not dropdown_elementos.is_open:
                    # Mudou elemento, atualiza lista de variantes
                    element_index = dropdown_elementos.selected_index
                    atualizar_variantes()
                    # Reseta o zoom pra ficar visualmente agradável no novo elemento
                    atom_renderer.zoom = 1.0

            if not handled:
                if dropdown_variantes.handle_event(event):
                    variant_index = dropdown_variantes.selected_index
                elif dropdown_elementos.handle_event(event):
                    if not dropdown_elementos.is_open:
                        element_index = dropdown_elementos.selected_index
                        atualizar_variantes()
                        atom_renderer.zoom = 1.0
            
            if btn_zoom_in.handle_event(event):
                atom_renderer.zoom = min(5.0, atom_renderer.zoom + 0.2)
            if btn_zoom_out.handle_event(event):
                atom_renderer.zoom = max(0.2, atom_renderer.zoom - 0.2)

        # Updates contínuos UI
        dropdown_elementos.update(mouse_pos)
        dropdown_variantes.update(mouse_pos)
        btn_zoom_in.update(mouse_pos)
        btn_zoom_out.update(mouse_pos)
        
        # --- RENDERIZAÇÃO ---
        screen.fill(COLOR_BG)
        
        # 1. Área do Átomo (Direita)
        atom_rect = pygame.Rect(menu_width, 0, w - menu_width, h)
        variante_atual = database[element_index]["variantes"][variant_index]
        atom_renderer.draw(screen, atom_rect, variante_atual, dt)
        
        # Botoes de Zoom
        btn_zoom_in.draw(screen)
        btn_zoom_out.draw(screen)
        
        # Tabela Pauling Textual na tela
        camadas_text = "Distribuição: " + " ".join([f"{c}e-" for c in configuracao_linus_pauling(variante_atual["e"])])
        pauling_surf = font_medium.render(camadas_text, True, COLOR_TEXT_DIM)
        screen.blit(pauling_surf, (menu_width + 20, 20))
        
        # 2. Área do Menu (Esquerda)
        menu_rect = pygame.Rect(0, 0, menu_width, h)
        pygame.draw.rect(screen, COLOR_MENU_BG, menu_rect)
        pygame.draw.line(screen, COLOR_UI_BORDER, (menu_width, 0), (menu_width, h), 2)
        
        # Textos do menu
        title_surf = font_medium.render("Elemento Químico:", True, COLOR_TEXT_DIM)
        screen.blit(title_surf, (20, 25))
        
        subtitle_surf = font_medium.render("Isótopo / Variante:", True, COLOR_TEXT_DIM)
        screen.blit(subtitle_surf, (20, 105))
        
        # Painel de Informações
        info_rect = pygame.Rect(20, 200, menu_width - 40, h - 220)
        pygame.draw.rect(screen, COLOR_UI_BG, info_rect, border_radius=5)
        
        # Textos informativos
        info_title = font_large.render("Informações", True, COLOR_TEXT)
        screen.blit(info_title, (info_rect.x + 15, info_rect.y + 15))
        
        stats_text = f"Prótons (Z): {variante_atual['p']}   |   Nêutrons (N): {variante_atual['n']}"
        stats_surf = font_medium.render(stats_text, True, COLOR_PROTON)
        screen.blit(stats_surf, (info_rect.x + 15, info_rect.y + 50))
        
        elec_text = f"Elétrons (E): {variante_atual['e']}"
        elec_surf = font_medium.render(elec_text, True, COLOR_ELECTRON)
        screen.blit(elec_surf, (info_rect.x + 15, info_rect.y + 75))
        
        # Descrição com quebra de linha
        desc_rect = pygame.Rect(info_rect.x + 15, info_rect.y + 120, info_rect.width - 30, info_rect.height - 130)
        render_wrapped_text(screen, variante_atual["info"], font_medium, COLOR_TEXT, desc_rect)
        
        # Elementos UI Desenhados por Último (Para sobrepor outras coisas, especialmente dropdowns)
        dropdown_elementos.draw(screen)
        dropdown_variantes.draw(screen)
        
        # Desenha as listas abertas no fim para sobrepor tudo!
        # Variante abre por cima do painel de info, elemento abre por cima da variante
        dropdown_variantes.draw_list(screen)
        dropdown_elementos.draw_list(screen)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()