const { chromium } = require('playwright');
const ids = JSON.parse(require('fs').readFileSync('ids.json'));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1920, height: 1200 }, deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  for (const [nome, id] of ids) {
    await p.goto(`https://miro.com/app/board/uXjVJkj7NUw=/?share_link_id=202799875564&moveToWidget=${id}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await p.waitForTimeout(16000);
    await p.mouse.move(960, 600);
    await p.keyboard.down('Control'); await p.mouse.wheel(0, 120); await p.keyboard.up('Control');
    await p.waitForTimeout(6000);
    await p.screenshot({ path: `miroz_${nome}.png` });
    console.log(nome);
  }
  await b.close();
})();
