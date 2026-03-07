#!/usr/bin/env python3
"""
Exportador de NFSe do Emissor Nacional.
Script principal que orquestra todo o processo de extração.
"""
import logging
import sys
from datetime import datetime
from config import Config
from auth import AuthManager
from scraper import collect_notes
from excel import generate_excel, generate_csv


# Configuração de logging
def setup_logging():
    """Configura o sistema de logging"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Cria handler para arquivo
    log_filename = f"nfse_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Cria handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    
    # Configura logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return log_filename


def print_banner():
    """Exibe banner inicial"""
    banner = """
===========================================================
           Exportador de NFSe - Emissor Nacional           
===========================================================
    """
    print(banner)


def print_summary(notes_count: int, excel_file: str, elapsed_time: float):
    """Exibe resumo da execução"""
    summary = f"""
===========================================================
                    RESUMO DA EXECUÇÃO                     
===========================================================
   Notas coletadas: {notes_count:<39} 
   Arquivo gerado:  {excel_file:<39} 
   Tempo decorrido: {elapsed_time:.2f}s{' ' * (39 - len(f'{elapsed_time:.2f}s'))} 
===========================================================
    """
    print(summary)


def main():
    """Função principal"""
    
    # Setup
    print_banner()
    log_filename = setup_logging()
    logger = logging.getLogger(__name__)
    
    start_time = datetime.now()
    auth_manager = None
    
    try:
        logger.info("=" * 60)
        logger.info("INICIANDO EXPORTAÇÃO DE NFSe")
        logger.info("=" * 60)
        
        # Valida configurações
        logger.info("Validando configurações...")
        Config.validate()
        logger.info(f"Período: {Config.START_DATE} até {Config.END_DATE}")
        logger.info(f"Usuário: {Config.NFSE_USER}")
        logger.info(f"Log salvo em: {log_filename}")
        
        # Autenticação
        logger.info("-" * 60)
        logger.info("ETAPA 1: Autenticação")
        logger.info("-" * 60)
        
        auth_manager = AuthManager()
        page = auth_manager.do_login()
        
        # Coleta de notas
        logger.info("-" * 60)
        logger.info("ETAPA 2: Coleta de Notas")
        logger.info("-" * 60)
        
        notes = collect_notes(page)
        
        if not notes:
            logger.warning("Nenhuma nota foi coletada!")
            print("\nAVISO: Nenhuma nota encontrada no período especificado.")
            return 1
        
        # Geração de relatório
        logger.info("-" * 60)
        logger.info("ETAPA 3: Geração de Relatório")
        logger.info("-" * 60)
        
        excel_file = generate_excel(notes)
        
        # Opcionalmente gera CSV também
        # csv_file = generate_csv(notes)
        
        # Finalização
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("EXPORTAÇÃO CONCLUÍDA COM SUCESSO")
        logger.info("=" * 60)
        
        print_summary(len(notes), excel_file, elapsed_time)
        
        print(f"\nExportação concluída com sucesso!")
        print(f"Relatório: {excel_file}")
        print(f"Log: {log_filename}\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Execução interrompida pelo usuário")
        print("\nExecução cancelada pelo usuário.")
        return 130
        
    except Exception as e:
        logger.error(f"Erro durante execução: {str(e)}", exc_info=True)
        print(f"\nErro: {str(e)}")
        print(f"Verifique o log para mais detalhes: {log_filename}\n")
        return 1
        
    finally:
        # Cleanup
        if auth_manager:
            try:
                logger.info("Fechando navegador...")
                auth_manager.close()
            except Exception as e:
                logger.warning(f"Erro ao fechar navegador: {e}")


if __name__ == "__main__":
    sys.exit(main())
