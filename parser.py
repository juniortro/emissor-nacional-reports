"""
Módulo de parsing de dados das NFSe.
Extrai informações estruturadas das páginas de nota - SELETORES AJUSTADOS.
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
        return "0,00"
    
    # Remove tudo exceto números, vírgula e ponto
    value = re.sub(r'[^\d,.]', '', text)
    
    # Mantém formato BR (1.234,56)
    return value if value else "0,00"


def extract_note_data(page: Page) -> dict:
    """
    Extrai todos os dados relevantes de uma NFSe.
    Seletores ajustados baseados na estrutura REAL do Emissor Nacional.
    """
    
    logger.debug("Extraindo dados da nota...")
    
    data = {}
    
    # === IDENTIFICAÇÃO DA NFS-E ===
    # Painel: "Identificação da NFS-e"
    try:
        # Chave de acesso - linha 184
        chave_elem = page.query_selector('h3.panel-title:has-text("Identificação da NFS-e") + .panel-body .form-group:has-text("Chave de acesso") span.texto')
        data['chave_acesso'] = clean_text(chave_elem.inner_text()) if chave_elem else ""
    except Exception as e:
        logger.debug(f"Erro ao extrair chave_acesso: {e}")
        data['chave_acesso'] = ""
    
    try:
        # Data de geração - linha 187
        data_elem = page.query_selector('h3.panel-title:has-text("Identificação da NFS-e") + .panel-body .form-group:has-text("Data de geração") span.texto')
        data['data_geracao'] = clean_text(data_elem.inner_text()) if data_elem else ""
    except Exception as e:
        logger.debug(f"Erro ao extrair data_geracao: {e}")
        data['data_geracao'] = ""
    
    # === IDENTIFICAÇÃO DO DPS ===
    # Painel: "Identificação do DPS"
    try:
        # Número do DPS - linha 202
        numero_elem = page.query_selector('h3.panel-title:has-text("Identificação do DPS") + .panel-body .form-group:has-text("Número") span.texto')
        data['numero_dps'] = clean_text(numero_elem.inner_text()) if numero_elem else ""
        # Assume numero da NFSe como numero do DPS para compatibilidade
        data['numero_nfse'] = data['numero_dps']
    except Exception as e:
        logger.debug(f"Erro ao extrair numero_dps: {e}")
        data['numero_dps'] = ""
    
    try:
        # Série - linha 205
        serie_elem = page.query_selector('h3.panel-title:has-text("Identificação do DPS") + .panel-body .form-group:has-text("Série") span.texto')
        data['serie'] = clean_text(serie_elem.inner_text()) if serie_elem else ""
    except Exception as e:
        logger.debug(f"Erro ao extrair serie: {e}")
        data['serie'] = ""
    
    try:
        # Data de emissão - linha 208
        data_emissao_elem = page.query_selector('h3.panel-title:has-text("Identificação do DPS") + .panel-body .form-group:has-text("Data de emissão") span.texto')
        data['data_emissao'] = clean_text(data_emissao_elem.inner_text()) if data_emissao_elem else ""
    except Exception as e:
        logger.debug(f"Erro ao extrair data_emissao: {e}")
        data['data_emissao'] = ""
    
    # === EMITENTE (PRESTADOR) ===
    # Dentro da aba NFS-e (id="nfse"), painel "Emitente"
    try:
        # Razão Social - linha 231
        razao_elem = page.query_selector('h3.panel-title:has-text("Emitente") + .panel-body .form-group:has-text("Razão Social") span.texto')
        data['prestador_razao_social'] = clean_text(razao_elem.inner_text()) if razao_elem else ""
    except Exception as e:
        logger.debug(f"Erro ao extrair prestador_razao_social: {e}")
        data['prestador_razao_social'] = ""
    
    try:
        # CNPJ - linha 236
        cnpj_elem = page.query_selector('h3.panel-title:has-text("Emitente") + .panel-body .form-group:has-text("CNPJ") span.texto')
        data['prestador_cnpj'] = extract_number(cnpj_elem.inner_text()) if cnpj_elem else ""
    except Exception as e:
        logger.debug(f"Erro ao extrair prestador_cnpj: {e}")
        data['prestador_cnpj'] = ""
    
    try:
        # Endereço (contém município) - linha 255
        endereco_elem = page.query_selector('h3.panel-title:has-text("Emitente") + .panel-body .form-group:has-text("Endereço") span.texto')
        if endereco_elem:
            endereco_text = endereco_elem.inner_text()
            # Extrai município (última parte antes de /UF)
            match = re.search(r'([\w\s]+)/([A-Z]{2})', endereco_text)
            if match:
                data['prestador_municipio'] = match.group(1).strip()
            else:
                data['prestador_municipio'] = ""
        else:
            data['prestador_municipio'] = ""
    except Exception as e:
        logger.debug(f"Erro ao extrair prestador_municipio: {e}")
        data['prestador_municipio'] = ""
    
    # === TOMADOR ===
    # Verifica se tomador está identificado
    tomador_nao_identificado = page.query_selector('.panel-body:has-text("O tomador e o intermediário não foram identificados")')
    
    if tomador_nao_identificado:
        data['tomador_razao_social'] = "Não identificado"
        data['tomador_cpf_cnpj'] = ""
        data['tomador_municipio'] = ""
    else:
        # Tenta estratégia 1: Painel explícito "Tomador" (similar ao Emitente)
        try:
            # Razão Social
            tomador_razao_elem = page.query_selector('h3.panel-title:has-text("Tomador") + .panel-body .form-group:has-text("Razão Social") span.texto')
            if not tomador_razao_elem:
                # Tenta "Nome"
                tomador_razao_elem = page.query_selector('h3.panel-title:has-text("Tomador") + .panel-body .form-group:has-text("Nome") span.texto')
            
            data['tomador_razao_social'] = clean_text(tomador_razao_elem.inner_text()) if tomador_razao_elem else ""
        except Exception:
            data['tomador_razao_social'] = ""

        try:
            # CPF/CNPJ
            tomador_doc_elem = page.query_selector('h3.panel-title:has-text("Tomador") + .panel-body .form-group:has-text("CNPJ") span.texto')
            if not tomador_doc_elem:
                 tomador_doc_elem = page.query_selector('h3.panel-title:has-text("Tomador") + .panel-body .form-group:has-text("CPF") span.texto')
            
            data['tomador_cpf_cnpj'] = extract_number(tomador_doc_elem.inner_text()) if tomador_doc_elem else ""
        except Exception:
            data['tomador_cpf_cnpj'] = ""

        try:
            # Endereço/Município
            tomador_mun_elem = page.query_selector('h3.panel-title:has-text("Tomador") + .panel-body .form-group:has-text("Município") span.texto')
            if not tomador_mun_elem:
                 # Tenta pegar do endereço completo se não tiver campo específico
                 tomador_end_elem = page.query_selector('h3.panel-title:has-text("Tomador") + .panel-body .form-group:has-text("Endereço") span.texto')
                 if tomador_end_elem:
                     end_text = tomador_end_elem.inner_text()
                     match = re.search(r'([\w\s]+)/([A-Z]{2})', end_text)
                     if match:
                         data['tomador_municipio'] = match.group(1).strip()
                     else:
                         data['tomador_municipio'] = ""
                 else:
                     data['tomador_municipio'] = ""
            else:
                data['tomador_municipio'] = clean_text(tomador_mun_elem.inner_text())
        except Exception:
            data['tomador_municipio'] = ""

        # Estratégia 2: Fallback (código antigo / genérico) se dados continuam vazios
        if not data.get('tomador_razao_social'):
             try:
                tomador_razao_elem = page.query_selector('.pnlSujeito .form-group:has-text("Razão Social") span.texto, .pnlSujeito .form-group:has-text("Nome") span.texto')
                if tomador_razao_elem:
                    data['tomador_razao_social'] = clean_text(tomador_razao_elem.inner_text())
             except: pass

        if not data.get('tomador_cpf_cnpj'):
             try:
                tomador_doc_elem = page.query_selector('.pnlSujeito .form-group:has-text("CNPJ") span.texto, .pnlSujeito .form-group:has-text("CPF") span.texto')
                if tomador_doc_elem:
                    data['tomador_cpf_cnpj'] = extract_number(tomador_doc_elem.inner_text())
             except: pass

        if not data.get('tomador_municipio'):
             try:
                tomador_mun_elem = page.query_selector('.pnlSujeito .form-group:has-text("Município") span.texto')
                if tomador_mun_elem:
                    data['tomador_municipio'] = clean_text(tomador_mun_elem.inner_text())
             except: pass
    
    # === VALORES - TRIBUTAÇÃO MUNICIPAL ===
    # Painel "Tributação Municipal"
    try:
        # Valor do Serviço - linha 296
        valor_servico_elem = page.query_selector('h3.panel-title:has-text("Tributação Municipal") + .panel-body .form-group:has-text("Valor do Serviço") span.numero')
        data['valor_servicos'] = clean_text(valor_servico_elem.inner_text()) if valor_servico_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair valor_servicos: {e}")
        data['valor_servicos'] = "0,00"
    
    try:
        # Desconto incondicionado - linha 300
        desconto_elem = page.query_selector('h3.panel-title:has-text("Tributação Municipal") + .panel-body .form-group:has-text("Desconto") span.numero')
        data['valor_desconto'] = clean_text(desconto_elem.inner_text()) if desconto_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair valor_desconto: {e}")
        data['valor_desconto'] = "0,00"
    
    try:
        # Total Deduções/Reduções - linha 308
        deducoes_elem = page.query_selector('h3.panel-title:has-text("Tributação Municipal") + .panel-body .form-group:has-text("Deduções") span.numero')
        data['valor_deducoes'] = clean_text(deducoes_elem.inner_text()) if deducoes_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair valor_deducoes: {e}")
        data['valor_deducoes'] = "0,00"
    
    try:
        # Base de Cálculo - linha 316
        base_elem = page.query_selector('h3.panel-title:has-text("Tributação Municipal") + .panel-body .form-group:has-text("Base de Cálculo") span.numero')
        data['base_calculo'] = clean_text(base_elem.inner_text()) if base_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair base_calculo: {e}")
        data['base_calculo'] = "0,00"
    
    try:
        # Alíquota - linha 324
        aliquota_elem = page.query_selector('h3.panel-title:has-text("Tributação Municipal") + .panel-body .form-group:has-text("Alíquota") span.numero')
        data['aliquota'] = clean_text(aliquota_elem.inner_text()) if aliquota_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair aliquota: {e}")
        data['aliquota'] = "0,00"
    
    try:
        # Valor do ISSQN - linha 330
        iss_elem = page.query_selector('h3.panel-title:has-text("Tributação Municipal") + .panel-body .form-group:has-text("Valor do ISSQN") span.numero')
        data['valor_iss'] = clean_text(iss_elem.inner_text()) if iss_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair valor_iss: {e}")
        data['valor_iss'] = "0,00"
    
    try:
        # Retenção - linha 336
        retencao_elem = page.query_selector('h3.panel-title:has-text("Tributação Municipal") + .panel-body .form-group:has-text("Retenção") span.texto')
        data['iss_retido'] = clean_text(retencao_elem.inner_text()) if retencao_elem else ""
    except Exception as e:
        logger.debug(f"Erro ao extrair iss_retido: {e}")
        data['iss_retido'] = ""
    
    # === TRIBUTOS FEDERAIS ===
    # Aba "Outros Tributos" (id="tributacao"), painel "Tributação Federal"
    try:
        # PIS - Valor do imposto - linha 450
        pis_elem = page.query_selector('h3.panel-title:has-text("Tributação Federal") + .panel-body .form-group:has-text("PIS - Valor do imposto") span.numero')
        data['valor_pis'] = clean_text(pis_elem.inner_text()) if pis_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair valor_pis: {e}")
        data['valor_pis'] = "0,00"
    
    try:
        # COFINS - Valor do imposto - linha 462
        cofins_elem = page.query_selector('h3.panel-title:has-text("Tributação Federal") + .panel-body .form-group:has-text("COFINS - Valor do imposto") span.numero')
        data['valor_cofins'] = clean_text(cofins_elem.inner_text()) if cofins_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair valor_cofins: {e}")
        data['valor_cofins'] = "0,00"
    
    try:
        # INSS - Valor Retido CP (Contribuição Previdenciária) - linha 487
        inss_elem = page.query_selector('h3.panel-title:has-text("Tributação Federal") + .panel-body .form-group:has-text("Valor Retido CP") span.numero')
        data['valor_inss'] = clean_text(inss_elem.inner_text()) if inss_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair valor_inss: {e}")
        data['valor_inss'] = "0,00"
    
    try:
        # IR - Valor Retido IRRF - linha 475
        ir_elem = page.query_selector('h3.panel-title:has-text("Tributação Federal") + .panel-body .form-group:has-text("Valor Retido IRRF") span.numero')
        data['valor_ir'] = clean_text(ir_elem.inner_text()) if ir_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair valor_ir: {e}")
        data['valor_ir'] = "0,00"
    
    try:
        # CSLL - Valor Retido CSLL - linha 481
        csll_elem = page.query_selector('h3.panel-title:has-text("Tributação Federal") + .panel-body .form-group:has-text("Valor Retido CSLL") span.numero')
        data['valor_csll'] = clean_text(csll_elem.inner_text()) if csll_elem else "0,00"
    except Exception as e:
        logger.debug(f"Erro ao extrair valor_csll: {e}")
        data['valor_csll'] = "0,00"
    
    # === SERVIÇO ===
    # Aba "Serviço" (id="servicos"), painel "Serviço Prestado"
    try:
        # Município de Incidência - linha 277 (na aba NFS-e)
        municipio_elem = page.query_selector('h3.panel-title:has-text("Tributação Municipal") + .panel-body .form-group:has-text("Município de Incidência") span.texto')
        data['municipio_incidencia'] = clean_text(municipio_elem.inner_text()) if municipio_elem else ""
    except Exception as e:
        logger.debug(f"Erro ao extrair municipio_incidencia: {e}")
        data['municipio_incidencia'] = ""
    
    try:
        # Código de Tributação Nacional - linha 379
        codigo_elem = page.query_selector('h3.panel-title:has-text("Serviço Prestado") + .panel-body .form-group:has-text("Código de Tributação Nacional") span.texto')
        if codigo_elem:
            codigo_text = codigo_elem.inner_text()
            # Extrai apenas o código (antes do hífen)
            match = re.match(r'(\d+)', codigo_text)
            data['codigo_servico'] = match.group(1) if match else codigo_text
        else:
            data['codigo_servico'] = ""
    except Exception as e:
        logger.debug(f"Erro ao extrair codigo_servico: {e}")
        data['codigo_servico'] = ""
    
    try:
        # Descrição do serviço - linha 389
        desc_elem = page.query_selector('h3.panel-title:has-text("Serviço Prestado") + .panel-body .form-group:has-text("Descrição do serviço") span.texto')
        data['discriminacao_servicos'] = clean_text(desc_elem.inner_text()) if desc_elem else ""
    except Exception as e:
        logger.debug(f"Erro ao extrair discriminacao_servicos: {e}")
        data['discriminacao_servicos'] = ""
    
    # === SITUAÇÃO ===
    # Painel "Outras Informações" - linha 352
    try:
        situacao_elem = page.query_selector('h3.panel-title:has-text("Outras Informações") + .panel-body .form-group:has-text("Situação da NFS-e") span.texto')
        data['situacao'] = clean_text(situacao_elem.inner_text()) if situacao_elem else ""
    except Exception as e:
        logger.debug(f"Erro ao extrair situacao: {e}")
        data['situacao'] = ""
    
    # Log dos campos vazios para debug
    empty_fields = [k for k, v in data.items() if not v or v == "0,00"]
    if empty_fields:
        logger.debug(f"Campos vazios/zero: {', '.join(empty_fields)}")
    
    logger.info(f"Nota extraída: DPS {data.get('numero_dps', 'N/A')}")
    
    return data
