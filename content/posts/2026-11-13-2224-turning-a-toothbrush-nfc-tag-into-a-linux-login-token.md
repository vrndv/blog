---
title: "Turning a Toothbrush NFC Tag into a Linux Login Token"
description: "Learn how a replaceable electric‑toothbrush head’s NFC chip can be repurposed to unlock a Linux desktop, with a step‑by‑step guide and security tips."
date: 2026-11-13T22:24:59+00:00
category: "Cybersecurity"
tags: ["nfc", "linux", "authentication", "esp32", "hardware\u2011hacking"]
source_name: "Hackaday"
source_url: "https://hackaday.com/2026/11/13/using-a-toothbrushs-nfc-chip-to-unlock-a-computer/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

A recent Hackaday article described how the replaceable heads of some electric toothbrushes embed an NXP NTAG213 NFC tag. The tag stores data such as brush type, total runtime and pressure metrics, which the toothbrush handle reads to provide usage statistics.  

Using a cheap PN532 NFC reader attached to an ESP32‑S3 microcontroller, the author demonstrated that the tag’s memory can be both read and written. After extracting the NFC antenna from the brush head—a process the article notes is “quite easy”—the author programmed the tag to act as a credential for unlocking an Apple MacBook. While the MacBook example is niche, the underlying technique works with any system that can accept NFC‑based keyboard‑wedge input, including Linux desktops.  

The key take‑away is that a toothbrush head can become a low‑cost, reusable NFC token once its original data is overwritten.  

## Why it matters  

### Re‑using everyday hardware for security  

NFC tags are common in contactless payment cards, transit passes and access badges. Their ubiquity makes them a convenient factor for two‑factor authentication (2FA) or password‑less login. However, buying dedicated NFC cards can be costly for hobbyists or small teams. Repurposing a toothbrush head provides a free source of NTAG213 tags, each with a 144‑byte user memory area that can store a custom identifier.  

### Open‑source, hardware‑based login  

Linux already supports NFC login through tools like `pam_nfc` and `libnfc`. By pairing an NFC tag with a PAM (Pluggable Authentication Module) configuration, users can replace a password prompt with a simple tap of the toothbrush chip. This reduces the attack surface associated with typed passwords—no keyloggers, no shoulder surfing.  

### Security considerations  

While convenient, NFC tags are inherently low‑security if the stored identifier is static. An attacker who can skim the tag could replay the credential. Therefore, the token should be used **in conjunction** with another factor (e.g., a PIN, a TPM‑bound challenge, or a time‑based one‑time password). Additionally, because the toothbrush chip is removable, physical security of the token is critical; treat it like a physical key.  

## What you can do  

Below is a practical workflow for turning a toothbrush NFC chip into a Linux login token on a Fedora‑based system. The steps assume basic familiarity with the command line and a willingness to flash firmware onto an ESP32‑S3 board.  

### 1. Gather the hardware  

| Item | Why you need it |
|------|-----------------|
| Electric toothbrush with replaceable heads (NTAG213 confirmed) | Source of the NFC tag |
| PN532 NFC reader module | Reads/writes the tag |
| ESP32‑S3 development board | Hosts the reader and runs the firmware |
| Small screwdriver or tweezers | To detach the antenna from the brush head |
| USB cable (micro‑USB or USB‑C) | Connect ESP32 to your PC |

All of these components are inexpensive and widely available from electronics hobby stores.  

### 2. Extract the NFC antenna  

1. Remove the brush head from the toothbrush handle.  
2. Locate the small rectangular chip (the NTAG213) and the surrounding copper antenna.  
3. Using tweezers, gently pry the antenna away from the plastic housing. The chip remains attached to the antenna; do not apply force that could bend the leads.  

> **Safety note:** The brush head is a personal hygiene item. Keep the extracted antenna separate from the bristles and wash your hands after handling.  

### 3. Wire the PN532 to the ESP32‑S3  

The PN532 can operate over I²C or SPI; I²C is simpler for this use case. Connect as follows (ESP32‑S3 pins may vary by board):  

```c
// Wiring diagram (I2C)
// PN532   ESP32‑S3
// VCC  →  3.3V
// GND  →  GND
// SDA  →  GPIO21
// SCL  →  GPIO22
```

### 4. Flash firmware that emulates a keyboard wedge  

A “keyboard wedge” presents NFC tag data as keystrokes to the host computer. The open‑source project **NFC‑Keyboard-Emu** (available on GitHub) includes an ESP32‑S3 example.  

```bash
# Install ESP-IDF (skip if already installed)
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh
source export.sh

# Clone the keyboard emulation repo
git clone https://github.com/example/NFC-Keyboard-Emu.git
cd NFC-Keyboard-Emu

# Build and flash
idf.py set-target esp32s3
idf.py menuconfig   # optional: adjust UART pins, log level
idf.py build
idf.py -p /dev/ttyUSB0 flash
```

The firmware reads the NFC tag’s UID and sends it as a string followed by an “Enter” key press.  

### 5. Program the toothbrush tag with a unique identifier  

Use the PN532 in “write” mode from a simple Python script that leverages `pynfc`.  

```python
#!/usr/bin/env python3
import nfc

def on_connect(tag):
    # Replace with a random 8‑character string
    payload = b'brush01'
    tag.ndef.message = nfc.ndef.Message(nfc.ndef.Record('urn:nfc:wkt:T', payload))
    print("Tag written")
    return False

clf = nfc.ContactlessFrontend('usb')
clf.connect(rdwr={'on-connect': on_connect})
```

Run the script while the tag is placed on the PN532 reader. The NFC chip now holds the string `brush01`.  

### 6. Install PAM support for NFC on Linux  

On Fedora, the `pam_nfc` package provides a PAM module that validates NFC tag data against a local whitelist.  

```bash
sudo dnf install pam_nfc
```

Edit `/etc/pam.d/gdm-password` (or the PAM file for your display manager) to add the module before the password check:  

```text
auth    sufficient      pam_nfc.so
auth    required        pam_unix.so try_first_pass
```

Create a whitelist file that maps the tag’s UID or payload to a user account:  

```bash
sudo mkdir -p /etc/pam_nfc
echo "brush01:yourusername" | sudo tee /etc/pam_nfc/whitelist
```

Set appropriate permissions:  

```bash
sudo chmod 600 /etc/pam_nfc/whitelist
sudo chown root:root /etc/pam_nfc/whitelist
```

### 7. Test the login flow  

1. Reboot or log out to the GDM login screen.  
2. Tap the toothbrush NFC tag on the PN532 reader (the ESP32 will forward the string as keystrokes).  
3. If the identifier matches the whitelist, PAM will grant access without prompting for a password.  

If the tag is not recognized, the system falls back to the normal password prompt, preserving access.  

### 8. Harden the setup  

- **Rotate identifiers**: Periodically re‑write the tag with a new random string and update the whitelist.  
- **Combine with a PIN**: Configure PAM to require a short numeric PIN after NFC validation (`auth required pam_unix.so`).  
- **Lock down the USB port**: Prevent unauthorized devices from injecting keystrokes by disabling USB mass‑storage on the login console.  

## Key takeaways  

- Many electric toothbrush heads contain an NTAG213 NFC tag that can be read and rewritten with inexpensive hardware (PN532 + ESP32‑S3).  
- By extracting the antenna and programming a unique identifier, the tag can serve as a low‑cost NFC credential for Linux login.  
- Linux’s PAM framework, together with `pam_nfc`, enables password‑less authentication while still allowing a fallback to passwords.  
- Security best practices—rotating secrets, adding a secondary factor, and protecting physical access—are essential to keep the convenience from becoming a liability.  

Repurposing a toothbrush’s NFC chip is a fun illustration of how everyday objects can become part of a personal security toolkit. With a few dollars of hardware and a modest amount of configuration, you can replace a typed password with a tap of a toothbrush head—just remember to treat that tiny chip with the same care you would a traditional access badge.
