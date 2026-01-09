#!/usr/bin/env python3
"""
Script para exploração manual do site.
Abre o navegador, faz login e deixa você navegar manualmente.
"""
import logging
from config import Config
from auth import AuthManager
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║         EXPLORAÇÃO MANUAL - Emissor Nacional            ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    print("Este script vai:")
    print("1. Fazer login automaticamente")
    print("2. Deixar o navegador aberto para você explorar")
    print("3. Salvar screenshots e HTML quando você pressionar ENTER\n")
    
    auth_manager = None
    
    try:
        Config.validate()
        
        logger.info("Fazendo login...")
        auth_manager = AuthManager()
        page = auth_manager.do_login()
        
        logger.info("✅ Login realizado com sucesso!")
        
        # Salva screenshot inicial
        page.screenshot(path="screenshot_pos_login.png")
        logger.info("📸 Screenshot salvo: screenshot_pos_login.png")
        
        # Salva HTML inicial
        with open("html_pos_login.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        logger.info("📄 HTML salvo: html_pos_login.html")
        
        print("\n" + "="*60)
        print("NAVEGADOR ABERTO - Você pode explorar o site agora")
        print("="*60)
        print("\nInstruções:")
        print("1. Navegue até a página de consulta/lista de notas")
        print("2. Quando estiver na página certa, volte aqui e pressione ENTER")
        print("3. O script vai salvar a estrutura HTML dessa página")
        print("\nURL atual:", page.url)
        print()
        
        input("⏸️  Pressione ENTER quando estiver na página de LISTAGEM de notas...")
        
        # Salva página de listagem
        page.screenshot(path="screenshot_listagem.png")
        with open("html_listagem.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        
        logger.info("✅ Listagem salva!")
        logger.info("   - screenshot_listagem.png")
        logger.info("   - html_listagem.html")
        
        print("\n" + "="*60)
        print("Agora vamos capturar uma NOTA específica")
        print("="*60)
        print("\nInstruções:")
        print("1. Clique em uma nota para abrir os detalhes")
        print("2. Quando os detalhes da nota estiverem visíveis, volte aqui")
        print("3. Pressione ENTER para salvar")
        print()
        
        input("⏸️  Pressione ENTER quando estiver vendo os DETALHES de uma nota...")
        
        # Salva página de detalhe
        page.screenshot(path="screenshot_nota_detalhe.png", full_page=True)
        with open("html_nota_detalhe.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        
        logger.info("✅ Detalhes da nota salvos!")
        logger.info("   - screenshot_nota_detalhe.png")
        logger.info("   - html_nota_detalhe.html")
        
        print("\n" + "="*60)
        print("CAPTURAS CONCLUÍDAS!")
        print("="*60)
        print("\nArquivos gerados:")
        print("  📸 screenshot_pos_login.png")
        print("  📄 html_pos_login.html")
        print("  📸 screenshot_listagem.png")
        print("  📄 html_listagem.html")
        print("  📸 screenshot_nota_detalhe.png")
        print("  📄 html_nota_detalhe.html")
        print("\n" + "="*60)
        print("PRÓXIMOS PASSOS:")
        print("="*60)
        print("""
1. Abra html_listagem.html no navegador
   - Pressione F12 para DevTools
   - Inspecione a TABELA de notas
   - Encontre os seletores para:
     * Linhas da tabela (ex: table tbody tr)
     * Botões de paginação (próxima página)
   
2. Abra html_nota_detalhe.html no navegador
   - Pressione F12 para DevTools
   - Inspecione CADA CAMPO que você quer extrair
   - Anote os seletores (ID, classe, etc)
   
3. Edite os arquivos:
   - scraper.py → seletores da tabela e paginação
   - parser.py → seletores dos campos da nota

DICA: No DevTools, clique com botão direito no elemento
      e escolha "Copy > Copy selector"
        """)
        
        input("\nPressione ENTER para fechar o navegador...")
        
        return 0
        
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return 1
        
    finally:
        if auth_manager:
            try:
                auth_manager.close()
            except:
                pass


if __name__ == "__main__":
    import sys
    sys.exit(main())
