// Renders a reel page frame by frame with Playwright and encodes it with ffmpeg.
//
//   node render.mjs src/reel1-ia.html output/reel1-ia.mp4          # full video
//   node render.mjs src/reel1-ia.html stills/ --stills 1,4.5,10     # PNG stills
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn, execFileSync } from 'node:child_process';
import { mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { dirname, resolve, join, basename } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const [, , page, out, ...rest] = process.argv;
const opt = (name, def) => { const i = rest.indexOf(name); return i >= 0 ? rest[i + 1] : def; };
const FPS = Number(opt('--fps', 30));
const stills = opt('--stills');

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
const tab = await ctx.newPage();
await tab.goto(pathToFileURL(resolve(page)).href);
await tab.evaluate(() => document.fonts.ready);
await tab.waitForFunction(() => typeof window.renderFrame === 'function');
const meta = await tab.evaluate(() => ({ duration: window.DURATION, sfx: window.SFX || [], music: window.MUSIC || {} }));

async function frameAt(t, type = 'jpeg') {
  await tab.evaluate(t => window.renderFrame(t), t);
  return tab.screenshot({ type, ...(type === 'jpeg' ? { quality: 94 } : {}) });
}

if (stills) {
  mkdirSync(out, { recursive: true });
  for (const t of stills.split(',').map(Number)) {
    const file = join(out, `${basename(page, '.html')}_${t.toFixed(2)}.png`);
    writeFileSync(file, await frameAt(t, 'png'));
    console.log(file);
  }
  await browser.close();
  process.exit(0);
}

mkdirSync(dirname(resolve(out)), { recursive: true });
const tmp = resolve(out + '.tmp');
mkdirSync(tmp, { recursive: true });
const silent = join(tmp, 'video.mp4');
const wav = join(tmp, 'audio.wav');

const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], { stdio: ['pipe', 'inherit', 'inherit'] });
const total = Math.round(meta.duration * FPS);
for (let i = 0; i < total; i++) {
  const buf = await frameAt(i / FPS);
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 60 === 0) process.stdout.write(`\r${basename(page)} frame ${i}/${total}`);
}
ff.stdin.end();
await new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg ' + c)))));
await browser.close();
console.log(`\r${basename(page)} frames done (${total})`);

writeFileSync(join(tmp, 'cues.json'), JSON.stringify({ duration: meta.duration, sfx: meta.sfx, ...meta.music }));
execFileSync('python3', [join(here, 'soundtrack.py'), join(tmp, 'cues.json'), wav], { stdio: 'inherit' });
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', silent, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', resolve(out)], { stdio: 'inherit' });
rmSync(tmp, { recursive: true, force: true });
console.log('wrote', out);
