from __future__ import annotations

from django.http import HttpResponse
from django.templatetags.static import static


def manifest(request):
    """
    Serve the web app manifest under /app/invoice/ so the PWA is clearly scoped.
    """
    content = {
        "name": "نظام تحصيل التعدين",
        "short_name": "التحصيل",
        "description": "نظام التحصيل الإلكتروني - فواتير وإيصالات التعدين",
        "start_url": "/app/invoice/",
        "scope": "/app/invoice/",
        "display": "standalone",
        "dir": "rtl",
        "lang": "ar",
        "theme_color": "#1d4ed8",
        "background_color": "#f9fafb",
        "icons": [
            {
                "src": static("form15_tra/icons/icon-192.png"),
                "sizes": "192x192",
                "type": "image/png",
            },
            {
                "src": static("form15_tra/icons/icon-512.png"),
                "sizes": "512x512",
                "type": "image/png",
            },
        ],
    }
    import json

    resp = HttpResponse(
        json.dumps(content, ensure_ascii=False, separators=(",", ":")),
        content_type="application/manifest+json; charset=utf-8",
    )
    resp["Cache-Control"] = "public, max-age=300"
    return resp


def offline(request):
    """
    Same-origin offline fallback page for service worker navigations.
    """
    from django.conf import settings
    from django.contrib.staticfiles import finders

    rel_path = "form15_tra/offline.html"
    abs_path = finders.find(rel_path)
    if not abs_path:
        return HttpResponse("Offline", content_type="text/plain; charset=utf-8", status=404)

    with open(abs_path, "rb") as f:
        data = f.read()

    resp = HttpResponse(data, content_type="text/html; charset=utf-8")
    resp["Cache-Control"] = "public, max-age=0"
    return resp


def service_worker(request):
    """
    Serve the service worker under /app/invoice/ so it can control that scope.
    """
    css_url = static("form15_tra/css/app.css")
    offline_url = "/app/invoice/offline/"
    icon_192 = static("form15_tra/icons/icon-192.png")
    icon_512 = static("form15_tra/icons/icon-512.png")

    js = f"""/* PWA service worker (Form15 scope) */
const CACHE_VERSION = "form15-tra-pwa-v1";
const OFFLINE_URL = "{offline_url}";
const PRECACHE_URLS = [
  "{css_url}",
  "{icon_192}",
  "{icon_512}",
  OFFLINE_URL,
];

self.addEventListener("install", (event) => {{
  event.waitUntil((async () => {{
    const cache = await caches.open(CACHE_VERSION);
    await Promise.all(PRECACHE_URLS.map(async (url) => {{
      try {{
        const absolute = new URL(url, self.location.href);
        const isCrossOrigin = absolute.origin !== self.location.origin;
        const req = isCrossOrigin ? new Request(absolute.href, {{ mode: "no-cors" }}) : new Request(absolute.href);
        const res = await fetch(req);
        // Cache opaque (no-cors) and ok responses. Never fail install for one asset.
        if (res && (res.ok || res.type === "opaque")) {{
          await cache.put(absolute.href, res.clone());
        }}
      }} catch (e) {{
        // ignore
      }}
    }}));
  }})());
  self.skipWaiting();
}});

self.addEventListener("activate", (event) => {{
  event.waitUntil(
    (async () => {{
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => (k === CACHE_VERSION ? null : caches.delete(k))));
      await self.clients.claim();
    }})()
  );
}});

function isNavigationRequest(request) {{
  return request.mode === "navigate" || (request.method === "GET" && request.headers.get("accept")?.includes("text/html"));
}}

self.addEventListener("fetch", (event) => {{
  const request = event.request;
  if (request.method !== "GET") return;

  if (isNavigationRequest(request)) {{
    event.respondWith(
      (async () => {{
        try {{
          const networkResponse = await fetch(request);
          return networkResponse;
        }} catch (e) {{
          const cache = await caches.open(CACHE_VERSION);
          const cachedOffline = await cache.match(OFFLINE_URL);
          return cachedOffline || new Response("Offline", {{ status: 503, headers: {{ "Content-Type": "text/plain; charset=utf-8" }} }});
        }}
      }})()
    );
    return;
  }}

  // Static assets: cache-first
  event.respondWith(
    (async () => {{
      const cached = await caches.match(request);
      if (cached) return cached;
      const response = await fetch(request);
      const url = new URL(request.url);
      if (response.ok && (url.pathname.startsWith("/static/") || url.pathname.includes("/media/"))) {{
        const cache = await caches.open(CACHE_VERSION);
        cache.put(request, response.clone());
      }}
      return response;
    }})()
  );
}});
"""

    resp = HttpResponse(js, content_type="application/javascript; charset=utf-8")
    resp["Cache-Control"] = "public, max-age=0"
    return resp

