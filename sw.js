/* Planner badge worker 2026.10.08.3-r1. No cache and no fetch interception.
   Never handles, stores or transmits plan content or access keys. */
self.addEventListener('install',event=>event.waitUntil(self.skipWaiting()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
