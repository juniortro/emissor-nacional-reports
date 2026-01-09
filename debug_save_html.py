"""
Script de debug para salvar HTML da página de detalhe da nota.
Executa login, acessa uma nota e salva o HTML completo.
"""
import logging
import time
from playwright.sync_api import sync_playwright
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    with sync_playwright() as p:
        # Lança Firefox
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Login
            logger.info("Fazendo login...")
            page.goto("https://www.nfse.gov.br/EmissorNacional/Login", timeout=15000)
            time.sleep(2)
            
            page.fill('input[name="Login"]', Config.USERNAME)
            page.fill('input[name="Senha"]', Config.PASSWORD)
            page.click('button[type="submit"]')
            time.sleep(3)
            page.wait_for_load_state("networkidle")
            
            # Acessa página de notas
            logger.info("Acessando notas emitidas...")
            page.goto(Config.QUERY_URL, timeout=15000)
            time.sleep(2)
            page.wait_for_load_state("networkidle")
            
            # Pega primeira nota da lista
            logger.info("Buscando primeira nota...")
            rows = page.query_selector_all('table.table tbody tr[data-chave]')
            
            if rows:
                first_row = rows[0]
                visualizar_link = first_row.query_selector('a[href*="Visualizar"]')
                
                if visualizar_link:
                    href = visualizar_link.get_attribute('href')
                    if href.startswith('/'):
                        url = 'https://www.nfse.gov.br' + href
                    else:
                        url = href
                    
                    logger.info(f"Abrindo nota: {url}")
                    page.goto(url, timeout=15000)
                    time.sleep(3)
                    page.wait_for_load_state("networkidle")
                    
                    # Salva HTML completo
                    html_content = page.content()
                    output_file = 'html_nota_detalhe_completo.html'
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    logger.info(f"HTML salvo em: {output_file}")
                    
                    # Aguarda para visualizar
                    logger.info("Pressione CTRL+C para encerrar...")
                    time.sleep(60)
                else:
                    logger.error("Link visualizar não encontrado")
            else:
                logger.error("Nenhuma nota encontrada")
        
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
