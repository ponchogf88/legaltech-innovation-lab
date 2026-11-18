"""Structured W3C-compatible OpenTelemetry span tracing with zero-PII guardrails."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
import secrets
import time
from typing import Any

from .security import assert_synthetic_and_safe


@dataclass(frozen=True)
class TelemetrySpan:
    """Immutable OpenTelemetry-compatible span record for synthetic workflows."""

    trace_id: str
    span_id: str
    parent_span_id: str | None
    name: str
    start_time_unix_nano: int
    end_time_unix_nano: int
    duration_ms: float
    status_code: str
    attributes: dict[str, Any] = field(default_factory=dict)

    @property
    def w3c_traceparent(self) -> str:
        """Return W3C Trace Context traceparent header value (version 00, sampled)."""
        return f"00-{self.trace_id}-{self.span_id}-01"

    def to_dict(self) -> dict[str, Any]:
        """Serialize the span and W3C traceparent into JSON-safe primitives."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "start_time_unix_nano": self.start_time_unix_nano,
            "end_time_unix_nano": self.end_time_unix_nano,
            "duration_ms": self.duration_ms,
            "status_code": self.status_code,
            "attributes": dict(self.attributes),
            "w3c_traceparent": self.w3c_traceparent,
        }


class TelemetryTracer:
    """In-memory span collector enforcing PII sanitization on every span."""

    def __init__(self) -> None:
        self._spans: list[TelemetrySpan] = []
        self._active_stack: list[tuple[str, str]] = []

    @contextmanager
    def start_span(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Enter a traced span, validating attributes for synthetic-only compliance."""
        assert_synthetic_and_safe(name)
        if attributes is not None:
            assert_synthetic_and_safe(attributes)

        merged_attrs: dict[str, Any] = {
            "service.name": "legaltech-innovation-lab",
            "pii_redacted": True,
        }
        if attributes:
            merged_attrs.update(attributes)
        merged_attrs["pii_redacted"] = True

        if self._active_stack:
            trace_id, parent_span_id = self._active_stack[-1]
        else:
            trace_id = secrets.token_hex(16)
            parent_span_id = None

        span_id = secrets.token_hex(8)
        span_ctx: dict[str, Any] = {
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "attributes": merged_attrs,
        }

        start_ns = time.time_ns()
        start_perf = time.perf_counter_ns()
        status_code = "OK"
        self._active_stack.append((trace_id, span_id))
        try:
            yield span_ctx
        except Exception as exc:
            status_code = "ERROR"
            span_ctx["attributes"]["error.type"] = type(exc).__name__
            raise
        finally:
            self._active_stack.pop()
            end_ns = time.time_ns()
            elapsed_ms = round((time.perf_counter_ns() - start_perf) / 1_000_000, 4)
            final_attrs = dict(span_ctx["attributes"])
            final_attrs["pii_redacted"] = True
            assert_synthetic_and_safe(final_attrs)
            self._spans.append(
                TelemetrySpan(
                    trace_id=trace_id,
                    span_id=span_id,
                    parent_span_id=parent_span_id,
                    name=name,
                    start_time_unix_nano=start_ns,
                    end_time_unix_nano=end_ns,
                    duration_ms=elapsed_ms,
                    status_code=status_code,
                    attributes=final_attrs,
                )
            )

    def get_spans(self) -> list[TelemetrySpan]:
        """Return a snapshot list of recorded TelemetrySpan objects."""
        return list(self._spans)

    def export_spans(self) -> list[dict[str, Any]]:
        """Serialize all recorded spans as JSON-ready dictionaries."""
        return [span.to_dict() for span in self._spans]

    def clear(self) -> None:
        """Remove all recorded spans and clear any leftover stack entries."""
        self._spans.clear()
        self._active_stack.clear()


DEFAULT_TRACER = TelemetryTracer()


@contextmanager
def trace_span(
    name: str,
    attributes: dict[str, Any] | None = None,
    tracer: TelemetryTracer | None = None,
) -> Iterator[dict[str, Any]]:
    """Context manager wrapper delegating to tracer or DEFAULT_TRACER."""
    active_tracer = tracer if tracer is not None else DEFAULT_TRACER
    with active_tracer.start_span(name=name, attributes=attributes) as span_ctx:
        yield span_ctx
