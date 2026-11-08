# Blog Engine

Every 6 hours (05:03, 11:03, 17:03, 23:03 UTC) a GitHub Action:
1. picks a recent story (Hacker News front page, then security / Linux / tech RSS feeds),
2. reads the article text for grounding,
3. has Groq write an ORIGINAL explainer that names and links the source (copy checks included),
4. adds a free Pexels photo (or a generated cover if none),
5. commits the post, then rebuilds and deploys the Astro site to GitHub Pages.
If no story is found it writes an evergreen post from `config/topics.json`.

## One-time setup
1. Public GitHub repo, upload everything here (keep `.github/`).
2. Secrets (Settings -> Secrets and variables -> Actions -> Secrets):
   - `GROQ_API_KEY` from https://console.groq.com (required)
   - `PEXELS_API_KEY` from https://www.pexels.com/api/ (free, optional; no key = generated covers only)
3. Settings -> Pages -> Source: **GitHub Actions**.
4. Custom domain / sub-path (Settings -> Secrets and variables -> Actions -> Variables):
   - `SITE_URL` = https://yourdomain.com
   - `BASE_PATH` = only if you want to override. Default is `/` for a repo named USER.github.io, else `/<repo-name>` (so repo `blog` + domain varundev.tech gives varundev.tech/blog/).
5. Run "Publish blog post" once by hand (Actions tab), then check the deploy.
6. Edit `src/config.ts` (name, description, email).

## Sources
Edit `config/sources.json` (feeds, keywords, max age). Feed URLs can change; failing feeds are skipped.
Posts are written in original words, link to the source, and are rejected if they reuse a 9-word run from it.
Source-site images are never copied.

## Ads (Google AdSense)
1. Apply at adsense.google.com once the site has real content. Approval is not guaranteed.
2. After approval put your publisher ID in `src/config.ts`: `adsense.client: 'ca-pub-...'`. With only that set, Auto ads place themselves.
   Optional manual slots: create ad units in AdSense and paste their IDs into `adsense.slots`.
3. `ads.txt`: needs to live at the ROOT of your domain. The site generates the line at /ads.txt (under your base path); copy it to the root site if the blog is in a sub-path.
4. In AdSense -> Privacy & messaging: publish a consent message (required for EEA/UK) and turn on the **Ad blocking recovery** message.

## Removing a post
Delete its file in `content/posts/` (or set `draft: true`). The site redeploys on that push.

## Site features
Static HTML (only JS: light/dark toggle), per-page meta + Open Graph, JSON-LD (WebSite, BlogPosting, BreadcrumbList), sitemap, robots.txt, RSS,
/llms.txt, /api/posts.json, Markdown copy of each post at /posts/<slug>.md, About / Editorial policy / Privacy pages.
