---
title: "OpenRun 1.0 Brings Declarative GitOps for Internal Tools on Docker and Kubernetes"
description: "OpenRun 1.0 is an open‑source self‑hosted GitOps platform that lets teams declaratively deploy internal web apps with built‑in auth, RBAC and audit, on a single node or a Kubernetes cluster."
date: 2026-11-19T23:26:24+00:00
category: "Tech Explained"
tags: ["gitops", "internal-tools", "docker", "kubernetes", "authentication"]
source_name: "Lobsters"
source_url: "https://openrun.dev/blog/openrun-1.0/"
image: "https://live.staticflickr.com/3186/2759159448_17455a0fb2_b.jpg"
image_alt: "17° Server Room @ Work"
image_credit: "Leonardo Rizzi"
image_credit_url: "https://www.flickr.com/photos/29479498@N05"
image_source_url: "https://www.flickr.com/photos/29479498@N05/2759159448"
image_license: "BY-SA 2.0"
image_license_url: "https://creativecommons.org/licenses/by-sa/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to the OpenRun project blog, version 1.0 has just been released after more than three years of development, thousands of commits, and dozens of releases. OpenRun is an open‑source, self‑hosted GitOps platform designed for deploying web applications and internal tools in a declarative fashion. It can run on a single node using Docker or Podman, or scale out to a full Kubernetes cluster.  

Key features highlighted in the release notes include:  

- **Built‑in authentication and authorization** – OpenRun ships with out‑of‑the‑box support for OIDC/SAML providers and role‑based access control (RBAC) policies that govern which teams can see which apps.  
- **Auditing** – All deployment actions are recorded, giving teams a clear trail for compliance and debugging.  
- **Starlark‑based configuration** – Deployments are described in Starlark, a Python‑like language that many developers find approachable. A simple `openrun apply apps.star` command creates or updates the declared apps.  
- **Two storage back‑ends** – SQLite powers single‑node installations, while PostgreSQL is used when running on Kubernetes. No ORM layer is used, giving the developers full control over SQL queries.  
- **Hypermedia UI** – The optional console UI is built with HTMX, avoiding heavyweight JavaScript frameworks and the associated build pipelines.  

The platform was originally called “Clace” when it started in early 2023 and has been used in production by several customers. The author notes that the biggest technical hurdle was adding dynamic behavior in Go; the solution was to use the `go-plugin` system for out‑of‑process loading, accepting a small RPC overhead for greater stability.

## Why it matters  

### Declarative internal‑tool deployment  

Many organizations build internal dashboards, admin panels, or custom APIs that sit outside the main product codebase. Traditionally these tools are either:

1. **Manually deployed** – requiring ad‑hoc scripts, SSH access, or container orchestration knowledge that only a few engineers possess.  
2. **Hosted on low‑code platforms** – which provide authentication and UI scaffolding but lock you into proprietary runtimes and limit flexibility.

OpenRun bridges that gap by giving developers the same GitOps workflow used for production services—code‑driven, version‑controlled, and reproducible—while also providing the authentication, RBAC and audit capabilities that are usually only found in low‑code offerings.  

### Simplified ops for small teams  

Because OpenRun can run on a single node with SQLite, a small team can spin up a fully‑featured internal‑tool platform without provisioning a full Kubernetes cluster. When the need arises, the same configuration can be pointed at a PostgreSQL‑backed Kubernetes deployment, making scaling painless.  

### Reduced frontend complexity  

By leveraging HTMX for the console UI, OpenRun avoids pulling in large JavaScript bundles or maintaining a separate front‑end build pipeline. This reduces the attack surface (fewer dependencies) and cuts operational overhead.  

### Security‑by‑design  

- **OIDC/SAML integration** means you can reuse your existing identity provider, eliminating password sprawl.  
- **RBAC policies** are defined once in the server config and automatically apply to all apps, preventing accidental over‑exposure.  
- **Audit logs** give you visibility into who deployed what and when, supporting compliance requirements.  

## What you can do  

### 1. Try OpenRun locally  

If you want to experiment, the simplest path is a single‑node Docker deployment using SQLite. The following commands illustrate a safe, non‑destructive setup:

```bash
# Pull the latest OpenRun image
docker pull ghcr.io/openrun/openrun:latest

# Create a Docker network (optional, helps isolate the container)
docker network create openrun-net

# Run OpenRun with a persistent volume for SQLite data
docker run -d \
  --name openrun \
  --network openrun-net \
  -p 8080:8080 \
  -v $(pwd)/openrun-data:/var/lib/openrun \
  ghcr.io/openrun/openrun:latest
```

> **Warning**: The above creates a container that listens on port 8080 of your host. Ensure the port is not already in use and that you trust the image source.

### 2. Define your first app with Starlark  

Create a file named `apps.star`:

```starlark
# Example internal tool definition
app(
    name = "hello-world",
    image = "docker.io/library/nginx:alpine",
    port = 80,
)
```

Apply the configuration:

```bash
openrun apply apps.star
```

OpenRun will pull the image, create the container (or Kubernetes pod, depending on your deployment mode), and expose it according to the declared port.

### 3. Hook up your corporate identity provider  

OpenRun’s server configuration supports OIDC and SAML. A minimal OIDC snippet looks like:

```yaml
auth:
  oidc:
    issuer: https://login.mycompany.com/
    client_id: openrun
    client_secret: <redacted>
    redirect_uri: https://openrun.mycompany.com/callback
```

Place this in `server.yaml` and restart the service. Users will now be redirected to your corporate login page before accessing any app.

### 4. Enforce RBAC  

Define role policies in the same `server.yaml`:

```yaml
rbac:
  roles:
    - name: engineering
      apps: ["*"]          # engineers can see all apps
    - name: finance
      apps: ["billing", "reports"]
```

Assign users to roles via the OIDC groups claim or manually in the OpenRun UI. This ensures that only authorized teams can launch particular internal tools.

### 5. Move to Kubernetes when you’re ready  

When you outgrow a single node, switch the metadata store to PostgreSQL and point OpenRun at your cluster:

```yaml
metadata:
  backend: postgres
  dsn: "postgres://openrun:password@db-host/openrun?sslmode=disable"
kubernetes:
  context: my‑cluster
```

After updating the config, restart OpenRun and re‑apply your `apps.star`. OpenRun will translate the declarative definitions into Kubernetes resources (Deployments, Services, etc.) automatically.

## Key takeaways  

- **OpenRun 1.0** offers a GitOps‑style workflow for internal tools, combining the flexibility of code‑first deployments with enterprise‑grade auth, RBAC and audit.  
- **Starlark** provides a familiar, Python‑like syntax for declaring apps, lowering the learning curve for developers.  
- **Single‑node or Kubernetes** deployments are supported out of the box, letting teams start small and grow without re‑architecting.  
- **Built‑in OIDC/SAML** integration lets you reuse existing identity providers, reducing credential sprawl and simplifying compliance.  
- **Hypermedia UI** built with HTMX keeps the front‑end lightweight and reduces dependency risk.  

If you’re managing a suite of internal dashboards, admin panels, or custom APIs, OpenRun gives you a unified, secure, and declarative platform to bring those services under the same GitOps umbrella used for your production workloads. Give it a spin, integrate it with your identity provider, and let your teams focus on building value instead of wrestling with ad‑hoc deployment scripts.
