# Decisiones Técnicas - ICBC Prevención de Fraudes

## ADR-001: SQLAlchemy vs BULK INSERT para ingesta de datos

**Fecha:** Junio 2026  
**Estado:** Aceptada

### Contexto
Durante la Fase 1 se evaluaron dos métodos para cargar los CSVs sintéticos a SQL Server:
- `BULK INSERT` nativo de SQL Server
- `to_sql()` de SQLAlchemy vía Python

### Decisión
Se optó por SQLAlchemy `to_sql()`.

### Justificación
- Permite transformaciones de tipos de datos previas a la carga (conversión de fechas, strings)
- Integración natural con el pipeline Python existente
- Mayor control sobre errores fila por fila
- En entornos bancarios reales ambos métodos coexisten: BULK INSERT para cargas batch nocturnas de alto volumen, SQLAlchemy para pipelines programáticos con lógica de negocio

### Consecuencias
La carga es levemente más lenta que BULK INSERT nativo, pero suficiente para el volumen del proyecto (5000 registros). Para volúmenes de millones de registros se recomendaría BULK INSERT o COPY en PostgreSQL.

## ADR-002: Power BI conectado a vista SQL vs importación de CSV

**Fecha:** Junio 2026  
**Estado:** Aceptada

### Decisión
Power BI se conecta directamente a `dbo.vista_alertas_monitoreo` en SQL Server 
mediante conexión en vivo (DirectQuery o Import), no mediante archivos CSV exportados.

### Justificación
- La vista ya filtra y calcula el Z-score - Power BI consume datos listos
- En producción el dashboard refleja el estado actual de la base operativa
- Es la práctica estándar en entornos bancarios reales