"""
PrinterManager — Módulo de gestión de impresoras Windows.
Refactorizado con pywin32, PowerShell fallback, tipado estricto
y manejo estructurado de excepciones.
"""

import logging
import subprocess
import ctypes
import sys
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import List, Optional, Dict, Tuple
from pathlib import Path

# pywin32
import win32print
import win32service
import win32api

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class PrinterManagerError(Exception):
    """Excepción base para errores del gestor de impresoras."""
    pass


class AdminRequiredError(PrinterManagerError):
    """Se requieren privilegios de administrador."""
    pass


class SpoolerError(PrinterManagerError):
    """Error relacionado con el servicio de cola de impresión."""
    pass


class PrinterOperationError(PrinterManagerError):
    """Error en una operación sobre una impresora específica."""
    pass


class SpoolerState(IntEnum):
    """Estados del servicio Spooler basados en Win32 Service API."""
    STOPPED = win32service.SERVICE_STOPPED          # 0x00000001
    STARTING = win32service.SERVICE_START_PENDING    # 0x00000002
    STOPPING = win32service.SERVICE_STOP_PENDING     # 0x00000003
    RUNNING = win32service.SERVICE_RUNNING           # 0x00000004
    CONTINUING = win32service.SERVICE_CONTINUE_PENDING
    PAUSING = win32service.SERVICE_PAUSE_PENDING
    PAUSED = win32service.SERVICE_PAUSED


@dataclass(frozen=True)
class PrinterData:
    """Modelo inmutable de datos de una impresora."""
    name: str
    share_name: Optional[str]
    port: str
    driver: str
    is_local: bool
    is_shared: bool
    is_default: bool
    status: str


class PrinterManager:
    """
    Gestor de impresoras Windows con soporte pywin32 nativo
    y comandos PowerShell como fallback robusto.
    """

    # Impresoras virtuales a ignorar en listados por defecto
    VIRTUAL_KEYWORDS: Tuple[str, ...] = (
        'OneNote', 'Fax', 'Microsoft Print to PDF',
        'PDF', 'XPS', 'Fax', 'OneNote (Desktop)'
    )

    def __init__(self, ignore_virtual: bool = True) -> None:
        self._ignore_virtual = ignore_virtual
        self._admin_cache: Optional[bool] = None

    # --------------------------------------------------------------------- #
    # UTILIDADES INTERNAS
    # --------------------------------------------------------------------- #

    @staticmethod
    def is_admin() -> bool:
        """
        Verifica si el proceso actual tiene privilegios elevados.
        
        Returns:
            True si es administrador, False en caso contrario.
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as exc:
            logger.warning("No se pudo verificar estado de admin: %s", exc)
            return False

    def _require_admin(self) -> None:
        """Lanza AdminRequiredError si no se tienen privilegios de administrador."""
        if self._admin_cache is None:
            self._admin_cache = self.is_admin()
        if not self._admin_cache:
            raise AdminRequiredError(
                "Esta operación requiere privilegios de Administrador. "
                "Ejecute la aplicación como administrador."
            )

    @staticmethod
    def _run_powershell(command: str, timeout: int = 30) -> subprocess.CompletedProcess:
        """
        Ejecuta un comando PowerShell de forma segura sin shell=True.
        
        Args:
            command: Comando PowerShell a ejecutar.
            timeout: Tiempo máximo de espera en segundos.
            
        Returns:
            Resultado del proceso completado.
            
        Raises:
            PrinterManagerError: Si el comando falla o excede el tiempo.
        """
        ps_args = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-Command",
            command
        ]
        try:
            result = subprocess.run(
                ps_args,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,  # Seguro: no interpeta shell
                encoding="utf-8",
                errors="ignore"
            )
            return result
        except subprocess.TimeoutExpired as exc:
            raise PrinterManagerError(f"Tiempo excedido ejecutando comando PowerShell: {exc}") from exc
        except FileNotFoundError as exc:
            raise PrinterManagerError("PowerShell no está disponible en el sistema.") from exc
        except Exception as exc:
            raise PrinterManagerError(f"Error ejecutando PowerShell: {exc}") from exc

    def _filter_virtual(self, printers: List[PrinterData]) -> List[PrinterData]:
        """Filtra impresoras virtuales si está configurado."""
        if not self._ignore_virtual:
            return printers
        return [
            p for p in printers
            if not any(vk.lower() in p.name.lower() for vk in self.VIRTUAL_KEYWORDS)
        ]

    # --------------------------------------------------------------------- #
    # LISTADO DE IMPRESORAS
    # --------------------------------------------------------------------- #

    def get_printers(self) -> List[PrinterData]:
        """
        Obtiene todas las impresoras (locales y de conexión) con metadatos enriquecidos.
        
        Returns:
            Lista de objetos PrinterData.
            
        Raises:
            PrinterManagerError: Si no se puede acceder al subsistema de impresión.
        """
        printers: List[PrinterData] = []
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS

        try:
            raw_printers = win32print.EnumPrinters(
                flags,
                None,
                2  # Nivel 2: más metadatos (nombre, puerto, driver, etc.)
            )
        except Exception as exc:
            logger.error("EnumPrinters falló: %s", exc)
            raise PrinterManagerError(f"No se pudo enumerar impresoras: {exc}") from exc

        default_printer = ""
        try:
            default_printer = win32print.GetDefaultPrinter()
        except Exception:
            pass  # Puede no haber impresora por defecto

        for p in raw_printers:
            try:
                info = PrinterData(
                    name=p.get("pPrinterName", "Desconocida"),
                    share_name=p.get("pShareName") or None,
                    port=p.get("pPortName", "N/A"),
                    driver=p.get("pDriverName", "N/A"),
                    is_local=bool(p.get("Attributes", 0) & win32print.PRINTER_ATTRIBUTE_LOCAL),
                    is_shared=bool(p.get("Attributes", 0) & win32print.PRINTER_ATTRIBUTE_SHARED),
                    is_default=p.get("pPrinterName") == default_printer,
                    status=self._decode_status(p.get("Status", 0))
                )
                printers.append(info)
            except Exception as exc:
                logger.warning("Error parseando impresora %s: %s", p, exc)
                continue

        return self._filter_virtual(printers)

    @staticmethod
    def _decode_status(status_code: int) -> str:
        """Decodifica el código de estado Win32 a texto legible."""
        mapping = {
            0: "Desconocido",
            1: "Otros",
            2: "Desconocido",
            3: "Inactiva",
            4: "Impresión",
            5: "Calentamiento",
            6: "Detenida",
            7: "Entrada manual",
            8: "Fuera de línea",
            9: "Falta papel",
            10: "Atasco de papel",
            11: "Puerta abierta",
            12: "Error de impresora",
            13: "En pausa",
            14: "Error de memoria",
            15: "Disponible",
            16: "Selección manual requerida",
            17: "Procesando",
            18: "Inicializando",
            19: "Apagando",
            20: "Reanudando",
            21: "Eliminando",
        }
        return mapping.get(status_code, f"Estado código {status_code}")

    # --------------------------------------------------------------------- #
    # SERVICIO SPOOLER
    # --------------------------------------------------------------------- #

    def get_spooler_status(self) -> Tuple[bool, str]:
        """
        Consulta el estado del servicio Spooler.
        
        Returns:
            Tupla (está_corriendo, descripción_texto).
        """
        try:
            # Método nativo pywin32
            scm = win32service.OpenSCManager(
                None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE
            )
            try:
                service = win32service.OpenService(
                    scm, "spooler", win32service.SERVICE_QUERY_STATUS
                )
                try:
                    status = win32service.QueryServiceStatus(service)[1]
                    is_running = status == SpoolerState.RUNNING
                    state_name = SpoolerState(status).name if status in SpoolerState._value2member_map_ else f"Código {status}"
                    return is_running, state_name
                finally:
                    win32service.CloseServiceHandle(service)
            finally:
                win32service.CloseServiceHandle(scm)
        except Exception as exc:
            logger.warning("Fallo consulta nativa de Spooler, intentando PowerShell: %s", exc)
            # Fallback PowerShell
            result = self._run_powershell("(Get-Service spooler).Status")
            state = result.stdout.strip()
            is_running = state == "Running"
            return is_running, state

    def start_spooler(self) -> None:
        """
        Inicia el servicio Spooler.
        
        Raises:
            AdminRequiredError: Si no hay permisos de administrador.
            SpoolerError: Si no se puede iniciar el servicio.
        """
        self._require_admin()
        running, _ = self.get_spooler_status()
        if running:
            logger.info("Spooler ya está en ejecución.")
            return

        try:
            scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_CONNECT)
            service = win32service.OpenService(
                scm, "spooler", win32service.SERVICE_START
            )
            win32service.StartService(service, None)
            win32service.CloseServiceHandle(service)
            win32service.CloseServiceHandle(scm)
            logger.info("Servicio Spooler iniciado correctamente.")
        except Exception as exc:
            logger.error("Error iniciando Spooler vía API: %s", exc)
            # Fallback PowerShell
            result = self._run_powershell("Start-Service spooler -ErrorAction Stop")
            if result.returncode != 0:
                raise SpoolerError(f"No se pudo iniciar Spooler: {result.stderr}") from exc

    def stop_spooler(self) -> None:
        """
        Detiene el servicio Spooler.
        
        Raises:
            AdminRequiredError: Si no hay permisos de administrador.
            SpoolerError: Si no se puede detener el servicio.
        """
        self._require_admin()
        running, _ = self.get_spooler_status()
        if not running:
            logger.info("Spooler ya está detenido.")
            return

        try:
            scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_CONNECT)
            service = win32service.OpenService(
                scm, "spooler", win32service.SERVICE_STOP
            )
            win32service.ControlService(service, win32service.SERVICE_CONTROL_STOP)
            win32service.CloseServiceHandle(service)
            win32service.CloseServiceHandle(scm)
            logger.info("Servicio Spooler detenido correctamente.")
        except Exception as exc:
            logger.error("Error deteniendo Spooler vía API: %s", exc)
            result = self._run_powershell("Stop-Service spooler -Force -ErrorAction Stop")
            if result.returncode != 0:
                raise SpoolerError(f"No se pudo detener Spooler: {result.stderr}") from exc

    def restart_spooler(self) -> None:
        """Reinicia el servicio Spooler."""
        self.stop_spooler()
        self.start_spooler()

    # --------------------------------------------------------------------- #
    # OPERACIONES SOBRE IMPRESORAS
    # --------------------------------------------------------------------- #

    def print_test_page(self, printer_name: str) -> None:
        """
        Envía una página de prueba a la impresora especificada.
        
        Args:
            printer_name: Nombre exacto de la impresora.
            
        Raises:
            AdminRequiredError: Si no hay permisos de administrador.
            PrinterOperationError: Si la impresora no existe o falla la operación.
        """
        self._require_admin()
        logger.info("Enviando página de prueba a: %s", printer_name)

        # Primero verificamos que exista
        printers = self.get_printers()
        target = next((p for p in printers if p.name == printer_name), None)
        if not target:
            raise PrinterOperationError(f"La impresora '{printer_name}' no existe.")

        try:
            # Método WMI/CIM vía PowerShell (más confiable que wmic deprecado)
            safe_printer_name = printer_name.replace("'", "''")

            ps_cmd = (
                f"$printer = Get-CimInstance -ClassName Win32_Printer | "
                f"Where-Object {{ $_.Name -eq '{safe_printer_name}' }}; "
                f"if ($null -eq $printer) {{ "
                f"Write-Error 'No se encontró la impresora'; exit 1 "
                f"}}; "
                f"$result = Invoke-CimMethod -InputObject $printer "
                f"-MethodName PrintTestPage; "
                f"$result.ReturnValue"
            )
            result = self._run_powershell(ps_cmd)
            if result.returncode != 0:
                raise PrinterOperationError(result.stderr)

            # ReturnValue 0 = éxito en WMI
            rv = result.stdout.strip()
            if rv != "0":
                raise PrinterOperationError(f"WMI retornó código de error: {rv}")
            logger.info("Página de prueba enviada exitosamente.")
        except Exception as exc:
            if isinstance(exc, PrinterOperationError):
                raise
            raise PrinterOperationError(f"Error enviando página de prueba: {exc}") from exc

    def cancel_all_jobs(self, printer_name: str) -> int:
        """
        Cancela todos los trabajos de impresión pendientes.
        
        Args:
            printer_name: Nombre exacto de la impresora.
            
        Returns:
            Cantidad de trabajos cancelados.
            
        Raises:
            PrinterOperationError: Si falla la operación.
        """
        logger.info("Cancelando trabajos de: %s", printer_name)
        try:
            handle = win32print.OpenPrinter(printer_name)
            try:
                jobs = win32print.EnumJobs(handle, 0, -1, 1)
                count = 0
                for job in jobs:
                    win32print.SetJob(handle, job["JobId"], None, win32print.JOB_CONTROL_DELETE)
                    count += 1
                logger.info("%d trabajos cancelados.", count)
                return count
            finally:
                win32print.ClosePrinter(handle)
        except Exception as exc:
            # Fallback: usar PowerShell
            ps_cmd = (
                f"Get-PrintJob -PrinterName '{printer_name}' | "
                f"Remove-PrintJob -ErrorAction SilentlyContinue; "
                f"(Get-PrintJob -PrinterName '{printer_name}').Count"
            )
            result = self._run_powershell(ps_cmd)
            if result.returncode != 0:
                raise PrinterOperationError(f"Error cancelando trabajos: {result.stderr}") from exc
            return 0  # No podemos saber el conteo exacto en fallback silencioso

    def open_printer_properties(self, printer_name: str) -> None:
        """
        Abre el diálogo de propiedades de Windows para la impresora.
        
        Args:
            printer_name: Nombre exacto de la impresora.
        """
        logger.info("Abriendo propiedades de: %s", printer_name)
        # rundll32 es seguro aquí porque el nombre se pasa entrecomillado
        # pero usamos listas para evitar inyección
        cmd = [
            "rundll32.exe",
            "printui.dll,PrintUIEntry",
            "/p",
            "/n",
            printer_name
        ]
        try:
            subprocess.run(cmd, check=False, shell=False)
        except Exception as exc:
            raise PrinterOperationError(f"No se pudieron abrir las propiedades: {exc}") from exc

    def delete_printer(self, printer_name: str) -> None:
        """
        Elimina el controlador de impresora del sistema (no el software del driver).
        
        Args:
            printer_name: Nombre exacto de la impresora.
            
        Raises:
            AdminRequiredError: Si no hay permisos de administrador.
            PrinterOperationError: Si la impresora no existe o no se puede eliminar.
        """
        self._require_admin()
        logger.info("Eliminando impresora: %s", printer_name)

        # Verificar existencia
        printers = self.get_printers()
        if not any(p.name == printer_name for p in printers):
            raise PrinterOperationError(f"La impresora '{printer_name}' no existe.")

        try:
            win32print.DeletePrinter(printer_name)
            logger.info("Impresora eliminada correctamente.")
        except Exception as exc:
            # Fallback PowerShell
            ps_cmd = f"Remove-Printer -Name '{printer_name}' -ErrorAction Stop"
            result = self._run_powershell(ps_cmd)
            if result.returncode != 0:
                raise PrinterOperationError(f"Error eliminando impresora: {result.stderr}") from exc

    def delete_all_except(self, keep_printer: str) -> List[str]:
        """
        Elimina todas las impresoras excepto la especificada.
        
        Args:
            keep_printer: Nombre de la impresora a preservar.
            
        Returns:
            Lista de nombres de impresoras eliminadas.
            
        Raises:
            AdminRequiredError: Si no hay permisos de administrador.
        """
        self._require_admin()
        printers = self.get_printers()
        deleted: List[str] = []

        for p in printers:
            if p.name != keep_printer:
                try:
                    self.delete_printer(p.name)
                    deleted.append(p.name)
                except Exception as exc:
                    logger.error("No se pudo eliminar %s: %s", p.name, exc)
        return deleted

    def set_default_printer(self, printer_name: str) -> None:
        """
        Establece la impresora por defecto del sistema.
        
        Args:
            printer_name: Nombre exacto de la impresora.
        """
        try:
            win32print.SetDefaultPrinter(printer_name)
            logger.info("Impresora por defecto cambiada a: %s", printer_name)
        except Exception as exc:
            raise PrinterOperationError(f"No se pudo establecer como predeterminada: {exc}") from exc   