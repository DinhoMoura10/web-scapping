# google_drive_uploader.py
"""
Módulo responsável por toda a interação com a API do Google Drive.
Inclui autenticação e a função de upload de arquivos.
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Importa as configurações necessárias
import config

def autenticar_e_obter_servico():
    """Gerencia a autenticação com a API do Google e retorna um objeto de serviço."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", config.SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", config.SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    try:
        service = build("drive", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"Ocorreu um erro ao construir o serviço do Drive: {e}")
        return None

def upload_para_drive(service, file_path):
    """Faz o upload de um único arquivo para a pasta configurada no Google Drive."""
    if not service:
        print("Serviço do Google Drive não está disponível. Upload cancelado.")
        return False
        
    try:
        file_metadata = {
            "name": os.path.basename(file_path),
            "parents": [config.DRIVE_FOLDER_ID]
        }
        media = MediaFileUpload(file_path, mimetype='image/png')
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()
        
        print(f"Upload bem-sucedido! ID do arquivo no Drive: {file.get('id')}")
        return True

    except HttpError as error:
        print(f"Ocorreu um erro na API do Google Drive: {error}")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado no upload: {e}")
        return False