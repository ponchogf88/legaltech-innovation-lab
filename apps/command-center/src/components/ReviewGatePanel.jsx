import React, { useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  FileCheck2,
  Lock,
  RotateCcw,
  Send,
  ShieldAlert,
  ShieldCheck,
  UserCheck,
  XCircle,
} from 'lucide-react';
import { REVIEW_GATE_STAGES } from '../data/syntheticCase';

export default function ReviewGatePanel({
  caseData,
  gateState,
  lawyerName,
  onLawyerNameChange,
  validatedCount,
  totalEvidenceCount,
  onSendToReview,
  onApprove,
  onReject,
  onSubmitMock,
  onConfirmReceiptIfSubmitted,
  onResetCycle,
  apiSyncStatus,
}) {
  const [rejectionReason, setRejectionReason] = useState('');
  const [formError, setFormError] = useState('');

  const currentStageIndex = REVIEW_GATE_STAGES.findIndex((s) => s.key === gateState.status);
  const isApproved = gateState.status === 'APPROVED';
  const isSubmitted = gateState.status === 'SUBMITTED';
  const isReceipted = gateState.status === 'RECEIPTED';
  const canSubmitMock = isApproved;

  function handleSendToReviewClick() {
    setFormError('');
    onSendToReview();
  }

  function handleApproveClick() {
    const cleanedName = lawyerName.trim();
    if (!cleanedName) {
      setFormError('Ingresa el nombre del abogado/a responsable antes de aprobar.');
      return;
    }
    setFormError('');
    onApprove(cleanedName);
  }

  function handleRejectClick() {
    const cleanedReason = rejectionReason.trim();
    if (!cleanedReason) {
      setFormError('El motivo de rechazo es obligatorio para devolver el escrito a DRAFT.');
      return;
    }
    const reviewer = lawyerName.trim() || 'Abogado/a Revisor/a (Simulado)';
    setFormError('');
    onReject(cleanedReason, reviewer);
    setRejectionReason('');
  }

  return (
    <section id="review-gate-section" className="panel-card review-gate-panel" aria-labelledby="review-gate-heading">
      <div className="panel-header">
        <div>
          <div className="panel-eyebrow">
            <ShieldCheck size={14} strokeWidth={1.75} aria-hidden="true" />
            <span>Compuerta Human-in-the-Loop (Nomos)</span>
          </div>
          <h2 id="review-gate-heading" className="panel-title">
            Control de Revisión y Emisión Mock
          </h2>
        </div>
        <div className="panel-header-badges">
          <span className={`gate-state-badge state-${gateState.status.toLowerCase()}`}>
            {gateState.status}
          </span>
          {apiSyncStatus?.label && (
            <span className={`sync-pill sync-${apiSyncStatus.mode}`} title={apiSyncStatus.detail}>
              {apiSyncStatus.label}
            </span>
          )}
        </div>
      </div>

      {/* 5-Stage State Stepper */}
      <ol className="gate-stepper" aria-label="Estados de la compuerta de revisión">
        {REVIEW_GATE_STAGES.map((stage, idx) => {
          const isCompleted = idx < currentStageIndex || isReceipted;
          const isCurrent = idx === currentStageIndex && !isReceipted;
          return (
            <li
              key={stage.key}
              className={`gate-step ${isCurrent ? 'is-current' : ''} ${isCompleted ? 'is-done' : ''}`}
            >
              <span className="step-index">
                {isCompleted ? <CheckCircle2 size={14} strokeWidth={2} aria-hidden="true" /> : idx + 1}
              </span>
              <span className="step-text">
                <span className="step-code">{stage.label}</span>
                <span className="step-desc">{stage.description}</span>
              </span>
            </li>
          );
        })}
      </ol>

      {/* Last Rejection Banner when returned to DRAFT */}
      {gateState.lastRejection && gateState.status === 'DRAFT' && (
        <div className="callout callout-crimson" role="status">
          <XCircle size={18} strokeWidth={1.75} aria-hidden="true" />
          <div>
            <strong>Devuelto a DRAFT por rechazo humano</strong>
            <p className="callout-body">
              Motivo: &ldquo;{gateState.lastRejection.reason}&rdquo; — Registrado por{' '}
              <span className="mono-inline">{gateState.lastRejection.rejectedBy}</span>.
            </p>
          </div>
        </div>
      )}

      {/* SubmissionBlockedError Guard Banner */}
      {!isApproved && !isSubmitted && !isReceipted && (
        <div className="callout callout-guard" role="note">
          <ShieldAlert size={18} strokeWidth={1.75} aria-hidden="true" />
          <div>
            <strong>Protección SubmissionBlockedError Activa</strong>
            <p className="callout-body">
              La presentación ante <span className="mono-inline">{caseData.authority}</span> está
              bloqueada por código hasta que un abogado/a ingrese su nombre y firme la transición a{' '}
              <span className="mono-inline">APPROVED</span>.
            </p>
          </div>
        </div>
      )}

      {/* Evidence validation advisory */}
      {validatedCount < totalEvidenceCount && !isReceipted && (
        <div className="callout callout-amber">
          <AlertTriangle size={16} strokeWidth={1.75} aria-hidden="true" />
          <span>
            Recomendación de Themis: <strong>{validatedCount} de {totalEvidenceCount}</strong> piezas
            probatorias validadas manualmente en el panel derecho.
          </span>
        </div>
      )}

      {/* Stage-specific Controls */}
      <div className="gate-workspace">
        {gateState.status === 'DRAFT' && (
          <div className="gate-stage-box">
            <p className="stage-instruction">
              El escrito sintético está en etapa de edición (<span className="mono-inline">DRAFT</span>).
              Envíalo a revisión humana para habilitar la firma del abogado/a o el rechazo documentado.
            </p>
            <div className="gate-actions-row">
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleSendToReviewClick}
              >
                <FileCheck2 size={16} strokeWidth={1.75} aria-hidden="true" />
                <span>Enviar a Revisión (IN_REVIEW)</span>
              </button>
              <button
                type="button"
                className="btn btn-submit-mock"
                disabled
                aria-disabled="true"
                title="Bloqueado por SubmissionBlockedError: requiere estado APPROVED"
              >
                <Lock size={15} strokeWidth={1.75} aria-hidden="true" />
                <span>Emitir / Presentar (Mock)</span>
              </button>
            </div>
          </div>
        )}

        {gateState.status === 'IN_REVIEW' && (
          <div className="gate-stage-box">
            <div className="form-grid">
              <div className="field-group">
                <label htmlFor="hitl-lawyer-name" className="field-label">
                  Abogado/a Responsable de la Validación Nominal
                </label>
                <input
                  id="hitl-lawyer-name"
                  type="text"
                  className="text-input"
                  value={lawyerName}
                  onChange={(e) => {
                    onLawyerNameChange(e.target.value);
                    if (formError) setFormError('');
                  }}
                  placeholder="Ej. Lic. Valeria Mendoza (Simulado)"
                />
                <span className="field-helper">
                  El nombre quedará registrado de forma inmutable en la bitácora SHA-256.
                </span>
              </div>

              <div className="field-group">
                <label htmlFor="hitl-rejection-reason" className="field-label">
                  Motivo de Rechazo (obligatorio únicamente si se devuelve a DRAFT)
                </label>
                <input
                  id="hitl-rejection-reason"
                  type="text"
                  className="text-input"
                  value={rejectionReason}
                  onChange={(e) => {
                    setRejectionReason(e.target.value);
                    if (formError) setFormError('');
                  }}
                  placeholder="Ej. Ajustar cuantía sintética o cotejar Anexo ANX-SINT-02"
                />
              </div>
            </div>

            {formError && (
              <p className="inline-error" role="alert">
                {formError}
              </p>
            )}

            <div className="gate-actions-row">
              <button
                type="button"
                className="btn btn-sage"
                onClick={handleApproveClick}
              >
                <UserCheck size={16} strokeWidth={1.75} aria-hidden="true" />
                <span>Aprobar como Abogado/a</span>
              </button>

              <button
                type="button"
                className="btn btn-danger-outline"
                onClick={handleRejectClick}
              >
                <XCircle size={16} strokeWidth={1.75} aria-hidden="true" />
                <span>Rechazar (Devolver a DRAFT)</span>
              </button>

              <button
                type="button"
                className="btn btn-submit-mock"
                disabled
                aria-disabled="true"
                title="Bloqueado por SubmissionBlockedError: primero haz clic en Aprobar como Abogado/a"
              >
                <Lock size={15} strokeWidth={1.75} aria-hidden="true" />
                <span>Emitir / Presentar (Mock)</span>
              </button>
            </div>
          </div>
        )}

        {gateState.status === 'APPROVED' && (
          <div className="gate-stage-box">
            <div className="callout callout-sage">
              <CheckCircle2 size={18} strokeWidth={1.75} aria-hidden="true" />
              <div>
                <strong>Aprobación Nominal Registrada ({gateState.approvedBy})</strong>
                <p className="callout-body">
                  La protección <span className="mono-inline">SubmissionBlockedError</span> ha sido
                  levantada. Ya puedes emitir la promoción hacia{' '}
                  <span className="mono-inline">{caseData.authority}</span>.
                </p>
              </div>
            </div>

            <div className="gate-actions-row">
              <button
                type="button"
                className="btn btn-primary"
                disabled={!canSubmitMock}
                onClick={onSubmitMock}
              >
                <Send size={16} strokeWidth={1.75} aria-hidden="true" />
                <span>Emitir / Presentar (Mock)</span>
              </button>
            </div>
          </div>
        )}

        {gateState.status === 'SUBMITTED' && (
          <div className="gate-stage-box">
            <div className="callout callout-amber">
              <Send size={18} strokeWidth={1.75} aria-hidden="true" />
              <div>
                <strong>Despacho en curso hacia Tribunal Virtual (Simulado — MOCK)</strong>
                <p className="callout-body">
                  Promoción transmitida por <span className="mono-inline">{gateState.approvedBy}</span>.
                  Esperando sello de acuse simulado.
                </p>
              </div>
            </div>
            {onConfirmReceiptIfSubmitted && (
              <div className="gate-actions-row">
                <button type="button" className="btn btn-sage" onClick={onConfirmReceiptIfSubmitted}>
                  <CheckCircle2 size={16} strokeWidth={1.75} aria-hidden="true" />
                  <span>Generar Acuse Mock</span>
                </button>
              </div>
            )}
          </div>
        )}

        {gateState.status === 'RECEIPTED' && (
          <div className="gate-stage-box">
            <div className="receipt-folio-card" role="status">
              <div className="receipt-folio-header">
                <span className="receipt-badge">
                  <CheckCircle2 size={16} strokeWidth={2} aria-hidden="true" />
                  <span>ACUSE SIMULADO EMITIDO</span>
                </span>
                <span className="receipt-authority">{caseData.authority}</span>
              </div>
              <div className="receipt-folio-code">{gateState.receiptFolio}</div>
              <p className="receipt-folio-meta">
                Aprobado por <strong>{gateState.approvedBy}</strong> · Expediente{' '}
                <span className="mono-inline">{caseData.caseId}</span> · Evento registrado en la
                bitácora append-only SHA-256.
              </p>
            </div>

            <div className="gate-actions-row">
              <button type="button" className="btn btn-ghost" onClick={onResetCycle}>
                <RotateCcw size={15} strokeWidth={1.75} aria-hidden="true" />
                <span>Nuevo Ciclo de Simulación (Mantiene Bitácora)</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
