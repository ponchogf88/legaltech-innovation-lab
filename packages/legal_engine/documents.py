"""Jinja2 document rendering with StrictUndefined for synthetic legal templates."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .authorities import KNOWN_AUTHORITIES
from .models import Document, Matter

DEFAULT_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"

TEMPLATES: dict[str, str] = {
    "solicitud_general": "solicitud_general.j2",
    "escrito_presentacion": "escrito_presentacion.j2",
}


class DocumentRenderError(ValueError):
    """Raised when template selection or template rendering fails."""


def render_document(
    matter: Matter,
    template_key: str = "solicitud_general",
    templates_dir: Path | str = DEFAULT_TEMPLATES_DIR,
    document_id: str | None = None,
) -> Document:
    """Render a synthetic legal document for a Matter using Jinja2 StrictUndefined."""
    if template_key not in TEMPLATES:
        raise DocumentRenderError(
            f"Unknown template_key '{template_key}'. Expected one of: {sorted(TEMPLATES)}"
        )

    template_filename = TEMPLATES[template_key]
    templates_path = Path(templates_dir)
    if not templates_path.is_dir():
        raise DocumentRenderError(f"Templates directory does not exist: {templates_path}")

    env = Environment(
        loader=FileSystemLoader(str(templates_path)),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_filename)

    authority_label = KNOWN_AUTHORITIES.get(matter.authority, matter.authority)
    filing_date_str = matter.filing_date.isoformat() if matter.filing_date else "POR DEFINIR"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    rendered = template.render(
        matter=matter,
        matter_id=matter.id,
        client_name=matter.client_name,
        matter_type=matter.matter_type,
        authority=matter.authority,
        authority_label=authority_label,
        facts=matter.facts,
        documents_needed=matter.documents_needed,
        filing_date=filing_date_str,
        generated_at=generated_at,
        watermark="[DOCUMENTO SINTÉTICO — DEMO ÚNICAMENTE]",
    )

    resolved_doc_id = (
        document_id.strip()
        if isinstance(document_id, str) and document_id.strip()
        else f"DOC-{uuid4().hex[:8].upper()}"
    )

    return Document(
        id=resolved_doc_id,
        matter_id=matter.id,
        template_name=template_filename,
        content=rendered,
    )
