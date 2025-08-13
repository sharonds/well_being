// Minimal IndexedDB helper
const DB_NAME = 'wellbeing-db';
const STORE = 'insights';

export async function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(STORE)) {
        const os = db.createObjectStore(STORE, { keyPath: 'key' });
        os.createIndex('byDate', 'payload.date');
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export async function putInsight(db, envelope) {
  // idempotent key: date + type
  const key = `insight:${envelope.payload.date}:${envelope.type}`;
  const tx = db.transaction(STORE, 'readwrite');
  const store = tx.objectStore(STORE);

  // last-write-wins by created_at (if existing)
  await new Promise((resolve, reject) => {
    const getReq = store.get(key);
    getReq.onsuccess = () => {
      const existing = getReq.result;
      const shouldWrite = !existing || (existing.created_at || '') <= (envelope.created_at || '');
      if (!shouldWrite) return resolve();
      const putReq = store.put({ key, ...envelope });
      putReq.onsuccess = () => resolve();
      putReq.onerror = () => reject(putReq.error);
    };
    getReq.onerror = () => reject(getReq.error);
  });

  await new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.onabort = () => reject(tx.error);
  });
  return key;
}

export async function listInsights(db) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readonly');
    const store = tx.objectStore(STORE);
    const out = [];
    const cursorReq = store.openCursor();
    cursorReq.onsuccess = () => {
      const cursor = cursorReq.result;
      if (cursor) {
        out.push(cursor.value);
        cursor.continue();
      } else {
        resolve(out);
      }
    };
    cursorReq.onerror = () => reject(cursorReq.error);
  });
}

export async function clearAll(db) {
  const tx = db.transaction(STORE, 'readwrite');
  const store = tx.objectStore(STORE);
  await new Promise((resolve, reject) => {
    const req = store.clear();
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
  await new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.onabort = () => reject(tx.error);
  });
}
