---
title: "MiniPG: Running a Full Postgres Server from a Single Executable"
description: "A single‑binary tool lets you use PostgreSQL like SQLite, removing the need for a separate server or Docker for local development."
date: 2026-11-21T22:04:06+00:00
category: "Tech Explained"
tags: ["postgresql", "sqlite", "self\u2011hosting", "development", "cli"]
source_name: "Lobsters"
source_url: "https://progrium.xyz/articles/2026/single-binary-postgres"
image: "https://live.staticflickr.com/3085/2432297278_94853b8760_b.jpg"
image_alt: "IMG_3355"
image_credit: "Jemimus"
image_credit_url: "https://www.flickr.com/photos/12967790@N00"
image_source_url: "https://www.flickr.com/photos/12967790@N00/2432297278"
image_license: "BY 2.0"
image_license_url: "https://creativecommons.org/licenses/by/2.0/"
draft: false
ai_assisted: true
model: "openai/gpt-oss-120b"
---
## What happened  

According to the author’s post on Lobsters, a new utility called **miniPG** packages a complete PostgreSQL server and client into one self‑contained executable. The binary works on macOS, Windows, and Linux. You invoke it much like the `sqlite3` command‑line tool: point it at a directory, and that directory becomes the database storage. The program starts an embedded PostgreSQL instance, runs the query you supplied, prints the result, and then shuts down. No background daemon, no Docker container, and no separate configuration files are required.  

The project is not a compatibility shim that pretends to be PostgreSQL; it runs the real server code compiled into the single binary. Because the data lives in ordinary files, you can back it up, copy it, or delete it just as you would with a SQLite file. The author also notes that miniPG can launch other programs with the appropriate environment variables so that those programs think they are talking to a normal PostgreSQL server, then cleanly exit when the program finishes.  

## Why it matters  

### Bridging two worlds  

SQLite’s appeal is its simplicity: a single file, no server, instant access. PostgreSQL, on the other hand, offers advanced features—concurrency control, robust extensions, sophisticated indexing, and a proven track record in production environments. Historically, developers had to choose between the ease of SQLite and the power of PostgreSQL, or they had to manage a full server stack (often via Docker) for local testing. MiniPG collapses that decision by giving the “single‑file” experience while retaining PostgreSQL’s full feature set.  

### Lowering the barrier for experimentation  

Open‑source tools that require PostgreSQL can be intimidating for newcomers who must install the server, configure users, and keep the daemon running. MiniPG lets you spin up a database in seconds, making it easier to try out new software, debug migrations, or prototype schemas without polluting your system with a long‑running service.  

### Reducing dependency churn  

When a project depends on Docker, you inherit the Docker daemon, its networking quirks, and the need for a compatible container runtime. MiniPG removes that extra layer, which is especially valuable on machines where Docker is unavailable or undesirable (e.g., low‑resource laptops, CI pipelines that avoid containers, or secure environments that restrict daemon processes).  

### Consistent data handling  

Because the data resides in a regular directory, standard backup tools (rsync, tar, cloud sync) work without special dump utilities. This aligns with the way many developers already version‑control SQLite databases for test fixtures.  

## What you can do  

### Install miniPG  

1. Download the appropriate binary for your platform from the miniPG website.  
2. Make it executable and place it in a directory that’s on your `$PATH`.  

```bash
# Example for Linux – adjust the filename as needed
chmod +x minipg-linux-amd64
sudo mv minipg-linux-amd64 /usr/local/bin/minipg
```

> **Warning:** The command above moves a file into a system directory. Ensure you trust the source and have appropriate permissions.  

### Use it like SQLite  

Create a new database directory and run a query:

```bash
mkdir mydb
minipg mydb "SELECT version();"
```

The command starts an embedded PostgreSQL instance, prints the server version, and exits. The `mydb` directory now contains the cluster’s data files.  

### Run an existing application against miniPG  

Many tools read PostgreSQL connection info from environment variables (`PGHOST`, `PGPORT`, `PGUSER`, `PGDATABASE`). MiniPG can launch a program with those variables automatically set:

```bash
minipg mydb --exec ./myapp --config ./config.yml
```

`myapp` will see a normal PostgreSQL server on a Unix socket or TCP port, interact with the database, and when it exits the embedded server shuts down.  

### Backup and restore  

Because the data lives in ordinary files, you can back it up with any file‑level tool:

```bash
tar -czf mydb-backup.tar.gz mydb
```

To restore, simply extract the archive into a fresh directory and point miniPG at it.  

### Integrate into CI pipelines  

Add a step that starts miniPG, runs your test suite, and then stops automatically:

```yaml
steps:
  - name: Test with PostgreSQL
    run: |
      minipg testdb "CREATE DATABASE test;"
      ./run-tests.sh
```

No Docker service definition is needed, keeping the pipeline lightweight.  

## Key takeaways  

- **miniPG** bundles a full PostgreSQL server and client into a single executable, eliminating the need for a separate daemon or container.  
- It offers the convenience of SQLite’s single‑file model while preserving PostgreSQL’s advanced capabilities.  
- The tool simplifies onboarding for developers, reduces system dependencies, and fits well into scripts, CI pipelines, and low‑resource environments.  
- Data is stored in a regular directory, making backup, copy, and deletion straightforward.  
- You can launch any PostgreSQL‑aware application through miniPG, letting it think it’s talking to a normal server without any lingering processes.  

By providing a “single binary PostgreSQL,” miniPG opens the door for more projects to adopt PostgreSQL’s feature set without the traditional operational overhead. Give it a try the next time you need a quick, fully‑featured database for local development or testing.
