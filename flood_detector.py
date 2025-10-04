# flood_detector.py
"""
Módulo para detecção de enchentes em imagens usando um modelo de Machine Learning.
"""
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os

# --- CONFIGURAÇÕES DO MODELO ---
# Caminho para o arquivo do modelo treinado.
# Este arquivo será gerado pelo script de treinamento (train_model.py).
MODEL_PATH = "flood_detection_model.h5"
# Dimensões esperadas pela entrada do modelo (ajuste conforme o treinamento)
IMG_WIDTH, IMG_HEIGHT = 150, 150

# Carrega o modelo treinado uma única vez para evitar recarregamentos.
try:
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Modelo de detecção de enchentes carregado com sucesso.")
    else:
        model = None
        print("AVISO: Arquivo do modelo não encontrado. A detecção de enchentes está desativada.")
except Exception as e:
    model = None
    print(f"Erro ao carregar o modelo: {e}. A detecção está desativada.")

def classificar_imagem(caminho_da_imagem):
    """
    Carrega uma imagem, a pré-processa e usa o modelo para prever se há uma enchente.
    Retorna True se for uma enchente, False caso contrário.
    """
    if not model:
        print("Modelo não disponível. Impossível classificar a imagem.")
        return False

    try:
        # Carrega e redimensiona a imagem para o tamanho que o modelo espera.
        img = image.load_img(caminho_da_imagem, target_size=(IMG_WIDTH, IMG_HEIGHT))
        
        # Converte a imagem para um array numpy e normaliza os pixels.
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Normalização

        # Realiza a predição.
        prediction = model.predict(img_array)
        
        # A saída do modelo é uma probabilidade. Se for > 0.5, consideramos "enchente".
        if prediction[0][0] > 0.5:
            print(f"ALERTA: Possível enchente detectada na imagem '{caminho_da_imagem}' (Confiança: {prediction[0][0]:.2f})")
            return True
        else:
            print(f"Análise: Nenhuma enchente detectada na imagem '{caminho_da_imagem}' (Confiança: {1 - prediction[0][0]:.2f})")
            return False
            
    except Exception as e:
        print(f"Erro ao classificar a imagem '{caminho_da_imagem}': {e}")
        return False