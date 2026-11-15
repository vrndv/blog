---
title: "IBM Enables ARM64 Guest VMs on Mainframe s390 Platforms"
description: "IBM’s new dual‑architecture support lets Linux KVM run ARM64 guests on s390 hardware, expanding workload flexibility for mainframe users."
date: 2026-11-15T12:32:48+00:00
category: "Tech Explained"
tags: ["ibm", "arm", "virtualization", "linux", "mainframe"]
source_name: "Phoronix"
source_url: "https://www.phoronix.com/news/IBM-VMs-ARM64-On-s390"
image: "https://live.staticflickr.com/31/99991779_a7997fd239_b.jpg"
image_alt: "28TB"
image_credit: "jared"
image_credit_url: "https://www.flickr.com/photos/35468148654@N01"
image_source_url: "https://www.flickr.com/photos/35468148654@N01/99991779"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to Phoronix, IBM has announced a “dual‑architecture” capability that allows ARM64 instruction sets to be executed inside virtual machines hosted on its s390 mainframe hardware. The feature relies on recent Linux KVM virtualization patches that have been merged into the upcoming Linux 7.4 kernel series. With this integration, a single s390 system can run both native s390 workloads and ARM64 guest operating systems side‑by‑side.  

## Why it matters  

### Broadening workload placement  

Mainframes are traditionally prized for their reliability, I/O throughput, and ability to consolidate large numbers of Linux instances. By adding native support for ARM64 guests, IBM gives customers the option to move workloads that are already optimized for ARM—such as certain cloud‑native microservices or edge‑oriented applications—onto existing mainframe investments. This reduces the need for separate ARM‑based servers and can simplify data‑center footprints.  

### Leveraging ARM’s efficiency  

ARM64 processors are known for strong performance‑per‑watt characteristics. Running those workloads on a mainframe that already offers sophisticated power‑management and cooling can further improve overall energy efficiency, an increasingly important metric for large enterprises.  

### Strengthening the Linux ecosystem  

The required KVM patches being accepted upstream means the capability is not a proprietary IBM extension; it is part of the mainline Linux kernel. This encourages broader community testing, future enhancements, and compatibility with a wide range of Linux distributions. It also showcases the flexibility of KVM as a hypervisor that can abstract away the underlying CPU architecture.  

### Strategic partnership  

IBM’s collaboration with Arm highlights a trend where traditional enterprise hardware vendors are embracing heterogeneous architectures. This partnership may spur additional joint development, such as tool‑chain improvements or performance‑tuning guides tailored for mixed‑architecture environments.  

## What you can do  

If you manage Linux workloads on IBM s390 hardware, consider the following steps to start experimenting with ARM64 guests once the Linux 7.4 kernel (or later) is available.  

### 1. Verify kernel version  

Ensure your host is running a kernel that includes the KVM patches. You can check the version with:  

```bash
uname -r
```  

If the version is older than the required release, plan an upgrade using your distribution’s standard package manager.  

### 2. Install KVM and related tools  

On most Linux distributions, the necessary packages are `qemu-kvm`, `libvirt`, and `virt-manager`. Install them with your package manager:  

```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install qemu-kvm libvirt-daemon-system libvirt-clients virt-manager

# RHEL/CentOS
sudo dnf install @virtualization
```  

### 3. Enable the ARM64 virtualization module  

Load the KVM module for the ARM architecture on the host:  

```bash
sudo modprobe kvm_arm
```  

> **Warning:** Loading an unsupported module can cause kernel warnings. Verify that the module is present in `/lib/modules/$(uname -r)/kernel/arch/arm64/kvm/`.  

### 4. Create an ARM64 guest image  

Download a minimal ARM64 Linux distribution (e.g., an Alpine or Ubuntu cloud image).  

```bash
wget https://cloud-images.ubuntu.com/releases/22.04/release/ubuntu-22.04-server-arm64.img
```  

### 5. Define and start the VM  

Use `virt-install` to create a new VM that targets the ARM64 architecture while the host remains s390:  

```bash
sudo virt-install \
  --name arm64-test \
  --memory 2048 \
  --vcpus 2 \
  --arch aarch64 \
  --os-variant ubuntu22.04 \
  --disk path=ubuntu-22.04-server-arm64.img,format=qcow2 \
  --import \
  --network network=default \
  --graphics none \
  --console pty,target_type=serial
```  

The `--arch aarch64` flag tells KVM to emulate an ARM64 CPU for the guest.  

### 6. Test and monitor  

After the VM boots, log in via the serial console and run basic commands to confirm CPU identification:  

```bash
cat /proc/cpuinfo | grep "model name"
```  

You should see an ARM64 identifier. Use standard monitoring tools (`top`, `htop`) to observe performance and compare against native s390 VMs.  

### 7. Harden your environment  

- **Restrict access**: Use libvirt’s ACLs to limit which users can create or manage ARM64 guests.  
- **Apply security updates**: Keep both the host kernel and guest images patched.  
- **Enable SELinux/AppArmor**: Enforce mandatory access controls for the VM processes.  
- **Network segmentation**: Place ARM64 guests on isolated virtual networks if they will handle untrusted workloads.  

## Key takeaways  

- IBM’s new dual‑architecture support lets ARM64 guests run on s390 mainframes via Linux KVM.  
- The feature is enabled by upstream kernel patches merged for Linux 7.4, ensuring broad compatibility.  
- This capability can consolidate heterogeneous workloads, improve energy efficiency, and deepen the Linux‑mainframe partnership.  
- System administrators can start testing by upgrading to a compatible kernel, installing KVM tools, and launching ARM64 VMs with `virt-install`.  
- As always, apply hardening best practices—access control, timely updates, and network isolation—to keep the mixed‑architecture environment secure.
