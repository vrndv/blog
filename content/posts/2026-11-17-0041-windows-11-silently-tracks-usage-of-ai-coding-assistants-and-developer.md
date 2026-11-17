---
title: "Windows 11 silently tracks usage of AI coding assistants and developer tools"
description: "A built‑in Windows component records when you run popular AI coding agents and development binaries, then sends the data to Microsoft unless you opt out."
date: 2026-11-17T00:41:00+00:00
category: "Cybersecurity"
tags: ["windows", "telemetry", "developer-tools", "privacy", "diagnostics"]
source_name: "xusheng.dev"
source_url: "https://xusheng.dev/posts/windows-coding-agent-telemetry/"
image: "https://live.staticflickr.com/8482/8191245592_65e5bbd144_b.jpg"
image_alt: "Google Analytics on Computer Screen"
image_credit: "bluefountainmedia"
image_credit_url: "https://www.flickr.com/photos/32110556@N03"
image_source_url: "https://www.flickr.com/photos/32110556@N03/8191245592"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

While probing recent Windows binaries for hidden features, a researcher discovered that **MissionControlAggregator.dll** contains hard‑coded strings for a range of AI coding agents (e.g., *codex.exe*, *claude.exe*, *copilot.exe*, *cursor.exe*) and traditional developer utilities (e.g., *python.exe*, *dotnet.exe*, *gcc.exe*, *code.exe*).  

The DLL implements a series of “executable‑name matcher” functions. When Windows loads the component, it subscribes to system events that report process state changes (KernelProcess.AppStateChangeSummary, Win32kTraceLogging.AppInteractivitySummary) as well as WSL execution events (Microsoft.Windows.Lxss.Manager.Exec). Each time a process matching one of the embedded names appears, the matcher records a hit in an internal table.  

Later, the component aggregates the hits into three bitsets—twelve broad tool categories, four CLI‑style AI agents, and five desktop‑style AI agents—and emits an ETW (Event Tracing for Windows) report called **Segments.SubCohorts**. This report is forwarded to the Windows Diagnostics service.  

Because the “optional diagnostic data” setting is enabled by default, the telemetry is uploaded to Microsoft unless the user explicitly disables it.  

## Why it matters  

### Privacy implications  
The telemetry does not merely note that a generic development environment was used; it distinguishes between specific AI assistants and individual compilers. This level of granularity can reveal a developer’s workflow, preferred tooling, and even the adoption of emerging AI‑driven code generators. For privacy‑conscious users or organizations with strict data‑handling policies, that information may be considered sensitive.  

### Compliance considerations  
Enterprises that must comply with regulations such as GDPR, CCPA, or internal data‑handling agreements often need to know exactly what personal or operational data leaves their machines. Implicit collection of tool‑usage data could be viewed as a breach of consent if users are not clearly informed.  

### Security posture  
Telemetry pipelines are attractive targets for threat actors seeking to infer the software stack of a system. Knowing that a machine runs a particular compiler or AI assistant can help an attacker tailor exploits. While the data is transmitted over encrypted channels, the mere existence of this fingerprint adds another surface for potential abuse.  

## What you can do  

### 1. Review and adjust your diagnostic settings  

Windows stores the diagnostic preference under **Settings → Privacy & security → Diagnostics & feedback**.  

```powershell
# Check current setting (0 = required, 1 = optional, 2 = full)
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name "AllowTelemetry"
```

- **Disable optional telemetry**: Set the value to `0` (required) or `1` (basic) to stop the optional data, which includes the coding‑agent usage.  
- **Turn off full diagnostics**: Choose the “Basic” level to limit what is sent.  

> **Warning:** Changing the registry can affect system behavior. Use the Settings UI when possible, or back up the key before editing.  

### 2. Use local firewalls to block the telemetry endpoint  

If you prefer to keep the setting unchanged but still block outbound traffic, add a rule that denies connections to the Windows Diagnostics service endpoints.  

```bash
# Example using Windows Defender Firewall (run as Administrator)
netsh advfirewall firewall add rule name="Block Windows Diagnostics" dir=out action=block remoteip=13.107.64.0/20 enable=yes
```

> **Note:** The IP range above is illustrative; you’ll need to identify the exact endpoint used by your version of Windows.  

### 3. Employ process‑monitoring tools to verify activity  

Tools like **Process Monitor** or **Windows Event Viewer** can show when MissionControlAggregator.dll receives process‑state events.  

```powershell
# Simple ETW trace to watch for the specific provider
logman start "MissionControlTrace" -p Microsoft-Windows-Diagnostics-MissionControl -ets
```

Watch for events with the name **Segments.SubCohorts**; their appearance indicates a telemetry payload is being generated.  

### 4. Consider sandboxing or containerizing development workloads  

Running compilers and AI assistants inside a VM, container, or WSL distribution with network isolation prevents the host‑level DLL from seeing those processes. For example, use a Docker container that has no outbound network access, or a WSL2 distro with a custom firewall rule.  

```bash
# Example Docker run with no network
docker run --rm -it --network none my-dev-image bash
```

### 5. Stay informed about future Windows updates  

Microsoft occasionally modifies telemetry scopes. Subscribe to the Windows Insider release notes or the official Windows telemetry documentation to track changes.  

## Key takeaways  

- **MissionControlAggregator.dll** in Windows 11 watches for a predefined list of AI coding agents and classic developer tools, records matches, and sends the data to Microsoft’s diagnostics service.  
- The telemetry is part of the “optional diagnostic data” bundle, which is enabled by default on most installations.  
- Privacy‑focused users can mitigate the collection by disabling optional diagnostics, blocking the outbound endpoint, or isolating development tools in sandboxed environments.  
- Understanding what telemetry is sent from your machine is essential for compliance, security, and maintaining control over your development workflow.
