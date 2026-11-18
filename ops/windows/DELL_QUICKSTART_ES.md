# Guía Rápida para AntiGravity Dell (Windows Lab)

## 1. Qué modelo poner en la Dell
* **Orquestador principal:** Pon la Dell en **Gemini 4 Argon (Máximo)**. Es quien lee `ORCHESTRATOR_INBOX.md`, `MULTI_NODE_HANDSHAKE.json`, `PROJECT_STATE.json`, revisa seguridad y coordina merges sin pisar archivos.
* **Implementación pesada de código:** Cuando Argon delegue edición masiva o conexión de API/flujos n8n, pasa ese bloque (o subagente) a **Gemini 4 Hydrogen (Ultracode / Máximo)**.

---

## 2. Instalación Única en Windows (Copiar y Pegar en PowerShell)
Si todavía no tienes clonado el repositorio maestro en la Dell:

```powershell
cd $env:USERPROFILE
git clone https://github.com/ponchogf88/legaltech-innovation-lab.git
cd legaltech-innovation-lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Registra la sincronización automática (al iniciar Windows, cada 15 minutos y diario a las `08:15`):

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\windows\register_dell_autopilot_task.ps1 -RepoPath "$env:USERPROFILE\legaltech-innovation-lab" -MorningTime "08:15"
```

---

## 3. Cómo activar alertas automáticas por correo electrónico (Opcional)
Para que Windows te mande un correo real cuando falte **última revisión humana** o haya una alerta crítica (sin guardar contraseñas en Git), define estas variables de entorno de usuario en Windows (usa una contraseña de aplicación de Gmail o tu SMTP):

```powershell
[Environment]::SetEnvironmentVariable("LEGAL_LAB_SMTP_HOST", "smtp.gmail.com", "User")
[Environment]::SetEnvironmentVariable("LEGAL_LAB_SMTP_PORT", "587", "User")
[Environment]::SetEnvironmentVariable("LEGAL_LAB_SMTP_USER", "tu_correo@gmail.com", "User")
[Environment]::SetEnvironmentVariable("LEGAL_LAB_SMTP_PASSWORD", "TU_APP_PASSWORD", "User")
[Environment]::SetEnvironmentVariable("LEGAL_LAB_ALERT_TO", "tu_correo_destino@gmail.com", "User")
```

Para disparar la prueba manual del sincronizador + alerta:

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\windows\sync_and_notify.ps1 -SendTestAlert
```

---

## 4. Prueba en Vivo de Comunicación Mac $\leftrightarrow$ Dell
En cuanto enciendas AntiGravity en la Dell, pégale esta única frase:

> **"Lee `ORCHESTRATOR_INBOX.md` y `MULTI_NODE_HANDSHAKE.json`, ejecuta la prueba de eco `expected_echo_command` y haz commit + push."**
