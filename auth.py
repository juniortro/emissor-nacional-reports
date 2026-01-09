"""
Módulo de autenticação no Emissor Nacional.
Gerencia login e manutenção de sessão.
"""
import logging
import time
from playwright.sync_api import sync_playwright, Page, Browser, Playwright
from config import Config

logger = logging.getLogger(__name__)


class AuthManager:
    """Gerenciador de autenticação"""
    
    def __init__(self):
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.page: Page = None
    
    def start_browser(self):
        """Inicializa o navegador Playwright"""
        logger.info("Iniciando Firefox...")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.firefox.launch(
            headless=Config.HEADLESS
        )
        
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080} if not Config.HEADLESS else None
        )
        
        self.page = context.new_page()
        self.page.set_default_timeout(Config.TIMEOUT)
        
        logger.info("Navegador iniciado com sucesso")
        return self.page
    
    def do_login(self) -> Page:
        """
        Realiza login no Emissor Nacional.
        Retorna a página autenticada.
        """
        if not self.page:
            self.start_browser()
        
        logger.info(f"Acessando URL de login: {Config.BASE_URL}")
        
        try:
            # Acessa a página principal
            self.page.goto(Config.BASE_URL, wait_until="domcontentloaded")
            time.sleep(2)
            
            logger.info("Preenchendo credenciais...")
            
            # NOTA: Os seletores abaixo são GENÉRICOS e precisam ser ajustados
            # após inspeção do site real com DevTools
            
            # Tenta diferentes seletores comuns para login
            user_selectors = [
                'input[name="username"]',
                'input[id="username"]',
                'input[name="usuario"]',
                'input[type="text"]',
                '#login',
                '[placeholder*="CPF"]',
                '[placeholder*="CNPJ"]',
                '[placeholder*="Usuário"]'
            ]
            
            password_selectors = [
                'input[name="password"]',
                'input[id="password"]',
                'input[name="senha"]',
                'input[type="password"]',
                '[placeholder*="Senha"]'
            ]
            
            button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Entrar")',
                'button:has-text("Login")',
                'button:has-text("Acessar")',
                '.btn-login',
                '#btnLogin'
            ]
            
            # Tenta preencher usuário
            user_field = None
            for selector in user_selectors:
                try:
                    user_field = self.page.wait_for_selector(selector, timeout=2000)
                    if user_field:
                        logger.info(f"Campo usuário encontrado: {selector}")
                        break
                except:
                    continue
            
            if not user_field:
                raise Exception("Campo de usuário não encontrado. Ajuste os seletores em auth.py")
            
            user_field.fill(Config.NFSE_USER)
            time.sleep(0.5)
            
            # Tenta preencher senha
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.page.wait_for_selector(selector, timeout=2000)
                    if password_field:
                        logger.info(f"Campo senha encontrado: {selector}")
                        break
                except:
                    continue
            
            if not password_field:
                raise Exception("Campo de senha não encontrado. Ajuste os seletores em auth.py")
            
            password_field.fill(Config.NFSE_PASSWORD)
            time.sleep(0.5)
            
            # Tenta clicar no botão de login
            login_button = None
            for selector in button_selectors:
                try:
                    login_button = self.page.wait_for_selector(selector, timeout=2000)
                    if login_button:
                        logger.info(f"Botão login encontrado: {selector}")
                        break
                except:
                    continue
            
            if not login_button:
                raise Exception("Botão de login não encontrado. Ajuste os seletores em auth.py")
            
            logger.info("Efetuando login...")
            login_button.click()
            
            # Aguarda navegação pós-login
            time.sleep(3)
            self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # Verifica se o login foi bem-sucedido
            current_url = self.page.url
            logger.info(f"URL após login: {current_url}")
            
            # Verifica se ainda está na página de login (indicaria falha)
            if "login" in current_url.lower() and "error" not in current_url.lower():
                # Pode estar aguardando redirecionamento, aguarda mais um pouco
                time.sleep(2)
                current_url = self.page.url
            
            # Verifica indicadores de erro
            visible_errors = self.page.query_selector_all('.alert-danger, .error, [class*="erro"]')
            if visible_errors:
                error_message = visible_errors[0].inner_text()
                raise Exception(f"Erro no login: {error_message}")
            
            logger.info("Login realizado com sucesso!")
            return self.page
            
        except Exception as e:
            logger.error(f"Erro ao fazer login: {str(e)}")
            # Salva screenshot para debug
            try:
                self.page.screenshot(path="erro_login.png")
                logger.info("Screenshot salvo: erro_login.png")
            except:
                pass
            raise
    
    def close(self):
        """Fecha o navegador e libera recursos"""
        logger.info("Fechando navegador...")
        
        if self.page:
            self.page.close()
        
        if self.browser:
            self.browser.close()
        
        if self.playwright:
            self.playwright.stop()
        
        logger.info("Navegador fechado")


def login() -> Page:
    """
    Função de conveniência para fazer login.
    Retorna a página autenticada.
    """
    auth = AuthManager()
    return auth.do_login()
