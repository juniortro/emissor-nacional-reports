# 🚀 Início Rápido - Exportador NFSe

## Instalação Automática

```bash
./install.sh
```

## Instalação Manual

### 1. Ativar ambiente virtual
```bash
source venv/bin/activate
```

### 2. Instalar dependências (se ainda não instalou)
```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuração

### 1. Copiar arquivo de configuração
```bash
cp .env.example .env
```

### 2. Editar credenciais
```bash
nano .env
```

Altere:
- `NFSE_USER` → seu CPF/CNPJ
- `NFSE_PASSWORD` → sua senha
- `DATA_INICIO` e `DATA_FIM` → período desejado

## Execução

```bash
# Com ambiente virtual ativado
python main.py

# Ou diretamente
./main.py
```

## Primeiro Uso

1. **Execute com interface gráfica** para ver o que está acontecendo:
   ```env
   HEADLESS=false
   ```

2. **Use período curto** para testar (ex: 1 semana)

3. **Ajuste os seletores** em `auth.py`, `scraper.py` e `parser.py` conforme necessário

## Arquivos Gerados

- `NFSe_Report_YYYYMMDD_HHMMSS.xlsx` → Relatório Excel
- `nfse_export_YYYYMMDD_HHMMSS.log` → Log da execução

## Ajustes Necessários

⚠️ **Os seletores CSS precisam ser ajustados após inspeção do site real!**

### Como ajustar:

1. Execute com `HEADLESS=false`
2. Pressione **F12** quando o navegador abrir
3. Inspecione os elementos (clique no ícone 🔍)
4. Copie os seletores corretos
5. Edite os arquivos Python:
   - **auth.py** → campos de login
   - **scraper.py** → tabela de notas e paginação
   - **parser.py** → campos da nota

## Comandos Úteis

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Desativar ambiente virtual
deactivate

# Ver estrutura do projeto
ls -lh

# Ver logs da última execução
ls -lt *.log | head -1 | xargs cat

# Ver último Excel gerado
ls -lt *.xlsx | head -1 | awk '{print $NF}'
```

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError` | `source venv/bin/activate && pip install -r requirements.txt` |
| Navegador não abre | `playwright install chromium --force` |
| Campos não extraídos | Ajustar seletores em `parser.py` (veja logs) |
| Timeout | Aumentar `TIMEOUT` em `.env` |
| Login falha | Ajustar seletores em `auth.py` |

## Estrutura do Código

```
main.py       → Ponto de entrada, orquestra tudo
├── config.py     → Carrega configurações do .env
├── auth.py       → Faz login no site
├── scraper.py    → Navega e coleta notas
├── parser.py     → Extrai campos de cada nota
└── excel.py      → Gera relatório formatado
```

## Variáveis em Inglês

✅ Todos os nomes de variáveis, funções e classes estão em **inglês**
✅ Comentários e documentação estão em **português**

## Dicas

💡 **Comece simples**: Teste com 1 semana de notas primeiro
💡 **Use modo visual**: `HEADLESS=false` para ver o que acontece
💡 **Monitore logs**: Acompanhe o arquivo `.log` gerado
💡 **Screenshots**: Em caso de erro, o sistema salva `erro_login.png`
💡 **Backup**: Guarde os Excel gerados em local seguro

## Próximos Passos

Depois de funcionar com sucesso:

1. ✅ Ajustar delays conforme performance do site
2. ✅ Testar com períodos maiores
3. ✅ Configurar execução agendada (cron)
4. ✅ Adicionar filtros personalizados
5. ✅ Exportar também para CSV

## Suporte

📖 Documentação completa: `README.md`
📝 Logs detalhados: `*.log`
🐛 Debug: Execute com `HEADLESS=false` e pressione F12

---

**Bom uso! 🎉**
