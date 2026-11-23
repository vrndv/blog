---
title: "CachyOS November Release Adds Recovery Mode and Game Anti‑Cheat Support"
description: "CachyOS’s latest update brings a built‑in recovery environment, Easy Anti‑Cheat v2 compatibility, and a revamped package installer for Arch‑based users."
date: 2026-11-23T15:44:08+00:00
category: "Tech Explained"
tags: ["cachyos", "arch-linux", "linux-distro", "system-recovery", "gaming"]
source_name: "LWN.net"
source_url: "https://lwn.net/Articles/1109269/"
image: "https://live.staticflickr.com/7363/9754578134_0890cb02c5_b.jpg"
image_alt: "『If nothing happens — Check printer 』"
image_credit: "Kyra Ocean Rehn ♡"
image_credit_url: "https://www.flickr.com/photos/49832497@N02"
image_source_url: "https://www.flickr.com/photos/49832497@N02/9754578134"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to LWN.net, the Arch‑based distribution CachyOS has rolled out its November 2026 release. The update introduces several user‑focused features:  

* A new recovery environment called **cachyos-recovery** that lets users roll back a broken system to a previous state.  
* Support for **Easy Anti‑Cheat (EAC) version 2**, enabling games that rely on this anti‑cheat service to run out‑of‑the‑box.  
* **CachyOS Package Installer 2.0.0**, a refreshed installer that unifies the handling of packages from the official repos, the Arch User Repository (AUR), Flatpak, and AppImage formats.  

The release also includes a collection of smaller updates and bug fixes that continue CachyOS’s focus on performance and a streamlined user experience.

## Why it matters  

### Built‑in recovery for rolling releases  

Arch‑derived distributions are known for their rolling‑release model, which delivers the latest software but can also introduce instability when an update breaks a critical component. Historically, users have had to rely on manual snapshots, external tools, or reinstallations to recover from a bad state. By bundling a dedicated recovery environment, CachyOS gives its users a safety net that is tightly integrated with the distro’s package management. This reduces downtime and the risk of data loss, especially for power users who frequently chase the newest kernels and drivers.

### Gaming on Linux becomes smoother  

Easy Anti‑Cheat is a widely used anti‑cheat solution in many popular multiplayer titles. Support for EAC v2 means that games which previously refused to launch on Linux because of missing anti‑cheat libraries can now run without workarounds. This is a notable step for the broader Linux gaming ecosystem, where compatibility layers (like Proton) often have to negotiate with anti‑cheat SDKs. By providing native support, CachyOS lowers the barrier for gamers who want a performant, Arch‑based platform.

### Unified installer streamlines software acquisition  

CachyOS Package Installer 2.0.0 consolidates several previously separate installation pathways. Users no longer need to switch between `pacman`, an AUR helper, Flatpak commands, or manual AppImage handling. A single UI now presents all options, simplifying the decision process and reducing the chance of mixing incompatible package formats. For newcomers to Arch, this can make the distro feel more approachable while still preserving the flexibility that advanced users expect.

### Performance‑first philosophy remains intact  

While the headline features focus on recovery and gaming, the underlying theme of the release continues CachyOS’s emphasis on low‑latency kernels, tuned systemd settings, and aggressive compiler optimizations. These choices keep the distro attractive for users who need every ounce of performance—whether for gaming, media production, or scientific workloads.

## What you can do  

### Enable the recovery environment  

The recovery environment is installed alongside the main system but is not activated by default. To make it available:  

```bash
# Update the bootloader configuration to add the recovery entry
sudo cp /usr/lib/cachyos-recovery/boot-entry.conf /etc/grub.d/40_custom
sudo update-grub   # On systems using GRUB
```

> **Warning:** Modifying bootloader entries can render a system unbootable if done incorrectly. Verify the copied file’s syntax before running `update-grub`.  

After updating, reboot and select the “CachyOS Recovery” entry from the boot menu. The recovery console provides options to:  

* List available snapshots (automatically created after each successful `pacman -Syu`).  
* Roll back to a chosen snapshot.  
* Restore the bootloader configuration if it has been corrupted.  

### Verify Easy Anti‑Cheat support  

If you use Steam or another game launcher, you can test EAC functionality by launching a title that requires it. Should the game fail to start, confirm that the required libraries are present:  

```bash
# List EAC libraries installed by the distro
pacman -Qs easy-anti-cheat
```

If the package is missing, install it manually:  

```bash
sudo pacman -S easy-anti-cheat
```

After installation, restart the game client. Successful launch indicates that the integration is working.

### Try the new package installer  

Launch the installer from your desktop environment’s application menu or via the terminal:  

```bash
cachyos-installer
```

The UI presents four tabs:  

1. **Official repos** – standard `pacman` packages.  
2. **AUR** – community‑maintained build scripts.  
3. **Flatpak** – sandboxed applications.  
4. **AppImage** – portable binaries.  

Select a package, click “Install,” and watch the progress bar. The installer handles dependency resolution across the different sources, automatically choosing the most appropriate format based on your system’s current configuration.

### Keep the system up to date  

Even with a recovery environment, it’s best practice to apply updates regularly. Use the standard Arch command:  

```bash
sudo pacman -Syu
```

Consider enabling automatic snapshots after each successful upgrade by adding a systemd timer:  

```ini
# /etc/systemd/system/cachyos-snapshot.timer
[Unit]
Description=Create a system snapshot after upgrades

[Timer]
OnBootSec=5min
OnUnitActiveSec=1d
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl enable --now cachyos-snapshot.timer
```

This creates daily snapshots that the recovery environment can roll back to if needed.

## Key takeaways  

* **Recovery built in:** CachyOS now ships a dedicated recovery mode, giving rolling‑release users a straightforward way to revert problematic updates.  
* **Gaming friendliness:** Native Easy Anti‑Cheat v2 support removes a common obstacle for Linux gamers, expanding the catalog of playable titles.  
* **Unified installer:** Version 2.0.0 of the CachyOS Package Installer merges multiple package ecosystems under a single, user‑friendly interface.  
* **Performance focus persists:** The release continues to prioritize low‑latency kernels and tuned system defaults, making it suitable for high‑performance workloads.  
* **Practical steps:** Enable the recovery entry in your bootloader, verify EAC libraries for gaming, adopt the new installer for software management, and set up automatic snapshots to safeguard future upgrades.  

By integrating recovery tools and gaming compatibility while preserving its performance‑first ethos, CachyOS’s November release offers a compelling blend of safety and speed for Arch enthusiasts.
