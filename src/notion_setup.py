import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

import httpx
notion = Client(auth=os.environ["NOTION_TOKEN"], client=httpx.Client(verify=False))
PAGE_ID = os.environ["NOTION_PAGE_ID"]


def crear_encabezado(texto, nivel=1):
    tipos = {1: "heading_1", 2: "heading_2", 3: "heading_3"}
    return {
        "object": "block",
        "type": tipos[nivel],
        tipos[nivel]: {
            "rich_text": [{"type": "text", "text": {"content": texto}}]
        }
    }


def crear_parrafo(texto):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": texto}}]
        }
    }


def crear_todo(texto, checked=False):
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {
            "rich_text": [{"type": "text", "text": {"content": texto}}],
            "checked": checked
        }
    }


def crear_divisor():
    return {"object": "block", "type": "divider", "divider": {}}


bloques = [
    crear_encabezado("ICBC — Sistema de Prevención de Fraudes End-to-End"),
    crear_parrafo("Proyecto de portfolio profesional que simula un entorno bancario real de prevención de fraudes transaccionales."),
    crear_divisor(),

    # Stack tecnológico
    crear_encabezado("Stack Tecnológico", 2),
    crear_parrafo("Python · SQL Server · Power BI · Git · GitHub · Notion API · Faker · SQLAlchemy"),
    crear_divisor(),

    # Arquitectura
    crear_encabezado("Arquitectura del Sistema", 2),
    crear_parrafo("Python genera CSV (datos sintéticos) → SQL Server ingesta y modela → Motor de Riesgo evalúa → Power BI visualiza alertas y KPIs."),
    crear_divisor(),

    # Fase 0
    crear_encabezado("Fase 0 — Arquitectura y Planificación", 2),
    crear_todo("Definición de stack tecnológico", checked=True),
    crear_todo("Diseño de arquitectura del sistema", checked=True),
    crear_todo("Estructura del repositorio en GitHub", checked=True),
    crear_todo("README.md profesional publicado", checked=True),
    crear_todo("Documento de planificación en Notion (este documento)", checked=False),
    crear_divisor(),

    # Fase 1
    crear_encabezado("Fase 1 — SQL Server y Modelo de Datos", 2),
    crear_todo("Script DDL: fact_transacciones"),
    crear_todo("Script DDL: dim_perfil_usuarios_historico"),
    crear_todo("Script DDL: dim_dispositivos_huella"),
    crear_todo("Vista analítica: vista_alertas_monitoreo"),
    crear_todo("Queries avanzadas: Z-score con ventanas móviles"),
    crear_todo("Validación de ingesta con BULK INSERT"),
    crear_divisor(),

    # Fase 2
    crear_encabezado("Fase 2 — Generación de Datos y Motor de Riesgo", 2),
    crear_todo("data_generator.py: transacciones sintéticas con Faker"),
    crear_todo("etl_pipeline.py: limpieza y carga a SQL Server"),
    crear_todo("risk_engine.py: las 3 capas del motor de riesgo"),
    crear_todo("config/rules.json: ABM de reglas configurable"),
    crear_todo("01_EDA_fraude.ipynb: análisis exploratorio"),
    crear_todo("02_motor_reglas.ipynb: prototipado del motor"),
    crear_divisor(),

    # Fase 3
    crear_encabezado("Fase 3 — Dashboard Power BI", 2),
    crear_todo("Conexión a vista_alertas_monitoreo en SQL Server"),
    crear_todo("KPIs: FPR, FNR, monto financiero salvado"),
    crear_todo("Panel de alertas en tiempo real (REVIEW / DECLINE)"),
    crear_todo("Análisis por canal de pago"),
    crear_divisor(),

    # Fase 4
    crear_encabezado("Fase 4 — Cierre y Presentación", 2),
    crear_todo("README final con capturas del dashboard"),
    crear_todo("Sincronización Notion → GitHub"),
    crear_todo("Revisión de documentación técnica en docs/"),
    crear_divisor(),

    # Motor de riesgo
    crear_encabezado("Motor de Riesgo — Lógica de Decisión", 2),
    crear_encabezado("Umbrales de decisión", 3),
    crear_parrafo("APPROVE: Score < 30 — Transacción liberada"),
    crear_parrafo("REVIEW: Score 31-75 — Alerta generada, pasa a Power BI"),
    crear_parrafo("DECLINE: Score > 75 — Bloqueo automático preventivo"),
    crear_encabezado("Reglas configuradas en rules.json", 3),
    crear_parrafo("R001: Monto > percentil 95 del usuario AND dispositivo nuevo → +40 pts"),
    crear_parrafo("R002: Z-score del monto > 3 en DEBIN o transferencia → +50 pts"),
    crear_parrafo("R003: Más de 5 transacciones en 10 minutos → +35 pts"),
    crear_parrafo("R004: IP inconsistente con perfil histórico → +45 pts"),
    crear_parrafo("R005: Primer uso de tarjeta en comercio de alto riesgo → +30 pts"),
]

notion.blocks.children.append(block_id=PAGE_ID, children=bloques)
print("Estructura de planificacion creada en Notion correctamente.")