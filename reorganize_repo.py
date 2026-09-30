import os
import shutil

base_dir = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling'

# 1. Definir nueva estructura de directorios
dirs_to_create = [
    'docs',
    'src/mql5/Experts',
    'src/mql5/Include',
    'src/python/meta_labeling',
    'src/python/utils',
    'research_archive',
    'data'
]

print("Creando estructura de directorios...")
for d in dirs_to_create:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

# 2. Mover archivos existentes a research_archive
folders_to_archive = ['python', 'scripts', 'training', 'pipelines', 'reports']
for folder in folders_to_archive:
    src_folder = os.path.join(base_dir, folder)
    dst_folder = os.path.join(base_dir, 'research_archive', folder)
    if os.path.exists(src_folder) and not os.path.exists(dst_folder):
        print(f"Moviendo {folder} a research_archive...")
        shutil.move(src_folder, dst_folder)

# 3. Mover MQL5 a src/mql5
mql5_src = os.path.join(base_dir, 'mql5')
mql5_dst = os.path.join(base_dir, 'src', 'mql5')
if os.path.exists(mql5_src):
    print("Moviendo MQL5 a src/mql5...")
    # Para evitar errores de movimiento si el destino existe, iteramos sobre los contenidos
    for item in os.listdir(mql5_src):
        s = os.path.join(mql5_src, item)
        d = os.path.join(mql5_dst, item)
        if not os.path.exists(d):
            shutil.move(s, d)
    # Una vez vacío (o casi), eliminamos o ignoramos la carpeta original
    try: os.rmdir(mql5_src)
    except: pass

print("Reestructuracion fisica completada con exito.")
