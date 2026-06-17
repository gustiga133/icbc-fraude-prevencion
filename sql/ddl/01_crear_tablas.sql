-- ============================================
-- ICBC Prevención de Fraudes
-- Script: Creación de tablas principales
-- ============================================

USE ICBC_Fraude;
GO

-- Tabla de dimensión: perfil histórico del usuario
CREATE TABLE dim_perfil_usuarios_historico (
    id_usuario          VARCHAR(20)     NOT NULL PRIMARY KEY,
    nombre              VARCHAR(100)    NOT NULL,
    cuit                VARCHAR(13)     NOT NULL,
    cbu                 VARCHAR(22)     NOT NULL,
    monto_promedio      DECIMAL(18,2)   NOT NULL,
    monto_desvio_std    DECIMAL(18,2)   NOT NULL,
    monto_percentil_95  DECIMAL(18,2)   NOT NULL,
    cant_cuentas_destino_usuales INT    NOT NULL DEFAULT 0,
    fecha_alta_cuenta   DATE            NOT NULL,
    activo              BIT             NOT NULL DEFAULT 1
);
GO

-- Tabla de dimensión: huella de dispositivos
CREATE TABLE dim_dispositivos_huella (
    id_huella           VARCHAR(50)     NOT NULL PRIMARY KEY,
    id_usuario          VARCHAR(20)     NOT NULL,
    tipo_dispositivo    VARCHAR(30)     NOT NULL,  -- MOBILE / DESKTOP / POS
    sistema_operativo   VARCHAR(30)     NULL,
    navegador           VARCHAR(30)     NULL,
    es_confiable        BIT             NOT NULL DEFAULT 1,
    fecha_primer_uso    DATETIME2       NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES dim_perfil_usuarios_historico(id_usuario)
);
GO

-- Tabla de hechos: transacciones
CREATE TABLE fact_transacciones (
    id_transaccion          VARCHAR(36)     NOT NULL PRIMARY KEY,
    fecha_hora              DATETIME2       NOT NULL,
    id_usuario              VARCHAR(20)     NOT NULL,
    canal                   VARCHAR(20)     NOT NULL,  -- TARJETA / TRANSFERENCIA / BILLETERA / DEBIN
    monto                   DECIMAL(18,2)   NOT NULL,
    id_dispositivo          VARCHAR(50)     NULL,
    id_comercio             VARCHAR(20)     NULL,
    pais_origen             CHAR(2)         NOT NULL DEFAULT 'AR',
    score_riesgo            INT             NULL,
    decision                VARCHAR(10)     NULL,      -- APPROVE / REVIEW / DECLINE
    reglas_activadas        VARCHAR(200)    NULL,
    es_fraude_confirmado    BIT             NOT NULL DEFAULT 0,
    fecha_carga             DATETIME2       NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (id_usuario) REFERENCES dim_perfil_usuarios_historico(id_usuario)
);
GO

PRINT 'Tablas creadas correctamente en ICBC_Fraude.';
GO