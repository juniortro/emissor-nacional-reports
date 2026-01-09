# Exportador de NFSe - Emissor Nacional

Ferramenta de automação RPA para extração de dados de Notas Fiscais de Serviço Eletrônicas (NFSe) do portal Emissor Nacional, com geração de relatórios em Excel.

## 📋 Características

- ✅ Automação completa via navegador (Playwright)
- ✅ Login seguro no Emissor Nacional
- ✅ Coleta de todas as notas de um período
- ✅ Paginação automática
- ✅ Extração de todos os campos relevantes
- ✅ Geração de Excel formatado e filtrável
- ✅ Logs detalhados para auditoria
- ✅ Tratamento de erros com retry automático
- ✅ Execução em modo headless ou visível

## 🏗️ Arquitetura

```
nfse-nacional-report/
├── main.py                # Orquestrador principal
├── auth.py                # Módulo de autenticação
├── scraper.py             # Coleta e navegação
├── parser.py              # Extração de dados
├── excel.py               # Geração de relatórios
├── config.py              # Configurações
├── requirements.txt       # Dependências
├── .env.example           # Template de configuração
├── .env                   # Credenciais (NÃO versionado)
└── README.md              # Esta documentação
```

## 🚀 Instalação

### 1. Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 2. Clonar ou criar o projeto

```bash
cd /home/dev2/workspace/cloudpark-info-work/POC/nfse-nacional-report
```

### 3. Criar ambiente virtual

```bash
python3 -m venv venv
```

### 4. Ativar ambiente virtual

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 5. Instalar dependências

```bash
pip install -r requirements.txt
```

### 6. Instalar navegadores do Playwright

```bash
playwright install chromium
```

## ⚙️ Configuração

### 1. Criar arquivo de configuração

Copie o arquivo de exemplo e edite com suas credenciais:

```bash
cp .env.example .env
```

### 2. Editar `.env`

```env
# Credenciais do Emissor Nacional
NFSE_USER=seu_cpf_ou_cnpj
NFSE_PASSWORD=sua_senha

# Período de busca (formato: YYYY-MM-DD)
DATA_INICIO=2026-01-01
DATA_FIM=2026-01-31

# Configurações do navegador
HEADLESS=false          # true para execução sem interface gráfica
TIMEOUT=30000           # Timeout em milissegundos

# Configurações de comportamento
DELAY_ENTRE_NOTAS=1.5   # Delay entre notas (segundos)
MAX_RETRIES=3           # Máximo de tentativas em caso de erro
```

## 🎯 Uso

### Execução básica

```bash
python main.py
```

ou

```bash
python3 main.py
```

### Execução com log visível

Por padrão, os logs são salvos em arquivo e exibidos no console. Para acompanhar a execução:

```bash
python main.py
```

### Modo headless (sem interface gráfica)

Edite `.env` e defina:
```env
HEADLESS=true
```

## 📊 Saída

### Arquivos gerados

1. **Excel**: `NFSe_Report_YYYYMMDD_HHMMSS.xlsx`
   - Planilha formatada com todas as notas
   - Cabeçalho destacado
   - Colunas ajustadas
   - Filtros automáticos

2. **Log**: `nfse_export_YYYYMMDD_HHMMSS.log`
   - Registro detalhado da execução
   - Útil para debug e auditoria

### Campos extraídos

- **Identificação**: Número, Data de Emissão, Código de Verificação
- **Prestador**: Razão Social, CNPJ, Município
- **Tomador**: Razão Social, CPF/CNPJ, Município
- **Valores**: Serviços, Deduções, Base de Cálculo, Alíquota, ISS
- **Retenções**: PIS, COFINS, INSS, IR, CSLL
- **Outros**: Código do Serviço, Discriminação, Situação

## 🔧 Ajustes Necessários

⚠️ **IMPORTANTE**: Os seletores CSS/XPath nos módulos são **GENÉRICOS** e precisam ser ajustados após inspeção do site real.

### Onde ajustar

1. **auth.py** (linhas 62-89)
   - Seletores dos campos de login
   - Ajustar após inspecionar a página de login

2. **scraper.py** (linhas 32-105)
   - Seletores da tabela de resultados
   - Seletores de paginação
   - Ajustar após inspecionar a página de consulta

3. **parser.py** (linhas 76-269)
   - Seletores de cada campo da nota
   - Ajustar após inspecionar a página de detalhe da nota

### Como ajustar

1. Execute o script com `HEADLESS=false`
2. Quando o navegador abrir, pressione **F12** (DevTools)
3. Inspecione os elementos da página
4. Copie os seletores corretos (ID, classe, nome, etc.)
5. Substitua nos arquivos Python

## 🐛 Troubleshooting

### Erro: "Campo de usuário não encontrado"

**Solução**: Ajuste os seletores em `auth.py` conforme o site real.

### Erro: "Nenhuma nota encontrada"

**Possíveis causas**:
1. Período sem notas emitidas
2. Seletores da tabela incorretos (ajuste em `scraper.py`)
3. Formulário de filtros não foi preenchido corretamente

### Erro: "Campos não extraídos"

**Solução**: Ajuste os seletores em `parser.py` para os campos específicos que falharam (o log indica quais).

### Navegador não abre

**Solução**:
```bash
playwright install chromium --force
```

### Erro de timeout

**Solução**: Aumente o `TIMEOUT` no arquivo `.env`:
```env
TIMEOUT=60000
```

## 📝 Melhores Práticas

1. **Teste primeiro com período curto** (ex: 1 semana)
2. **Execute com `HEADLESS=false`** na primeira vez para observar
3. **Ajuste os delays** se o site for lento
4. **Monitore os logs** para identificar problemas
5. **Faça backup** dos arquivos gerados

## 🔒 Segurança

- ✅ Credenciais armazenadas em `.env` (ignorado pelo git)
- ✅ Sem hardcoding de senhas
- ✅ Usa as mesmas permissões do usuário autenticado
- ✅ Não burla segurança ou autenticação
- ✅ Apenas automatiza ações manuais

## 🚧 Próximas Melhorias

- [ ] Exportação para CSV
- [ ] Filtros por prestador/tomador
- [ ] Execução agendada (cron)
- [ ] Interface gráfica (GUI)
- [ ] Download de PDFs das notas
- [ ] Integração com sistemas contábeis

## 📄 Licença

Este projeto é para uso interno e automação de processos legítimos. Respeite os Termos de Uso do Emissor Nacional.

## 🤝 Contribuição

Para ajustar seletores ou melhorar a ferramenta:

1. Teste as alterações localmente
2. Documente as mudanças
3. Atualize este README se necessário

## 📞 Suporte

Em caso de dúvidas ou problemas:

1. Verifique os logs gerados
2. Consulte a seção Troubleshooting
3. Valide os seletores com DevTools (F12)

---

**Desenvolvido com** 🐍 Python + 🎭 Playwright
