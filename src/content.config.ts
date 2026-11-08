import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './content/posts' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    category: z.string().default('General'),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    ai_assisted: z.boolean().default(false),
    model: z.string().optional(),
    source_name: z.string().optional(),
    source_url: z.string().optional(),
    image: z.string().optional(),
    image_alt: z.string().optional(),
    image_credit: z.string().optional(),
    image_credit_url: z.string().optional(),
    image_source_url: z.string().optional(),
    image_license: z.string().optional(),
    image_license_url: z.string().optional(),
  }),
});

export const collections = { posts };
