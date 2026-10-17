/* The Room's service worker (1.0.8): keeps the app shell for a poor signal, and shows notifications.
   A push carries only a production id; the name comes from this phone's own store. Nothing else is in a push. */
const SHELL = "room-shell-1.0.8";
const FILES = ["/app/", "/app/index.html", "/app/app.css", "/app/app.js", "/app/room-crypto.js", "/app/words.txt",
  "/app/vendor/libsodium.js", "/app/vendor/libsodium-wrappers.js", "/app/vendor/livekit-client.umd.js",
  "/app/vendor/livekit-client.e2ee.worker.js", "/app/fonts/Geist-Variable.woff2", "/app/fonts/SourceSerif4-Variable.woff2",
  "/app/fonts/GeistMono-Variable.woff2", "/app/icons/icon-192.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(SHELL).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== SHELL).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin || !u.pathname.startsWith("/app/")) return;   /* the API always goes to the network */
  e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); if (r.ok) caches.open(SHELL).then(c => c.put(e.request, copy)); return r; })
    .catch(() => caches.match(e.request).then(r => r || caches.match("/app/"))));
});
function productionName(id) {
  return new Promise(resolve => {
    const rq = indexedDB.open("room", 1);
    rq.onupgradeneeded = () => { const db = rq.result; ["kv", "items", "wraps", "names"].forEach(s => db.objectStoreNames.contains(s) || db.createObjectStore(s)); };
    rq.onerror = () => resolve("");
    rq.onsuccess = () => { try { const g = rq.result.transaction("names").objectStore("names").get(id); g.onsuccess = () => resolve(g.result || ""); g.onerror = () => resolve(""); } catch (err) { resolve(""); } };
  });
}
self.addEventListener("push", e => {
  let p = "";
  try { p = (e.data && e.data.json() || {}).p || ""; } catch (err) { /* nothing to read */ }
  e.waitUntil(productionName(p).then(name => self.registration.showNotification(name ? `Something new in ${name}` : "Something new in the Room",
    { body: "Open the Room to see it.", tag: p || "room", icon: "/app/icons/icon-192.png", badge: "/app/icons/icon-192.png" })));
});
self.addEventListener("notificationclick", e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: "window" }).then(ws => { for (const w of ws) if (w.url.includes("/app/")) return w.focus(); return self.clients.openWindow("/app/"); }));
});
