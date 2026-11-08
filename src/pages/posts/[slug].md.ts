import type { APIRoute } from 'astro';
import { getPosts } from '../../lib/posts';
import { SITE } from '../../config';
import { absUrl } from '../../lib/util';

export async function getStaticPaths() {
  const posts = await getPosts();
  return posts.map((post) => ({ params: { slug: post.slug }, props: { post } }));
}

// Plain Markdown version of each article for agents and tools.
export const GET: APIRoute = ({ props, site }) => {
  const { post } = props as { post: Awaited<ReturnType<typeof getPosts>>[number] };
  const d = post.data;
  const url = absUrl(`/posts/${post.slug}/`, site);
  const md = [
    `# ${d.title}`,
    '',
    `> ${d.description}`,
    '',
    `- Source: ${url}`,
    `- Published: ${d.date.toISOString()}`,
    `- Category: ${d.category}`,
    `- Tags: ${d.tags.join(', ')}`,
    `- Publisher: ${SITE.name}`,
    d.source_url ? `- Based on reporting from: ${d.source_name ?? ''} ${d.source_url}` : '',
    d.ai_assisted ? '- Note: written with AI assistance and published without individual human review.' : '',
    '',
    post.body ?? '',
    '',
  ].filter((l, i, a) => !(l === '' && a[i - 1] === '')).join('\n');
  return new Response(md, { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
};
