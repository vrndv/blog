export const withBase = (path: string) =>
  import.meta.env.BASE_URL.replace(/\/$/, '') + path;

export const absUrl = (path: string, site: URL | undefined) =>
  new URL(withBase(path), site ?? 'https://example.github.io').toString();

export const slugify = (s: string) =>
  s.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');

export const fmtDate = (d: Date) =>
  d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });

export const wordCount = (body?: string) => (body ?? '').split(/\s+/).filter(Boolean).length;

export const readingMinutes = (body?: string) => Math.max(1, Math.round(wordCount(body) / 220));

export const escapeJson = (o: unknown) => JSON.stringify(o).replace(/</g, '\\u003c');

export const coverGradient = (seed: string) => {
  let h = 0;
  for (const c of seed) h = (h * 31 + c.charCodeAt(0)) % 360;
  return `linear-gradient(135deg, hsl(${h} 55% 30%), hsl(${(h + 45) % 360} 60% 20%))`;
};

export const hostOf = (url?: string) => {
  try { return new URL(url ?? '').hostname.replace(/^www\./, ''); } catch { return ''; }
};
