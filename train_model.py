# train_model.py
"""
Script para treinar um modelo de classificação de imagens para detectar enchentes.
"""
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# --- CONFIGURAÇÕES DE TREINAMENTO ---
# Caminho para a pasta com as imagens de treinamento.
# Você PRECISA criar esta estrutura de pastas.
DATASET_PATH = "dataset"
TRAIN_DIR = os.path.join(DATASET_PATH, "train")

# Parâmetros do modelo e treinamento.
IMG_WIDTH, IMG_HEIGHT = 150, 150
EPOCHS = 15  # Número de vezes que o modelo verá todo o dataset.
BATCH_SIZE = 32 # Número de imagens processadas por vez.

def criar_estrutura_pastas():
    """Cria a estrutura de pastas necessária se ela não existir."""
    if not os.path.exists(DATASET_PATH):
        print(f"Criando a pasta principal do dataset em '{DATASET_PATH}'...")
        os.makedirs(DATASET_PATH)
        
    train_flood_dir = os.path.join(TRAIN_DIR, "enchente")
    train_no_flood_dir = os.path.join(TRAIN_DIR, "nao_enchente")
    
    if not os.path.exists(train_flood_dir):
        os.makedirs(train_flood_dir)
        print(f"Pasta criada: '{train_flood_dir}'")
        print("-> COLOQUE SUAS IMAGENS DE ENCHENTE AQUI <-")
        
    if not os.path.exists(train_no_flood_dir):
        os.makedirs(train_no_flood_dir)
        print(f"Pasta criada: '{train_no_flood_dir}'")
        print("-> COLOQUE SUAS IMAGENS NORMAIS (SEM ENCHENTE) AQUI <-")

def treinar_modelo():
    """
    Constrói, compila e treina o modelo de CNN.
    """
    # 1. Preparação dos Dados (Data Augmentation)
    # Gera mais dados de treinamento a partir das imagens existentes (rotações, zoom, etc.)
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2 # Separa 20% dos dados para validação.
    )

    # Carrega imagens da pasta de treino.
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_WIDTH, IMG_HEIGHT),
        batch_size=BATCH_SIZE,
        class_mode='binary', # 'binary' porque temos 2 classes (enchente/nao_enchente)
        subset='training'
    )
    
    # Carrega imagens da pasta de validação.
    validation_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_WIDTH, IMG_HEIGHT),
        batch_size=BATCH_SIZE,
        class_mode='binary',
        subset='validation'
    )

    # 2. Construção do Modelo (CNN - Rede Neural Convolucional)
    model = Sequential([
        # Camada 1: Extrai características básicas (bordas, texturas).
        Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)),
        MaxPooling2D(2, 2),

        # Camada 2: Extrai características mais complexas.
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        # Camada 3
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        # Achata os dados para a rede neural densa.
        Flatten(),

        # Camada densa para aprender as combinações de características.
        Dense(512, activation='relu'),
        Dropout(0.5), # Técnica para evitar overfitting.

        # Camada de saída: 1 neurônio com 'sigmoid' para dar uma probabilidade (0 a 1).
        Dense(1, activation='sigmoid')
    ])

    # 3. Compilação do Modelo
    model.compile(loss='binary_crossentropy',
                  optimizer=tf.keras.optimizers.RMSprop(learning_rate=1e-4),
                  metrics=['accuracy'])
                  
    model.summary()

    # 4. Treinamento
    print("\nIniciando o treinamento do modelo...")
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE
    )

    # 5. Salvar o Modelo Treinado
    model.save("flood_detection_model.h5")
    print("\nTreinamento concluído! Modelo salvo como 'flood_detection_model.h5'.")

if __name__ == "__main__":
    criar_estrutura_pastas()
    print("\nEstrutura de pastas verificada. Por favor, adicione suas imagens antes de treinar.")
    # Para treinar, descomente a linha abaixo após adicionar as imagens.
    treinar_modelo()