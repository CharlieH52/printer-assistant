import sys
import os
import shutil
import argparse
import subprocess
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

# --------------------------------------------------------------------------- #
# CONFIGURACIÓN
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).parent.resolve()
MAIN_SCRIPT = PROJECT_ROOT / "main.py"
APP_NAME = "PrinterManager"
OUTPUT_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_DIR = PROJECT_ROOT / "specs"

# Dependencias ocultas que PyInstaller podría no detectar automáticamente
HIDDEN_IMPORTS = [
    "win32api",
    "win32print",
    "win32service",
    "win32serviceutil",
    "win32event",
    "win32con",
    "win32gui",
    "pywintypes",
    "ctypes",
    "flet",
    "asyncio",
]

# Módulos binarios implícitos de pywin32
BINARIES = [
    "pywintypes39.dll",
    "pywintypes310.dll",
    "pywintypes311.dll",
    "pywintypes312.dll",
    "pythoncom39.dll",
    "pythoncom310.dll",
    "pythoncom311.dll",
    "pythoncom312.dll",
]

# --------------------------------------------------------------------------- #
# UTILIDADES
# --------------------------------------------------------------------------- #

def log(msg: str, level: str = "INFO") -> None:
    """Imprime mensajes formateados en consola."""
    colors = {"INFO": "[94m", "OK": "[92m", "WARN": "[93m", "ERR": "[91m", "RESET": "[0m"}
    c = colors.get(level, colors["INFO"])
    print(f"{c}[{level}]{colors['RESET']} {msg}")


def clean_previous_builds() -> None:
    """Elimina directorios de builds anteriores para evitar conflictos."""
    dirs_to_clean = [BUILD_DIR, SPEC_DIR]
    for d in dirs_to_clean:
        if d.exists():
            log(f"Eliminando directorio anterior: {d}", "WARN")
            shutil.rmtree(d, ignore_errors=True)


def verify_environment() -> None:
    """Verifica que existan los archivos y dependencias necesarias."""
    if not MAIN_SCRIPT.exists():
        log(f"No se encontró {MAIN_SCRIPT.name} en la raíz del proyecto.", "ERR")
        sys.exit(1)

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        log("PyInstaller no está instalado. Ejecuta: pip install pyinstaller", "ERR")
        sys.exit(1)

    try:
        import flet  # noqa: F401
    except ImportError:
        log("Flet no está instalado. Ejecuta: pip install flet", "ERR")
        sys.exit(1)

    log("Entorno verificado correctamente.", "OK")


def collect_pywin32_binaries() -> list[str]:
    """
    Intenta localizar los DLLs de pywin32 para incluirlos explícitamente.
    Retorna una lista de argumentos --add-binary para PyInstaller.
    """
    args = []
    try:
        import pywin32_system32
        sys32_path = Path(pywin32_system32.__file__).parent
        for dll in BINARIES:
            dll_path = sys32_path / dll
            if dll_path.exists():
                args.extend(["--add-binary", f"{dll_path};."])
                log(f"Incluyendo binario: {dll}", "INFO")
    except Exception as exc:
        log(f"No se pudieron detectar DLLs de pywin32 automáticamente: {exc}", "WARN")
    return args


def build_command(args: argparse.Namespace) -> list[str]:
    """Construye la lista de argumentos para invocar PyInstaller."""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(MAIN_SCRIPT),
        "--name", APP_NAME,
        "--noconfirm",
        "--windowed",           # ← Sin consola (equivalente a --noconsole)
        "--noconsole",          # ← Doble garantía de no mostrar terminal
        "--distpath", str(OUTPUT_DIR),
        "--workpath", str(BUILD_DIR),
        "--specpath", str(SPEC_DIR),
    ]

    # Modo de empaquetado
    if args.onefile:
        cmd.append("--onefile")
        log("Modo de compilación: un solo ejecutable (.exe)", "INFO")
    else:
        cmd.append("--onedir")
        log("Modo de compilación: directorio (más rápido para Flet)", "INFO")

    # Icono personalizado
    if args.icon:
        icon_path = Path(args.icon)
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path.resolve())])
            log(f"Usando icono: {icon_path}", "INFO")
        else:
            log(f"Icono no encontrado: {icon_path}", "WARN")

    # Hidden imports
    for mod in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", mod])

    # Incluir todos los archivos, submódulos y binarios de Flet
    cmd.extend(["--collect-all", "flet"])
    log("Recolectando todos los recursos de Flet", "INFO")

    # Binarios adicionales de pywin32
    cmd.extend(collect_pywin32_binaries())

    # Upx (compresión opcional)
    if args.no_upx:
        cmd.append("--noupx")
    else:
        log("Compresión UPX habilitada (si está disponible)", "INFO")

    return cmd


def run_build(cmd: list[str]) -> int:
    """Ejecuta PyInstaller y retorna el código de salida."""
    log("Ejecutando PyInstaller...", "INFO")
    log(f"Comando: {' '.join(cmd)}", "INFO")
    print("-" * 60)

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    print("-" * 60)
    return result.returncode


def post_build() -> None:
    """Muestra instrucciones finales y verifica el artefacto generado."""
    exe_path = OUTPUT_DIR / APP_NAME / f"{APP_NAME}.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        log(f"¡Compilación exitosa!", "OK")
        log(f"Ejecutable generado: {exe_path}", "OK")
        log(f"Tamaño aproximado: {size_mb:.1f} MB", "INFO")
        log("Ejecute como Administrador para funciones de gestión de impresoras.", "WARN")
    else:
        # En modo onefile la ruta cambia
        onefile_path = OUTPUT_DIR / f"{APP_NAME}.exe"
        if onefile_path.exists():
            size_mb = onefile_path.stat().st_size / (1024 * 1024)
            log(f"¡Compilación exitosa! (onefile)", "OK")
            log(f"Ejecutable generado: {onefile_path}", "OK")
            log(f"Tamaño aproximado: {size_mb:.1f} MB", "INFO")
        else:
            log("No se detectó el ejecutable en la ruta esperada.", "WARN")


def main() -> int:
    """Punto de entrada principal del script de build."""
    parser = argparse.ArgumentParser(
        description="Compila PrinterManager con PyInstaller (sin consola)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Ejemplos:
            python build.py                    # Compilación por defecto (directorio)
            python build.py --onefile          # Empaqueta todo en un solo .exe
            python build.py --clean            # Limpia builds previos antes de compilar
            python build.py --icon app.ico     # Usa un icono personalizado
        """
    )
    parser.add_argument("--onefile", action="store_true", help="Genera un único archivo ejecutable")
    parser.add_argument("--clean", action="store_true", help="Elimina builds anteriores antes de compilar")
    parser.add_argument("--icon", type=str, default=None, help="Ruta al archivo .ico personalizado")
    parser.add_argument("--no-upx", action="store_true", help="Deshabilita compresión UPX")
    args = parser.parse_args()

    log("=" * 60)
    log("  PrinterManager — Script de compilación PyInstaller")
    log("=" * 60)

    verify_environment()

    if args.clean:
        clean_previous_builds()

    cmd = build_command(args)
    exit_code = run_build(cmd)

    if exit_code == 0:
        post_build()
    else:
        log(f"PyInstaller finalizó con código de error: {exit_code}", "ERR")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())