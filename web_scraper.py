# web_scraper.py
"""
Módulo responsável pela raspagem de dados do mapa de câmeras usando Selenium.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import time
import datetime

# Importa as configurações e utilitários
import config
from utils import sanitizar_nome_arquivo

def capturar_imagens_marcadores():
    """
    Navega no mapa, clica nos marcadores, tira screenshots e 'yield' o caminho de cada arquivo salvo.
    """
    service = Service(config.CHROME_DRIVER_PATH)
    pasta_destino = config.PASTA_IMAGENS_LOCAIS
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"Pasta '{pasta_destino}' criada.")

    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    try:
        print(f"Acessando o mapa: {config.URL_MAPA_CAMERAS}")
        driver.get(config.URL_MAPA_CAMERAS)
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

                # ... (resto da sua lógica de scraping é mantida) ...
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

                # EM VEZ DE FAZER UPLOAD, "ENTREGA" O CAMINHO DO ARQUIVO
                yield nome_arquivo

            except Exception as e:
                print(f"Erro ao processar o marcador {i + 1}: {type(e).__name__} - {e}.")

            finally:
                if i < num_marcadores - 1:
                    try:
                        driver.refresh()
                        wait.until(EC.presence_of_all_elements_located(marcadores_selector))
                    except TimeoutException:
                        print("ERRO FATAL: A página não recarregou. Encerrando.")
                        break
    finally:
        print("\nProcesso de captura de imagens concluído!")
        driver.quit()