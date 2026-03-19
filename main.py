import flet as ft
import os
import threading
import yt_dlp
import time

class MyLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"Error: {msg}")

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE PÁGINA ---
    page.title = "VDSoft v4.7 Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = ft.padding.only(top=60, left=20, right=20, bottom=20)
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    is_android = os.path.exists("/system/bin/app_process")

    # --- CONTROLES UI ---
    url_input = ft.TextField(
        label="Enlace (YouTube, TikTok, FB, Pinterest)", 
        border_color="#00B0FF",
        expand=True,
        text_size=14,
        hint_text="Pega el link aquí..."
    )

    # Pegar corregido para máxima compatibilidad
    def paste_link(e):
        clipboard_data = page.get_clipboard()
        if clipboard_data:
            url_input.value = clipboard_data
            page.update()
        else:
            # Si el método normal falla, intentamos el asíncrono silencioso
            async def get_async():
                val = await page.get_clipboard_async()
                if val: 
                    url_input.value = val
                    page.update()
            import asyncio
            threading.Thread(target=lambda: asyncio.run(get_async()), daemon=True).start()

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

    # --- LÓGICA DE LIMPIEZA ---
    def auto_clean():
        time.sleep(4)
        url_input.value = ""
        progress_bar.value = 0
        status_label.value = "Listo para el siguiente"
        status_label.color = "grey"
        page.update()

    # --- MOTOR DE DESCARGA MEJORADO (PINTEREST FIX) ---
    def run_download(url, quality):
        save_path = "/storage/emulated/0/Download/VDSoft" if is_android else "Descargas_VDSoft"
        if not os.path.exists(save_path):
            try: os.makedirs(save_path, exist_ok=True)
            except: save_path = "./"

        ydl_opts = {
            'format': 'best' if quality == "720" else 'bestaudio/best',
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'logger': MyLogger(),
            'noplaylist': True,
            # User Agent específico para evitar el bloqueo de Pinterest y FB
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
            'progress_hooks': [lambda d: progress_update(d)],
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
                status_label.value = "Conectando..."
                page.update()
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Video Social')
                
                history_list.controls.insert(0, ft.ListTile(
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color="#00E5FF"),
                    title=ft.Text(title[:25]+"...", size=12, color="white")
                ))
                status_label.value = "¡Descarga completada!"
                status_label.color = "#00E5FF"
                page.update()
                threading.Thread(target=auto_clean, daemon=True).start()

        except Exception as e:
            status_label.value = "Error: Enlace protegido o inválido"
            status_label.color = "red"
            page.update()

    def start_download(e):
        if url_input.value:
            status_label.value = "Analizando..."
            page.update()
            threading.Thread(target=run_download, args=(url_input.value, quality_dropdown.value), daemon=True).start()

    # --- PAYPAL MEJORADO ---
    def go_paypal(e):
        # Enlace de transferencia directa (Más efectivo que el de donación en móviles)
        page.launch_url("https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=smithsanchez2807@gmail.com&item_name=Apoyo+VDSoft+Pro&currency_code=USD")

    # --- DISEÑO ---
    page.add(
        ft.Column([
            ft.Text("VDSoft Pro v4.7", size=32, weight="bold", color="#00B0FF"),
            ft.Text("YouTube • TikTok • FB • Pinterest", size=12, color="grey"),
            ft.Container(height=15),
            ft.Row([url_input, btn_paste], alignment="center"),
            quality_dropdown,
            ft.Container(height=10),
            progress_bar,
            status_label,
            ft.ElevatedButton(
                "DESCARGAR", 
                width=380, height=50, 
                on_click=start_download,
                style=ft.ButtonStyle(bgcolor="#00B0FF", color="white")
            ),
            ft.Divider(height=30, color="#222222"),
            ft.Text("Historial:", size=16, weight="bold"),
            ft.Container(content=history_list, bgcolor="#1e1e1e", border_radius=10, padding=10),
            ft.Container(height=10),
            ft.ElevatedButton(
                "Apoyar proyecto (PayPal)", 
                icon=ft.Icons.FAVORITE, 
                on_click=go_paypal,
                style=ft.ButtonStyle(bgcolor="#003087", color="white")
            ),
            ft.Text("© 2026 Desarrollado por Yohander Sanchez", size=10, color="grey")
        ], horizontal_alignment="center")
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")