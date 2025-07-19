"""
Configuração de logging otimizada para Windows
Resolve problemas de encoding com emojis e caracteres unicode
"""

import logging
import sys
import os
from datetime import datetime

def setup_windows_logging(level=logging.INFO):
    """
    Configura logging para funcionar corretamente no Windows
    com suporte a caracteres unicode e emojis
    """
    
    # Remove handlers existentes
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configuração do formatter sem emojis problemáticos
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console com encoding UTF-8
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Configuração do logger raiz
    logging.root.setLevel(level)
    logging.root.addHandler(console_handler)
    
    # Handler para arquivo de log
    try:
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'scraper_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logging.root.addHandler(file_handler)
        
    except Exception as e:
        logging.warning(f"Não foi possível configurar log de arquivo: {e}")

def clean_message(message):
    """Remove emojis e caracteres problemáticos das mensagens de log"""
    # Substitui emojis comuns por texto
    replacements = {
        '🚀': '[INICIO]',
        '✅': '[OK]',
        '❌': '[ERRO]',
        '⚠️': '[AVISO]',
        '🔍': '[BUSCA]',
        '📊': '[DADOS]',
        '🎯': '[ALVO]',
        '🔧': '[CONFIG]',
        '📄': '[ARQUIVO]',
        '⏱️': '[TEMPO]',
        '🏁': '[FIM]',
        '🎉': '[SUCESSO]',
        '🏠': '[IMOVEL]',
        '⏰': '[HORA]'
    }
    
    clean_msg = str(message)
    for emoji, replacement in replacements.items():
        clean_msg = clean_msg.replace(emoji, replacement)
    
    return clean_msg

def log_info(message):
    """Log info com limpeza de caracteres"""
    logging.info(clean_message(message))

def log_error(message):
    """Log error com limpeza de caracteres"""
    logging.error(clean_message(message))

def log_warning(message):
    """Log warning com limpeza de caracteres"""
    logging.warning(clean_message(message))

def log_debug(message):
    """Log debug com limpeza de caracteres"""
    logging.debug(clean_message(message))
