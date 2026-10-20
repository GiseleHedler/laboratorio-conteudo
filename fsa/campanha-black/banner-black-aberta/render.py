import asyncio,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        for f,w,h,o in [('h.html',1200,400,'banner-black-horizontal-2400x800.png'),('q.html',540,540,'banner-black-quadrado-1080.png')]:
            pg=await b.new_page(viewport={'width':w,'height':h},device_scale_factor=2)
            await pg.goto('file://'+os.path.abspath(f)); await pg.wait_for_timeout(700)
            await pg.screenshot(path=o); await pg.close()
        await b.close()
asyncio.run(main())
