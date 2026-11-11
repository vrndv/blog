---
title: "eMudhra’s TLS Certificate Phase‑Out and Independent Review Explained"
description: "A clear overview of eMudhra’s withdrawal of emSign TLS certificates, browser trust changes, and steps administrators can take to stay secure."
date: 2026-11-11T23:21:07+00:00
category: "Cybersecurity"
tags: ["tls", "certificates", "browser\u2011trust", "compliance", "migration"]
source_name: "Lobsters"
source_url: "https://emudhra.com/en/post/certificate-security-incident"
image: "https://live.staticflickr.com/21/31436962_6b49d24fb9_b.jpg"
image_alt: "Server room shelves"
image_credit: "sylvar"
image_credit_url: "https://www.flickr.com/photos/44124401501@N01"
image_source_url: "https://www.flickr.com/photos/44124401501@N01/31436962"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to a statement from eMudhra, the company is completing the wind‑down of its **emSign TLS certificates**. The move follows a prior decision to stop issuing certificates under the **emSign G1 hierarchy** and is now focused on the **G3 hierarchies** that were still in use, primarily by customers in the United States.  

Browser root programs have published concrete dates for when they will stop trusting certificates that chain to the emSign G1 hierarchy. For Chrome and Mozilla, the “SCTNotAfter” field indicates that **after those dates** any certificate that chains to the G1 root will be rejected by the browsers, though certificates issued **before** the cut‑off remain technically valid for other uses. Apple’s policy is stricter: **all** certificates that ever chained to the G1 hierarchy will be untrusted on its platforms, regardless of issuance date.  

In response, eMudhra has already migrated the majority of its TLS customers to **alternative certificate authorities** across most regions. The only remaining segment is a U.S. client ecosystem that holds roughly **30,800 certificates** under the affected G3 hierarchies. Those customers have been given a temporary issuance path through eMudhra’s **G1 RSA root** to keep services running while they transition to other providers. eMudhra has asked the browser and root‑store programs for additional time to complete this migration without service disruption.  

To bring transparency to the incident that caused the distrust of several intermediate CAs earlier this month, eMudhra appointed **KPMG** as an independent external reviewer. The review is intended to clarify the root cause, assess any governance gaps, and confirm that the company’s remediation steps meet industry standards.  

Other business lines—global digital signature certificates (DSC), eSignature, and enterprise solutions—are **unaffected** and continue operating normally.  

## Why it matters  

### Trust is the foundation of TLS  

TLS (Transport Layer Security) relies on a chain of trust that starts at a **root certificate** trusted by browsers and operating systems. When a root or intermediate certificate is removed from a browser’s trust store, any website or service that presents a chain ending at that root becomes **untrusted**. Users will see warnings, and automated systems (e.g., API clients, CI pipelines) may reject the connection outright.  

### Browser policies differ  

Chrome and Mozilla’s approach—rejecting only post‑date certificates—means legacy certificates may still function in limited contexts (e.g., internal tools that don’t validate SCTs). Apple’s blanket revocation, however, can break connections on macOS, iOS, and Safari instantly. Organizations that serve mixed client bases must consider the most restrictive policy to avoid unexpected outages.  

### Business continuity risk  

The U.S. ecosystem holding tens of thousands of certificates represents a sizable attack surface. If any of those certificates expire or become untrusted during the transition, services such as payment gateways, internal portals, or API endpoints could become inaccessible, potentially violating SLAs or regulatory requirements.  

### Independent review builds confidence  

By engaging KPMG, eMudhra signals a commitment to **governance, risk management, and compliance**. An external audit can uncover procedural weaknesses—like insufficient key‑management controls or inadequate monitoring—that might have contributed to the earlier distrust event. For customers, the review’s findings will be a key factor in deciding whether to continue using eMudhra‑issued certificates or move entirely to other CAs.  

## What you can do  

### 1. Inventory every TLS certificate  

- List all certificates in use, noting **issuer**, **expiry**, and **chain** (root → intermediate → leaf).  
- Include certificates used by web servers, load balancers, email gateways, VPNs, and internal services.  

```bash
# Example: find leaf certificates in /etc/ssl and print issuer and expiry
find /etc/ssl -type f -name "*.crt" -exec openssl x509 -noout -issuer -enddate -in {} \;
```  

> **Warning**: The command only reads certificates; it does not modify anything.  

### 2. Verify browser trust status  

- Use online tools (e.g., SSL Labs) or local OpenSSL checks to confirm that each certificate chains to a root still trusted by Chrome, Firefox, and Safari.  
- For Apple‑only environments, treat any certificate that ever chained to the emSign G1 root as **untrusted**.  

```bash
# Check the chain for a given certificate
openssl verify -CAfile /path/to/truststore.pem /path/to/leaf.crt
```  

### 3. Prioritize migration for at‑risk certificates  

- **Immediate**: Any certificate that chains to the emSign G1 root and serves external clients (public‑facing websites, APIs).  
- **Short‑term**: Internal services that rely on strict browser validation (e.g., corporate portals accessed via Safari).  
- **Long‑term**: Legacy systems that can tolerate a temporary trust gap but should still be re‑issued before the next renewal cycle.  

### 4. Choose a replacement CA  

- Look for CAs that support **automatic renewal** via ACME or similar protocols to reduce operational overhead.  
- Verify that the CA’s root certificates are already present in all major browsers and OS trust stores.  
- If you need a **free** option for non‑production workloads, consider Let’s Encrypt, but be aware of rate limits and certificate lifetimes.  

### 5. Automate re‑issuance where possible  

- For web servers managed by configuration management tools (Ansible, Chef, Puppet), integrate certificate renewal tasks.  
- Example using Certbot for an Nginx server:  

```bash
# Install Certbot (Debian/Ubuntu)
sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx

# Obtain/renew a certificate
sudo certbot --nginx -d example.com -d www.example.com
```  

> **Caution**: Test the renewal in a staging environment before applying to production.  

### 6. Update monitoring and alerting  

- Add checks that validate the **expiry** and **trust status** of each certificate daily.  
- Alert on any certificate that is within 30 days of expiry or that fails a trust‑chain verification.  

```yaml
# Example Prometheus rule
- alert: TLSCertificateExpiringSoon
  expr: (tls_cert_not_after - time()) < 2592000
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "TLS certificate for {{ $labels.instance }} expires in < 30 days"
```  

### 7. Communicate with stakeholders  

- Inform internal teams (dev, ops, security) about the migration timeline and any expected downtime.  
- If you serve external customers, publish a short notice explaining the upcoming certificate change and any steps they need to take (e.g., updating pinned certificates).  

### 8. Review the KPMG findings  

- Once KPMG releases its report, compare its recommendations against your own processes.  
- Implement any suggested improvements—especially around **key‑generation**, **certificate lifecycle management**, and **audit logging**.  

## Key takeaways  

- **Browser trust is changing**: Chrome/Firefox will stop trusting emSign G1 certificates after a set date; Apple already distrusts all of them.  
- **eMudhra is actively migrating** most customers, but a large U.S. client base still relies on a temporary G1 path.  
- **Independent review** by KPMG aims to clarify the root cause of the earlier distrust incident and bolster governance.  
- **Immediate actions** for administrators include inventorying certificates, verifying trust chains, prioritizing migration, automating re‑issuance, and tightening monitoring.  
- **Future‑proofing**: Adopt automated renewal workflows, keep trust stores up‑to‑date, and regularly audit certificate management practices to avoid similar disruptions.
