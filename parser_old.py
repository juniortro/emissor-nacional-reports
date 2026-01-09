"""
Módulo de parsing de dados das NFSe.
Extrai informações estruturadas das páginas de nota.
"""
import logging
import re
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Remove espaços extras e quebras de linha"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def extract_number(text: str) -> str:
    """Extrai apenas números de um texto"""
    if not text:
        return ""
    return re.sub(r'\D', '', text)


def extract_monetary_value(text: str) -> str:
    """Extrai valor monetário de um texto"""
    if not text:
        return "0.00"
    
    # Remove tudo exceto números, vírgula e ponto
    value = re.sub(r'[^\d,.]', '', text)
    
    # Converte formato BR para US (1.234,56 -> 1234.56)
    if ',' in value and '.' in value:
        value = value.replace('.', '').replace(',', '.')
    elif ',' in value:
        value = value.replace(',', '.')
    
    try:
        return f"{float(value):.2f}"
    except:
        return "0.00"


def try_extract(page: Page, selectors: list, extract_func=None) -> str:
    """
    Tenta extrair texto usando múltiplos seletores.
    Retorna o primeiro que funcionar.
    """
    for selector in selectors:
        try:
            element = page.query_selector(selector)
            if element:
                text = clean_text(element.inner_text())
                if extract_func:
                    text = extract_func(text)
                return text
        except:
            continue
    return ""


def extract_note_data(page: Page) -> dict:
    """
    Extrai todos os dados relevantes de uma NFSe.
    
    IMPORTANTE: Os seletores abaixo são GENÉRICOS e precisam ser ajustados
    após inspeção da página real da nota com DevTools (F12).
    """
    
    logger.debug("Extraindo dados da nota...")
    
    # Seletores genéricos - DEVEM SER AJUSTADOS conforme o site real
    data = {
        "numero_nfse": try_extract(page, [
            '#numero-nfse',
            '[data-field="numero"]',
            '.numero-nota',
            'span:has-text("Número")',
            'label:has-text("Número") + span',
            'td:has-text("Número") + td'
        ]),
        
        "data_emissao": try_extract(page, [
            '#data-emissao',
            '[data-field="dataEmissao"]',
            '.data-emissao',
            'span:has-text("Data de Emissão")',
            'label:has-text("Emissão") + span',
            'td:has-text("Emissão") + td'
        ]),
        
        "codigo_verificacao": try_extract(page, [
            '#codigo-verificacao',
            '[data-field="codigoVerificacao"]',
            '.codigo-verificacao',
            'span:has-text("Código de Verificação")',
            'label:has-text("Verificação") + span'
        ]),
        
        # Dados do Prestador
        "prestador_razao_social": try_extract(page, [
            '#prestador-nome',
            '[data-field="prestador.nome"]',
            '.prestador-nome',
            '.razao-social-prestador',
            'div:has-text("Prestador") + div .nome',
            'h3:has-text("Prestador") ~ div .nome'
        ]),
        
        "prestador_cnpj": try_extract(page, [
            '#prestador-cnpj',
            '[data-field="prestador.cnpj"]',
            '.prestador-cnpj',
            'div:has-text("Prestador") + div .cnpj',
            'h3:has-text("Prestador") ~ div .cnpj'
        ], extract_number),
        
        "prestador_municipio": try_extract(page, [
            '#prestador-municipio',
            '[data-field="prestador.municipio"]',
            '.prestador-municipio',
            'div:has-text("Prestador") + div .municipio'
        ]),
        
        # Dados do Tomador
        "tomador_razao_social": try_extract(page, [
            '#tomador-nome',
            '[data-field="tomador.nome"]',
            '.tomador-nome',
            '.razao-social-tomador',
            'div:has-text("Tomador") + div .nome',
            'h3:has-text("Tomador") ~ div .nome'
        ]),
        
        "tomador_cpf_cnpj": try_extract(page, [
            '#tomador-documento',
            '[data-field="tomador.documento"]',
            '.tomador-documento',
            '.tomador-cnpj',
            '.tomador-cpf',
            'div:has-text("Tomador") + div .documento',
            'h3:has-text("Tomador") ~ div .cpf',
            'h3:has-text("Tomador") ~ div .cnpj'
        ], extract_number),
        
        "tomador_municipio": try_extract(page, [
            '#tomador-municipio',
            '[data-field="tomador.municipio"]',
            '.tomador-municipio',
            'div:has-text("Tomador") + div .municipio'
        ]),
        
        # Valores
        "valor_servicos": try_extract(page, [
            '#valor-servicos',
            '[data-field="valorServicos"]',
            '.valor-servicos',
            'td:has-text("Valor dos Serviços") + td',
            'label:has-text("Valor dos Serviços") + span',
            'tr:has-text("Valor") td:last-child'
        ], extract_monetary_value),
        
        "valor_deducoes": try_extract(page, [
            '#valor-deducoes',
            '[data-field="valorDeducoes"]',
            '.valor-deducoes',
            'td:has-text("Deduções") + td',
            'label:has-text("Deduções") + span'
        ], extract_monetary_value),
        
        "base_calculo": try_extract(page, [
            '#base-calculo',
            '[data-field="baseCalculo"]',
            '.base-calculo',
            'td:has-text("Base de Cálculo") + td',
            'label:has-text("Base de Cálculo") + span'
        ], extract_monetary_value),
        
        "aliquota": try_extract(page, [
            '#aliquota',
            '[data-field="aliquota"]',
            '.aliquota',
            'td:has-text("Alíquota") + td',
            'label:has-text("Alíquota") + span'
        ]),
        
        "valor_iss": try_extract(page, [
            '#valor-iss',
            '[data-field="valorIss"]',
            '.valor-iss',
            'td:has-text("Valor do ISS") + td',
            'td:has-text("ISS") + td',
            'label:has-text("ISS") + span'
        ], extract_monetary_value),
        
        "valor_liquido": try_extract(page, [
            '#valor-liquido',
            '[data-field="valorLiquido"]',
            '.valor-liquido',
            'td:has-text("Valor Líquido") + td',
            'label:has-text("Líquido") + span'
        ], extract_monetary_value),
        
        # Retenções
        "iss_retido": try_extract(page, [
            '#iss-retido',
            '[data-field="issRetido"]',
            '.iss-retido',
            'td:has-text("ISS Retido") + td'
        ]),
        
        "valor_pis": try_extract(page, [
            '#valor-pis',
            '[data-field="valorPis"]',
            'td:has-text("PIS") + td'
        ], extract_monetary_value),
        
        "valor_cofins": try_extract(page, [
            '#valor-cofins',
            '[data-field="valorCofins"]',
            'td:has-text("COFINS") + td'
        ], extract_monetary_value),
        
        "valor_inss": try_extract(page, [
            '#valor-inss',
            '[data-field="valorInss"]',
            'td:has-text("INSS") + td'
        ], extract_monetary_value),
        
        "valor_ir": try_extract(page, [
            '#valor-ir',
            '[data-field="valorIr"]',
            'td:has-text("IR") + td',
            'td:has-text("IRRF") + td'
        ], extract_monetary_value),
        
        "valor_csll": try_extract(page, [
            '#valor-csll',
            '[data-field="valorCsll"]',
            'td:has-text("CSLL") + td'
        ], extract_monetary_value),
        
        # Outros
        "discriminacao_servicos": try_extract(page, [
            '#discriminacao',
            '[data-field="discriminacao"]',
            '.discriminacao',
            'textarea',
            '.descricao-servico',
            'td:has-text("Discriminação") + td'
        ]),
        
        "codigo_servico": try_extract(page, [
            '#codigo-servico',
            '[data-field="codigoServico"]',
            '.codigo-servico',
            'td:has-text("Código do Serviço") + td'
        ]),
        
        "situacao": try_extract(page, [
            '#situacao',
            '[data-field="situacao"]',
            '.situacao',
            '.status',
            'span.badge',
            'td:has-text("Situação") + td'
        ]),
    }
    
    # Log dos campos que não foram preenchidos (para debug)
    empty_fields = [k for k, v in data.items() if not v]
    if empty_fields:
        logger.warning(f"Campos não extraídos: {', '.join(empty_fields)}")
    
    logger.debug(f"Nota extraída: {data.get('numero_nfse', 'N/A')}")
    
    return data
