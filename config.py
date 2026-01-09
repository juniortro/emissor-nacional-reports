"""
Módulo de configuração do exportador de NFSe.
Carrega variáveis de ambiente e define constantes do sistema.
"""
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()


class Config:
    """Configurações do sistema"""
    
    # Credenciais
    NFSE_USER = os.getenv("NFSE_USER")
    NFSE_PASSWORD = os.getenv("NFSE_PASSWORD")
    
    # Período de busca
    START_DATE = os.getenv("DATA_INICIO", "2026-01-01")
    END_DATE = os.getenv("DATA_FIM", "2026-01-31")
    
    # Configurações do navegador
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    TIMEOUT = int(os.getenv("TIMEOUT", "30000"))
    
    # Comportamento
    DELAY_BETWEEN_NOTES = float(os.getenv("DELAY_ENTRE_NOTAS", "1.5"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # URLs
    BASE_URL = "https://www.nfse.gov.br/EmissorNacional"
    LOGIN_URL = f"{BASE_URL}/login"
    QUERY_URL = f"{BASE_URL}/Notas/Emitidas"  # URL real do menu
    
    @classmethod
    def validate(cls):
        """Valida se as configurações obrigatórias estão presentes"""
        errors = []
        
        if not cls.NFSE_USER:
            errors.append("NFSE_USER não configurado")
        
        if not cls.NFSE_PASSWORD:
            errors.append("NFSE_PASSWORD não configurado")
        
        if errors:
            raise ValueError(f"Configuração inválida: {', '.join(errors)}")
        
        return True
