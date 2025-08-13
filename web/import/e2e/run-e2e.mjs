import http from 'http';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { chromium } from 'playwright';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '../../..');

function contentType(p) {
  if (p.endsWith('.html')) return 'text/html; charset=utf-8';
  if (p.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (p.endsWith('.mjs')) return 'text/javascript; charset=utf-8';
  if (p.endsWith('.css')) return 'text/css; charset=utf-8';
  if (p.endsWith('.json')) return 'application/json; charset=utf-8';
  if (p.endsWith('.png')) return 'image/png';
  if (p.endsWith('.jpg') || p.endsWith('.jpeg')) return 'image/jpeg';
  if (p.endsWith('.svg')) return 'image/svg+xml';
  return 'application/octet-stream';
}

function startServer(rootDir) {
  return new Promise((resolve, reject) => {
    const server = http.createServer(async (req, res) => {
      try {
        const rawUrlPath = decodeURIComponent((req.url || '/').split('?')[0]);
        const normalized = path.posix.normalize(rawUrlPath).replace(/^\/+/, '');
        const requested = normalized || 'index.html';
        const candidate = path.resolve(rootDir, requested);
        const rel = path.relative(rootDir, candidate);
        if (rel.startsWith('..') || path.isAbsolute(rel)) {
          res.statusCode = 403;
          res.setHeader('Content-Type', 'text/plain; charset=utf-8');
          res.end('Forbidden');
          return;
        }
        const filePath = candidate;
        let stat;
        try { stat = await fs.stat(filePath); } catch { res.statusCode = 404; res.setHeader('Content-Type', 'text/plain; charset=utf-8'); res.end('Not found'); return; }
        let toServe = filePath;
        if (stat.isDirectory()) {
          const indexPath = path.join(filePath, 'index.html');
          try { await fs.access(indexPath); toServe = indexPath; } catch { res.statusCode = 404; res.setHeader('Content-Type', 'text/plain; charset=utf-8'); res.end('Not found'); return; }
        }
        const buf = await fs.readFile(toServe);
        res.setHeader('Content-Type', contentType(toServe));
        res.end(buf);
      } catch (e) {
        console.error('E2E server error:', e);
        res.statusCode = 500;
        res.setHeader('Content-Type', 'text/plain; charset=utf-8');
        res.end('Internal Server Error');
      }
    });
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      resolve({ server, port });
    });
    server.on('error', reject);
  });
}

async function run() {
  const { server, port } = await startServer(repoRoot);
  let browser;
  try {
    browser = await chromium.launch();
    const ctx = await browser.newContext();
    const page = await ctx.newPage();

    const url = `http://127.0.0.1:${port}/web/import/index.html`;
    await page.goto(url);
    await page.waitForSelector('#importBtn');

    const sample = await fs.readFile(path.join(repoRoot, 'docs/specs/insight_packet_v1.sample.json'), 'utf8');

    // Fill and import
    await page.fill('#json', sample.trim());
    await page.click('#importBtn');
    await page.waitForFunction(() => document.getElementById('status')?.textContent?.includes('Imported'));

    // Validate IndexedDB contents
    const result = await page.evaluate(() => {
      function openDb() {
        return new Promise((resolve, reject) => {
          const req = indexedDB.open('wellbeing-db', 1);
          req.onupgradeneeded = () => {
            // should already exist, but ensure store exists
            const db = req.result;
            if (!db.objectStoreNames.contains('insights')) db.createObjectStore('insights', { keyPath: 'key' });
          };
          req.onsuccess = () => resolve(req.result);
          req.onerror = () => reject(req.error);
        });
      }
      function listAll(db) {
        return new Promise((resolve, reject) => {
          const tx = db.transaction('insights', 'readonly');
          const store = tx.objectStore('insights');
          const out = [];
          const cur = store.openCursor();
          cur.onsuccess = () => {
            const c = cur.result;
            if (c) { out.push(c.value); c.continue(); }
            else resolve(out);
          };
          cur.onerror = () => reject(cur.error);
        });
      }
      return openDb().then(db => listAll(db));
    });

    // Basic assertions
    if (!Array.isArray(result) || result.length < 1) throw new Error('No entries in IndexedDB');
    const item = result.find(x => x?.payload?.date && x?.type === 'plan_daily');
    if (!item) throw new Error('plan_daily entry not found');
    if (item.payload.score !== 65) throw new Error(`Unexpected score ${item.payload.score}`);
    if (!item.key?.startsWith('insight:')) throw new Error('Missing or invalid key');

    console.log('E2E PASS: import + IndexedDB ✅');
  } catch (e) {
    console.error('E2E FAIL:', e);
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    server.close();
  }
}

run();
