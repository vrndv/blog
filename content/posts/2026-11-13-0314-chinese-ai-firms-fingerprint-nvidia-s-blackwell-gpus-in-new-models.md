---
title: "Chinese AI Firms Fingerprint NVIDIA’s Blackwell GPUs in New Models"
description: "Forensic study shows Chinese AI companies likely used restricted Blackwell GPUs to train recent models, raising export‑control concerns."
date: 2026-11-13T03:14:05+00:00
category: "Cybersecurity"
tags: ["ai", "exportcontrol", "nvidia", "forensics", "gpu"]
source_name: "unemploymentlabs.com"
source_url: "https://unemploymentlabs.com/checkpoint-forensics"
image: "https://upload.wikimedia.org/wikipedia/commons/c/cf/Universit%C3%A4t_T%C3%BCbingen_AI_Research_Building_Schild.jpg"
image_alt: "Universität Tübingen AI Research Building Schild"
image_credit: "Qwave"
image_credit_url: "https://commons.wikimedia.org/wiki/User:Qwave"
image_source_url: "https://commons.wikimedia.org/w/index.php?curid=172318484"
image_license: "CC0 1.0"
image_license_url: "https://creativecommons.org/publicdomain/zero/1.0/deed.en/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-20b"
---
## What happened  
A forensic investigation of publicly released AI models has uncovered evidence that several Chinese AI developers—DeepSeek, Moonshot AI, MiniMax, and Ant Group—have likely used NVIDIA’s Blackwell GPUs to train their latest language models. The analysis, conducted by researchers at Unemployment Labs, examined the numerical patterns embedded in the models’ published weights. These patterns matched the signatures of Blackwell hardware, a generation of GPUs that is subject to U.S. export controls and is not legally allowed to be shipped to China.  

The study focused on six models released since April 2026. Earlier models from the same companies were found to align with NVIDIA’s older Hopper generation, indicating a shift in hardware usage for newer releases. By reconstructing the initial random values used during training, the researchers could infer the type of GPU that produced those values. For two models—DeepSeek‑V4‑Flash and Kimi K3—the team even confirmed the match on physical Blackwell chips, strengthening the evidence that Blackwell was involved in the training process.  

The findings do not reveal how the chips were accessed, where they were located, or whether export‑control regulations were breached. They also do not prove that the training was performed on Blackwell GPUs, only that the fingerprints strongly suggest it. No U.S. licenses for exporting Blackwell GPUs to China have been reported for these companies.  

## Why it matters  
### Export controls and national security  
The U.S. government restricts the sale of advanced GPUs like Blackwell to certain countries, including China, because these chips enable cutting‑edge AI research that could have military or strategic applications. If Chinese firms are indeed using Blackwell hardware, it could indicate a loophole in the enforcement of export controls or a new method of obtaining restricted technology.  

### AI model transparency  
The study demonstrates that model weights can serve as forensic evidence of the underlying hardware. This is a powerful tool for regulators and researchers to verify compliance with export regulations and to understand the provenance of AI models. It also highlights the importance of transparency in the AI supply chain, as undisclosed hardware can undermine trust in model claims and licensing agreements.  

### Implications for the AI ecosystem  
If Chinese developers are leveraging Blackwell GPUs, they may gain a performance advantage over competitors who are restricted to older hardware. This could accelerate the pace of AI development in China and shift the balance of technological leadership. It also raises questions about how other countries enforce similar controls and whether the global AI community can rely on open‑source models as a neutral baseline.  

## What you can do  
### For developers and researchers  
- **Verify hardware fingerprints**: If you release a model, consider publishing a brief audit of the hardware used, or provide a checksum that can be cross‑checked against known GPU signatures.  
- **Use open‑source tooling**: Tools that analyze Philox seeds or other PRNG outputs can help detect the underlying hardware. Open‑source libraries for this purpose should be integrated into your model‑release pipeline.  

```bash
# Example: extract Philox seed from a PyTorch checkpoint
python -c "import torch; ckpt = torch.load('model.pt'); print(ckpt['seed'])"
```

- **Document training environments**: Maintain a clear record of the GPUs, drivers, and software versions used during training. This documentation can be shared with stakeholders to demonstrate compliance.  

### For policy makers and regulators  
- **Enhance monitoring**: Encourage or mandate the inclusion of hardware fingerprinting in export‑control compliance checks for AI models.  
- **Promote transparency**: Require companies to disclose the hardware used for training when publishing models, especially for high‑impact applications.  

### For end users and consumers  
- **Stay informed**: Pay attention to announcements from regulatory bodies about potential breaches of export controls.  
- **Demand transparency**: When choosing AI services, ask providers about the hardware used for training and inference.  

## Key takeaways  
- A forensic study found that six recent AI models from Chinese firms show hardware fingerprints matching NVIDIA’s Blackwell GPUs, which are export‑controlled.  
- The evidence comes from the models’ own weights, not from insider leaks, and includes confirmation on physical Blackwell chips for two models.  
- The analysis does not prove how the chips were accessed or whether export controls were violated, but it highlights a potential gap in enforcement.  
- Hardware fingerprinting of model weights can serve as a valuable tool for verifying compliance and ensuring transparency in the AI supply chain.  
- Stakeholders—developers, regulators, and users—can take concrete steps to document training environments, adopt forensic tools, and demand disclosure to mitigate risks associated with restricted technology.
