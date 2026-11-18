import React, { useMemo, useState } from 'react';
import {
  CalendarClock,
  Code2,
  Eye,
  FileCode2,
  Lock,
  Menu,
  Scale,
  Server,
  ShieldCheck,
  X,
} from 'lucide-react';
import AgentConstellation from './components/AgentConstellation';
import AuditTimeline, { ChronosDeadlinesList } from './components/AuditTimeline';
import EvidenceInspector from './components/EvidenceInspector';
import HallOfJuristsPanel from './components/HallOfJuristsPanel';
import LegalAcademyPanel from './components/LegalAcademyPanel';
import ReviewGatePanel from './components/ReviewGatePanel';
import {
  AGENTS,
  CHRONOS_DEADLINES,
  INITIAL_AUDIT_EVENTS,
  INITIAL_EVIDENCE,
  INITIAL_LEGAL_COURSES,
  SYNTHETIC_CASE,
  appendHashChainedEvent,
  buildDraftDocumentPreview,
} from './data/syntheticCase';

const FOCUS_SECTION_IDS = {
  evidence: 'evidence-inspector-section',
  draft: 'draft-preview-section',
  gate: 'review-gate-section',
  deadlines: 'chronos-deadlines-section',
  audit: 'audit-timeline-section',
};

export default function App() {
  const [activeAgentId, setActiveAgentId] = useState('nomos');
  const [mobileRailOpen, setMobileRailOpen] = useState(false);
  const [draftViewMode, setDraftViewMode] = useState('document'); // 'document' | 'bindings'
  const [lawyerName, setLawyerName] = useState('');

  const [evidenceItems, setEvidenceItems] = useState(INITIAL_EVIDENCE);
  const [auditEvents, setAuditEvents] = useState(INITIAL_AUDIT_EVENTS);
  const [legalCourses, setLegalCourses] = useState(INITIAL_LEGAL_COURSES);

  const [gateState, setGateState] = useState({
    status: 'DRAFT',
    approvedBy: null,
    approvedAt: null,
    lastRejection: null,
    receiptFolio: null,
    submissionCount: 0,
  });

  const [apiSyncStatus, setApiSyncStatus] = useState({
    mode: 'local',
    label: 'Sandbox Local',
    detail: 'Operando en modo cliente sintético sin dependencia de backend.',
  });

  const validatedCount = useMemo(
    () => evidenceItems.filter((item) => item.validationStatus === 'VALIDATED').length,
    [evidenceItems]
  );

  const draftPreview = useMemo(
    () => buildDraftDocumentPreview(SYNTHETIC_CASE, gateState, evidenceItems),
    [gateState, evidenceItems]
  );

  async function optionalSyncTransition(payload) {
    if (apiSyncStatus.mode !== 'connected') return;
    try {
      await fetch('/api/review-gate/transition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          matterId: SYNTHETIC_CASE.caseId,
          ...payload,
        }),
      });
    } catch {
      setApiSyncStatus({
        mode: 'local',
        label: 'Sandbox Local',
        detail: 'Backend :8790 no disponible; el estado continúa validado localmente.',
      });
    }
  }

  async function handleToggleApiSync() {
    if (apiSyncStatus.mode === 'connected') {
      setApiSyncStatus({
        mode: 'local',
        label: 'Sandbox Local',
        detail: 'Modo local activo (sin llamadas externas).',
      });
      return;
    }

    setApiSyncStatus({
      mode: 'checking',
      label: 'Verificando :8790…',
      detail: 'Consultando proxy opcional /api/health en 127.0.0.1:8790.',
    });

    try {
      const response = await fetch('/api/health', { method: 'GET' });
      if (response.ok) {
        setApiSyncStatus({
          mode: 'connected',
          label: 'API :8790 Conectada',
          detail: 'Sincronización opcional activa con backend local.',
        });
      } else {
        setApiSyncStatus({
          mode: 'local',
          label: 'Sandbox Local',
          detail: `Proxy /api respondió ${response.status}; se mantiene modo local sintético.`,
        });
      }
    } catch {
      setApiSyncStatus({
        mode: 'local',
        label: 'Sandbox Local',
        detail: 'Backend :8790 no detectado; el entorno local sintético funciona de forma autónoma.',
      });
    }
  }

  function handleNavigateFocus(targetKey) {
    const elementId = FOCUS_SECTION_IDS[targetKey];
    if (!elementId) return;
    const targetEl = document.getElementById(elementId);
    if (targetEl) {
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function handleSelectAgent(agentId) {
    setActiveAgentId(agentId);
    setMobileRailOpen(false);
  }

  function handleSendToReview() {
    if (gateState.status !== 'DRAFT') return;
    setGateState((prev) => ({
      ...prev,
      status: 'IN_REVIEW',
    }));
    setAuditEvents((prev) =>
      appendHashChainedEvent(prev, {
        actor: 'Dike · Redacción',
        action: 'REVIEW_REQUESTED',
        actionLabel: 'Borrador enviado a compuerta de revisión humana',
        matterId: SYNTHETIC_CASE.caseId,
        stage: 'IN_REVIEW',
        detail: 'Promoción solicitud_general.j2 lista para validación nominal de abogado/a.',
      })
    );
    optionalSyncTransition({ toStatus: 'IN_REVIEW', actor: 'Dike' });
  }

  function handleApprove(cleanedLawyerName) {
    if (gateState.status !== 'IN_REVIEW') return;
    const now = new Date().toISOString();
    setGateState((prev) => ({
      ...prev,
      status: 'APPROVED',
      approvedBy: cleanedLawyerName,
      approvedAt: now,
      lastRejection: null,
    }));
    setAuditEvents((prev) =>
      appendHashChainedEvent(prev, {
        actor: cleanedLawyerName,
        action: 'HUMAN_APPROVAL_GRANTED',
        actionLabel: 'Aprobación nominal firmada en compuerta HITL',
        matterId: SYNTHETIC_CASE.caseId,
        stage: 'APPROVED',
        detail: `Protección SubmissionBlockedError liberada por ${cleanedLawyerName}.`,
      })
    );
    optionalSyncTransition({ toStatus: 'APPROVED', actor: cleanedLawyerName });
  }

  function handleReject(reason, reviewer) {
    if (gateState.status !== 'IN_REVIEW') return;
    const now = new Date().toISOString();
    setGateState((prev) => ({
      ...prev,
      status: 'DRAFT',
      approvedBy: null,
      approvedAt: null,
      lastRejection: {
        reason,
        rejectedBy: reviewer,
        rejectedAt: now,
      },
    }));
    setAuditEvents((prev) =>
      appendHashChainedEvent(prev, {
        actor: reviewer,
        action: 'HUMAN_REVIEW_REJECTED',
        actionLabel: 'Promoción rechazada y devuelta a DRAFT',
        matterId: SYNTHETIC_CASE.caseId,
        stage: 'DRAFT',
        detail: `Motivo registrado: ${reason}`,
      })
    );
    optionalSyncTransition({ toStatus: 'DRAFT', actor: reviewer, reason });
  }

  function handleSubmitMock() {
    // Defense in depth: mirror backend SubmissionBlockedError invariant on client
    if (gateState.status !== 'APPROVED' || !gateState.approvedBy) {
      return;
    }

    const nextCount = gateState.submissionCount + 1;
    const folio = `MOCK-TV-${SYNTHETIC_CASE.caseId}-${String(nextCount).padStart(3, '0')}`;
    const approver = gateState.approvedBy;

    setGateState((prev) => ({
      ...prev,
      status: 'RECEIPTED',
      receiptFolio: folio,
      submissionCount: nextCount,
    }));

    setAuditEvents((prev) => {
      const afterSubmit = appendHashChainedEvent(prev, {
        actor: approver,
        action: 'MOCK_SUBMISSION_DISPATCHED',
        actionLabel: 'Emisión enviada a autoridad simulada',
        matterId: SYNTHETIC_CASE.caseId,
        stage: 'SUBMITTED',
        detail: `Promoción transmitida a ${SYNTHETIC_CASE.authority} tras aprobación de ${approver}.`,
      });
      return appendHashChainedEvent(afterSubmit, {
        actor: SYNTHETIC_CASE.authority,
        action: 'MOCK_RECEIPT_ISSUED',
        actionLabel: 'Acuse sintético generado con folio oficial mock',
        matterId: SYNTHETIC_CASE.caseId,
        stage: 'RECEIPTED',
        detail: `Folio de acuse simulado: ${folio}.`,
      });
    });

    optionalSyncTransition({ toStatus: 'RECEIPTED', actor: approver, receiptFolio: folio });
  }

  function handleResetCycle() {
    setGateState((prev) => ({
      ...prev,
      status: 'DRAFT',
      approvedBy: null,
      approvedAt: null,
      lastRejection: null,
      receiptFolio: null,
    }));
    setAuditEvents((prev) =>
      appendHashChainedEvent(prev, {
        actor: 'Nomos · Gobernanza',
        action: 'SIMULATION_CYCLE_RESET',
        actionLabel: 'Nuevo ciclo de revisión iniciado (bitácora preservada)',
        matterId: SYNTHETIC_CASE.caseId,
        stage: 'DRAFT',
        detail: 'Estado de compuerta restablecido a DRAFT manteniendo historial SHA-256 append-only.',
      })
    );
  }

  function handleUpdateEvidenceValidation(evidenceId, nextStatus) {
    const actor = lawyerName.trim() || 'Revisor Humano (Simulado)';
    const targetPiece = evidenceItems.find((item) => item.id === evidenceId);
    if (!targetPiece || targetPiece.validationStatus === nextStatus) return;

    setEvidenceItems((prev) =>
      prev.map((item) =>
        item.id === evidenceId
          ? {
              ...item,
              validationStatus: nextStatus,
              validatedBy: nextStatus === 'PENDING' ? null : actor,
              validatedAt: nextStatus === 'PENDING' ? null : new Date().toISOString(),
            }
          : item
      )
    );

    const actionMap = {
      VALIDATED: {
        action: 'EVIDENCE_VALIDATED',
        actionLabel: `Pieza validada: ${targetPiece.title}`,
        detail: `Hecho y criterio preliminar de ${targetPiece.folio} validados por ${actor}.`,
      },
      FLAGGED: {
        action: 'EVIDENCE_FLAGGED',
        actionLabel: `Observación abierta en ${targetPiece.title}`,
        detail: `Pieza ${targetPiece.folio} marcada para revisión adicional por ${actor}.`,
      },
      PENDING: {
        action: 'EVIDENCE_RESET_PENDING',
        actionLabel: `Pieza devuelta a pendiente: ${targetPiece.title}`,
        detail: `Estado de ${targetPiece.folio} restablecido a PENDING por ${actor}.`,
      },
    };

    const meta = actionMap[nextStatus];
    setAuditEvents((prev) =>
      appendHashChainedEvent(prev, {
        actor,
        action: meta.action,
        actionLabel: meta.actionLabel,
        matterId: SYNTHETIC_CASE.caseId,
        stage: gateState.status,
        detail: meta.detail,
      })
    );
  }

  function handleAdvanceLegalCourse(courseId) {
    const target = legalCourses.find((c) => c.id === courseId);
    if (!target || target.status === 'CERTIFICADO') return;

    const transitioningToCertified = target.status !== 'POR_INICIAR';
    const earnedCount = legalCourses.filter((c) => c.status === 'CERTIFICADO').length;
    const nextFolio = transitioningToCertified
      ? `CERT-SINT-2026-${String(earnedCount + 1).padStart(3, '0')}`
      : null;

    setLegalCourses((prev) =>
      prev.map((course) => {
        if (course.id !== courseId) return course;
        if (course.status === 'POR_INICIAR') {
          return {
            ...course,
            status: 'EN_CURSO',
            progressPct: 35,
            nextMilestoneLabel: 'Módulo I iniciado · Evaluación parcial en progreso',
          };
        }
        return {
          ...course,
          status: 'CERTIFICADO',
          progressPct: 100,
          certificateFolio: nextFolio,
          nextMilestoneLabel: 'Diploma acreditado y archivado en expediente curricular',
        };
      })
    );

    setAuditEvents((prev) =>
      appendHashChainedEvent(prev, {
        actor: 'Irnerio · Academia Legal',
        action: transitioningToCertified ? 'LEGAL_CERTIFICATE_EARNED' : 'LEGAL_COURSE_STARTED',
        actionLabel: transitioningToCertified
          ? `Certificado legal obtenido: ${target.title}`
          : `Curso jurídico iniciado: ${target.title}`,
        matterId: target.id,
        stage: gateState.status,
        detail: transitioningToCertified
          ? `Diploma acreditado (${target.creditHours} h, ${target.practiceArea}) con folio ${nextFolio}.`
          : `Seguimiento iniciado en ${target.institution} (agente vinculado: ${target.linkedCouncilAgent}).`,
      })
    );
  }

  function handleInvokeJurist(jurist, stratum) {
    setAuditEvents((prev) =>
      appendHashChainedEvent(prev, {
        actor: `${jurist.name} · ${stratum.tabLabel}`,
        action: 'JURIST_COUNCIL_CONSULTED',
        actionLabel: `Dictamen preliminar invocado (${jurist.preferredProvider})`,
        matterId: SYNTHETIC_CASE.caseId,
        stage: gateState.status,
        detail: `${jurist.sealLabel} | Ruta=${jurist.taskKind}: ${jurist.briefSample}`,
      })
    );
  }

  return (
    <div className="app-shell">
      {/* Obsidian Topbar */}
      <header className="topbar">
        <div className="topbar-left">
          <button
            type="button"
            className="mobile-rail-toggle"
            aria-label={mobileRailOpen ? 'Cerrar menú de agentes' : 'Abrir menú de agentes'}
            aria-expanded={mobileRailOpen}
            onClick={() => setMobileRailOpen((prev) => !prev)}
          >
            {mobileRailOpen ? <X size={18} strokeWidth={1.75} /> : <Menu size={18} strokeWidth={1.75} />}
          </button>

          <div className="brand-block">
            <span className="brand-mark" aria-hidden="true">
              <Scale size={16} strokeWidth={1.75} />
            </span>
            <div className="brand-copy">
              <span className="brand-title">LegalTech Innovation Lab</span>
              <span className="brand-subtitle">Command Center · {SYNTHETIC_CASE.caseId}</span>
            </div>
          </div>
        </div>

        <div className="topbar-right">
          <span className="safety-badge" role="status">
            SIMULACIÓN SINTÉTICA · MOCK AUTHORITY
          </span>

          <span className="governance-pill">
            <ShieldCheck size={14} strokeWidth={1.75} aria-hidden="true" />
            <span>HITL: {gateState.status}</span>
          </span>

          <button
            type="button"
            className={`api-sync-btn mode-${apiSyncStatus.mode}`}
            onClick={handleToggleApiSync}
            title={apiSyncStatus.detail}
          >
            <Server size={13} strokeWidth={1.75} aria-hidden="true" />
            <span>{apiSyncStatus.label}</span>
          </button>
        </div>
      </header>

      {/* Mobile backdrop for drawer */}
      {mobileRailOpen && (
        <div
          className="mobile-backdrop"
          aria-hidden="true"
          onClick={() => setMobileRailOpen(false)}
        />
      )}

      {/* 3-Column Workstation Grid */}
      <div className="workstation-grid">
        {/* Left Obsidian Rail */}
        <aside className={`left-rail ${mobileRailOpen ? 'is-open' : ''}`} aria-label="Navegación de agentes y plazos">
          <AgentConstellation
            variant="roster"
            agents={AGENTS}
            activeAgentId={activeAgentId}
            onSelectAgent={handleSelectAgent}
          />

          <div className="rail-section rail-deadlines">
            <div className="rail-section-header">
              <span className="rail-section-title">
                <CalendarClock size={13} strokeWidth={1.75} aria-hidden="true" />
                <span>Plazos del Expediente</span>
              </span>
              <span className="rail-count-badge">{CHRONOS_DEADLINES.length}</span>
            </div>
            <ChronosDeadlinesList deadlines={CHRONOS_DEADLINES} compact />
          </div>

          <div className="privacy-lock-banner">
            <div className="privacy-lock-header">
              <Lock size={14} strokeWidth={1.75} aria-hidden="true" />
              <span>Privacy Lock Activo</span>
            </div>
            <p className="privacy-lock-copy">{SYNTHETIC_CASE.privacyNotice}</p>
          </div>
        </aside>

        {/* Center Parchment Editorial Workspace */}
        <main className="center-pane">
          {/* Case Masthead */}
          <header className="case-masthead">
            <div className="masthead-top-row">
              <span className="case-id-tag">{SYNTHETIC_CASE.caseId}</span>
              <span className="procedure-tag">{SYNTHETIC_CASE.procedureType}</span>
            </div>
            <h1 className="case-title">{SYNTHETIC_CASE.title}</h1>
            <dl className="case-parties-grid">
              <div className="party-cell">
                <dt>Actora (Sintética)</dt>
                <dd>{SYNTHETIC_CASE.plaintiff}</dd>
              </div>
              <div className="party-cell">
                <dt>Demandada (Sintética)</dt>
                <dd>{SYNTHETIC_CASE.defendant}</dd>
              </div>
              <div className="party-cell">
                <dt>Autoridad Destino</dt>
                <dd>{SYNTHETIC_CASE.authority}</dd>
              </div>
              <div className="party-cell">
                <dt>Cuantía Simulada</dt>
                <dd>{SYNTHETIC_CASE.syntheticClaimAmount}</dd>
              </div>
            </dl>
          </header>

          {/* Active Agent Mission Brief */}
          <AgentConstellation
            variant="brief"
            agents={AGENTS}
            activeAgentId={activeAgentId}
            onSelectAgent={handleSelectAgent}
            onNavigateFocus={handleNavigateFocus}
            gateStatus={gateState.status}
            validatedCount={validatedCount}
            totalEvidenceCount={evidenceItems.length}
            auditCount={auditEvents.length}
          />

          {/* Interactive HITL Review Gate Panel */}
          <ReviewGatePanel
            caseData={SYNTHETIC_CASE}
            gateState={gateState}
            lawyerName={lawyerName}
            onLawyerNameChange={setLawyerName}
            validatedCount={validatedCount}
            totalEvidenceCount={evidenceItems.length}
            onSendToReview={handleSendToReview}
            onApprove={handleApprove}
            onReject={handleReject}
            onSubmitMock={handleSubmitMock}
            onResetCycle={handleResetCycle}
            apiSyncStatus={apiSyncStatus}
          />

          {/* Document Draft Preview (solicitud_general.j2 synthetic preview) */}
          <section
            id="draft-preview-section"
            className="panel-card draft-preview-panel"
            aria-labelledby="draft-preview-heading"
          >
            <div className="panel-header">
              <div>
                <div className="panel-eyebrow">
                  <FileCode2 size={14} strokeWidth={1.75} aria-hidden="true" />
                  <span>Vista Previa de Promoción (Dike · Jinja2)</span>
                </div>
                <h2 id="draft-preview-heading" className="panel-title">
                  {SYNTHETIC_CASE.templateName}{' '}
                  <span className="template-version">{SYNTHETIC_CASE.templateVersion}</span>
                </h2>
              </div>

              <div className="segmented-toggle" role="group" aria-label="Modo de vista del borrador">
                <button
                  type="button"
                  className={`seg-btn ${draftViewMode === 'document' ? 'is-active' : ''}`}
                  onClick={() => setDraftViewMode('document')}
                >
                  <Eye size={14} strokeWidth={1.75} aria-hidden="true" />
                  <span>Documento</span>
                </button>
                <button
                  type="button"
                  className={`seg-btn ${draftViewMode === 'bindings' ? 'is-active' : ''}`}
                  onClick={() => setDraftViewMode('bindings')}
                >
                  <Code2 size={14} strokeWidth={1.75} aria-hidden="true" />
                  <span>Contexto Jinja2</span>
                </button>
              </div>
            </div>

            <div
              className={`draft-watermark-bar ${
                gateState.status === 'APPROVED' ||
                gateState.status === 'SUBMITTED' ||
                gateState.status === 'RECEIPTED'
                  ? 'is-cleared'
                  : 'is-blocked'
              }`}
            >
              {draftPreview.watermarkLabel}
            </div>

            {draftViewMode === 'document' ? (
              <div className="draft-paper-sheet">
                <pre className="draft-document-body">{draftPreview.renderedText}</pre>
              </div>
            ) : (
              <div className="draft-bindings-box">
                <pre className="draft-bindings-code">
                  {JSON.stringify(draftPreview.templateBindings, null, 2)}
                </pre>
              </div>
            )}
          </section>

          {/* Historical Council of Jurists (4 Strata - School of Athens) & Multi-Model Router */}
          <HallOfJuristsPanel onInvokeJurist={handleInvokeJurist} />

          {/* Specialized Legal Academy, Diplomas & Certifications Panel */}
          <LegalAcademyPanel courses={legalCourses} onAdvanceCourse={handleAdvanceLegalCourse} />
        </main>

        {/* Right Pane: Evidence Inspector + Audit Timeline */}
        <aside className="right-pane" aria-label="Inspector probatorio y bitácora de auditoría">
          <EvidenceInspector
            evidenceItems={evidenceItems}
            onUpdateValidation={handleUpdateEvidenceValidation}
          />
          <AuditTimeline events={auditEvents} deadlines={CHRONOS_DEADLINES} />
        </aside>
      </div>
    </div>
  );
}
