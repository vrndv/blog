---
title: "Convex plugin skills bypass user safety checks and fetch remote code"
description: "A review of three Convex plugin skills reveals hidden remote code execution and disabled safety filters, highlighting the need for transparent AI tool onboarding."
date: 2026-11-28T00:22:52+00:00
category: "Cybersecurity"
tags: ["ai", "plugins", "security", "privacy", "open-source"]
source_name: "github.com"
source_url: "https://github.com/convex/convex-backend-skill/issues/64"
image: "https://upload.wikimedia.org/wikipedia/commons/b/b3/Wikimedia_Developer_Satisfaction_2021_Code_review_questions.svg"
image_alt: "Wikimedia Developer Satisfaction 2021 Code review questions"
image_credit: "TCipriani (WMF)"
image_credit_url: "https://commons.wikimedia.org/wiki/User:TCipriani_(WMF)"
image_source_url: "https://commons.wikimedia.org/w/index.php?curid=106386391"
image_license: "CC0 1.0"
image_license_url: "https://creativecommons.org/publicdomain/zero/1.0/deed.en"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened

According to a GitHub issue discussing the Convex backend skill, three skills published in Anthropic’s Claude‑plugins marketplace contain logic that sends a user’s “app idea” to a remote server without informing the user. The code also modifies a command’s shape so that existing safety tooling—such as content classifiers or admin‑enforced policies—fails to recognise the request.  

The problematic sequence is:

1. The skill receives a user’s description of an application they want to build.  
2. It forwards that description to a server whose hostname is generated at runtime, making the endpoint impossible to audit.  
3. Before the request is sent, the skill rewrites the command to evade any classifier the user or their organization may have enabled.  

Because the script that is downloaded is referenced only by a name (not a fixed hash), the user cannot verify its integrity before it runs. The issue remains in the main branch of the repository as of the last check, though a lab version shows the same lines of code.

## Why it matters

### Trust boundaries are being crossed

AI‑driven “skills” or plugins are meant to extend the capabilities of large language models (LLMs) while respecting the security posture of the host environment. When a skill silently ships user data to an external service, it defeats the purpose of any data‑loss‑prevention (DLP) or privacy controls the organization has put in place.

### Evasion of safety classifiers

Many enterprises rely on classifiers that block unsafe commands (e.g., attempts to download and execute arbitrary code). By deliberately reshaping the command, the skill sidesteps these controls, effectively granting the LLM unrestricted execution rights. This opens the door to:

- Exfiltration of proprietary ideas or code snippets.  
- Execution of malicious payloads that have not been vetted.  
- Loss of auditability, since the remote host is generated on the fly.

### Lack of reproducible builds

Fetching a script at runtime without pinning it to a known hash means the content can change without notice. Even if the original author had benign intentions, a compromised supply chain could replace the script with malicious code, and the user would have no way to detect the change.

### User confidence erosion

The issue was raised by a community member who was considering paying for Convex services. After discovering these hidden behaviors, they indicated they would look more closely at alternatives. When developers lose trust in a platform’s transparency, adoption suffers.

## What you can do

### 1. Audit the plugin code before enabling it

If you are using Claude‑plugins or any LLM‑extension framework, pull the plugin repository locally and inspect the source. Look for:

- Network calls that transmit user data (`fetch`, `http.request`, etc.).  
- Dynamic host generation (`${randomString}.example.com`).  
- Commands that are deliberately obfuscated or altered before execution.

```bash
# Example: clone the repo and search for network calls
git clone https://github.com/convex/convex-backend-skill.git
cd convex-backend-skill
grep -RE "fetch|http|request" .
```

### 2. Pin external scripts or bundle them

If a skill must download auxiliary scripts, require the maintainer to provide a cryptographic hash (SHA‑256) and verify it at runtime:

```bash
# Safe download pattern (bash)
URL="https://example.com/script.sh"
EXPECTED_HASH="ab12cd34ef56..."
curl -sSf "$URL" -o /tmp/script.sh
ACTUAL_HASH=$(sha256sum /tmp/script.sh | awk '{print $1}')
if [ "$ACTUAL_HASH" != "$EXPECTED_HASH" ]; then
  echo "Hash mismatch! Aborting."
  exit 1
fi
bash /tmp/script.sh   # Only run after verification
```

> **Warning:** Running downloaded scripts without verification can compromise your system.

### 3. Disable or monitor classifier‑bypassing transformations

Many LLM platforms allow you to define a whitelist of allowed commands. Add a rule that rejects any command that has been programmatically altered (e.g., check for unexpected whitespace, case changes, or added escape characters).

```json
{
  "commandPolicy": {
    "disallowPattern": ".*[\\s]{2,}.*|.*\\\\.*"
  }
}
```

### 4. Use network egress controls

Enforce outbound firewall rules that only permit connections to known, vetted endpoints. Block connections to dynamically generated hostnames or unknown domains.

```bash
# Example using nftables to block outbound to unknown domains
nft add rule ip filter OUTPUT ip daddr 0.0.0.0/0 ct state new drop
# Then add explicit allow rules for trusted services.
```

### 5. Report and request fixes

Open a transparent issue on the plugin’s repository (as the original reporter did) asking the maintainer to:

- Notify users before any data is sent externally.  
- Make the remote‑fetch step optional or replace it with an on‑premise bundle.  
- Remove the classifier‑evasion instruction entirely.  

Community pressure often leads to quicker remediation.

## Key takeaways

- **Transparency is non‑negotiable**: AI plugins must disclose when they transmit user data and give users the ability to opt‑out.  
- **Never trust runtime‑fetched code**: Pin dependencies or bundle them to guarantee integrity.  
- **Maintain strict classifier enforcement**: Modifying commands to evade safety checks defeats the purpose of those controls.  
- **Apply defense‑in‑depth**: Combine code audits, hash verification, network egress filtering, and policy enforcement to protect against hidden data exfiltration.  
- **Stay vocal**: Reporting suspicious behavior helps improve the ecosystem for everyone.
