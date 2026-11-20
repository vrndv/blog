---
title: "AI routing services leak secret data at scale, study shows"
description: "A new experiment that injected millions of hidden canaries into AI prompts exposed systemic leaks across AI routers and hosting providers."
date: 2026-11-20T22:58:44+00:00
category: "Cybersecurity"
tags: ["ai", "supply-chain", "data-leak", "privacy", "detection"]
source_name: "Ars Technica"
source_url: "https://arstechnica.com/security/2026/11/a-leaky-ai-supply-chain-is-exposing-secret-user-data-at-an-alarming-rate/"
image: "https://live.staticflickr.com/4529/38649159932_76ac68322e_b.jpg"
image_alt: "171125-N-ZS023-019"
image_credit: "SurfaceWarriors"
image_credit_url: "https://www.flickr.com/photos/55244200@N05"
image_source_url: "https://www.flickr.com/photos/55244200@N05/38649159932"
image_license: "BY-SA 2.0"
image_license_url: "https://creativecommons.org/licenses/by-sa/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to Ars Technica, a security researcher embedded two million unique “digital canaries” into prompts sent through a sprawling network of AI services. Each canary was a piece of fresh, controllable secret – an AWS access key, an SSH password, a private‑git URL, or a distinct DNS name – that had never been used before. The researcher sent each secret in exactly one prompt to a single AI provider, then watched the internet for any sign that the secret resurfaced.  

The experiment revealed that the AI ecosystem acts like a sieve for sensitive data. When a prompt reaches an “AI router” – a broker that decides which inference engine should handle the request based on price, capability, or latency – the router must decrypt the request to read its contents. After that, the prompt may be passed to a pool of models that run on different hosting providers, or even hop from one router to another. At each hop the plaintext prompt can be logged, cached, or otherwise stored according to the operator’s policies, often indefinitely.  

During the testing window, the researcher observed three separate hosting providers that had been compromised. In one case, an attacker copied every request that arrived at the provider’s front‑end, stealing the embedded AWS keys even when the request was rejected before any model ran. In the other two breaches, the attacker accessed requests marked with a privacy flag (ZDR) and still extracted the secrets. Within hours of the canaries being delivered, the malicious actors tested the stolen keys, probing S3 buckets and secret stores.  

The key finding is that the leakage does not happen deep inside a model; it occurs at the routing and ingestion layers where plaintext prompts are visible to many independent services. Even encryption in transit does not protect the data once it is decrypted for routing decisions.  

## Why it matters  

### 1. AI becomes a new attack surface for credential theft  

AI applications are now embedded in everything from customer‑support chatbots to code‑generation assistants. Developers often rely on third‑party routers to avoid vendor lock‑in and to get the best price per token. Those routers, however, become privileged observers of every user prompt. If a router or any downstream host is breached, the attacker gains a snapshot of raw user data – which can include passwords, API keys, internal URLs, or proprietary code snippets.  

### 2. Supply‑chain risk expands beyond traditional software binaries  

Historically, supply‑chain security focused on code integrity (e.g., compromised build pipelines). This research shows that the data‑flow supply chain – the path a user’s request takes through multiple services – is equally vulnerable. A single compromised router can expose millions of secrets, magnifying the impact of a breach far beyond the typical “one compromised server” scenario.  

### 3. Privacy flags and data‑retention policies provide a false sense of security  

One of the breached providers stored prompts flagged as “ZDR” (zero‑data‑retention). The attacker’s ability to read those prompts demonstrates that once an adversary controls the ingestion point, policy‑level protections are moot. Organizations cannot rely on provider‑side privacy settings alone; they must assume that any service that sees plaintext could be compromised.  

### 4. Real‑world consequences for cloud accounts and infrastructure  

The stolen AWS keys gave the attackers immediate access to cloud resources. Even a single active key can enable data exfiltration, creation of new compute instances, or deployment of ransomware. Because the keys were tied to empty accounts, the breach was detectable, but in a production environment the same technique could harvest keys with full privileges, leading to massive lateral movement.  

## What you can do  

### Harden your AI‑integrated applications  

1. **Avoid sending secrets in prompts** – Treat every prompt as potentially observable. If an application must convey credentials to a downstream system, use a separate, secure channel (e.g., mutual TLS, signed JWTs) rather than embedding them in the AI request.  

2. **Encrypt payloads end‑to‑end** – Some AI routers support client‑side encryption where the model only receives ciphertext. While this limits the router’s ability to route based on content, you can design a “function‑as‑a‑service” pattern where the router forwards encrypted blobs to a trusted backend that performs the decryption and inference.  

3. **Select routers with strict data‑handling policies** – Prefer providers that explicitly state they do not log prompts, or that delete logs within a short, auditable window. Verify these claims through third‑party audits or certifications.  

### Detect and respond to leakage  

1. **Deploy canary secrets** – As demonstrated by the researcher, planting unique, unused credentials in a controlled set of prompts can alert you when a leak occurs. Automate monitoring of cloud logs, Git repositories, and DNS queries for any appearance of those canaries.  

2. **Monitor inbound traffic to AI routers** – If you operate your own router, log request metadata (timestamp, source IP, model selected) but avoid storing full prompt bodies. Use hash‑based deduplication to detect repeated payloads that may indicate exfiltration attempts.  

3. **Implement rapid key rotation** – Treat any key that could have been sent to an AI service as potentially compromised. Rotate IAM credentials, SSH keys, and API tokens on a frequent schedule, and enforce short‑lived credentials where possible.  

### Secure the broader supply chain  

1. **Contractual security clauses** – When signing with AI routers or hosting providers, include clauses that require immediate notification of any breach, detailed logs of data handling, and the right to audit.  

2. **Zero‑trust networking** – Deploy AI routers inside a zero‑trust perimeter where each hop is authenticated and authorized. Use mutual TLS between routers and inference engines, and enforce least‑privilege service accounts for each connection.  

3. **Regular third‑party assessments** – Commission independent penetration tests that specifically target the ingestion path of prompts. Verify that the provider does not retain plaintext beyond the necessary processing window.  

### Sample command: rotating AWS access keys safely  

> **⚠️ Warning:** The following command revokes and creates new keys for an IAM user. Ensure you have alternative credentials before running it.  

```bash
# List current access keys for a user
aws iam list-access-keys --user-name myuser

# Deactivate the old key (replace KEY_ID with the actual ID)
aws iam update-access-key --user-name myuser --access-key-id KEY_ID --status Inactive

# Delete the old key after confirming the new one works
aws iam delete-access-key --user-name myuser --access-key-id KEY_ID
```

Replace `myuser` and `KEY_ID` with your actual IAM user name and key identifier. After rotation, update any applications that relied on the old key, preferably using environment variables or secret‑management tools rather than hard‑coding.  

## Key takeaways  

- AI routers decrypt every prompt to decide where to send it, creating a visibility point for any data contained in the request.  
- The research experiment that injected two million unique secrets uncovered multiple compromised hosting providers that stole those secrets at the routing layer.  
- Privacy flags and data‑retention policies do not protect against an attacker who controls the ingestion point.  
- Developers should treat prompts as public data: never embed passwords, API keys, or other secrets directly in AI requests.  
- Deploy canary secrets, enforce rapid credential rotation, and demand clear data‑handling guarantees from AI service providers.  
- A zero‑trust approach, end‑to‑end encryption, and rigorous monitoring are essential to mitigate the emerging supply‑chain risk introduced by AI routing services.
