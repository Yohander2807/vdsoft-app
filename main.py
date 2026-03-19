import flet as ft
import os
import threading
import yt_dlp
import time
import asyncio

# Logger para evitar saturación de consola en Android
class MyLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"Error: {msg}")

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE LA PÁGINA ---
    page.title = "VDSoft v4.6 Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # Padding superior para evitar choque con la barra de tareas
    page.padding = ft.padding.only(top=60, left=20, right=20, bottom=20)

    is_android = os.path.exists("/system/bin/app_process")

    # --- CONTROLES DE INTERFAZ ---
    url_input = ft.TextField(
        label="Enlace (YouTube, TikTok, FB, Pinterest)", 
        border_color="#00B0FF",
        expand=True,
        text_size=14,
        hint_text="Pega el link aquí..."
    )

    # Función de pegar corregida (Asíncrona para Android)
    async def paste_link(e):
        try:
            value = await page.get_clipboard_async()
            if value:
                url_input.value = value
                page.update()
        except Exception:
            status_label.value = "Error al acceder al portapapeles"
            page.update()

    btn_paste = ft.IconButton(
        icon=ft.Icons.PASTE_ROUNDED, 
        icon_color="#00B0FF", 
        on_click=paste_link
    )

    quality_dropdown = ft.Dropdown(
        label="Formato",
        width=380,
        options=[
            ft.dropdown.Option("720", "Video (MP4)"),
            ft.dropdown.Option("mp3", "Audio (Webm/MP3)"),
        ],
        value="720"
    )

    progress_bar = ft.ProgressBar(value=0, color="#00B0FF", width=380)
    status_label = ft.Text("Listo", color="grey", size=12)
    history_list = ft.ListView(expand=True, spacing=10, height=150)

    # --- LÓGICA DE LIMPIEZA AUTOMÁTICA ---
    def clean_ui():
        time.sleep(4) # Tiempo para que el usuario vea el mensaje de éxito
        url_input.value = ""
        progress_bar.value = 0
        status_label.value = "Listo para el siguiente enlace"
        status_label.color = "grey"
        page.update()

    # --- LÓGICA DE DESCARGA MULTISOCIAL ---
    def run_download(url, quality):
        # Ruta de guardado estándar en Android
        save_path = "/storage/emulated/0/Download/VDSoft" if is_android else "Descargas_VDSoft"
        if not os.access(os.path.dirname(save_path), os.W_OK):
            save_path = "./" # Fallback a carpeta local si no hay permisos

        if not os.path.exists(save_path):
            try: os.makedirs(save_path, exist_ok=True)
            except: pass

        ydl_opts = {
            'format': 'best' if quality == "720" else 'bestaudio/best',
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'progress_hooks': [lambda d: progress_update(d)],
            'logger': MyLogger(),
            'noplaylist': True,
            # User Agent para evitar bloqueos de red social
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        def progress_update(d):
            if d['status'] == 'downloading':
                try:
                    p = d.get('_percent_str', '0%').replace('%','').strip()
                    progress_bar.value = float(p) / 100
                    status_label.value = f"Descargando... {p}%"
                    page.update()
                except: pass

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                status_label.value = "Analizando enlace..."
                page.update()
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Multimedia')
                
                # Agregar al historial
                history_list.controls.insert(0, ft.ListTile(
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color="#00E5FF"),
                    title=ft.Text(title[:25]+"...", size=12, color="white")
                ))
                status_label.value = "¡Descarga completada!"
                status_label.color = "#00E5FF"
                page.update()
                
                # Disparar limpieza de interfaz
                threading.Thread(target=clean_ui, daemon=True).start()

        except Exception:
            status_label.value = "Error: Enlace no compatible o privado"
            status_label.color = "red"
            page.update()

    def start_download(e):
        if url_input.value:
            status_label.value = "Iniciando proceso..."
            status_label.color = "grey"
            page.update()
            threading.Thread(target=run_download, args=(url_input.value, quality_dropdown.value), daemon=True).start()

    # --- BOTÓN DE PAYPAL (FORMATO DONACIÓN) ---
    def go_paypal(e):
        page.launch_url("https://www.paypal.com/donate/?business=smithsanchez2807@gmail.com&no_recurring=0&currency_code=USD")

    # --- CONSTRUCCIÓN DE LA VISTA ---
    page.add(
        ft.Column([
            ft.Text("VDSoft Pro v4.6", size=32, weight="bold", color="#00B0FF"),
            ft.Text("YouTube • TikTok • FB • Pinterest", size=12, color="grey"),
            ft.Container(height=15),
            ft.Row([url_input, btn_paste], alignment="center"),
            quality_dropdown,
            ft.Container(height=10),
            progress_bar,
            status_label,
            ft.ElevatedButton(
                "DESCARGAR", 
                width=380, 
                height=50, 
                on_click=start_download,
                style=ft.ButtonStyle(bgcolor="#00B0FF", color="white")
            ),
            ft.Divider(height=30, color="#222222"),
            ft.Text("Historial:", size=16, weight="bold"),
            ft.Container(content=history_list, bgcolor="#1e1e1e", border_radius=10, padding=10),
            ft.Container(height=10),
            ft.ElevatedButton(
                "Donar al Proyecto (PayPal)", 
                icon=ft.Icons.FAVORITE, 
                on_click=go_paypal,
                style=ft.ButtonStyle(bgcolor="#003087", color="white")
            ),
            ft.Text("© 2026 Desarrollado por Yohander Sanchez", size=10, color="grey")
        ], horizontal_alignment="center")
    )

if __name__ == "__main__":
    # Importante: Asegúrate de tener la carpeta /assets con icon.png
    ft.app(target=main, assets_dir="assets")