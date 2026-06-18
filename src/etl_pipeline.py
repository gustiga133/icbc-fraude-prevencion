# ============================================
# ICBC Prevención de Fraudes
# Script: ETL Pipeline — Carga de CSVs a SQL Server
# Emula el proceso de ingesta desde un core bancario
# ============================================

import pandas as pd
from sqlalchemy import create_engine, text
import urllib
import os

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
# Funciones de carga
# ------------------------------------------------
def cargar_tabla(df, nombre_tabla, engine):
    print(f"Cargando {nombre_tabla}... ", end="")
    df.to_sql(
        name=nombre_tabla,
        con=engine,
        if_exists='append',
        index=False,
        schema='dbo'
    )
    print(f"{len(df):,} registros cargados.")

def verificar_carga(engine):
    print("\nVerificacion de carga en SQL Server:")
    consultas = {
        'dim_perfil_usuarios_historico': 'SELECT COUNT(*) FROM dbo.dim_perfil_usuarios_historico',
        'dim_dispositivos_huella':       'SELECT COUNT(*) FROM dbo.dim_dispositivos_huella',
        'fact_transacciones':            'SELECT COUNT(*) FROM dbo.fact_transacciones',
    }
    with engine.connect() as conn:
        for tabla, query in consultas.items():
            resultado = conn.execute(text(query)).scalar()
            print(f"  {tabla:<40} {resultado:>6,} registros")

# ------------------------------------------------
# Ejecución principal
# ------------------------------------------------
if __name__ == "__main__":

    print("Leyendo CSVs desde data/raw/...\n")

    usuarios_df      = pd.read_csv('data/raw/dim_perfil_usuarios_historico.csv')
    dispositivos_df  = pd.read_csv('data/raw/dim_dispositivos_huella.csv')
    transacciones_df = pd.read_csv('data/raw/fact_transacciones.csv')

    # Conversión de tipos antes de cargar
    usuarios_df['cbu'] = usuarios_df['cbu'].astype(str)    # Cargar tabla de dispositivos
    usuarios_df['fecha_alta_cuenta']       = pd.to_datetime(usuarios_df['fecha_alta_cuenta'])
    dispositivos_df['fecha_primer_uso']    = pd.to_datetime(dispositivos_df['fecha_primer_uso'])
    transacciones_df['fecha_hora']         = pd.to_datetime(transacciones_df['fecha_hora'])

    print("Iniciando carga a SQL Server...\n")

    cargar_tabla(usuarios_df,     'dim_perfil_usuarios_historico', engine)
    cargar_tabla(dispositivos_df, 'dim_dispositivos_huella',       engine)
    cargar_tabla(transacciones_df,'fact_transacciones',            engine)

    verificar_carga(engine)

    print("\nETL completado exitosamente.")