---
title: "systemd adds Rust support while keeping C core intact"
description: "systemd now lets developers write new components in Rust, but the core library stays in C to avoid bloat and maintain compatibility."
date: 2026-11-08T21:02:20+00:00
category: "Tech Explained"
tags: ["systemd", "rust", "linux", "build-system", "security"]
source_name: "Lobsters"
source_url: "https://amutable.com/blog/systemd-loves-rust"
image: "https://live.staticflickr.com/32/38935271_dec5673861_b.jpg"
image_alt: "The messy server room, minus shelving"
image_credit: "sylvar"
image_credit_url: "https://www.flickr.com/photos/44124401501@N01"
image_source_url: "https://www.flickr.com/photos/44124401501@N01/38935271"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

The init system and service manager **systemd** has merged a new code path that allows developers to add Rust‑based binaries to the project. From now on, contributors can write fresh utilities in Rust while the existing shared library and the majority of the code base remain written in C.  

The decision was not taken lightly. Systemd’s maintainers evaluated two possible integration strategies:  

1. **Wrap the existing C library with Rust crates** – keep the shared core in C, expose its functions to Rust, and let new Rust programs link against those crates.  
2. **Replace core components with Rust code compiled into the same shared library** – this would require a stable ABI for Rust libraries, something the language still lacks.  

The team concluded that option 1 is acceptable, while option 2 is currently impractical. The “stable ABI problem” means that a Rust‑compiled shared library cannot reliably be mixed with other binaries without duplicating large portions of the Rust runtime. For a project that already ships more than a hundred small executables, static linking each one with its own copy of the Rust runtime would dramatically increase size and memory usage.  

Consequently, systemd will continue to provide its extensive C‑only shared library, which contains many security‑focused helpers such as the `chase*()` family of file‑descriptor‑based path‑lookup functions. Rust code will call into this library through thin wrappers, ensuring that the same core functionality is available regardless of the implementation language.  

The integration also respects systemd’s long‑standing build philosophy. Systemd uses the **Meson** build system, and the maintainers deliberately avoided pulling in Cargo, Rust’s default build tool, to keep the build process uniform for downstream packagers. Dependency handling remains strict: systemd links only against the standard C library, and any additional code is loaded at runtime via `dlopen()`. External Rust crates are not automatically accepted; each would undergo a security and maintenance review before being allowed.  

## Why it matters  

### Consistency across the ecosystem  

Systemd is a foundational component of most modern Linux distributions. Its tools are expected to behave identically, regardless of whether a particular binary is written in C or Rust. By enforcing uniform command‑line parsing, help output, and error handling, the project prevents users from encountering subtle differences that could break scripts or automation.  

### Security‑first approach  

The C core of systemd already implements many hardening mechanisms that are not present in the standard Rust libraries. For example, the `chase*()` helpers provide a vetted, file‑descriptor‑based path resolution that automatically incorporates the latest kernel security features. By keeping these helpers in C and exposing them to Rust, the project ensures that new Rust utilities inherit the same level of protection without re‑implementing complex logic.  

### Supply‑chain hygiene  

Introducing Cargo into the build pipeline would open a new attack surface: the Rust package ecosystem is vast, and each crate brings its own set of transitive dependencies. Systemd’s maintainers have historically been wary of such “dependency creep,” preferring to keep the binary’s external footprint minimal. By restricting Rust usage to optional crates that wrap the existing C API, the project reduces the risk of malicious code slipping into the core system.  

### Practicality for distributions  

Linux distributions already maintain patches and packaging scripts for systemd’s Meson build. Adding a second build system would increase maintenance burden for every downstream maintainer, from Debian to Arch. The decision to stay with Meson preserves the status quo for packagers and avoids the need for additional tooling or CI pipelines.  

## What you can do  

### For developers interested in contributing  

1. **Read the contribution guidelines** – systemd’s documentation outlines the process for adding new Rust crates that wrap the core C library.  
2. **Set up a Meson build environment** – you can compile systemd with Rust support by enabling the appropriate Meson option (e.g., `-Denable-rust=true`).  
3. **Write thin wrappers** – expose needed C functions via `extern "C"` declarations in Rust, then build a crate that calls them. This keeps the Rust binary small and leverages existing security‑critical code.  

```bash
# Example: install build dependencies (adjust for your distro)
sudo apt-get install meson ninja-build rustc cargo libsystemd-dev

# Clone the systemd repo and configure with Rust enabled
git clone https://github.com/systemd/systemd.git
cd systemd
meson setup build -Denable-rust=true
ninja -C build
```

> **Warning:** The commands above compile the full systemd source tree. Only run them on a development machine or in a container; do not replace the system’s init system on a production host.  

### For sysadmins and power users  

- **Stay on the distribution’s packaged version** – most distros will ship systemd without the experimental Rust components until they are deemed stable.  
- **Monitor changelogs** – when a new systemd release adds Rust utilities, review the list of binaries to understand any new capabilities or configuration options.  
- **Audit binary sizes** – if you enable optional Rust components, compare their disk usage against the C equivalents to ensure they meet your resource constraints.  

### For security‑focused teams  

- **Review external crates** – any third‑party Rust crate that a systemd component wishes to use must pass the same vetting process as C dependencies. Request the maintainers provide a security assessment before approving new crates.  
- **Enable reproducible builds** – use Meson’s built‑in support for deterministic builds to verify that the compiled binaries match the upstream source.  

## Key takeaways  

- systemd now supports writing new components in Rust while keeping its core library in C to avoid ABI and bloat issues.  
- The project emphasizes uniform behavior, security‑first APIs, and a single build system (Meson) to simplify distribution packaging.  
- External Rust crates are not accepted by default; each must be carefully vetted for maintenance quality and security.  
- Developers can contribute Rust code by wrapping existing C functions, and sysadmins should continue using distribution packages until the new Rust binaries are fully vetted.  

By blending Rust’s safety guarantees with systemd’s battle‑tested C foundation, the project aims to modernize its code base without compromising the stability and security that Linux users rely on.
