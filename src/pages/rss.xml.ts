import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { getPosts } from '../lib/posts';
import { SITE } from '../config';
import { withBase } from '../lib/util';

export async function GET(context: APIContext) {
  const posts = (await getPosts()).slice(0, 50);
  return rss({
    title: SITE.name,
    description: SITE.description,
    site: context.site!,
    items: posts.map((p) => ({
      title: p.data.title,
      description: p.data.description,
      pubDate: p.data.date,
      link: withBase(`/posts/${p.slug}/`),
      categories: [p.data.category, ...p.data.tags],
    })),
    customData: `<language>${SITE.lang}</language>`,
  });
}
