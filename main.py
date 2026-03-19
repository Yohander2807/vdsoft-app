import flet as ft
import os
import threading
import yt_dlp
import re
import time

class MyLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"Error: {msg}")

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE PÁGINA ---
    page.title = "VDSoft v4.1 Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = "#121212"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    is_android = os.path.exists("/system/bin/app_process")

    # --- UI CONTROLS ---
    url_input = ft.TextField(
        label="Pegue el enlace de YouTube", 
        border_color="#00B0FF",
        width=380,
        focused_border_color="#00E5FF"
    )

    quality_dropdown = ft.Dropdown(
        label="Calidad / Formato",
        width=380,
        options=[
            ft.dropdown.Option("720", "720p (MP4 - Compatible)"),
            ft.dropdown.Option("480", "480p (MP4 - Ahorro)"),
            ft.dropdown.Option("mp3", "Audio (Original/Webm)"),
        ],
        value="720"
    )

    progress_bar = ft.ProgressBar(value=0, color="#00B0FF", width=380)
    status_label = ft.Text("Estado: Esperando enlace...", color="grey")
    history_list = ft.ListView(expand=True, spacing=10, height=200)

    # --- LÓGICA DE DESCARGA ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','').strip()
                progress_bar.value = float(p) / 100
                status_label.value = f"Descargando... {p}%"
                page.update()
            except: pass

    def run_download(url, quality):
        # Carpeta de descargas
        save_path = "/storage/emulated/0/Download/VDSoft" if is_android else "Descargas_VDSoft"
        if not os.path.exists(save_path):
            try: os.makedirs(save_path, exist_ok=True)
            except: save_path = "./"

        # Ajuste de formato para evitar errores de enlace/FFmpeg
        # Usamos 'best' para asegurar que el servidor entregue un archivo ya combinado
        fmt = "bestaudio/best" if quality == "mp3" else f"best[height<={quality}]/best"

        ydl_opts = {
            'format': fmt,
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'logger': MyLogger(),
            'noplaylist': True,
            # User agent para evitar bloqueos de YouTube
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                status_label.value = "Conectando con YouTube..."
                page.update()
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Video')
                
                history_list.controls.insert(0, ft.ListTile(
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color="green"),
                    title=ft.Text(title, size=12),
                    subtitle=ft.Text(f"Carpeta: Download/VDSoft", size=10)
                ))
                status_label.value = "¡Descarga Exitosa!"
                status_label.color = "green"
        except Exception as e:
            status_label.value = "Error de enlace. Verifica tu conexión."
            status_label.color = "red"
            print(f"DEBUG ERROR: {e}")
        
        progress_bar.value = 0
        page.update()

    def start_click(e):
        if not url_input.value:
            url_input.error_text = "Ingresa un link"
            page.update()
            return
        status_label.value = "Iniciando proceso..."
        page.update()
        threading.Thread(target=run_download, args=(url_input.value, quality_dropdown.value), daemon=True).start()

    # --- DONACIONES (PAYPAL FIX) ---
    def open_paypal(e):
        # Usamos launch_url directamente con el enlace de PayPal
        page.launch_url("https://www.paypal.com/paypalme/smithsanchez2807")

    # --- DISEÑO ---
    page.add(
        ft.Column([
            ft.Text("VDSoft Pro v4.1", size=30, weight="bold", color="#00B0FF"),
            ft.Text("Descargador de Medios Premium", size=14, color="grey"),
            ft.Divider(height=20, color="transparent"),
            url_input,
            quality_dropdown,
            ft.Container(height=10),
            progress_bar,
            status_label,
            ft.ElevatedButton(
                "DESCARGAR", 
                width=380, 
                height=50, 
                on_click=start_click,
                style=ft.ButtonStyle(bgcolor="#00B0FF", color="white")
            ),
            ft.Divider(height=20),
            ft.Text("Historial:", size=16, weight="bold"),
            ft.Container(content=history_list, bgcolor="#1e1e1e", border_radius=10, padding=10),
            ft.Container(height=10),
            ft.ElevatedButton(
                "Apoyar proyecto (PayPal)", 
                icon=ft.Icons.PAYMENT, 
                on_click=open_paypal,
                style=ft.ButtonStyle(color="white", bgcolor="#003087")
            ),
            ft.Text("© 2026 Desarrollado por Yohander Sanchez", size=10, color="grey")
        ], horizontal_alignment="center")
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")