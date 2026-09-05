const CACHE='bbts-live-v4';
const ASSETS=['./','./index.html','./events.json','./manifest.webmanifest','./assets/bbts-logo.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));
self.addEventListener('fetch',e=>e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request))));
