#!/usr/bin/env python3
"""
Renderiza cada .slide de um arquivo HTML em PNG 1080x1350 (formato carrossel Instagram).

Uso:
    python render_carrossel.py <arquivo.html> <pasta_saida>

Requer: playwright + chromium
    pip install playwright --break-system-packages
    playwright install chromium

Cada <div class="slide"> vira um PNG numerado (slide_1.png, slide_2.png, ...).
As imagens referenciadas no HTML devem estar embutidas em base64 OU no mesmo
diretorio do HTML (caminho relativo).
"""
import sys
import os
from playwright.sync_api import sync_playwright


def render(html_path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    html_path = os.path.abspath(html_path)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 1080, "height": 1350},
            device_scale_factor=2,  # exporta em 2x para nitidez
        )
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(2000)  # espera carregar fontes e imagens

        slides = page.query_selector_all(".slide")
        if not slides:
            print("ERRO: nenhum elemento .slide encontrado no HTML.")
            browser.close()
            return

        for i, el in enumerate(slides, start=1):
            out = os.path.join(out_dir, f"slide_{i}.png")
            el.screenshot(path=out)
            print(f"slide_{i}.png ok")

        browser.close()
    print(f"\nPronto: {len(slides)} slides em {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python render_carrossel.py <arquivo.html> <pasta_saida>")
        sys.exit(1)
    render(sys.argv[1], sys.argv[2])
