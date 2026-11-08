#!/usr/bin/env python3
"""Generate one blog post with Groq and save it as Markdown.

Standard library only. Needs env var GROQ_API_KEY.
Optional env: GROQ_MODELS (comma list, tried in order), MIN_WORDS.
"""
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "content" / "posts"
CONFIG = json.loads((ROOT / "config" / "topics.json").read_text(encoding="utf-8"))
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELS = [m.strip() for m in os.environ.get(
    "GROQ_MODELS", "openai/gpt-oss-120b,llama-3.3-70b-versatile").split(",") if m.strip()]
MIN_WORDS = int(os.environ.get("MIN_WORDS", "700"))
MAX_ATTEMPTS = 3

SYSTEM_PROMPT = """You are a careful technical writer for a blog about technology, Linux and defensive cybersecurity.
Rules:
- Write accurate, practical, original articles for beginners to intermediate readers.
- Cybersecurity content must be defensive only: hardening, detection, safe configuration, awareness. No exploit code, malware, credential theft or attack walk-throughs.
- Never invent statistics, quotes, studies, CVE numbers, version numbers or URLs. If unsure of a specific fact, describe it generally.
- Use short paragraphs, clear ## and ### headings, and fenced code blocks with a language tag for commands.
- Commands must be safe to run on a normal system; warn before anything destructive.
- No filler intro like "In today's fast-paced world". Be direct.

Reply in EXACTLY this format and nothing else:
TITLE: <specific, 40-90 characters>
DESCRIPTION: <one sentence summary, 90-160 characters>
TAGS: <3 to 5 lowercase tags, comma separated>
===
<article body in Markdown, 800-1100 words, no top-level # heading>"""


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:70].strip("-") or "post"


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def recent_titles(limit: int = 40):
    titles = []
    for p in sorted(POSTS_DIR.glob("*.md"), reverse=True)[:limit]:
        m = re.search(r'^title:\s*(.+)$', p.read_text(encoding="utf-8"), re.M)
        if m:
            try:
                titles.append(json.loads(m.group(1)))
            except Exception:
                titles.append(m.group(1).strip('"'))
    return titles


def pick_topic(now: datetime):
    slot = (now.hour // 6) % 4  # 05->0, 11->1, 17->2, 23->3
    cats = CONFIG["categories"]
    cat = cats[(now.timetuple().tm_yday * 4 + slot) % len(cats)]
    rng = random.Random(f"{now.date()}-{slot}")
    return cat["name"], rng.choice(cat["seeds"])


def call_groq(model: str, user_prompt: str, key: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_completion_tokens": 4500,
    }
    if "gpt-oss" in model:
        payload["reasoning_effort"] = "low"
    data = json.dumps(payload).encode()
    for attempt in range(4):
        req = urllib.request.Request(API_URL, data=data, method="POST", headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "blog-engine/1.0",
        })
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read())
            return body["choices"][0]["message"]["content"] or ""
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
    fields = {}
    for key in ("TITLE", "DESCRIPTION", "TAGS"):
        m = re.search(rf"^{key}:\s*(.+)$", head, re.M | re.I)
        if not m:
            raise ValueError(f"missing {key}")
        fields[key] = m.group(1).strip().strip('"')
    body = body.lstrip("=").strip()
    body = re.sub(r"^# .+\n+", "", body)  # drop accidental H1
    tags = [t.strip().lower().replace(" ", "-") for t in fields["TAGS"].split(",") if t.strip()][:5]
    return fields["TITLE"], fields["DESCRIPTION"], tags, body


def validate(title, desc, tags, body, existing_titles):
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


def main() -> int:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        print("GROQ_API_KEY is not set", file=sys.stderr)
        return 1
    now = datetime.now(timezone.utc)
    category, seed = pick_topic(now)
    existing = recent_titles()
    avoid = "\n".join(f"- {t}" for t in existing[:25]) or "(none yet)"
    prompt = (f"Category: {category}\nTopic idea: {seed}\n"
              f"Pick a fresh, specific angle on this topic. Do NOT repeat or closely resemble these recent titles:\n{avoid}")

    last_error = "unknown"
    for model in MODELS:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                raw = call_groq(model, prompt, key)
                title, desc, tags, body = parse(raw)
                validate(title, desc, tags, body, existing)
            except (ValueError, RuntimeError) as e:
                last_error = f"{model} attempt {attempt}: {e}"
                print(last_error, file=sys.stderr)
                if isinstance(e, RuntimeError):
                    break  # API-level failure: move to next model
                continue
            POSTS_DIR.mkdir(parents=True, exist_ok=True)
            slug = slugify(title)
            path = POSTS_DIR / f"{now:%Y-%m-%d-%H%M}-{slug}.md"
            front = "\n".join([
                "---",
                f"title: {json.dumps(title, ensure_ascii=False)}",
                f"description: {json.dumps(desc, ensure_ascii=False)}",
                f"date: {now.isoformat(timespec='seconds')}",
                f"category: {json.dumps(category)}",
                f"tags: {json.dumps(tags)}",
                "draft: false",
                "ai_assisted: true",
                f"model: {json.dumps(model)}",
                "---",
                "",
            ])
            path.write_text(front + body + "\n", encoding="utf-8")
            print(f"Wrote {path.relative_to(ROOT)} ({len(body.split())} words, {model})")
            return 0
    print(f"All attempts failed. Last error: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
