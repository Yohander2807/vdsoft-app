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
    page.title = "VDSoft v4.2 Pro - Multisocial"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = "#121212"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    is_android = os.path.exists("/system/bin/app_process")

    # --- UI CONTROLS ---
    url_input = ft.TextField(
        label="Pegue el enlace (YouTube, TikTok, FB)", 
        border_color="#00B0FF",
        width=380,
        hint_text="https://..."
    )

    quality_dropdown = ft.Dropdown(
        label="Calidad de descarga",
        width=380,
        options=[
            ft.dropdown.Option("720", "Video (MP4 - Compatible)"),
            ft.dropdown.Option("mp3", "Audio (Formato Original)"),
        ],
        value="720"
    )

    progress_bar = ft.ProgressBar(value=0, color="#00B0FF", width=380)
    status_label = ft.Text("Estado: Esperando enlace...", color="grey")
    history_list = ft.ListView(expand=True, spacing=10, height=180)

    # --- LÓGICA DE DESCARGA ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','').strip()
                progress_bar.value = float(p) / 100
                status_label.value = f"Bajando contenido... {p}%"
                page.update()
            except: pass

    def run_download(url, quality):
        save_path = "/storage/emulated/0/Download/VDSoft" if is_android else "Descargas_VDSoft"
        if not os.path.exists(save_path):
            try: os.makedirs(save_path, exist_ok=True)
            except: save_path = "./"

        # Configuración optimizada para múltiples redes sociales
        ydl_opts = {
            'format': 'best' if quality == "720" else 'bestaudio/best',
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'logger': MyLogger(),
            'noplaylist': True,
            'ignoreerrors': True,
            # User Agent actualizado para evitar bloqueos en FB/TikTok
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                status_label.value = "Analizando enlace social..."
                page.update()
                # Esta función extrae y descarga de casi cualquier sitio soportado por yt-dlp
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Contenido Multimedia')
                
                history_list.controls.insert(0, ft.ListTile(
                    leading=ft.Icon(ft.Icons.DONE_ALL, color="cyan"),
                    title=ft.Text(title[:30] + "...", size=12),
                    subtitle=ft.Text(f"Red Social Detectada", size=10)
                ))
                status_label.value = "¡Descarga Exitosa!"
                status_label.color = "cyan"
        except Exception as e:
            status_label.value = "Error: El enlace no es compatible o es privado."
            status_label.color = "red"
        
        progress_bar.value = 0
        page.update()

    def start_click(e):
        if not url_input.value:
            url_input.error_text = "Ingresa un enlace"
            page.update()
            return
        status_label.value = "Conectando..."
        page.update()
        threading.Thread(target=run_download, args=(url_input.value, quality_dropdown.value), daemon=True).start()

    # --- DONACIONES (PAYPAL FIX) ---
    def open_paypal(e):
        # Usamos una URL de PayPal directa y limpia
        page.launch_url("https://www.paypal.com/paypalme/smithsanchez2807")

    # --- DISEÑO ---
    page.add(
        ft.Column([
            ft.Text("VDSoft Pro v4.2", size=30, weight="bold", color="#00B0FF"),
            ft.Row([
                ft.Icon(ft.Icons.PLAY_CIRCLE_FILL, color="red", size=20),
                ft.Icon(ft.Icons.FACEBOOK, color="blue", size=20),
                ft.Icon(ft.Icons.MUSIC_NOTE, color="white", size=20),
                ft.Text("YouTube | Facebook | TikTok", size=12, color="grey"),
            ], alignment="center"),
            ft.Divider(height=10, color="transparent"),
            url_input,
            quality_dropdown,
            ft.Container(height=10),
            progress_bar,
            status_label,
            ft.ElevatedButton(
                "DESCARGAR AHORA", 
                width=380, 
                height=50, 
                on_click=start_click,
                style=ft.ButtonStyle(bgcolor="#00B0FF", color="white")
            ),
            ft.Divider(height=20),
            ft.Text("Historial de Descargas:", size=16, weight="bold"),
            ft.Container(content=history_list, bgcolor="#1e1e1e", border_radius=10, padding=10),
            ft.Container(height=10),
            # Botón de PayPal resaltado
            ft.Container(
                content=ft.ElevatedButton(
                    "Apoyar el Proyecto (PayPal)", 
                    icon=ft.Icons.FAVORITE, 
                    on_click=open_paypal,
                    style=ft.ButtonStyle(color="white", bgcolor="#003087")
                ),
                alignment=ft.alignment.center
            ),
            ft.Text("© 2026 Desarrollado por Yohander Sanchez", size=10, color="grey")
        ], horizontal_alignment="center")
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")