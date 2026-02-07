#!/usr/bin/env python3
"""
Script de debug para capturar a estrutura HTML da nota e ajustar seletores.
"""
import logging
from config import Config
from auth import AuthManager
from scraper import navigate_to_query_page, get_notes_from_list, open_note_detail
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    print("\n===========================================================")
    print("          DEBUG - Captura de Estrutura HTML              ")
    print("===========================================================\n")
    
    auth_manager = None
    
    try:
        # Validar config
        Config.validate()
        
        # Login
        logger.info("Fazendo login...")
        auth_manager = AuthManager()
        page = auth_manager.do_login()
        
        # Navegar para consulta
        logger.info("Navegando para página de consulta...")
        navigate_to_query_page(page)
        
        # Obter primeira nota
        logger.info("Buscando notas...")
        notes_list = get_notes_from_list(page)
        
        if not notes_list:
            logger.error("Nenhuma nota encontrada!")
            return 1
        
        logger.info(f"Encontradas {len(notes_list)} notas")
        
        # Abrir primeira nota
        logger.info("\nAbrindo primeira nota para análise...")
        note_info = notes_list[0]
        
        if open_note_detail(page, note_info):
            time.sleep(3)  # Aguarda carregamento completo
            
            # Salvar HTML completo da página de detalhe
            html_file = "html_nota_detalhe_completo.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(page.content())
            logger.info(f"✅ HTML da nota salvo: {html_file}")
            
            # Salvar screenshot
            screenshot_file = "nota_debug.png"
            page.screenshot(path=screenshot_file, full_page=True)
            logger.info(f"✅ Screenshot salvo: {screenshot_file}")
            
            # Tentar encontrar campos comuns e mostrar seletores
            print("\n" + "="*60)
            print("ANÁLISE AUTOMÁTICA - Elementos encontrados:")
            print("="*60)
            
            # Busca por campos de texto
            inputs = page.query_selector_all('input, textarea')
            if inputs:
                print(f"\n📝 Campos de entrada encontrados: {len(inputs)}")
                for i, inp in enumerate(inputs[:10]):  # Primeiros 10
                    try:
                        tag = inp.evaluate('el => el.tagName')
                        id_attr = inp.get_attribute('id') or ''
                        name_attr = inp.get_attribute('name') or ''
                        type_attr = inp.get_attribute('type') or ''
                        value = inp.input_value() or inp.inner_text() or ''
                        
                        if value:
                            print(f"\n  [{i+1}] <{tag.lower()}>")
                            if id_attr:
                                print(f"      ID: #{id_attr}")
                            if name_attr:
                                print(f"      Name: [name=\"{name_attr}\"]")
                            if type_attr:
                                print(f"      Type: [type=\"{type_attr}\"]")
                            print(f"      Valor: {value[:100]}")
                    except:
                        pass
            
            # Busca por tabelas
            tables = page.query_selector_all('table')
            if tables:
                print(f"\n📊 Tabelas encontradas: {len(tables)}")
                for i, table in enumerate(tables):
                    try:
                        rows = table.query_selector_all('tr')
                        print(f"\n  Tabela {i+1}: {len(rows)} linhas")
                        
                        # Mostra primeira linha como exemplo
                        if rows:
                            cells = rows[0].query_selector_all('td, th')
                            if cells:
                                texts = [c.inner_text().strip()[:30] for c in cells if c.inner_text().strip()]
                                if texts:
                                    print(f"    Primeira linha: {' | '.join(texts)}")
                    except:
                        pass
            
            # Busca por divs com classes/ids relevantes
            print(f"\nProcurando elementos com IDs/classes relevantes...")
            keywords = ['numero', 'data', 'valor', 'prestador', 'tomador', 'iss', 'cnpj', 'cpf']
            
            for keyword in keywords:
                selectors = [
                    f'[id*="{keyword}" i]',
                    f'[class*="{keyword}" i]',
                    f'label:has-text("{keyword.title()}")',
                ]
                
                for selector in selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            print(f"\n  Palavra-chave '{keyword}':")
                            for elem in elements[:3]:  # Primeiros 3
                                try:
                                    tag = elem.evaluate('el => el.tagName')
                                    id_attr = elem.get_attribute('id')
                                    class_attr = elem.get_attribute('class')
                                    text = elem.inner_text()[:50]
                                    
                                    info = f"    <{tag.lower()}>"
                                    if id_attr:
                                        info += f" id=\"{id_attr}\""
                                    if class_attr:
                                        info += f" class=\"{class_attr[:50]}\""
                                    if text:
                                        info += f" → {text}"
                                    
                                    print(info)
                                except:
                                    pass
                            break
                    except:
                        pass
            
            print("\n" + "="*60)
            print("PRÓXIMOS PASSOS:")
            print("="*60)
            print("""
1. Abra o arquivo 'nota_debug.html' no navegador
2. Pressione F12 para abrir DevTools
3. Use o seletor de elementos (🔍) para inspecionar cada campo
4. Copie os seletores corretos (ID, classe, etc)
5. Edite parser.py com os seletores reais
            
EXEMPLOS DE SELETORES:
- Por ID: #numero-nota ou input[id="numero-nota"]
- Por classe: .campo-numero ou span.valor-nota
- Por nome: input[name="numeroNota"]
- Por atributo: [data-field="numero"]
- Por texto: label:has-text("Número") + span
- Por posição: table tr:nth-child(1) td:nth-child(2)
            """)
            
        else:
            logger.error("Não foi possível abrir a nota")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return 1
        
    finally:
        if auth_manager:
            try:
                input("\nPressione ENTER para fechar o navegador...")
                auth_manager.close()
            except:
                pass


if __name__ == "__main__":
    import sys
    sys.exit(main())
