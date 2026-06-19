# ICBC - Sistema de Prevención de Fraudes End-to-End

> **Proyecto de portfolio profesional** que simula un entorno bancario real de prevención de fraudes,  
> cubriendo desde la ingesta de datos transaccionales hasta la operación de un motor de riesgo y su visualización ejecutiva.

---

## Objetivo del Proyecto

Diseñar e implementar un sistema de monitoreo y prevención de fraudes transaccionales que replica la arquitectura lógica utilizada por motores de riesgo corporativos como **Thales**, **Kount** y **DRS**, aplicado a los medios de pago más relevantes del ecosistema financiero argentino:

- 💳 Tarjetas de crédito y débito
- 🏧 Transferencias inmediatas (CVU/CBU)
- 📱 Billeteras digitales
- 🔁 DEBIN (Débito Inmediato)

---

## Stack Tecnológico

| Capa | Herramienta | Rol en el proyecto |
|---|---|---|
| Generación de datos | Python + Faker + Pandas | Simulación de transacciones sintéticas realistas |
| Staging | CSV estructurados | Capa raw auditable — emula ingesta desde core bancario |
| Base de datos | SQL Server + VSC (`mssql`) | Modelo relacional, vistas analíticas, Z-score, ventanas móviles |
| Motor de riesgo | Python (módulo `risk_engine`) | Simulación de Kount/Thales: Enrichment → Rules → Orquestación |
| Análisis exploratorio | Jupyter Notebooks (VSC) | EDA de fraude, distribuciones, correlaciones |
| Visualización | Power BI | Dashboard operativo de alertas y KPIs para Gerencia de Riesgos |
| Control de versiones | Git + GitHub | Trazabilidad completa de cada decisión técnica |

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        FUENTE DE DATOS                          │
│          Python script → CSV raw (emula core bancario)          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ BULK INSERT
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL SERVER — MODELO FÍSICO                   │
│                                                                 │
│  fact_transacciones  │  dim_perfil_usuarios  │  dim_dispositivos│
│                                                                 │
│           vista_alertas_monitoreo (REVIEW / DECLINE)            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│               MOTOR DE RIESGO (Python — src/)                   │
│                                                                 │
│  [1] Data Enrichment      → Variables dinámicas en ventana      │
│  [2] Decision Engine      → ABM de reglas con puntaje de riesgo │
│  [3] Orquestación         → APPROVE / REVIEW / DECLINE          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    POWER BI — DASHBOARD                         │
│   KPIs: FPR · FNR · Monto salvado · Alertas por canal          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Motor de Riesgo - Lógica de Decisión

El módulo `src/risk_engine.py` simula las tres capas operativas de plataformas como Kount y Thales:

### Capa 1 - Data Enrichment (Atributos Dinámicos)
Calcula en tiempo real variables contextuales sobre la transacción entrante:
- Conteo de transacciones del usuario en los últimos 10 / 30 / 60 minutos
- Z-score del monto respecto al perfil histórico del usuario
- Coincidencia de dispositivo con huella histórica (`dim_dispositivos_huella`)
- Detección de IP/geolocalización anómala

### Capa 2 - Decision Engine (ABM de Reglas)
Matriz de reglas configurables en `config/rules.json`:

| ID Regla | Condición | Score asignado |
|---|---|---|
| R001 | Monto > percentil 95 del usuario AND dispositivo nuevo | +40 pts |
| R002 | Z-score del monto > 3 en DEBIN o transferencia | +50 pts |
| R003 | Más de 5 transacciones en 10 minutos | +35 pts |
| R004 | País/IP inconsistente con perfil histórico | +45 pts |
| R005 | Primer uso de tarjeta en comercio de alto riesgo | +30 pts |

### Capa 3 - Orquestación (Resolución Final)

```
Score < 30   →  ✅ APPROVE   — Transacción liberada
Score 31-75  →  ⚠️  REVIEW    — Alerta generada → SQL Server → Power BI
Score > 75   →  🚫 DECLINE   — Bloqueo automático preventivo
```

---

## 📁 Estructura del Repositorio

```
icbc-fraude-prevencion/
│
├── 📁 data/
│   ├── raw/                  ← CSVs generados por Python (no modificar)
│   └── processed/            ← CSVs limpios listos para SQL Server
│
├── 📁 sql/
│   ├── ddl/                  ← CREATE TABLE, CREATE VIEW, índices
│   └── dml/                  ← Queries analíticas, Z-score, ventanas móviles
│
├── 📁 notebooks/
│   ├── 01_EDA_fraude.ipynb   ← Análisis exploratorio de transacciones
│   └── 02_motor_reglas.ipynb ← Prototipado del motor de riesgo
│
├── 📁 src/
│   ├── data_generator.py     ← Generador de datos sintéticos (Faker)
│   ├── etl_pipeline.py       ← Limpieza y carga a SQL Server
│   └── risk_engine.py        ← Motor de riesgo (3 capas)
│
├── 📁 config/
│   └── rules.json            ← ABM de reglas del motor (configurable)
│
├── 📁 power_bi/
│   └── dashboard_icbc.pbix   ← Dashboard operativo de alertas
│
├── 📁 docs/
│   ├── arquitectura.png      ← Diagrama del sistema
│   └── decisiones_tecnicas.md← ADR (Architecture Decision Records)
│
└── 📄 README.md              ← Este archivo
```

---

## Plan de Ejecución - Hitos

### Fase 0 - Arquitectura y Planificación
-  Definición de stack tecnológico
-  Diseño de arquitectura del sistema
-  Estructura del repositorio
-  Documento de planificación (Notion + README)

### Fase 1 - SQL Server & Modelo de Datos
- [ ] Scripts DDL: `fact_transacciones`, `dim_perfil_usuarios_historico`, `dim_dispositivos_huella`
- [ ] Vista analítica: `vista_alertas_monitoreo`
- [ ] Queries avanzadas: Z-score con ventanas móviles (`OVER PARTITION BY`)
- [ ] Validación de ingesta - implementada via SQLAlchemy `to_sql()` como alternativa programática al BULK INSERT nativo, permitiendo control de tipos de datos y transformaciones previas a la carga. Decisión técnica documentada.

### Fase 2 - Generación de Datos y Motor de Riesgo
- [ ] `data_generator.py`: transacciones sintéticas con Faker (tarjetas, DEBIN, billeteras)
- [ ] `etl_pipeline.py`: limpieza y carga a SQL Server vía `sqlalchemy`
- [ ] `risk_engine.py`: implementación de las 3 capas del motor
- [ ] `config/rules.json`: ABM de reglas configurable
- [ ] `01_EDA_fraude.ipynb`: análisis exploratorio completo
- [ ] `02_motor_reglas.ipynb`: prototipado y validación del motor

### Fase 3 - Dashboard Power BI
- [ ] Conexión directa a `vista_alertas_monitoreo` en SQL Server
- [ ] KPIs: Tasa de Falsos Positivos (FPR), Tasa de Falsos Negativos (FNR)
- [ ] Panel de alertas en tiempo real (REVIEW / DECLINE)
- [ ] Análisis de monto financiero salvado por canal

### Fase 4 - Cierre y Presentación
- [ ] README final pulido con capturas del dashboard
- [ ] Sincronización Notion → GitHub
- [ ] Revisión de documentación técnica (`docs/`)

---

## KPIs del Sistema

| KPI | Descripción | Fórmula |
|---|---|---|
| **FPR** | Tasa de Falsos Positivos | FP / (FP + TN) |
| **FNR** | Tasa de Falsos Negativos | FN / (FN + TP) |
| **Precisión** | % alertas que son fraude real | TP / (TP + FP) |
| **Monto salvado** | Valor financiero de DECLINEs correctos | Σ monto transacciones DECLINE verdaderas |
| **Tiempo de respuesta** | Latencia del motor de reglas | ms por transacción evaluada |

---

## Modelo de Datos - Tablas Principales

### `fact_transacciones`
Registro continuo de todas las transacciones evaluadas por el motor.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_transaccion` | VARCHAR(36) | UUID único de la transacción |
| `fecha_hora` | DATETIME2 | Timestamp con precisión de milisegundos |
| `id_usuario` | VARCHAR(20) | Identificador del cliente |
| `canal` | VARCHAR(20) | `TARJETA` / `TRANSFERENCIA` / `BILLETERA` / `DEBIN` |
| `monto` | DECIMAL(18,2) | Importe de la transacción |
| `id_dispositivo` | VARCHAR(50) | Huella del dispositivo |
| `id_comercio` | VARCHAR(20) | Código de comercio destino |
| `pais_origen` | CHAR(2) | Código ISO país |
| `score_riesgo` | INT | Puntaje asignado por el motor |
| `decision` | VARCHAR(10) | `APPROVE` / `REVIEW` / `DECLINE` |
| `reglas_activadas` | VARCHAR(200) | IDs de reglas que sumaron score |
| `es_fraude_confirmado` | BIT | Etiqueta real (para backtesting) |

---

## 👤 Autor

**Alberto Gustavo Estigarribia** - Data Analyst / Data Engineer  
📍 Buenos Aires, Argentina  
🔗 [LinkedIn](#) · [GitHub](#)

> *Proyecto desarrollado como caso de uso profesional para postulación a posición de Analista SR de Prevención de Fraudes.*

---

*Última actualización: Junio 2026*
