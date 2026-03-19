import flet as ft
import os
import threading
import yt_dlp
import re
import sys
import time

class MyLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"Error: {msg}")

def main(page: ft.Page):
    # --- CONFIGURACIÓN VISUAL ---
    page.title = "VDSoft v4.0 Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = "#121212"
    page.window_width = 450
    page.window_height = 850
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    is_android = os.path.exists("/system/bin/app_process")
    downloaded_files = []

    # --- CONTROLES DE UI ---
    title_text = ft.Text("VDSoft Video Downloader", size=28, weight="bold", color="#00B0FF")
    url_input = ft.TextField(
        label="Enlace de Video", 
        hint_text="https://www.youtube.com/watch?...",
        border_color="#00B0FF",
        width=380
    )

    quality_dropdown = ft.Dropdown(
        label="Seleccionar Calidad",
        width=380,
        options=[
            ft.dropdown.Option("1080", "1080p (Requiere FFmpeg)"),
            ft.dropdown.Option("720", "720p (Recomendado)"),
            ft.dropdown.Option("480", "480p"),
            ft.dropdown.Option("mp3", "Solo Audio (MP3/Webm)"),
        ],
        value="720"
    )

    progress_bar = ft.ProgressBar(value=0, color="#00B0FF", width=380, height=8)
    status_label = ft.Text("Listo para iniciar", color="grey")
    history_list = ft.ListView(expand=True, spacing=10, height=200)

    # --- LÓGICA DE DESCARGA ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                progress_bar.value = float(p) / 100
                status_label.value = f"Descargando... {p}%"
                page.update()
            except: pass

    def run_download(url, quality):
        # Carpeta de descargas en Android o PC
        save_path = "/storage/emulated/0/Download/VDSoft" if is_android else "Descargas_VDSoft"
        if not os.path.exists(save_path):
            try: os.makedirs(save_path, exist_ok=True)
            except: save_path = "./"

        # Configuración de Calidad
        # Nota: 1080p siempre necesita FFmpeg para unir video y audio. 
        # Si no hay FFmpeg, yt-dlp bajará el video sin audio o dará error.
        if quality == "mp3":
            fmt = "bestaudio/best"
        elif quality == "1080":
            fmt = "bestvideo[height<=1080]+bestaudio/best"
        elif quality == "480":
            fmt = "bestvideo[height<=480]+bestaudio/best/best"
        else:
            # 720p 'best' es lo más seguro para Android sin FFmpeg
            fmt = "best[height<=720]/best"

        opts = {
            'format': fmt,
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'logger': MyLogger(),
            'noplaylist': True,
        }

        # Post-procesador para MP3 (Solo funcionará si el sistema tiene FFmpeg)
        if quality == "mp3":
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_title = info.get('title', 'Archivo descargado')
                
                # Actualizar Historial
                history_list.controls.insert(0, ft.ListTile(
                    leading=ft.Icon(ft.Icons.FILE_DOWNLOAD_DONE, color="green"),
                    title=ft.Text(file_title, size=12),
                    subtitle=ft.Text(f"Guardado en: {save_path}", size=10)
                ))
                status_label.value = "¡Éxito! Guardado en Descargas/VDSoft"
                status_label.color = "green"
        except Exception as e:
            status_label.value = "Error: FFmpeg ausente o link caído"
            status_label.color = "red"
        
        progress_bar.value = 0
        page.update()

    def start_process(e):
        if not url_input.value:
            url_input.error_text = "Pega un enlace válido"
            page.update()
            return
        status_label.value = "Analizando enlace..."
        page.update()
        threading.Thread(target=run_download, args=(url_input.value, quality_dropdown.value), daemon=True).start()

    # --- SECCIÓN DE DONACIONES Y FOOTER ---
    donation_btn = ft.TextButton(
        "Apoyar proyecto (PayPal)", 
        icon=ft.Icons.FAVORITE, 
        icon_color="pink",
        on_click=lambda _: page.launch_url("https://www.paypal.me/smithsanchez2807")
    )

    footer = ft.Column([
        ft.Divider(color="#333333"),
        donation_btn,
        ft.Text("Desarrollado por Yohander Sanchez", size=12, color="grey"),
        ft.Text("© 2026 VDSoft | v4.0 Pro", size=10, color="#444444")
    ], horizontal_alignment="center")

    # --- AGREGAR A PÁGINA ---
    page.add(
        ft.Column([
            title_text,
            ft.Text("Soporte para 1080p, 720p y MP3", size=14, color="grey"),
            ft.Container(height=10),
            url_input,
            quality_dropdown,
            ft.Container(height=10),
            progress_bar,
            status_label,
            ft.ElevatedButton(
                "DESCARGAR AHORA", 
                width=380, 
                height=50, 
                on_click=start_process,
                style=ft.ButtonStyle(bgcolor="#00B0FF", color="white")
            ),
            ft.Text("Historial de Descargas:", size=14, weight="bold"),
            ft.Container(content=history_list, bgcolor="#1e1e1e", border_radius=10, padding=10),
            footer
        ], horizontal_alignment="center")
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")