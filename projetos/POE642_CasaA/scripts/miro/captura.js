const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 } });
  const p = await ctx.newPage();
  let n = 0, tot = 0;
  const out = fs.createWriteStream('ws.bin');
  p.on('websocket', ws => {
    console.log('ws', ws.url().slice(0, 120));
    ws.on('framereceived', f => { const d = typeof f.payload === 'string' ? Buffer.from(f.payload) : f.payload; tot += d.length; n++;
      const hdr = Buffer.alloc(8); hdr.writeUInt32LE(d.length, 0); hdr.writeUInt32LE(typeof f.payload === 'string' ? 1 : 0, 4); out.write(hdr); out.write(d); });
  });
  const resp = [];
  p.on('response', async r => { const u = r.url(); if (/board|widget|content|items|api/i.test(u)) resp.push(u.slice(0, 160) + ' ' + r.status()); });
  await p.goto('https://miro.com/app/board/uXjVJkj7NUw=/?share_link_id=202799875564', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await p.waitForTimeout(30000);
  out.end();
  console.log('frames', n, 'bytes', tot);
  fs.writeFileSync('resp.txt', resp.join('\n'));
  await b.close();
})();
