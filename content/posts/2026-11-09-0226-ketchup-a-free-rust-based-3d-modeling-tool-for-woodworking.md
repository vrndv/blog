---
title: "KetchUp – A Free Rust‑Based 3D Modeling Tool for Woodworking"
description: "An open‑source, browser‑first 3D app lets woodworkers design furniture with exact dimensions, no accounts, and full local control."
date: 2026-11-09T02:26:41+00:00
category: "Tech Explained"
tags: ["rust", "3d-modeling", "woodworking", "open-source", "webgpu"]
source_name: "ketchup3d.github.io"
source_url: "https://ketchup3d.github.io/app/"
image: "https://live.staticflickr.com/2049/5726065025_a5c562164f_b.jpg"
image_alt: "CreativeTools.se - ZPrinter-made plastic injection mold 13"
image_credit: "Creative Tools"
image_credit_url: "https://www.flickr.com/photos/33907867@N02"
image_source_url: "https://www.flickr.com/photos/33907867@N02/5726065025"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to the KetchUp project page, a new free 3D modeling application called **KetchUp** has been released. It targets woodworkers, furniture makers, and DIY builders who need to visualize projects before cutting material. The app runs in a desktop‑class web browser or as a native binary on Windows, macOS, and Linux. It is built with the Rust programming language and leverages WebGPU (or WebGL2 as a fallback) for hardware‑accelerated rendering.  

Key features listed by the developers include:  

* Simple primitive creation – lines, rectangles, circles, and freehand outlines.  
* Classic “push/pull” extrusion to turn 2‑D faces into 3‑D solids.  
* Precise input – users can type exact lengths, snap to geometry or axes, and add dimension annotations.  
* Organizational tools – groups, reusable components, and tags keep larger assemblies manageable.  
* Local autosave and the ability to download a portable “.ketchup” project file.  
* Import of SketchUp (.skp) files and export of Wavefront OBJ (.obj) files for downstream workflows.  

The interface is deliberately minimal: a toolbar with the most‑used tools stays close to the canvas, and the mouse‑and‑keyboard workflow mirrors traditional desktop CAD programs. No cloud account is required; everything stays on the user’s device unless they explicitly export a file.

## Why it matters  

### Open‑source alternatives to commercial CAD  

Most mainstream 3D modeling tools for furniture design are either expensive (e.g., SketchUp Pro) or locked behind subscription services. KetchUp’s MIT‑licensed codebase gives hobbyists and small workshops a cost‑free entry point while preserving the freedom to audit, modify, or extend the software. The Rust foundation also brings memory safety guarantees that are rare in graphics‑heavy applications, potentially reducing crash‑related data loss.

### Browser‑first deployment lowers the barrier to entry  

Because the primary interface runs in any modern browser that supports hardware acceleration, users can start designing on a machine without installing anything. This is especially helpful in shared workshop environments where installing software may be restricted. The same codebase also powers native desktop builds, so users who prefer a dedicated window can download a compiled binary for their OS.

### Local‑only workflow improves privacy and reliability  

All modeling data is stored locally and autosaved in the browser’s storage. There is no mandatory cloud sync, which eliminates concerns about accidental exposure of design files or reliance on internet connectivity. Users who need to keep a record simply download the “.ketchup” file; clearing browser data will erase the autosave, so the explicit export step encourages good data‑management habits.

### Interoperability with existing pipelines  

Importing SketchUp files means that designers can migrate legacy models into KetchUp without starting from scratch. Exporting to OBJ provides a universal geometry format that can be fed into rendering engines, slicers for 3‑D printing, or other CAD packages. While textures and advanced SketchUp features are not preserved, the core geometry remains usable.

## What you can do  

### Try the web version  

1. Open a recent version of Chrome, Edge, or Firefox.  
2. Navigate to the KetchUp site (the URL is on the project’s homepage).  
3. Allow the browser to use hardware acceleration when prompted.  

> **Safety note:** The app runs entirely in your browser; no external binaries are executed.

### Install the native desktop app (optional)  

If you prefer a stand‑alone program:  

```bash
# Example for Linux (Debian/Ubuntu)
sudo apt-get install wget unzip
wget https://github.com/ketchup3d/ketchup/releases/latest/download/ketchup-linux.zip
unzip ketchup-linux.zip -d $HOME/ketchup
chmod +x $HOME/ketchup/ketchup
$HOME/ketchup/ketchup &
```

> **Warning:** Verify the download URL and checksum from the official GitHub releases page before running.  

### Adopt a disciplined saving habit  

* **Autosave** works while the tab remains open, but clearing browser data removes it.  
* After each major design iteration, use **File → Save** to download a `.ketchup` file.  
* Store those files in a version‑controlled folder (e.g., a Git repo or a cloud backup you trust).  

### Leverage groups and components  

When modeling a cabinet, create a “Drawer” component once and reuse it across the assembly. This reduces file size and makes later edits (e.g., changing the drawer height) propagate automatically.

### Export for downstream processing  

If you need to render a photorealistic image or generate CNC toolpaths:  

```bash
# Export OBJ from the menu, then import into Blender, FreeCAD, or your CAM software.
```

Remember that OBJ does not carry material information, so you’ll need to reassign textures in the target application.

### Contribute or audit the code  

Because the project is MIT‑licensed and hosted on GitHub, you can:  

* Review the Rust source for security or performance concerns.  
* Submit bug reports or feature requests via the issue tracker.  
* Fork the repo and experiment with custom plugins (e.g., a built‑in bill‑of‑materials generator).  

## Key takeaways  

* **KetchUp** provides a free, Rust‑based 3‑D modeling environment focused on woodworking and furniture design.  
* It runs in any modern desktop browser with WebGPU/WebGL2 support and also offers native binaries for the three major OS families.  
* All data stays local; users must manually export projects, which enhances privacy and forces good backup practices.  
* Importing SketchUp files and exporting OBJ keeps the tool compatible with existing design pipelines.  
* The open‑source nature invites community contributions, and the Rust foundation promises a stable, memory‑safe codebase.  

Whether you’re a hobbyist building a simple shelf or a small workshop planning a complex cabinet system, KetchUp offers a low‑cost, privacy‑respecting way to prototype in 3‑D before the first cut. Give it a spin in your browser, and consider adding the native app to your workstation for a smoother workflow.
