import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  BookOpenCheck,
  Check,
  Columns,
  Copy,
  Cpu,
  Feather,
  Headphones,
  Landmark,
  ScrollText,
  Sliders,
  Sparkles,
  Volume2,
  VolumeX,
} from 'lucide-react';
import {
  ADVERSARIAL_ARCHETYPES,
  CASE_TYPE_AVATAR_ROUTES,
  COUNCIL_JURISTS,
  GEMINI_MASTER_PROMPTS,
  HISTORICAL_STRATA,
} from '../data/syntheticCase';

function FullBodySpiritFigure({ juristId, adversarialId, visualMode }) {
  const isAthena = juristId === 'atenea';
  const isThemis = juristId === 'temis';
  const showsTrident = isAthena && visualMode !== 'adversarial';
  const showsScales = isThemis && visualMode !== 'adversarial';
  const showsOvercoat = visualMode === 'adversarial' || ['abogado_diablo', 'tony_montana', 'saul_goodman', 'harvey_specter'].includes(adversarialId);

  return (
    <svg
      className="fullbody-spirit-figure"
      viewBox="0 0 240 440"
      role="img"
      aria-label="Representación monocromo de cuerpo completo en el Reasoning Room (100% Full-Frame, cero recorte)"
    >
      <defs>
        <linearGradient id="seeleBeamGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#f2c98a" stopOpacity="0.46" />
          <stop offset="32%" stopColor="#d8c8ad" stopOpacity="0.14" />
          <stop offset="100%" stopColor="#070809" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="spiritMarbleGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#eceae4" stopOpacity="0.96" />
          <stop offset="48%" stopColor="#7b7d80" stopOpacity="0.92" />
          <stop offset="100%" stopColor="#1b1c1e" stopOpacity="0.98" />
        </linearGradient>
        <linearGradient id="robeShadowGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#d4d2cc" stopOpacity="0.95" />
          <stop offset="55%" stopColor="#4f5154" stopOpacity="0.96" />
          <stop offset="100%" stopColor="#121315" stopOpacity="1" />
        </linearGradient>
      </defs>

      {/* Monolith Chamber Frame & SEELE Zenithal Light Beam */}
      <rect x="44" y="8" width="152" height="414" rx="4" fill="#070809" stroke="rgba(235,184,108,0.34)" strokeWidth="1.2" />
      <polygon points="74,10 166,10 212,418 28,418" fill="url(#seeleBeamGrad)" />
      <rect x="92" y="10" width="56" height="4" fill="#f3c57c" opacity="0.9" />

      {/* Plinth / Obsidian Dais so 100% feet remain visible above bottom border */}
      <rect x="64" y="394" width="112" height="14" rx="2" fill="#17191c" stroke="#5c5e61" strokeWidth="1" />
      <ellipse cx="120" cy="394" rx="46" ry="5" fill="#2b2d30" opacity="0.7" />

      {/* Full-length Weapon / Attribute rendered completely from top to bottom inside frame */}
      {showsTrident && (
        <g stroke="#e6e3dc" strokeWidth="2.2" fill="none" strokeLinecap="round" strokeLinejoin="round">
          <line x1="168" y1="62" x2="168" y2="394" stroke="#cfccc4" strokeWidth="2.4" />
          <path d="M156 84 L156 60 Q156 54 159 48" />
          <path d="M168 84 L168 42" />
          <path d="M180 84 L180 60 Q180 54 177 48" />
          <line x1="156" y1="84" x2="180" y2="84" strokeWidth="2.6" />
        </g>
      )}

      {showsScales && (
        <g stroke="#e3e0d8" strokeWidth="1.6" fill="none">
          <line x1="56" y1="184" x2="94" y2="184" />
          <line x1="75" y1="176" x2="75" y2="210" />
          <line x1="58" y1="184" x2="53" y2="206" />
          <line x1="58" y1="184" x2="63" y2="206" />
          <path d="M51 206 Q58 214 65 206 Z" fill="#9ea0a4" />
          <line x1="92" y1="184" x2="87" y2="206" />
          <line x1="92" y1="184" x2="97" y2="206" />
          <path d="M85 206 Q92 214 99 206 Z" fill="#9ea0a4" />
        </g>
      )}

      {/* Full-Body Spirit Silhouette Head-to-Toe (Zero Crop) */}
      <g>
        {/* Crest / Helmet or Classic Sculpted Hair */}
        {isAthena && visualMode !== 'adversarial' ? (
          <g>
            <path d="M108 66 Q120 34 134 62 Q125 68 108 66 Z" fill="#dcd9d1" />
            <path d="M105 84 Q105 64 120 62 Q135 64 135 84 L132 95 L108 95 Z" fill="url(#spiritMarbleGrad)" />
          </g>
        ) : (
          <ellipse cx="120" cy="82" rx="14" ry="17" fill="url(#spiritMarbleGrad)" />
        )}

        {/* Face profile / Chiaroscuro mask */}
        <ellipse cx="120" cy="91" rx="11.5" ry="14" fill="url(#spiritMarbleGrad)" />
        <rect x="115" y="103" width="10" height="10" fill="#8b8d90" />

        {/* Shoulders & Torso */}
        <path
          d={
            showsOvercoat && visualMode === 'adversarial'
              ? 'M86 122 Q120 108 154 122 L148 228 L92 228 Z'
              : 'M84 124 Q120 110 156 124 L144 214 L96 214 Z'
          }
          fill="url(#spiritMarbleGrad)"
        />

        {/* Pleated Full-Length Peplos Dress / Judicial Coat down to Ankles */}
        <path
          d={
            showsOvercoat && visualMode === 'adversarial'
              ? 'M92 226 L148 226 L156 364 L84 364 Z'
              : 'M96 212 L144 212 L158 378 L82 378 Z'
          }
          fill="url(#robeShadowGrad)"
        />
        {/* Vertical Classical Drapery Folds */}
        <line x1="106" y1="218" x2="98" y2="376" stroke="#c8c5bd" strokeWidth="1" opacity="0.5" />
        <line x1="120" y1="215" x2="120" y2="377" stroke="#e4e1d9" strokeWidth="1.2" opacity="0.6" />
        <line x1="134" y1="218" x2="142" y2="376" stroke="#c8c5bd" strokeWidth="1" opacity="0.5" />

        {/* Both Arms & Hands completely inside frame */}
        <path d="M86 126 Q72 170 76 216 L88 216 Q88 176 96 146 Z" fill="#9b9d9f" />
        <path d="M154 126 Q168 168 166 206 L154 206 Q152 174 144 146 Z" fill="#b4b6b8" />
        <circle cx="81" cy="220" r="5" fill="#d9d6ce" />
        <circle cx="163" cy="208" r="5.5" fill="#e6e3db" />

        {/* Visible Feet / Sandals / Dress Shoes planted squarely on plinth (No Amputation) */}
        <ellipse cx="107" cy="389" rx="9" ry="5" fill="#dcd9d1" />
        <ellipse cx="133" cy="389" rx="9" ry="5" fill="#dcd9d1" />
      </g>
    </svg>
  );
}

export default function HallOfJuristsPanel({ onInvokeJurist }) {
  const [activeStratumId, setActiveStratumId] = useState('STRATUM_I');
  const [selectedJuristId, setSelectedJuristId] = useState('atenea');
  const [selectedCaseTypeId, setSelectedCaseTypeId] = useState('agrupacion_delictuosa_contra_salud');
  const [overrideAdversarialId, setOverrideAdversarialId] = useState('tony_montana');
  const [isManualOverride, setIsManualOverride] = useState(false);
  const [stageTab, setStageTab] = useState('reasoning_room'); // 'reasoning_room' | 'planilla_v1'
  const [ambientPlaying, setAmbientPlaying] = useState(false);
  const [copiedKey, setCopiedKey] = useState(null);
  const [lastInvokedSummary, setLastInvokedSummary] = useState(null);

  const audioCtxRef = useRef(null);
  const oscNodesRef = useRef([]);

  useEffect(() => {
    return () => {
      try {
        oscNodesRef.current.forEach((node) => node.stop());
        if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
          audioCtxRef.current.close();
        }
      } catch {
        // Ignore teardown issues in non-audio headless environments
      }
    };
  }, []);

  const activeCaseRoute = useMemo(
    () => CASE_TYPE_AVATAR_ROUTES.find((c) => c.id === selectedCaseTypeId) || CASE_TYPE_AVATAR_ROUTES[0],
    [selectedCaseTypeId]
  );

  const activeStratum = useMemo(
    () => HISTORICAL_STRATA.find((s) => s.id === activeStratumId) || HISTORICAL_STRATA[0],
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

  const activeAdversarial = useMemo(
    () => ADVERSARIAL_ARCHETYPES.find((a) => a.id === overrideAdversarialId) || ADVERSARIAL_ARCHETYPES[0],
    [overrideAdversarialId]
  );

  function handleSelectStratum(stratumId) {
    setActiveStratumId(stratumId);
    const firstInStratum = COUNCIL_JURISTS.find((j) => j.stratumId === stratumId);
    if (firstInStratum) {
      setSelectedJuristId(firstInStratum.id);
    }
  }

  function handleSelectCaseType(caseTypeId) {
    setSelectedCaseTypeId(caseTypeId);
    const route = CASE_TYPE_AVATAR_ROUTES.find((c) => c.id === caseTypeId);
    if (!route) return;
    setIsManualOverride(false);
    setOverrideAdversarialId(route.recommendedAdversarialId);
    const recommendedJurist = COUNCIL_JURISTS.find((j) => j.id === route.recommendedJuristId);
    if (recommendedJurist) {
      setActiveStratumId(recommendedJurist.stratumId);
      setSelectedJuristId(recommendedJurist.id);
    }
  }

  function handleOverrideAdversarial(archetypeId) {
    setOverrideAdversarialId(archetypeId);
    const matchesAi = archetypeId === activeCaseRoute.recommendedAdversarialId;
    setIsManualOverride(!matchesAi);
  }

  function handleToggleAmbientSound() {
    if (ambientPlaying) {
      try {
        oscNodesRef.current.forEach((node) => node.stop());
      } catch {
        // Ignore already stopped oscillators
      }
      oscNodesRef.current = [];
      setAmbientPlaying(false);
      return;
    }

    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      if (!audioCtxRef.current || audioCtxRef.current.state === 'closed') {
        audioCtxRef.current = new AudioCtx();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }
      const gain = ctx.createGain();
      gain.gain.value = 0.025;
      gain.connect(ctx.destination);

      const frequencies = [110, 164.81, 220];
      const nodes = frequencies.map((freq) => {
        const osc = ctx.createOscillator();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, ctx.currentTime);
        osc.connect(gain);
        osc.start();
        return osc;
      });
      oscNodesRef.current = nodes;
      setAmbientPlaying(true);
    } catch {
      setAmbientPlaying(false);
    }
  }

  async function handleCopyPrompt(key, text) {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 2000);
    } catch {
      setCopiedKey(null);
    }
  }

  function handleInvoke() {
    if (!activeJurist) return;
    onInvokeJurist(activeJurist, activeStratum);
    setLastInvokedSummary({
      juristName: activeJurist.name,
      adversarialName: activeAdversarial.name,
      selectionMode: isManualOverride ? 'Reconfigurado por Abogado/a' : 'Recomendación IA',
      caseLabel: activeCaseRoute.label,
      provider: activeJurist.preferredProvider,
      stratum: activeStratum.tabLabel,
      seal: activeJurist.sealLabel,
      dossierPath: activeAdversarial.dossierPath,
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
            <span>El Salón de los Pensadores · Universo Lexis &amp; Reasoning Room</span>
          </div>
          <h2 id="hall-of-jurists-heading" className="panel-title">
            Consejo de Jurisconsultos, Avatares Adversariales y Enrutador IA
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

      {/* Headphones & Calm Focus Soundscape Advisory Banner */}
      <div className="immersion-headphone-banner" role="region" aria-label="Recomendación de inmersión sonora">
        <div className="immersion-copy">
          <Headphones size={16} strokeWidth={1.75} aria-hidden="true" />
          <div>
            <strong>Inmersión Sonora del Reasoning Room (Audífonos Recomendados):</strong>{' '}
            <span>
              Para razonamiento jurídico profundo, utiliza audífonos con música ambiental tranquila — sug:{' '}
              <em>{activeCaseRoute.audioPreset}</em>.
            </span>
          </div>
        </div>
        <button
          type="button"
          className={`btn btn-sm immersion-sound-btn ${ambientPlaying ? 'is-active' : ''}`}
          onClick={handleToggleAmbientSound}
        >
          {ambientPlaying ? <Volume2 size={14} aria-hidden="true" /> : <VolumeX size={14} aria-hidden="true" />}
          <span>{ambientPlaying ? 'Pausar Frecuencia 110Hz' : 'Ambiente Sonoro'}</span>
        </button>
      </div>

      {/* AI Case-Type Recommendation + Human Lawyer Manual Reconfiguration */}
      <div className="case-avatar-router-box">
        <div className="case-router-head">
          <div className="case-router-title">
            <Sliders size={14} strokeWidth={1.75} aria-hidden="true" />
            <span>Selección IA por Tipo de Asunto (Reconfigurable por el Abogado/a)</span>
          </div>
          <span className={`selection-mode-badge ${isManualOverride ? 'is-override' : 'is-ai'}`}>
            {isManualOverride ? 'Reconfiguración Manual Activa' : 'Recomendación IA Activa'}
          </span>
        </div>

        <div className="case-type-pills" role="group" aria-label="Tipo de caso jurídico">
          {CASE_TYPE_AVATAR_ROUTES.map((route) => {
            const active = route.id === selectedCaseTypeId;
            return (
              <button
                key={route.id}
                type="button"
                className={`case-type-pill ${active ? 'is-active' : ''}`}
                aria-pressed={active}
                onClick={() => handleSelectCaseType(route.id)}
              >
                {route.label}
              </button>
            );
          })}
        </div>

        <p className="case-protocol-note">{activeCaseRoute.protocolSummary}</p>

        {/* Manual Override Strip for Adversarial / Cinematic Lenses */}
        <div className="adversarial-override-row" role="group" aria-label="Reconfigurar avatar adversarial">
          <span className="override-row-label">Alternar Lente Adversarial (Estrato V):</span>
          <div className="adversarial-chips">
            {ADVERSARIAL_ARCHETYPES.map((arch) => {
              const selected = arch.id === overrideAdversarialId;
              return (
                <button
                  key={arch.id}
                  type="button"
                  className={`jurist-chip ${selected ? 'is-active' : ''}`}
                  aria-pressed={selected}
                  onClick={() => handleOverrideAdversarial(arch.id)}
                >
                  {arch.name}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Dual Visual Stage: B&W Full-Body Spirit Reasoning Room OR V1 Monolith Roster & Prompts */}
      <div className="reasoning-stage-shell">
        <div className="stage-tabs-bar" role="tablist" aria-label="Vista visual del Reasoning Room">
          <button
            type="button"
            role="tab"
            aria-selected={stageTab === 'reasoning_room'}
            className={`stage-view-btn ${stageTab === 'reasoning_room' ? 'is-active' : ''}`}
            onClick={() => setStageTab('reasoning_room')}
          >
            Cámara B&amp;N Cuerpo Completo (Zero Crop)
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={stageTab === 'planilla_v1'}
            className={`stage-view-btn ${stageTab === 'planilla_v1' ? 'is-active' : ''}`}
            onClick={() => setStageTab('planilla_v1')}
          >
            Roster Monolitos V1 (`jurisconsultosv1.jpeg`) &amp; Prompts Gemini V2
          </button>
        </div>

        {stageTab === 'reasoning_room' ? (
          <div className="reasoning-room-stage">
            <div className="seele-monolith-visual">
              <FullBodySpiritFigure
                juristId={activeJurist?.id || 'atenea'}
                adversarialId={activeAdversarial.id}
                visualMode={isManualOverride ? 'adversarial' : 'council'}
              />
              <div className="monolith-spirit-caption">
                <span>ESPÍRITU MONOCROMO · 100% FULL-FRAME ZERO CROP</span>
                <strong>
                  {activeJurist?.name} × {activeAdversarial.name}
                </strong>
              </div>
            </div>

            <div className="reasoning-dossier-panel">
              <div className="dossier-source-pill">
                <BookOpenCheck size={13} strokeWidth={1.75} aria-hidden="true" />
                <span>Dossier Verificable: {activeAdversarial.dossierPath}</span>
              </div>
              <h3 className="dossier-lenses-title">{activeAdversarial.name}</h3>
              <p className="dossier-lenses-sub">{activeAdversarial.stratumLabel}</p>

              <div className="dossier-block">
                <span className="dossier-block-label">Criterio Metodológico Adaptado al Caso</span>
                <p>{activeAdversarial.reasoningTone}</p>
              </div>

              <div className="dossier-block is-guardrail">
                <span className="dossier-block-label">Candado Ético y Constitucional (Temis · HITL)</span>
                <p>{activeAdversarial.ethicalGuardrail}</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="planilla-v1-grid">
            <figure className="roster-v1-frame">
              <img
                src={`${import.meta.env.BASE_URL}jurisconsultosv1.jpeg`}
                alt="Planilla V1 Personajes del Universo Lexis con iluminación cenital Evangelion"
                className="roster-v1-preview-img"
              />
              <figcaption className="roster-v1-caption">
                Referencia real `jurisconsultosv1.jpeg` · 5 Monolitos Character Select con luz cenital cálida SEELE.
              </figcaption>
            </figure>

            <div className="gemini-prompts-column">
              <div className="prompt-card-mini">
                <div className="prompt-card-head">
                  <strong>Prompt Gemini V2 · Planilla 2 (Estrato V Adversarial)</strong>
                  <button
                    type="button"
                    className="btn-icon-text"
                    onClick={() => handleCopyPrompt('planillaV2', GEMINI_MASTER_PROMPTS.planillaV2)}
                  >
                    {copiedKey === 'planillaV2' ? <Check size={12} /> : <Copy size={12} />}
                    <span>{copiedKey === 'planillaV2' ? 'Copiado' : 'Copiar'}</span>
                  </button>
                </div>
                <p className="prompt-card-text">{GEMINI_MASTER_PROMPTS.planillaV2}</p>
              </div>

              <div className="prompt-card-mini">
                <div className="prompt-card-head">
                  <strong>Prompt Atenea B&amp;N Cuerpo Completo (Zero Crop)</strong>
                  <button
                    type="button"
                    className="btn-icon-text"
                    onClick={() => handleCopyPrompt('athenaBW', GEMINI_MASTER_PROMPTS.athenaFullBodyBW)}
                  >
                    {copiedKey === 'athenaBW' ? <Check size={12} /> : <Copy size={12} />}
                    <span>{copiedKey === 'athenaBW' ? 'Copiado' : 'Copiar'}</span>
                  </button>
                </div>
                <p className="prompt-card-text">{GEMINI_MASTER_PROMPTS.athenaFullBodyBW}</p>
              </div>
            </div>
          </div>
        )}
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
              Dictamen preliminar de {lastInvokedSummary.juristName} × {lastInvokedSummary.adversarialName} (
              {lastInvokedSummary.selectionMode})
            </strong>
            <p className="callout-body">
              Asunto: {lastInvokedSummary.caseLabel} · Vía{' '}
              <span className="mono-inline">{lastInvokedSummary.provider}</span> — Evento encadenado a bitácora SHA-256 (dossier: {lastInvokedSummary.dossierPath}).
            </p>
          </div>
        </div>
      )}
    </section>
  );
}
