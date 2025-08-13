import { InsightEnvelopeSchema, PlanDailySchema } from './schema.js';
import { openDb, putInsight, listInsights, clearAll } from './db.js';
import { validateJson } from './validator.js';

function assertValid(obj, schema, label) {
  const { valid, errors } = validateJson(obj, schema);
  if (!valid) throw new Error(`${label} invalid: ${errors[0]}`);
}

async function importJson(jsonStr, setStatus, render) {
  try {
    const env = JSON.parse(jsonStr);
  assertValid(env, InsightEnvelopeSchema, 'Envelope');
    if (env.version !== 'v1') throw new Error('Unsupported version');

  if (env.type === 'plan_daily') assertValid(env.payload, PlanDailySchema, 'Plan payload');

    const db = await openDb();
    await putInsight(db, env);
    setStatus('Imported', 'ok');
    await render();
  } catch (e) {
    setStatus(`Error: ${e.message}`, 'err');
  }
}

async function renderHistory(container) {
  const db = await openDb();
  const items = await listInsights(db);
  items.sort((a, b) => (a.payload?.date || '').localeCompare(b.payload?.date || ''));
  container.innerHTML = items.map(env => `
    <div class="item">
      <strong>${env.payload?.date || '—'}</strong>
      <span class="badge">${env.type}</span>
      <div class="muted">${env.payload?.band || ''} · ${env.payload?.score ?? ''}</div>
      <div>${env.payload?.plan ? `${env.payload.plan.type} ${env.payload.plan.minutes_range} + ${(env.payload.plan.addons||[]).slice(0,2).join(' + ')}` : ''}</div>
      <div class="muted">${(env.payload?.why||[]).join(', ')}</div>
    </div>
  `).join('');
}

function setupUI() {
  const jsonEl = document.getElementById('json');
  const importBtn = document.getElementById('importBtn');
  const scanBtn = document.getElementById('scanBtn');
  const clearBtn = document.getElementById('clearBtn');
  const statusEl = document.getElementById('status');
  const historyEl = document.getElementById('history');
  const scannerEl = document.getElementById('scanner');
  const videoEl = document.getElementById('video');

  const setStatus = (msg, cls) => { statusEl.textContent = msg; statusEl.className = cls || 'muted'; };
  const render = () => renderHistory(historyEl);

  importBtn.onclick = () => importJson(jsonEl.value, setStatus, render);

  let mediaStream = null;
  let scanning = false;
  let scanInterval = null;

  async function stopScanner() {
    scanning = false;
    if (scanInterval) { clearInterval(scanInterval); scanInterval = null; }
    if (mediaStream) {
      for (const t of mediaStream.getTracks()) t.stop();
      mediaStream = null;
    }
    scannerEl.style.display = 'none';
  }

  async function startScanner() {
    if (!('BarcodeDetector' in window)) {
      setStatus('QR scanning not supported in this browser. Use paste.', 'err');
      return;
    }
    try {
      const supported = await window.BarcodeDetector.getSupportedFormats?.();
      if (supported && !supported.includes('qr_code')) {
        setStatus('QR format not supported. Use paste.', 'err');
        return;
      }
      const detector = new window.BarcodeDetector({ formats: ['qr_code'] });
      mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      videoEl.srcObject = mediaStream;
      scannerEl.style.display = 'block';
      setStatus('Scanning… aim camera at QR', 'muted');
      scanning = true;

      const track = mediaStream.getVideoTracks()[0];
      const imageCapture = 'ImageCapture' in window ? new window.ImageCapture(track) : null;

      async function scanOnce() {
        if (!scanning) return;
        try {
          let bitmap;
          if (imageCapture && imageCapture.grabFrame) {
            bitmap = await imageCapture.grabFrame();
          } else {
            const canvas = document.createElement('canvas');
            canvas.width = videoEl.videoWidth || 640;
            canvas.height = videoEl.videoHeight || 480;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
            bitmap = await createImageBitmap(canvas);
          }
          const codes = await detector.detect(bitmap);
          if (codes && codes.length) {
            const text = codes[0].rawValue || codes[0].displayValue || '';
            if (text) {
              await stopScanner();
              jsonEl.value = text;
              await importJson(text, setStatus, render);
            }
          }
        } catch (e) {
          // swallow intermittent errors during scanning
        }
      }

      // Try to detect every 500ms
      scanInterval = setInterval(scanOnce, 500);
    } catch (e) {
      setStatus(`Camera error: ${e.message}. Use paste.`, 'err');
      await stopScanner();
    }
  }

  scanBtn.onclick = () => {
    if (scanning) {
      stopScanner();
      setStatus('Scanner stopped.', 'muted');
    } else {
      startScanner();
    }
  };

  clearBtn.onclick = async () => {
    const db = await openDb();
    await clearAll(db);
    await render();
    setStatus('Cleared local data', 'ok');
  };

  // Pre-fill with sample if empty (fallback for file://)
  fetch('../../docs/specs/insight_packet_v1.sample.json')
    .then(r => r.ok ? r.text() : Promise.reject(new Error('fetch failed')))
    .then(t => { if (!jsonEl.value) jsonEl.value = t.trim(); })
    .catch(() => {
      if (!jsonEl.value) {
        jsonEl.value = JSON.stringify({
          version: 'v1',
          type: 'plan_daily',
          device_id: 'demo',
          created_at: new Date().toISOString(),
          payload: {
            date: new Date().toISOString().slice(0,10),
            band: 'Maintain',
            score: 65,
            delta: -4,
            plan: { type: 'easy', minutes_range: '30-40', addons: ['core10','breath10'] },
            why: ['sleep −1.2h','RHR +6'],
            schema_version: 'v1.0.0'
          }
        }, null, 2);
      }
    });

  render();
}

setupUI();
