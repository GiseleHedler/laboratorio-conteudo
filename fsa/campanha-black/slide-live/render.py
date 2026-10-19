import asyncio,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg=await b.new_page(viewport={'width':1920,'height':1080})
        await pg.goto('file://'+os.path.abspath('slide.html')); await pg.wait_for_timeout(900)
        await pg.locator('#moldura').screenshot(path='live-moldura-transparente-1920x1080.png',omit_background=True)
        await pg.locator('#cheia').screenshot(path='live-slide-tela-cheia-1920x1080.png')
        await b.close()
asyncio.run(main())
