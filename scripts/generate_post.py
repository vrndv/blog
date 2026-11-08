#!/usr/bin/env python3
"""Generate one blog post with Groq and save it as Markdown. Standard library only.

Flow: pick a recent story (Hacker News / RSS feeds) -> read the article text for grounding ->
Groq writes an ORIGINAL explainer with attribution -> checks -> optional openly licensed Openverse image -> save.
Falls back to an evergreen topic if no story can be found.

Env: GROQ_API_KEY (required), GROQ_MODELS (optional override), MIN_WORDS.
Openverse is queried anonymously; no image API key is required.
"""
import html
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "content" / "posts"
CONFIG = json.loads((ROOT / "config" / "topics.json").read_text(encoding="utf-8"))
SOURCES = json.loads((ROOT / "config" / "sources.json").read_text(encoding="utf-8"))
API_URL = "https://api.groq.com/openai/v1/chat/completions"
UA = "Mozilla/5.0 (compatible; blog-engine/1.0)"
PREFERRED_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "llama-3.3-70b-versatile"]
SKIP_MODELS = ("whisper", "tts", "guard", "orpheus", "playai", "embed", "compound", "safeguard")
MIN_WORDS = int(os.environ.get("MIN_WORDS", "700"))
MAX_ATTEMPTS = 2
ALL_CATEGORIES = [c["name"] for c in CONFIG["categories"]]

FORMAT = (
    "\nReply in EXACTLY this format and nothing else:\n"
    "TITLE: <specific, in your own words, 40-90 characters>\n"
    "DESCRIPTION: <one sentence, 90-160 characters>\n"
    "CATEGORY: <exactly one of: " + ", ".join(ALL_CATEGORIES) + ">\n"
    "TAGS: <3 to 5 lowercase tags, comma separated>\n"
    "IMAGE_QUERY: <2-3 plain words describing a generic stock photo, e.g. server room, laptop lock. No brand or people names>\n"
    "===\n"
    "<article body in Markdown, 800-1100 words, no top-level # heading>"
)
COMMON_RULES = (
    "- Cybersecurity content is defensive only: hardening, detection, safe configuration, awareness. "
    "No exploit code, malware, credential theft or attack walk-throughs.\n"
    "- Never invent statistics, quotes, CVE numbers, version numbers or URLs.\n"
    "- Short paragraphs, clear ## and ### headings, fenced code blocks with a language tag for commands.\n"
    "- Commands must be safe on a normal system; warn before anything destructive.\n"
    "- No filler intros like 'In today's fast-paced world'. Be direct.\n"
)
NEWS_SYSTEM = (
    "You are a careful technology writer for an independent blog on Linux, cybersecurity and tech. "
    "You are given source material about a recent story. Write an ORIGINAL explainer based on it.\n"
    "Rules:\n"
    "- For what happened, use only facts present in the source material. Add no names, numbers, dates or "
    "details that are not in it. If the material is thin, say less rather than guess.\n"
    "- Add your own value: general background, why it matters, and concrete steps readers can take.\n"
    "- Do NOT copy sentences or distinctive phrasing from the source and never quote more than 8 words. "
    "Write your own headline, not the source's.\n"
    "- Name the source once, early, with natural attribution (for example: 'According to <Source>, ...').\n"
    "- Suggested sections: ## What happened, ## Why it matters, ## What you can do, ## Key takeaways.\n"
    + COMMON_RULES + FORMAT
)
EVERGREEN_SYSTEM = (
    "You are a careful technical writer for a blog about technology, Linux and defensive cybersecurity.\n"
    "Rules:\n- Write accurate, practical, original articles for beginners to intermediate readers.\n"
    + COMMON_RULES + FORMAT
)


# ---------- helpers ----------
def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:70].strip("-") or "post"


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def fetch(url, timeout=20, max_bytes=800_000, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(max_bytes)
        charset = r.headers.get_content_charset() or "utf-8"
    return data, charset


def clean(text: str, limit=700) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return " ".join(html.unescape(text).split())[:limit]


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d


def frontmatter_values(key: str):
    vals = []
    for p in POSTS_DIR.glob("*.md"):
        m = re.search(rf"^{key}:\s*(.+)$", p.read_text(encoding="utf-8"), re.M)
        if m:
            try:
                vals.append(json.loads(m.group(1)))
            except Exception:
                vals.append(m.group(1).strip('"'))
    return vals


def recent_titles(limit=40):
    files = sorted(POSTS_DIR.glob("*.md"), reverse=True)[:limit]
    out = []
    for p in files:
        m = re.search(r"^title:\s*(.+)$", p.read_text(encoding="utf-8"), re.M)
        if m:
            try:
                out.append(json.loads(m.group(1)))
            except Exception:
                out.append(m.group(1).strip('"'))
    return out


# ---------- story discovery ----------
def parse_feed(raw: bytes, source_name: str):
    root = ET.fromstring(raw)
    items = []
    for el in root.iter():
        if not isinstance(el.tag, str) or el.tag.split("}")[-1] not in ("item", "entry"):
            continue
        d = {"source": source_name}
        for ch in el:
            if not isinstance(ch.tag, str):
                continue
            t = ch.tag.split("}")[-1]
            if t == "title":
                d["title"] = clean(ch.text or "", 300)
            elif t == "link" and "link" not in d:
                href = ch.get("href")
                if href and ch.get("rel", "alternate") == "alternate":
                    d["link"] = href.strip()
                elif ch.text and ch.text.strip():
                    d["link"] = ch.text.strip()
            elif t in ("description", "summary", "content") and "summary" not in d:
                d["summary"] = clean(ch.text or "")
            elif t in ("pubDate", "published", "updated", "date") and "published" not in d:
                d["published"] = parse_date(ch.text)
        if d.get("title") and d.get("link", "").startswith("http"):
            d.setdefault("summary", "")
            d.setdefault("published", None)
            items.append(d)
    return items


def hn_items(cfg):
    raw, cs = fetch("https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=50")
    items = []
    for h in json.loads(raw.decode(cs)).get("hits", []):
        url, title = h.get("url"), h.get("title")
        if not url or not title or (h.get("points") or 0) < cfg.get("min_score", 80):
            continue
        host = urllib.parse.urlparse(url).netloc.removeprefix("www.")
        items.append({
            "title": title, "link": url, "summary": "", "source": host,
            "published": datetime.fromtimestamp(h.get("created_at_i", 0), timezone.utc),
            "points": h.get("points") or 0,
        })
    return items


def group_candidates(group, used_urls, used_titles, now):
    items = []
    try:
        if group["type"] == "hn":
            items = hn_items(group)
        else:
            for feed in group["feeds"]:
                try:
                    raw, _ = fetch(feed["url"])
                    items += parse_feed(raw, feed["name"])
                except Exception as e:
                    print(f"feed failed {feed['name']}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"group failed {group['name']}: {e}", file=sys.stderr)
    cutoff = now - timedelta(days=SOURCES.get("max_age_days", 4))
    kws = SOURCES.get("relevance_keywords", [])
    out = []
    for it in items:
        if it["link"] in used_urls or norm(it["title"]) in used_titles:
            continue
        if it["published"] and it["published"] < cutoff:
            continue
        if group.get("filter") and not any(k in (it["title"] + " " + it["summary"]).lower() for k in kws):
            continue
        out.append(it)
    out.sort(key=lambda i: i["published"] or datetime(1970, 1, 1, tzinfo=timezone.utc), reverse=True)
    return out


class ParaExtractor(HTMLParser):
    SKIP = {"script", "style", "nav", "footer", "header", "aside", "noscript", "form"}

    def __init__(self):
        super().__init__()
        self.skip, self.in_p, self.buf, self.paras = 0, False, [], []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "p" and not self.skip:
            self.in_p, self.buf = True, []

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag == "p" and self.in_p:
            txt = " ".join("".join(self.buf).split())
            if len(txt) > 60:
                self.paras.append(txt)
            self.in_p = False

    def handle_data(self, data):
        if self.in_p and not self.skip:
            self.buf.append(data)


def article_text(url: str) -> str:
    try:
        raw, cs = fetch(url, timeout=20, max_bytes=700_000)
        p = ParaExtractor()
        p.feed(raw.decode(cs, errors="replace"))
        return " ".join(p.paras)[:3500]
    except Exception as e:
        print(f"article fetch failed {url}: {e}", file=sys.stderr)
        return ""


def pick_story(now, used_urls, used_titles):
    groups = SOURCES["groups"]
    slot = (now.hour // 6) % 4
    start = (now.timetuple().tm_yday * 4 + slot) % len(groups)
    for i in range(len(groups)):
        group = groups[(start + i) % len(groups)]
        cands = group_candidates(group, used_urls, used_titles, now)
        for it in cands[:5]:
            material = (article_text(it["link"]) + " " + it["summary"]).strip()
            if len(material) >= 300:
                it["material"] = material[:3800]
                it["group"] = group["name"]
                return it
    return None


# ---------- Groq ----------
def call_groq(model, system, user_prompt, key):
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_prompt}],
        "temperature": 0.6,
        "max_completion_tokens": 4000,
    }
    if "gpt-oss" in model:
        payload["reasoning_effort"] = "low"
    data = json.dumps(payload).encode()
    for attempt in range(4):
        req = urllib.request.Request(API_URL, data=data, method="POST", headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "blog-engine/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())["choices"][0]["message"]["content"] or ""
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                wait = min(float(e.headers.get("retry-after") or 5 * (attempt + 1)), 90)
                print(f"[{model}] HTTP {e.code}, retrying in {wait:.0f}s", file=sys.stderr)
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError(f"network error: {e}")
    raise RuntimeError("exhausted retries")


def parse(raw: str):
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.S).strip()
    head, sep, body = raw.partition("\n===")
    if not sep:
        raise ValueError("missing === separator")
    f = {}
    for key in ("TITLE", "DESCRIPTION", "TAGS", "CATEGORY", "IMAGE_QUERY"):
        m = re.search(rf"^{key}:\s*(.+)$", head, re.M | re.I)
        f[key] = m.group(1).strip().strip('"') if m else ""
    for key in ("TITLE", "DESCRIPTION", "TAGS"):
        if not f[key]:
            raise ValueError(f"missing {key}")
    body = re.sub(r"^# .+\n+", "", body.lstrip("=").strip())
    tags = [t.strip().lower().replace(" ", "-") for t in f["TAGS"].split(",") if t.strip()][:5]
    return f["TITLE"], f["DESCRIPTION"], tags, body, f["CATEGORY"], f["IMAGE_QUERY"]


class CopyError(ValueError):
    def __init__(self, phrase):
        super().__init__(f"copied a long phrase from the source: '{phrase}'")
        self.phrase = phrase


def _tokens(text):
    return re.findall(r"[a-z0-9']+", re.sub(r"```.*?```", " ", text, flags=re.S).lower())


def find_copied(body, material, n=10, max_hits=1):
    """Return the first copied run of 10+ words if the draft repeats the source too closely, else None."""
    st = _tokens(material)
    src = {tuple(st[i:i + n]) for i in range(max(0, len(st) - n + 1))}
    bt = _tokens(body)
    hits = [" ".join(bt[i:i + n]) for i in range(max(0, len(bt) - n + 1)) if tuple(bt[i:i + n]) in src]
    return hits[0] if len(hits) > max_hits else None


def validate(title, desc, tags, body, existing_titles, story=None):
    if not 20 <= len(title) <= 110:
        raise ValueError(f"title length {len(title)}")
    if not 40 <= len(desc) <= 220:
        raise ValueError(f"description length {len(desc)}")
    if len(tags) < 2:
        raise ValueError("too few tags")
    words = len(body.split())
    if words < MIN_WORDS:
        raise ValueError(f"only {words} words")
    if len(re.findall(r"^##\s", body, re.M)) < 3:
        raise ValueError("fewer than 3 headings")
    if body.count("```") % 2:
        raise ValueError("unbalanced code fence")
    low = (title + " " + body).lower()
    for phrase in CONFIG["blocked_phrases"]:
        if phrase in low:
            raise ValueError(f"blocked phrase: {phrase}")
    if norm(title) in {norm(t) for t in existing_titles}:
        raise ValueError("duplicate title")
    if story:
        a, b = set(norm(title).split()), set(norm(story["title"]).split())
        if a and b and len(a & b) / len(a | b) >= 0.75:
            raise ValueError("title too close to source headline")
        copied = find_copied(body, story["material"])
        if copied:
            raise CopyError(copied)


# ---------- images ----------
def find_image(query, used_images):
    """Find a commercially reusable, openly licensed image via Openverse.

    Anonymous Openverse requests are rate-limited, so this workflow makes only
    one small search per generated post. A failed search is non-fatal: the site
    displays its built-in generated cover instead.
    """
    if not query:
        return None
    try:
        url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({
            "q": query,
            "page_size": 20,
            "license_type": "commercial",
            "mature": "false",
        })
        raw, cs = fetch(url, timeout=25, headers={"Accept": "application/json"})
        results = json.loads(raw.decode(cs)).get("results", [])
        random.shuffle(results)
        for item in results:
            src = item.get("url")
            landing = item.get("foreign_landing_url")
            license_url = item.get("license_url")
            license_code = (item.get("license") or "").upper()
            if not src or src in used_images or not landing or not license_url or not license_code:
                continue
            creator = (item.get("creator") or "").strip()
            creator_url = item.get("creator_url") or landing
            title = (item.get("title") or "").strip()
            return {
                "image": src,
                "image_alt": title or item.get("attribution") or query,
                "image_credit": creator or "Unknown creator",
                "image_credit_url": creator_url,
                "image_source_url": landing,
                "image_license": f"{license_code}{(' ' + str(item.get('license_version'))) if item.get('license_version') else ''}",
                "image_license_url": license_url,
            }
    except Exception as e:
        print(f"Openverse image search failed: {e}", file=sys.stderr)
    return None


# ---------- main ----------
def write_post(now, title, desc, tags, body, category, model, story, img):
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    path = POSTS_DIR / f"{now:%Y-%m-%d-%H%M}-{slugify(title)}.md"
    lines = [
        "---",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"description: {json.dumps(desc, ensure_ascii=False)}",
        f"date: {now.isoformat(timespec='seconds')}",
        f"category: {json.dumps(category)}",
        f"tags: {json.dumps(tags)}",
    ]
    if story:
        lines += [f"source_name: {json.dumps(story['source'], ensure_ascii=False)}",
                  f"source_url: {json.dumps(story['link'])}"]
    if img:
        for k, v in img.items():
            lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    lines += ["draft: false", "ai_assisted: true", f"model: {json.dumps(model)}", "---", ""]
    path.write_text("\n".join(lines) + body + "\n", encoding="utf-8")
    return path


def pick_models(key):
    env = os.environ.get("GROQ_MODELS")
    if env:
        return [x.strip() for x in env.split(",") if x.strip()]
    try:
        raw, cs = fetch("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {key}"})
        ids = [x["id"] for x in json.loads(raw.decode(cs)).get("data", []) if x.get("active", True)]
    except Exception as e:
        print(f"could not list models ({e}); using defaults", file=sys.stderr)
        return PREFERRED_MODELS[:2]
    chosen = [x for x in PREFERRED_MODELS if x in ids]
    chosen += [i for i in ids if i not in chosen and not any(k in i.lower() for k in SKIP_MODELS)][:2]
    print("Models to try:", chosen)
    return chosen or PREFERRED_MODELS[:2]


def attempt_models(models, system, prompt, key, existing, story):
    last, extra = "unknown", ""
    for model in models:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                raw = call_groq(model, system, prompt + extra, key)
                parsed = parse(raw)
                validate(*parsed[:4], existing, story)
                return model, parsed
            except CopyError as e:
                last = f"{model} attempt {attempt}: {e}"
                print(last, file=sys.stderr)
                extra = ("\n\nIMPORTANT: your previous draft reused this passage from the source: "
                         f"\"{e.phrase}\". Rewrite the WHOLE article in completely different words. "
                         "Do not quote the source; explain ideas in your own phrasing.")
            except ValueError as e:
                last = f"{model} attempt {attempt}: {e}"
                print(last, file=sys.stderr)
            except RuntimeError as e:
                last = f"{model} attempt {attempt}: {e}"
                print(last, file=sys.stderr)
                break  # API-level problem: try the next model
    print(f"All attempts failed. Last error: {last}", file=sys.stderr)
    return None


def main() -> int:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        print("GROQ_API_KEY is not set", file=sys.stderr)
        return 1
    now = datetime.now(timezone.utc)
    existing = recent_titles()
    used_urls = set(frontmatter_values("source_url"))
    used_images = set(frontmatter_values("image"))
    used_titles = {norm(t) for t in existing}
    avoid = "\n".join(f"- {t}" for t in existing[:25]) or "(none yet)"
    models = pick_models(key)

    result, fixed_category = None, None
    story = pick_story(now, used_urls, used_titles)
    if story:
        print(f"Story: {story['title']} ({story['source']}, group {story['group']})", flush=True)
        prompt = (f"Source site: {story['source']}\nSource URL: {story['link']}\n"
                  f"Original headline (do not reuse): {story['title']}\n\nSOURCE MATERIAL:\n{story['material']}\n\n"
                  f"Recent blog titles to avoid resembling:\n{avoid}")
        result = attempt_models(models, NEWS_SYSTEM, prompt, key, existing, story)
    if result is None:
        print("Writing an evergreen post instead", file=sys.stderr, flush=True)
        story = None
        cats = [c for c in CONFIG["categories"] if c.get("seeds")]
        slot = (now.hour // 6) % 4
        cat = cats[(now.timetuple().tm_yday * 4 + slot) % len(cats)]
        seed = random.Random(f"{now.date()}-{slot}").choice(cat["seeds"])
        prompt = (f"Category: {cat['name']}\nTopic idea: {seed}\nPick a fresh, specific angle. "
                  f"Do NOT resemble these recent titles:\n{avoid}")
        fixed_category = cat["name"]
        result = attempt_models(models, EVERGREEN_SYSTEM, prompt, key, existing, None)
    if result is None:
        return 1

    model, (title, desc, tags, body, category, img_query) = result
    category = fixed_category or (category if category in ALL_CATEGORIES else "Tech News")
    img = find_image(img_query, used_images)
    path = write_post(now, title, desc, tags, body, category, model, story, img)
    print(f"Wrote {path.relative_to(ROOT)} ({len(body.split())} words, {model}, image={'yes' if img else 'no'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
