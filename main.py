# main.py
"""
Arquivo principal que orquestra o fluxo do programa:
1. Inicia o scraper de imagens.
2. Para cada imagem capturada, aciona o sistema de detecção de enchentes.
3. Aciona o upload para o Google Drive.
4. Repete o processo em um ciclo infinito com um tempo de espera.
"""
import time
import os

# Importa as funções e configurações dos outros módulos
from web_scraper import capturar_imagens_marcadores
from drive_api import autenticar_e_obter_servico, upload_para_drive
from flood_detector import classificar_imagem # <--- IMPORTAÇÃO ADICIONADA
import config

def main():
    """Função principal que executa o loop de captura e upload."""
    
    # Autentica no Google Drive uma vez no início.
    print("Autenticando com o Google Drive...")
    servico_drive = autenticar_e_obter_servico()
    if not servico_drive:
        print("Não foi possível autenticar. O programa será encerrado.")
        return

    while True:
        print("="*50)
        print("Iniciando novo ciclo de captura e upload...")
        print("="*50)
        
        # O 'for' loop consome os caminhos de arquivo que o scraper "gera" (yield).
        # A cada imagem salva localmente, o loop executa uma iteração.
        for caminho_do_arquivo in capturar_imagens_marcadores():
            
            # --- NOVA ETAPA: DETECÇÃO DE ENCHENTE ---
            print(f"\nAnalisando a imagem '{caminho_do_arquivo}' para detecção de enchentes...")
            is_flood = classificar_imagem(caminho_do_arquivo)
            
            # Ação com base na detecção (aqui você pode adicionar alertas, etc.)
            if is_flood:
                print(f"ALERTA DE ENCHENTE! A imagem '{caminho_do_arquivo}' foi classificada como contendo uma enchente.")
                # Futuramente: enviar um email, notificação, etc.
            
            # --- FIM DA NOVA ETAPA ---

            print("\nIniciando upload para o Google Drive...")
            sucesso = upload_para_drive(servico_drive, caminho_do_arquivo)
            
            # Opcional: Apaga o arquivo local após o upload bem-sucedido
            if sucesso:
                try:
                    os.remove(caminho_do_arquivo)
                    print(f"Arquivo local removido: '{caminho_do_arquivo}'")
                except OSError as e:
                    print(f"Erro ao remover arquivo local: {e}")
        
        print(f"\nCiclo finalizado. Aguardando {config.TEMPO_ESPERA_CICLO_SEGUNDOS / 60} minutos para reiniciar...")
        print("="*50)
        time.sleep(config.TEMPO_ESPERA_CICLO_SEGUNDOS)

if __name__ == "__main__":
    main()