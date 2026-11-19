const { chromium } = require('playwright');
const ids = JSON.parse(process.argv[2]);
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1920, height: 1200 }, deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  for (const [nome, id] of ids) {
    await p.goto(`https://miro.com/app/board/uXjVJkj7NUw=/?share_link_id=202799875564&moveToWidget=${id}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await p.waitForTimeout(18000);
    // tira a interface por cima do quadro
    await p.addStyleTag({ content: '[data-testid*="toolbar"],[class*="toolbar"],[class*="Toolbar"],[data-testid*="banner"],header{visibility:hidden !important}' });
    await p.waitForTimeout(1500);
    await p.screenshot({ path: `miro_${nome}.png` });
    console.log(nome);
  }
  await b.close();
})();
