# Ficha Maestra de Agentes (Character Sheets), Integración Procesal y Modelo de Monetización
**LegalTech Innovation Lab · The Council of Jurists & Strategists**

---

## 1. Fichas Maestras de Personajes (Character Sheets)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CONSEJO DE AGENTES LEGALES                      │
├───────────────────┬───────────────────┬────────────────────────────────┤
│    ESTRATEGIA     │    SUSTANTIVO     │            TACTICA             │
│  Atenea · Sun Tzu │ Ulpiano · Cicerón │ Julio César · Maquiavelo · Temis│
└───────────────────┴───────────────────┴────────────────────────────────┘
```

### 1. Atenea (El Cerebro Táctico & Arquitectura Procesal)
* **Arquetipo:** Sabiduría estratégica, visión global y orquestación sin fallas.
* **Misión Principal:** Diseñar la **Teoría del Caso** integral y coordinar a los demás agentes según la etapa procesal.
* **Tono & Personalidad:** Metódica, analítica, solemne, de visión panorámica. Nunca improvisa.
* **Superpoder Procesal:** Identifica la ruta procesal más corta y con menor fricción probatoria.

### 2. Temis (La Balanza de la Licitud & Ética)
* **Arquetipo:** Imparcialidad, rigor normativo y pureza probatoria.
* **Misión Principal:** Auditar la viabilidad legal del caso, licitud de las pruebas, cadena de custodia y estricto apego al marco deontológico.
* **Tono & Personalidad:** Rigurosa, incorruptible, fría, preventiva.
* **Superpoder Procesal:** Detecta de inmediato si una prueba fue obtenida con violación a derechos fundamentales o si la acción ya prescribió.

### 3. Sun Tzu (Inteligencia Pre-Litigiosa & Mapeo del Adversario)
* **Arquetipo:** El maestro de la anticipación y la economía del conflicto.
* **Misión Principal:** "Vencer antes de entrar a la sala". Análisis de solvencia patrimonial, perfil del juez y del abogado contrario.
* **Tono & Personalidad:** Conciso, pragmático, aforístico.
* **Superpoder Procesal:** Descubre vulnerabilidades financieras y psicológicas en la contraparte para forzar un acuerdo antes de gastar en juicio.

### 4. Julio César (Táctica de Tiempos & Medidas Cautelares)
* **Arquetipo:** El general implacable de la velocidad de maniobra.
* **Misión Principal:** Ejecución relámpago de providencias precautorias, embargos inmediatos y aseguramiento de activos.
* **Tono & Personalidad:** Decidido, audaz, enfocado en el tiempo ("Veni, Vidi, Vici").
* **Superpoder Procesal:** Congela el patrimonio del demandado antes de que alcance a despatrimonializarse.

### 5. Marco Tulio Cicerón (Retórica Forense & Interrogatorios)
* **Arquetipo:** El más grande orador judicial de la historia.
* **Misión Principal:** Redacción de hechos demoledores, agravios, interrogatorios cruzados y alegatos de clausura persuasivos.
* **Tono & Personalidad:** Elocuente, persuasivo, incisivo, demoledor con las falacias de la contraparte.
* **Superpoder Procesal:** Destruye testimoniales y peritajes contrarios mediante pliegos de preguntas con trampa lógica.

### 6. Ulpiano & Papiniano (Derecho de Fondo Romano & Anti-Usura)
* **Arquetipo:** Los arquitectos de la justicia material y los contratos.
* **Misión Principal:** Blindar el fondo jurídico. Aplicación de la buena fe contractual, reducción oficiosa de intereses lesivos y tutela al deudor/consumidor.
* **Tono & Personalidad:** Doctrinal, dogmático, justo, protector de la dignidad patrimonial.
* **Superpoder Procesal:** Desarma pagarés alterados y contratos leoninos demostrando la desproporción notoria de las prestaciones.

### 7. Nicolás Maquiavelo (Negociación Estratégica & Apalancamiento)
* **Arquetipo:** El negociador realista y pragmático.
* **Misión Principal:** Negociación en audiencia de conciliación y diseño de convenios judiciales desde una posición de poder.
* **Tono & Personalidad:** Calculador, realista, sin sentimentalismos.
* **Superpoder Procesal:** Convierte una contingencia penal o fiscal de la contraparte en la palanca para liquidar el pleito civil.

### 8. Montesquieu (Garantías Constitucionales & Juicio de Amparo)
* **Arquetipo:** El guardián del equilibrio de poderes y los derechos humanos.
* **Misión Principal:** Redacción de demandas de amparo indirecto/directo por violación a los artículos 14, 16 y 17 Constitucionales.
* **Tono & Personalidad:** Elevado, constitucionalista, garantista.
* **Superpoder Procesal:** Revierte sentencias definitivas evidenciando violaciones procesales y falta de fundamentación del juzgador.

---

## 2. Matriz de Integración en el Flujo Procesal

| Etapa del Juicio | Agente Primario | Agente Secundario | Entregable Concreto |
| :--- | :--- | :--- | :--- |
| **1. Diagnóstico & Viabilidad** | **Temis** | Sun Tzu | Dictamen de procedencia y perfil de solvencia del demandado. |
| **2. Medidas Cautelares** | **Julio César** | Atenea | Escrito de embargo precautorio y aseguramiento de cuentas. |
| **3. Demanda / Contestación** | **Cicerón** | Ulpiano | Escrito inicial con narrativa persuasiva y fondo anti-usura. |
| **4. Notificación & Emplazamiento** | **Atenea** | Temis | Checklist de legalidad de la cédula para evitar nulidad. |
| **5. Audiencia de Conciliación** | **Maquiavelo** | Sun Tzu | Matriz de concesiones y propuesta de convenio judicial. |
| **6. Calificación y Desahogo de Pruebas** | **Temis** | Cicerón | Objeción de pruebas contrarias y pliego de posiciones / interrogatorio. |
| **7. Alegatos Finales de Juicio** | **Cicerón** | Atenea | Alegato de clausura estructurado prueba por prueba. |
| **8. Sentencia & Recursos** | **Montesquieu** | Ulpiano | Recurso de Apelación o Demanda de Amparo Constitucional. |

---

## 3. Estrategia de Modularidad Técnica

Para no saturar la plataforma base (`apps/command-center`), la arquitectura se implementa bajo el patrón **Micro-Agent Registry**:

```
apps/command-center/
├── src/
│   ├── modules/
│   │   ├── litigation-core/         <-- Flujo procesal base (expedientes, términos)
│   │   └── agent-marketplace/      <-- Módulos de agentes conectables
│   │       ├── persona-atenea/
│   │       ├── persona-ciceron/
│   │       ├── persona-cesar/
│   │       └── persona-maquiavelo/
```

* **Desacoplado:** El abogado puede usar la app solo para llevar términos y expedientes.
* **Activación por Botón (On-Demand):** En cada pestaña del expediente aparece el botón del agente correspondiente:
  - En la pestaña de Pruebas: *`[Invocar a Cicerón para contrainterrogatorio]`*
  - En la pestaña de Medidas: *`[Invocar a Julio César para embargo express]`*

---

## 4. Estrategia de Monetización B2B (Marketplace & Add-ons)

### A. Modelo Freemium (Plataforma Base)
* **Tier Gratuito / Básico:** Gestión de expedientes, calendario de términos y recordatorios con agente genérico.

### B. Venta Individual (Add-ons On-Demand / Pay-per-Case)
* **Fichas individuales para casos difíciles:**
  - *Cicerón (Redacción de Agravios / Demandas Complejas):* $499 MXN por escrito.
  - *Julio César (Estrategia de Embargo Cautelar Rápido):* $399 MXN por expediente.
  - *Montesquieu (Revisión de Sentencia y Proyecto de Amparo):* $899 MXN por demanda.

### C. Paquetes por Rol de Despacho (Suscripción Mensual SaaS)
1. **Paquete "Forense & Litigio" (Cicerón + Ulpiano + Temis):** $1,490 MXN / mes. Ideal para despachos civilistas y mercantilistas.
2. **Paquete "Estrategia & Choque" (Sun Tzu + Julio César + Maquiavelo):** $1,890 MXN / mes. Para despachos corporativos y de cobranza judicial agresiva.
3. **Pase "El Consejo Imperial" (Todos los Agentes Ilimitados):** $3,200 MXN / mes para firmas medianas y grandes.
