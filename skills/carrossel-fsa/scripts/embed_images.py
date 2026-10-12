#!/usr/bin/env python3
"""
Embute imagens locais como base64 dentro do HTML, substituindo os placeholders
de caminho (ex: FOTO_1.jpeg) pelo data URI correspondente.

Uso:
    python embed_images.py <arquivo.html> <placeholder>=<caminho_imagem> [<placeholder>=<caminho> ...]

Exemplo:
    python embed_images.py carrossel.html FOTO_1.jpeg=fotos/a.jpg FOTO_2.jpeg=fotos/b.jpg

Sobrescreve o HTML com as imagens embutidas. Faz isso para o render nao depender
de caminhos relativos quebrarem.
"""
import sys
import base64
import mimetypes


def embed(html_path: str, mappings: dict):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    for placeholder, img_path in mappings.items():
        mime = mimetypes.guess_type(img_path)[0] or "image/jpeg"
        with open(img_path, "rb") as imgf:
            b64 = base64.b64encode(imgf.read()).decode()
        data_uri = f"data:{mime};base64,{b64}"
        # substitui src="placeholder" pelo data uri
        html = html.replace(f'src="{placeholder}"', f'src="{data_uri}"')
        print(f"embutida: {placeholder} <- {img_path}")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML atualizado: {html_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python embed_images.py <arquivo.html> <placeholder>=<caminho> ...")
        sys.exit(1)
    html_path = sys.argv[1]
    mappings = {}
    for arg in sys.argv[2:]:
        k, v = arg.split("=", 1)
        mappings[k] = v
    embed(html_path, mappings)
