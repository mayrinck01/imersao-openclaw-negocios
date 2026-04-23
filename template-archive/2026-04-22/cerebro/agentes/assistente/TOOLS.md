# TOOLS.md — Ferramentas Conectadas

## Ferramentas Ativas

### 1. Google Sheets (Planilha de Vendas)
- **Uso:** Relatório de vendas, métricas de produto
- **Acesso:** Planilha com link público (viewer)
- **Como ler:** Export CSV via URL pública

### 2. GitHub (Second Brain)
- **Uso:** Repositório de contexto da empresa — fonte de verdade
- **Acesso:** Personal Access Token
- **Repo:** `empresa-exemplo/second-brain`

### 3. WhatsApp / Telegram (Comunicação)
- **Uso:** Canal de comunicação com a equipe
- **Acesso:** Via OpenClaw (canal configurado)

## Ferramentas Planejadas

| Ferramenta | O que falta | Prioridade |
|------------|-------------|------------|
| Meta Ads API | Token + Account ID | Alta |
| Hotmart (vendas) | API key | Alta |
| Crisp (suporte) | Plugin token | Média |

## Regras de Uso
- Dados da planilha de vendas → ler do CSV em `dados/vendas.csv` ou export direto
- Dados de leads → ler de `dados/leads.csv`
- Contexto → sempre do repositório (`second-brain/`)
- **Nunca** guardar credenciais em arquivos do repositório (usar `.env` local)
