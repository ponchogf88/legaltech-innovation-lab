# Ingesta Inteligente de Demandas y Acuerdos Judiciales (Arquitectura Híbrida)

> [!TIP]
> **Optimización de Costos y Latencia**: No todos los documentos requieren un modelo de razonamiento pesado. Usar un **modelo rápido y económico para OCR visual** y reservar el **modelo de razonamiento profundo solo para el análisis estratégico de litigios complejos** hace que tu plataforma sea instantánea y de costo casi nulo ($0).

---

## 🏛️ Diagrama del Flujo de Ingesta y Enrutamiento

```mermaid
flowchart TD
    A["📄 Llegada de Caso (PDF escaneado / Fotos de Demanda)"] --> B["⚡ Gemini 2.5 Flash\nOCR Multimodal Nativo (<2s)"]

    subgraph Extraccion ["Fase 1: Extracción Inmediata"]
        B --> C1["Número de Expediente y Juzgado"]
        B --> C2["Sello de Notificación y Fechas"]
        B --> C3["Partes: Actor vs. Demandado"]
        B --> C4["Clasificación: ¿Trámite Simple o Demanda Compleja?"]
    end

    C4 --> D{"🔀 Enrutador Inteligente"}

    D -->|"Acuerdo de Trámite Simple\n(Notificación de rutina, copias)"| E["📋 Ficha de Trámite Rápida\n(Gemini Flash - Archivo & Notificación)"]
    
    D -->|"Demanda Inicial / Emplazamiento / Amparo\n(Riesgo Alto - Término Fatal)"| F["🧠 Gemini 2.5 Pro + Thinking Mode\n(El Consejo Estratégico)"]

    subgraph Consejo ["Fase 2: Razonamiento Forense Profundo"]
        F --> S1["🔍 Sherlock Holmes: Hallazgo de contradicciones y documentos apócrifos"]
        F --> S2["⏳ Sun Tzu: Cómputo de días hábiles y estrategia de desgaste"]
        F --> S3["🛡️ Atenea: Redacción de excepciones dilatorias y reconvención"]
    end

    E --> G["📱 Panel del Abogado & Alerta Telegram"]
    Consejo --> G
```

---

## 🔍 Desglose de los Dos Tiers

### 1. Tier Rápido: OCR Multimodal (Gemini 2.5 Flash)
- **El problema del OCR tradicional**: Los motores OCR antiguos (Tesseract, Adobe) fallan miserablemente con sellos borrosos de juzgados, hojas chuecas o anotaciones manuales al margen.
- **La solución de Gemini Flash**: Gemini 2.5 Flash tiene **visión multimodal nativa**. No hace OCR texto por texto; "mira" el documento como un humano, lee el sello de tinta morada del actuario, entiende la caligrafía y extrae en 1.5 segundos:
  - Fecha en que surte efectos la notificación.
  - Vía del juicio (Ejecutivo Mercantil, Oral Civil, Laboral, etc.).
  - Monto exacto de las prestaciones reclamadas.

### 2. Tier de Razonamiento Profundo: El Senado Legal (Gemini 2.5 Pro)
Si el documento es una **demanda formal**, el sistema no se conforma con resumir: activa el razonamiento profundo:
- **Cómputo Fatal**: Identifica si tienes 8, 9, 15 o 30 días para contestar, descontando fines de semana e inhábiles del calendario judicial.
- **Filtro de Excepciones**: Evalúa de inmediato si procede promover:
  - Incompetencia de jurisdicción.
  - Falta de personalidad en el apoderado del actor.
  - Oscuridad de la demanda.
- **Borrador de Contestación**: Redacta el capítulo de hechos contestando punto por punto (*"Es falso y se niega..."*) con las pruebas que Sherlock detecte necesarias.

---

## 📂 Archivo de Configuración Listo

El flujo completo de n8n con los nodos y prompts calibrados quedó guardado en:  
[`04_ingesta_demandas_ocr_enrutador_ia.json`](file:///C:/Users/USUARIO/laboratorio-asistente-ia/workflows/04_ingesta_demandas_ocr_enrutador_ia.json)
