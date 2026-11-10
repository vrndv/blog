---
title: "Remote Code Execution Found in Classic Star Wars Racer’s Multiplayer Protocol"
description: "An analysis of the 1999 Star Wars: Episode I Racer reveals a UDP‑based multiplayer flaw that lets attackers run code on vulnerable Windows hosts."
date: 2026-11-10T22:10:42+00:00
category: "Cybersecurity"
tags: ["vulnerability", "multiplayer", "reverse\u2011engineering", "wireshark", "directplay"]
source_name: "Lobsters"
source_url: "https://synacktiv.com/en/publications/star-wars-episode-i-racer"
image: "https://live.staticflickr.com/5506/14296435236_c7ff13f3f4_b.jpg"
image_alt: "Vintage games"
image_credit: "Steven-L-Johnson"
image_credit_url: "https://www.flickr.com/photos/31295868@N06"
image_source_url: "https://www.flickr.com/photos/31295868@N06/14296435236"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to a Synacktiv research note, the multiplayer component of *Star Wars: Episode I – Racer* (the 1999 Windows release distributed by GOG) contains a remote‑code‑execution flaw. The game uses Microsoft’s DirectPlay API to discover and join sessions on a local network.  

During normal operation the client broadcasts UDP packets to port 54792 on the local subnet’s broadcast address. The host replies with a small packet that includes the game name. The researchers captured this traffic with Wireshark and noticed that the payload contains the string “play”, a hint that DirectPlay is in use. However, because the string appears at an unexpected offset, Wireshark’s built‑in DirectPlay dissector does not recognise the protocol.  

Reverse‑engineering the binary in IDA revealed that the game creates a DirectPlay COM object via `CoCreateInstance`, then calls `EnumConnections`. For each discovered network service provider the game receives a GUID and stores it in a `ConnectionInfo_t` array. The array is later used to open a UDP socket and exchange game data.  

A flaw in the handling of the GUID data allows an attacker who can inject a crafted UDP packet to overwrite memory in the host process. The overwritten memory can be controlled to point to attacker‑supplied shellcode, resulting in remote code execution with the privileges of the game process.  

The vulnerability is triggered entirely over the LAN; no authentication or encryption is performed. Because the game runs with the user’s rights, an exploit could be used to install additional malware, steal credentials stored by the user, or pivot to other systems on the same network.  

## Why it matters  

*Legacy software on modern systems* – Many enthusiasts still run classic Windows games on current hardware, often using compatibility layers or virtual machines. Even though the game is over two decades old, it still ships a network stack that can be abused.  

*Unprotected UDP services* – The issue exemplifies the risks of exposing UDP services without authentication or integrity checks. Broadcast discovery is convenient for gamers but also gives any device on the subnet a chance to speak the protocol.  

*DirectPlay’s obscurity* – DirectPlay is a deprecated Microsoft API that is rarely examined today. Vulnerabilities in such legacy components can slip through security reviews, especially when they are hidden behind custom binary protocols.  

*Potential lateral movement* – An attacker who compromises one player’s machine can use the game’s process to launch further attacks against other hosts on the same LAN, a classic “trusted‑host” scenario.  

## What you can do  

### 1. Isolate the game from trusted networks  

If you still enjoy playing *Star Wars Racer* on a modern Windows box, keep it on a separate VLAN or a virtual network that does not have access to sensitive resources.  

```bash
# Example: create an isolated Hyper‑V virtual switch (requires admin)
# WARNING: This will affect existing VMs using the default switch.
New-VMSwitch -Name "IsolatedSwitch" -SwitchType Private
```  

### 2. Block the UDP port at the firewall  

The game uses UDP port 54792 for discovery and session traffic. Adding a rule to block inbound/outbound traffic on that port will stop the exploit from reaching the vulnerable process.  

```powershell
# Windows Defender Firewall rule (run as Administrator)
New-NetFirewallRule -DisplayName "Block Racer UDP" `
    -Direction Inbound -Protocol UDP -LocalPort 54792 -Action Block
```  

### 3. Run the game with limited privileges  

Create a dedicated, non‑admin local user account for playing legacy titles and launch the game under that account. This limits the impact of any code execution.  

```powershell
# Create a low‑privilege user (run as Administrator)
New-LocalUser -Name "racer_user" -NoPassword -AccountNeverExpires
Add-LocalGroupMember -Group "Users" -Member "racer_user"
```  

Then use `runas` to start the game:  

```cmd
runas /user:racer_user "C:\Games\Racer\racer.exe"
```  

### 4. Monitor network traffic for suspicious broadcasts  

Because the protocol is UDP‑based and uses a fixed port, you can set up a simple Wireshark or Zeek filter to alert on unexpected traffic.  

Wireshark display filter:  

```
udp.port == 54792 && ip.dst == 255.255.255.255
```  

Zeek script snippet (save as `racer-detect.zeek`):  

```zeek
event udp_packet(c: connection, is_orig: bool, len: count, payload: string)
{
    if (c$dest_port == 54792 && c$dst == 255.255.255.255)
        NOTICE([$msg = fmt("Possible Racer broadcast from %s", c$orig_h)]);
}
```  

Deploy the script with your Zeek sensor to get real‑time alerts.  

### 5. Consider removing or sandboxing the game  

If you do not need the multiplayer feature, uninstall the game or move its executable into a sandbox (e.g., Windows Sandbox or a lightweight VM). This eliminates the attack surface entirely.  

## Key takeaways  

- *Star Wars: Episode I – Racer* uses an unauthenticated UDP broadcast on port 54792 for multiplayer discovery.  
- Reverse‑engineering shows DirectPlay is employed, but Wireshark’s default dissector misses it due to an offset mismatch.  
- A memory‑corruption bug in the handling of GUID data enables remote code execution from any device on the same LAN.  
- Mitigations include network isolation, firewall blocking of the UDP port, running the game under a low‑privilege account, and monitoring for abnormal broadcasts.  
- Legacy games can harbor serious flaws; always treat old networked software with the same caution you would apply to modern applications.
