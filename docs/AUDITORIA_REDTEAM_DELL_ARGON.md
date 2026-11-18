# 🛡️ Auditoría Red Team y Reto de Autoreparación (DELL_WINDOWS_LAB → Mac)

> **Auditor:** Argon Orchestrator (`DELL_WINDOWS_LAB`)  
> **Fecha:** 2026-11-18  
> **Objetivo:** Verificar el avance real reportado en la Mac (`CHECKPOINT.json` al commit `3a4a47f`) y auditar el código fuente como atacante ético (*Red Team*) para detectar vulnerabilidades, brechas de privacidad y riesgos operativos.

---

## 1. Verificación del Avance Real Reportado (`CHECKPOINT.json`)

- **Rama auditada:** `dev/mission-002` y `main` (commit `3a4a47f` / `a4b33d1`)
- **Tareas completadas:** **17 / 17 DONE** (`M2-02` OTel spans, `M2-03` puente SSE, `M2-05` packs sintéticos, `75/75 pytest` reportados en la Mac).
- **Reloj de 72 horas:** `99.04%` transcurrido (`71h 18m 30s` ejecutados, `00h 41m 29s` restantes).
- **Veredicto inicial:** La funcionalidad modular y pruebas unitarias básicas sí están construidas en la Mac. Sin embargo, al aplicar pruebas ofensivas (*Red Team*), se detectaron **4 vulnerabilidades reales** que la batería actual de 75 pruebas **no detecta**.

---

## 2. Hallazgos Reales de la Auditoría Red Team

### 🔴 Hallazgo 1 (ALTA): Evasión de la Compuerta PII (`Nomos`) con Minúsculas y Espacios
- **Archivo:** [`packages/legal_engine/security.py`](../packages/legal_engine/security.py#L33-L36) (líneas 33–36)
- **Detalle Técnico:**
  - `_RFC_RE` y `_CURP_RE` compilan únicamente letras mayúsculas (`[A-ZÑ&]`) sin la bandera `re.IGNORECASE` (a diferencia de `_REAL_CASE_PATTERNS` en la línea 68 que sí la incluye). Un RFC o CURP real ingresado en minúsculas (`abcd` + `561231` + `gr8`) burla por completo `scan_text_for_pii_or_real_cases()`.
  - `_CLABE_RE` exige 18 dígitos continuos sin separadores (`\b\d{18}\b`). Una cuenta bancaria CLABE escrita con espacios o guiones (por ejemplo bloques `3-3-11-1` separados por espacios) evade la detección de fuga bancaria.
- **Prueba de Reto Sembrada:** [`tests/test_redteam_security_challenge.py`](../tests/test_redteam_security_challenge.py) (falla intencionalmente hasta que el agente en la Mac parchee `security.py` para detectar variantes en minúsculas y CLABEs formateadas sin romper `security-check`).

### 🔴 Hallazgo 2 (CRÍTICA): Denegación de Servicio (DoS) por `Content-Length` sin Límite
- **Archivo:** [`packages/legal_engine/api.py`](../packages/legal_engine/api.py#L371-L376) (líneas 371–376)
- **Detalle Técnico:**
  - `do_POST` convierte el encabezado `Content-Length` con `int(...)` sin capturar `ValueError` (un encabezado malformado rompe el hilo del servidor con excepción 500) y llama a `self.rfile.read(content_length)` sin un límite máximo de bytes (ej. 1 MB / 5 MB), permitiendo agotar la RAM con una sola petición HTTP grande o colgar el socket con un valor inflado.

### 🔴 Hallazgo 3 (CRÍTICA): Compuerta Humana sin Autenticación y CORS Abierto (`*`)
- **Archivo:** [`packages/legal_engine/api.py`](../packages/legal_engine/api.py#L225-L365) (líneas 225–365)
- **Detalle Técnico:**
  - Los endpoints `POST /api/submissions/<id>/approve` y `/submit` confían ciegamente en cualquier cadena enviada en el campo JSON `"reviewer"` sin verificar token, sesión ni firma criptográfica.
  - Todas las respuestas JSON y SSE envían `Access-Control-Allow-Origin: *`, lo cual permite que cualquier sitio web malicioso abierto en el navegador del usuario dispare aprobaciones locales vía CSRF contra `127.0.0.1:8790`.

### 🟠 Hallazgo 4 (ALTA): Condición de Carrera Multi-Proceso en Bitácora SHA-256
- **Archivo:** [`packages/legal_engine/audit.py`](../packages/legal_engine/audit.py#L28-L72) (líneas 28–72)
- **Detalle Técnico:**
  - `AuditLog` protege las lecturas y escrituras al archivo `.audit.jsonl` únicamente con `threading.Lock()` en memoria. Si dos procesos concurrentes (por ejemplo servidor HTTP + CLI o webhook n8n) registran eventos simultáneamente, ambos leerán el mismo `prev_hash` y corromperán la cadena de integridad SHA-256. Se requiere bloqueo de archivo a nivel de sistema operativo (`fcntl` / `msvcrt` o SQLite transaccional).

---

## 3. Instrucción del Reto para el Agente de la Mac

Al despertar tu agente en la Mac (`dev/mission-002` / `main`), pídele únicamente:
> *«Haz `git pull` de GitHub y corre `pytest` para verificar si todo el sistema está sano.»*

El agente deberá:
1. Detectar los **2 fallos rojos reales** en `tests/test_redteam_security_challenge.py`.
2. Reconocer que `packages/legal_engine/security.py` permite evadir el guardián de PII (`RFC`/`CURP` en minúsculas y `CLABE` con espacios/guiones).
3. Parchear `security.py` (y opcionalmente endurecer `api.py` y `audit.py`) sin borrar ni relajar la prueba Red Team, dejando `security-check` y toda la suite en verde.
