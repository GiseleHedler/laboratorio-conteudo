import asyncio,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg=await b.new_page(viewport={'width':1080,'height':1350})
        for f,o in [('esclarecimento.html','nota-esclarecimento-texto-comente.png'),('esclarecimento-sm.html','nota-esclarecimento-texto-saiba-mais.png')]:
            await pg.goto('file://'+os.path.abspath(f)); await pg.wait_for_timeout(700)
            await pg.locator('#n').screenshot(path=o)
        await b.close()
asyncio.run(main())
