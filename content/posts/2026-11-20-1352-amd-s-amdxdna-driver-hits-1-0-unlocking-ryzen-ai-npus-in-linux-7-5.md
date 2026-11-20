---
title: "AMD’s AMDXDNA Driver Hits 1.0, Unlocking Ryzen AI NPUs in Linux 7.5"
description: "AMD’s AMDXDNA driver reaches version 1.0 with Linux 7.5, adding support for Ryzen AI NPU10 and NPU11, expanding AI workloads on Linux."
date: 2026-11-20T13:52:05+00:00
category: "Tech Explained"
tags: ["amd", "linux", "ai", "driver", "hardware"]
source_name: "Phoronix"
source_url: "https://www.phoronix.com/news/AMDXDNA-1.0-Linux-Driver"
image: "https://live.staticflickr.com/4640/39218551432_31999e2312_b.jpg"
image_alt: "2017-12-23_03-26-09"
image_credit: "steevithak"
image_credit_url: "https://www.flickr.com/photos/8386148@N06"
image_source_url: "https://www.flickr.com/photos/8386148@N06/39218551432"
image_license: "BY-SA 2.0"
image_license_url: "https://creativecommons.org/licenses/by-sa/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-20b"
---
## What happened  
According to Phoronix, the AMDXDNA accelerator driver has been promoted to version 1.0 with the release of the Linux 7.5 kernel. This milestone brings official support for the Ryzen AI Neural Processing Units (NPUs), specifically the NPU10 and NPU11 models, into the Linux kernel’s hardware acceleration stack. The driver is now a stable, production‑ready component that developers can rely on for AI inference workloads on AMD‑based systems.

## Why it matters  
### Expanding AI on commodity hardware  
Historically, high‑performance AI inference on Linux has leaned heavily on NVIDIA GPUs or specialized accelerators. With the AMDXDNA driver now stable, Ryzen‑based CPUs can offload neural network inference to their integrated NPUs. This means that developers and researchers can run AI models directly on mainstream desktop and server hardware without needing a separate GPU or external accelerator.

### Kernel‑level integration  
The driver’s inclusion in the mainline kernel removes the need for third‑party binaries or proprietary firmware. It integrates with existing kernel interfaces such as the *device‑tree* and *devlink* subsystems, making it easier for distributions to ship fully supported binaries. This also simplifies the build process for custom kernels and reduces the attack surface compared to shipping unverified binaries.

### Performance and power efficiency  
Ryzen AI NPUs are designed for low‑power inference, targeting workloads like image classification, object detection, and natural language processing on edge devices. By providing a kernel‑level driver, AMD enables fine‑grained power management and better scheduling of AI tasks alongside other workloads. Early benchmarks from community testing suggest that NPU10 can deliver competitive throughput for lightweight models, while NPU11 offers higher compute density for more demanding inference.

### Ecosystem impact  
The driver’s release encourages the growth of AI frameworks that can target AMD hardware. Libraries such as TensorFlow, PyTorch, and ONNX Runtime can, in future releases, expose backends that tap into the AMDXDNA API. This will broaden the hardware options for developers, fostering competition and potentially driving down costs for AI workloads.

## What you can do  
Below are concrete steps for developers, system integrators, and enthusiasts who want to take advantage of the new driver.

### 1. Verify kernel support  
Make sure your distribution is running Linux 7.5 or later. On most systems, you can check the kernel version with:

```bash
uname -r
```

If you’re not on 7.5, upgrade your kernel or install a backport that includes the AMDXDNA driver.

### 2. Install the latest firmware  
AMD’s NPUs require firmware blobs that are usually bundled with the kernel. Verify that the firmware files (`amdxdna.bin`, etc.) are present in `/lib/firmware/`. If not, install the `linux-firmware` package for your distribution.

```bash
# Debian/Ubuntu
sudo apt-get install linux-firmware

# Fedora/RHEL
sudo dnf install linux-firmware
```

### 3. Check device visibility  
The driver exposes the NPUs as character devices under `/dev`. List them with:

```bash
ls -l /dev/amdxdna*
```

You should see entries like `/dev/amdxdna0` for NPU10 and `/dev/amdxdna1` for NPU11. If they’re missing, ensure the kernel module is loaded:

```bash
sudo modprobe amdxdna
```

### 4. Use the driver in your application  
Most AI frameworks will need a custom backend to communicate with the AMDXDNA driver. If you’re developing a C/C++ application, the driver exposes a simple ioctl interface. A minimal example in C:

```c
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <stdio.h>

int main() {
    int fd = open("/dev/amdxdna0", O_RDWR);
    if (fd < 0) {
        perror("open");
        return 1;
    }

    // Example: submit a dummy inference request
    // ioctl(fd, AMDXDNA_SUBMIT, &request);

    close(fd);
    return 0;
}
```

> **Warning:** The ioctl constants and request structures are not publicly documented; consult the kernel source or AMD’s SDK for details.

### 5. Benchmark your workload  
Use a simple inference script (e.g., a TensorFlow Lite model) and time its execution with the NPUs versus CPU. A basic benchmark script:

```bash
#!/usr/bin/env bash
MODEL="mobilenet_v2.tflite"

# Run on CPU
time tflite_runtime_interpreter --model $MODEL --device cpu

# Run on NPU
time tflite_runtime_interpreter --model $MODEL --device amdxdna0
```

Compare the timings to gauge the performance benefit.

### 6. Contribute back  
If you discover bugs or performance regressions, consider opening an issue in the kernel’s AMDXDNA subsystem or contributing a patch. The driver is now at version 1.0, but the community can still improve its stability and feature set.

## Key takeaways  
- The AMDXDNA driver has reached a stable 1.0 release with Linux 7.5, enabling Ryzen AI NPU10 and NPU11 support.  
- This integration brings AI inference to mainstream AMD CPUs, reducing reliance on GPUs and specialized accelerators.  
- The driver is kernel‑level, simplifying distribution packaging and enhancing security through official maintenance.  
- Developers can now explore low‑power, high‑throughput inference on commodity hardware, broadening the AI ecosystem.  

By keeping your kernel up to date, installing the required firmware, and leveraging the driver in your AI projects, you can tap into the full potential of AMD’s AI hardware directly from Linux.
