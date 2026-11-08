# Blog Engine

Module 1: Groq writes 4 posts/day (05:03, 11:03, 17:03, 23:03 UTC) and commits them to `content/posts/`.
Module 2: an Astro static site rebuilds and deploys to GitHub Pages after every new post. All free.

## One-time setup
1. Create a **public** GitHub repo. For best SEO name it `YOURUSERNAME.github.io`
   (the site then lives at the domain root, so robots.txt and sitemap work properly).
2. Upload everything in this folder, keeping the `.github/` folder.
3. Add your Groq key (free at https://console.groq.com):
   Settings -> Secrets and variables -> Actions -> New repository secret -> `GROQ_API_KEY`.
4. Settings -> Pages -> Build and deployment -> Source: **GitHub Actions**.
5. Actions tab -> "Publish blog post" -> Run workflow. It writes a post and starts the deploy.
   (Or run "Deploy site" by hand.) Your site appears at the URL shown in the deploy job.
6. Edit `src/config.ts` (site name, description, email) and push.

Custom domain later: add a repository *variable* `SITE_URL` (e.g. https://example.com) and set the domain in Settings -> Pages.

## Removing a post
Delete its file in `content/posts/` (or set `draft: true`). The site redeploys on that push.

## What the site includes
- Static HTML, no JavaScript except a tiny light/dark toggle (remembers choice, respects system setting)
- Per-page title, description, canonical, Open Graph and Twitter tags
- JSON-LD: WebSite, BlogPosting, BreadcrumbList
- XML sitemap, robots.txt, RSS, paginated home and category pages, related-article links
- Agent-friendly: /llms.txt, /api/posts.json (full index), and a Markdown copy of every post at /posts/<slug>.md
- About, Editorial policy (AI disclosure) and Privacy pages

## Free-tier notes
- Groq limits are per organisation and can change; check your console limits page.
- Public repo = unlimited Actions minutes and free Pages. Each deploy takes about 1-2 minutes.
- Pages sites have a soft 1 GB size and 100 GB/month bandwidth limit; text posts will not come close.
# blog
