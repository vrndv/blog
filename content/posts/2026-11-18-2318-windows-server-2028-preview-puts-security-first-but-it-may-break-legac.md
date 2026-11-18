---
title: "Windows Server 2028 preview puts security first, but it may break legacy workloads"
description: "Microsoft’s new Server 2028 preview ships a hardened‑by‑default Core install aligned with DoD benchmarks, shifting the hardening effort from post‑deployment to out‑of‑the‑box."
date: 2026-11-18T23:18:20+00:00
category: "Cybersecurity"
tags: ["windows", "server", "hardening", "dod", "preview"]
source_name: "Ars Technica"
source_url: "https://arstechnica.com/gadgets/2026/11/windows-server-2028-public-preview-bets-on-a-security-first-approach/"
image: "https://live.staticflickr.com/65535/52869680198_d77a3efb5e_b.jpg"
image_alt: "12 Pneumatic tubes, Radio space DSC_0183"
image_credit: "wbaiv"
image_credit_url: "https://www.flickr.com/photos/9998127@N06"
image_source_url: "https://www.flickr.com/photos/9998127@N06/52869680198"
image_license: "BY-SA 2.0"
image_license_url: "https://creativecommons.org/licenses/by-sa/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

At Microsoft’s recent Ignite event the company unveiled a public preview of **Windows Server 2028**. The most notable change is a “security‑by‑default” posture for the Server Core edition, which now boots with a configuration that mirrors the Department of Defense’s DISA Security Technical Implementation Guide (STIG).  

Key points of the hardened default include:  

- **Kerberos** is the preferred authentication protocol, with NTLM still present but not the default.  
- **TLS** connections are limited to modern cipher suites, and the TLS stack uses a hybrid post‑quantum key‑exchange (ML‑KEM) for added future‑proofing.  
- **LSASS** receives extra protections, and remote‑desktop authentication is tightened.  
- **PowerShell** script‑block logging is enabled by default, giving administrators better visibility into script activity.  
- The **NVMe storage stack** that previously required manual activation is now the default, removing the SCSI translation layer for better performance.  

These defaults apply only to Server Core installations; the Desktop Experience flavor retains the traditional, more configurable baseline. Microsoft stresses that administrators can still adjust settings, but the starting point is now a pre‑hardened system rather than a blank canvas.  

The preview is not a release candidate. Microsoft openly acknowledges that the hardened defaults may cause compatibility problems with older applications, legacy authentication mechanisms, or existing management scripts. A known issue in the current build is a race condition in the hybrid TLS key‑exchange that can crash the LSASS service; the recommendation is to disable hybrid groups until the bug is fixed.  

## Why it matters  

### Reducing the “window of exposure”  

Historically, a newly provisioned Windows Server would run with permissive defaults, leaving it vulnerable until an admin applied hardening scripts or Group Policy objects. By shipping a server that is already aligned with a recognized DoD benchmark, Microsoft shortens the period during which a fresh machine is exposed to common attacks such as credential dumping, man‑in‑the‑middle TLS downgrade, or NTLM relay.  

### Aligning with high‑assurance standards  

Enterprises that must comply with federal or regulated environments often adopt DISA STIGs as a baseline. Having those controls baked into the OS reduces the administrative overhead of importing and validating STIG compliance, and it makes audit trails clearer—what you see on a fresh install is already “STIG‑compliant.”  

### Preparing for post‑quantum cryptography  

The inclusion of a hybrid post‑quantum key exchange shows Microsoft’s intent to future‑proof its server platform. While the current implementation still has a bug, the move signals that future Windows Server releases will likely default to quantum‑resistant algorithms, an important consideration for long‑term data confidentiality.  

### Compatibility trade‑offs  

The flip side is that legacy software expecting NTLM, older cipher suites, or specific storage stack behavior may fail to start. Organizations with deep‑rooted on‑premises workloads will need to test extensively before adopting the preview in production. The approach also pushes the responsibility of compatibility testing onto the community, as Microsoft solicits feedback on what breaks.  

## What you can do  

### 1. Spin up a test environment  

Use the preview build on a non‑production machine or a sandboxed virtual environment. Because the hardened defaults only affect Server Core, you can compare a Core install with a Desktop Experience install to see the impact on your tooling.  

```bash
# Example: create a Windows Server 2028 Core VM with Hyper‑V (run on a Windows host)
# Adjust memory and disk sizes to match your test needs.
New-VM -Name WS2028CorePreview -MemoryStartupBytes 4GB -Generation 2
Set-VMFirmware -VMName WS2028CorePreview -EnableSecureBoot On
Set-VHD -Path "C:\VMs\WS2028CorePreview\VirtualHardDisk.vhdx" -SizeBytes 60GB
# Attach the preview ISO (downloaded from Microsoft’s preview portal)
Add-VMDvdDrive -VMName WS2028CorePreview -Path "C:\Downloads\WindowsServer2028-Preview.iso"
Start-VM -Name WS2028CorePreview
```

> **Warning:** The commands above create a new virtual machine and allocate storage. Ensure you have sufficient disk space and that the VM does not interfere with production workloads.  

### 2. Verify authentication defaults  

After the VM boots, check which authentication protocol is active.  

```powershell
# List the current authentication provider order
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\Kerberos\Parameters" -Name "SupportedEncryptionTypes"
```  

If you need to temporarily re‑enable NTLM for legacy apps, you can adjust the relevant registry keys, but remember to document any deviation from the hardened baseline.  

### 3. Test TLS and cipher suite selection  

Run a simple OpenSSL client against the server to see which cipher suites are offered.  

```bash
openssl s_client -connect <server_ip>:443 -tls1_2 -cipher ALL
```  

If the connection fails because the client only supports older suites, you’ll know that the server’s default policy is blocking it.  

### 4. Evaluate NVMe performance  

If your workload relies on high‑throughput storage, compare the default NVMe stack against the older SCSI‑based path. Use a tool like `diskspd` to generate I/O patterns and record latency.  

```powershell
# Example: 4K random read test for 30 seconds
diskspd -b4K -r -t4 -d30 -o2 -w0 -c1G \\.\PhysicalDrive0
```  

### 5. Report findings  

Microsoft encourages feedback. When you encounter a breakage, note the exact setting, the application involved, and the change required to make it work. Submit this information through the preview feedback portal or the Windows Server Team blog comment section.  

### 6. Plan for phased rollout  

If testing shows acceptable compatibility, consider a staged deployment:  

1. **Pilot** – Deploy the hardened Core on a small set of non‑critical services.  
2. **Monitor** – Use built‑in logging (e.g., PowerShell script‑block logs, Event Viewer) to watch for unexpected failures.  
3. **Adjust** – Apply targeted exceptions only where absolutely necessary, keeping the rest of the system on the hardened baseline.  
4. **Scale** – Expand to broader workloads once confidence is established.  

## Key takeaways  

- **Windows Server 2028 preview ships a DoD‑aligned, hardened‑by‑default configuration for Server Core**, moving security from a post‑install project to the initial state.  
- The default switches to **Kerberos**, modern TLS cipher suites, and a hybrid post‑quantum key exchange, while also enabling **NVMe storage** without manual activation.  
- **Compatibility is the trade‑off**; older protocols, legacy authentication, and some management scripts may break, and a known TLS race condition can crash LSASS.  
- **Testing is essential** – use a sandboxed Core VM, validate authentication, TLS, and storage behavior, and provide feedback to Microsoft.  
- Organizations can **reduce exposure time**, simplify compliance, and start preparing for post‑quantum cryptography, but must manage exceptions carefully to avoid operational disruption.
