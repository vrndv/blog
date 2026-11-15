---
title: "Strata OS: An Explicit‑Memory Architecture That Puts Control Back in Software"
description: "Strata replaces hidden caches with software‑managed local stores, letting programs decide what lives where and overlap transfers for performance."
date: 2026-11-15T21:29:37+00:00
category: "Tech Explained"
tags: ["operating-systems", "cpu-architecture", "low-level-programming", "microkernel", "systems"]
source_name: "Lobsters"
source_url: "https://yrashk.com/strata/"
image: "https://upload.wikimedia.org/wikipedia/commons/9/97/Compaq_CR120_Processor_Board-3197.jpg"
image_alt: "Compaq CR120 Processor Board-3197"
image_credit: "Raimond Spekking"
image_credit_url: "https://www.wikidata.org/wiki/Q108103612"
image_source_url: "https://commons.wikimedia.org/w/index.php?curid=86014131"
image_license: "BY-SA 4.0"
image_license_url: "https://creativecommons.org/licenses/by-sa/4.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to the author’s blog post, a new experimental system called **Strata** rethinks the way modern CPUs expose memory. Instead of presenting a flat, uniformly fast address space, Strata makes the hierarchy of storage explicit. Each core owns a small, fast **Local Store** of 64 KiB for data and another 64 KiB for instructions. Anything outside those stores is considered “far memory” and can only be accessed through explicit transfer primitives: `tget`, `tput` and `tgetx`.  

These primitives issue a transfer and return a *completion tag*. The hardware stalls any further access to the same address range until the tag signals completion, allowing software to overlap computation with data movement. Memory capabilities describe far memory regions; they can be split, joined, handed to another core, or revoked in bulk, eliminating implicit copying.  

The system runs a microkernel written in Strata assembly. The kernel itself is tiny—only a few kilobytes stay resident—while the rest of its code is loaded on demand into the instruction Local Store using the same transfer mechanism that user programs use. Services such as process management, device drivers, the file system, terminals and a window server all execute in user mode and communicate by passing *lent buffer capabilities* directly to each other, bypassing any hidden kernel mediation.  

Context switches are implemented by copying the used Local Store contents out and back in, making the cache flush that other CPUs hide visible to the programmer. The window server is the only component that touches the framebuffer; it receives drawing buffers from clients as capabilities, tiles them on a grid, and updates a visual indicator that shows which core runs which process.  

A bootstrapped Forth environment demonstrates the model: words compile to native Strata code in data memory, then are installed into instruction memory with `tgetx`, effectively acting as a just‑in‑time compiler you can watch. A self‑hosting C99 compiler (`cc`) runs inside StrataOS, compiling programs in a single pass without a separate assembler or linker. The reference emulator, compiled to WebAssembly, lets users explore the system on a typical desktop, watching multiple cores render a Mandelbrot set or compile C code on the fly.  

## Why it matters  

### Exposing memory hierarchy removes hidden latency  

Current mainstream CPUs hide cache behavior behind a uniform address space. While this simplifies programming, it also forces developers to accept unpredictable stalls caused by cache misses, write‑back policies, and coherence traffic. Strata makes those costs visible, enabling programs to schedule transfers deliberately and overlap them with useful work. This can lead to more predictable performance, especially on workloads that are memory‑bound or that run on many cores where contention is a major factor.  

### Capability‑based access reduces accidental data races  

Because far memory is accessed only through capabilities that can be lent and revoked atomically, the system eliminates the traditional notion of a data race as a programmer‑written invariant. When a capability is revoked, all outstanding accesses are invalidated together, providing a clean synchronization point without the need for locks or memory fences in many cases.  

### Microkernel design with explicit I/O simplifies verification  

All inter‑process communication is a direct transfer of a capability, and interrupts are modeled as the completion of a transfer. This uniform model reduces the number of special‑case code paths in the kernel, making formal reasoning about correctness more tractable.  

### A self‑hosting toolchain proves the model is practical  

The existence of a working Forth environment and a C compiler that compile themselves inside StrataOS demonstrates that the architecture is not just a thought experiment. It can support real‑world languages and development workflows, which is essential for any platform that hopes to attract developers.  

## What you can do  

### 1. Play with the Strata emulator  

The reference emulator runs as WebAssembly, so you can try it in any modern browser. Follow these steps on a Linux or macOS terminal (the emulator itself is safe; it does not modify your host system):

```bash
# Install Verilator 5 (required for building the emulator)
sudo apt-get install verilator   # Debian/Ubuntu
# or
brew install verilator           # macOS

# Clone the repository
git clone https://github.com/yrashk/strata
cd strata

# Build the emulator (takes a few minutes)
make emulator

# Run the emulator with the default 12‑core configuration
./emulator -c 12
```

> **Warning:** The build process compiles Verilog sources; ensure you have enough RAM (≈2 GiB) and disk space.  

Once the emulator starts, you’ll see a window showing the core lattice and a shell prompt. Try typing `mandelbrot` to watch the cores draw a fractal, or explore the built‑in Forth REPL.  

### 2. Examine the source‑browser  

The project ships a web‑based source browser that lets you navigate every assembly, Forth, and C file. Use it to see how `tgetx` is used to load code into the instruction Local Store, or how capability revocation is implemented. Understanding these patterns can inspire similar designs in your own low‑level projects.  

### 3. Experiment with capability‑based buffers  

Write a tiny program that allocates a far‑memory buffer, splits it into two capabilities, and hands one to a second core. Observe how the runtime enforces exclusive access and how revocation works. This hands‑on experience will deepen your intuition about safe sharing without locks.  

```c
// Pseudo‑code illustrating capability split
capability buf = allocate_far(4096);
capability part1, part2;
split(buf, &part1, &part2);   // now two halves
send_to_core(core_id, part1); // core 1 can only touch its half
revoke(buf);                  // instantly invalidates both halves
```

> The actual syntax depends on the Strata assembly language; the above is illustrative only.  

### 4. Follow the project’s development  

If you’re interested in low‑level OS research, consider watching the project’s mailing list or GitHub issues. Contributing a small utility—perhaps a new device driver written in Strata assembly—can be a valuable way to learn the platform while helping the community.  

## Key takeaways  

- **Strata discards the illusion of a flat, fast memory space**; instead, it gives programs explicit control over where data lives and when it moves.  
- **Local Stores act as programmer‑managed scratchpads**, turning what is normally hidden cache behavior into a first‑class resource.  
- **Capability‑based far memory eliminates implicit copies and simplifies synchronization**, offering a fresh approach to avoiding data races.  
- **The microkernel and its services run entirely in user mode**, communicating via lent capabilities, which reduces kernel complexity and improves verifiability.  
- **A working Forth environment and self‑hosting C compiler prove the model is usable**, not just theoretical.  
- **You can explore the system today** with the WebAssembly emulator; no special hardware is required.  

By making memory hierarchy explicit, Strata invites developers to think like the hardware they run on, potentially unlocking more deterministic performance and safer concurrency models. Even if the design never reaches mainstream CPUs, the ideas it showcases are valuable for anyone building high‑performance, low‑level software.
