import http from 'http';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '../..');

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
        // Normalize to POSIX-style and strip leading slashes to avoid absolute paths
        const normalized = path.posix.normalize(rawUrlPath).replace(/^\/+/, '');
        const requested = normalized || 'web/import/index.html';
        const candidate = path.resolve(rootDir, requested);
        // Ensure the resolved path stays within rootDir
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
        // Log details server-side, but do not expose exception text to clients
        console.error('Server error:', e);
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

function openBrowser(url) {
  const platform = process.platform;
  if (platform === 'darwin') spawn('open', [url], { stdio: 'ignore', detached: true });
  else if (platform === 'win32') spawn('cmd', ['/c', 'start', '', url], { stdio: 'ignore', detached: true });
  else spawn('xdg-open', [url], { stdio: 'ignore', detached: true });
}

const args = process.argv.slice(2);
const shouldOpen = args.includes('--open');

const { server, port } = await startServer(repoRoot);
const url = `http://127.0.0.1:${port}/web/import/index.html`;
console.log(`Local server ready: ${url}`);
console.log('Press Ctrl+C to stop.');
if (shouldOpen) openBrowser(url);

process.on('SIGINT', () => { server.close(() => process.exit(0)); });
