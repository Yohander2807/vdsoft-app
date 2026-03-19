import flet as ft
import os
import threading
import yt_dlp
import re
import sys
import time

def main(page: ft.Page):
    # --- CONFIGURACIÓN ---
    page.title = "VDSoft v3.9"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = "#1a1a1a"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    is_android = os.path.exists("/system/bin/app_process")

    # --- CONTROLES UI ---
    title = ft.Text("VDSoft Downloader", size=28, color=ft.Colors.BLUE_400, weight=ft.FontWeight.BOLD)
    url_input = ft.TextField(label="Pegue el enlace de YouTube", width=350)
    quality_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="720", label="720p"),
            ft.Radio(value="mp3", label="MP3"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="720"
    )
    progress_bar = ft.ProgressBar(value=0, color=ft.Colors.BLUE_400, width=350)
    status_label = ft.Text("Listo", color=ft.Colors.GREY_400)

    def get_save_path():
        if is_android:
            # Intentamos la carpeta pública, si no, la privada de la app
            path = "/storage/emulated/0/Download"
            return path if os.access(path, os.W_OK) else "./"
        return "Descargas_VDSoft"

    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                progress_bar.value = float(p) / 100
                status_label.value = f"Descargando... {p}%"
                page.update()
            except: pass

    def run_download(url, quality):
        folder = get_save_path()
        
        # LOGICA DE COMPATIBILIDAD:
        # Si es MP3 o 1080p, yt-dlp NECESITA FFmpeg. 
        # Si estamos en Android y no tenemos FFmpeg, bajamos el 'best' (normalmente 720p)
        # que viene ya unido para evitar el error.
        
        opts = {
            'progress_hooks': [progress_hook],
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'noplaylist': True,
        }

        if quality == "mp3":
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            # 'best' descarga el video con audio ya integrado (máximo 720p generalmente)
            # Esto NO requiere FFmpeg, por lo que NO dará error en el celular.
            opts['format'] = 'best' 

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
                status_label.value = "¡Completado! Revisa tu carpeta Download"
                status_label.color = "green"
        except Exception as e:
            status_label.value = "Error: Intenta con otro link"
            status_label.color = "red"
            print(f"Error: {e}")
        
        progress_bar.value = 0
        page.update()

    def on_click(e):
        if url_input.value:
            status_label.value = "Iniciando..."
            page.update()
            threading.Thread(target=run_download, args=(url_input.value, quality_radio.value), daemon=True).start()

    page.add(
        title, url_input, quality_radio, progress_bar, status_label,
        ft.ElevatedButton("DESCARGAR", on_click=on_click, width=350),
        ft.Text("© 2026 VDSoft | Yohander Sanchez", size=10, color="grey")
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")