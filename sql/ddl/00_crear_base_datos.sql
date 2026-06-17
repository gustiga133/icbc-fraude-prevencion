-- ============================================
-- ICBC Prevención de Fraudes
-- Script: Creación de base de datos
-- ============================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ICBC_Fraude')
BEGIN
    CREATE DATABASE ICBC_Fraude;
    PRINT 'Base de datos ICBC_Fraude creada correctamente.';
END
ELSE
    PRINT 'La base de datos ICBC_Fraude ya existe.';
GO