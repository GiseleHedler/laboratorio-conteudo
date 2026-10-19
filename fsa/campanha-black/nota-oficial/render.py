import asyncio,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg=await b.new_page(viewport={'width':1080,'height':1350})
        await pg.goto('file://'+os.path.abspath('nota.html')); await pg.wait_for_timeout(800)
        for i in ['repudio','comunicado']:
            el=pg.locator('#'+i)
            h=await el.evaluate('e=>e.scrollHeight'); print(i,'altura conteudo',h)
            await el.screenshot(path=f'nota-{i}-feed.png')
        await b.close()
asyncio.run(main())
