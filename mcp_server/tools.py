"""Shared MCP tool implementations (used by Cursor MCP server + Streamlit Cloud UI)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def project_status() -> dict[str, Any]:
    """Return project health: domain PDFs, env key presence, output files."""
    domain = ROOT / "Domain_documents"
    pdfs = sorted(p.name for p in domain.glob("*.pdf")) if domain.exists() else []
    traces = ROOT / "outputs" / "traces.jsonl"
    feedback = ROOT / "outputs" / "feedback.jsonl"
    return {
        "root": str(ROOT),
        "groq_api_key_set": bool(os.getenv("GROQ_API_KEY")),
        "groq_model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        "domain_pdfs": pdfs,
        "traces_exists": traces.exists(),
        "feedback_exists": feedback.exists(),
        "app_entry": "app.py",
        "mcp_surface": "streamlit+cursor",
    }


def search_domain(query: str, top_k: int = 3) -> str:
    """BM25 search over Domain_documents PDFs (healthcare RAG corpus)."""
    from rag.knowledge import retrieve_domain

    k = max(1, min(int(top_k), 8))
    return retrieve_domain(query.strip() or "healthcare EHR HIPAA", top_k=k)


def wikipedia_context(topic: str = "electronic health record", sentences: int = 4) -> str:
    """Fetch a short Wikipedia extract for a healthcare topic."""
    from rag.knowledge import fetch_wikipedia

    return fetch_wikipedia(
        topic.strip() or "electronic health record",
        sentences=max(1, min(int(sentences), 8)),
    )


def recent_feedback(limit: int = 10) -> list[dict[str, Any]]:
    """Load recent agent feedback ratings from outputs/feedback.jsonl."""
    from feedback.store import load_feedback

    return load_feedback(max(1, min(int(limit), 50)))


def recent_traces(limit: int = 5) -> list[dict[str, Any]]:
    """Load recent observability run/agent traces from outputs/traces.jsonl."""
    path = ROOT / "outputs" / "traces.jsonl"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows[-max(1, min(int(limit), 30)) :]


def list_agents() -> list[dict[str, str]]:
    """List the 5 SDLC agents and their roles."""
    from agents.crew_pipeline import AGENTS

    return [{"key": a["key"], "name": a["name"], "role": a["role"]} for a in AGENTS]
