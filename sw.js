const CACHE_NAME = 'basim-studio-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // تمرير الطلبات للشبكة مباشرة
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
