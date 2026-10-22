import asyncio,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        await pg.goto('file://'+os.path.abspath('pills.html')); await pg.wait_for_timeout(800)
        for i in ['nf','sup','hor','fer','jej','hem','ale','ava','vit','preco']:
            await pg.locator('#'+i).screenshot(path=f'pill-{i}.png',omit_background=True)
        await b.close()
asyncio.run(main())
