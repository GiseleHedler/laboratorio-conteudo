import asyncio,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg=await b.new_page(viewport={'width':1080,'height':1350})
        await pg.goto('file://'+os.path.abspath('esclarecimento-anuncio.html')); await pg.wait_for_timeout(700)
        await pg.locator('#n').screenshot(path='nota-esclarecimento-anuncio-v2.png')
        await b.close()
asyncio.run(main())
