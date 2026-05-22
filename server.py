#!/usr/bin/env python3
"""
MCP Config Generator — MCP Server by AgentPay Labs
Generate, validate, and convert MCP configuration files for Claude Desktop,
Cursor, Windsurf, and other MCP-compatible platforms.
© 2026 AgentPay Labs
"""

import json
import sys
import os
import re
from typing import Any

# ─── Rate limiting ───────────────────────────────────────────
FREE_LIMIT = 50
PRO_KEYS = {"PROL_AGENTPAY_DEMO": "demo"}
STRIPE_LINK = "https://buy.stripe.com/4gM9AVehNbg07HOcfh1oI1m"

PRO_KEY = None
for i, arg in enumerate(sys.argv):
    if arg == "--pro-key" and i + 1 < len(sys.argv):
        PRO_KEY = sys.argv[i + 1]
IS_PRO = PRO_KEY in PRO_KEYS
call_counter = 0

def check_rate_limit():
    global call_counter
    if IS_PRO:
        return None
    call_counter += 1
    if call_counter > FREE_LIMIT:
        return {
            "error": f"Free tier limit ({FREE_LIMIT} calls) reached. Upgrade to Pro for unlimited access.",
            "isError": True,
            "next_steps": [
                f"Buy Pro: {STRIPE_LINK}",
                "Restart the server to reset the counter",
                "Use --pro-key PROL_AGENTPAY_DEMO for demo access"
            ],
            "calls_used": call_counter,
            "limit": FREE_LIMIT
        }
    return None

# ─── Platform definitions ────────────────────────────────────
PLATFORMS = {
    "claude-desktop": {
        "name": "Claude Desktop",
        "config_file": "~/Library/Application Support/Claude/claude_desktop_config.json",
        "config_file_windows": "%APPDATA%/Claude/claude_desktop_config.json",
        "config_file_linux": "~/.config/Claude/claude_desktop_config.json",
        "format": "json",
        "schema": {"mcpServers": {}},
        "description": "Anthropic Claude Desktop MCP configuration"
    },
    "cursor": {
        "name": "Cursor",
        "config_file": "~/.cursor/mcp.json",
        "format": "json",
        "schema": {"mcpServers": {}},
        "description": "Cursor IDE MCP configuration"
    },
    "windsurf": {
        "name": "Windsurf",
        "config_file": "~/.codeium/windsurf/mcp.json",
        "format": "json",
        "schema": {"mcpServers": {}},
        "description": "Windsurf IDE MCP configuration"
    },
    "cline": {
        "name": "Cline (VS Code)",
        "config_file": "<VS Code settings>",
        "format": "json",
        "schema": {"mcpServers": {}},
        "description": "Cline extension for VS Code MCP configuration"
    },
    "continue": {
        "name": "Continue.dev",
        "config_file": "~/.continue/config.json",
        "format": "json",
        "schema": {"experimental": {"mcpServers": {}}},
        "description": "Continue.dev MCP configuration (nested under experimental)"
    },
    "roocode": {
        "name": "Roo Code",
        "config_file": "<Roo Code settings>",
        "format": "json",
        "schema": {"mcpServers": {}},
        "description": "Roo Code VS Code extension MCP configuration"
    },
    "claude-code": {
        "name": "Claude Code CLI",
        "config_file": "~/.claude/settings.json",
        "format": "json",
        "schema": {"mcpServers": {}},
        "description": "Anthropic Claude Code CLI MCP configuration"
    }
}

KNOWN_SERVERS = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"],
        "description": "Read/write files within allowed directories"
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"},
        "description": "GitHub API — repos, PRs, issues"
    },
    "postgres": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"],
        "description": "PostgreSQL database access"
    },
    "brave-search": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {"BRAVE_API_KEY": "<your-key>"},
        "description": "Brave Search API"
    },
    "puppeteer": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "description": "Browser automation via Puppeteer"
    },
    "memory": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"],
        "description": "Knowledge graph memory system"
    },
    "fetch": {
        "command": "uvx",
        "args": ["mcp-server-fetch"],
        "description": "Fetch and convert URLs to markdown"
    },
    "sequential-thinking": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "description": "Dynamic step-by-step reasoning"
    },
    "sqlite": {
        "command": "uvx",
        "args": ["mcp-server-sqlite", "--db-path", "/path/to/db.sqlite"],
        "description": "SQLite database access"
    }
}

CHARACTER_LIMIT = 25000


def _truncate_response(data: dict, items_key: str = "items") -> dict:
    output = json.dumps(data)
    if len(output) <= CHARACTER_LIMIT:
        return data
    items = data.get(items_key, [])
    half = max(1, len(items) // 2)
    data[items_key] = items[:half]
    data["truncated"] = True
    data["truncated_message"] = (
        f"Response truncated from {len(items)} to {half} items. "
        "Use filters or pagination to get more results."
    )
    return data


def mcp_list_platforms(response_format: str = "markdown") -> dict:
    """List all supported MCP platforms and their config locations."""
    limit_check = check_rate_limit()
    if limit_check:
        return limit_check

    platforms = []
    for key, info in PLATFORMS.items():
        platforms.append({
            "id": key,
            "name": info["name"],
            "config_file": info["config_file"],
            "format": info["format"],
            "description": info["description"]
        })

    if response_format == "json":
        return {"status": "ok", "count": len(platforms), "platforms": platforms}

    lines = ["# Supported MCP Platforms\n"]
    for p in platforms:
        lines.append(f"## {p['name']} (`{p['id']}`)")
        lines.append(f"- **Config file:** `{p['config_file']}`")
        lines.append(f"- **Format:** {p['format']}")
        lines.append(f"- {p['description']}")
        lines.append("")
    return {"status": "ok", "count": len(platforms), "markdown": "\n".join(lines)}


def mcp_generate_config(
    servers: list,
    platform: str = "claude-desktop",
    response_format: str = "markdown"
) -> dict:
    """Generate an MCP configuration for the specified platform."""
    limit_check = check_rate_limit()
    if limit_check:
        return limit_check

    if platform not in PLATFORMS:
        return {
            "status": "error",
            "isError": True,
            "error": f"Unknown platform: {platform}",
            "next_steps": [
                f"Supported platforms: {', '.join(sorted(PLATFORMS.keys()))}",
                "Use mcp_list_platforms to see all options"
            ]
        }

    platform_info = PLATFORMS[platform]

    if not servers:
        return {
            "status": "error",
            "isError": True,
            "error": "No servers provided",
            "next_steps": [
                "Provide a list of server objects with 'name', 'command', and optionally 'args' and 'env'",
                'Example: [{"name": "my-server", "command": "python3", "args": ["server.py"]}]'
            ]
        }

    # Validate each server entry
    for i, srv in enumerate(servers):
        if "name" not in srv:
            return {
                "status": "error",
                "isError": True,
                "error": f"Server at index {i} missing required 'name' field"
            }
        if "command" not in srv:
            return {
                "status": "error",
                "isError": True,
                "error": f"Server '{srv['name']}' missing required 'command' field"
            }

    # Build config
    config = {"mcpServers": {}}
    for srv in servers:
        entry = {"command": srv["command"]}
        if srv.get("args"):
            entry["args"] = srv["args"]
        if srv.get("env"):
            entry["env"] = srv["env"]
        if srv.get("disabled"):
            entry["disabled"] = True
        if srv.get("timeout"):
            entry["timeout"] = srv["timeout"]
        config["mcpServers"][srv["name"]] = entry

    # For continue.dev, nest under experimental
    if platform == "continue":
        config = {"experimental": config}

    config_json = json.dumps(config, indent=2)

    result = {
        "status": "ok",
        "platform": platform,
        "platform_name": platform_info["name"],
        "config_file": platform_info["config_file"],
        "server_count": len(servers),
        "config": config,
        "config_json": config_json
    }

    if response_format == "json":
        return result

    lines = [
        f"# MCP Config for {platform_info['name']}",
        "",
        f"**Config file:** `{platform_info['config_file']}`",
        f"**Servers configured:** {len(servers)}",
        "",
        "## Generated Config",
        "",
        "```json",
        config_json,
        "```",
        "",
        "## How to use",
        "",
        f"1. Open `{platform_info['config_file']}`",
        "2. Paste the config above (merge with existing mcpServers if present)",
        "3. Restart {platform_info['name']}",
        "",
        "## Servers in this config",
        ""
    ]
    for srv in servers:
        lines.append(f"- **{srv['name']}**: `{srv['command']}` {' '.join(srv.get('args', []))}".strip())
        if srv.get("env"):
            lines.append(f"  - Environment: {', '.join(srv['env'].keys())}")
        if srv.get("disabled"):
            lines.append("  - ⚠️ Disabled by default")
        if srv.get("timeout"):
            lines.append(f"  - Timeout: {srv['timeout']}s")

    result["markdown"] = "\n".join(lines)
    return result


def mcp_validate_config(config_json: str) -> dict:
    """Validate an existing MCP configuration JSON string."""
    limit_check = check_rate_limit()
    if limit_check:
        return limit_check

    issues = []
    warnings = []

    try:
        config = json.loads(config_json)
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "isError": True,
            "error": f"Invalid JSON: {e}",
            "next_steps": ["Fix the JSON syntax at position indicated above", "Use a JSON validator if needed"]
        }

    if not isinstance(config, dict):
        return {
            "status": "error",
            "isError": True,
            "error": "Config must be a JSON object (dict)",
            "next_steps": ["The top-level structure must be a JSON object with 'mcpServers' key"]
        }

    # Check for mcpServers key (may be nested under experimental)
    servers_config = None
    if "mcpServers" in config:
        servers_config = config["mcpServers"]
    elif "experimental" in config and isinstance(config["experimental"], dict):
        if "mcpServers" in config["experimental"]:
            servers_config = config["experimental"]["mcpServers"]
            warnings.append("mcpServers found under 'experimental' (Continue.dev format)")

    if servers_config is None:
        issues.append("Missing 'mcpServers' key at top level or 'experimental.mcpServers' for Continue.dev")
        return {
            "status": "error",
            "isError": True,
            "issues": issues,
            "warnings": warnings,
            "next_steps": [
                "Add a top-level 'mcpServers' key containing your server configs",
                "For Continue.dev, nest under 'experimental.mcpServers'"
            ]
        }

    if not isinstance(servers_config, dict):
        issues.append("'mcpServers' must be an object, not an array")
        return {
            "status": "error",
            "isError": True,
            "issues": issues,
            "warnings": warnings
        }

    valid_servers = 0
    for name, srv in servers_config.items():
        if not isinstance(srv, dict):
            issues.append(f"Server '{name}': value must be an object")
            continue
        if "command" not in srv:
            issues.append(f"Server '{name}': missing required 'command' field")
        else:
            valid_servers += 1

        if srv.get("disabled") and not isinstance(srv["disabled"], bool):
            warnings.append(f"Server '{name}': 'disabled' should be a boolean")

        if srv.get("timeout") and not isinstance(srv["timeout"], (int, float)):
            warnings.append(f"Server '{name}': 'timeout' should be a number")

    return {
        "status": "ok" if not issues else "error",
        "isError": bool(issues),
        "server_count": len(servers_config),
        "valid_servers": valid_servers,
        "issues": issues,
        "warnings": warnings,
        "verdict": "✅ Valid" if not issues else f"⚠️ {len(issues)} issue(s) found"
    }


def mcp_add_server(
    config_json: str,
    server_name: str,
    command: str,
    args: list = None,
    env: dict = None,
    disabled: bool = False,
    platform: str = "claude-desktop"
) -> dict:
    """Add a server to an existing MCP configuration."""
    limit_check = check_rate_limit()
    if limit_check:
        return limit_check

    # Parse existing config
    try:
        config = json.loads(config_json)
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "isError": True,
            "error": f"Invalid JSON in config_json: {e}"
        }

    # Find mcpServers
    servers_key = "mcpServers"
    if platform == "continue":
        if "experimental" not in config:
            config["experimental"] = {}
        if "mcpServers" not in config["experimental"]:
            config["experimental"]["mcpServers"] = {}
        servers_key = None
        target = config["experimental"]["mcpServers"]
    else:
        if "mcpServers" in config:
            target = config["mcpServers"]
        else:
            config["mcpServers"] = {}
            target = config["mcpServers"]

    if server_name in target:
        return {
            "status": "error",
            "isError": True,
            "error": f"Server '{server_name}' already exists in config",
            "next_steps": [
                "Remove the existing entry first if you want to replace it",
                "Use a different server name"
            ]
        }

    entry = {"command": command}
    if args:
        entry["args"] = args
    if env:
        entry["env"] = env
    if disabled:
        entry["disabled"] = True

    target[server_name] = entry

    new_config_json = json.dumps(config, indent=2)

    return {
        "status": "ok",
        "server_added": server_name,
        "server_count": len(target),
        "new_config": config,
        "new_config_json": new_config_json
    }


def mcp_get_server_template(
    server_id: str,
    platform: str = "claude-desktop",
    response_format: str = "markdown"
) -> dict:
    """Get a ready-to-use config snippet for a known MCP server."""
    limit_check = check_rate_limit()
    if limit_check:
        return limit_check

    if server_id not in KNOWN_SERVERS:
        similar = [k for k in KNOWN_SERVERS if server_id.lower() in k.lower()]
        return {
            "status": "error",
            "isError": True,
            "error": f"Unknown server: {server_id}",
            "next_steps": [
                f"Available servers: {', '.join(sorted(KNOWN_SERVERS.keys()))}",
                f"Similar: {similar if similar else 'none found'}",
                "Use mcp_generate_config with custom server details for unsupported servers"
            ]
        }

    if platform not in PLATFORMS:
        return {
            "status": "error",
            "isError": True,
            "error": f"Unknown platform: {platform}",
            "next_steps": [f"Supported platforms: {', '.join(sorted(PLATFORMS.keys()))}"]
        }

    server_info = KNOWN_SERVERS[server_id]
    platform_info = PLATFORMS[platform]

    config = {"mcpServers": {server_id: {"command": server_info["command"]}}}
    if server_info.get("args"):
        config["mcpServers"][server_id]["args"] = server_info["args"]
    if server_info.get("env"):
        config["mcpServers"][server_id]["env"] = server_info["env"]

    if platform == "continue":
        config = {"experimental": config}

    config_json = json.dumps(config, indent=2)

    if response_format == "json":
        return {
            "status": "ok",
            "server_id": server_id,
            "platform": platform,
            "config": config,
            "config_json": config_json,
            "description": server_info["description"]
        }

    lines = [
        f"# {server_id} MCP Template for {platform_info['name']}",
        "",
        f"**Server:** {server_id}",
        f"**Description:** {server_info['description']}",
        f"**Platform:** {platform_info['name']}",
        f"**Config file:** `{platform_info['config_file']}`",
        "",
        "## Config Snippet",
        "",
        "```json",
        config_json,
        "```",
        "",
        "## Setup",
        "",
        f"1. Copy the config above into `{platform_info['config_file']}`",
        f"2. Replace `<your-token>` and other placeholders with actual values",
        f"3. Restart {platform_info['name']}",
        ""
    ]
    if any(v for v in json.dumps(server_info) if "<your-" in str(v)):
        lines.append("⚠️ **Remember to replace placeholder values!**")

    return {"status": "ok", "markdown": "\n".join(lines)}


def mcp_batch_generate(
    server_ids: list,
    platforms: list = None,
    response_format: str = "markdown"
) -> dict:
    """Generate configs for multiple known servers across one or more platforms."""
    limit_check = check_rate_limit()
    if limit_check:
        return limit_check

    if platforms is None:
        platforms = ["claude-desktop"]

    unknown_servers = [s for s in server_ids if s not in KNOWN_SERVERS]
    if unknown_servers:
        return {
            "status": "error",
            "isError": True,
            "error": f"Unknown servers: {unknown_servers}",
            "next_steps": [
                f"Available: {', '.join(sorted(KNOWN_SERVERS.keys()))}",
                "Use mcp_generate_config for custom servers"
            ]
        }

    unknown_platforms = [p for p in platforms if p not in PLATFORMS]
    if unknown_platforms:
        return {
            "status": "error",
            "isError": True,
            "error": f"Unknown platforms: {unknown_platforms}",
            "next_steps": [f"Supported: {', '.join(sorted(PLATFORMS.keys()))}"]
        }

    results = {}
    for platform in platforms:
        servers_list = [
            {
                "name": sid,
                "command": KNOWN_SERVERS[sid]["command"],
                "args": KNOWN_SERVERS[sid].get("args"),
                "env": KNOWN_SERVERS[sid].get("env")
            }
            for sid in server_ids
        ]
        result = mcp_generate_config(servers_list, platform, response_format="json")
        results[platform] = result

    if response_format == "json":
        return {
            "status": "ok",
            "server_ids": server_ids,
            "platform_count": len(platforms),
            "platforms": results
        }

    lines = [
        "# Batch MCP Config Generation",
        "",
        f"**Servers:** {', '.join(server_ids)}",
        f"**Platforms:** {len(platforms)}",
        ""
    ]
    for plat, result in results.items():
        plat_name = PLATFORMS[plat]["name"]
        lines.append(f"## {plat_name}")
        lines.append(f"**Config file:** `{PLATFORMS[plat]['config_file']}`")
        lines.append("")
        lines.append("```json")
        lines.append(result.get("config_json", json.dumps(result.get("config", {}), indent=2)))
        lines.append("```")
        lines.append("")

    return {"status": "ok", "markdown": "\n".join(lines)}


# ─── MCP stdio server ────────────────────────────────────────
def handle_request(request: dict) -> dict:
    """Route requests to the appropriate handler."""
    method = request.get("method", "")
    req_id = request.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "mcp_list_platforms",
                        "description": "List all supported MCP platforms (Claude Desktop, Cursor, Windsurf, etc.) with their config file locations",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "response_format": {
                                    "type": "string",
                                    "enum": ["markdown", "json"],
                                    "description": "Output format (default: markdown)"
                                }
                            }
                        }
                    },
                    {
                        "name": "mcp_generate_config",
                        "description": "Generate an MCP configuration JSON for a given platform from a list of server definitions",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "servers": {
                                    "type": "array",
                                    "description": "List of server objects: [{name, command, args?, env?, disabled?, timeout?}]",
                                    "items": {"type": "object"}
                                },
                                "platform": {
                                    "type": "string",
                                    "description": "Target platform ID (default: claude-desktop)",
                                    "default": "claude-desktop"
                                },
                                "response_format": {
                                    "type": "string",
                                    "enum": ["markdown", "json"],
                                    "description": "Output format (default: markdown)",
                                    "default": "markdown"
                                }
                            },
                            "required": ["servers"]
                        }
                    },
                    {
                        "name": "mcp_validate_config",
                        "description": "Validate an existing MCP configuration JSON for correctness and completeness",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "config_json": {
                                    "type": "string",
                                    "description": "Complete MCP config JSON as a string to validate"
                                }
                            },
                            "required": ["config_json"]
                        }
                    },
                    {
                        "name": "mcp_add_server",
                        "description": "Add a new server entry to an existing MCP configuration",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "config_json": {
                                    "type": "string",
                                    "description": "Existing MCP config JSON as a string"
                                },
                                "server_name": {
                                    "type": "string",
                                    "description": "Name for the new server"
                                },
                                "command": {
                                    "type": "string",
                                    "description": "Command to run (e.g., 'npx', 'python3', 'uvx')"
                                },
                                "args": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Command arguments"
                                },
                                "env": {
                                    "type": "object",
                                    "description": "Environment variables for the server"
                                },
                                "disabled": {
                                    "type": "boolean",
                                    "description": "Whether the server starts disabled",
                                    "default": False
                                },
                                "platform": {
                                    "type": "string",
                                    "description": "Target platform (default: claude-desktop)",
                                    "default": "claude-desktop"
                                }
                            },
                            "required": ["config_json", "server_name", "command"]
                        }
                    },
                    {
                        "name": "mcp_get_server_template",
                        "description": "Get a ready-to-use config snippet for a known MCP server (filesystem, github, postgres, brave-search, etc.)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "server_id": {
                                    "type": "string",
                                    "description": "Known server ID (filesystem, github, postgres, brave-search, puppeteer, memory, fetch, sequential-thinking, sqlite)"
                                },
                                "platform": {
                                    "type": "string",
                                    "description": "Target platform (default: claude-desktop)",
                                    "default": "claude-desktop"
                                },
                                "response_format": {
                                    "type": "string",
                                    "enum": ["markdown", "json"],
                                    "default": "markdown"
                                }
                            },
                            "required": ["server_id"]
                        }
                    },
                    {
                        "name": "mcp_batch_generate",
                        "description": "Generate configs for multiple known MCP servers across one or more platforms at once",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "server_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of known server IDs to include"
                                },
                                "platforms": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Target platforms (default: ['claude-desktop'])"
                                },
                                "response_format": {
                                    "type": "string",
                                    "enum": ["markdown", "json"],
                                    "default": "markdown"
                                }
                            },
                            "required": ["server_ids"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        handlers = {
            "mcp_list_platforms": lambda: mcp_list_platforms(**arguments),
            "mcp_generate_config": lambda: mcp_generate_config(**arguments),
            "mcp_validate_config": lambda: mcp_validate_config(**arguments),
            "mcp_add_server": lambda: mcp_add_server(**arguments),
            "mcp_get_server_template": lambda: mcp_get_server_template(**arguments),
            "mcp_batch_generate": lambda: mcp_batch_generate(**arguments),
        }

        if tool_name in handlers:
            try:
                result = handlers[tool_name]()
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "isError": True,
                                "error": str(e),
                                "next_steps": [
                                    "Check the tool parameters for correctness",
                                    f"Verify all required fields are provided"
                                ]
                            }, indent=2)
                        }]
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
            }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not supported: {method}"}
        }


def main():
    """MCP stdio server main loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")


if __name__ == "__main__":
    main()
