import asyncio,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        await pg.goto('file://'+os.path.abspath('pecas.html')); await pg.wait_for_timeout(800)
        await pg.locator('#selo').screenshot(path='selo.png',omit_background=True)
        for i in ['olimpo','cinquenta','fim','fim2']:
            await pg.locator('#'+i).screenshot(path=f'{i}.png',omit_background=True)
        await b.close()
asyncio.run(main())
