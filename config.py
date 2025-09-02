# config.py
"""
Arquivo de configuração central para o projeto.
Armazena todas as variáveis que podem mudar, como URLs, IDs e caminhos.
"""

# --- CONFIGURAÇÕES DO GOOGLE DRIVE ---
# Escopos de permissão para a API do Google Drive.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
# ID da pasta no Google Drive para onde as imagens serão enviadas.
# IMPORTANTE: Extraia apenas o ID da URL.
# Ex: .../folders/1JRkkyA6Oy-3TN2CHkEdrOS0MI0BUxmmT -> O ID é a parte final.
DRIVE_FOLDER_ID = "1JRkkyA6Oy-3TN2CHkEdrOS0MI0BUxmmT"

# --- CONFIGURAÇÕES DO WEB SCRAPER ---
# URL do mapa de câmeras a ser raspado.
URL_MAPA_CAMERAS = "https://cameras.praiagrande.sp.gov.br/aovivo/"
# Caminho para o executável do ChromeDriver.
CHROME_DRIVER_PATH = "D:\\Downloads\\chromedriver.exe"
# Pasta local onde as imagens serão salvas temporariamente antes do upload.
PASTA_IMAGENS_LOCAIS = r"D:\TCC\raspagem de dados\imagens_cameras_mapa"

# --- CONFIGURAÇÕES DO CICLO DE EXECUÇÃO ---
# Tempo de espera em segundos entre cada ciclo completo de captura.
# 60 segundos = 1 minuto.
TEMPO_ESPERA_CICLO_SEGUNDOS = 60