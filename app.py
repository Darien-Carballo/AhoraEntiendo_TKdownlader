import streamlit as st
import yt_dlp
import zipfile
import io
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Ahora Entiendo - TikTok Downloader", page_icon="🎬")

st.title("🎬 TikTok Bulk Downloader")
st.markdown("### Herramienta Profesional para Ahora Entiendo")
st.info("Pega los enlaces de TikTok (uno por línea). Esta versión usa yt-dlp para máxima compatibilidad.")

links_raw = st.text_area("Enlaces de TikTok:", height=200, placeholder="https://www.tiktok.com/@usuario/video/..." )

def download_tiktok(url):
    """Descarga video de TikTok sin marca de agua usando yt-dlp"""
    # Configuración de yt-dlp para obtener el video sin marca de agua
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': 'temp_video.%(ext)s',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            with open(filename, 'rb') as f:
                video_data = f.read()
            
            # Limpiar archivo temporal
            if os.path.exists(filename):
                os.remove(filename)
                
            return video_data, f"tiktok_{info['id']}.mp4"
    except Exception as e:
        st.error(f"Error con {url}: {str(e)}")
        return None, None

if st.button("🚀 Procesar y Descargar ZIP", type="primary"):
    links = [link.strip() for link in links_raw.split('\n') if link.strip()]
    
    if not links:
        st.warning("⚠️ Por favor, ingresa al menos un enlace.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        downloaded_count = 0
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for i, url in enumerate(links):
                status_text.text(f"Descargando video {i+1} de {len(links)}...")
                video_data, filename = download_tiktok(url)
                
                if video_data:
                    zip_file.writestr(filename, video_data)
                    downloaded_count += 1
                
                progress_bar.progress((i + 1) / len(links))

        if downloaded_count > 0:
            status_text.success(f"✅ ¡Éxito! Se descargaron {downloaded_count} videos.")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📥 Descargar archivo ZIP",
                data=zip_buffer.getvalue(),
                file_name=f"TikToks_AE_{timestamp}.zip",
                mime="application/zip"
            )
        else:
            status_text.error("❌ No se pudo descargar ningún video. Verifica los enlaces.")

st.markdown("---")
st.caption("Desarrollado con yt-dlp para el equipo de Ahora Entiendo.")
