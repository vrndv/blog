import type { APIRoute } from 'astro';
import { SITE } from '../config';

// NOTE: ad networks only read ads.txt from the ROOT of your domain (example.com/ads.txt).
// If this site lives under a sub-path such as /blog/, copy this line into the root file.
export const GET: APIRoute = () => {
  const pub = SITE.adsense.client.replace(/^ca-/, '');
  const body = pub
    ? `google.com, ${pub}, DIRECT, f08c47fec0942fa0\n`
    : '# Set adsense.client in src/config.ts to generate your ads.txt line.\n';
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
