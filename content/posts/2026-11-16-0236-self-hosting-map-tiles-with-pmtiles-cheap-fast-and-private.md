---
title: "Self‑hosting map tiles with PMTiles: cheap, fast, and private"
description: "Learn how PMTiles and Protomaps let you serve world‑scale map tiles from a single file on a CDN, saving money and keeping data under your control."
date: 2026-11-16T02:36:38+00:00
category: "Tech Explained"
tags: ["maps", "cdn", "open\u2011source", "self\u2011hosting", "cost\u2011saving"]
source_name: "bruceroettgers.eu"
source_url: "https://bruceroettgers.eu/blog/protomaps/"
image: "https://live.staticflickr.com/5285/5269761547_a1e20a1588.jpg"
image_alt: "Is there anything more Real World Zelda than downloading map tiles as you ride the subway?"
image_credit: "dpstyles™"
image_credit_url: "https://www.flickr.com/photos/77725780@N00"
image_source_url: "https://www.flickr.com/photos/77725780@N00/5269761547"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to bruceroettgers.eu, the Protomaps project introduced **PMTiles**, a single‑file tile archive that can be served via standard HTTP Range requests. Because the file can be placed in any storage bucket that supports Range requests, a map can be delivered without a dedicated tile server or a complex database backend.  

The author experimented with a popular CDN (Bunny.net) that honors Range requests, uploading the 139 GB world‑map file and configuring a pull zone to serve it. By tweaking CDN settings—enabling “Optimize for large object delivery,” restricting CORS origins, and throttling large single‑request downloads—the setup became both cost‑effective and resistant to abuse.  

## Why it matters  

### 1. Cost reduction compared with commercial APIs  
Commercial map APIs charge per 1 000 map loads once free tiers are exceeded. A single PMTiles file, once cached at the edge, costs only a few cents per gigabyte of bandwidth and a modest monthly storage fee. In practice, serving a continent‑scale map can be **over 100 × cheaper** than typical commercial pricing.  

### 2. Simplicity of deployment  
Traditional tile servers require a database (e.g., PostGIS), a rendering engine, and a web server that translates `/z/x/y.pbf` URLs into vector tiles. With PMTiles, the entire dataset lives in one file; the CDN handles the Range request logic, eliminating the need for custom backend code.  

### 3. Portability and privacy  
Because the tile archive is a static file, you can move it between cloud providers, host it on a private object store, or even serve it from an on‑premises NAS. No third‑party API logs your users’ location queries, and you control who can embed the tiles via CORS settings.  

### 4. Performance at scale  
CDN edge nodes cache the requested byte ranges, so subsequent users in the same region receive the data from the nearest PoP, reducing latency dramatically. Even large‑scale “viral” usage only adds marginal bandwidth costs because most of the map is already cached locally.  

## What you can do  

### 1. Obtain a PMTiles archive  

1. Visit the Protomaps build page.  
2. Download the latest world‑map PMTiles file (or generate a custom extract with the CLI for a specific region/zoom range).  

```bash
# Example: extract Europe at zoom levels 5‑10
pmtiles extract --bbox=-10,35,30,70 --min-zoom=5 --max-zoom=10 world.pmtiles europe.pmtiles
```

> **Safety note:** The CLI only reads the source file and writes a new one; it does not modify your system.  

### 2. Choose a storage backend  

- **Object store with S3 compatibility** (e.g., Bunny.net storage zone, AWS S3, Wasabi).  
- Enable S3‑compatible API; this avoids HTTP upload timeouts that can happen with plain PUT requests.  

### 3. Upload the file  

```bash
# Using rclone (install from your distro’s repo)
rclone copy ./europe.pmtiles bunny:my-storage-zone
```

Run the upload inside a `tmux` session or on a temporary VPS if your home connection is unreliable.  

### 4. Configure the CDN  

1. **Create a pull zone** and set the storage zone as the origin.  
2. Under **Security → General**, whitelist only the domains that should embed the tiles (set Allowed Referrers).  
3. In **Caching**, enable “Optimize for large object delivery” so the CDN will honor Range requests.  
4. (Optional) Under **Network limits**, set a download‑speed cap after a certain amount of data (e.g., 10 kB/s after 10 MB) to discourage full‑file downloads that could inflate your bill.  

### 5. Test the deployment  

Open a browser console and request a tile using a Range header:

```bash
curl -I -H "Range: bytes=0-1023" https://my-cdn.example.com/world.pmtiles
```

You should see a `206 Partial Content` response, confirming that the CDN is correctly handling Range requests.  

### 6. Integrate with your map library  

Most modern web‑mapping libraries (MapLibre GL, Leaflet with vector‑tile plugins) accept a custom tile URL template. Point it to your CDN endpoint:

```javascript
const map = new maplibregl.Map({
  container: 'map',
  style: 'https://my-cdn.example.com/world.pmtiles',
  // For vector tiles, you may need to specify the format and tile size
});
```

### 7. Monitor usage  

- Enable CDN analytics to track bandwidth per region.  
- Set alerts for unusually high data transfer, which could indicate misuse.  

## Key takeaways  

- **PMTiles** turns an entire world‑scale map into a single, portable file that can be served via HTTP Range requests.  
- Deploying on a CDN that supports Range requests (e.g., Bunny.net) costs only a few dollars per month for storage and negligible bandwidth for typical usage.  
- The approach eliminates the need for a dynamic tile server, reduces operational complexity, and gives you full control over privacy and cost.  
- Proper CDN configuration—CORS restrictions, large‑object optimization, and download throttling—helps prevent accidental over‑billing.  
- With a few command‑line steps and basic CDN settings, anyone can replace expensive commercial map APIs with a self‑hosted, open‑source solution.
