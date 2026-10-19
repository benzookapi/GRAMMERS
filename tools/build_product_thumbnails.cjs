// Place the original covers on square white canvases without scaling the art.
const fs = require('node:fs/promises');
const path = require('node:path');
const sharp = require('sharp');

async function main() {
  const root = path.resolve(__dirname, '..');
  const out = path.join(root, 'output', 'shopify');
  await fs.mkdir(out, { recursive: true });
  for (const edition of ['complete', 'sample']) {
    const source = await fs.readFile(path.join(root, 'output', 'pdf', `grammers-${edition}-cover.png`));
    const { width, height } = await sharp(source).metadata();
    const side = Math.max(width, height);
    const left = Math.floor((side - width) / 2);
    const top = Math.floor((side - height) / 2);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${side}" height="${side}" viewBox="0 0 ${side} ${side}"><rect width="${side}" height="${side}" fill="white"/><image x="${left}" y="${top}" width="${width}" height="${height}" xlink:href="data:image/png;base64,${source.toString('base64')}"/></svg>`;
    const base = path.join(out, `grammers-${edition}-cover-square`);
    await fs.writeFile(`${base}.svg`, svg);
    await sharp(Buffer.from(svg)).png().toFile(`${base}.png`);
    const originalPixels = await sharp(source).removeAlpha().raw().toBuffer();
    const placedPixels = await sharp(`${base}.png`).extract({ left, top, width, height }).removeAlpha().raw().toBuffer();
    if (!originalPixels.equals(placedPixels)) throw new Error(`${edition}: original cover pixels changed`);
    console.log(`${edition}: ${side}x${side}; all original cover pixels preserved`);
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
