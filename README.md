# Audio Transformer Pro

Aplicacion de escritorio desarrollada en Python para la conversion por lotes de archivos de audio, deteccion automatica de tonalidad musical y normalizacion de sonoridad bajo el estandar EBU R128.

## Caracteristicas Principales

- **Conversion multiformato por lotes**: Soporte de exportacion a MP3 (320 kbps), AAC (256 kbps), OGG Vorbis (Q8), FLAC (Lossless) y WAV (PCM 16-bit).
- **Deteccion de tonalidad musical**: Analisis espectral mediante cromagramas (`librosa`) y perfiles tonales de Krumhansl-Schmuckler para identificar automaticamente la escala mayor o menor de cada pista.
- **Normalizacion de sonoridad (EBU R128)**: Integracion del filtro `loudnorm` de FFmpeg (`I=-14 LUFS`, `LRA=11`, `TP=-1.5 dBTP`) para estandarizar el rango dinamico y el nivel de volumen.
- **Nomenclatura estructurada**: Los archivos procesados se almacenan en el subdirectorio `Audios_Transformados` incluyendo en su nombre la tonalidad detectada y el perfil de calidad aplicado.
- **Procesamiento asincrono**: Ejecucion en segundo plano mediante hilos (`threading`) para mantener la interfaz grafica receptiva durante el procesamiento de multiples pistas.

## Requisitos del Sistema

- Python 3.10 o superior
- Dependencias listadas en `requirements.txt` (incluye `imageio-ffmpeg` para proveer el binario de FFmpeg automaticamente)

## Instalacion

1. Clonar el repositorio:

```bash
git clone https://github.com/TU_USUARIO/audio_transformer.git
cd audio_transformer
```

2. Crear y activar un entorno virtual:

```bash
python -m venv .venv
# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# En Linux / macOS:
source .venv/bin/activate
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

Ejecutar la aplicacion desde la raiz del proyecto:

```bash
python audio_transformer.py
```

### Flujo de Trabajo

1. Hacer clic en **[1] Seleccionar Audios** y elegir uno o varios archivos compatibles (`.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.m4a`, `.wma`, `.opus`).
2. Elegir el formato de salida deseado en **[2] Formato destino**.
3. Activar o desactivar la casilla **[3] Mejorar calidad (Filtro Neuronal - EBU R128)** segun se requiera normalizacion de sonoridad.
4. Presionar **[ INICIAR SECUENCIA ]** para comenzar el analisis tonal y la conversion. Los archivos resultantes se guardaran en una carpeta llamada `Audios_Transformados` dentro del mismo directorio de los audios de origen.

## Compilacion a Ejecutable (Opcional)

Para generar un ejecutable independiente en Windows mediante PyInstaller:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --icon=icon.ico --add-data "icon.ico;." --add-data "heuristica.png;." audio_transformer.py
```

## Estructura del Proyecto

```text
audio_transformer/
├── audio_transformer.py   # Codigo fuente principal de la aplicacion
├── requirements.txt       # Dependencias de Python
├── icon.ico               # Icono de la ventana principal
├── heuristica.png         # Logotipo de la interfaz
├── .gitignore             # Reglas de exclusion para control de versiones
└── README.md              # Documentacion tecnica del proyecto
```

## Licencia

Distribuido bajo la licencia MIT.

