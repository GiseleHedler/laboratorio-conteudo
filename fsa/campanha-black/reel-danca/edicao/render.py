import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        await pg.goto('file://'+__import__('os').path.abspath('pecas.html')); await pg.wait_for_timeout(800)
        for i in ['topo','tit','prova','fecha']:
            await pg.locator('#'+i).screenshot(path=f'{i}.png',omit_background=True)
        await b.close()
asyncio.run(main())
