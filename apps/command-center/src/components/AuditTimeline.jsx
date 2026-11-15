import React, { useMemo, useState } from 'react';
import {
  CalendarClock,
  CheckCircle2,
  Link2,
  ShieldAlert,
  ArrowDownUp,
} from 'lucide-react';
import { verifyAuditChain } from '../data/syntheticCase';

function formatUtcTimestamp(isoString) {
  if (!isoString) return '';
  return isoString.replace('T', ' ').replace(/\.\d{3}Z$/, 'Z');
}

function truncateHash(hash) {
  if (!hash) return '000000…0000';
  return `${hash.slice(0, 10)}…${hash.slice(-6)}`;
}

export function ChronosDeadlinesList({ deadlines, compact = false }) {
  return (
    <ul className={`chronos-list ${compact ? 'is-compact' : ''}`}>
      {deadlines.map((dl) => (
        <li key={dl.id} className={`chronos-item urgency-${dl.urgency}`}>
          <div className="chronos-item-top">
            <span className="chronos-title">{dl.title}</span>
            <span className={`chronos-badge urgency-${dl.urgency}`}>{dl.remaining}</span>
          </div>
          <div className="chronos-item-meta">
            <span className="mono-inline">{dl.targetDate}</span>
            <span aria-hidden="true">·</span>
            <span>{dl.owner}</span>
          </div>
        </li>
      ))}
    </ul>
  );
}

export default function AuditTimeline({ events, deadlines }) {
  const [newestFirst, setNewestFirst] = useState(true);

  const chainCheck = useMemo(() => verifyAuditChain(events), [events]);

  const orderedEvents = useMemo(() => {
    const indexed = events.map((ev, idx) => ({ ...ev, seq: idx + 1 }));
    return newestFirst ? [...indexed].reverse() : indexed;
  }, [events, newestFirst]);

  return (
    <section
      id="audit-timeline-section"
      className="right-pane-section audit-timeline"
      aria-labelledby="audit-timeline-heading"
    >
      {/* Procedural Deadlines from Chronos */}
      <div id="chronos-deadlines-section" className="chronos-subpanel">
        <div className="section-header-compact">
          <div>
            <div className="panel-eyebrow">
              <CalendarClock size={13} strokeWidth={1.75} aria-hidden="true" />
              <span>Términos Procesales (Chronos)</span>
            </div>
            <h3 className="section-title-sm">Plazos Simulados del Expediente</h3>
          </div>
          <span className="counter-pill">{deadlines.length} activos</span>
        </div>
        <ChronosDeadlinesList deadlines={deadlines} />
      </div>

      {/* Hash-Chained Audit Log from Apollō */}
      <div className="audit-subpanel">
        <div className="section-header-compact">
          <div>
            <div className="panel-eyebrow">
              <Link2 size={13} strokeWidth={1.75} aria-hidden="true" />
              <span>Bitácora Append-Only (Apollō)</span>
            </div>
            <h2 id="audit-timeline-heading" className="section-title-sm">
              Auditoría Hash-Chained ({events.length})
            </h2>
          </div>

          <div className="audit-header-controls">
            <span
              className={`chain-integrity-badge ${chainCheck.valid ? 'is-valid' : 'is-broken'}`}
              title={
                chainCheck.valid
                  ? 'Todos los entryHash verifican SHA-256 contra su prevHash'
                  : `Ruptura detectada en índice ${chainCheck.brokenIndex}`
              }
            >
              {chainCheck.valid ? (
                <>
                  <CheckCircle2 size={12} strokeWidth={2} aria-hidden="true" />
                  <span>SHA-256 Íntegra</span>
                </>
              ) : (
                <>
                  <ShieldAlert size={12} strokeWidth={2} aria-hidden="true" />
                  <span>Alerta Cadena</span>
                </>
              )}
            </span>
            <button
              type="button"
              className="btn-icon-text"
              onClick={() => setNewestFirst((prev) => !prev)}
              title="Alternar orden cronológico"
            >
              <ArrowDownUp size={12} strokeWidth={1.75} aria-hidden="true" />
              <span>{newestFirst ? 'Recientes' : 'Cronológico'}</span>
            </button>
          </div>
        </div>

        <ol className="audit-list" aria-label="Eventos encadenados por hash SHA-256">
          {orderedEvents.map((entry) => (
            <li key={entry.id} className="audit-entry">
              <div className="audit-entry-rail" aria-hidden="true">
                <span className="audit-node" />
              </div>
              <div className="audit-entry-card">
                <div className="audit-entry-top">
                  <span className="audit-action-code">
                    #{String(entry.seq).padStart(2, '0')} · {entry.action}
                  </span>
                  <span className="audit-matter-chip">{entry.matterId}</span>
                </div>

                {entry.actionLabel && (
                  <div className="audit-action-label">{entry.actionLabel}</div>
                )}

                <p className="audit-detail">{entry.detail}</p>

                <div className="audit-entry-meta">
                  <span className="audit-actor">{entry.actor}</span>
                  <time className="audit-time" dateTime={entry.timestamp}>
                    {formatUtcTimestamp(entry.timestamp)}
                  </time>
                </div>

                <div className="audit-hash-row">
                  <span
                    className="hash-badge"
                    title={`entryHash: ${entry.entryHash}\nprevHash: ${entry.prevHash}`}
                  >
                    sha256:{truncateHash(entry.entryHash)}
                  </span>
                  <span className="prev-hash-ref" title={`prevHash: ${entry.prevHash}`}>
                    prev:{entry.prevHash.slice(0, 8)}
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
