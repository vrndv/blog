---
title: "Collabora Online Cuts Document Memory Footprint by Half"
description: "A new copy‑on‑write optimization lets Collabora Online use roughly 50 % less RAM per document, easing server load for self‑hosted deployments."
date: 2026-11-24T15:35:58+00:00
category: "Tech Explained"
tags: ["collabora", "libreoffice", "memory", "optimization", "self\u2011hosting"]
source_name: "Phoronix"
source_url: "https://www.phoronix.com/news/Collabora-Online-Half-Memory"
image: "https://live.staticflickr.com/65535/53714869271_c297f26c7b_b.jpg"
image_alt: "Mysterious server rack behind an automatic door, restaurant, Tartu, Estonia"
image_credit: "gruntzooki"
image_credit_url: "https://www.flickr.com/photos/37996580417@N01"
image_source_url: "https://www.flickr.com/photos/37996580417@N01/53714869271"
image_license: "BY-SA 2.0"
image_license_url: "https://creativecommons.org/licenses/by-sa/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to Phoronix, the Collabora Online suite – an open‑source, web‑based office suite built on LibreOffice – now consumes about half the memory it previously required for each open document. The improvement stems from a change in how the software handles copy‑on‑write (CoW) memory pages, allowing the server to share more data between document instances instead of duplicating it.  

## Why it matters  

### Server cost and scalability  
Collabora Online is often deployed on shared‑hosting or on‑premises servers that run multiple user sessions simultaneously. Memory is a primary constraint: each additional document adds to the RAM demand, and exceeding physical memory forces swapping, which dramatically degrades responsiveness. Halving the per‑document memory usage means a single server can host twice as many concurrent users before hitting the same memory ceiling, or it can be downsized to a smaller, cheaper instance while keeping capacity unchanged.  

### Energy and environmental impact  
Lower RAM consumption reduces overall power draw. In data‑center environments, even modest savings per node add up across thousands of machines, contributing to lower operational costs and a smaller carbon footprint.  

### User experience  
When memory pressure is reduced, document loading, editing, and real‑time collaboration become smoother. Users are less likely to encounter lag or temporary “out‑of‑memory” errors, which can interrupt workflow and cause data loss if autosave fails.  

### Open‑source momentum  
Collabora Online’s improvement showcases how community‑driven projects can evolve performance characteristics without sacrificing compatibility. The change does not require a new major version of LibreOffice; it is an internal optimization that can be back‑ported to existing deployments, reinforcing confidence in the sustainability of open‑source office solutions.  

## What you can do  

### 1. Verify your current memory usage  
Before upgrading, capture a baseline of how much RAM each document consumes. On a Linux host you can use `ps` or `smem` to inspect the Collabora Online process.  

```bash
# Install smem if not present (Debian/Ubuntu example)
sudo apt-get install smem

# Show memory usage per Collabora Online worker
smem -r -k | grep collabora
```  

> **Warning**: The commands above are read‑only; they do not modify the system.  

### 2. Update to the latest Collabora Online package  

Most Linux distributions that package Collabora Online provide a regular update channel. Pull the newest version from your package manager:  

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install collabora-online

# Fedora
sudo dnf upgrade collabora-online
```  

If you run Collabora Online from Docker, pull the latest image:  

```bash
docker pull collabora/code:latest
docker stop collabora
docker rm collabora
docker run -d --name collabora \
    -e "domain=yourdomain.com" \
    -p 9980:9980 \
    collabora/code:latest
```  

> **Warning**: Stopping the container will terminate any active editing sessions. Notify users before performing the restart.  

### 3. Tune your server for the new memory profile  

With the reduced per‑document RAM demand you can safely increase the number of worker processes. Collabora Online’s `COOLWSD` daemon uses the `max\_processes` setting in its configuration file (`/etc/coolwsd/coolwsd.xml`). Raise the value to match your expected concurrent user count, keeping an eye on overall system memory.  

```xml
<!-- Example snippet from coolwsd.xml -->
<max_processes>30</max_processes>
```  

After editing, restart the service:  

```bash
sudo systemctl restart coolwsd
```  

### 4. Monitor after the change  

Use standard monitoring tools (e.g., `htop`, `glances`, or Prometheus node exporter) to confirm that RAM usage aligns with expectations. Look for a roughly 50 % reduction in the RSS (resident set size) of each worker compared to your baseline.  

### 5. Consider scaling down hardware  

If your server was previously memory‑constrained, you may be able to move to a smaller instance type (e.g., from 8 GB to 4 GB RAM) without sacrificing capacity. Test the new size in a staging environment first to ensure latency remains acceptable.  

## Key takeaways  

- **Copy‑on‑write optimization** cuts Collabora Online’s memory per document by about half.  
- **Cost savings**: servers can host more users or be downsized, lowering hardware and energy expenses.  
- **Performance boost**: reduced swapping leads to smoother real‑time collaboration.  
- **Action steps**: measure current usage, update the package or Docker image, adjust worker limits, and monitor the impact.  

By applying these straightforward updates, administrators can immediately reap the benefits of the new memory handling, making Collabora Online a more efficient choice for self‑hosted office suites.
