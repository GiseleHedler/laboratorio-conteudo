#!/usr/bin/env python3
"""Gera a camada de texto (PNG transparente 1080x1920) na identidade da Gisele.
Uso: texto_marca.py <claro|foto> <frase1|frase2|marca> saida.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = "/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad/fonts/"
REG, ITA, BLK, CUR = (F + "Merriweather-400-normal.ttf", F + "Merriweather-400-italic.ttf",
                      F + "Merriweather-900-normal.ttf", F + "Satisfy-400-normal.ttf")
ROXO, ROSE, BRANCO, FRAMBOESA = "#241751", "#e29f8e", "#eae8ec", "#b53b70"
W, H = 1080, 1920

modo, qual, saida = sys.argv[1], sys.argv[2], sys.argv[3]
texto = ROXO if modo == "claro" else BRANCO
destaque = FRAMBOESA if modo == "claro" else ROSE

# cada linha: lista de trechos (texto, fonte, tamanho, cor)
FRASES = {
    "frase1": [
        [("Por gerações,", REG, 60, texto)],
        [("a gente entregou", REG, 60, texto)],
        [("o que recebeu.", BLK, 64, texto)],
    ],
    "frase2": [
        [("Até que um dia,", REG, 60, texto)],
        [("a ", ITA, 58, texto), ("madame", CUR, 112, destaque)],
        [("aprendeu que podia replantar.", BLK, 54, texto)],
    ],
    "marca": [],
}
linhas = FRASES[qual]

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
if modo == "foto" and qual != "marca":
    # degradê preto por cima da foto (regra da marca: nunca roxo)
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(150 * max(0.0, 1 - y / (H * 0.42))))
    preto = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    preto.putalpha(grad.resize((W, H)))
    img = Image.alpha_composite(img, preto)

d = ImageDraw.Draw(img)

def desenhar(linhas, pintar=True):
    y = 110
    for linha in linhas:
        partes = [(t, ImageFont.truetype(f, sz), c) for t, f, sz, c in linha]
        larg = sum(d.textlength(t, font=fo) for t, fo, _ in partes)
        alt = max(sz * (0.72 if f == CUR else 0.95) for _, f, sz, _ in linha)
        base = y + alt  # linha de base comum
        x = (W - larg) / 2
        for t, fo, c in partes:
            if pintar:
                d.text((x, base), t, font=fo, fill=c, anchor="ls")
            x += d.textlength(t, font=fo)
        y = base + 24
    return y

if qual == "marca":
    # o @ fica sempre logo abaixo do bloco mais longo (frase 2)
    y_marca = desenhar(FRASES["frase2"], pintar=False) + 18
    d.text((W / 2, y_marca), "@giselehedler", font=ImageFont.truetype(ITA, 28),
           fill=texto + "b0", anchor="mt")
else:
    desenhar(linhas)

if modo == "claro":
    # brilho claro e suave atrás das letras para separar da parede
    halo = img.split()[3].filter(ImageFilter.GaussianBlur(6)).point(lambda a: int(a * 0.35))
    luz = Image.new("RGBA", (W, H), BRANCO)
    luz.putalpha(halo)
    img = Image.alpha_composite(luz, img)
img.save(saida)
