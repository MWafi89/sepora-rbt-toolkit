/* =========================================================================
   SEPORA RBT TOOLKIT - Service Worker (PWA)
   Tujuan: aplikasi boleh dibuka & dijana OFFLINE (kelas tanpa internet),
   data kekal dalam storan peranti (localStorage) + arkib Google Drive DELIMa.
   Naikkan CACHE_VERSION setiap kali deploy supaya guru dapat versi terbaru.
   ========================================================================= */
const CACHE_VERSION = 'sepora-rbt-v3-2026-09-12b';
const SHELL = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-maskable-512.png',
  '/icons/apple-touch-icon.png'
];
// Sumber CDN (fon/ikon/library eksport) - dicache supaya eksport PDF/Word jalan offline
const CDN = [
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.6.0/mammoth.browser.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.umd.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE_VERSION);
    for (const u of SHELL) { try { await c.add(new Request(u, { cache: 'reload' })); } catch (err) { } }
    for (const u of CDN) { try { await c.add(new Request(u, { mode: 'cors' })); } catch (err) { } }
    self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

function isDriveApi(url) {
  return /googleapis\.com|accounts\.google\.com|gstatic\.com\/accounts/.test(url);
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;                 // POST/PUT/PATCH (Drive) -> terus ke rangkaian
  const url = new URL(req.url);
  if (isDriveApi(req.url)) return;                  // jangan cache API Google
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;

  // Navigasi: cuba rangkaian dahulu (dapat versi terbaru), jika offline guna cache
  if (req.mode === 'navigate') {
    e.respondWith((async () => {
      try {
        const fresh = await fetch(req);
        const c = await caches.open(CACHE_VERSION);
        c.put('/index.html', fresh.clone()).catch(() => { });
        return fresh;
      } catch (err) {
        const c = await caches.open(CACHE_VERSION);
        return (await c.match('/index.html')) || (await c.match('/')) || Response.error();
      }
    })());
    return;
  }

  // Aset lain: cache dahulu, kemas kini di latar belakang (stale-while-revalidate)
  e.respondWith((async () => {
    const c = await caches.open(CACHE_VERSION);
    const hit = await c.match(req, { ignoreSearch: url.origin === location.origin });
    const net = fetch(req).then(res => { if (res && res.status === 200) c.put(req, res.clone()).catch(() => { }); return res; }).catch(() => null);
    return hit || (await net) || Response.error();
  })());
});

self.addEventListener('message', (e) => {
  if (e.data === 'SEPORA_SKIP_WAITING') self.skipWaiting();
});
