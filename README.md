# 🔧 MCP Config Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![npm](https://img.shields.io/npm/v/@rumblingb/mcp-config-generator)](https://www.npmjs.com/package/@rumblingb/mcp-config-generator)
[![Smithery](https://img.shields.io/badge/Smithery-Deploy-blue)](https://smithery.ai/server/@rumblingb/mcp-config-generator)

**Generate, validate, and convert MCP configuration files for every MCP-compatible platform.** Built by [AgentPay Labs](https://github.com/Rumblingb).

> Your AI agent can now manage MCP server configs without touching JSON. Generate configs for Claude Desktop, Cursor, Windsurf, and more — all from natural language.

---

## ✨ Features

- **6 tools** for complete MCP config management
- **7 platforms** supported: Claude Desktop, Cursor, Windsurf, Cline, Continue.dev, Roo Code, Claude Code CLI
- **9+ popular server templates** pre-configured
- **Zero dependencies beyond Python stdlib** — no API keys needed
- **Offline-capable** — all generation happens locally
- **Rate limiting built-in** — Free: 50 calls/session, Pro: unlimited ($19/mo)
- **Dual response format** — markdown (human) and JSON (programmatic)

---

## 🛠 Tools

| Tool | Description |
|------|-------------|
| `mcp_generate_config` | Generate MCP config JSON for any platform from server definitions |
| `mcp_list_platforms` | List all supported platforms with config file locations |
| `mcp_validate_config` | Validate existing MCP config for errors and warnings |
| `mcp_add_server` | Add a server to an existing config |
| `mcp_get_server_template` | Get pre-configured templates for 9+ popular MCP servers |
| `mcp_batch_generate` | Generate configs for multiple servers across multiple platforms |

---

## 📦 Installation

```bash
# Clone
git clone https://github.com/Rumblingb/mcp-config-generator.git
cd mcp-config-generator

# Install
pip install -r requirements.txt
```

## 🚀 Quick Start

### As an MCP Server

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mcp-config-generator": {
      "command": "python3",
      "args": ["/path/to/mcp-config-generator/server.py"]
    }
  }
}
```

### Example: Generate a Config

Ask your agent:

> "Use mcp-config-generator to create a Claude Desktop config with the filesystem, github, and postgres servers."

The agent will call `mcp_batch_generate` with `server_ids: ["filesystem", "github", "postgres"]` and return a complete, validated JSON config.

### Example: Validate a Config

> "Validate my MCP config: [paste JSON]"

The agent calls `mcp_validate_config` and returns issues, warnings, and a verdict.

---

## 💰 Pricing

| Tier | Price | Limits |
|------|-------|--------|
| **Free** | $0 | 50 calls per session (resets on restart) |
| **Pro** | **$19/mo** | Unlimited calls, priority support |

[⬆️ Upgrade to Pro →](https://buy.stripe.com/4gM9AVehNbg07HOcfh1oI1m)

---

## 🔌 Supported Platforms

| Platform | Config File | Notes |
|----------|------------|-------|
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` | macOS default |
| **Cursor** | `~/.cursor/mcp.json` | |
| **Windsurf** | `~/.codeium/windsurf/mcp.json` | |
| **Cline (VS Code)** | VS Code settings | |
| **Continue.dev** | `~/.continue/config.json` | Nested under `experimental.mcpServers` |
| **Roo Code** | VS Code settings | |
| **Claude Code CLI** | `~/.claude/settings.json` | |

### Pre-configured Server Templates

| Server | Command | Description |
|--------|---------|-------------|
| `filesystem` | `npx @modelcontextprotocol/server-filesystem` | File system access |
| `github` | `npx @modelcontextprotocol/server-github` | GitHub API |
| `postgres` | `npx @modelcontextprotocol/server-postgres` | PostgreSQL database |
| `brave-search` | `npx @modelcontextprotocol/server-brave-search` | Web search |
| `puppeteer` | `npx @modelcontextprotocol/server-puppeteer` | Browser automation |
| `memory` | `npx @modelcontextprotocol/server-memory` | Knowledge graph |
| `fetch` | `uvx mcp-server-fetch` | URL fetching |
| `sequential-thinking` | `npx @modelcontextprotocol/server-sequential-thinking` | Reasoning |
| `sqlite` | `uvx mcp-server-sqlite` | SQLite database |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────┐
│                 AI Agent                         │
│  "Generate a config for Claude Desktop with      │
│   filesystem, github, and brave-search"          │
└──────────────────┬───────────────────────────────┘
                   │ MCP stdio
                   ▼
┌──────────────────────────────────────────────────┐
│           MCP Config Generator                    │
│                                                  │
│  ┌─────────────┐  ┌──────────────┐              │
│  │ Generate    │  │ Validate     │              │
│  │ Config      │  │ Config       │              │
│  └─────────────┘  └──────────────┘              │
│  ┌─────────────┐  ┌──────────────┐              │
│  │ List        │  │ Add Server   │              │
│  │ Platforms   │  │ to Config    │              │
│  └─────────────┘  └──────────────┘              │
│  ┌─────────────┐  ┌──────────────┐              │
│  │ Server      │  │ Batch        │              │
│  │ Templates   │  │ Generate     │              │
│  └─────────────┘  └──────────────┘              │
│                                                  │
│  Pure Python stdlib — zero network calls         │
└──────────────────────────────────────────────────┘
```

---

## 📄 API Reference

### `mcp_generate_config`

Generate a complete MCP config JSON from server definitions.

```
servers: [{name, command, args?, env?, disabled?, timeout?}]
platform: "claude-desktop" | "cursor" | "windsurf" | ...
response_format: "markdown" | "json"
```

### `mcp_validate_config`

Validate an existing MCP config JSON string.

```
config_json: string
```

### `mcp_add_server`

Add a single server to an existing config.

```
config_json: string
server_name: string
command: string
args?: string[]
env?: object
disabled?: boolean
platform?: string
```

### `mcp_get_server_template`

Get a ready-to-use config snippet for a known server.

```
server_id: "filesystem" | "github" | "postgres" | ...
platform?: string
response_format?: "markdown" | "json"
```

### `mcp_batch_generate`

Generate configs for multiple servers across multiple platforms.

```
server_ids: string[]
platforms?: string[]
response_format?: "markdown" | "json"
```

---

## 🧪 Quality Standards

- ✅ **Service-prefixed naming**: `mcp_generate_config`, `mcp_validate_config`
- ✅ **Dual response format**: Markdown for humans, JSON for agents
- ✅ **Pagination contract**: Paginated results with `total`, `count`, `offset`, `has_more`
- ✅ **CHARACTER_LIMIT truncation**: Auto-truncates at 25K chars
- ✅ **Error as result**: Errors returned inside tool response, never thrown
- ✅ **Rate limiting**: Free tier with Stripe upgrade path
- ✅ **Tool annotations**: readOnlyHint, destructiveHint, idempotentHint, openWorldHint

---

## 🔗 Related Products

- [MCP Server Directory](https://rumblingb.github.io/mcp-server-directory/) — 60+ MCP servers
- [AgentPay Labs](https://github.com/Rumblingb) — All products

---

## 📄 License

MIT — © 2026 AgentPay Labs
