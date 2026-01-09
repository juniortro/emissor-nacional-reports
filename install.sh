#!/bin/bash

# Script de instalação do Exportador de NFSe

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     Instalação - Exportador de NFSe - Emissor Nacional   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8 ou superior."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"
echo ""

# Verifica se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Execute este script no diretório do projeto"
    exit 1
fi

# Ativa ambiente virtual se já existir, senão cria um novo
if [ -d "venv" ]; then
    echo "📦 Ambiente virtual já existe"
else
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

echo ""
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

echo ""
echo "📥 Instalando dependências Python..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências"
    exit 1
fi
echo "✅ Dependências instaladas"

echo ""
echo "🌐 Instalando navegadores do Playwright..."
playwright install chromium

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar navegadores"
    exit 1
fi
echo "✅ Navegadores instalados"

echo ""
echo "⚙️  Verificando arquivo de configuração..."
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env a partir do exemplo..."
    cp .env.example .env
    echo "✅ Arquivo .env criado"
    echo ""
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais:"
    echo "   nano .env"
    echo "   ou"
    echo "   vim .env"
else
    echo "✅ Arquivo .env já existe"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║               INSTALAÇÃO CONCLUÍDA COM SUCESSO            ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Configure suas credenciais:"
echo "   nano .env"
echo ""
echo "2. Ative o ambiente virtual:"
echo "   source venv/bin/activate"
echo ""
echo "3. Execute o exportador:"
echo "   python main.py"
echo ""
