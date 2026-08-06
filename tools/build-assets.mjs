// Render the raster site assets from their sources.
//
//     node tools/build-assets.mjs
//
// Outputs, all committed:
//     og.png                1200x630 social card, from tools/og-image.html
//     apple-touch-icon.png  180x180 home-screen icon, from favicon.svg
//     favicon-32.png        32x32 fallback for browsers that ignore SVG favicons
//
// Chromium does the rasterising because it is already here for the tests, and it
// renders the same SVG the browser will.
// require() rather than a bare import so a globally installed playwright on
// NODE_PATH resolves too — ESM import ignores NODE_PATH.
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { readFile } from 'node:fs/promises';
const { chromium } = createRequire(import.meta.url)('playwright');

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const browser = await chromium.launch();

// Social card
{
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  await page.goto('file://' + path.join(ROOT, 'tools/og-image.html'), { waitUntil: 'load' });
  await page.waitForTimeout(200);
  await page.screenshot({ path: path.join(ROOT, 'og.png') });
  await page.close();
}

// Icons, from the same favicon.svg the page links. The SVG is inlined into a
// page rather than navigated to: an SVG opened directly is an image document
// with no <head> to size it from.
const svg = await readFile(path.join(ROOT, 'favicon.svg'), 'utf8');
for (const [size, name] of [[180, 'apple-touch-icon.png'], [32, 'favicon-32.png']]) {
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  await page.setContent(
    `<style>html,body{margin:0;padding:0}svg{display:block;width:100vw;height:100vh}</style>${svg}`);
  await page.waitForTimeout(120);
  await page.screenshot({ path: path.join(ROOT, name) });
  await page.close();
}

await browser.close();
console.log('wrote og.png, apple-touch-icon.png, favicon-32.png');
