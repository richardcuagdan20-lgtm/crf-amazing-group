/**
 * Prefix an internal path with the Astro base (e.g. /crf-amazing-group).
 * Leave external, tel, mailto, viber, and WhatsApp links unchanged.
 */
export function withBase(path = "/") {
  if (path == null || path === "") path = "/";
  if (
    /^(https?:|mailto:|tel:|viber:|sms:)/i.test(path) ||
    path.startsWith("//") ||
    path.startsWith("#") ||
    path.startsWith("data:")
  ) {
    return path;
  }
  const raw = import.meta.env.BASE_URL || "/";
  const base = raw.endsWith("/") ? raw.slice(0, -1) : raw;
  if (path === "/") return base || "/";
  const p = path.startsWith("/") ? path : `/${path}`;
  if (base && (p === base || p.startsWith(`${base}/`))) return p;
  return `${base}${p}`;
}

/** Pathname with the deploy base removed, for current-page checks. */
export function pagePath(pathname) {
  const raw = import.meta.env.BASE_URL || "/";
  const base = raw.endsWith("/") ? raw.slice(0, -1) : raw;
  let path = (pathname || "/").replace(/\/$/, "") || "/";
  if (base && (path === base || path.startsWith(`${base}/`))) {
    path = path.slice(base.length) || "/";
  }
  return path;
}
