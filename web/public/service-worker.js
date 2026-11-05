const CACHE_NAME = 'sportlink-pwa-v1'
const APP_SHELL = [
  '/',
  '/manifest.webmanifest',
  '/icons/icon-180.png',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting()),
  )
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => Promise.all(
        cacheNames
          .filter((cacheName) => cacheName.startsWith('sportlink-pwa-') && cacheName !== CACHE_NAME)
          .map((cacheName) => caches.delete(cacheName)),
      ))
      .then(() => self.clients.claim()),
  )
})

self.addEventListener('fetch', (event) => {
  const request = event.request
  const url = new URL(request.url)

  if (
    request.method !== 'GET'
    || url.origin !== self.location.origin
    || url.pathname.startsWith('/api/')
    || url.pathname.startsWith('/admin/')
    || url.pathname.startsWith('/downloads/')
  ) {
    return
  }

  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME)

    try {
      const response = await fetch(request)
      if (response.ok && response.type === 'basic') {
        try {
          await cache.put(request, response.clone())
        } catch (error) {
          console.error('Failed to cache a Sportlink resource.', error)
        }
      }
      return response
    } catch (error) {
      const cachedResponse = await cache.match(request)
      if (cachedResponse) return cachedResponse

      if (request.mode === 'navigate') {
        const appShell = await cache.match('/')
        if (appShell) return appShell
      }

      throw error
    }
  })())
})
