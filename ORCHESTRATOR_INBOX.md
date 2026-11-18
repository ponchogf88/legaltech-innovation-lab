# `ORCHESTRATOR_INBOX.md` — Buzón de Relevo Multi-Nodo (Mac / iMac / Windows Dell)

> **Fuente Única de Verdad:** `https://github.com/ponchogf88/legaltech-innovation-lab`  
> **Reloj Inmutable de 72 Horas:** `72H_CLOCK.json` (`2026-11-15T14:03:47-06:00` $\rightarrow$ `2026-11-18T14:03:47-06:00`)  
> **Recomendación de Modelo en Dell:** Orquestador en **Gemini 4 Argon (Máximo)**; tareas pesadas de código en **Hydrogen (Ultracode)**.

---

## 1. Protocolo de Arranque Automático para Cualquier Agente (Dell, MacBook o iMac)
Al abrir este repositorio en cualquier máquina, ejecuta en orden:

1. `git pull --ff-only origin dev/mission-002` (o `main` según rama activa indicada en `MULTI_NODE_HANDSHAKE.json`).
2. `python -m legal_engine.cli clock` y `python -m legal_engine.cli state` (nunca reinicies tareas que ya están en `DONE`).
3. Lee `MULTI_NODE_HANDSHAKE.json` y `CHECKPOINT.json`.
4. Si `active_ping_id` empieza con `PING-`, responde inmediatamente ejecutando `expected_echo_command` para confirmar comunicación real entre nodos, haz commit y `git push`.

---

## 2. Rutinas Activas Delegadas al Nodo Dell (`DELL_WINDOWS_LAB`)

| Rutina | Tarea Estado | Qué Debe Construir e Integrar la Dell | Criterio de Aceptación |
| :--- | :--- | :--- | :--- |
| **`ROUTINE-DELL-01`** | `M2-03` | Conectar los flujos n8n (`workflows/n8n/03..05_*.json`) y las alertas HITL con el puente SSE en tiempo real en `packages/legal_engine/api.py` hacia `apps/command-center/src/App.jsx`. | Endpoint SSE funcionando sin romper modo Sandbox Local ni `test_e2e_playwright.py`. |
| **`ROUTINE-DELL-02`** | `M2-02` | Completar spans estructurados OpenTelemetry en `intake.py`, `documents.py`, `review.py`, `submissions.py` y `api.py` (cero PII en atributos). | Pruebas unitarias de telemetría pasando + `security-check` limpio (`6/6`). |
| **`ROUTINE-DELL-03`** | `M2-05` | Implementar el **Cotizador Preliminar (Fase 1)** (`docs/dell_lab_sync/COTIZADOR_HONORARIOS_PRELIMINARES.md`) y el **Buzón Multimodal** (`BUZON_MULTIMODAL_OMNICANAL.md`) como módulos conectables sin romper los tests E2E existentes. | Nuevas pruebas verdes + `npm run build` + `pytest` al 100%. |

---

## 3. Regla de Alertamiento al Dueño (Atención / Última Revisión)
Al concluir cualquier rutina o quedar bloqueado en compuerta humana:
1. Actualiza `PROJECT_STATE.json`, `CHECKPOINT.json` (`python -m legal_engine.cli checkpoint --op "..."`), y ejecuta `python -m legal_engine.cli handoff --from-node DELL_WINDOWS_LAB --to-node MAC_COMMAND_CENTER --requires-review --note "..."`.
2. Dispara `python -m legal_engine.cli notify --level URGENT_REVIEW --title "..." --summary "..."`.
3. Haz `git push` limpio; **jamás fusiones cambios sin revisar a `main` si la compuerta de aprobación sigue abierta** ni expongas credenciales, FIEL o PII real.
