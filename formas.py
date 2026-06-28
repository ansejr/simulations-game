import pygame
import pygame_gui
import math
import sys
import json
import os

# ==============================================================================
# DICIONÁRIOS E REGRAS DE TRADUÇÃO E INTERNACIONALIZAÇÃO (i18n)
# ==============================================================================
IDIOMAS = {
    "Português": "pt",
    "Español": "es",
    "English": "en",
    "Greek (Ελληνικά)": "el",
    "Chinese (中文)": "zh",
    "Japanese (日本語)": "ja",
    "Arabic (العربية)": "ar",
    "Hindi (हिन्दी)": "hi"
}

# Tradução direta para formas estáticas/especiais
FORMAS_ESTATICAS_TRADUZIDAS = {
    "pt": {
        "Ponto": "Ponto", "Linha": "Linha", "Triângulo": "Triângulo", "Quadrilátero": "Quadrilátero",
        "Estrela (5 Pontas)": "Estrela (5 Pontas)", "Pentagrama": "Pentagrama", "Estrela de Davi": "Estrela de Davi",
        "Cubo (Isométrico)": "Cubo (Isométrico)", "Coração": "Coração", "Infinito": "Infinito",
        "Engrenagem": "Engrenagem", "Borboleta": "Borboleta", "Símbolo do Batman": "Símbolo do Batman",
        "Rosa Polar (4 Pétalas)": "Rosa Polar (4 Pétalas)", "Rosa Polar (5 Pétalas)": "Rosa Polar (5 Pétalas)",
        "Rosa Polar (8 Pétalas)": "Rosa Polar (8 Pétalas)", "Lágrima": "Lágrima", "Estrela Ninja (Shuriken)": "Estrela Ninja (Shuriken)",
        "Cruz": "Cruz", "Raio": "Raio", "Ampulheta": "Ampulheta", "Triângulo Místico": "Triângulo Místico",
        "Heptagrama": "Heptagrama", "Octagrama": "Octagrama", "Dodecagrama": "Dodecagrama", "Seta": "Seta",
        "Círculo Perfeito": "Círculo Perfeito", "Asteroide": "Asteroide", "Deltoide": "Deltoide",
        "Superelipse (Squircle)": "Superelipse (Squircle)", "Ovo": "Ovo", "Lissajous (3:2)": "Lissajous (3:2)",
        "Lissajous (5:4)": "Lissajous (5:4)", "Gota d'Água": "Gota d'Água", "Bifolium": "Bifolium",
        "Trevo (3 Folhas)": "Trevo (3 Folhas)", "Trevo (4 Folhas)": "Trevo (4 Folhas)", "Lente (Vesica Piscis)": "Lente (Vesica Piscis)",
        "Pac-Man": "Pac-Man", "Cápsula": "Cápsula", "Meia-Lua": "Meia-Lua", "Cruz de Malta": "Cruz de Malta",
        "Diamante": "Diamante", "Pipa": "Pipa", "Trapézio": "Trapézio", "Hexágono Côncavo": "Hexágono Côncavo",
        "Escudo": "Escudo", "Espada": "Espada", "Coroa": "Coroa", "Pinheiro": "Pinheiro", "Bumerangue": "Bumerangue",
        "Seta Dupla": "Seta Dupla", "Balão": "Balão", "Sinal de Adição": "Sinal de Adição", "Estrela (4 Pontas)": "Estrela (4 Pontas)",
        "Ziguezague Circular": "Ziguezague Circular", "Engrenagem Quadrada": "Engrenagem Quadrada"
    },
    "es": {
        "Ponto": "Punto", "Linha": "Línea", "Triângulo": "Triángulo", "Quadrilátero": "Cuadrilátero",
        "Estrela (5 Pontas)": "Estrella (5 Puntas)", "Pentagrama": "Pentagrama", "Estrela de Davi": "Estrella de David",
        "Cubo (Isométrico)": "Cubo (Isométrico)", "Coração": "Corazón", "Infinito": "Infinito",
        "Engrenagem": "Engranaje", "Borboleta": "Mariposa", "Símbolo do Batman": "Símbolo de Batman",
        "Rosa Polar (4 Pétalas)": "Rosa Polar (4 Pétalos)", "Rosa Polar (5 Pétalas)": "Rosa Polar (5 Pétalos)",
        "Rosa Polar (8 Pétalas)": "Rosa Polar (8 Pétalos)", "Lágrima": "Lágrima", "Estrela Ninja (Shuriken)": "Estrella Ninja (Shuriken)",
        "Cruz": "Cruz", "Raio": "Rayo", "Ampulheta": "Reloj de Arena", "Triângulo Místico": "Triángulo Místico",
        "Heptagrama": "Heptagrama", "Octagrama": "Octagrama", "Dodecagrama": "Dodecagrama", "Seta": "Flecha",
        "Círculo Perfeito": "Círculo Perfecto", "Asteroide": "Asteroide", "Deltoide": "Deltoide",
        "Superelipse (Squircle)": "Superelipse (Squircle)", "Ovo": "Huevo", "Lissajous (3:2)": "Lissajous (3:2)",
        "Lissajous (5:4)": "Lissajous (5:4)", "Gota d'Água": "Gota de Agua", "Bifolium": "Bifolium",
        "Trevo (3 Folhas)": "Trébol (3 Hojas)", "Trevo (4 Folhas)": "Trébol (4 Hojas)", "Lente (Vesica Piscis)": "Lente (Vesica Piscis)",
        "Pac-Man": "Pac-Man", "Cápsula": "Cápsula", "Meia-Lua": "Media Luna", "Cruz de Malta": "Cruz de Malta",
        "Diamante": "Diamante", "Pipa": "Cometa", "Trapézio": "Trapecio", "Hexágono Côncavo": "Hexágono Cóncavo",
        "Escudo": "Escudo", "Espada": "Espada", "Coroa": "Corona", "Pinheiro": "Pino", "Bumerangue": "Búmeran",
        "Seta Dupla": "Flecha Doble", "Balão": "Globo", "Sinal de Adição": "Signo de Suma", "Estrela (4 Pontas)": "Estrella (4 Puntas)",
        "Ziguezague Circular": "Zigzag Circular", "Engrenagem Quadrada": "Engranaje Cuadrado"
    },
    "en": {
        "Ponto": "Point", "Linha": "Line", "Triângulo": "Triangle", "Quadrilátero": "Quadrilateral",
        "Estrela (5 Pontas)": "Star (5 Points)", "Pentagrama": "Pentagrama", "Estrela de Davi": "Star of David",
        "Cubo (Isométrico)": "Cube (Isometric)", "Coração": "Heart", "Infinito": "Infinity",
        "Engrenagem": "Gear", "Borboleta": "Butterfly", "Símbolo do Batman": "Batman Symbol",
        "Rosa Polar (4 Pétalas)": "Rose Curve (4 Petals)", "Rosa Polar (5 Pétalas)": "Rose Curve (5 Petals)",
        "Rosa Polar (8 Pétalas)": "Rose Curve (8 Petals)", "Lágrima": "Teardrop", "Estrela Ninja (Shuriken)": "Ninja Star (Shuriken)",
        "Cruz": "Cross", "Raio": "Lightning Bolt", "Ampulheta": "Hourglass", "Triângulo Místico": "Mystic Triangle",
        "Heptagrama": "Heptagram", "Octagrama": "Octagram", "Dodecagrama": "Dodecagram", "Seta": "Arrow",
        "Círculo Perfeito": "Perfect Circle", "Asteroide": "Astroid", "Deltoide": "Deltoid",
        "Superelipse (Squircle)": "Squircle", "Ovo": "Egg", "Lissajous (3:2)": "Lissajous (3:2)",
        "Lissajous (5:4)": "Lissajous (5:4)", "Gota d'Água": "Water Droplet", "Bifolium": "Bifolium",
        "Trevo (3 Folhas)": "Clover (3 Leaves)", "Trevo (4 Folhas)": "Clover (4 Leaves)", "Lente (Vesica Piscis)": "Lens (Vesica Piscis)",
        "Pac-Man": "Pac-Man", "Cápsula": "Capsule", "Meia-Lua": "Crescent Moon", "Cruz de Malta": "Maltese Cross",
        "Diamante": "Diamond", "Pipa": "Kite", "Trapézio": "Trapezoid", "Hexágono Côncavo": "Concave Hexagon",
        "Escudo": "Shield", "Espada": "Sword", "Coroa": "Crown", "Pinheiro": "Pine Tree", "Bumerangue": "Boomerang",
        "Seta Dupla": "Double Arrow", "Balão": "Balloon", "Sinal de Adição": "Plus Sign", "Estrela (4 Pontas)": "Star (4 Points)",
        "Ziguezague Circular": "Circular Zigzag", "Engrenagem Quadrada": "Square Gear"
    },
    "el": {
        "Ponto": "Σημείο", "Linha": "Γραμμή", "Triângulo": "Τρίγωνο", "Quadrilátero": "Τετράπλευρο",
        "Estrela (5 Pontas)": "Αστέρι (5 Άκρες)", "Pentagrama": "Πεντάγραμμο", "Estrela de Davi": "Άστρο του Δαβίδ",
        "Cubo (Isométrico)": "Κύβος (Ισομετρικός)", "Coração": "Καρδιά", "Infinito": "Άπειρο",
        "Engrenagem": "Γρανάζι", "Borboleta": "Πεταλούδα", "Símbolo do Batman": "Σύμβολο Μπάτμαν",
        "Rosa Polar (4 Pétalas)": "Ρόδο (4 Πέταλα)", "Rosa Polar (5 Pétalas)": "Ρόδο (5 Πέταλα)",
        "Rosa Polar (8 Pétalas)": "Ρόδο (8 Πέταλα)", "Lágrima": "Δάκρυ", "Estrela Ninja (Shuriken)": "Νίντζα Αστέρι",
        "Cruz": "Σταυρός", "Raio": "Κεραυνός", "Ampulheta": "Κλεψύδρα", "Triângulo Místico": "Μυστικό Τρίγωνο",
        "Heptagrama": "Επτάγραμμο", "Octagrama": "Οκτάγραμμο", "Dodecagrama": "Δωδεκάγραμμο", "Seta": "Βέλος",
        "Círculo Perfeito": "Τέλειος Κύκλος", "Asteroide": "Αστεροειδής", "Deltoide": "Δελτοειδές",
        "Superelipse (Squircle)": "Υπερελλειπτικό", "Ovo": "Αυγό", "Lissajous (3:2)": "Lissajous (3:2)",
        "Lissajous (5:4)": "Lissajous (5:4)", "Gota d'Água": "Σταγόνα Νερού", "Bifolium": "Δίφυλλο",
        "Trevo (3 Folhas)": "Τριφύλλι (3 Φύλλα)", "Trevo (4 Folhas)": "Τετράφυλλο Τριφύλλι", "Lente (Vesica Piscis)": "Φακός",
        "Pac-Man": "Pac-Man", "Cápsula": "Κάψουλα", "Meia-Lua": "Μισοφέγγαρο", "Cruz de Malta": "Σταυρός της Μάλτας",
        "Diamante": "Ρόμβος", "Pipa": "Χαρταετός", "Trapézio": "Τραπέζιο", "Hexágono Côncavo": "Κοίλο Εξάγωνο",
        "Escudo": "Ασπίδα", "Espada": "Σπαθί", "Coroa": "Στέμμα", "Pinheiro": "Πεύκο", "Bumerangue": "Μπούμερανγκ",
        "Seta Dupla": "Διπλό Βέλος", "Balão": "Μπαλόνι", "Sinal de Adição": "Συν", "Estrela (4 Pontas)": "Αστέρι (4 Άκρες)",
        "Ziguezague Circular": "Κυκλικό Ζιγκ-Ζαγκ", "Engrenagem Quadrada": "Τετράγωνο Γρανάζι"
    },
    "zh": {
        "Ponto": "点", "Linha": "线", "Triângulo": "三角形", "Quadrilátero": "四边形",
        "Estrela (5 Pontas)": "五角星", "Pentagrama": "五角星线", "Estrela de Davi": "大卫之星",
        "Cubo (Isométrico)": "等轴立方体", "Coração": "心形", "Infinito": "无限",
        "Engrenagem": "齿轮", "Borboleta": "蝴蝶形", "Símbolo do Batman": "蝙蝠侠标志",
        "Rosa Polar (4 Pétalas)": "玫瑰线 (4 瓣)", "Rosa Polar (5 Pétalas)": "玫瑰线 (5 瓣)",
        "Rosa Polar (8 Pétalas)": "玫瑰线 (8 瓣)", "Lágrima": "泪滴", "Estrela Ninja (Shuriken)": "忍者手里剑",
        "Cruz": "十字架", "Raio": "闪电", "Ampulheta": "沙漏", "Triângulo Místico": "神秘三角形",
        "Heptagrama": "七角星", "Octagrama": "八角星", "Dodecagrama": "十二角星", "Seta": "箭头",
        "Círculo Perfeito": "完美圆形", "Asteroide": "星形线", "Deltoide": "内摆线",
        "Superelipse (Squircle)": "超椭圆", "Ovo": "蛋形", "Lissajous (3:2)": "利萨茹 (3:2)",
        "Lissajous (5:4)": "利萨茹 (5:4)", "Gota d'Água": "水滴", "Bifolium": "双叶线",
        "Trevo (3 Folhas)": "三叶草", "Trevo (4 Folhas)": "四叶草", "Lente (Vesica Piscis)": "透镜",
        "Pac-Man": "吃豆人", "Cápsula": "胶囊形", "Meia-Lua": "新月形", "Cruz de Malta": "马耳他十字",
        "Diamante": "菱形", "Pipa": "风筝形", "Trapézio": "梯形", "Hexágono Côncavo": "凹六边形",
        "Escudo": "盾牌", "Espada": "剑", "Coroa": "皇冠", "Pinheiro": "松树", "Bumerangue": "回力镖",
        "Seta Dupla": "双向箭头", "Balão": "气球", "Sinal de Adição": "加号", "Estrela (4 Pontas)": "四角星",
        "Ziguezague Circular": "圆周锯齿", "Engrenagem Quadrada": "方形齿轮"
    },
    "ja": {
        "Ponto": "点", "Linha": "線", "Triângulo": "三角形", "Quadrilátero": "四角形",
        "Estrela (5 Pontas)": "星型 (5角)", "Pentagrama": "ペンタグラム", "Estrela de Davi": "ダビデの星",
        "Cubo (Isométrico)": "アイソメトリック立方体", "Coração": "ハート型", "Infinito": "無限",
        "Engrenagem": "歯車", "Borboleta": "バタフライ曲線", "Símbolo do Batman": "バットマンマーク",
        "Rosa Polar (4 Pétalas)": "バラ曲線 (4弁)", "Rosa Polar (5 Pétalas)": "バラ曲線 (5弁)",
        "Rosa Polar (8 Pétalas)": "バラ曲線 (8弁)", "Lágrima": "涙滴型", "Estrela Ninja (Shuriken)": "手裏剣",
        "Cruz": "十字", "Raio": "稲妻", "Ampulheta": "砂時計", "Triângulo Místico": "神秘の三角形",
        "Heptagrama": "ヘプタグラム", "Octagrama": "オクタグラム", "Dodecagrama": "ドデカグラム", "Seta": "矢印",
        "Círculo Perfeito": "真円", "Asteroide": "アステロイド", "Deltoide": "デルトイド",
        "Superelipse (Squircle)": "スクアクル", "Ovo": "卵型", "Lissajous (3:2)": "リサージュ (3:2)",
        "Lissajous (5:4)": "リサージュ (5:4)", "Gota d'Água": "水滴", "Bifolium": "二葉線",
        "Trevo (3 Folhas)": "三つ葉", "Trevo (4 Folhas)": "四つ葉のクローバー", "Lente (Vesica Piscis)": "レンズ型",
        "Pac-Man": "パックマン", "Cápsula": "カプセル", "Meia-Lua": "三日月", "Cruz de Malta": "マルタ十字",
        "Diamante": "ひし形", "Pipa": "凧型", "Trapézio": "台形", "Hexágono Côncavo": "凹六角形",
        "Escudo": "盾", "Espada": "剣", "Coroa": "王冠", "Pinheiro": "松の木", "Bumerangue": "ブーメラン",
        "Seta Dupla": "両方向矢印", "Balão": "風船", "Sinal de Adição": "プラス記号", "Estrela (4 Pontas)": "星型 (4角)",
        "Ziguezague Circular": "円形ジグザグ", "Engrenagem Quadrada": "四角い歯車"
    },
    "ar": {
        "Ponto": "نقطة", "Linha": "خط", "Triângulo": "مثلت", "Quadrilátero": "رباعي الأضلاع",
        "Estrela (5 Pontas)": "نجمة (5 نقاط)", "Pentagrama": "نجمة خماسية", "Estrela de Davi": "نجمة داود",
        "Cubo (Isométrico)": "مكعب متساوي القياس", "Coração": "قلب", "Infinito": "لانهاية",
        "Engrenagem": "ترس", "Borboleta": "فراشة", "Símbolo do Batman": "شعار باتمان",
        "Rosa Polar (4 Pétalas)": "منحنى وردي (4 بتلات)", "Rosa Polar (5 Pétalas)": "منحنى وردي (5 بتلات)",
        "Rosa Polar (8 Pétalas)": "منحنى وردي (8 بتلات)", "Lágrima": "دمعة", "Estrela Ninja (Shuriken)": "نجمة النينجا",
        "Cruz": "صليب", "Raio": "برق", "Ampulheta": "ساعة رملية", "Triângulo Místico": "المثلث الغامض",
        "Heptagrama": "مسبع", "Octagrama": "مثمن", "Dodecagrama": "اثنا عشري الأضلاع نجمي", "Seta": "سهم",
        "Círculo Perfeito": "دائرة مثالية", "Asteroide": "منحنى نجمي", "Deltoide": "دلتاوي",
        "Superelipse (Squircle)": "مربع مستدير", "Ovo": "بيضة", "Lissajous (3:2)": "ليساجو (3:2)",
        "Lissajous (5:4)": "ليساجو (5:4)", "Gota d'Água": "قطرة ماء", "Bifolium": "ثنائي الأوراق",
        "Trevo (3 Folhas)": "برسيم ثلاثي الأوراق", "Trevo (4 Folhas)": "برسيم رباعي الأوراق", "Lente (Vesica Piscis)": "عدسة",
        "Pac-Man": "باك مان", "Cápsula": "كبسولة", "Meia-Lua": "هلال", "Cruz de Malta": "صليب مالطا",
        "Diamante": "معين", "Pipa": "طائرة ورقية", "Trapézio": "شبه منحرف", "Hexágono Côncavo": "مسدس مقعر",
        "Escudo": "درع", "Espada": "سيف", "Coroa": "تاج", "Pinheiro": "شجرة صنوبر", "Bumerangue": "بومرنغ",
        "Seta Dupla": "سهم مزدوج", "Balão": "بالون", "Sinal de Adição": "علامة زائد", "Estrela (4 Pontas)": "نجمة (4 نقاط)",
        "Ziguezague Circular": "عرجاء دائرية", "Engrenagem Quadrada": "ترس مربع"
    },
    "hi": {
        "Ponto": "बिंदु", "Linha": "रेखा", "Triângulo": "त्रिकोण", "Quadrilátero": "चतुर्भुज",
        "Estrela (5 Pontas)": "तारा (5 कोने)", "Pentagrama": "पंचकोण तारा", "Estrela de Davi": "डेविड का तारा",
        "Cubo (Isométrico)": "घन (आइसोमेट्रिक)", "Coração": "दिल", "Infinito": "अनंत",
        "Engrenagem": "गियर", "Borboleta": "तितली वक्र", "Símbolo do Batman": "बैटमैन का प्रतीक",
        "Rosa Polar (4 Pétalas)": "ध्रुवीय गुलाब (4 पंखुड़ी)", "Rosa Polar (5 Pétalas)": "ध्रुवीय गुलाब (5 पंखुड़ी)",
        "Rosa Polar (8 Pétalas)": "ध्रुवीय गुलाब (8 पंखुड़ी)", "Lágrima": "आँसू की बूंद", "Estrela Ninja (Shuriken)": "निंजा स्टार",
        "Cruz": "क्रॉस", "Raio": "बिजली", "Ampulheta": "बालूघड़ी", "Triângulo Místico": "रहस्यमयी त्रिकोण",
        "Heptagrama": "सप्तकोण", "Octagrama": "अष्टकोण", "Dodecagrama": "द्वादशकोण", "Seta": "तीर",
        "Círculo Perfeito": "पूर्ण वृत्त", "Asteroide": "एस्ट्रोइड", "Deltoide": "डेल्टॉइड",
        "Superelipse (Squircle)": "स्क्विर्कल", "Ovo": "अंडा", "Lissajous (3:2)": "लिसाजूस (3:2)",
        "Lissajous (5:4)": "लिसाजूस (5:4)", "Gota d'Água": "पानी की बूंद", "Bifolium": "बाइफोलियम",
        "Trevo (3 Folhas)": "तीन पत्तियों वाला तिपतिया", "Trevo (4 Folhas)": "चार पत्तियों वाला तिपतिया", "Lente (Vesica Piscis)": "लेंस",
        "Pac-Man": "पैक-मैन", "Cápsula": "कैप्सूल", "Meia-Lua": "अर्धचंद्र", "Cruz de Malta": "माल्टीज़ क्रॉस",
        "Diamante": "हीरा", "Pipa": "पतंग", "Trapézio": "समलम्ब", "Hexágono Côncavo": "अवतल षट्कोण",
        "Escudo": "ढाल", "Espada": "तलवार", "Coroa": "मुकुट", "Pinheiro": "देवदार का पेड़", "Bumerangue": "बूमरैंग",
        "Seta Dupla": "दोहरा तीर", "Balão": "गुब्बारा", "Sinal de Adição": "प्लस का चिह्न", "Estrela (4 Pontas)": "तारा (4 कोने)",
        "Ziguezague Circular": "वृत्ताकार ज़िगज़ैग", "Engrenagem Quadrada": "वर्गाकार गियर"
    }
}

# Tradução dos sufixos para geração paramétrica livre
SUFIXOS = {
    "pt": {"gono": "ágono", "grama": "grama", "flor": "flor"},
    "es": {"gono": "ágono", "grama": "grama", "flor": "flor"},
    "en": {"gono": "gon", "grama": "gram", "flor": "flower"},
    "el": {"gono": "γωνο", "grama": "γραμμο", "flor": "λούλουδο"},
    "zh": {"gono": "边形", "grama": "角星", "flor": "瓣花"},
    "ja": {"gono": "角形", "grama": "角星", "flor": "枚の葉の花"},
    "ar": {"gono": " أضلاع", "grama": " نجمي", "flor": " زهرة"},
    "hi": {"gono": "भुज", "grama": " कोणीय तारा", "flor": " पंखुड़ियों का फूल"}
}

# ==============================================================================
# ALGORITMO DE NOMENCLATURA MULTILÍNGUE (Suporta até 99.999)
# ==============================================================================
def obter_nome_forma_i18n(n, tipo_sufixo, lang):
    """
    Retorna o nome correto do polígono em Português, Espanhol, Inglês, Grego,
    Chinês, Japonês, Árabe ou Hindi até 99.999 lados/pontas/pétalas.
    """
    # Casos triviais
    if n == 1:
        trad_ponto = {"pt": "Ponto", "es": "Punto", "en": "Point", "el": "Σημείο", "zh": "点", "ja": "点", "ar": "نقطة", "hi": "बिंदु"}
        return trad_ponto.get(lang, "Ponto")
    if n == 2:
        trad_linha = {"pt": "Linha", "es": "Línea", "en": "Line", "el": "Γραμμή", "zh": "线", "ja": "線", "ar": "خط", "hi": "रेखा"}
        return trad_linha.get(lang, "Linha")

    suf_dict = SUFIXOS.get(lang, SUFIXOS["pt"])
    suf = suf_dict.get(tipo_sufixo, "gono")

    if lang in ["zh", "ja"]:
        return f"{n}{suf}"

    if lang in ["ar", "hi"]:
        if lang == "ar":
            if tipo_sufixo == "gono": return f"شكل ذو {n}{suf}"
            elif tipo_sufixo == "grama": return f"نجمة ذات {n}{suf}"
            return f"زهرة ذات {n}{suf}"
        elif lang == "hi":
            return f"{n}{suf}"

    unidades = ["", "hena", "di", "tri", "tetra", "penta", "hexa", "hepta", "octa", "enea"]
    dezenas = ["", "deca", "icosa", "triaconta", "tetraconta", "pentaconta", "hexaconta", "heptaconta", "octaconta", "eneaconta"]
    centenas = ["", "hecto", "diacosi", "triacosi", "tetracosi", "pentacosi", "hexacosi", "heptacosi", "octacosi", "eneacosi"]
    milhares = ["", "quilia", "diquilia", "triquilia", "tetraquilia", "pentaquilia", "hexaquilia", "heptaquilia", "octaquilia", "eneaquilia"]
    miriades = ["", "miria", "dimiria", "trimiria", "tetramiria", "pentamiria", "hexamiria", "heptamiria", "octamiria", "eneamiria"]

    if lang == "el":
        unidades = ["", "μονο", "δι", "τρι", "τετρα", "πεντα", "εξα", "επτα", "οκτω", "εννεα"]
        dezenas = ["", "δεκα", "εικοσι", "τριακοντα", "σαραντα", "πενηντα", "εξηντα", "εβδομηντα", "ογδοντα", "ενενηντα"]
        centenas = ["", "εκατοντα", "διακοσι", "τριακοσι", "τετρακοσι", "πεντακοσι", "εξακοσι", "επτακοσι", "οκτωκοσι", "εννεακοσι"]
        milhares = ["", "χιλια", "δισχιλια", "τρισχιλια", "τετραχιλια", "πενταχιλια", "εξαχιλια", "επταχιλια", "οκτωχιλια", "εννεαχιλια"]
        miriades = ["", "μυρια", "δισμυρια", "τρισμυρια", "τετραμυρια", "πενταμυρια", "εξαμυρια", "επταμυρια", "οκτωμυρια", "εννεαμυρια"]

    n_seguro = min(n, 99999)
    s = str(n_seguro).zfill(5)
    mi, m, c, d, u = int(s[0]), int(s[1]), int(s[2]), int(s[3]), int(s[4])
    prefixo = ""

    if mi > 0:
        if mi == 1 and m == 0 and c == 0 and d == 0 and u == 0:
            if lang == "el": return "Μυριάγωνο"
            return f"Miria{suf}".capitalize()
        prefixo += miriades[mi]
    if m > 0: prefixo += milhares[m]
    if c > 0: prefixo += centenas[c]

    if d == 1:
        if lang == "el":
            excecoes_dez = ["δεκα", "ενδεκα", "δωδεκα", "δεκατρια", "δεκατεσσερα", "δεκαπεντε", "δεκαεξι", "δεκαεπτα", "δεκαοκτω", "δεκαεννεα"]
        else:
            excecoes_dez = ["deca", "hendeca", "dodeca", "trideca", "tetradeca", "pentadeca", "hexadeca", "heptadeca", "octadeca", "eneadeca"]
        prefixo += excecoes_dez[u]
        u = 0
    elif d > 1:
        prefixo += dezenas[d]

    if u > 0: prefixo += unidades[u]

    if lang != "el":
        prefixo = prefixo.replace("aa", "a").replace("oo", "o").replace("ao", "o").replace("ea", "e")

    if lang == "pt":
        if tipo_sufixo == "gono":
            if prefixo.endswith("a"): prefixo = prefixo[:-1] + "ágono"
            elif prefixo.endswith("o"): prefixo = prefixo[:-1] + "ógono"
            elif prefixo.endswith("e"): prefixo = prefixo[:-1] + "égono"
            elif prefixo.endswith("i"): prefixo = prefixo[:-1] + "ígono"
            else: prefixo += "gono"
        else:
            prefixo += suf
    elif lang == "es":
        if tipo_sufixo == "gono":
            if prefixo.endswith("a"): prefixo = prefixo[:-1] + "ágono"
            elif prefixo.endswith("o"): prefixo = prefixo[:-1] + "ógono"
            elif prefixo.endswith("e"): prefixo = prefixo[:-1] + "égono"
            elif prefixo.endswith("i"): prefixo = prefixo[:-1] + "ígono"
            else: prefixo += "gono"
        else:
            prefixo += suf
    elif lang == "en":
        prefixo += suf
    elif lang == "el":
        prefixo += suf

    return prefixo.capitalize()

# ==============================================================================
# MOTOR MATEMÁTICO DE FORMAS ESPECIAIS E LIVRES
# ==============================================================================
def gerar_forma_livre(n, raio):
    return [(raio * math.cos(-math.pi/2 + 2*math.pi*i/n), raio * math.sin(-math.pi/2 + 2*math.pi*i/n)) for i in range(n)]

def gerar_estrela_livre(n, raio):
    if n < 2: return gerar_forma_livre(n, raio)
    pts = []
    for i in range(2 * n):
        r = raio if i % 2 == 0 else raio * 0.4
        a = -math.pi/2 + math.pi*i/n
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts

def gerar_flor_livre(n, raio):
    pts = []
    n_pontos = max(100, n * 15)
    for i in range(n_pontos):
        t = 2 * math.pi * i / n_pontos
        r = raio * (0.6 + 0.4 * math.cos(n * t))
        pts.append((r * math.cos(t), r * math.sin(t)))
    return pts

def gerar_estrela(raio):
    pts = []
    for i in range(10):
        r = raio if i % 2 == 0 else raio * 0.4
        a = -math.pi/2 + 2*math.pi*i/10
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts

def gerar_pentagrama(raio):
    return [(raio * math.cos(-math.pi/2 + 4*math.pi*i/5), raio * math.sin(-math.pi/2 + 4*math.pi*i/5)) for i in range(5)]

def gerar_estrela_davi(raio):
    pts = []
    for i in range(12):
        r = raio if i % 2 == 0 else raio * 0.577
        a = -math.pi/2 + 2*math.pi*i/12
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts

def gerar_cubo_isometrico(raio):
    a = [math.pi/6 + 2*math.pi*i/6 for i in range(6)]
    hex_pts = [(raio * math.cos(ang), raio * math.sin(ang)) for ang in a]
    centro = (0, 0)
    return [hex_pts[0], hex_pts[1], hex_pts[2], hex_pts[3], hex_pts[4], hex_pts[5], hex_pts[0], centro, hex_pts[2], centro, hex_pts[4]]

def gerar_coracao(raio):
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        x = 16 * (math.sin(t)**3)
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        pts.append((x * (raio/16), y * (raio/16)))
    return pts

def gerar_infinito(raio):
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        den = 1 + math.sin(t)**2
        x = (raio * math.sqrt(2) * math.cos(t)) / den
        y = (raio * math.sqrt(2) * math.cos(t) * math.sin(t)) / den
        pts.append((x, y))
    return pts

def gerar_engrenagem(raio):
    pts = []
    dentes = 8
    for i in range(80):
        t = 2 * math.pi * i / 80
        r = raio * (0.8 + 0.2 * math.cos(dentes * t))
        pts.append((r * math.cos(t), r * math.sin(t)))
    return pts

def gerar_borboleta(raio):
    pts = []
    for i in range(120):
        t = 12 * math.pi * i / 120
        r = math.exp(math.sin(t)) - 2 * math.cos(4*t) + (math.sin((2*t - math.pi)/24)**5)
        pts.append(((r * math.cos(t)) * (raio/3.5), -(r * math.sin(t)) * (raio/3.5)))
    return pts

def gerar_cruz(raio):
    r1, r2 = raio, raio * 0.3
    return [
        (r2, -r1), (r2, -r2), (r1, -r2), (r1, r2),
        (r2, r2), (r2, r1), (-r2, r1), (-r2, r2),
        (-r1, r2), (-r1, -r2), (-r2, -r2), (-r2, -r1)
    ]

def gerar_rosa_polar(raio, petalas):
    pts = []
    n_pontos = 100
    for i in range(n_pontos):
        t = 2 * math.pi * i / n_pontos
        r = raio * math.cos(petalas * t)
        pts.append((r * math.cos(t), r * math.sin(t)))
    return pts

def gerar_lagrima(raio):
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        x = raio * 0.5 * (1 - math.sin(t)) * math.cos(t)
        y = -raio * (math.sin(t) - 0.5)
        pts.append((x, y))
    return pts

def gerar_shuriken(raio):
    pts = []
    for i in range(8):
        r = raio if i % 2 == 0 else raio * 0.2
        a = -math.pi/2 + 2*math.pi*i/8
        a_offset = a + (0.3 if i % 2 != 0 else 0)
        pts.append((r * math.cos(a_offset), r * math.sin(a_offset)))
    return pts

def gerar_ampulheta(raio):
    return [(-raio, -raio), (raio, -raio), (-raio, raio), (raio, raio)]

def gerar_raio(raio):
    return [(0, -raio), (raio*0.4, 0), (raio*0.1, 0), (raio*0.3, raio), (-raio*0.4, -raio*0.1), (-raio*0.1, -raio*0.1)]

def gerar_batman(raio):
    right_half = [
        (0.0, 0.5), (0.05, 0.5), (0.1, 0.7), (0.15, 0.4), (0.3, 0.4),
        (0.6, 0.6), (1.0, 0.2), (0.8, -0.1), (0.5, 0.0), (0.4, -0.4),
        (0.2, -0.1), (0.1, -0.6), (0.0, -0.4)
    ]
    left_half = [(-x, y) for x, y in reversed(right_half[:-1])]
    left_half.pop() 
    return [(x * raio, -y * raio) for x, y in right_half + left_half]

def gerar_asteroide(raio):
    return [(raio * math.cos(2*math.pi*i/100)**3, raio * math.sin(2*math.pi*i/100)**3) for i in range(100)]

def gerar_deltoide(raio):
    return [(raio/3 * (2*math.cos(2*math.pi*i/100) + math.cos(4*math.pi*i/100)),
             raio/3 * (2*math.sin(2*math.pi*i/100) - math.sin(4*math.pi*i/100))) for i in range(100)]

def gerar_squircle(raio):
    return [(math.copysign(abs(math.cos(2*math.pi*i/100))**0.5, math.cos(2*math.pi*i/100)) * raio,
             math.copysign(abs(math.sin(2*math.pi*i/100))**0.5, math.sin(2*math.pi*i/100)) * raio) for i in range(100)]

def gerar_ovo(raio):
    return [(-raio * math.sin(2*math.pi*i/100),
              raio * math.cos(2*math.pi*i/100) * (1 + 0.2 * math.sin(2*math.pi*i/100))) for i in range(100)]

def gerar_lissajous_3_2(raio):
    return [(raio * math.sin(3*2*math.pi*i/150 + math.pi/2), raio * math.sin(2*2*math.pi*i/150)) for i in range(150)]

def gerar_lissajous_5_4(raio):
    return [(raio * math.sin(5*2*math.pi*i/200 + math.pi/4), raio * math.sin(4*2*math.pi*i/200)) for i in range(200)]

def gerar_gota(raio):
    return [(raio * math.sin(2*math.pi*i/100) * math.sin(math.pi*i/100)**2,
             -raio * math.cos(2*math.pi*i/100)) for i in range(100)]

def gerar_bifolium(raio):
    return [(raio * 2 * math.sin(2*math.pi*i/100) * math.cos(2*math.pi*i/100)**2,
             raio * 2 * math.sin(2*math.pi*i/100)**2 * math.cos(2*math.pi*i/100)) for i in range(100)]

def gerar_trevo_3(raio):
    return [(raio * (1 + 0.5*math.cos(3*2*math.pi*i/120)) * math.cos(2*math.pi*i/120),
             raio * (1 + 0.5*math.cos(3*2*math.pi*i/120)) * math.sin(2*math.pi*i/120)) for i in range(120)]

def gerar_trevo_4(raio):
    return [(raio * (1 + 0.5*math.cos(4*2*math.pi*i/120)) * math.cos(2*math.pi*i/120),
             raio * (1 + 0.5*math.cos(4*2*math.pi*i/120)) * math.sin(2*math.pi*i/120)) for i in range(120)]

def gerar_lente(raio):
    pts1 = [(raio * math.cos(math.pi*i/50), raio * 0.5 * math.sin(math.pi*i/50)) for i in range(51)]
    pts2 = [(raio * math.cos(math.pi + math.pi*i/50), -raio * 0.5 * math.sin(math.pi + math.pi*i/50)) for i in range(51)]
    return pts1 + pts2

def gerar_pacman(raio):
    return [(0,0)] + [(raio * math.cos(math.pi/4 + 1.5*math.pi*i/50), 
                       raio * math.sin(math.pi/4 + 1.5*math.pi*i/50)) for i in range(51)]

def gerar_capsula(raio):
    top_arc = [(raio*0.5*math.cos(math.pi + math.pi*i/20), -raio*0.5 + raio*0.5*math.sin(math.pi + math.pi*i/20)) for i in range(21)]
    bot_arc = [(raio*0.5*math.cos(math.pi*i/20), raio*0.5 + raio*0.5*math.sin(math.pi*i/20)) for i in range(21)]
    return top_arc + bot_arc

def gerar_meia_lua(raio):
    outer = [(raio*math.cos(-math.pi/2 + math.pi*i/40), raio*math.sin(-math.pi/2 + math.pi*i/40)) for i in range(41)]
    inner = [(raio*0.5*math.cos(math.pi/2 - math.pi*i/40) + raio*0.5, raio*math.sin(math.pi/2 - math.pi*i/40)) for i in range(41)]
    return outer + inner
    
def gerar_cruz_malta(raio):
    r = raio
    return [(r*0.2, r*0.2), (r, r*0.4), (r, -r*0.4), (r*0.2, -r*0.2), (r*0.4, -r), (-r*0.4, -r), (-r*0.2, -r*0.2), (-r, -r*0.4), (-r, r*0.4), (-r*0.2, r*0.2), (-r*0.4, r), (r*0.4, r)]

# Catálogo completo de formas
SHAPES_CATALOG = {
    "Forma Livre": lambda r, n: gerar_forma_livre(n, r),
    "Estrela Livre": lambda r, n: gerar_estrela_livre(n, r),
    "Flor Livre": lambda r, n: gerar_flor_livre(n, r),
    "Estrela (5 Pontas)": lambda r, n: gerar_estrela(r),
    "Pentagrama": lambda r, n: gerar_pentagrama(r),
    "Estrela de Davi": lambda r, n: gerar_estrela_davi(r),
    "Cubo (Isométrico)": lambda r, n: gerar_cubo_isometrico(r),
    "Coração": lambda r, n: gerar_coracao(r),
    "Infinito": lambda r, n: gerar_infinito(r),
    "Engrenagem": lambda r, n: gerar_engrenagem(r),
    "Borboleta": lambda r, n: gerar_borboleta(r),
    "Símbolo do Batman": lambda r, n: gerar_batman(r),
    "Rosa Polar (4 Pétalas)": lambda r, n: gerar_rosa_polar(r, 2),
    "Rosa Polar (5 Pétalas)": lambda r, n: gerar_rosa_polar(r, 5),
    "Rosa Polar (8 Pétalas)": lambda r, n: gerar_rosa_polar(r, 4),
    "Lágrima": lambda r, n: gerar_lagrima(r),
    "Estrela Ninja (Shuriken)": lambda r, n: gerar_shuriken(r),
    "Cruz": lambda r, n: gerar_cruz(r),
    "Raio": lambda r, n: gerar_raio(r),
    "Ampulheta": lambda r, n: gerar_ampulheta(r),
    "Triângulo Místico": lambda r, n: gerar_forma_livre(3, r) + gerar_forma_livre(3, -r),
    "Heptagrama": lambda r, n: [(r * math.cos(-math.pi/2 + 6*math.pi*i/7), r * math.sin(-math.pi/2 + 6*math.pi*i/7)) for i in range(7)],
    "Octagrama": lambda r, n: [(r * math.cos(-math.pi/2 + 6*math.pi*i/8), r * math.sin(-math.pi/2 + 6*math.pi*i/8)) for i in range(8)],
    "Dodecagrama": lambda r, n: [(r * math.cos(-math.pi/2 + 10*math.pi*i/12), r * math.sin(-math.pi/2 + 10*math.pi*i/12)) for i in range(12)],
    "Seta": lambda r, n: [(0, -r), (r*0.5, -r*0.2), (r*0.2, -r*0.2), (r*0.2, r), (-r*0.2, r), (-r*0.2, -r*0.2), (-r*0.5, -r*0.2)],
    "Círculo Perfeito": lambda r, n: gerar_forma_livre(100, r),
    "Asteroide": lambda r, n: gerar_asteroide(r),
    "Deltoide": lambda r, n: gerar_deltoide(r),
    "Superelipse (Squircle)": lambda r, n: gerar_squircle(r),
    "Ovo": lambda r, n: gerar_ovo(r),
    "Lissajous (3:2)": lambda r, n: gerar_lissajous_3_2(r),
    "Lissajous (5:4)": lambda r, n: gerar_lissajous_5_4(r),
    "Gota d'Água": lambda r, n: gerar_gota(r),
    "Bifolium": lambda r, n: gerar_bifolium(r),
    "Trevo (3 Folhas)": lambda r, n: gerar_trevo_3(r),
    "Trevo (4 Folhas)": lambda r, n: gerar_trevo_4(r),
    "Lente (Vesica Piscis)": lambda r, n: gerar_lente(r),
    "Pac-Man": lambda r, n: gerar_pacman(r),
    "Cápsula": lambda r, n: gerar_capsula(r),
    "Meia-Lua": lambda r, n: gerar_meia_lua(r),
    "Cruz de Malta": lambda r, n: gerar_cruz_malta(r),
    "Diamante": lambda r, n: [(0, -r), (r*0.6, 0), (0, r), (-r*0.6, 0)],
    "Pipa": lambda r, n: [(0, -r), (r*0.5, -r*0.2), (0, r), (-r*0.5, -r*0.2)],
    "Trapézio": lambda r, n: [(-r*0.5, -r*0.5), (r*0.5, -r*0.5), (r*0.8, r*0.5), (-r*0.8, r*0.5)],
    "Hexágono Côncavo": lambda r, n: [(0,-r), (r,-r*0.5), (r*0.5,0), (r,r*0.5), (0,r), (-r,r*0.5), (-r*0.5,0), (-r,-r*0.5)],
    "Escudo": lambda r, n: [(0, r), (r*0.8, r*0.5), (r*0.8, -r*0.8), (-r*0.8, -r*0.8), (-r*0.8, r*0.5)],
    "Espada": lambda r, n: [(0,-r), (r*0.1,-r*0.8), (r*0.1,r*0.4), (r*0.3,r*0.4), (r*0.3,r*0.5), (r*0.1,r*0.5), (r*0.1,r*0.9), (r*0.2,r), (-r*0.2,r), (-r*0.1,r*0.9), (-r*0.1,r*0.5), (-r*0.3,r*0.5), (-r*0.3,r*0.4), (-r*0.1,r*0.4), (-r*0.1,-r*0.8)],
    "Coroa": lambda r, n: [(-r, r), (-r*0.8, -r), (-r*0.4, r*0.2), (0, -r*1.2), (r*0.4, r*0.2), (r*0.8, -r), (r, r)],
    "Pinheiro": lambda r, n: [(0, -r), (r*0.4, -r*0.4), (r*0.2, -r*0.4), (r*0.6, r*0.2), (r*0.3, r*0.2), (r*0.8, r*0.8), (r*0.2, r*0.8), (r*0.2, r), (-r*0.2, r), (-r*0.2, r*0.8), (-r*0.8, r*0.8), (-r*0.3, r*0.2), (-r*0.6, r*0.2), (-r*0.2, -r*0.4), (-r*0.4, -r*0.4)],
    "Bumerangue": lambda r, n: [(r, r), (r*0.2, 0), (r, -r), (r*0.8, -r*1.2), (-r*0.2, 0), (r*0.8, r*1.2)],
    "Seta Dupla": lambda r, n: [(r, 0), (r*0.6, -r*0.4), (r*0.6, -r*0.2), (-r*0.6, -r*0.2), (-r*0.6, -r*0.4), (-r, 0), (-r*0.6, r*0.4), (-r*0.6, r*0.2), (r*0.6, r*0.2), (r*0.6, r*0.4)],
    "Balão": lambda r, n: [(r*math.sin(2*math.pi*i/40), -r*math.cos(2*math.pi*i/40)) for i in range(40)] + [(r*0.1, r*1.2), (-r*0.1, r*1.2)],
    "Sinal de Adição": lambda r, n: [(-r*0.2, -r), (r*0.2, -r), (r*0.2, -r*0.2), (r, -r*0.2), (r, r*0.2), (r*0.2, r*0.2), (r*0.2, r), (-r*0.2, r), (-r*0.2, r*0.2), (-r, r*0.2), (-r, -r*0.2), (-r*0.2, -r*0.2)],
    "Estrela (4 Pontas)": lambda r, n: [((r if i%2==0 else r*0.2)*math.cos(-math.pi/2 + math.pi*i/4), (r if i%2==0 else r*0.2)*math.sin(-math.pi/2 + math.pi*i/4)) for i in range(8)],
    "Ziguezague Circular": lambda r, n: [((r if i%2==0 else r*0.8)*math.cos(2*math.pi*i/40), (r if i%2==0 else r*0.8)*math.sin(2*math.pi*i/40)) for i in range(40)],
    "Engrenagem Quadrada": lambda r, n: [((r if i%2==0 else r*0.7)*math.cos(2*math.pi*i/16), (r if i%2==0 else r*0.7)*math.sin(2*math.pi*i/16)) for i in range(16)]
}

# ==============================================================================
# DETECÇÃO DE FONTE DE SISTEMA (Focado em Windows Nativo)
# ==============================================================================
def find_unicode_font_path():
    """
    Localiza uma fonte compatível com o maior número de caracteres Unicode no Windows.
    Usamos caminhos absolutos baseados no diretório do Windows para evitar erros
    de mapeamento no Pygame.
    """
    # 1. Caminho dinâmico baseado na variável de ambiente do Windows
    windir = os.environ.get("SystemRoot", "C:\\Windows")
    windows_font_dir = os.path.join(windir, "Fonts")

    # Candidatos nativos do Windows com excelente cobertura Unicode (como Kanji, Hanzi e Kana)
    windows_candidates = [
        "msyh.ttc",       # Microsoft YaHei (Excelente para Chinês/Japonês/Universal)
        "msyhbd.ttc",     # Microsoft YaHei Bold
        "simsun.ttc",     # SimSun (Chinês tradicional/simplificado)
        "msgothic.ttc",   # MS Gothic (Japonês)
        "segoeui.ttf",    # Segoe UI (Excelente cobertura Unicode geral)
        "seguiemj.ttf",   # Segoe UI Emoji
        "arial.ttf"       # Arial tradicional
    ]

    for font_file in windows_candidates:
        full_path = os.path.join(windows_font_dir, font_file)
        if os.path.exists(full_path):
            print(f"[Windows Nativo] Carregando fonte com sucesso: {full_path}")
            return full_path

    # 2. Caso falhe (outros OS ou setups atípicos)
    fallback_candidates = ["microsoftyahei", "msyh", "segoeui", "msgothic", "simsun", "arial"]
    for name in fallback_candidates:
        path = pygame.font.match_font(name)
        if path:
            print(f"[Pygame Match] Carregando fonte alternativa: {path}")
            return path

    return None

# ==============================================================================
# LÓGICA PRINCIPAL, FÍSICA E CÂMERA
# ==============================================================================
def main():
    pygame.init()
    pygame.font.init()

    # Configurações Iniciais de Janela
    MIN_WIDTH, MIN_HEIGHT = 1000, 700
    WIDTH, HEIGHT = MIN_WIDTH, MIN_HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Gerador Geométrico Avançado - Zoom e Física")
    
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))

    # --- AJUSTE DE FONTE UNICODE NO PYGAME_GUI ---
    font_path = find_unicode_font_path()
    if font_path:
        # Registra a fonte explicitamente para o pygame_gui utilizar
        manager.add_font_paths(
            font_name="unicode_font",
            regular_path=font_path,
            bold_path=font_path,
            italic_path=font_path,
            bold_italic_path=font_path
        )
        
        # Criação do tema explícito apontando para a fonte unicode cadastrada
        theme_config = {
            "defaults": {
                "font": {
                    "name": "unicode_font",
                    "size": "14"
                }
            }
        }
        
        try:
            # Força o caminho correto usando o manipulador de arquivos nativo do Python
            with open("theme.json", "w", encoding="utf-8") as f:
                json.dump(theme_config, f, indent=4)
            manager.get_theme().load_theme("theme.json")
        except Exception as e:
            print(f"Erro ao inicializar arquivo de tema: {e}")
    else:
        print("[AVISO] Nenhuma fonte Unicode nativa do Windows foi localizada.")

    # --- ELEMENTOS DA UI ---
    dropdown_formas = pygame_gui.elements.UIDropDownMenu(
        options_list=list(SHAPES_CATALOG.keys()),
        starting_option="Forma Livre",
        relative_rect=pygame.Rect((20, 10), (180, 40)),
        manager=manager
    )

    dropdown_idiomas = pygame_gui.elements.UIDropDownMenu(
        options_list=list(IDIOMAS.keys()),
        starting_option="Português",
        relative_rect=pygame.Rect((210, 10), (160, 40)),
        manager=manager
    )

    input_lados = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((380, 10), (60, 40)), manager=manager
    )
    input_lados.set_allowed_characters('numbers')
    
    btn_gerar = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((450, 10), (70, 40)),
        text='Gerar', manager=manager
    )

    btn_reset_cam = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((530, 10), (120, 40)),
        text='Reset Visão', manager=manager
    )
    
    btn_fullscreen = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((660, 10), (100, 40)),
        text='Tela Cheia', manager=manager
    )

    label_nome = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WIDTH - 220, 10), (200, 40)),
        text='', manager=manager
    )

    # --- VARIÁVEIS DE ESTADO ---
    current_x, current_y = [], []
    target_x, target_y = [], []
    vel_x, vel_y = [], []
    current_n = 0
    is_fullscreen = False
    forma_atual_selecionada = "Forma Livre"
    idioma_atual = "pt"
    
    camera_offset_x = 0
    camera_offset_y = 0
    zoom_level = 1.0

    SPRING_K = 0.15 
    DAMPING = 0.82

    def calcular_alvos():
        raio_base = 250
        lados = 3
        if input_lados.get_text().isdigit():
            lados = int(input_lados.get_text())
        if lados < 1: lados = 1

        pontos = SHAPES_CATALOG[forma_atual_selecionada](raio_base, lados)
        tx = [p[0] for p in pontos]
        ty = [p[1] for p in pontos]
        return tx, ty, len(pontos), lados

    def gerar_poligono():
        nonlocal current_x, current_y, vel_x, vel_y, target_x, target_y, current_n
        novo_tx, novo_ty, novo_n_pts, lados_inseridos = calcular_alvos()

        if novo_n_pts > current_n:
            for i in range(current_n, novo_n_pts):
                current_x.append(0) 
                current_y.append(0)
                vel_x.append(0.0)
                vel_y.append(0.0)
        elif novo_n_pts < current_n:
            current_x = current_x[:novo_n_pts]
            current_y = current_y[:novo_n_pts]
            vel_x = vel_x[:novo_n_pts]
            vel_y = vel_y[:novo_n_pts]

        target_x = novo_tx
        target_y = novo_ty
        current_n = novo_n_pts
        atualizar_label_traducao(lados_inseridos)

    def atualizar_label_traducao(lados_inseridos=None):
        if lados_inseridos is None:
            if input_lados.get_text().isdigit():
                lados_inseridos = int(input_lados.get_text())
            else:
                lados_inseridos = 3

        if forma_atual_selecionada == "Forma Livre":
            label_nome.set_text(obter_nome_forma_i18n(lados_inseridos, "gono", idioma_atual))
        elif forma_atual_selecionada == "Estrela Livre":
            label_nome.set_text(obter_nome_forma_i18n(lados_inseridos, "grama", idioma_atual))
        elif forma_atual_selecionada == "Flor Livre":
            label_nome.set_text(obter_nome_forma_i18n(lados_inseridos, "flor", idioma_atual))
        else:
            traducao = FORMAS_ESTATICAS_TRADUZIDAS.get(idioma_atual, {}).get(forma_atual_selecionada, forma_atual_selecionada)
            label_nome.set_text(traducao)

    def converter_mundo_para_tela(x_mundo, y_mundo):
        tela_x = (x_mundo - camera_offset_x) * zoom_level + WIDTH / 2
        tela_y = (y_mundo - camera_offset_y) * zoom_level + HEIGHT / 2 + 30 
        return tela_x, tela_y

    def reposicionar_ui(w, h):
        label_width = min(400, w - 780)
        if label_width > 50:
            label_nome.set_dimensions((label_width, 40))
            label_nome.set_position((w - label_width - 20, 10))
            label_nome.show()
        else:
            label_nome.hide()

    # Inicialização Padrão
    input_lados.set_text("5")
    gerar_poligono()
    reposicionar_ui(WIDTH, HEIGHT)

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and is_fullscreen:
                    is_fullscreen = False
                    WIDTH, HEIGHT = MIN_WIDTH, MIN_HEIGHT
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    manager.set_window_resolution((WIDTH, HEIGHT))
                    reposicionar_ui(WIDTH, HEIGHT)

            if event.type == pygame.MOUSEWHEEL:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_y > 60:
                    mundo_mouse_x = (mouse_x - WIDTH / 2) / zoom_level + camera_offset_x
                    mundo_mouse_y = (mouse_y - HEIGHT / 2 - 30) / zoom_level + camera_offset_y
                    
                    zoom_factor = 1.1
                    if event.y > 0: zoom_level *= zoom_factor
                    elif event.y < 0: zoom_level /= zoom_factor
                    zoom_level = max(0.05, min(zoom_level, 50.0))

                    mundo_mouse_x_novo = (mouse_x - WIDTH / 2) / zoom_level + camera_offset_x
                    mundo_mouse_y_novo = (mouse_y - HEIGHT / 2 - 30) / zoom_level + camera_offset_y
                    camera_offset_x += mundo_mouse_x - mundo_mouse_x_novo
                    camera_offset_y += mundo_mouse_y - mundo_mouse_y_novo

            if event.type == pygame.VIDEORESIZE and not is_fullscreen:
                WIDTH, HEIGHT = max(MIN_WIDTH, event.w), max(MIN_HEIGHT, event.h)
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                manager.set_window_resolution((WIDTH, HEIGHT))
                reposicionar_ui(WIDTH, HEIGHT)

            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == dropdown_formas:
                    forma_atual_selecionada = event.text
                    gerar_poligono()
                elif event.ui_element == dropdown_idiomas:
                    idioma_atual = IDIOMAS.get(event.text, "pt")
                    atualizar_label_traducao()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == btn_gerar:
                    gerar_poligono()
                elif event.ui_element == btn_reset_cam:
                    camera_offset_x, camera_offset_y = 0, 0
                    zoom_level = 1.0
                elif event.ui_element == btn_fullscreen:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        info = pygame.display.Info()
                        WIDTH, HEIGHT = info.current_w, info.current_h
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        WIDTH, HEIGHT = MIN_WIDTH, MIN_HEIGHT
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    manager.set_window_resolution((WIDTH, HEIGHT))
                    reposicionar_ui(WIDTH, HEIGHT)

            manager.process_events(event)
        manager.update(time_delta)

        # --- ATUALIZAÇÃO DA FÍSICA ---
        for i in range(current_n):
            dx = target_x[i] - current_x[i]
            dy = target_y[i] - current_y[i]
            vel_x[i] = (vel_x[i] + dx * SPRING_K) * DAMPING
            vel_y[i] = (vel_y[i] + dy * SPRING_K) * DAMPING
            current_x[i] += vel_x[i]
            current_y[i] += vel_y[i]

        # --- DESENHO ---
        screen.fill((30, 30, 46))

        pontos_tela = []
        for i in range(current_n):
            px, py = converter_mundo_para_tela(current_x[i], current_y[i])
            pontos_tela.append((px, py))

        if current_n == 1:
            if pontos_tela: pygame.draw.circle(screen, (166, 227, 161), pontos_tela[0], max(2, int(6 * zoom_level)))
        elif current_n == 2:
            if pontos_tela: pygame.draw.line(screen, (166, 227, 161), pontos_tela[0], pontos_tela[1], max(1, int(4 * zoom_level)))
        elif current_n >= 3:
            if len(pontos_tela) >= 3:
                poly_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                try:
                    pygame.draw.polygon(poly_surface, (137, 180, 250, 60), pontos_tela)
                    pygame.draw.lines(poly_surface, (137, 180, 250, 255), True, pontos_tela, max(1, int(3 * zoom_level)))
                except ValueError:
                    pass 
                screen.blit(poly_surface, (0, 0))

        pygame.draw.rect(screen, (24, 24, 37), (0, 0, WIDTH, 60))
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()