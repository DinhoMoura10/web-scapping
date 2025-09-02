# utils.py
"""
Módulo para funções utilitárias e auxiliares.
"""
import re

def sanitizar_nome_arquivo(nome):
    """Limpa e formata um nome para ser seguro como nome de arquivo."""
    if nome.lower().startswith("câmera:"):
        nome = nome[7:].strip()
    # Remove caracteres inválidos e substitui espaços por underscores
    return re.sub(r'[\\/*?:"<>|\s]', '_', nome)