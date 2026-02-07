"""
Módulo de scraping de NFSe.
Navega pelo site, pagina resultados e coleta as notas.
"""
import logging
import time
from typing import List, Dict
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from config import Config
from parser import extract_note_data

logger = logging.getLogger(__name__)


def navigate_to_query_page(page: Page):
    """
    Navega até a página de consulta de notas.
    """
    logger.info("Navegando para página de consulta de notas...")
    
    try:
        # NOTA: Os seletores abaixo são GENÉRICOS
        # Ajuste conforme a estrutura real do site
        
        # Acessa diretamente a página de notas emitidas
        logger.info(f"Acessando: {Config.QUERY_URL}")
        page.goto(Config.QUERY_URL, wait_until="domcontentloaded", timeout=15000)
        time.sleep(2)
        page.wait_for_load_state("networkidle", timeout=10000)
        
        # Preenche filtros de data (baseado no HTML real)
        try:
            # Campos de data no HTML real são input[id="datainicio"] e input[id="datafim"]
            data_inicio = page.query_selector('input#datainicio')
            if data_inicio:
                # Limpa campo antes
                data_inicio.click()
                data_inicio.fill('')
                # Formato: DD/MM/YYYY conforme o site
                data_formatada = Config.START_DATE.split('-')
                data_br = f"{data_formatada[2]}/{data_formatada[1]}/{data_formatada[0]}"
                data_inicio.fill(data_br)
                logger.info(f"Data início preenchida: {data_br}")
            
            data_fim = page.query_selector('input#datafim')
            if data_fim:
                data_fim.click()
                data_fim.fill('')
                # Formato: DD/MM/YYYY conforme o site
                data_formatada = Config.END_DATE.split('-')
                data_br = f"{data_formatada[2]}/{data_formatada[1]}/{data_formatada[0]}"
                data_fim.fill(data_br)
                logger.info(f"Data fim preenchida: {data_br}")
            
            # Clica no botão filtrar
            filtrar_button = page.query_selector('button:has-text("Filtrar")')
            if filtrar_button:
                logger.info("Aplicando filtro...")
                filtrar_button.click()
                time.sleep(3)
                page.wait_for_load_state("networkidle", timeout=10000)
            else:
                logger.warning("Botão filtrar não encontrado")
        
        except Exception as e:
            logger.warning(f"Não foi possível preencher filtros de data: {e}")
        
        logger.info("Página de consulta carregada")
        
    except Exception as e:
        logger.error(f"Erro ao navegar para página de consulta: {e}")
        raise


def get_notes_from_list(page: Page) -> List[Dict]:
    """
    Extrai informações básicas das notas da listagem atual.
    Retorna lista de dicts com informações para navegação.
    """
    notes_info = []
    
    # Seletor ajustado baseado no HTML real
    rows = page.query_selector_all('table.table tbody tr[data-chave]')
    
    if not rows:
        logger.warning("Nenhuma nota encontrada na página")
        return notes_info
    
    logger.info(f"Encontradas {len(rows)} notas na listagem")
    
    for idx, row in enumerate(rows):
        try:
            # Pega o link de visualizar
            visualizar_link = row.query_selector('a[href*="Visualizar"]')
            
            if visualizar_link:
                note_info = {
                    'index': idx,
                    'visualizar_url': visualizar_link.get_attribute('href'),
                    'data_chave': row.get_attribute('data-chave'),
                    'valor': row.get_attribute('data-valor')
                }
                
                # Extrai data da primeira célula
                data_cell = row.query_selector('td.td-data')
                if data_cell:
                    note_info['data'] = data_cell.inner_text().strip()
                
                notes_info.append(note_info)
            
        except Exception as e:
            logger.warning(f"Erro ao processar linha {idx}: {e}")
            continue
    
    logger.info(f"Processadas {len(notes_info)} notas da listagem")
    return notes_info


def open_note_detail(page: Page, note_info: Dict, retry_count: int = 0) -> bool:
    """
    Abre o detalhe de uma nota específica.
    Retorna True se bem-sucedido.
    """
    try:
        # Navega diretamente para a URL da nota
        visualizar_url = note_info.get('visualizar_url')
        
        if not visualizar_url:
            logger.warning(f"URL de visualização não encontrada")
            return False
        
        # Se for URL relativa, completa com base URL
        if visualizar_url.startswith('/'):
            # Remove /EmissorNacional se já estiver na URL relativa
            if visualizar_url.startswith('/EmissorNacional'):
                visualizar_url = 'https://www.nfse.gov.br' + visualizar_url
            else:
                visualizar_url = Config.BASE_URL + visualizar_url
        
        logger.debug(f"Abrindo URL: {visualizar_url}")
        page.goto(visualizar_url, wait_until="domcontentloaded", timeout=10000)
        time.sleep(1.5)
        
        # Verifica se carregou corretamente (verificação mais específica)
        page_content = page.content()
        
        # Verifica se é página de erro do servidor
        if "server error" in page_content.lower() or "404" in page_content:
            logger.warning(f"Página de erro 404 - URL: {visualizar_url}")
            # Salva HTML para debug
            with open('erro_404_debug.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            return False
        
        # Verifica se tem conteúdo de nota (painel de identificação)
        if 'Identificação da NFS-e' in page_content or 'panel-title' in page_content:
            return True
        else:
            logger.warning(f"Página sem conteúdo de nota")
            return False
        
    except Exception as e:
        if retry_count < Config.MAX_RETRIES:
            logger.warning(f"Erro ao abrir nota, tentativa {retry_count + 1}/{Config.MAX_RETRIES}: {e}")
            time.sleep(2)
            return open_note_detail(page, note_info, retry_count + 1)
        else:
            logger.error(f"Falha ao abrir nota após {Config.MAX_RETRIES} tentativas: {e}")
            return False


def close_note_detail(page: Page):
    """Fecha o detalhe da nota e volta para a listagem."""
    try:
        # Tenta fechar modal se existir
        close_selectors = [
            'button.close',
            '.modal-header .close',
            'button[aria-label="Close"]',
            '[data-dismiss="modal"]'
        ]
        
        for selector in close_selectors:
            close_button = page.query_selector(selector)
            if close_button:
                close_button.click()
                time.sleep(0.5)
                return
        
        # Se não for modal, pode ser nova página - volta
        page.go_back()
        time.sleep(1)
        
    except Exception as e:
        logger.warning(f"Erro ao fechar detalhe da nota: {e}")


def has_next_page(page: Page) -> bool:
    """Verifica se existe próxima página na paginação."""
    
    # Busca o link "Próxima" que NÃO está disabled
    # No HTML real: <li><a href="/EmissorNacional/Notas/Emitidas?pg=2">...</a></li>
    
    # Verifica se tem botão de próxima página ativo
    next_links = page.query_selector_all('.pagination li:not(.disabled) a[href*="?pg="]')
    
    for link in next_links:
        # Verifica se o ícone é o de "próxima" (fa-angle-right)
        icon = link.query_selector('i.fa-angle-right')
        if icon:
            return True
    
    return False


def go_to_next_page(page: Page) -> bool:
    """Navega para a próxima página. Retorna True se bem-sucedido."""
    
    # Busca o link com ícone fa-angle-right (próxima página)
    next_links = page.query_selector_all('.pagination li:not(.disabled) a[href*="?pg="]')
    
    for link in next_links:
        # Verifica se o ícone é o de "próxima" (fa-angle-right, não double)
        icon = link.query_selector('i.fa-angle-right:not(.fa-angle-double-right)')
        if icon:
            try:
                href = link.get_attribute('href')
                logger.info(f"Navegando para próxima página: {href}")
                link.click()
                time.sleep(2)
                page.wait_for_load_state("networkidle", timeout=10000)
                return True
            except Exception as e:
                logger.warning(f"Erro ao clicar em próxima página: {e}")
                return False
    
    return False


def collect_notes(page: Page) -> List[Dict]:
    """
    Função principal de coleta de notas.
    Navega por todas as páginas e extrai dados de cada nota.
    """
    logger.info("Iniciando coleta de notas...")
    
    all_notes = []
    page_number = 1
    
    try:
        # Navega até página de consulta
        navigate_to_query_page(page)
        
        while True:
            logger.info(f"Processando página {page_number}...")
            
            # Obtém lista de notas da página atual
            notes_list = get_notes_from_list(page)
            
            if not notes_list:
                logger.warning("Nenhuma nota encontrada na página")
                break
            
            # Processa cada nota
            for idx, note_info in enumerate(notes_list):
                try:
                    logger.info(f"Processando nota {idx + 1}/{len(notes_list)} da página {page_number}")
                    
                    # Abre detalhe da nota
                    if open_note_detail(page, note_info):
                        # Aguarda carregamento
                        time.sleep(Config.DELAY_BETWEEN_NOTES)
                        
                        # Extrai dados da nota
                        note_data = extract_note_data(page)
                        all_notes.append(note_data)
                        
                        # Monta log rico com detalhes da nota
                        log_msg = f"Nota coletada: DPS {note_data.get('numero_dps', 'N/A')}"
                        if note_data.get('valor_total'):
                             log_msg += f" - Valor: R$ {note_data.get('valor_total')}"
                        elif note_data.get('valor_servicos'):
                             log_msg += f" - Valor: R$ {note_data.get('valor_servicos')}"
                        
                        if note_data.get('tomador_razao_social'):
                             log_msg += f" - Tomador: {note_data.get('tomador_razao_social')}"
                             
                        logger.info(log_msg)
                        
                        # Fecha detalhe
                        close_note_detail(page)
                        time.sleep(0.2)
                    else:
                        logger.warning(f"Pulando nota {idx + 1} por falha ao abrir")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar nota {idx + 1}: {e}")
                    # Tenta recuperar voltando para listagem
                    try:
                        close_note_detail(page)
                    except:
                        pass
                    continue
            
            # Verifica se há próxima página
            if has_next_page(page):
                if go_to_next_page(page):
                    page_number += 1
                    time.sleep(1)
                else:
                    logger.info("Não foi possível navegar para próxima página")
                    break
            else:
                logger.info("Última página processada")
                break
        
        logger.info(f"Coleta finalizada. Total de notas coletadas: {len(all_notes)}")
        return all_notes
        
    except Exception as e:
        logger.error(f"Erro durante coleta de notas: {e}")
        raise
