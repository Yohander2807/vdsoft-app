import flet as ft
import os
import yt_dlp
import re
import threading
import time

class MyLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"Error: {msg}")

def main(page: ft.Page):
    # Configuración de inicio (Síncrona para evitar pantalla negra)
    page.title = "VDSoft v5.2.2"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = ft.padding.only(top=60, left=20, right=20, bottom=20)
    page.bgcolor = "#121212"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    is_android = os.path.exists("/system/bin/app_process")
    default_path = "/storage/emulated/0/Download/VDSoft" if is_android else "Descargas_VDSoft"
    
    if not os.path.exists(default_path):
        try: os.makedirs(default_path, exist_ok=True)
        except: default_path = "./"

    search_results = ft.Column(spacing=15, horizontal_alignment="center")
    history_list = ft.ListView(expand=True, spacing=10)
    
    # --- PROGRESO ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                p_raw = d.get('_percent_str', '0%')
                p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_raw).replace('%', '').strip()
                progress_bar.value = float(p_clean) / 100
                status_label.value = f"Descargando: {p_clean}%"
                page.update()
            except: pass

    # --- LÓGICA DE DESCARGA (THREADING) ---
    def run_dl_thread(url, title, quality):
        ydl_opts = {
            'outtmpl': f'{path_input.value}/%(title)s.%(ext)s',
            'logger': MyLogger(),
            'progress_hooks': [progress_hook],
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
        }
        
        if quality == "mp3":
            ydl_opts.update({'format': 'bestaudio/best'})
        else:
            ydl_opts.update({'format': 'bestvideo[height<=720]+bestaudio/best/best', 'merge_output_format': 'mp4'})

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            status_label.value = "¡Éxito! Limpiando..."
            status_label.color = "blue400"
            history_list.controls.insert(0, ft.ListTile(title=ft.Text(title[:30], size=12), leading=ft.Icon(ft.Icons.DONE, color="blue400")))
            page.update()
            time.sleep(3)
            url_input.value = ""
            progress_bar.value = 0
            status_label.value = "Listo"
        except:
            status_label.value = "Error en descarga"
        page.update()

    # --- BÚSQUEDA ---
    def start_search(e):
        query = url_input.value.strip()
        if not query: return
        search_results.controls.clear()
        status_label.value = "Buscando..."
        page.update()

        def fetch():
            opts = {'quiet': True, 'nocheckcertificate': True}
            target = query if query.startswith("http") else f"ytsearch6:{query}"
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(target, download=False)
                    entries = info.get('entries', [info])
                    for item in entries:
                        if not item: continue
                        v_url = item.get('webpage_url') or item.get('url')
                        v_title = item.get('title', 'Video')
                        v_thumb = item.get('thumbnail', '')
                        
                        search_results.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Image(src=v_thumb, height=150, border_radius=10),
                                    ft.Text(v_title[:40], size=12, weight="bold"),
                                    ft.FilledButton("BAJAR", on_click=lambda _, u=v_url, t=v_title: threading.Thread(target=run_dl_thread, args=(u,t,quality_radio.value), daemon=True).start())
                                ], horizontal_alignment="center"),
                                bgcolor="#1e1e1e", padding=10, border_radius=15
                            )
                        )
                status_label.value = "Resultados OK"
            except: status_label.value = "Error de red"
            page.update()
        
        threading.Thread(target=fetch, daemon=True).start()

    # --- COMPONENTES ---
    url_input = ft.TextField(label="Link o Nombre", border_radius=15, on_submit=start_search)
    path_input = ft.TextField(label="Ruta", value=default_path, text_size=10)
    quality_radio = ft.RadioGroup(content=ft.Row([ft.Radio(value="720", label="MP4"), ft.Radio(value="mp3", label="MP3")], alignment="center"), value="720")
    progress_bar = ft.ProgressBar(value=0, color="blue400", width=300)
    status_label = ft.Text("Listo", size=12, color="grey")

    # --- NAVEGACIÓN ---
    def change_view(e):
        vista_buscador.visible = (e.control.data == "explorar")
        vista_historial.visible = not vista_buscador.visible
        btn_explorar.style = style_active if vista_buscador.visible else style_inactive
        btn_historial.style = style_active if not vista_buscador.visible else style_inactive
        page.update()

    style_active, style_inactive = ft.ButtonStyle(bgcolor="blue800"), ft.ButtonStyle(bgcolor="white10")
    btn_explorar = ft.FilledButton("EXPLORAR", on_click=change_view, data="explorar", style=style_active, expand=True)
    btn_historial = ft.FilledButton("HISTORIAL", on_click=change_view, data="historial", style=style_inactive, expand=True)

    vista_buscador = ft.Column([url_input, ft.FilledButton("BUSCAR", on_click=start_search), quality_radio, progress_bar, status_label, ft.Column([search_results], scroll="auto", expand=True)], expand=True, horizontal_alignment="center")
    vista_historial = ft.Column([ft.Text("HISTORIAL"), history_list], expand=True, visible=False)

    # PAYPAL FIX FINAL
    def open_paypal(e):
        page.launch_url("https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=smithsanchez2807@gmail.com&currency_code=USD")

    page.add(
        ft.Row([ft.Icon(ft.Icons.DOWNLOAD), ft.Text("VDSoft", size=24, weight="bold")], alignment="center"),
        ft.Row([btn_explorar, btn_historial]),
        ft.Container(content=ft.Column([vista_buscador, vista_historial]), expand=True),
        ft.Container(bgcolor="#1a1a1a", padding=10, border_radius=15, content=ft.Column([ft.Text("Yohander Sanchez", size=10), ft.TextButton("PayPal", on_click=open_paypal)], horizontal_alignment="center"))
    )

if __name__ == "__main__":
    ft.app(target=main)