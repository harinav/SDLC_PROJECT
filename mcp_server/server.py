"""Cursor MCP server for Healthcare SDLC Automation.

Transports:
  - stdio (default) — Cursor launches this via .cursor/mcp.json
  - http  — optional: set MCP_TRANSPORT=http (local / non-Streamlit hosts)

Streamlit Community Cloud cannot expose this MCP protocol endpoint (single
Streamlit port only). The same tools run in the cloud app UI via mcp_server.tools.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from mcp_server import tools as T

load_dotenv(ROOT / ".env", override=False)

_mcp_host = os.getenv("MCP_HOST", "127.0.0.1")
_mcp_port = int(os.getenv("MCP_PORT", "8765"))
mcp = FastMCP("sdlc-internal", host=_mcp_host, port=_mcp_port)


@mcp.tool()
def project_status() -> dict:
    """Return project health: domain PDFs, env key presence, output files."""
    return T.project_status()


@mcp.tool()
def search_domain(query: str, top_k: int = 3) -> str:
    """BM25 search over Domain_documents PDFs (healthcare RAG corpus)."""
    return T.search_domain(query, top_k)


@mcp.tool()
def wikipedia_context(topic: str = "electronic health record", sentences: int = 4) -> str:
    """Fetch a short Wikipedia extract for a healthcare topic."""
    return T.wikipedia_context(topic, sentences)


@mcp.tool()
def recent_feedback(limit: int = 10) -> list:
    """Load recent agent feedback ratings from outputs/feedback.jsonl."""
    return T.recent_feedback(limit)


@mcp.tool()
def recent_traces(limit: int = 5) -> list:
    """Load recent observability run/agent traces from outputs/traces.jsonl."""
    return T.recent_traces(limit)


@mcp.tool()
def list_agents() -> list:
    """List the 5 SDLC agents and their roles."""
    return T.list_agents()


def main() -> None:
    transport = (os.getenv("MCP_TRANSPORT") or "stdio").strip().lower()
    if transport in {"http", "streamable-http"}:
        mcp.run(transport="streamable-http")
    elif transport == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
