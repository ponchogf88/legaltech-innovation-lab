import React, { useMemo, useState } from 'react';
import { Columns, Cpu, Feather, Landmark, ScrollText, Sparkles } from 'lucide-react';
import { COUNCIL_JURISTS, HISTORICAL_STRATA } from '../data/syntheticCase';

export default function HallOfJuristsPanel({ onInvokeJurist }) {
  const [activeStratumId, setActiveStratumId] = useState('STRATUM_II');
  const [selectedJuristId, setSelectedJuristId] = useState('ulpiano');
  const [lastInvokedSummary, setLastInvokedSummary] = useState(null);

  const activeStratum = useMemo(
    () => HISTORICAL_STRATA.find((s) => s.id === activeStratumId) || HISTORICAL_STRATA[1],
    [activeStratumId]
  );

  const stratumJurists = useMemo(
    () => COUNCIL_JURISTS.filter((j) => j.stratumId === activeStratum.id),
    [activeStratum.id]
  );

  const activeJurist = useMemo(
    () => stratumJurists.find((j) => j.id === selectedJuristId) || stratumJurists[0],
    [stratumJurists, selectedJuristId]
  );

  function handleSelectStratum(stratumId) {
    setActiveStratumId(stratumId);
    const firstInStratum = COUNCIL_JURISTS.find((j) => j.stratumId === stratumId);
    if (firstInStratum) {
      setSelectedJuristId(firstInStratum.id);
    }
  }

  function handleInvoke() {
    if (!activeJurist) return;
    onInvokeJurist(activeJurist, activeStratum);
    setLastInvokedSummary({
      juristName: activeJurist.name,
      provider: activeJurist.preferredProvider,
      stratum: activeStratum.tabLabel,
      seal: activeJurist.sealLabel,
      brief: activeJurist.briefSample,
    });
  }

  return (
    <section
      id="hall-of-jurists-section"
      className={`panel-card hall-of-jurists-panel ${activeStratum.themeClass}`}
      aria-labelledby="hall-of-jurists-heading"
    >
      <div className="panel-header">
        <div>
          <div className="panel-eyebrow">
            <Landmark size={14} strokeWidth={1.75} aria-hidden="true" />
            <span>El Salón de los Pensadores · La Escuela de Atenas</span>
          </div>
          <h2 id="hall-of-jurists-heading" className="panel-title">
            Consejo de Jurisconsultos y Enrutador Multi-Modelo
          </h2>
        </div>

        <span
          className="zero-anachronism-badge"
          title="Regla estética: respeto estricto de época y motivo visual por estrato"
        >
          <Columns size={13} strokeWidth={1.75} aria-hidden="true" />
          <span>Regla: Cero Anacronismos</span>
        </span>
      </div>

      {/* 4 Canonical Strata Tabs */}
      <div className="strata-tabs" role="tablist" aria-label="Los 4 Estratos Históricos">
        {HISTORICAL_STRATA.map((stratum) => {
          const isSelected = stratum.id === activeStratum.id;
          return (
            <button
              key={stratum.id}
              type="button"
              role="tab"
              aria-selected={isSelected}
              className={`stratum-tab ${isSelected ? 'is-selected' : ''}`}
              onClick={() => handleSelectStratum(stratum.id)}
            >
              <span className="stratum-roman">{stratum.tabLabel}</span>
            </button>
          );
        })}
      </div>

      {/* Active Stratum Epoch Banner */}
      <div className="stratum-epoch-banner">
        <div className="stratum-epoch-head">
          <strong>{activeStratum.title}</strong>
          <span className="stratum-visual-tag">{activeStratum.visualStyle}</span>
        </div>
        <p className="stratum-epoch-rule">{activeStratum.epochRule}</p>
      </div>

      {/* Jurist Roster Selector within Stratum */}
      <div className="jurist-chips-row" role="group" aria-label="Jurisconsultos del estrato activo">
        {stratumJurists.map((jurist) => {
          const isCurrent = jurist.id === activeJurist?.id;
          return (
            <button
              key={jurist.id}
              type="button"
              className={`jurist-chip ${isCurrent ? 'is-active' : ''}`}
              aria-pressed={isCurrent}
              onClick={() => setSelectedJuristId(jurist.id)}
            >
              <span>{jurist.name}</span>
            </button>
          );
        })}
      </div>

      {/* Active Jurist Dossier & Smart Multi-Model Router Telemetry */}
      {activeJurist && (
        <div className="jurist-dossier-grid">
          <article className="jurist-sheet-card">
            <div className="jurist-sheet-top">
              <span className="jurist-seal-badge">
                <Feather size={12} strokeWidth={1.75} aria-hidden="true" />
                <span>{activeJurist.sealLabel}</span>
              </span>
              <span className="jurist-phase-chip">{activeJurist.phase}</span>
            </div>
            <h3 className="jurist-name">{activeJurist.name}</h3>
            <p className="jurist-subtitle">{activeJurist.title}</p>
            <p className="jurist-superpower">{activeJurist.superpower}</p>
            <div className="jurist-brief-box">
              <span className="jurist-brief-label">
                <ScrollText size={12} strokeWidth={1.75} aria-hidden="true" />
                <span>Criterio Preliminar (Requiere Validación Humana)</span>
              </span>
              <p className="jurist-brief-text">{activeJurist.briefSample}</p>
            </div>
          </article>

          <aside className="router-telemetry-card" aria-label="Smart Multi-Model Router">
            <div className="router-card-eyebrow">
              <Cpu size={13} strokeWidth={1.75} aria-hidden="true" />
              <span>Smart Multi-Model Router</span>
            </div>
            <div className="router-provider-name">{activeJurist.preferredProvider}</div>
            <div className="router-model-tier mono-inline">{activeJurist.preferredModelLabel}</div>
            <dl className="router-meta-list">
              <div>
                <dt>Ruta de Tarea</dt>
                <dd className="mono-inline">{activeJurist.taskKind}</dd>
              </div>
              <div>
                <dt>Perfil de Costo</dt>
                <dd>{activeJurist.costTier}</dd>
              </div>
              <div>
                <dt>Privacidad</dt>
                <dd>Sintético · Cero PII</dd>
              </div>
            </dl>
            <button type="button" className="btn btn-primary btn-sm jurist-invoke-btn" onClick={handleInvoke}>
              <Sparkles size={14} strokeWidth={1.75} aria-hidden="true" />
              <span>Invocar Dictamen en Bitácora</span>
            </button>
          </aside>
        </div>
      )}

      {lastInvokedSummary && (
        <div className="callout callout-sage jurist-invoked-banner" role="status">
          <Sparkles size={16} strokeWidth={1.75} aria-hidden="true" />
          <div>
            <strong>
              Dictamen preliminar de {lastInvokedSummary.juristName} ({lastInvokedSummary.stratum})
            </strong>
            <p className="callout-body">
              Enrutado vía <span className="mono-inline">{lastInvokedSummary.provider}</span> · Sello:{' '}
              {lastInvokedSummary.seal} — Evento encadenado a la bitácora SHA-256 (sujeto a revisión humana).
            </p>
          </div>
        </div>
      )}
    </section>
  );
}
