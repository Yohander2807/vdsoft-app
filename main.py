import flet as ft
import os
import threading
import yt_dlp
import re
import sys
import time

# Intentamos importar el binario de FFmpeg para Android
try:
    import ffmpeg_android_bin
    FFMPEG_ANDROID_PATH = ffmpeg_android_bin.get_bin_path()
except ImportError:
    FFMPEG_ANDROID_PATH = None

class MyLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"Error: {msg}")

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE PÁGINA ---
    page.title = "VDSoft Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = "#1a1a1a"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Detectar si es Android
    is_android = os.path.exists("/system/bin/app_process")

    # --- LÓGICA DE RUTAS ---
    def get_ffmpeg_exe():
        if is_android and FFMPEG_ANDROID_PATH:
            return FFMPEG_ANDROID_PATH
        # En Windows/Linux, intentamos usar el comando global 'ffmpeg'
        return "ffmpeg"

    def get_download_folder():
        if is_android:
            # Ruta estándar para la carpeta de Descargas en la mayoría de Android
            path = "/storage/emulated/0/Download/VDSoft"
        else:
            path = "Descargas_VDSoft"
        
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except:
                # Si falla por permisos, usamos la carpeta local de la app
                path = "./descargas"
                os.makedirs(path, exist_ok=True)
        return path

    # --- UI CONTROLS ---
    title = ft.Text("VDSoft Downloader", size=28, color=ft.Colors.BLUE_400, weight=ft.FontWeight.BOLD)
    url_input = ft.TextField(
        label="Pegue el enlace de YouTube", 
        border_color=ft.Colors.BLUE_400, 
        width=350,
        text_size=14
    )
    
    quality_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="720", label="720p"),
            ft.Radio(value="1080", label="1080p"),
            ft.Radio(value="mp3", label="MP3"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="720"
    )

    progress_bar = ft.ProgressBar(value=0, color=ft.Colors.BLUE_400, width=350)
    status_label = ft.Text("Listo para descargar", color=ft.Colors.GREY_400, size=12)
    history_list = ft.ListView(expand=True, spacing=5)

    # --- PROCESO DE DESCARGA ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            p_raw = d.get('_percent_str', '0%')
            p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_raw).replace('%', '').strip()
            try:
                val = float(p_clean) / 100
                progress_bar.value = val
                status_label.value = f"Descargando... {int(val*100)}%"
                page.update()
            except: pass
        elif d['status'] == 'finished':
            status_label.value = "Procesando archivo final..."
            page.update()

    def run_download(url, quality):
        folder = get_download_folder()
        ffmpeg_path = get_ffmpeg_exe()

        # Configuración de calidad
        if quality == "mp3":
            fmt = "bestaudio/best"
        elif quality == "1080":
            fmt = "bestvideo[height<=1080]+bestaudio/best"
        else:
            fmt = "bestvideo[height<=720]+bestaudio/best"

        opts = {
            'format': fmt,
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'logger': MyLogger(),
            'ffmpeg_location': ffmpeg_path,
            'noplaylist': True,
        }

        if quality == "mp3":
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                history_list.controls.insert(0, ft.ListTile(
                    title=ft.Text(info.get('title', 'Video'), size=12),
                    leading=ft.Icon(ft.Icons.DOWNLOAD_DONE, color="green")
                ))
                status_label.value = "¡Descarga completada!"
                status_label.color = "green"
        except Exception as e:
            status_label.value = f"Error: Revisa el link o FFmpeg"
            status_label.color = "red"
            print(f"Error detallado: {e}")
        
        progress_bar.value = 0
        page.update()

    def on_click_download(e):
        if not url_input.value:
            url_input.error_text = "Ingresa un link"
            page.update()
            return
        
        url_input.error_text = None
        status_label.value = "Iniciando..."
        status_label.color = ft.Colors.GREY_400
        page.update()
        
        threading.Thread(
            target=run_download, 
            args=(url_input.value, quality_radio.value), 
            daemon=True
        ).start()

    # --- DISEÑO ---
    footer = ft.Column([
        ft.Divider(color=ft.Colors.GREY_800),
        ft.Text("Desarrollado por Yohander Sanchez", size=10, color=ft.Colors.GREY_600),
        ft.Text("© 2026 VDSoft v3.8 | Premium Mode", size=9, color=ft.Colors.GREY_700),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.add(
        ft.Column([
            title,
            ft.VerticalDivider(height=10, color="transparent"),
            url_input,
            quality_radio,
            progress_bar,
            status_label,
            ft.ElevatedButton(
                "DESCARGAR AHORA", 
                icon=ft.Icons.DOWNLOAD, 
                on_click=on_click_download,
                width=350,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800, color=ft.Colors.WHITE)
            ),
            ft.Container(
                content=history_list,
                height=150,
                bgcolor="#222222",
                border_radius=10,
                padding=10
            ),
            footer
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ADAPTIVE)
    )

if __name__ == "__main__":
    # Importante para Flet: assets_dir permite cargar el icon.png
    ft.app(target=main, assets_dir="assets")