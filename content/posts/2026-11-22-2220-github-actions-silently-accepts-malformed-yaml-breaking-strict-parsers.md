---
title: "GitHub Actions silently accepts malformed YAML, breaking strict parsers"
description: "GitHub Actions tolerates certain invalid YAML structures, causing compatibility issues for tools that enforce the YAML spec."
date: 2026-11-22T22:20:19+00:00
category: "Cybersecurity"
tags: ["github", "yaml", "ci/cd", "parsing", "devops"]
source_name: "Lobsters"
source_url: "https://yossarian.net/til/post/github-actions-accepts-invalid-yaml/"
image: "https://upload.wikimedia.org/wikipedia/commons/f/fb/Map_-_NL_-_Municipality_code_1586_%282009%29.svg"
image_alt: "Map - NL - Municipality code 1586 (2009)"
image_credit: "Michiel1972 (talk) 23:58, 24 January 2009 (UTC)"
image_credit_url: "https://commons.wikimedia.org/wiki/User:Michiel1972"
image_source_url: "https://commons.wikimedia.org/w/index.php?curid=5784644"
image_license: "BY-SA 3.0"
image_license_url: "https://creativecommons.org/licenses/by-sa/3.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to a post on Lobsters, GitHub Actions’ workflow engine accepts YAML that does not conform to the official YAML specification. A real‑world workflow step uses a multi‑line flow‑style string for a `json:` key, but the indentation of that flow node is insufficient according to the spec. The YAML spec requires any flow‑style node nested inside a block collection (a map or list) to be indented at least one space farther than its parent.  

The offending snippet parses fine in GitHub Actions, yet a strict parser—such as the one used by the open‑source scanner *zizmor*—rejects it. The discrepancy stems from the parser GitHub Actions relies on: YamlDotNet version 5.3.0, a .NET library that has not been updated to enforce this rule. Even newer releases of YamlDotNet still contain the same bug, because a 2020 patch only addressed double‑quoted strings, leaving single‑quoted and plain flow styles unchecked.  

In short, GitHub Actions is more permissive than the YAML spec, making it impossible for some tools that enforce strict conformance to read certain workflow files without modification.

## Why it matters  

### CI/CD reliability  

Continuous‑integration pipelines are only as reliable as the configuration they execute. When a platform silently accepts malformed YAML, developers may write workflows that work on GitHub but break when the same files are linted, version‑controlled, or migrated to other CI systems. This hidden incompatibility can surface during audits, migrations, or when using security‑focused scanners that expect spec‑compliant YAML.

### Security tooling  

Many security tools parse workflow files to detect secrets, insecure permissions, or risky actions. If those tools reject a workflow because of a spec violation that GitHub itself ignores, the workflow may be falsely flagged as insecure or, conversely, the tool may skip analysis altogether. Both outcomes reduce the effectiveness of automated security checks.

### Ecosystem fragmentation  

Open‑source projects that aim to provide universal linting or static analysis for GitHub Actions must either implement work‑arounds for GitHub’s lax parsing or risk false positives. This adds maintenance overhead and can discourage contributions, slowing down the overall improvement of CI security hygiene.

## What you can do  

### 1. Validate locally with a strict parser  

Before committing workflow files, run a YAML validator that adheres to the spec. The `yamllint` tool is a popular choice:

```bash
# Install yamllint (requires Python)
pip install yamllint

# Validate a workflow file
yamllint -d "{extends: relaxed, rules: {indentation: {spaces: 2}}}" .github/workflows/ci.yml
```

If `yamllint` reports an error, adjust the indentation or switch to a block‑style scalar (e.g., `|` or `>` for multi‑line strings) instead of a flow‑style string.

### 2. Prefer block‑style scalars for complex values  

When embedding JSON or other large strings, use block scalars:

```yaml
- name: Set payload
  env:
    json: |
      {
        "key": "value",
        "list": [1, 2, 3]
      }
```

Block scalars avoid the indentation rules that trip up flow‑style nodes and are clearly supported by both GitHub Actions and strict parsers.

### 3. Add a CI lint step  

Integrate a linting job into your own workflow to catch spec violations early:

```yaml
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install yamllint
        run: pip install yamllint
      - name: Lint workflows
        run: yamllint .github/workflows/*.yml
```

This step will fail the run if any workflow file contains invalid YAML, preventing the problem from reaching production.

### 4. Report the inconsistency  

While the underlying parser is proprietary, you can still file a GitHub issue describing the observed behavior and linking to the offending workflow snippet. Providing a minimal reproducible example helps the GitHub team understand the impact and may motivate a move toward stricter parsing.

### 5. Keep an eye on parser updates  

If you depend on YamlDotNet in your own tooling, monitor its repository for fixes related to rule 8.2.3 (flow‑style indentation). Upgrading to a version that addresses both double‑quoted and single‑quoted flow nodes will reduce false rejections.

## Key takeaways  

- GitHub Actions uses a YAML parser that tolerates certain indentation errors, allowing malformed flow‑style strings to pass.  
- Strict YAML validators reject these files, causing compatibility and security‑analysis problems.  
- Use block‑style scalars for multi‑line content, lint locally with tools like `yamllint`, and add a lint step to your own CI pipeline.  
- Reporting the issue to GitHub and staying updated on YamlDotNet patches can help drive the ecosystem toward proper spec compliance.
