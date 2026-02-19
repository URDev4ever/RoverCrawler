<h1 align="center">RoverCrawler 🕷️🚀</h1>
<p align="center">
  🇺🇸 <a href="README.md"><b>English</b></a> |
  🇪🇸 <a href="README_ES.md">Español</a>
</p>
<p align="center">
  <img width="498" height="214" alt="image-removebg-preview (43)" src="https://github.com/user-attachments/assets/ae86bcac-179c-4b62-add8-79dc082d94de" />
</p>
<h2 align="center">Single-file web crawler for site structure mapping</h2>

<h3 align="center">
  RoverCrawler is a single-file Python web crawler designed to explore websites and generate a tree-mapped representation of their structure.
  It supports interactive mode, command-line usage, colored tree output, rate limiting, and exporting results — all without external project scaffolding.
</h3>

> Built for clarity, portability, and controlled crawling.

---

## ✨ Features

* 📄 **Single Python file** (`rovercrawler.py`)
* 🌳 **Tree-based site structure mapping** (default output)
* 🎨 **Subtle colored output** (cross-platform via `colorama`)
* 🧭 **Interactive configuration mode**
* 🖥️ **Full CLI support (argparse)**
* 🔍 **Domain-restricted crawling** (optional external links)
* 🛑 **Safety limits** (max depth & max pages)
* ⏱️ **Rate limiting** to avoid hammering servers
* 📊 **Crawl statistics** (pages, links, errors, speed)
* 📦 **Export results** to:

  * JSON
  * Plain text
* 💻 **Cross-platform** (Windows / Linux / macOS)

---

## 🖥️ Installation

Just clone this repository: (you NEED `git` installed for you to be able to clone it)

```bash
git clone https://github.com/URDev4ever/RoverCrawler.git
cd RoverCrawler/
```

---

## 📦 Requirements

Python **3.8+** recommended.

External dependencies (install once):

```bash
pip install requests beautifulsoup4 colorama
```

---

## 🚀 Usage

### 1️⃣ Interactive Mode (recommended for manual scans)

Just run the script without arguments:

```bash
python rovercrawler.py
```

You will be prompted to configure:

* Target URL
* Max crawl depth
* Max pages
* Verbose mode
* External link following

---

### 2️⃣ Command-Line Mode (CLI)

Basic usage:

```bash
python rovercrawler.py https://example.com
```

With options:

```bash
python rovercrawler.py https://example.com -d 4 -p 200 -v --external
```

---

## ⚙️ Command-Line Options

| Option               | Description                           |
| -------------------- | ------------------------------------- |
| `url`                | Target URL to crawl                   |
| `-d`, `--depth`      | Maximum crawl depth                   |
| `-p`, `--pages`      | Maximum pages to crawl                |
| `-v`, `--verbose`    | Enable verbose output                 |
| `-e`, `--external`   | Follow external (out-of-domain) links |
| `-t`, `--timeout`    | Request timeout (seconds)             |
| `--export-json FILE` | Export results as JSON                |
| `--export-txt FILE`  | Export results as plain text          |
| `--no-banner`        | Disable ASCII banner                  |
| `--no-colors`        | Disable colored output                |

---

## 🌳 Output Example (Tree View)

```
/
├── /about
│   ├── /team
│   └── /history
├── /blog
│   ├── /post-1
│   └── /post-2
└── /contact
```

* Internal links are shown in **cyan**
* External links (if enabled) are marked and colored **yellow**
* Output is depth-aware and loop-safe

---

## 📤 Exporting Results

### Export to JSON

```bash
python rovercrawler.py https://example.com --export-json results.json
```

The JSON preserves the **tree structure**, ideal for post-processing or visualization.

---

### Export to Plain Text

```bash
python rovercrawler.py https://example.com --export-txt results.txt
```

* Colors are automatically stripped
* Includes crawl metadata and statistics

---

## 📊 Crawl Statistics

At the end of each crawl, RoverCrawler reports:

* Pages crawled
* Links discovered
* Errors encountered
* Total time elapsed
* Average crawl speed (pages/sec)

Example:

```
Pages crawled: 87
Links found:  412
Errors:       2
Time elapsed: 12.4 seconds
Avg speed:    7.0 pages/sec
```

---

## 🧠 Technical Notes

* Uses **BFS (Breadth-First Search)** for predictable tree depth
* Normalizes URLs (scheme, domain, path)
* Skips common binary/static file extensions
* Ignores fragments, mailto, javascript, tel links
* Enforces rate limiting per request
* Uses a single `requests.Session()` for efficiency

---

## ⚠️ Disclaimer

RoverCrawler is intended for **educational, research, and legitimate testing purposes**.
Always respect:

* Website terms of service
* `robots.txt`
* Applicable local laws

You are responsible for how you use this tool.

---

## ⭐ Contributing

Pull requests are welcome if they:

* Improve crawling reliability, URL normalization, or tree-structure accuracy without introducing aggressive behavior
* Enhance performance, rate limiting logic, or export capabilities while keeping the project single-file and clean
* Maintain the controlled, respectful crawling philosophy (no exploitation, no bypass techniques, no evasion features)

---
Made with <3 by URDev.
