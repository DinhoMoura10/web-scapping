from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
import os
import time
import re
import datetime

# --- BIBLIOTECAS DO GOOGLE ---
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# --- CONFIGURAÇÕES DO GOOGLE DRIVE ---
# Se modificar esses escopos, exclua o arquivo token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
# ID da pasta no Google Drive para onde as imagens serão enviadas.
# Abra a pasta no Drive e copie o ID da URL.
# Ex: .../folders/ESTE_EH_O_ID
DRIVE_FOLDER_ID = "1JRkkyA6Oy-3TN2CHkEdrOS0MI0BUxmmT" # <-- CORREÇÃO APLICADA AQUI

def upload_to_drive(file_path):
    """Faz o upload de um arquivo para uma pasta específica no Google Drive."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret_671287945142-5mbrh2p2gj7iul8ulatb7aji5dr86j4s.apps.googleusercontent.com.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        file_metadata = {
            "name": os.path.basename(file_path),
            "parents": [DRIVE_FOLDER_ID] 
        }
        media = MediaFileUpload(file_path, mimetype='image/png')
        
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields="id"
        ).execute()
        
        print(f"Upload bem-sucedido! ID do arquivo no Drive: {file.get('id')}")

    except HttpError as error:
        print(f"Ocorreu um erro no upload: {error}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado no upload: {e}")

def sanitizar_nome_arquivo(nome):
    if nome.lower().startswith("câmera:"):
        nome = nome[7:].strip()
    return re.sub(r'[\\/*?:"<>|\s]', '_', nome)

def capturar_imagens_marcadores(url_do_mapa, pasta_destino):
    chrome_driver_path = "D:\\Downloads\\chromedriver.exe"
    service = Service(chrome_driver_path)

    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"Pasta '{pasta_destino}' criada.")

    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    try:
        print(f"Acessando o mapa: {url_do_mapa}")
        driver.get(url_do_mapa)
        wait = WebDriverWait(driver, 20)
        marcadores_selector = (By.CSS_SELECTOR, "img.leaflet-marker-icon")
        
        wait.until(EC.presence_of_element_located(marcadores_selector))
        num_marcadores = len(driver.find_elements(*marcadores_selector))
        print(f"Encontrados {num_marcadores} marcadores de câmera.")

        for i in range(num_marcadores):
            print(f"\n--- Processando Marcador {i + 1} de {num_marcadores} ---")
            try:
                marcadores = wait.until(EC.presence_of_all_elements_located(marcadores_selector))
                if i >= len(marcadores):
                    print("Índice do marcador fora do alcance. Pulando.")
                    continue
                
                marcador_atual = marcadores[i]
                driver.execute_script("arguments[0].click();", marcador_atual)
                print(f"Clicado no marcador {i + 1}.")

                try:
                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    print(f"AVISO: Câmera indisponível: '{alert.text}'")
                    alert.accept()
                    continue
                except TimeoutException:
                    pass

                camera_content_selector = (By.CSS_SELECTOR, "div.slideshowLightbox img")
                camera_image_element = wait.until(EC.visibility_of_element_located(camera_content_selector))
                time.sleep(2)

                nome_camera = "camera_desconhecida"
                try:
                    info_container = driver.find_element(By.CSS_SELECTOR, ".descLightbox")
                    nome_camera = sanitizar_nome_arquivo(info_container.text)
                except NoSuchElementException:
                    print("Nome da câmera não encontrado, usando nome padrão.")
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = os.path.join(pasta_destino, f"{nome_camera}_{timestamp}_{i+1}.png")
                
                camera_image_element.screenshot(nome_arquivo)
                print(f"Screenshot salvo localmente em '{nome_arquivo}'")

                # --- FAZ O UPLOAD DA IMAGEM PARA O GOOGLE DRIVE ---
                print("Iniciando upload para o Google Drive...")
                upload_to_drive(nome_arquivo)

            except Exception as e:
                print(f"Erro ao processar o marcador {i + 1}: {type(e).__name__}.")

            finally:
                if i < num_marcadores - 1:
                    try:
                        driver.refresh()
                        wait.until(EC.presence_of_all_elements_located(marcadores_selector))
                    except TimeoutException:
                        print("ERRO FATAL: A página não recarregou. Encerrando.")
                        break
    except Exception as e:
        print(f"\nOcorreu um erro fatal inesperado: {e}")
    finally:
        print("\nProcesso de captura de imagens concluído!")
        driver.quit()

if __name__ == "__main__":
    url_do_mapa_cameras = "https://cameras.praiagrande.sp.gov.br/aovivo/"
    pasta_para_salvar = r"D:\TCC\raspagem de dados\imagens_cameras_mapa"
    
    while True:
        print("="*50)
        print("Iniciando novo ciclo de captura de imagens...")
        print("="*50)
        
        capturar_imagens_marcadores(url_do_mapa_cameras, pasta_para_salvar)
        
        tempo_de_espera_segundos = 60 
        print(f"\nCiclo finalizado. Aguardando {tempo_de_espera_segundos / 60} minutos para reiniciar...")
        print("="*50)
        time.sleep(tempo_de_espera_segundos)