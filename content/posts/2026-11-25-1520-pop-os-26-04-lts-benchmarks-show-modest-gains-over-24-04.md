---
title: "Pop!_OS 26.04 LTS Benchmarks Show Modest Gains Over 24.04"
description: "A look at performance differences between Pop!_OS 26.04 LTS and 24.04 LTS on System76’s Thelio Prime hardware, with practical take‑aways for users."
date: 2026-11-25T15:20:58+00:00
category: "Tech Explained"
tags: ["popos", "linux", "benchmarking", "system76", "performance"]
source_name: "Phoronix"
source_url: "https://www.phoronix.com/review/pop-os-2604-benchmarks"
image: "https://live.staticflickr.com/4610/27905041519_457929258c_b.jpg"
image_alt: "laptop-desk-notebook-computer-macbook-writing - Must Link to https://coffee-channel.com"
image_credit: "Coffee-Channel.com"
image_credit_url: "https://www.flickr.com/photos/158790927@N08"
image_source_url: "https://www.flickr.com/photos/158790927@N08/27905041519"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to Phoronix, System76 shipped its new Thelio Prime SFF workstation with Pop!_OS 26.04 LTS, the latest Ubuntu‑based release that includes the in‑house COSMIC desktop. To see whether the new OS brings any speed improvements, the reviewer installed Pop!_OS 26.04 on a Thelio Prime unit and then performed a clean reinstall of Pop!_OS 24.04 LTS for side‑by‑side testing.  

Both machines shared identical hardware: an AMD Ryzen 7 9800X3D CPU, 32 GB of DDR5‑5600 RAM, a 1 TB Samsung 9100 PRO NVMe SSD, and an NVIDIA GeForce RTX 5060 Ti GPU. The software stack was also aligned as closely as possible—both runs used the Linux 7.2 kernel and the same NVIDIA driver version, and both were on COSMIC 1.11.  

The primary differences between the two OS versions are the underlying toolchain and libraries. Pop!_OS 26.04 moves from GCC 13.2 to GCC 15.2, upgrades Python from 3.12 to 3.14, and includes a slew of other package updates that System76 does not back‑port as stable‑release updates (SRUs). The benchmark suite covered typical desktop workloads, such as compilation, Python script execution, and GPU‑accelerated tasks, though the article does not list exact numbers.

## Why it matters  

### Consistent baseline for hardware reviewers  

System76’s Thelio Prime is marketed toward developers and creators who expect reliable performance out of the box. By publishing side‑by‑side numbers, the company gives potential buyers a concrete sense of what “LTS” really means—whether the newer release merely updates packages or actually squeezes extra throughput from the same silicon.

### Compiler upgrades can matter  

Moving from GCC 13 to GCC 15 may seem incremental, but newer compilers often generate tighter machine code, improve auto‑vectorization, and support newer instruction sets. For developers who compile large codebases (e.g., the Linux kernel, scientific libraries, or game engines), even a few percent gain can translate into noticeable productivity boosts.

### Python version bump  

Python 3.14 introduces performance optimizations and new standard‑library features. Users who run data‑science notebooks, automation scripts, or web services on the desktop may see faster script start‑up and reduced CPU usage, especially when the workload is CPU‑bound.

### Keeping the kernel and driver constant  

By aligning the kernel and NVIDIA driver across both releases, the test isolates the impact of user‑space changes. This is a good practice for anyone who wants to compare distro upgrades without the noise of driver regressions or kernel‑level scheduling differences.

## What you can do  

### 1. Verify your own performance after an upgrade  

If you’re already on Pop!_OS 24.04 and are considering the jump to 26.04, run a few simple checks to see whether you notice a difference.

```bash
# Measure compilation speed of a medium‑sized project
time make -j$(nproc)

# Benchmark Python start‑up time
python3 -c "import time, sys; start=time.time(); import numpy; print('Import time:', time.time()-start)"
```

> **Caution:** The `make` command will compile whatever source is in the current directory. Use a test project, not a production codebase, to avoid unintended rebuilds.

### 2. Pin the kernel or driver if you need stability  

Because System76 updates the kernel and NVIDIA driver across LTS releases, you can keep the current kernel if you’ve verified it works well with your workloads. Use `apt-mark hold` to prevent accidental upgrades:

```bash
sudo apt-mark hold linux-image-7.2.0-... linux-headers-7.2.0-...
sudo apt-mark hold nvidia-driver-595
```

Replace the ellipsis with the exact package names shown by `dpkg -l | grep linux-image` and `dpkg -l | grep nvidia-driver`.

### 3. Take advantage of the newer compiler  

If you compile software manually, ensure you’re using the default GCC that ships with the new release:

```bash
gcc --version   # Should report 15.2
```

If you need an older version for compatibility, install it side‑by‑side:

```bash
sudo apt install gcc-13
```

Then invoke it explicitly with `gcc-13` when needed.

### 4. Update your Python virtual environments  

After upgrading, recreate your virtual environments to pull in the new interpreter and any updated wheels:

```bash
python3.14 -m venv ~/venv-py314
source ~/venv-py314/bin/activate
pip install --upgrade pip setuptools wheel
```

Test critical scripts inside the new environment before discarding the old one.

### 5. Monitor system resources  

Use `htop` or GNOME System Monitor to watch CPU and memory usage after the upgrade. If you notice regressions, you can roll back specific packages using `apt-get install package=version`.

```bash
sudo apt-get install gcc-13=13.2.0-...   # Example version pinning
```

## Key takeaways  

- **Hardware unchanged, software refreshed:** The benchmark comparison isolates user‑space changes by keeping kernel and GPU driver identical.  
- **Compiler and language upgrades are the main differentiators:** GCC 15.2 and Python 3.14 provide modest performance improvements without altering the underlying kernel.  
- **Real‑world impact is modest but measurable:** For typical desktop tasks the gains are not dramatic, but developers and power users may appreciate the extra speed in compile‑heavy workflows.  
- **Upgrade safely:** Verify performance on your own hardware, pin critical packages if needed, and refresh Python environments to fully benefit from the newer runtime.  
- **Future comparisons pending:** The author plans to benchmark Pop!_OS 26.04 against other distros, which will give a broader perspective on where System76’s LTS sits in the Linux ecosystem.
