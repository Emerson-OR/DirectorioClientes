# Directorio de Clientes (Django)

Aplicación Django para gestionar clientes (CRUD), con autenticación, roles (usuario, admin, superadmin), historial de cambios y manejo de logos en `media/logos/`. Permite importar datos desde Excel usando `pandas + openpyxl` y mostrar logos desde el campo de imagen o por archivo en `media/logos/{identificacion}.{ext}`.

## Requisitos

- Python 3.13 (probado con 3.13.7)
- Pip (incluido con Python)
- Sistema operativo: Windows (desarrollado/validado en Windows)

## Dependencias principales

- Django 5.2
- pandas 2.3
- openpyxl 3.1
- Pillow 11.x
- django-widget-tweaks (opcional para plantillas)
- Dependencias transitivas relevantes: numpy, python-dateutil, tzdata, et-xmlfile, asgiref, sqlparse, six

Consulta el archivo `requirements.txt` para las versiones exactas usadas.

## Estructura del proyecto (resumen)

- `directorio_project/` – Configuración del proyecto Django (settings, urls, middleware)
- `clientes/` – App principal (modelos, vistas, formularios, comandos management)
  - `management/commands/` – Comandos: `create_groups`, `limpiar_clientes_eliminados`
  - `migrations/` – Migraciones del modelo
- `templates/` – Plantillas base y de autenticación
- `templates/clientes/` – Plantillas de clientes (lista, detalle, agregar)
- `media/logos/` – Almacenamiento de logos
- `db.sqlite3` – Base de datos por defecto

## Instalación y ejecución (Windows, PowerShell)

1) Crear y/o activar entorno virtual (ya existe uno en `Directorio/`):

```powershell
# Activar el venv existente
. .\Directorio\Scripts\Activate.ps1
```

2) Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3) Aplicar migraciones y crear superusuario (si es necesario):

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4) (Opcional) Crear grupos/roles por defecto:

```powershell
python manage.py create_groups
```

5) Ejecutar el servidor de desarrollo:

```powershell
python manage.py runserver
```

Luego accede a http://127.0.0.1:8000/

## Configuración relevante

- Base de datos: SQLite (archivo `db.sqlite3` en el raíz). Puedes cambiar a otro motor en `directorio_project/settings.py`.
- Media: `MEDIA_ROOT = media/`, `MEDIA_URL = /media/`.
- Los logos se guardan en `media/logos/`. Si el campo de imagen no está cargado, el sistema intenta resolver `media/logos/{identificacion}` con extensiones comunes (`png|jpg|jpeg|webp`).

## Importar clientes desde Excel

- El proyecto usa `pandas` y `openpyxl` para leer datos tabulares y extraer imágenes embebidas si aplica.
- Asegúrate de tener los archivos de Excel y/o logos en `media/logos/` si vas a usar el fallback basado en `identificacion`.
- Si existe un comando o script de importación en tu copia (por ejemplo, un management command), ejecútalo desde PowerShell con `python manage.py nombre_del_comando`. Si estás usando un script independiente, actívalo con el venv y ejecútalo con `python ruta\al\script.py`.

Nota: En esta base se han reemplazado flujos con `xlwings` por `pandas + openpyxl` para mayor compatibilidad y reproducibilidad.

## Roles y permisos (UI)

- Usuarios con rol `admin`/`superadmin` pueden editar y ver el historial de cambios; las cards de Detalles e Historial se muestran a la misma altura.
- Usuarios estándar ven una versión de solo lectura compacta.

## Comandos útiles

- Crear grupos por defecto (roles):
  ```powershell
  python manage.py create_groups
  ```
- Limpiar clientes marcados como eliminados (si aplica):
  ```powershell
  python manage.py limpiar_clientes_eliminados
  ```

## Variables de entorno

Para despliegue, configura al menos:
- `SECRET_KEY` (no uses la de desarrollo)
- `DEBUG=False`
- `ALLOWED_HOSTS` con tus dominios

En desarrollo puedes dejar `DEBUG=True`.

## Solución de problemas

- Si los logos no se muestran: verifica que existan en `media/logos/` y que el nombre coincida con `identificacion` o que el `ImageField` tenga un archivo.
- Si `pandas` o `openpyxl` fallan al abrir el Excel: confirma que el archivo no esté corrupto y que tenga permisos de lectura.
- En Windows, si hay advertencias de ejecución de scripts, abre PowerShell como administrador y establece la política de ejecución según tu política de seguridad.

## Licencia

Este proyecto es de uso interno/educativo. Ajusta la licencia según tus necesidades.
