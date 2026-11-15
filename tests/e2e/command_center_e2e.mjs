import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..', '..');
const COMMAND_CENTER_DIR = path.join(REPO_ROOT, 'apps', 'command-center');
const DIST_DIR = path.join(COMMAND_CENTER_DIR, 'dist');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
};

function loadPlaywright() {
  const require = createRequire(import.meta.url);
  const candidatePaths = [
    path.join(COMMAND_CENTER_DIR, 'node_modules'),
    path.join(REPO_ROOT, 'node_modules'),
    '/Users/user/node_modules',
  ];
  const resolved = require.resolve('playwright', { paths: candidatePaths });
  return require(resolved);
}

function ensureBuiltDist() {
  const indexPath = path.join(DIST_DIR, 'index.html');
  if (!fs.existsSync(indexPath)) {
    execFileSync('npm', ['run', 'build'], {
      cwd: COMMAND_CENTER_DIR,
      stdio: 'pipe',
    });
  }
  if (!fs.existsSync(indexPath)) {
    throw new Error(`Missing built frontend bundle at ${indexPath}`);
  }
}

function startStaticServer(rootDir) {
  const server = http.createServer((req, res) => {
    const cleanUrl = (req.url || '/').split('?')[0];
    const relPath = cleanUrl === '/' ? 'index.html' : cleanUrl.replace(/^\/+/, '');
    let filePath = path.resolve(rootDir, relPath);
    if (!filePath.startsWith(rootDir)) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }
    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
      filePath = path.join(rootDir, 'index.html');
    }
    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'application/octet-stream' });
    fs.createReadStream(filePath).pipe(res);
  });

  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const addr = server.address();
      resolve({ server, url: `http://127.0.0.1:${addr.port}` });
    });
  });
}

async function launchChromium(chromium) {
  if (process.env.CI) {
    return chromium.launch({ headless: true });
  }
  try {
    return await chromium.launch({ headless: true });
  } catch {
    return chromium.launch({ headless: true, channel: 'chrome' });
  }
}

function assertCondition(condition, message) {
  if (!condition) {
    throw new Error(`E2E Assertion Failed: ${message}`);
  }
}

async function main() {
  ensureBuiltDist();
  const { chromium } = loadPlaywright();
  const { server, url } = await startStaticServer(DIST_DIR);
  const browser = await launchChromium(chromium);

  const browserErrors = [];
  const checks = [];

  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 960 } });
    const page = await context.newPage();

    page.on('pageerror', (err) => browserErrors.push(`pageerror: ${err.message}`));
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        browserErrors.push(`console.error: ${msg.text()}`);
      }
    });

    await page.goto(url, { waitUntil: 'networkidle' });

    // Check 1: Synthetic Case & Privacy Lock Verification
    const caseIdText = (await page.locator('.case-id-tag').textContent())?.trim();
    const safetyText = (await page.locator('.safety-badge').textContent())?.trim();
    const privacyText = (await page.locator('.privacy-lock-banner').textContent())?.trim();
    assertCondition(caseIdText === 'EXP-SINT-2026-001', `Expected caseId EXP-SINT-2026-001, got ${caseIdText}`);
    assertCondition(
      safetyText?.includes('SIMULACIÓN SINTÉTICA · MOCK AUTHORITY'),
      `Missing synthetic safety badge text: ${safetyText}`
    );
    assertCondition(privacyText?.includes('Privacy Lock Activo'), 'Privacy Lock banner missing');
    checks.push('check_1_synthetic_case_and_privacy_lock');

    // Check 2: Epistemic Separation (Hechos vs Conclusiones) & Evidence Validation Counter
    const factHeader = await page.locator('.epistemic-fact').textContent();
    const conclusionHeader = await page.locator('.epistemic-conclusion').textContent();
    assertCondition(
      factHeader?.includes('1. Hecho Verificable Extraído') && factHeader?.includes('Hecho Extraído (Factual)'),
      'Fact card missing expected separation markers'
    );
    assertCondition(
      conclusionHeader?.includes('2. Análisis / Conclusión Jurídica (No vinculante)') &&
        conclusionHeader?.includes('Conclusión Jurídica Preliminar (Requiere Validación)'),
      'Conclusion card missing expected separation markers'
    );
    const initialCounter = (await page.locator('.evidence-inspector .counter-pill').textContent())?.trim();
    assertCondition(initialCounter === '0/3 validadas', `Expected initial counter 0/3 validadas, got ${initialCounter}`);
    await page.locator('.evidence-validation-bar button', { hasText: 'Validar' }).click();
    const updatedCounter = (await page.locator('.evidence-inspector .counter-pill').textContent())?.trim();
    assertCondition(updatedCounter === '1/3 validadas', `Expected updated counter 1/3 validadas, got ${updatedCounter}`);
    checks.push('check_2_epistemic_separation_and_validation');

    // Check 3: HITL Submission Block in DRAFT and IN_REVIEW
    const initialStage = (await page.locator('.gate-state-badge').textContent())?.trim();
    assertCondition(initialStage === 'DRAFT', `Expected initial HITL stage DRAFT, got ${initialStage}`);
    assertCondition(
      await page.locator('.gate-workspace .btn-submit-mock').isDisabled(),
      'Submit mock button must be disabled in DRAFT'
    );
    const guardText = await page.locator('.callout-guard').textContent();
    assertCondition(guardText?.includes('SubmissionBlockedError'), 'Missing SubmissionBlockedError guard callout');

    await page.getByRole('button', { name: /Enviar a Revisión \(IN_REVIEW\)/ }).click();
    const reviewStage = (await page.locator('.gate-state-badge').textContent())?.trim();
    assertCondition(reviewStage === 'IN_REVIEW', `Expected stage IN_REVIEW, got ${reviewStage}`);
    assertCondition(
      await page.locator('.gate-workspace .btn-submit-mock').isDisabled(),
      'Submit mock button must remain disabled in IN_REVIEW'
    );
    checks.push('check_3_hitl_blocked_before_approved');

    // Check 4: Nominal Lawyer Validation & Rejection Loop (IN_REVIEW -> DRAFT)
    await page.getByRole('button', { name: /Aprobar como Abogado\/a/ }).click();
    const alertText = (await page.locator('[role="alert"].inline-error').textContent())?.trim();
    assertCondition(
      alertText === 'Ingresa el nombre del abogado/a responsable antes de aprobar.',
      `Expected missing lawyer alert, got ${alertText}`
    );

    await page.locator('#hitl-rejection-reason').fill('Verificar cotejo sintético de Anexo ANX-SINT-02');
    await page.getByRole('button', { name: /Rechazar \(Devolver a DRAFT\)/ }).click();
    const returnedStage = (await page.locator('.gate-state-badge').textContent())?.trim();
    assertCondition(returnedStage === 'DRAFT', `Expected rejection to return to DRAFT, got ${returnedStage}`);
    const rejectionCallout = await page.locator('.callout-crimson').textContent();
    assertCondition(
      rejectionCallout?.includes('Devuelto a DRAFT por rechazo humano'),
      'Missing human rejection callout after returning to DRAFT'
    );
    checks.push('check_4_nominal_validation_and_rejection_loop');

    // Check 5: Human Approval (IN_REVIEW -> APPROVED) & Mock Submission (APPROVED -> RECEIPTED)
    await page.getByRole('button', { name: /Enviar a Revisión \(IN_REVIEW\)/ }).click();
    await page.locator('#hitl-lawyer-name').fill('Lic. Valeria Mendoza (Simulado)');
    await page.getByRole('button', { name: /Aprobar como Abogado\/a/ }).click();
    const approvedStage = (await page.locator('.gate-state-badge').textContent())?.trim();
    assertCondition(approvedStage === 'APPROVED', `Expected APPROVED stage, got ${approvedStage}`);

    const submitButton = page.locator('.gate-workspace button', { hasText: /Emitir \/ Presentar \(Mock\)/ });
    assertCondition(!(await submitButton.isDisabled()), 'Submit mock button must be enabled when APPROVED');
    await submitButton.click();

    const receiptStage = (await page.locator('.gate-state-badge').textContent())?.trim();
    const receiptFolio = (await page.locator('.receipt-folio-code').textContent())?.trim();
    assertCondition(receiptStage === 'RECEIPTED', `Expected RECEIPTED stage, got ${receiptStage}`);
    assertCondition(
      receiptFolio === 'MOCK-TV-EXP-SINT-2026-001-001',
      `Expected folio MOCK-TV-EXP-SINT-2026-001-001, got ${receiptFolio}`
    );
    checks.push('check_5_approval_and_mock_receipt');

    // Check 6: Append-Only SHA-256 Audit Timeline Integrity
    const integrityText = (await page.locator('.chain-integrity-badge.is-valid').textContent())?.trim();
    const auditEntriesCount = await page.locator('.audit-list .audit-entry').count();
    assertCondition(integrityText?.includes('SHA-256 Íntegra'), `Expected SHA-256 Íntegra badge, got ${integrityText}`);
    assertCondition(auditEntriesCount === 10, `Expected 10 audit entries after full cycle, got ${auditEntriesCount}`);
    checks.push('check_6_audit_timeline_integrity');

    assertCondition(browserErrors.length === 0, `Browser errors detected: ${browserErrors.join('; ')}`);

    console.log(
      JSON.stringify(
        {
          status: 'PASSED',
          checks_passed: checks.length,
          checks,
          case_id: caseIdText,
          evidence_validated_counter: updatedCounter,
          receipt_folio: receiptFolio,
          audit_entries_count: auditEntriesCount,
          audit_chain_valid: true,
          browser_errors: browserErrors,
        },
        null,
        2
      )
    );
  } finally {
    await browser.close();
    server.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
