---
title: "Crowdsourcing LLM Detection for Community Articles"
description: "Exploring a proposal to share cheap, centralized LLM detection scans of community submissions and what it means for content quality."
date: 2026-11-08T19:02:54+00:00
category: "Tech Explained"
tags: ["llm", "detection", "community", "open-source", "moderation"]
source_name: "Lobsters"
source_url: "https://lobste.rs/s/jbdtim/who_wants_crowdsource_llm_scans_articles"
image: "https://live.staticflickr.com/2874/9720896079_cf2593368e_b.jpg"
image_alt: "Caledos Runner - New share buttons leaked... ;-) - WP_20130904_20_10_57_Pro"
image_credit: "Nicola since 1972"
image_credit_url: "https://www.flickr.com/photos/15216811@N06"
image_source_url: "https://www.flickr.com/photos/15216811@N06/9720896079"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

A community member who values human‑generated content on a discussion site has built a small prototype that publishes the results of an LLM detection service called **Pangram**. The idea is to let multiple contributors run scans with their own API keys and feed the findings into a shared index. By centralising the scans, the proposal aims to avoid each participant having to pay for their own expensive API calls while still benefitting from what the author perceives as a reasonably reliable detector.  

The author notes that false‑positive detections are rare, especially when the detector flags only content that appears to have been “tweaked” by an LLM rather than fully generated. They also acknowledge that the detector can sometimes mislabel genuine, hand‑written text, but argue that such cases are few compared to the total volume of scans performed.  

The discussion also touches on broader concerns: the stigma attached to using LLMs for drafting or translating, the desire for transparent statistics about how detection rates change over time, and the need for a “false‑positive” override mechanism so authors can contest erroneous flags.  

## Why it matters  

### Quality control without heavy moderation  

Community‑driven sites rely on a mix of human judgment and automated tools to keep discussions high‑quality. An inexpensive, shared detection index could give moderators a quick signal about potentially AI‑generated text, helping them focus their attention where it matters most.  

### Cost efficiency  

LLM detection APIs are typically priced per request. If dozens of contributors each submit hundreds of articles, the cumulative cost can become prohibitive. A pooled approach spreads the expense across many users, making the service accessible to smaller sites or hobbyist moderators.  

### Trust and transparency  

Any automated classifier carries a risk of false positives, which can frustrate legitimate writers. By publishing scan results openly, the community can audit the detector’s behavior, spot patterns of misclassification, and develop best‑practice guidelines (e.g., when to use a “override” button).  

### Ethical considerations  

The proposal raises questions about how much we should rely on machines to judge authenticity. Over‑reliance can pressure authors to “write like a human” rather than simply produce good content. Balancing detection with respect for author intent is crucial to avoid a chilling effect on legitimate use of language models for assistance or translation.  

## What you can do  

### 1. Test a detector locally before contributing  

If you want to help populate a shared index, start by running a few scans on your own machine. Below is a safe Bash snippet that calls a generic detection endpoint (replace `YOUR_API_KEY` and `ENDPOINT_URL` with the values you receive from the service).  

```bash
#!/usr/bin/env bash
# WARNING: This script makes network requests and may incur charges.
# Use only with a valid API key and be mindful of request limits.

API_KEY="YOUR_API_KEY"
ENDPOINT_URL="https://api.pangram.ai/detect"
TEXT_FILE="article.txt"

if [[ ! -f "$TEXT_FILE" ]]; then
  echo "Error: $TEXT_FILE not found."
  exit 1
fi

curl -s -X POST "$ENDPOINT_URL" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: text/plain" \
  --data-binary @"$TEXT_FILE" | jq .
```

Run the script, examine the JSON output, and decide whether the result seems reasonable.  

### 2. Contribute results responsibly  

When you upload a scan to a shared index, include:  

* A reference to the article (URL or identifier).  
* The raw detector score or label.  
* A short note if you suspect a false positive.  

This metadata lets others verify the entry and provides context for future analysis.  

### 3. Advocate for an override workflow  

If you are a site moderator or developer, consider adding a simple “Appeal” button to any AI‑flagged post. The button could:  

* Record the author’s claim that the text is human‑written.  
* Store the original detector output for later review.  
* Optionally trigger a secondary, independent scan for confirmation.  

Such a workflow reduces friction for legitimate writers while preserving the benefits of automated signals.  

### 4. Monitor trends without shaming  

Aggregated statistics (e.g., proportion of flagged posts per month) can be useful for research, but they should never be used to publicly shame contributors. Publish trend graphs in a neutral “Community Insights” section, and pair them with explanations about model releases or policy changes that might affect detection rates.  

### 5. Keep the human element front and centre  

Encourage authors to view LLM tools as assistants, not replacements. Remind writers that a well‑crafted article is judged on clarity, insight, and originality—qualities that detectors cannot fully capture.  

## Key takeaways  

* A prototype exists to share inexpensive LLM detection scans across a community, using the Pangram service as a reference point.  
* Centralising scans can lower costs and provide a transparent signal for moderators, but false positives—though rare—must be handled gracefully.  
* Contributors should test detectors locally, publish results with clear metadata, and support an appeal mechanism for disputed flags.  
* Trend data should be used for internal insight, not for public shaming, to maintain a healthy, human‑focused environment.  
* Ultimately, the goal is to keep “slop” out of discussions while respecting authors who responsibly use language models for assistance.
