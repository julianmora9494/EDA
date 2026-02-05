import pandas as pd
import numpy as np

print("Leyendo base_panama.xlsx...")
df = pd.read_excel('base_panama.xlsx')

print(f"Shape original: {df.shape}")
print("\nAjustando tipos de datos...")

# 1. Código Cliente: es ID, convertir a string
df['Código Cliente'] = df['Código Cliente'].astype(str)
print("  - Código Cliente: int64 -> string")

# 2. Celular: es teléfono, convertir a string (sin decimales) y agregar prefijo para forzar string
df['Celular'] = df['Celular'].apply(lambda x: str(int(x)) if pd.notna(x) and x != 0 else '')
# Forzar tipo string explícitamente
df['Celular'] = df['Celular'].astype(str).replace('0', '').replace('nan', '')
print("  - Celular: float64 -> string (forzado)")

# 3. TIN: ya es string, pero limpiar
df['TIN'] = df['TIN'].fillna('').astype(str)
print("  - TIN: limpiado")

# 4. Identificación: ya es string
df['Identificación'] = df['Identificación'].astype(str)
print("  - Identificación: confirmado como string")

# 5. Año Creación: convertir a int (si existe)
if 'Año Creación' in df.columns:
    df['Año Creación'] = df['Año Creación'].astype(int)
    print("  - Año Creación: confirmado como int")

# 6. Todas las columnas de saldo/cuentas: asegurar que sean numéricas
numeric_cols = [col for col in df.columns if any(kw in col for kw in ['Saldo', 'Cuentas', 'Total'])]
for col in numeric_cols:
    if df[col].dtype == 'object':
        df[col] = pd.to_numeric(df[col], errors='coerce')
        print(f"  - {col}: convertido a numérico")

print("\nGuardando base_panama_mejorada.csv...")
df.to_csv('base_panama_mejorada.csv', index=False, encoding='utf-8-sig')

print("\nResumen final:")
print(f"  Filas: {len(df):,}")
print(f"  Columnas: {len(df.columns)}")
print("\nTipos de datos corregidos:")
print(f"  - Código Cliente: {df['Código Cliente'].dtype}")
print(f"  - Celular: {df['Celular'].dtype}")
print(f"  - Identificación: {df['Identificación'].dtype}")
print(f"  - TIN: {df['TIN'].dtype}")

print("\n✓ Archivo guardado: base_panama_mejorada.csv")
print("  Este archivo tiene los tipos correctos para el análisis EDA")
