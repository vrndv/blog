---
title: "Cutting the Cord: Running a Coway Air Purifier Without the Cloud"
description: "Learn how to replace a proprietary IoT cloud link with a local, Home Assistant‑based control for a Wi‑Fi air purifier."
date: 2026-11-14T02:56:17+00:00
category: "Tech Explained"
tags: ["iot", "home-assistant", "air-purifier", "privacy", "linux"]
source_name: "scottjg.com"
source_url: "https://scottjg.com/posts/2026-11-11-reverse-engineering-my-coway-air-purifier-to-ditch-the-cloud/"
image: "https://live.staticflickr.com/7552/15330239274_bb10623ab5_b.jpg"
image_alt: "Internet of Things 2014 Conference"
image_credit: "datainnovation"
image_credit_url: "https://www.flickr.com/photos/115593373@N04"
image_source_url: "https://www.flickr.com/photos/115593373@N04/15330239274"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

A homeowner in the Bay Area relied on a Coway Airmega IconS air purifier to filter smoke from seasonal wildfires and to provide white‑noise at night. The unit is Wi‑Fi enabled and ships with a proprietary iPhone app that talks to Coway’s cloud service. An enthusiast reverse‑engineered that app and created a Home Assistant integration that mimics the phone, allowing the fan to be controlled from Apple Home.  

While the integration works, it still depends on Coway’s remote servers for status and commands. The author noticed that the cloud link occasionally fails and worries that the service may eventually be discontinued or turned into a paid feature. To regain full control, they set out to “ditch the cloud” by intercepting the device’s network traffic and handling it locally.  

## Why it matters  

### Privacy and reliability  

IoT devices that route every command through a vendor’s cloud expose usage patterns and device identifiers to an external party. If the service goes down, the device becomes effectively unusable for automation. By moving control to a local hub, you eliminate that dependency and keep data inside your trusted network.  

### Longevity of discontinued hardware  

Manufacturers often stop supporting older models, leaving owners with “bricked” smart features. A local integration extends the useful life of the hardware, reducing electronic waste and saving money.  

### Learning opportunity  

The process of reverse‑engineering the communication protocol, setting up a man‑in‑the‑middle (MitM) proxy, and re‑implementing the API provides practical experience with TLS inspection, packet capture, and Home Assistant custom components—skills that are valuable for any Linux‑oriented hobbyist or security‑conscious user.  

## What you can do  

Below is a high‑level roadmap for replicating this approach with any Wi‑Fi‑enabled air purifier that talks to a cloud endpoint. Adjust the specifics to match your device’s network behavior.  

### 1. Capture the traffic  

1. Connect a laptop to the same Wi‑Fi network as the purifier.  
2. Install `tcpdump` or `Wireshark`.  
3. Run a capture filtered to the purifier’s IP address, e.g.:  

```bash
# Replace 192.168.1.42 with your device’s address
sudo tcpdump -i wlan0 host 192.168.1.42 -w capture.pcap
```  

Let the official app perform a few actions (turn fan on/off, change speed). Stop the capture and open the `.pcap` file in Wireshark. Look for TLS handshakes and HTTP/HTTPS requests that contain JSON payloads describing commands or status.  

> **Warning**: Do not modify the purifier’s firmware or flash unsigned binaries. The steps below only observe existing traffic.  

### 2. Set up a local TLS‑terminating proxy  

Because the device validates the server’s certificate, you need a proxy that can present a trusted certificate. The easiest way is to generate a self‑signed CA, install it on the purifier (if the device allows custom CA bundles), and run `mitmproxy` as the endpoint.  

```bash
# Install mitmproxy (Debian/Ubuntu)
sudo apt-get update && sudo apt-get install -y mitmproxy

# Generate a new CA (mitmproxy does this automatically on first run)
mitmproxy --mode transparent --showhost
```  

Configure your router to redirect all outbound traffic from the purifier’s IP to the machine running `mitmproxy` (usually via DNAT or port‑forward rules). On many home routers this can be done with a simple “Port Forward” entry pointing port 443 to the proxy’s IP.  

### 3. Decode the API  

With the proxy in place, the purifier’s HTTPS requests will be decrypted and displayed by `mitmproxy`. Examine the request paths, headers, and JSON bodies. Typical actions include:  

- `GET /device/status` – returns current fan speed, filter life, AQI.  
- `POST /device/control` – payload `{ "mode": "auto", "speed": 3 }`.  

Document each endpoint and the required fields.  

### 4. Implement a local service  

Write a tiny Python script that mimics the cloud API and forwards commands to the purifier. Use Flask (or FastAPI) to expose the same routes the original cloud used, but have the handler send the captured JSON directly to the device over its local IP.  

```python
# local_coway_proxy.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
DEVICE_IP = "192.168.1.42"
CLOUD_BASE = f"https://{DEVICE_IP}"

@app.route("/device/status", methods=["GET"])
def status():
    resp = requests.get(f"{CLOUD_BASE}/device/status", verify=False)
    return jsonify(resp.json())

@app.route("/device/control", methods=["POST"])
def control():
    payload = request.json
    resp = requests.post(f"{CLOUD_BASE}/device/control", json=payload, verify=False)
    return jsonify(resp.json())

if __name__ == "__main__":
    # Run on port 443 with a self‑signed cert (generated separately)
    app.run(host="0.0.0.0", port=443, ssl_context=("cert.pem", "key.pem"))
```  

> **Safety note**: The script disables TLS verification (`verify=False`) only because the device uses a self‑signed cert inside your LAN. In a production setup, you should add the generated CA to the system’s trust store.  

### 5. Bridge to Home Assistant  

Home Assistant can call any REST endpoint via its `rest_command` or a custom integration. Add entries like:  

```yaml
rest_command:
  coway_set_speed:
    url: "https://{{ local_proxy_ip }}/device/control"
    method: post
    payload: '{"speed": {{ speed }}}'
    headers:
      Content-Type: application/json
```  

Create automations that trigger on the “Good Night” scene to set the desired fan speed.  

### 6. Verify and harden  

- Test the automation repeatedly to ensure the proxy stays reachable.  
- Lock down the proxy machine with a firewall that only allows connections from your LAN.  
- Keep the self‑signed CA private; do not expose the proxy to the internet.  

## Key takeaways  

- **Local control beats cloud lock‑in** – By intercepting and reproducing the vendor’s API, you regain autonomy over a smart appliance.  
- **TLS inspection is feasible** – Generating a custom CA and using a transparent proxy lets you view encrypted IoT traffic without flashing firmware.  
- **Home Assistant is a flexible bridge** – Its REST command integration can speak to any locally hosted service, making it ideal for DIY IoT rewiring.  
- **Future‑proofing matters** – Even discontinued devices can stay functional with a modest amount of reverse‑engineering and scripting.  

Taking these steps not only restores reliable automation for your air purifier but also sharpens your Linux networking and security skills—valuable tools for any modern home tech enthusiast.
