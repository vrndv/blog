---
title: "Trezor hardware wallets hit by supply‑chain implants, firmware fix released"
description: "Trezor confirms three Safe 5 wallets sold by a Southeast Asian reseller were compromised with a circuit‑board implant that stole recovery phrases, and outlines how the new firmware blocks the threat."
date: 2026-11-14T11:57:41+00:00
category: "Cybersecurity"
tags: ["trezor", "hardware-wallet", "supply-chain", "firmware", "crypto"]
source_name: "BleepingComputer"
source_url: "https://www.bleepingcomputer.com/news/cryptocurrency/trezor-confirms-crypto-stealing-implants-in-three-wallets-releases-fix/"
image: "https://upload.wikimedia.org/wikipedia/commons/4/4c/Coinkite_Coldcard_Hardware_Wallet_%2844917825622%29.png"
image_alt: "Coinkite Coldcard Hardware Wallet (44917825622)"
image_credit: "Gareth Halfacree from Bradford, UK"
image_credit_url: "https://www.flickr.com/people/120586634@N05"
image_source_url: "https://commons.wikimedia.org/w/index.php?curid=97147440"
image_license: "BY-SA 2.0"
image_license_url: "https://creativecommons.org/licenses/by-sa/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to BleepingComputer, Trezor has verified that three of its Safe 5 hardware wallets sold by the reseller CryptoBilis contained a malicious add‑on board. The extra circuit was soldered between the main board and the display, allowing it to read anything shown on the screen. When a recovery phrase or passphrase appeared, the implant captured the data, encrypted it, and attempted to push it out over a cellular connection to a server controlled by the attacker.  

The first device was reported in October after a buyer found an unauthorized board inside a Safe 5 purchased in Indonesia. Trezor could not examine the unit at that time, but a later laboratory analysis confirmed the implant’s capabilities. Photographs submitted by owners of two other wallets led the company to identify two more compromised units. All three devices were bought from CryptoBilis between late August and late September 2026.  

Trezor’s investigation also noted that similar implants have been found in Ledger wallets sold by the same reseller, linking the supply‑chain issue to previous cryptocurrency thefts. No confirmed loss of funds has been reported for the affected Trezor users, but the company warns that any recovery phrase already captured could be used by attackers.  

In response, Trezor released firmware version 2.13.1 on November 11, which adds a protection that blocks the implant from reading screen data. The update does not retroactively erase phrases that may have already been exfiltrated. Trezor also announced a dramatic cut‑back of its global reseller network—about an 80 % reduction—to limit exposure to rogue third‑party sellers.  

## Why it matters  

### Supply‑chain risk for crypto assets  
Hardware wallets are the gold standard for protecting private keys because the keys never leave the device. An implanted circuit defeats that model by turning a trusted device into a covert data‑exfiltration tool. The attack demonstrates that even reputable manufacturers can be compromised if a malicious actor gains access to the distribution chain.  

### Threat to recovery phrases  
The recovery phrase (often 12‑24 words) is the single point of failure for a wallet. If an attacker obtains it, they can recreate the wallet on any device and drain the funds. Because the implant captures the phrase at the moment it is displayed, users who entered their seed during setup or restoration were directly exposed.  

### Limited scope, but high impact  
Only three Trezor Safe 5 units have been confirmed, and they were all sold by a single reseller. Nevertheless, the technique could be replicated on larger batches or other models if the supply chain is not tightly controlled. The fact that no funds have yet been reported stolen does not diminish the risk; the stolen phrases could be used later, or the data could have been sold on underground markets.  

### Industry response  
Trezor’s swift firmware patch and reseller reduction signal a proactive stance, but the incident underscores the need for users to source hardware wallets directly from manufacturers or trusted authorized dealers. It also highlights the importance of firmware hygiene—running the latest signed firmware is now a critical mitigation step.  

## What you can do  

### 1. Verify your purchase source  

- **Buy directly** from the official Trezor website or an authorized reseller listed on the manufacturer’s site.  
- **Avoid third‑party marketplaces** that do not guarantee a sealed, untampered package.  

### 2. Update firmware immediately  

If you own a Trezor Safe 5 (or any Trezor device), run the following command in the Trezor Bridge or Trezor Suite to ensure you have the protective firmware:  

```bash
# Open Trezor Suite, go to Settings → Firmware, and follow the on‑screen prompts.
# No terminal command is required; the GUI handles verification and flashing.
```  

**Warning:** Do not interrupt the firmware flashing process. Power loss or disconnecting the device mid‑update can brick the wallet.  

### 3. Assume the recovery phrase may be compromised  

- **Generate a new wallet** on a freshly updated device.  
- **Write down a new recovery phrase** on paper (or a metal seed storage device) and store it securely offline.  
- **Transfer all assets** from the old wallet to the new one.  

### 4. Inspect the hardware (if you’re technically inclined)  

While most users won’t open their wallet, a visual inspection can reveal a foreign board between the main PCB and the display. Look for:  

- An extra thin board with solder joints not present in official teardown photos.  
- Unusual components (e.g., a tiny cellular modem chip).  

If you spot anything suspicious, discontinue use and contact Trezor support.  

### 5. Enable additional security layers  

- **Passphrase protection:** Use a hidden passphrase that is never displayed on the screen; the implant cannot capture what isn’t shown.  
- **Multi‑signature wallets:** Distribute control across multiple devices or services, reducing the impact of a single compromised wallet.  

### 6. Monitor for unusual activity  

- Regularly check transaction histories on blockchain explorers.  
- Set up alerts for outgoing transfers from your addresses.  

## Key takeaways  

- **Supply‑chain attacks can embed hardware that silently steals recovery phrases.**  
- **Trezor’s firmware 2.13.1 blocks the implant’s ability to read the screen, but it cannot erase data already taken.**  
- **Purchasing from authorized channels and keeping firmware up to date are the most effective defenses.**  
- **If you bought a Safe 5 from CryptoBilis or any unverified reseller, treat the existing recovery phrase as compromised and migrate to a new wallet.**  
- **The incident reinforces the broader lesson: hardware security is only as strong as the chain that delivers it.**
