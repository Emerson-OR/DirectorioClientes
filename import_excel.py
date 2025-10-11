# importar_clientes_logos.py

import os
import django
import pandas as pd
from io import BytesIO
from PIL import Image
import zipfile
import tempfile
import shutil
import natsort

# -----------------------------
# Configuración Django
# -----------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'directorio_project.settings')
django.setup()

# -----------------------------
# Importar modelos y utilidades de Django
# -----------------------------
from clientes.models import Cliente
from django.core.files.base import ContentFile

# -----------------------------
# Rutas y configuración
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, 'clientes_logos.xlsx')

print("--- Iniciando el script de importación ---")

# -----------------------------
# Parte 1: Leer datos de texto con Pandas
# -----------------------------
try:
    df = pd.read_excel(EXCEL_FILE, sheet_name=0)
    print(f"✅ Excel '{os.path.basename(EXCEL_FILE)}' leído correctamente. {len(df)} filas encontradas.")
except FileNotFoundError:
    print(f"❌ ERROR: No se encontró el archivo Excel en la ruta: {EXCEL_FILE}")
    exit()
except Exception as e:
    print(f"❌ ERROR: Ocurrió un error al leer el archivo Excel: {e}")
    exit()

# Limpiar y validar columnas
df.columns = [col.strip().lower().replace('í', 'i').replace('ñ', 'n') for col in df.columns]
required_columns = ['cliente', 'compania', 'id']
if not all(col in df.columns for col in required_columns):
    print(f"❌ ERROR: El archivo Excel debe contener las columnas: 'Cliente', 'Compañía', 'ID'.")
    exit()

# Filtrar filas donde el ID es nulo o vacío
df.dropna(subset=['id'], inplace=True)
df = df[df['id'].astype(str).str.strip() != '']
print(f"Se procesarán {len(df)} filas con ID válido.")

# -----------------------------
# Parte 2: Procesar clientes
# -----------------------------
print("\n--- Procesando datos de clientes ---")
for index, row in df.iterrows():
    identificacion = str(row['id']).strip()
    try:
        cliente, created = Cliente.objects.update_or_create(
            identificacion=identificacion,
            defaults={
                'nombre': str(row.get('cliente')),
                'compania': str(row.get('compania'))
            }
        )
        if created:
            print(f"✅ Cliente nuevo creado: {cliente.nombre} (ID: {identificacion})")
        else:
            print(f"ℹ️ Cliente existente actualizado: {cliente.nombre} (ID: {identificacion})")
    except Exception as e:
        print(f"❌ ERROR al procesar al cliente con ID {identificacion}: {e}")

# ----------------------------------------------------
# Parte 3: Extraer y asignar imágenes por orden
# ----------------------------------------------------
print("\n--- Extrayendo imágenes de xl/media y asignando por orden ---")

temp_dir = tempfile.mkdtemp()
try:
    with zipfile.ZipFile(EXCEL_FILE, 'r') as zip_ref:
        # Extraer solo las imágenes
        image_files = [f for f in zip_ref.namelist() if f.startswith('xl/media/')]
        if not image_files:
            print("⚠️ No se encontraron imágenes en la carpeta 'xl/media/' del archivo Excel.")
            raise StopIteration

        zip_ref.extractall(temp_dir, members=image_files)

    media_path = os.path.join(temp_dir, 'xl', 'media')
    
    # Ordenar las imágenes de forma natural (image1, image2, ..., image10)
    extracted_images = natsort.natsorted(os.listdir(media_path))
    print(f"✅ Se encontraron {len(extracted_images)} imágenes en 'xl/media'.")

    # Asegurarse de que el número de imágenes no exceda el número de clientes
    if len(extracted_images) > len(df):
        print(f"⚠️ Advertencia: Se encontraron {len(extracted_images)} imágenes pero solo {len(df)} clientes. Se procesarán solo las primeras {len(df)} imágenes.")

    # Iterar sobre los clientes y las imágenes al mismo tiempo
    for (index, row), image_name in zip(df.iterrows(), extracted_images):
        identificacion = str(row['id']).strip()
        
        try:
            cliente = Cliente.objects.get(identificacion=identificacion)
            
            if cliente.logo:
                print(f"ℹ️ Cliente {cliente.nombre} (ID: {identificacion}) ya tiene un logo. Se omite.")
                continue

            image_file_path = os.path.join(media_path, image_name)
            with open(image_file_path, 'rb') as f:
                img_bytes = f.read()

            img = Image.open(BytesIO(img_bytes))
            if img.mode != 'RGB': img = img.convert('RGB')

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_filename = f"{identificacion}.png"
            
            cliente.logo.save(img_filename, ContentFile(buffer.getvalue()), save=True)
            print(f"✅ Logo '{image_name}' asignado a {cliente.nombre} (ID: {identificacion})")

        except Cliente.DoesNotExist:
            print(f"⚠️ Cliente con ID {identificacion} no encontrado en la BD para asignarle el logo '{image_name}'.")
        except Exception as e:
            print(f"❌ ERROR al procesar la imagen '{image_name}' para el cliente con ID {identificacion}: {e}")

except (StopIteration, FileNotFoundError):
    pass # No hacer nada si no hay imágenes
except Exception as e:
    print(f"❌ ERROR general al procesar las imágenes: {e}")
finally:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

print("\n🎉 Importación de clientes y logos completada.")
