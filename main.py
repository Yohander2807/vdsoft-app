import flet as ft
import os
import yt_dlp
import re
import asyncio

class MyLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

async def main(page: ft.Page):
    page.title = "VDSoft v5.2.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = "#121212"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    default_path = os.path.join(os.path.expanduser("~"), "Downloads", "VDSoft_Downloads")
    if not os.path.exists(default_path):
        os.makedirs(default_path)

    search_results = ft.Column(spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    history_list = ft.ListView(expand=True, spacing=10)
    
    # --- PROGRESO ASÍNCRONO ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                p_raw = d.get('_percent_str', '0%')
                p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_raw).replace('%', '').strip()
                progress_bar.value = float(p_clean) / 100
                status_label.value = f"Descargando: {p_clean}%"
                page.update()
            except: pass

    # --- DESCARGA ASÍNCRONA ---
    async def download_media(url, title, quality):
        status_label.value = "Iniciando..."
        progress_bar.value = None
        page.update()
        
        ydl_opts = {
            'outtmpl': f'{path_input.value}/%(title)s.%(ext)s',
            'logger': MyLogger(),
            'progress_hooks': [progress_hook],
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        if quality == "mp3":
            ydl_opts.update({'format': 'bestaudio/best','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]})
        else:
            ydl_opts.update({'format': f'bestvideo[height<={quality}]+bestaudio/best/best','merge_output_format': 'mp4'})

        # Ejecutamos la descarga pesada sin bloquear la interfaz
        def run_dl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        try:
            await asyncio.to_thread(run_dl)
            status_label.value = "¡Guardado con éxito!"
            progress_bar.value = 0
            history_list.controls.insert(0, ft.Container(
                content=ft.ListTile(
                    title=ft.Text(title[:35], size=12, weight="bold"),
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color="blue400"),
                ),
                bgcolor="#1e1e1e", border_radius=10
            ))
            page.update()
        except:
            status_label.value = "Finalizado."
            page.update()

    # --- BÚSQUEDA ASÍNCRONA ---
    async def start_search(e):
        query = url_input.value.strip()
        if not query: return
        
        search_results.controls.clear()
        status_label.value = "Buscando..."
        page.update()
        
        def fetch_data():
            opts = {'quiet': True, 'nocheckcertificate': True, 'no_warnings': True}
            target = query if query.startswith("http") else f"ytsearch6:{query}"
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(target, download=False)

        try:
            info = await asyncio.to_thread(fetch_data)
            if info:
                entries = info.get('entries', [info])
                for item in entries:
                    if not item: continue
                    v_url = item.get('webpage_url') or item.get('url')
                    v_title = item.get('title', 'Video')
                    v_thumb = item.get('thumbnail') or ""
                    
                    search_results.controls.append(
                        ft.Container(
                            width=350,
                            content=ft.Column([
                                ft.Image(src=v_thumb, height=180, fit="cover", border_radius=15),
                                ft.Text(v_title[:50], size=13, weight="bold", text_align="center"),
                                ft.FilledButton(
                                    "DESCARGAR", width=250,
                                    on_click=lambda _, u=v_url, t=v_title: asyncio.create_task(download_media(u, t, quality_radio.value))
                                )
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                            bgcolor="#1e1e1e", padding=15, border_radius=20
                        )
                    )
                status_label.value = "Resultados listos"
            else:
                status_label.value = "Sin resultados"
        except:
            status_label.value = "Error en búsqueda"
        
        page.update()

    # --- ELEMENTOS UI ---
    url_input = ft.TextField(label="Nombre o Link", text_align="center", border_radius=15, on_submit=start_search)
    path_input = ft.TextField(label="Ruta", value=default_path, text_size=11, text_align="center")
    quality_radio = ft.RadioGroup(
        content=ft.Row([ft.Radio(value="720", label="720p"), ft.Radio(value="mp3", label="MP3")], alignment="center"), 
        value="720"
    )
    progress_bar = ft.ProgressBar(value=0, color="blue400", width=300)
    status_label = ft.Text("Esperando...", size=12, color="grey")

    async def change_view(e):
        is_explorar = e.control.data == "explorar"
        vista_buscador.visible = is_explorar
        vista_historial.visible = not is_explorar
        btn_explorar.style = style_active if is_explorar else style_inactive
        btn_historial.style = style_active if not is_explorar else style_inactive
        page.update()

    style_active = ft.ButtonStyle(bgcolor="blue800", color="white")
    style_inactive = ft.ButtonStyle(bgcolor="black12", color="white60")
    btn_explorar = ft.FilledButton("EXPLORAR", on_click=change_view, data="explorar", style=style_active, expand=True)
    btn_historial = ft.FilledButton("HISTORIAL", on_click=change_view, data="historial", style=style_inactive, expand=True)

    vista_buscador = ft.Column([
        url_input,
        ft.FilledButton("BUSCAR", icon=ft.Icons.SEARCH, width=200, on_click=start_search),
        ft.ExpansionTile(title=ft.Text("Ruta de guardado", size=11), controls=[path_input]),
        quality_radio, progress_bar, status_label,
        ft.Column([search_results], scroll="auto", expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    vista_historial = ft.Column([
        ft.Text("MIS DESCARGAS", size=20, weight="bold", color="blue200"),
        history_list
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=False)

    async def open_paypal(e):
        await page.launch_url("https://www.paypal.me/smithsanchez2807")

    creador = ft.Container(
        padding=15, bgcolor="#1a1a1a", border_radius=20,
        content=ft.Column([
            ft.Text("Yohander Sanchez | SOPSoft", size=11, weight="bold", color="blue200"),
            ft.TextButton("Apoyar en PayPal", icon=ft.Icons.FAVORITE, on_click=open_paypal)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
    )

    page.add(
        ft.Row([ft.Icon(ft.Icons.DOWNLOAD_FOR_OFFLINE, color="blue400"), ft.Text("VDSoft", size=26, weight="bold")], alignment="center"),
        ft.Row([btn_explorar, btn_historial], spacing=10),
        ft.Container(content=ft.Column([vista_buscador, vista_historial]), expand=True),
        creador
    )

if __name__ == "__main__":
    ft.app(target=main)