import React from 'react';
import {
  Clock,
  FileText,
  Inbox,
  Link2,
  Scale,
  ShieldCheck,
  ArrowUpRight,
  Shield,
} from 'lucide-react';

const AGENT_ICONS = {
  Inbox,
  Scale,
  FileText,
  ShieldCheck,
  Clock,
  Link2,
};

function renderAgentIcon(iconName, size = 16) {
  const IconComponent = AGENT_ICONS[iconName] || Shield;
  return <IconComponent size={size} strokeWidth={1.75} aria-hidden="true" />;
}

export default function AgentConstellation({
  variant = 'roster',
  agents,
  activeAgentId,
  onSelectAgent,
  onNavigateFocus,
  gateStatus,
  validatedCount,
  totalEvidenceCount,
  auditCount,
}) {
  if (variant === 'brief') {
    const activeAgent = agents.find((agent) => agent.id === activeAgentId) || agents[0];

    let liveTelemetry = activeAgent.lastOutput;
    if (activeAgent.id === 'nomos') {
      liveTelemetry =
        gateStatus === 'APPROVED'
          ? 'Compuerta HITL desbloqueada: estado APPROVED listo para emisión mock.'
          : gateStatus === 'RECEIPTED'
            ? 'Acuse mock emitido y sellado tras aprobación nominal.'
            : `Protección SubmissionBlockedError activa (estado actual: ${gateStatus}).`;
    } else if (activeAgent.id === 'themis') {
      liveTelemetry = `${validatedCount}/${totalEvidenceCount} piezas documentales validadas por revisor humano.`;
    } else if (activeAgent.id === 'apollo') {
      liveTelemetry = `${auditCount} eventos encadenados con SHA-256 íntegro en bitácora append-only.`;
    }

    const focusTargets = {
      hermes: { target: 'evidence', label: 'Inspeccionar Anexos' },
      themis: { target: 'evidence', label: 'Validar Hechos y Criterios' },
      dike: { target: 'draft', label: 'Ver Plantilla solicitud_general.j2' },
      nomos: { target: 'gate', label: 'Ir a Compuerta HITL' },
      chronos: { target: 'deadlines', label: 'Revisar Plazos Chronos' },
      apollo: { target: 'audit', label: 'Auditar Cadena SHA-256' },
    };
    const focusAction = focusTargets[activeAgent.id];

    return (
      <section className="agent-brief-card" aria-label={`Misión del agente ${activeAgent.name}`}>
        <div className="agent-brief-header">
          <div className="agent-brief-identity">
            <span className={`agent-emblem tone-${activeAgent.statusTone}`}>
              {renderAgentIcon(activeAgent.icon, 18)}
            </span>
            <div>
              <div className="agent-brief-eyebrow">Agente Activo · Constelación</div>
              <h2 className="agent-brief-title">
                {activeAgent.name} <span className="agent-brief-subtitle">— {activeAgent.greekTitle}</span>
              </h2>
            </div>
          </div>
          <div className="agent-brief-actions">
            <span className={`status-pill tone-${activeAgent.statusTone}`}>
              {activeAgent.shortStatus}
            </span>
            {focusAction && onNavigateFocus && (
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={() => onNavigateFocus(focusAction.target)}
              >
                <span>{focusAction.label}</span>
                <ArrowUpRight size={14} strokeWidth={1.75} aria-hidden="true" />
              </button>
            )}
          </div>
        </div>

        <p className="agent-brief-mission">{activeAgent.missionBrief}</p>

        <div className="agent-brief-meta">
          <div className="agent-guardrails">
            <span className="meta-label">Salvaguardas:</span>
            <ul className="guardrail-list">
              {activeAgent.guardrails.map((rule) => (
                <li key={rule} className="guardrail-chip">
                  {rule}
                </li>
              ))}
            </ul>
          </div>
          <div className="agent-telemetry">
            <span className="meta-label">Telemetría en vivo:</span>
            <span className="telemetry-value">{liveTelemetry}</span>
          </div>
        </div>
      </section>
    );
  }

  return (
    <div className="rail-section">
      <div className="rail-section-header">
        <span className="rail-section-title">Constelación de Agentes</span>
        <span className="rail-count-badge">{agents.length}</span>
      </div>
      <nav className="agent-roster" aria-label="Selector de agentes de la constelación">
        {agents.map((agent) => {
          const isActive = agent.id === activeAgentId;
          return (
            <button
              key={agent.id}
              type="button"
              className={`agent-roster-item ${isActive ? 'is-active' : ''}`}
              aria-pressed={isActive}
              onClick={() => onSelectAgent(agent.id)}
            >
              <span className={`roster-icon tone-${agent.statusTone}`}>
                {renderAgentIcon(agent.icon, 15)}
              </span>
              <span className="roster-copy">
                <span className="roster-name-row">
                  <span className="roster-name">{agent.name}</span>
                  <span className={`roster-dot tone-${agent.statusTone}`} aria-hidden="true" />
                </span>
                <span className="roster-role">{agent.greekTitle}</span>
                <span className="roster-status">{agent.shortStatus}</span>
              </span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
