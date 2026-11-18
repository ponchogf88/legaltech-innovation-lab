# Módulo de Cotización Dinámica de Honorarios Preliminares (Hoja de Encargo)

> [!TIP]
> **Modelo de Negocio Jurídico Moderno**: Ningún abogado debe regalar el estudio inicial del caso. Cuando el cliente envía su material, el sistema genera automáticamente una **Cotización de Estudio y Dictamen Estratégico** antes de redactar la demanda o contestación completa.

---

## 💰 Matriz de Cálculo de Honorarios Preliminares

```mermaid
flowchart LR
    subgraph Factores ["Factores de Ingesta Detectados"]
        F1["📄 Número de Fojas / Páginas"]
        F2["🎙️ Duración de Audios (Minutos)"]
        F3["⏳ Semáforo de Urgencia (Término Fatal)"]
        F4["💎 Cuantía del Litigio (Suerte Principal)"]
    end

    subgraph Calculadora ["Algoritmo de Honorarios de Estudio"]
        F1 & F2 & F3 & F4 --> Motor["⚙️ Motor de Cotización Preliminar\n(Reglas Base + Multiplicador de Urgencia)"]
    end

    subgraph Salida ["Propuesta Comercial Inmediata"]
        Motor --> Pro["📑 Hoja de Encargo / Cotización PDF"]
        Motor --> Link["💳 Enlace de Pago en Línea (Stripe / SPEI)"]
    end
```

---

## 📊 Fórmulas de Cotización por Parámetros

| Parámetro | Rango / Criterio | Tarifa Base Sugerida | Impacto en el Cálculo |
| :--- | :--- | :--- | :--- |
| **Volumen de Fojas** | 1 a 30 páginas<br>31 a 100 páginas<br>100+ fojas (Expediente voluminoso) | $1,500 MXN<br>$3,500 MXN<br>+$25 MXN por foja extra | Costo de análisis documental y compulsa de pruebas. |
| **Material Multimedia** | Hasta 15 min de audio<br>15 a 60 min de audio<br>60+ min (Llamadas completas) | Incluido en base<br>+$500 MXN<br>+$1,000 MXN | Procesamiento, transcripción y extracción fáctica. |
| **Factor de Urgencia** | Término > 8 días hábiles<br>Término entre 3 y 7 días<br>Término < 48 horas (Emergencia) | Factor 1.0 (Normal)<br>Factor 1.3 (+30%)<br>Factor 1.75 (+75%) | Compensación por trabajo urgente y nocturno del despacho. |
| **Cuantía del Asunto** | Menor a $100,000 MXN<br>$100,000 a $1,000,000 MXN<br>Mayor a $1,000,000 MXN | Tarifa Plana<br>+0.5% del reclamo<br>+1.0% del reclamo | Responsabilidad jurídica proporcional al riesgo del cliente. |

---

## 📑 Ejemplo de Propuesta Automática al Cliente

> **PROPUESTA DE ESTUDIO Y DICTAMEN ESTRATÉGICO**  
> **Cliente:** Inmobiliaria del Norte S.A. de C.V.  
> **Asunto:** Contestación de Juicio Ejecutivo Mercantil (Exp. 502/2026)  
> **Material Recibido:** 42 fojas escaneadas + 2 notas de voz (18 min).  
> **Vencimiento de Término:** 5 días hábiles (Urgencia Media).  
> 
> **Concepto:**  
> - Auditoría forense de pagaré y títulos de crédito adjuntos.  
> - Deliberación del Consejo Legal (Atenea, Sun Tzu y Sherlock Holmes).  
> - Emisión de Dictamen de Viabilidad y Borrador de Excepciones Procesales.  
> 
> **Inversión de Estudio Inicial:** **$4,850.00 MXN** *(IVA incluido)*  
> *(Este monto se acreditará al 100% como anticipo de honorarios si contrata la defensa integral del juicio).*  
> 
> [ 👉 Pagar Estudio del Caso con Tarjeta o SPEI ]

---

## 🛡️ Beneficios para el Abogado
1. **Cobro Inmediato**: Monetizas el tiempo de lectura, compulsa y análisis desde el minuto uno.
2. **Filtro de Clientes Serios**: El cliente que no paga un estudio inicial de bajo costo, difícilmente pagará los honorarios de un litigio largo.
3. **Formalidad Institucional**: Transmite seriedad corporativa, transparencia y rigor matemático en tus tarifas.
