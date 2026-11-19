# Dossiers Metodológicos del Consejo de Jurisconsultos & Lentes Adversariales (`docs/personas/`)

> **Propósito de Garantía Epistémica:** Que el abogado usuario conozca exactamente **de dónde nace el criterio de cada personaje**, qué fuentes jurídicas verificables utiliza, qué técnica argumentativa aplica y cuáles son sus **límites éticos y constitucionales inviolables** antes de invocarlo en el **Reasoning Room**.

---

## 1. Regla Madre de Confiabilidad (Por Qué Puedes Confiar en el Razonamiento)

Todo avatar —histórico o estratégico moderno— opera bajo **cinco candados duros del sistema** (`packages/legal_engine/`):

| Candado Técnico | Garantía Verificable en Código | Qué Evita |
| :--- | :--- | :--- |
| **1. Separación Epistémica** | [`models.py`](../../packages/legal_engine/models.py) (`EvidenceItem.extracted_fact` vs `legal_conclusion`) | Mezclar hechos literales del expediente con suposiciones o hipótesis argumentativas. |
| **2. Guardián Anti-Alucinación en Plantillas** | [`documents.py`](../../packages/legal_engine/documents.py) (`jinja2.StrictUndefined`) | Que un escrito salga con variables vacías o datos inventados. |
| **3. Control Humano Obligatorio (`HITL`)** | [`submissions.py`](../../packages/legal_engine/submissions.py) (`SubmissionBlockedError`) | Despacho automático sin firma nominal y aprobación expresa del abogado responsable. |
| **4. Reconfiguración Manual Soberana (`Manual Override`)** | [`router.py`](../../packages/legal_engine/router.py) (`select_reasoning_room_avatars`) | Que la IA imponga personajes rígidos: aunque el asunto sea *Familiar*, el abogado puede activar manualmente a *Saul Goodman* u otro perfil. |
| **5. Auditoría Inmutable y Cero PII** | [`audit.py`](../../packages/legal_engine/audit.py) + [`security.py`](../../packages/legal_engine/security.py) | Fuga de RFC, CURP, CLABE o expedientes reales y alteración de bitácoras. |

---

## 2. Mapa de Dossiers por Estrato

1. **[Estrato I · Deidades Éticas y Arquitectura Procesal](./ESTRATO_I_DEIDADES_ETICA_ESTRATEGIA.md)**  
   * *Temis* (licitud probatoria), *Atenea* (teoría del caso) y *Hermes* (boletines PJENL/CJF y cómputo exacto de términos).
2. **[Estratos II y III · Jurisconsultos Históricos e Ilustración](./ESTRATO_II_III_JURISTAS_HISTORICOS.md)**  
   * *Ulpiano & Papiniano*, *Marco Tulio Cicerón*, *Justiniano I & Triboniano*, *Julio César*, *Alejandro Magno*, *Montesquieu*, *Fray Luca Pacioli* e *Irnerio de Bolonia*.
3. **[Estratos IV y V · Inteligencia Forense, Lentes Cinematográficos & Advocatus Diaboli](./ESTRATO_IV_V_LENTES_MODERNOS_Y_ADVERSARIALES.md)**  
   * *Sherlock Holmes*, *Maquiavelo*, *Sun Tzu*, *Craso* + los Lentes de Alta Tensión del **Reasoning Room**: ***Saul Goodman***, ***El Abogado del Diablo (Advocatus Diaboli)***, ***Arquetipo Tony Montana (Red Team)***, ***Harvey Specter*** y ***Annalise Keating***.
