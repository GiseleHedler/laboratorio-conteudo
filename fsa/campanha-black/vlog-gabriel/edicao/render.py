import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg=await b.new_page(viewport={'width':1000,'height':1200})
        await pg.goto('file:///home/user/laboratorio-conteudo/fsa/campanha-black/vlog-gabriel/edicao/cartoes.html')
        await pg.wait_for_timeout(800)
        for i in ['hip','gal','oli','sel']:
            await pg.locator('#'+i).screenshot(path=f'card-{i}.png',omit_background=True)
        await b.close()
asyncio.run(main())
