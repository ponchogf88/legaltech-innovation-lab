import React, { useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  FileSearch,
  Flag,
  Fingerprint,
  Scale,
} from 'lucide-react';

const STATUS_META = {
  PENDING: { label: 'Pendiente', badgeClass: 'ev-badge-pending' },
  VALIDATED: { label: 'Validado', badgeClass: 'ev-badge-validated' },
  FLAGGED: { label: 'Observado', badgeClass: 'ev-badge-flagged' },
};

export default function EvidenceInspector({ evidenceItems, onUpdateValidation }) {
  const [selectedId, setSelectedId] = useState(evidenceItems[0]?.id || '');
  const activeItem =
    evidenceItems.find((item) => item.id === selectedId) || evidenceItems[0];

  if (!activeItem) return null;

  const validatedCount = evidenceItems.filter(
    (item) => item.validationStatus === 'VALIDATED'
  ).length;
  const activeStatusMeta = STATUS_META[activeItem.validationStatus] || STATUS_META.PENDING;

  return (
    <section
      id="evidence-inspector-section"
      className="right-pane-section evidence-inspector"
      aria-labelledby="evidence-inspector-heading"
    >
      <div className="section-header-compact">
        <div>
          <div className="panel-eyebrow">
            <FileSearch size={13} strokeWidth={1.75} aria-hidden="true" />
            <span>Inspector Probatorio (Themis)</span>
          </div>
          <h2 id="evidence-inspector-heading" className="section-title-sm">
            Piezas Documentales Sintéticas
          </h2>
        </div>
        <span className="counter-pill">
          {validatedCount}/{evidenceItems.length} validadas
        </span>
      </div>

      {/* Document selector tabs */}
      <div className="evidence-tabs" role="tablist" aria-label="Anexos documentales sintéticos">
        {evidenceItems.map((item) => {
          const isSelected = item.id === activeItem.id;
          return (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={isSelected}
              title={item.title}
              className={`evidence-tab ${isSelected ? 'is-selected' : ''} status-${item.validationStatus.toLowerCase()}`}
              onClick={() => setSelectedId(item.id)}
            >
              <span className={`ev-dot status-${item.validationStatus.toLowerCase()}`} aria-hidden="true" />
              <span className="ev-tab-short">{item.shortLabel}</span>
            </button>
          );
        })}
      </div>

      {/* Active piece metadata */}
      <div className="evidence-doc-meta">
        <div className="evidence-doc-title-row">
          <h3 className="evidence-doc-title">{activeItem.title}</h3>
          <span className={`ev-status-pill ${activeStatusMeta.badgeClass}`}>
            {activeStatusMeta.label}
          </span>
        </div>
        <div className="evidence-doc-submeta">
          <span>{activeItem.folio}</span>
          <span aria-hidden="true">·</span>
          <span>{activeItem.sourceType}</span>
        </div>
        <div className="evidence-hash-line" title={activeItem.documentHash}>
          <Fingerprint size={12} strokeWidth={1.75} aria-hidden="true" />
          <span>{activeItem.documentHash.slice(0, 26)}…</span>
        </div>
      </div>

      {/* Card 1: Hecho Verificable Extraído */}
      <article className="epistemic-card epistemic-fact" aria-label="1. Hecho Verificable Extraído">
        <header className="epistemic-header">
          <span className="epistemic-index">1. Hecho Verificable Extraído</span>
          <span className="epistemic-tag tag-fact">Hecho Extraído (Factual)</span>
        </header>
        <p className="epistemic-body">{activeItem.extractedFact}</p>
        <footer className="epistemic-footer">
          <span className="epistemic-source">Fuente verificable: {activeItem.factSourceRef}</span>
        </footer>
      </article>

      {/* Card 2: Análisis / Conclusión Jurídica (No vinculante) */}
      <article
        className="epistemic-card epistemic-conclusion"
        aria-label="2. Análisis / Conclusión Jurídica (No vinculante)"
      >
        <header className="epistemic-header">
          <span className="epistemic-index">2. Análisis / Conclusión Jurídica (No vinculante)</span>
          <span className="epistemic-tag tag-conclusion">
            Conclusión Jurídica Preliminar (Requiere Validación)
          </span>
        </header>
        <p className="epistemic-body">{activeItem.preliminaryConclusion}</p>
        <footer className="epistemic-footer epistemic-caution">
          <AlertTriangle size={13} strokeWidth={1.75} aria-hidden="true" />
          <span>{activeItem.legalCaution}</span>
        </footer>
      </article>

      {/* Human Validation Status Toggle */}
      <div className="evidence-validation-bar" aria-label="Control de validación humana">
        <div className="validation-bar-label">
          <Scale size={13} strokeWidth={1.75} aria-hidden="true" />
          <span>Validación Humana de Pieza</span>
        </div>
        <div className="validation-toggle-group" role="group" aria-label="Estado de validación">
          <button
            type="button"
            className={`val-toggle-btn ${activeItem.validationStatus === 'VALIDATED' ? 'is-active-validated' : ''}`}
            aria-pressed={activeItem.validationStatus === 'VALIDATED'}
            onClick={() => onUpdateValidation(activeItem.id, 'VALIDATED')}
          >
            <CheckCircle2 size={14} strokeWidth={1.75} aria-hidden="true" />
            <span>Validar</span>
          </button>
          <button
            type="button"
            className={`val-toggle-btn ${activeItem.validationStatus === 'FLAGGED' ? 'is-active-flagged' : ''}`}
            aria-pressed={activeItem.validationStatus === 'FLAGGED'}
            onClick={() => onUpdateValidation(activeItem.id, 'FLAGGED')}
          >
            <Flag size={14} strokeWidth={1.75} aria-hidden="true" />
            <span>Observar</span>
          </button>
          <button
            type="button"
            className={`val-toggle-btn ${activeItem.validationStatus === 'PENDING' ? 'is-active-pending' : ''}`}
            aria-pressed={activeItem.validationStatus === 'PENDING'}
            onClick={() => onUpdateValidation(activeItem.id, 'PENDING')}
          >
            <span>Pendiente</span>
          </button>
        </div>
        {activeItem.validatedBy && (
          <p className="validation-attribution">
            Última marca por <span className="mono-inline">{activeItem.validatedBy}</span>
          </p>
        )}
      </div>
    </section>
  );
}
