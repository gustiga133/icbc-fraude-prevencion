# ============================================
# ICBC Prevención de Fraudes
# Script: Motor de Riesgo
# Evalúa cada transacción contra 5 capas de reglas
# ============================================

import pandas as pd
import json
from sqlalchemy import create_engine, text
import urllib
from datetime import datetime, timedelta
import numpy as np

# ------------------------------------------------
# Conexión a SQL Server
# ------------------------------------------------
SERVER   = r'gustiga123\SQLEXPRESS'
DATABASE = 'ICBC_Fraude'

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# ------------------------------------------------
# Cargar reglas desde JSON
# ------------------------------------------------
def cargar_reglas():
    with open('config/rules.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# ------------------------------------------------
# Capa 1: Data Enrichment
# Calcula atributos dinámicos para cada transacción
# ------------------------------------------------
def enrichment(transaccion, perfil_usuario, todas_transacciones):
    
    id_usuario = transaccion['id_usuario']
    monto = transaccion['monto']
    fecha_hora = transaccion['fecha_hora']
    canal = transaccion['canal']
    dispositivo = transaccion['id_dispositivo']
    pais = transaccion['pais_origen']
    
    # Calculo de Z-score
    monto_promedio = perfil_usuario['monto_promedio']
    monto_desvio = perfil_usuario['monto_desvio_std']
    
    if monto_desvio == 0:
        zscore = 0
    else:
        zscore = (monto - monto_promedio) / monto_desvio
    
    # Conteo de transacciones en ventana de 10 minutos
    fecha_inicio_ventana = fecha_hora - timedelta(minutes=10)
    tx_ventana_10min = len([
        tx for tx in todas_transacciones
        if tx['id_usuario'] == id_usuario 
        and fecha_inicio_ventana <= tx['fecha_hora'] <= fecha_hora
    ])
    
    # Detección de dispositivo nuevo (no está en el histórico)
    dispositivo_nuevo = dispositivo not in [d['id_huella'] for d in []]  # Simplificado
    
    # Detección de país anómalo
    pais_anomalo = pais != 'AR' if perfil_usuario['monto_promedio'] > 10000 else False
    
    return {
        'zscore_monto': zscore,
        'tx_ultimos_10min': tx_ventana_10min,
        'dispositivo_nuevo': dispositivo_nuevo,
        'pais_anomalo': pais_anomalo,
        'percentil_95': perfil_usuario['monto_percentil_95'],
        'monto_promedio': monto_promedio
    }

# ------------------------------------------------
# Capa 2: Decision Engine
# Aplica las reglas y acumula score
# ------------------------------------------------
def evaluar_reglas(transaccion, enriched_data, reglas_config, perfil_usuario):
    
    reglas = reglas_config['reglas']
    score = 0
    reglas_activadas = []
    
    for regla in reglas:
        if not regla['activa']:
            continue
        
        activada = False
        
        if regla['id'] == 'R001':
            # Monto > percentil 95 AND dispositivo nuevo
            if transaccion['monto'] > enriched_data['percentil_95'] and enriched_data['dispositivo_nuevo']:
                activada = True
        
        elif regla['id'] == 'R002':
            # Z-score > 3 en DEBIN o TRANSFERENCIA
            if abs(enriched_data['zscore_monto']) > 3 and transaccion['canal'] in ['DEBIN', 'TRANSFERENCIA']:
                activada = True
        
        elif regla['id'] == 'R003':
            # Más de 5 transacciones en 10 minutos
            if enriched_data['tx_ultimos_10min'] > 5:
                activada = True
        
        elif regla['id'] == 'R004':
            # País anómalo
            if enriched_data['pais_anomalo']:
                activada = True
        
        elif regla['id'] == 'R005':
            # Monto supera 4 veces el promedio
            if transaccion['monto'] > enriched_data['monto_promedio'] * 4:
                activada = True
        
        if activada:
            score += regla['score']
            reglas_activadas.append(regla['id'])
    
    return score, reglas_activadas

# ------------------------------------------------
# Capa 3: Orquestación
# Toma la decisión final basada en score
# ------------------------------------------------
def tomar_decision(score, umbrales):
    
    if score <= umbrales['APPROVE']['max_score']:
        return 'APPROVE'
    elif umbrales['REVIEW']['min_score'] <= score <= umbrales['REVIEW']['max_score']:
        return 'REVIEW'
    else:
        return 'DECLINE'

# ------------------------------------------------
# Ejecución principal
# ------------------------------------------------
if __name__ == "__main__":
    
    print("Cargando configuración del motor...")
    reglas_config = cargar_reglas()
    
    print("Extrayendo datos de SQL Server...")
    with engine.connect() as conn:
        usuarios_df = pd.read_sql(
            "SELECT * FROM dbo.dim_perfil_usuarios_historico",
            conn
        )
        transacciones_df = pd.read_sql(
            "SELECT * FROM dbo.fact_transacciones ORDER BY fecha_hora",
            conn
        )
    
    usuarios_dict = {row['id_usuario']: row for _, row in usuarios_df.iterrows()}
    transacciones_list = transacciones_df.to_dict('records')
    
    print(f"Evaluando {len(transacciones_df)} transacciones...\n")
    
    resultados = []
    
    for idx, transaccion in enumerate(transacciones_list):
        
        id_usuario = transaccion['id_usuario']
        
        if id_usuario not in usuarios_dict:
            continue
        
        perfil = usuarios_dict[id_usuario]
        
        # Capa 1: Enrichment
        enriched_data = enrichment(transaccion, perfil, transacciones_list)
        
        # Capa 2: Decision Engine
        score, reglas_activadas = evaluar_reglas(
            transaccion,
            enriched_data,
            reglas_config,
            perfil
        )
        
        # Capa 3: Orquestación
        decision = tomar_decision(score, reglas_config['umbrales_decision'])
        
        resultados.append({
            'id_transaccion': transaccion['id_transaccion'],
            'score_riesgo': score,
            'decision': decision,
            'reglas_activadas': ','.join(reglas_activadas) if reglas_activadas else None
        })
        
        if (idx + 1) % 500 == 0:
            print(f"Procesadas {idx + 1:,} transacciones...")
    
    # Actualizar SQL Server con resultados
    print("\nActualizando transacciones en SQL Server...")
    
    for resultado in resultados:
        with engine.connect() as conn:
            conn.execute(text(
                f"""
                UPDATE dbo.fact_transacciones
                SET score_riesgo = {resultado['score_riesgo']},
                    decision = '{resultado['decision']}',
                    reglas_activadas = {f"'{resultado['reglas_activadas']}'" if resultado['reglas_activadas'] else 'NULL'}
                WHERE id_transaccion = '{resultado['id_transaccion']}'
                """
            ))
            conn.commit()
    
    # Estadísticas finales
    print("\nEstadísticas del motor:")
    
    with engine.connect() as conn:
        stats = conn.execute(text(
            """
            SELECT
                decision,
                COUNT(*) as cantidad,
                ROUND(AVG(CAST(score_riesgo AS FLOAT)), 2) as score_promedio,
                MAX(score_riesgo) as score_maximo
            FROM dbo.fact_transacciones
            GROUP BY decision
            ORDER BY decision
            """
        ))
        for row in stats:
            print(f"  {row[0]:<12} {row[1]:>6,} transacciones | Score promedio: {row[2]:>6} | Score máximo: {row[3]:>6}")
    
    print("\nMotor de riesgo ejecutado exitosamente.")