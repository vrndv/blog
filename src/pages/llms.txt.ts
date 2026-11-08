import type { APIRoute } from 'astro';
import { getPosts } from '../lib/posts';
import { SITE } from '../config';
import { absUrl } from '../lib/util';

export const GET: APIRoute = async ({ site }) => {
  const posts = (await getPosts()).slice(0, 50);
  const lines = [
    `# ${SITE.name}`,
    '',
    `> ${SITE.description}`,
    '',
    'Content is free to read.',
    '',
    '## Machine-readable access',
    '',
    `- [Full article index (JSON)](${absUrl('/api/posts.json', site)}): every article with metadata and Markdown URL`,
    `- [RSS feed](${absUrl('/rss.xml', site)}): latest 50 articles`,
    `- [Sitemap](${absUrl('/sitemap-index.xml', site)})`,
    '- Every article also exists as Markdown: replace the trailing slash of its URL with .md',
    '',
    '## Latest articles',
    '',
    ...posts.map((p) => `- [${p.data.title}](${absUrl(`/posts/${p.slug}.md`, site)}): ${p.data.description}`),
    '',
  ];
  return new Response(lines.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
