import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import zipfile
import io
import time
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Ahora Entiendo - TikTok Downloader", page_icon="🎬")

st.title("🎬 TikTok Bulk Downloader")
st.markdown("### Herramienta para el equipo de Ahora Entiendo")
st.info("Pega los enlaces de TikTok (uno por línea) para descargarlos sin marca de agua.")

# Área de texto para los links
links_raw = st.text_area("Enlaces de TikTok:", height=200, placeholder="https://www.tiktok.com/@usuario/video/..." )

def get_download_link(url):
    """Obtiene el link de descarga sin marca de agua usando ssstik.io"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }
    try:
        sesion = requests.Session()
        sesion.get("https://ssstik.io/es", headers=headers, timeout=10 )
        api_url = "https://ssstik.io/abc?url=dl"
        data = {'id': url, 'locale': 'es', 'tt': '0'}
        response = sesion.post(api_url, headers=headers, data=data, timeout=15 )
        
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            text = link.text.lower()
            if 'sin marca de agua' in text or 'without watermark' in text:
                return link['href']
        return None
    except:
        return None

if st.button("🚀 Procesar y Descargar ZIP", type="primary"):
    links = [link.strip() for link in links_raw.split('\n') if link.strip()]
    
    if not links:
        st.warning("⚠️ Por favor, ingresa al menos un enlace.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        downloaded_files = []
        
        # Crear un buffer en memoria para el archivo ZIP
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for i, url in enumerate(links):
                status_text.text(f"Procesando video {i+1} de {len(links)}...")
                video_url = get_download_link(url)
                
                if video_url:
                    try:
                        video_data = requests.get(video_url, timeout=20).content
                        video_id = re.search(r'/video/(\d+)', url)
                        id_str = video_id.group(1) if video_id else f"video_{int(time.time())}_{i}"
                        filename = f"tiktok_{id_str}.mp4"
                        
                        # Escribir directamente al ZIP en memoria
                        zip_file.writestr(filename, video_data)
                        downloaded_files.append(filename)
                    except Exception as e:
                        st.error(f"Error al descargar {url}: {e}")
                
                progress_bar.progress((i + 1) / len(links))
                time.sleep(1) # Pausa para evitar bloqueos

        if downloaded_files:
            status_text.success(f"✅ ¡Listo! Se procesaron {len(downloaded_files)} videos.")
            
            # Botón para descargar el ZIP generado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📥 Descargar archivo ZIP",
                data=zip_buffer.getvalue(),
                file_name=f"TikToks_AhoraEntiendo_{timestamp}.zip",
                mime="application/zip"
            )
        else:
            status_text.error("❌ No se pudo descargar ningún video. Revisa los enlaces.")

st.markdown("---")
st.caption("Desarrollado para el equipo de Ahora Entiendo.")
