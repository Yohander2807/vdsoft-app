import flet as ft
import os
import threading
import yt_dlp
import re

# Logger simple para no saturar la memoria
class MyLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"Error: {msg}")

def main(page: ft.Page):
    page.title = "VDSoft v4.3 Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    is_android = os.path.exists("/system/bin/app_process")

    # --- UI CONTROLS ---
    url_input = ft.TextField(
        label="Enlace (YouTube, TikTok, Facebook)", 
        border_color="#00B0FF",
        expand=True
    )

    # Botón para pegar del portapapeles
    def paste_link(e):
        # En Flet Android, esto lee el portapapeles del sistema
        url_input.value = page.get_clipboard()
        page.update()

    btn_paste = ft.IconButton(
        icon=ft.Icons.PASTE, 
        icon_color="#00B0FF", 
        on_click=paste_link,
        tooltip="Pegar enlace"
    )

    quality_dropdown = ft.Dropdown(
        label="Formato de descarga",
        width=380,
        options=[
            ft.dropdown.Option("720", "Video (MP4)"),
            ft.dropdown.Option("mp3", "Audio (Original)"),
        ],
        value="720"
    )

    progress_bar = ft.ProgressBar(value=0, color="#00B0FF", width=380)
    status_label = ft.Text("Listo para descargar", color="grey", size=12)
    history_list = ft.ListView(expand=True, spacing=10, height=150)

    # --- LÓGICA DE DESCARGA ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','').strip()
                progress_bar.value = float(p) / 100
                status_label.value = f"Bajando... {p}%"
                page.update()
            except: pass

    def run_download(url, quality):
        # Ruta segura para Android
        save_path = "/storage/emulated/0/Download/VDSoft" if is_android else "Descargas_VDSoft"
        if not os.path.exists(save_path):
            try: os.makedirs(save_path, exist_ok=True)
            except: save_path = "./"

        ydl_opts = {
            'format': 'best' if quality == "720" else 'bestaudio/best',
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'logger': MyLogger(),
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                status_label.value = "Conectando..."
                page.update()
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Video')
                
                history_list.controls.insert(0, ft.ListTile(
                    leading=ft.Icon(ft.Icons.DOWNLOAD_DONE, color="cyan"),
                    title=ft.Text(title[:25]+"...", size=12)
                ))
                status_label.value = "¡Descarga Exitosa!"
                status_label.color = "cyan"
        except Exception:
            status_label.value = "Error: Enlace no soportado"
            status_label.color = "red"
        
        progress_bar.value = 0
        page.update()

    def start_download(e):
        if url_input.value:
            status_label.value = "Iniciando..."
            page.update()
            threading.Thread(target=run_download, args=(url_input.value, quality_dropdown.value), daemon=True).start()

    # --- FOOTER Y DONACIONES ---
    def go_paypal(e):
        page.launch_url("https://www.paypal.me/smithsanchez2807")

    page.add(
        ft.Text("VDSoft Pro v4.3", size=32, weight="bold", color="#00B0FF"),
        ft.Row([url_input, btn_paste], alignment="center"),
        quality_dropdown,
        ft.Container(height=10),
        progress_bar,
        status_label,
        ft.ElevatedButton("DESCARGAR", width=380, height=50, on_click=start_download),
        ft.Divider(height=20),
        ft.Text("Historial:", size=16, weight="bold"),
        ft.Container(content=history_list, bgcolor="#1e1e1e", border_radius=10, padding=10),
        ft.ElevatedButton(
            "Donar al Proyecto (PayPal)", 
            icon=ft.Icons.FAVORITE, 
            on_click=go_paypal,
            style=ft.ButtonStyle(bgcolor="#003087", color="white")
        ),
        ft.Text("© 2026 Yohander Sanchez", size=10, color="grey")
    )

if __name__ == "__main__":
    # IMPORTANTE: Asegúrate de que el archivo icon.png esté en la carpeta /assets
    ft.app(target=main, assets_dir="assets")