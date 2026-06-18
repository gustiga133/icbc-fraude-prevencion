# ============================================
# ICBC Prevención de Fraudes
# Script: Generador de datos sintéticos
# Simula transacciones de un core bancario
# ============================================

import pandas as pd
import numpy as np
from faker import Faker
from faker.providers import bank, person, address
import random
import uuid
from datetime import datetime, timedelta
import os

fake = Faker('es_AR')
fake.add_provider(bank)
fake.add_provider(person)
random.seed(42)
np.random.seed(42)

# ------------------------------------------------
# Parámetros de simulación
# ------------------------------------------------
N_USUARIOS     = 200
N_TRANSACCIONES = 5000
DIAS_HISTORICO  = 90
TASA_FRAUDE     = 0.05  # 5% de transacciones son fraude real

CANALES = ['TARJETA', 'TRANSFERENCIA', 'BILLETERA', 'DEBIN']
PAISES  = ['AR'] * 92 + ['BR', 'US', 'CL', 'UY', 'CN', 'NG', 'RO', 'PY', 'VE']
TIPOS_DISPOSITIVO = ['MOBILE', 'DESKTOP', 'POS']
SISTEMAS_OPERATIVOS = ['Android', 'iOS', 'Windows', 'macOS', 'Linux']
NAVEGADORES = ['Chrome', 'Safari', 'Firefox', 'Edge', 'Desconocido']

# ------------------------------------------------
# Generación de perfiles de usuarios
# ------------------------------------------------
def generar_cuit(es_persona=True):
    prefijo = random.choice([20, 23, 24, 27]) if es_persona else random.choice([30, 33])
    numero = random.randint(10000000, 99999999)
    return f"{prefijo}-{numero}-{random.randint(0,9)}"

def generar_cbu():
    return ''.join([str(random.randint(0, 9)) for _ in range(22)])

def generar_usuarios(n):
    usuarios = []
    for _ in range(n):
        monto_promedio = round(random.uniform(1000, 80000), 2)
        monto_desvio   = round(monto_promedio * random.uniform(0.1, 0.4), 2)
        usuarios.append({
            'id_usuario':                   f"USR{str(random.randint(10000,99999))}",
            'nombre':                        fake.name(),
            'cuit':                          generar_cuit(),
            'cbu':                           generar_cbu(),
            'monto_promedio':                monto_promedio,
            'monto_desvio_std':              monto_desvio,
            'monto_percentil_95':            round(monto_promedio + 1.645 * monto_desvio, 2),
            'cant_cuentas_destino_usuales':  random.randint(1, 10),
            'fecha_alta_cuenta':             fake.date_between(start_date='-5y', end_date='-6m'),
            'activo':                        1
        })
    return pd.DataFrame(usuarios).drop_duplicates(subset='id_usuario')

# ------------------------------------------------
# Generación de huellas de dispositivos
# ------------------------------------------------
def generar_dispositivos(usuarios_df):
    dispositivos = []
    for _, usuario in usuarios_df.iterrows():
        n_dispositivos = random.randint(1, 3)
        for _ in range(n_dispositivos):
            dispositivos.append({
                'id_huella':        str(uuid.uuid4())[:20],
                'id_usuario':       usuario['id_usuario'],
                'tipo_dispositivo': random.choice(TIPOS_DISPOSITIVO),
                'sistema_operativo':random.choice(SISTEMAS_OPERATIVOS),
                'navegador':        random.choice(NAVEGADORES),
                'es_confiable':     1,
                'fecha_primer_uso': fake.date_time_between(start_date='-2y', end_date='-1m')
            })
    return pd.DataFrame(dispositivos)

# ------------------------------------------------
# Generación de transacciones
# ------------------------------------------------
def generar_transacciones(usuarios_df, dispositivos_df, n):
    transacciones = []
    fecha_inicio = datetime.now() - timedelta(days=DIAS_HISTORICO)

    for _ in range(n):
        usuario = usuarios_df.sample(1).iloc[0]
        es_fraude = random.random() < TASA_FRAUDE

        # Dispositivo: fraude usa dispositivo desconocido más seguido
        dispositivos_usuario = dispositivos_df[
            dispositivos_df['id_usuario'] == usuario['id_usuario']
        ]

        if es_fraude and random.random() < 0.6:
            id_dispositivo = str(uuid.uuid4())[:20]  # dispositivo nuevo/desconocido
        elif len(dispositivos_usuario) > 0:
            id_dispositivo = dispositivos_usuario.sample(1).iloc[0]['id_huella']
        else:
            id_dispositivo = str(uuid.uuid4())[:20]

        # Monto: fraude tiende a montos extremos
        if es_fraude:
            monto = round(random.uniform(
                usuario['monto_promedio'] * 2,
                usuario['monto_promedio'] * 6
            ), 2)
        else:
            monto = round(max(10, np.random.normal(
                usuario['monto_promedio'],
                usuario['monto_desvio_std']
            )), 2)

        # País: fraude tiene más probabilidad de país extranjero
        if es_fraude:
            pais = random.choice(['BR', 'US', 'CL', 'CN', 'NG', 'RO', 'PY', 'VE', 'AR'])
        else:
            pais = random.choice(PAISES)

        transacciones.append({
            'id_transaccion':       str(uuid.uuid4()),
            'fecha_hora':           fake.date_time_between(
                                        start_date=fecha_inicio,
                                        end_date='now'
                                    ),
            'id_usuario':           usuario['id_usuario'],
            'canal':                random.choice(CANALES),
            'monto':                monto,
            'id_dispositivo':       id_dispositivo,
            'id_comercio':          f"COM{random.randint(1000,9999)}",
            'pais_origen':          pais,
            'score_riesgo':         None,
            'decision':             None,
            'reglas_activadas':     None,
            'es_fraude_confirmado': int(es_fraude)
        })

    return pd.DataFrame(transacciones)

# ------------------------------------------------
# Ejecución principal
# ------------------------------------------------
if __name__ == "__main__":
    print("Generando perfiles de usuarios...")
    usuarios_df     = generar_usuarios(N_USUARIOS)

    print("Generando huellas de dispositivos...")
    dispositivos_df = generar_dispositivos(usuarios_df)

    print("Generando transacciones...")
    transacciones_df = generar_transacciones(usuarios_df, dispositivos_df, N_TRANSACCIONES)

    # Guardar CSVs en data/raw/
    os.makedirs("data/raw", exist_ok=True)
    usuarios_df.to_csv("data/raw/dim_perfil_usuarios_historico.csv",     index=False, encoding='utf-8-sig')
    dispositivos_df.to_csv("data/raw/dim_dispositivos_huella.csv",        index=False, encoding='utf-8-sig')
    transacciones_df.to_csv("data/raw/fact_transacciones.csv",            index=False, encoding='utf-8-sig')

    print(f"\nResumen de datos generados:")
    print(f"  Usuarios:       {len(usuarios_df):>6,}")
    print(f"  Dispositivos:   {len(dispositivos_df):>6,}")
    print(f"  Transacciones:  {len(transacciones_df):>6,}")
    print(f"  Fraudes reales: {transacciones_df['es_fraude_confirmado'].sum():>6,} ({TASA_FRAUDE*100:.0f}%)")
    print(f"\nCSVs guardados en data/raw/")