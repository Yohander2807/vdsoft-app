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
    # --- CONFIGURACIÓN DE PÁGINA ---
    page.title = "Video Downloader - VDSoft"
    page.window.width = 450
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = "#1a1a1a"
    
    # Icono de la ventana/app (debe estar en la carpeta /assets)
    page.icon = "icon.png" 
    
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    downloaded_files = set()

    # --- DETECCIÓN DE RUTAS ---
    if getattr(sys, 'frozen', False):
        curr_dir = os.path.dirname(sys.executable)
    else:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
    
    ffmpeg_path = os.path.join(curr_dir, "ffmpeg.exe")

    # --- UI CONTROLS ---
    title = ft.Text(
        "Video Downloader", 
        size=32, 
        color=ft.Colors.BLUE_400, 
        weight=ft.FontWeight.BOLD
    )

    url_input = ft.TextField(
        label="Pegue el enlace aquí",
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_600,
        width=380
    )

    quality_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="1080", label="1080p"),
            ft.Radio(value="720", label="720p"),
            ft.Radio(value="mp3", label="MP3"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="720"
    )

    progress_bar = ft.ProgressBar(value=0, color=ft.Colors.BLUE_400, height=10, width=380)
    status_label = ft.Text("Listo", color=ft.Colors.GREY_400, italic=True)
    
    history_list = ft.ListView(expand=True, spacing=5)

    # --- LÓGICA DE DESCARGA ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            p_raw = d.get('_percent_str', '0%')
            p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_raw).replace('%', '').strip()
            try:
                p_float = float(p_clean) / 100
                progress_bar.value = 0.99 if p_float >= 1.0 else p_float
                status_label.value = f"Bajando... {int(p_float*100)}%"
                page.update()
            except: pass
        elif d['status'] == 'finished':
            progress_bar.value = 1.0
            status_label.value = "Finalizando (FFmpeg)..."
            page.update()

    def run_download(url, quality):
        folder = "Descargas_SOPSoft"
        if not os.path.exists(folder): os.makedirs(folder)

        f_str = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best" if quality == "1080" else \
                "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best" if quality == "720" else \
                "bestaudio/best"

        opts = {
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'format': f_str,
            'progress_hooks': [progress_hook],
            'logger': MyLogger(),
            'prefer_ffmpeg': True,
            'merge_output_format': 'mp4',
            'ffmpeg_location': ffmpeg_path,
            'user_agent': 'Mozilla/5.0'
        }

        if quality == "mp3":
            opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = info.get('title', 'Video')
                if filename not in downloaded_files:
                    downloaded_files.add(filename)
                    # CORRECCIÓN: ft.icons en minúscula
                    history_list.controls.insert(0, ft.ListTile(
                        leading=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN),
                        title=ft.Text(filename, size=12, max_lines=1),
                    ))
                status_label.value = "¡Guardado con éxito!"
                page.update()
                time.sleep(2)
                progress_bar.value = 0
                status_label.value = "Listo"
                page.update()
        except Exception as e:
            print(f"Error: {e}")
            status_label.value = "Error: FFmpeg o Link inválido."
            progress_bar.value = 0
            page.update()

    def iniciar_proceso(e):
        if url_input.value:
            status_label.value = "Conectando..."
            page.update()
            threading.Thread(target=run_download, args=(url_input.value, quality_radio.value), daemon=True).start()

    # --- COMPONENTE FOOTER ---
    footer = ft.Container(
        content=ft.Column([
            ft.Divider(height=1, color=ft.Colors.GREY_800),
            ft.Row([
                # CORRECCIÓN: ft.icons en minúscula
                ft.Icon(ft.Icons.CODE, size=14, color=ft.Colors.BLUE_400),
                ft.Text("Desarrollado por Yohander Sanchez", size=12, weight=ft.FontWeight.W_300),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Text("© 2026 VDSoft v3.7 | Software Pro", size=10, color=ft.Colors.GREY_600)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
        margin=ft.Margin(0, 20, 0, 0)
    )

    # --- CUERPO PRINCIPAL ---
    body = ft.Container(
        content=ft.Column([
            ft.Container(title, margin=ft.Margin(0, 0, 0, 10)),
            url_input,
            ft.Text("Calidad:", size=14, color=ft.Colors.GREY_300),
            quality_radio,
            progress_bar,
            status_label,
            ft.FilledButton("DESCARGAR", width=380, height=50, on_click=iniciar_proceso),
            ft.Text("Historial:", size=12, color=ft.Colors.GREY_500),
            ft.Container(content=history_list, bgcolor="#252525", border_radius=10, expand=True, padding=10),
            footer 
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
        expand=True
    )

    page.add(body)

if __name__ == "__main__":
    # IMPORTANTE: Definir assets_dir para cargar el icon.png
    ft.run(main, assets_dir="assets")