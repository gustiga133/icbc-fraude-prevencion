-- ============================================
-- ICBC Prevención de Fraudes
-- Script: Vista analítica de alertas
-- ============================================

USE ICBC_Fraude;
GO

CREATE OR ALTER VIEW vista_alertas_monitoreo AS
SELECT
    t.id_transaccion,
    t.fecha_hora,
    t.id_usuario,
    p.nombre,
    t.canal,
    t.monto,
    p.monto_promedio,
    p.monto_desvio_std,
    -- Z-score del monto respecto al perfil histórico del usuario
    CASE 
        WHEN p.monto_desvio_std = 0 THEN 0
        ELSE ROUND((t.monto - p.monto_promedio) / p.monto_desvio_std, 2)
    END AS zscore_monto,
    t.score_riesgo,
    t.decision,
    t.reglas_activadas,
    t.es_fraude_confirmado,
    d.tipo_dispositivo,
    d.es_confiable AS dispositivo_confiable,
    t.pais_origen
FROM
    fact_transacciones t
    INNER JOIN dim_perfil_usuarios_historico p ON t.id_usuario = p.id_usuario
    LEFT JOIN dim_dispositivos_huella d ON t.id_dispositivo = d.id_huella
WHERE
    t.decision IN ('REVIEW', 'DECLINE');
GO

PRINT 'Vista vista_alertas_monitoreo creada correctamente.';
GO