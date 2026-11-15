/**
 * 100% SYNTHETIC SEED DATA — LEGALTECH INNOVATION LAB
 * No real client names, no real case numbers, no real addresses, no real credentials.
 */

export const SYNTHETIC_CASE = {
  caseId: 'EXP-SINT-2026-001',
  title: 'Juicio Ejecutivo Mercantil Sintético · Solicitud de Diligencias',
  procedureType: 'Juicio Ejecutivo Mercantil (Simulación Sandbox)',
  plaintiff: 'Corporativo Alfa Sintético S.A. de C.V.',
  plaintiffRfc: 'CAS000101AAA',
  defendant: 'Suministros Beta Ficticios S.A. de C.V.',
  defendantRfc: 'SBF000202BBB',
  authority: 'Tribunal Virtual (Simulado — MOCK)',
  courtRoom: 'Juzgado 99° Mercantil Virtual · Sala Sandbox',
  syntheticAddress: 'Av. Simulación Tecnológica No. 100, Col. Demo, C.P. 00000, Ciudad Sintética',
  syntheticClaimAmount: '$250,000.00 MXN (Valor Sintético)',
  syntheticAccountRef: 'CTA-MOCK-0000-0000-9999',
  templateName: 'solicitud_general.j2',
  templateVersion: 'v0.1-sintetico',
  privacyNotice:
    'Aislamiento estricto: datos 100% sintéticos. Cero PII real, cero FIEL/e.firma, cero conexión a tribunales en producción.',
};

export const AGENTS = [
  {
    id: 'hermes',
    name: 'Hermes',
    greekTitle: 'Ingesta y Despacho Documental',
    shortStatus: 'Indexado · Sandbox',
    statusTone: 'sage',
    icon: 'Inbox',
    role: 'Recepción de anexos sintéticos, normalización OCR simulada y filtro de prevención PII.',
    missionBrief:
      'Verificar que las 3 piezas documentales de EXP-SINT-2026-001 provengan exclusivamente del set sintético antes de liberarlas a análisis.',
    guardrails: [
      'Bloqueo preventivo de RFC, cuentas bancarias o domicilios reales',
      'Etiquetado de origen documental y hash SHA-256 por anexo',
    ],
    lastOutput: '3 anexos sintéticos normalizados sin alertas PII.',
  },
  {
    id: 'themis',
    name: 'Themis',
    greekTitle: 'Evaluación Probatoria y Criterio',
    shortStatus: 'Esperando Validación',
    statusTone: 'amber',
    icon: 'Scale',
    role: 'Separación estricta entre hechos fácticos verificables y conclusiones jurídicas preliminares.',
    missionBrief:
      'Presentar hechos extraídos con cita de folio junto a hipótesis preliminares no vinculantes para validación expresa del abogado.',
    guardrails: [
      'Prohibido presentar inferencias IA como hechos probados',
      'Toda conclusión requiere validación humana explícita',
    ],
    lastOutput: '3 pares Hecho/Conclusión listos en Inspector Probatorio.',
  },
  {
    id: 'dike',
    name: 'Dike',
    greekTitle: 'Redacción de Promociones',
    shortStatus: 'Borrador v0.1 Listo',
    statusTone: 'copper',
    icon: 'FileText',
    role: 'Ensamblado determinista de escritos con plantilla Jinja2 auditable (solicitud_general.j2).',
    missionBrief:
      'Preparar el proyecto de solicitud de diligencias para Corporativo Alfa Sintético S.A. de C.V. bajo marca de agua hasta aprobación nominal.',
    guardrails: [
      'Solo variables tipadas vinculadas al expediente sintético',
      'Marca de agua automática mientras el estado sea distinto a APPROVED',
    ],
    lastOutput: 'Plantilla solicitud_general.j2 compilada con datos mock.',
  },
  {
    id: 'nomos',
    name: 'Nomos',
    greekTitle: 'Gobernanza y Compuerta HITL',
    shortStatus: 'Compuerta Activa',
    statusTone: 'copper',
    icon: 'ShieldCheck',
    role: 'Custodia de la máquina de estados DRAFT → IN_REVIEW → APPROVED → SUBMITTED → RECEIPTED.',
    missionBrief:
      'Aplicar protección SubmissionBlockedError: impedir toda emisión ante Tribunal Virtual (Simulado — MOCK) sin firma nominal de abogado.',
    guardrails: [
      'Emisión bloqueada fuera del estado APPROVED',
      'Rechazos obligan motivo documentado y retorno a DRAFT',
    ],
    lastOutput: 'Protección SubmissionBlockedError verificada.',
  },
  {
    id: 'chronos',
    name: 'Chronos',
    greekTitle: 'Control de Términos y Plazos',
    shortStatus: '3 Plazos Activos',
    statusTone: 'amber',
    icon: 'Clock',
    role: 'Cómputo de términos procesales simulados, recordatorios preventivos y agenda de diligencias.',
    missionBrief:
      'Monitorear los plazos procesales simulados del expediente EXP-SINT-2026-001 y alertar vencimientos próximos.',
    guardrails: [
      'Cálculo basado en calendario procesal simulado',
      'Alerta temprana previa al vencimiento de términos',
    ],
    lastOutput: 'Próximo vencimiento simulado en 3 días hábiles.',
  },
  {
    id: 'apollo',
    name: 'Apollō',
    greekTitle: 'Trazabilidad y Bitácora SHA-256',
    shortStatus: 'Cadena Íntegra',
    statusTone: 'sage',
    icon: 'Link2',
    role: 'Registro append-only con encadenamiento criptográfico SHA-256 de cada acción humana o de agente.',
    missionBrief:
      'Encadenar cada transición de revisión, validación probatoria y emisión de acuse mock mediante hashes verificables.',
    guardrails: [
      'Bitácora estrictamente append-only sin edición retroactiva',
      'Encadenamiento prevHash → entryHash en cada evento',
    ],
    lastOutput: 'Cadena SHA-256 inicial verificada sin rupturas.',
  },
];

export const INITIAL_EVIDENCE = [
  {
    id: 'ev-01',
    shortLabel: 'Anexo 01',
    title: 'Contrato Marco Sintético',
    folio: 'ANX-SINT-01 · Págs. 1–4',
    sourceType: 'Documental Privada Simulada',
    documentHash: 'sha256:4f8c92a1e7b088431c902a5d6612f309e4d12a78c0a1e4f9b2c3d8e1a90491d2',
    extractedFact:
      'Documento fechado el 15 de enero de 2026 entre Corporativo Alfa Sintético S.A. de C.V. y Suministros Beta Ficticios S.A. de C.V.; la cláusula 8ª registra contraprestación por $250,000.00 MXN (valor sintético) pagadera a 30 días naturales.',
    factSourceRef: 'Cláusula 8ª, pág. 3 · Folio ANX-SINT-01',
    preliminaryConclusion:
      'Posible acreditación preliminar de la relación contractual mercantil y exigibilidad del saldo simulado, sujeta a verificación humana de facultades de representación y firmas.',
    legalCaution: 'No vinculante · Requiere cotejo de personalidad y clausulado por abogado/a.',
    validationStatus: 'PENDING',
    validatedBy: null,
    validatedAt: null,
  },
  {
    id: 'ev-02',
    shortLabel: 'Anexo 02',
    title: 'Estado de Cuenta Ficticio',
    folio: 'ANX-SINT-02 · Pág. 1',
    sourceType: 'Certificación Contable Simulada',
    documentHash: 'sha256:9b3e11c4a2f80159283b4e71d0f21c84a55e67d9c3b102f8e4a6c2d7b91030e7',
    extractedFact:
      'Corte contable simulado al 28 de febrero de 2026 sobre la referencia ficticia CTA-MOCK-0000-0000-9999: cargo principal de $250,000.00 MXN, abonos aplicados $0.00 MXN, saldo insoluto reportado $250,000.00 MXN.',
    factSourceRef: 'Tabla de movimientos, fila 4 · Folio ANX-SINT-02',
    preliminaryConclusion:
      'Indicio preliminar de liquidez y mora contable del saldo simulado; requiere validación humana sobre fecha exacta de exigibilidad y tasa moratoria aplicable.',
    legalCaution: 'No vinculante · Debe confirmarse si requiere certificación contable formal.',
    validationStatus: 'PENDING',
    validatedBy: null,
    validatedAt: null,
  },
  {
    id: 'ev-03',
    shortLabel: 'Anexo 03',
    title: 'Acuse Simulado',
    folio: 'ANX-SINT-03 · Pág. 1',
    sourceType: 'Constancia de Requerimiento Previo (Mock)',
    documentHash: 'sha256:7d20f5c8e1a97420b6e41c39a8d5f201e7b49c6a3d18e5f0c2b4a7d9e10388b4',
    extractedFact:
      'Acuse generado en sandbox con sello temporal 2026-03-05T16:20:00Z dirigido a Suministros Beta Ficticios S.A. de C.V. en Av. Simulación Tecnológica No. 100, Col. Demo, C.P. 00000.',
    factSourceRef: 'Bloque de acuse electrónico · Folio ANX-SINT-03',
    preliminaryConclusion:
      'Posible antecedente de gestión extrajudicial previa; no sustituye diligencia formal ordenada por Tribunal Virtual (Simulado — MOCK) y exige validación de domicilio procesal.',
    legalCaution: 'No vinculante · Verificar domicilio procesal vigente antes de solicitar diligencia.',
    validationStatus: 'PENDING',
    validatedBy: null,
    validatedAt: null,
  },
];

export const CHRONOS_DEADLINES = [
  {
    id: 'dl-01',
    title: 'Presentación de Solicitud de Diligencias (Mock)',
    remaining: '3 días hábiles',
    targetDate: '2026-11-19',
    urgency: 'high',
    owner: 'Dike · Nomos',
  },
  {
    id: 'dl-02',
    title: 'Validación Nominal de Hechos Probatorios',
    remaining: '24 horas',
    targetDate: '2026-11-16',
    urgency: 'medium',
    owner: 'Revisor Humano',
  },
  {
    id: 'dl-03',
    title: 'Verificación de Turno en Tribunal Virtual (Mock)',
    remaining: '7 días hábiles',
    targetDate: '2026-11-25',
    urgency: 'low',
    owner: 'Chronos',
  },
];

export const REVIEW_GATE_STAGES = [
  { key: 'DRAFT', label: 'DRAFT', description: 'Borrador editable' },
  { key: 'IN_REVIEW', label: 'IN_REVIEW', description: 'Revisión humana' },
  { key: 'APPROVED', label: 'APPROVED', description: 'Aprobado por abogado/a' },
  { key: 'SUBMITTED', label: 'SUBMITTED', description: 'Enviado a mock' },
  { key: 'RECEIPTED', label: 'RECEIPTED', description: 'Acuse emitido' },
];

/**
 * Pure synchronous SHA-256 implementation (UTF-8 input -> lowercase hex digest).
 * Ensures deterministic, verifiable hash-chaining across all environments.
 */
export function sha256Hex(message) {
  const bytes = new TextEncoder().encode(message);
  const K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ];
  const H = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
  ];

  const bitLen = bytes.length * 8;
  const paddedLen = Math.ceil((bytes.length + 9) / 64) * 64;
  const padded = new Uint8Array(paddedLen);
  padded.set(bytes);
  padded[bytes.length] = 0x80;

  const view = new DataView(padded.buffer);
  view.setUint32(paddedLen - 8, Math.floor(bitLen / 0x100000000), false);
  view.setUint32(paddedLen - 4, bitLen >>> 0, false);

  const w = new Uint32Array(64);
  for (let offset = 0; offset < paddedLen; offset += 64) {
    for (let i = 0; i < 16; i += 1) {
      w[i] = view.getUint32(offset + i * 4, false);
    }
    for (let i = 16; i < 64; i += 1) {
      const s0 =
        ((w[i - 15] >>> 7) | (w[i - 15] << 25)) ^
        ((w[i - 15] >>> 18) | (w[i - 15] << 14)) ^
        (w[i - 15] >>> 3);
      const s1 =
        ((w[i - 2] >>> 17) | (w[i - 2] << 15)) ^
        ((w[i - 2] >>> 19) | (w[i - 2] << 13)) ^
        (w[i - 2] >>> 10);
      w[i] = (w[i - 16] + s0 + w[i - 7] + s1) >>> 0;
    }

    let [a, b, c, d, e, f, g, h] = H;
    for (let i = 0; i < 64; i += 1) {
      const S1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7));
      const ch = (e & f) ^ (~e & g);
      const temp1 = (h + S1 + ch + K[i] + w[i]) >>> 0;
      const S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = (S0 + maj) >>> 0;

      h = g;
      g = f;
      f = e;
      e = (d + temp1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) >>> 0;
    }

    H[0] = (H[0] + a) >>> 0;
    H[1] = (H[1] + b) >>> 0;
    H[2] = (H[2] + c) >>> 0;
    H[3] = (H[3] + d) >>> 0;
    H[4] = (H[4] + e) >>> 0;
    H[5] = (H[5] + f) >>> 0;
    H[6] = (H[6] + g) >>> 0;
    H[7] = (H[7] + h) >>> 0;
  }

  return H.map((val) => val.toString(16).padStart(8, '0')).join('');
}

export function computeAuditPayloadString(entry) {
  return JSON.stringify({
    id: entry.id,
    timestamp: entry.timestamp,
    actor: entry.actor,
    action: entry.action,
    matterId: entry.matterId,
    stage: entry.stage,
    detail: entry.detail,
    prevHash: entry.prevHash,
  });
}

export function appendHashChainedEvent(existingEvents, eventInput) {
  const prevHash = existingEvents.length > 0 ? existingEvents[existingEvents.length - 1].entryHash : '0'.repeat(64);
  const nextIndex = existingEvents.length + 1;
  const draftEntry = {
    id: `evt-${String(nextIndex).padStart(3, '0')}`,
    timestamp: eventInput.timestamp || new Date().toISOString(),
    actor: eventInput.actor,
    action: eventInput.action,
    actionLabel: eventInput.actionLabel,
    matterId: eventInput.matterId || SYNTHETIC_CASE.caseId,
    stage: eventInput.stage,
    detail: eventInput.detail,
    prevHash,
  };
  const entryHash = sha256Hex(computeAuditPayloadString(draftEntry));
  return [...existingEvents, { ...draftEntry, entryHash }];
}

export function verifyAuditChain(events) {
  let expectedPrev = '0'.repeat(64);
  for (let i = 0; i < events.length; i += 1) {
    const entry = events[i];
    if (entry.prevHash !== expectedPrev) {
      return { valid: false, brokenIndex: i };
    }
    const recomputed = sha256Hex(computeAuditPayloadString(entry));
    if (recomputed !== entry.entryHash) {
      return { valid: false, brokenIndex: i };
    }
    expectedPrev = entry.entryHash;
  }
  return { valid: true, brokenIndex: -1 };
}

function buildInitialAuditEvents() {
  let chain = [];
  chain = appendHashChainedEvent(chain, {
    timestamp: '2026-11-15T18:00:00.000Z',
    actor: 'Hermes · Ingesta',
    action: 'SYNTHETIC_CASE_SEEDED',
    actionLabel: 'Expediente sintético inicializado en sandbox',
    matterId: SYNTHETIC_CASE.caseId,
    stage: 'DRAFT',
    detail: 'Cargados 3 anexos ficticios sin PII real (ANX-SINT-01..03).',
  });
  chain = appendHashChainedEvent(chain, {
    timestamp: '2026-11-15T18:02:15.000Z',
    actor: 'Themis · Evaluación',
    action: 'FACT_HYPOTHESIS_SEPARATED',
    actionLabel: 'Hechos fácticos aislados de conclusiones preliminares',
    matterId: SYNTHETIC_CASE.caseId,
    stage: 'DRAFT',
    detail: '3 piezas documentales marcadas como pendientes de validación humana.',
  });
  chain = appendHashChainedEvent(chain, {
    timestamp: '2026-11-15T18:05:40.000Z',
    actor: 'Dike · Redacción',
    action: 'DRAFT_RENDERED_J2',
    actionLabel: 'Borrador ensamblado con solicitud_general.j2',
    matterId: SYNTHETIC_CASE.caseId,
    stage: 'DRAFT',
    detail: 'Promoción sintética generada con protección SubmissionBlockedError activa.',
  });
  return chain;
}

export const INITIAL_AUDIT_EVENTS = buildInitialAuditEvents();

export function buildDraftDocumentPreview(caseData, gateState, evidenceItems) {
  const validatedCount = evidenceItems.filter((item) => item.validationStatus === 'VALIDATED').length;
  const watermarkLabel =
    gateState.status === 'APPROVED' || gateState.status === 'SUBMITTED' || gateState.status === 'RECEIPTED'
      ? `VALIDADO POR ${gateState.approvedBy?.toUpperCase() || 'ABOGADO/A'} · USO MOCK`
      : 'BORRADOR SINTÉTICO · PROHIBIDA SU PRESENTACIÓN SIN APROBACIÓN HITL';

  const bodyLines = [
    `EXPEDIENTE SINTÉTICO: ${caseData.caseId}`,
    `AUTORIDAD DESTINO: ${caseData.authority}`,
    `JUZGADO SIMULADO: ${caseData.courtRoom}`,
    '',
    `PARTE ACTORA (SINTÉTICA): ${caseData.plaintiff} (RFC ${caseData.plaintiffRfc})`,
    `PARTE DEMANDADA (SINTÉTICA): ${caseData.defendant} (RFC ${caseData.defendantRfc})`,
    `DOMICILIO PROCESAL SIMULADO: ${caseData.syntheticAddress}`,
    '',
    'OBJETO DE LA PROMOCIÓN (solicitud_general.j2):',
    `Por medio del presente escrito generado en entorno de simulación controlado, la parte actora ${caseData.plaintiff} solicita se tengan por desahogadas las diligencias preparatorias y de requerimiento respecto del adeudo sintético por ${caseData.syntheticClaimAmount} vinculado a la referencia ficticia ${caseData.syntheticAccountRef}.`,
    '',
    'ANEXOS FACTUALES VINCULADOS:',
    ...evidenceItems.map(
      (ev, idx) =>
        `${idx + 1}. ${ev.title} (${ev.folio}) — Validación humana: ${
          ev.validationStatus === 'VALIDATED'
            ? `VALIDADO (${ev.validatedBy || 'Revisor'})`
            : ev.validationStatus === 'FLAGGED'
              ? 'OBSERVADO'
              : 'PENDIENTE'
        }`
    ),
    '',
    `ESTADO DE COMPUERTA HITL: ${gateState.status}${
      gateState.receiptFolio ? ` · FOLIO ACUSE: ${gateState.receiptFolio}` : ''
    }`,
    `PROTESTA SIMULADA: Se protesta lo necesario únicamente para fines de demostración académica y prueba técnica en LegalTech Innovation Lab.`,
  ];

  const templateBindings = {
    matter_id: caseData.caseId,
    authority: caseData.authority,
    plaintiff: caseData.plaintiff,
    defendant: caseData.defendant,
    claim_amount_mock: caseData.syntheticClaimAmount,
    validated_evidence_count: `${validatedCount}/${evidenceItems.length}`,
    review_gate_status: gateState.status,
    approved_by: gateState.approvedBy || 'null (SubmissionBlockedError activo)',
    receipt_folio: gateState.receiptFolio || 'null',
  };

  return {
    watermarkLabel,
    renderedText: bodyLines.join('\n'),
    templateBindings,
    validatedCount,
  };
}
