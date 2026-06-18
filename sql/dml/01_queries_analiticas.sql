-- ============================================
-- ICBC Prevención de Fraudes
-- Script: Queries analíticas con ventanas móviles
-- ============================================

USE ICBC_Fraude;
GO

-- ------------------------------------------------
-- Query 1: Conteo de transacciones por usuario
-- en ventana móvil de 10 minutos
-- Detecta ráfagas de actividad sospechosa
-- ------------------------------------------------
SELECT
    t1.id_usuario,
    t1.id_transaccion,
    t1.fecha_hora,
    t1.monto,
    t1.canal,
    COUNT(t2.id_transaccion) AS cant_tx_ultimos_10min
FROM
    fact_transacciones t1
    INNER JOIN fact_transacciones t2
        ON  t1.id_usuario = t2.id_usuario
        AND t2.fecha_hora BETWEEN DATEADD(MINUTE, -10, t1.fecha_hora) AND t1.fecha_hora
        AND t2.id_transaccion != t1.id_transaccion
GROUP BY
    t1.id_usuario,
    t1.id_transaccion,
    t1.fecha_hora,
    t1.monto,
    t1.canal
ORDER BY
    cant_tx_ultimos_10min DESC;
GO

-- ------------------------------------------------
-- Query 2: Z-score por usuario con ventana histórica
-- Detecta montos anómalos respecto al perfil
-- ------------------------------------------------
SELECT
    t.id_transaccion,
    t.id_usuario,
    t.monto,
    p.monto_promedio,
    p.monto_desvio_std,
    ROUND(
        (t.monto - p.monto_promedio) / NULLIF(p.monto_desvio_std, 0),
    2) AS zscore_monto,
    CASE
        WHEN ABS((t.monto - p.monto_promedio) / NULLIF(p.monto_desvio_std, 0)) > 3
        THEN 'ANOMALIA CRITICA'
        WHEN ABS((t.monto - p.monto_promedio) / NULLIF(p.monto_desvio_std, 0)) > 2
        THEN 'DESVIO MODERADO'
        ELSE 'NORMAL'
    END AS clasificacion_zscore
FROM
    fact_transacciones t
    INNER JOIN dim_perfil_usuarios_historico p ON t.id_usuario = p.id_usuario
ORDER BY
    ABS((t.monto - p.monto_promedio) / NULLIF(p.monto_desvio_std, 0)) DESC;
GO

-- ------------------------------------------------
-- Query 3: Ranking de usuarios por score de riesgo
-- acumulado en las últimas 24 horas
-- KPI clave para el dashboard de Power BI
-- ------------------------------------------------
SELECT
    t.id_usuario,
    p.nombre,
    COUNT(t.id_transaccion)         AS cant_transacciones,
    SUM(t.monto)                    AS volumen_total,
    AVG(CAST(t.score_riesgo AS FLOAT)) AS score_promedio,
    MAX(t.score_riesgo)             AS score_maximo,
    SUM(CASE WHEN t.decision = 'DECLINE' THEN 1 ELSE 0 END) AS cant_declines,
    SUM(CASE WHEN t.decision = 'REVIEW'  THEN 1 ELSE 0 END) AS cant_reviews
FROM
    fact_transacciones t
    INNER JOIN dim_perfil_usuarios_historico p ON t.id_usuario = p.id_usuario
WHERE
    t.fecha_hora >= DATEADD(HOUR, -24, GETDATE())
GROUP BY
    t.id_usuario, p.nombre
ORDER BY
    score_maximo DESC;
GO

-- ------------------------------------------------
-- Query 4: Estadísticas generales del motor de riesgo
-- Resumen ejecutivo para Gerencia de Riesgos
-- ------------------------------------------------
USE ICBC_Fraude;
GO

SELECT
    decision,
    COUNT(*)                                    AS cantidad,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS porcentaje,
    ROUND(AVG(CAST(score_riesgo AS FLOAT)), 2)  AS score_promedio,
    MAX(score_riesgo)                           AS score_maximo,
    SUM(monto)                                  AS volumen_total,
    SUM(CASE WHEN es_fraude_confirmado = 1 THEN 1 ELSE 0 END) AS fraudes_reales
FROM
    dbo.fact_transacciones
GROUP BY
    decision
ORDER BY
    decision;
GO