import type { APIRoute } from 'astro';
import { getPosts } from '../../lib/posts';
import { SITE } from '../../config';
import { absUrl, wordCount } from '../../lib/util';

export const GET: APIRoute = async ({ site }) => {
  const posts = await getPosts();
  const body = {
    site: SITE.name,
    description: SITE.description,
    generated: new Date().toISOString(),
    count: posts.length,
    posts: posts.map((p) => ({
      title: p.data.title,
      description: p.data.description,
      published: p.data.date.toISOString(),
      category: p.data.category,
      tags: p.data.tags,
      words: wordCount(p.body),
      ai_assisted: p.data.ai_assisted,
      url: absUrl(`/posts/${p.slug}/`, site),
      markdown: absUrl(`/posts/${p.slug}.md`, site),
    })),
  };
  return new Response(JSON.stringify(body, null, 2), {
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  });
};
