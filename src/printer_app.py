import asyncio
import logging
import sys
from typing import Optional, List

import flet as ft

from src.printer_manager import (
    PrinterManager,
    PrinterData,
    AdminRequiredError,
    PrinterManagerError,
    SpoolerError,
    PrinterOperationError
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrinterApp:
    """
    Vista principal de la aplicación de gestión de impresoras.
    Diseño en tema claro con feedback visual completo.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.manager = PrinterManager(ignore_virtual=True)
        self.selected_printer: Optional[str] = None
        self.printers: List[PrinterData] = []

        # Configuración visual
        self._setup_theme()

        # Componentes UI
        self.printer_list = ft.ListView(expand=True, spacing=2, padding=10)
        self.status_text = ft.Text("Listo", size=12, color=ft.Colors.GREY_700)
        self.spooler_badge = ft.Chip(
            label=ft.Text("Spooler: ..."),
            bgcolor=ft.Colors.GREY_300
        )

        # Overlay de carga (bloquea toda la interfaz)
        self.loading_indicator = ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(width=50, height=50, stroke_width=4),
                    ft.Text("Procesando...", size=16, weight=ft.FontWeight.W_500)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
            alignment=ft.Alignment.CENTER,
            expand=True,
            visible=False,
            # animate_opacity=ft.Animation.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
        )

        # Diálogo de confirmación genérico
        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar acción"),
            content=ft.Text("¿Está seguro?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self._close_dialog),
                ft.ElevatedButton("Confirmar", on_click=self._on_confirm, color=ft.Colors.RED)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self._pending_action: Optional[callable] = None

        self._build_ui()

    # --------------------------------------------------------------------- #
    # THEME & LAYOUT
    # --------------------------------------------------------------------- #

    def _setup_theme(self) -> None:
        """Configura el tema claro y la paleta de colores."""
        self.page.title = "Gestor de Impresoras"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 950
        self.page.window_height = 750
        self.page.window_min_width = 700
        self.page.window_min_height = 500
        self.page.padding = 0
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE_700,
            use_material3=True
        )

    def _build_ui(self) -> None:
        """Construye la estructura visual completa."""
        # Barra superior
        app_bar = ft.AppBar(
            title=ft.Text("Gestor de Impresoras Windows", size=20, weight=ft.FontWeight.W_600),
            center_title=False,
            bgcolor=ft.Colors.BLUE_50,
            actions=[
                ft.Container(
                    content=self.spooler_badge,
                    padding=ft.Padding.only(right=15)
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Actualizar lista",
                    on_click=self._on_refresh
                ),
            ]
        )

        # Panel lateral de acciones
        action_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Acciones", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.BLUE_GREY_800),
                    ft.Divider(height=1),
                    ft.ElevatedButton(
                        "Página de prueba",
                        icon=ft.Icons.PRINT,
                        on_click=self._on_test_page,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "Propiedades",
                        icon=ft.Icons.SETTINGS,
                        on_click=self._on_properties,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "Cancelar trabajos",
                        icon=ft.Icons.CANCEL_PRESENTATION,
                        on_click=self._on_cancel_jobs,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "Predeterminar",
                        icon=ft.Icons.STAR,
                        on_click=self._on_set_default,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        expand=True
                    ),
                    ft.Divider(height=1),
                    ft.ElevatedButton(
                        "Iniciar Spooler",
                        icon=ft.Icons.PLAY_ARROW,
                        on_click=self._on_start_spooler,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            bgcolor=ft.Colors.GREEN_50
                        ),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "Detener Spooler",
                        icon=ft.Icons.STOP,
                        on_click=self._on_stop_spooler,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            bgcolor=ft.Colors.RED_50
                        ),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "Reiniciar Spooler",
                        icon=ft.Icons.RESTART_ALT,
                        on_click=self._on_restart_spooler,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            bgcolor=ft.Colors.ORANGE_50
                        ),
                        expand=True
                    ),
                    ft.Divider(height=1),
                    ft.ElevatedButton(
                        "Eliminar impresora",
                        icon=ft.Icons.DELETE_FOREVER,
                        on_click=self._on_delete_printer,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            bgcolor=ft.Colors.RED_50,
                            color=ft.Colors.RED_700
                        ),
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "Eliminar todas (excepto selección)",
                        icon=ft.Icons.DELETE_SWEEP,
                        on_click=self._on_delete_all_except,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            bgcolor=ft.Colors.RED_100,
                            color=ft.Colors.RED_800
                        ),
                        expand=True
                    ),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO
            ),
            width=280,
            padding=20,
            bgcolor=ft.Colors.GREY_50,
            border=ft.Border.only(right=ft.BorderSide(1, ft.Colors.GREY_300))
        )

        # Área principal de lista
        list_header = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Impresoras detectadas", size=18, weight=ft.FontWeight.W_600),
                    ft.Container(
                        content=ft.Text("Seleccione una impresora", size=12, color=ft.Colors.GREY_600, italic=True),
                        padding=ft.Padding.only(left=10)
                    )
                ]
            ),
            padding=ft.Padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200))
        )

        list_area = ft.Column(
            [
                list_header,
                ft.Container(
                    content=self.printer_list,
                    expand=True,
                    padding=ft.Padding.only(bottom=10)
                ),
                ft.Container(
                    content=self.status_text,
                    padding=ft.Padding.symmetric(horizontal=20, vertical=10),
                    border=ft.Border.only(top=ft.BorderSide(1, ft.Colors.GREY_200)),
                    bgcolor=ft.Colors.GREY_50
                )
            ],
            expand=True,
            spacing=0
        )

        # Layout principal con overlay de carga
        main_layout = ft.Stack(
            [
                ft.Row(
                    [action_panel, ft.VerticalDivider(width=1), list_area],
                    expand=True,
                    spacing=0
                ),
                self.loading_indicator
            ],
            expand=True
        )

        self.page.appbar = app_bar
        self.page.dialog = self.confirm_dialog
        self.page.add(main_layout)

        # Carga inicial
        self.page.run_task(self._load_initial_data)

    # --------------------------------------------------------------------- #
    # FEEDBACK & UTILIDADES UI
    # --------------------------------------------------------------------- #

    def _show_loading(self, message: str = "Procesando...") -> None:
        """Muestra el overlay de carga y deshabilita la interacción."""
        self.loading_indicator.content.controls[1].value = message  # type: ignore
        self.loading_indicator.visible = True
        self.loading_indicator.opacity = 1
        self.page.update()

    def _hide_loading(self) -> None:
        """Oculta el overlay de carga."""
        self.loading_indicator.visible = False
        self.page.update()

    def _show_snack(self, message: str, success: bool = True) -> None:
        """
        Muestra una alerta tipo SnackBar en la parte inferior.
        
        Args:
            message: Texto a mostrar.
            success: True para estilo éxito (verde), False para error (rojo).
        """
        color = ft.Colors.GREEN_700 if success else ft.Colors.RED_700
        bg_color = ft.Colors.GREEN_50 if success else ft.Colors.RED_50
        icon = ft.Icons.CHECK_CIRCLE if success else ft.Icons.ERROR

        snack = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(icon, color=color, size=20),
                    ft.Text(message, color=color, weight=ft.FontWeight.W_500)
                ],
                spacing=10
            ),
            bgcolor=bg_color,
            duration=4000,
            show_close_icon=True,
            close_icon_color=color
        )
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()

    def _confirm_action(self, title: str, message: str, action: callable) -> None:
        """
        Muestra un diálogo de confirmación antes de ejecutar una acción destructiva.
        
        Args:
            title: Título del diálogo.
            message: Contenido descriptivo.
            action: Función a ejecutar si se confirma.
        """
        self.confirm_dialog.title = ft.Text(title)
        self.confirm_dialog.content = ft.Text(message)
        self._pending_action = action
        self.confirm_dialog.open = True
        self.page.update()

    def _close_dialog(self, e=None) -> None:
        """Cierra el diálogo de confirmación."""
        self.confirm_dialog.open = False
        self._pending_action = None
        self.page.update()

    def _on_confirm(self, e) -> None:
        """Ejecuta la acción pendiente tras confirmación."""
        if self._pending_action:
            action = self._pending_action
            self._close_dialog()
            # Ejecutamos en task para no bloquear
            self.page.run_task(action)
        else:
            self._close_dialog()

    def _update_status(self, text: str) -> None:
        """Actualiza el texto de estado inferior."""
        self.status_text.value = text
        self.page.update()

    # --------------------------------------------------------------------- #
    # LÓGICA DE LISTA DE IMPRESORAS
    # --------------------------------------------------------------------- #

    async def _load_initial_data(self) -> None:
        """Carga inicial de impresoras y estado del spooler."""
        await self._refresh_printers()
        await self._refresh_spooler_status()

    async def _refresh_printers(self) -> None:
        """Recarga la lista de impresoras y actualiza la UI."""
        self._show_loading("Cargando impresoras...")
        try:
            self.printers = await asyncio.to_thread(self.manager.get_printers)
            self._render_printer_list()
            self._update_status(f"{len(self.printers)} impresora(s) detectada(s)")
        except PrinterManagerError as exc:
            self._show_snack(str(exc), success=False)
            self._update_status("Error al cargar impresoras")
        finally:
            self._hide_loading()

    def _render_printer_list(self) -> None:
        """Renderiza las tarjetas de impresora en la lista."""
        self.printer_list.controls.clear()

        if not self.printers:
            self.printer_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.PRINT_DISABLED, size=48, color=ft.Colors.GREY_400),
                            ft.Text("No se encontraron impresoras", color=ft.Colors.GREY_500)
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=40
                )
            )
            self.page.update()
            return

        for printer in self.printers:
            is_selected = self.selected_printer == printer.name
            card = ft.Card(
                content=ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.STAR if printer.is_default else ft.Icons.PRINT,
                            color=ft.Colors.BLUE_700 if is_selected else ft.Colors.GREY_600
                        ),
                        title=ft.Text(
                            printer.name,
                            weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.W_400,
                            color=ft.Colors.BLUE_900 if is_selected else ft.Colors.BLACK87
                        ),
                        subtitle=ft.Text(
                            f"{'🖥️ Local' if printer.is_local else '🌐 Compartida'}  •  "
                            f"Puerto: {printer.port}  •  Driver: {printer.driver}  •  "
                            f"Estado: {printer.status}",
                            size=12
                        ),
                        trailing=ft.Icon(
                            ft.Icons.RADIO_BUTTON_CHECKED if is_selected else ft.Icons.RADIO_BUTTON_UNCHECKED,
                            color=ft.Colors.BLUE_700 if is_selected else ft.Colors.GREY_400
                        ),
                        on_click=lambda e, name=printer.name: self._on_printer_select(name)
                    ),
                    bgcolor=ft.Colors.BLUE_50 if is_selected else ft.Colors.WHITE,
                    border_radius=10,
                    padding=5
                ),
                elevation=2 if is_selected else 0,
                margin=ft.Margin.symmetric(vertical=3, horizontal=5)
            )
            self.printer_list.controls.append(card)

        self.page.update()

    def _on_printer_select(self, name: str) -> None:
        """Maneja la selección de una impresora de la lista."""
        self.selected_printer = name
        self._render_printer_list()
        self._update_status(f"Seleccionada: {name}")

    # --------------------------------------------------------------------- #
    # ACCIONES DE BOTONES
    # --------------------------------------------------------------------- #

    async def _on_refresh(self, e=None) -> None:
        """Refresca la lista completa."""
        await self._refresh_printers()
        await self._refresh_spooler_status()
        self._show_snack("Lista actualizada")

    async def _refresh_spooler_status(self) -> None:
        """Actualiza el badge visual del estado del Spooler."""
        try:
            running, state = await asyncio.to_thread(self.manager.get_spooler_status)
            if running:
                self.spooler_badge.label = ft.Text(f"Spooler: {state} ✅")
                self.spooler_badge.bgcolor = ft.Colors.GREEN_100
            else:
                self.spooler_badge.label = ft.Text(f"Spooler: {state} ⚠️")
                self.spooler_badge.bgcolor = ft.Colors.ORANGE_100
            self.page.update()
        except Exception as exc:
            logger.error("Error consultando spooler: %s", exc)
            self.spooler_badge.label = ft.Text("Spooler: Error ❌")
            self.spooler_badge.bgcolor = ft.Colors.RED_100
            self.page.update()

    # --- Acciones de impresora ---

    async def _on_test_page(self, e=None) -> None:
        if not self._validate_selection():
            return
        self._show_loading("Enviando página de prueba...")
        try:
            await asyncio.to_thread(self.manager.print_test_page, self.selected_printer)
            self._show_snack(f"Página de prueba enviada a {self.selected_printer}")
        except AdminRequiredError as exc:
            self._show_snack(str(exc), success=False)
        except PrinterOperationError as exc:
            self._show_snack(str(exc), success=False)
        except Exception as exc:
            self._show_snack(f"Error inesperado: {exc}", success=False)
        finally:
            self._hide_loading()

    async def _on_properties(self, e=None) -> None:
        if not self._validate_selection():
            return
        try:
            await asyncio.to_thread(self.manager.open_printer_properties, self.selected_printer)
            self._show_snack("Ventana de propiedades abierta")
        except Exception as exc:
            self._show_snack(str(exc), success=False)

    async def _on_cancel_jobs(self, e=None) -> None:
        if not self._validate_selection():
            return
        self._show_loading("Cancelando trabajos...")
        try:
            count = await asyncio.to_thread(self.manager.cancel_all_jobs, self.selected_printer)
            msg = f"{count} trabajo(s) cancelado(s)" if count > 0 else "No había trabajos pendientes"
            self._show_snack(msg)
        except PrinterOperationError as exc:
            self._show_snack(str(exc), success=False)
        except Exception as exc:
            self._show_snack(f"Error: {exc}", success=False)
        finally:
            self._hide_loading()

    async def _on_set_default(self, e=None) -> None:
        if not self._validate_selection():
            return
        self._show_loading("Estableciendo impresora predeterminada...")
        try:
            await asyncio.to_thread(self.manager.set_default_printer, self.selected_printer)
            await self._refresh_printers()
            self._show_snack(f"{self.selected_printer} es ahora la predeterminada")
        except Exception as exc:
            self._show_snack(str(exc), success=False)
        finally:
            self._hide_loading()

    async def _on_delete_printer(self, e=None) -> None:
        if not self._validate_selection():
            return
        self._confirm_action(
            title="Eliminar impresora",
            message=f"¿Eliminar permanentemente '{self.selected_printer}'?\n\n"
                    f"Esta acción no se puede deshacer. Se eliminará solo el controlador del sistema, no el software del driver.",
            action=self._do_delete_printer
        )

    async def _do_delete_printer(self) -> None:
        self._show_loading("Eliminando impresora...")
        try:
            await asyncio.to_thread(self.manager.delete_printer, self.selected_printer)
            self.selected_printer = None
            await self._refresh_printers()
            self._show_snack("Impresora eliminada correctamente")
        except AdminRequiredError as exc:
            self._show_snack(str(exc), success=False)
        except PrinterOperationError as exc:
            self._show_snack(str(exc), success=False)
        except Exception as exc:
            self._show_snack(f"Error: {exc}", success=False)
        finally:
            self._hide_loading()

    async def _on_delete_all_except(self, e=None) -> None:
        if not self._validate_selection():
            self._show_snack("Seleccione la impresora que desea conservar", success=False)
            return
        self._confirm_action(
            title="Eliminación masiva",
            message=f"Se eliminarán TODAS las impresoras excepto:\n\n"
                    f"🖨️  {self.selected_printer}\n\n"
                    f"¿Desea continuar?",
            action=self._do_delete_all_except
        )

    async def _do_delete_all_except(self) -> None:
        self._show_loading("Eliminando impresoras...")
        try:
            deleted = await asyncio.to_thread(self.manager.delete_all_except, self.selected_printer)
            await self._refresh_printers()
            self._show_snack(f"{len(deleted)} impresora(s) eliminada(s)")
        except AdminRequiredError as exc:
            self._show_snack(str(exc), success=False)
        except Exception as exc:
            self._show_snack(f"Error: {exc}", success=False)
        finally:
            self._hide_loading()

    # --- Acciones de Spooler ---

    async def _on_start_spooler(self, e=None) -> None:
        self._show_loading("Iniciando servicio Spooler...")
        try:
            await asyncio.to_thread(self.manager.start_spooler)
            await self._refresh_spooler_status()
            self._show_snack("Servicio Spooler iniciado")
        except AdminRequiredError as exc:
            self._show_snack(str(exc), success=False)
        except SpoolerError as exc:
            self._show_snack(str(exc), success=False)
        except Exception as exc:
            self._show_snack(f"Error: {exc}", success=False)
        finally:
            self._hide_loading()

    async def _on_stop_spooler(self, e=None) -> None:
        self._show_loading("Deteniendo servicio Spooler...")
        try:
            await asyncio.to_thread(self.manager.stop_spooler)
            await self._refresh_spooler_status()
            self._show_snack("Servicio Spooler detenido")
        except AdminRequiredError as exc:
            self._show_snack(str(exc), success=False)
        except SpoolerError as exc:
            self._show_snack(str(exc), success=False)
        except Exception as exc:
            self._show_snack(f"Error: {exc}", success=False)
        finally:
            self._hide_loading()

    async def _on_restart_spooler(self, e=None) -> None:
        self._show_loading("Reiniciando servicio Spooler...")
        try:
            await asyncio.to_thread(self.manager.restart_spooler)
            await self._refresh_spooler_status()
            self._show_snack("Servicio Spooler reiniciado")
        except AdminRequiredError as exc:
            self._show_snack(str(exc), success=False)
        except SpoolerError as exc:
            self._show_snack(str(exc), success=False)
        except Exception as exc:
            self._show_snack(f"Error: {exc}", success=False)
        finally:
            self._hide_loading()

    # --------------------------------------------------------------------- #
    # VALIDACIONES
    # --------------------------------------------------------------------- #

    def _validate_selection(self) -> bool:
        """Valida que haya una impresora seleccionada antes de operar."""
        if not self.selected_printer:
            self._show_snack("Seleccione una impresora de la lista primero", success=False)
            return False
        return True