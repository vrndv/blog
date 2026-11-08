import { getCollection } from 'astro:content';
import { slugify } from './util';

const DATE_PREFIX = /^\d{4}-\d{2}-\d{2}-\d{4}-/;

/** Published posts, newest first, each with a clean URL slug (date prefix removed). */
export async function getPosts() {
  const entries = (await getCollection('posts', ({ data }) => !data.draft)).sort(
    (a, b) => a.data.date.valueOf() - b.data.date.valueOf(),
  );
  // Oldest first, so the earliest post keeps a short slug if two ever collide.
  const seen = new Set<string>();
  const withSlugs = entries.map((entry) => {
    let slug = entry.id.replace(DATE_PREFIX, '');
    if (seen.has(slug)) slug = entry.id;
    seen.add(slug);
    return { ...entry, slug };
  });
  return withSlugs.reverse();
}

export type PostWithSlug = Awaited<ReturnType<typeof getPosts>>[number];

export function categoryCounts(posts: PostWithSlug[]) {
  const map = new Map<string, number>();
  for (const p of posts) map.set(p.data.category, (map.get(p.data.category) ?? 0) + 1);
  return [...map.entries()]
    .map(([name, count]) => ({ name, slug: slugify(name), count }))
    .sort((a, b) => a.name.localeCompare(b.name));
}
