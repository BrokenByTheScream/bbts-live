const CACHE='bbts-live-v2';
const ASSETS=['./','./index.html','./manifest.webmanifest','./assets/bbts-live-bg.png','./assets/bbts-logo.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));
self.addEventListener('fetch',e=>e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request))));
