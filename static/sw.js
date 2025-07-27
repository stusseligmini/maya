// Maya AI Service Worker for PWA functionality
const CACHE_NAME = 'maya-ai-v1.0.0';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/app.js',
  '/static/manifest.json',
  '/health',
  '/api/dashboard/stats'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📱 Maya AI PWA: Caching app shell');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('📱 Maya AI PWA: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Push notification handling
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New content ready for review!',
    icon: '/static/icon-192.png',
    badge: '/static/badge.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Content',
        icon: '/static/view-icon.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/close-icon.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Maya AI', options)
  );
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  return fetch('/api/sync')
    .then(response => {
      console.log('📱 Background sync completed');
      return response;
    })
    .catch(err => {
      console.log('📱 Background sync failed:', err);
    });
}
