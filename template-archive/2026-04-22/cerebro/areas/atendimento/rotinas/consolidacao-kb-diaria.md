# Rotina: Consolidação KB Diária

> Analisa perguntas do dia e alimenta a base de conhecimento automaticamente.

## Schedule

`cron: 0 23 * * *` — todo dia às 23h (após o relatório de suporte)

## Passos

1. **Consultar Supabase** — perguntas das últimas 24h
2. **Identificar padrões**:
   - Perguntas feitas 3+ vezes (ou variações da mesma dúvida)
   - Respostas que foram validadas (respondidas sem escalação)
3. **Para cada padrão identificado**:
   - Verificar se já existe na base de conhecimento
   - Se não existe → criar entrada nova com:
     - Pergunta consolidada (versão limpa)
     - Resposta validada
     - Módulo/aula relacionado
     - Data de criação
     - Status: `auto-gerado` (Bruno valida depois)
   - Se já existe → atualizar contador de frequência
4. **Registrar no Supabase** — log da consolidação (quantas entradas criadas/atualizadas)

## Regras

- **Nunca sobrescrever** entrada validada pelo Bruno
- **Status `auto-gerado`** até Bruno aprovar — bot já usa, mas com flag
- **Mínimo 3 ocorrências** pra virar entrada na base (evitar ruído)

## Output

- Novas entradas na base de conhecimento (gerada do Supabase)
- Log de consolidação no Supabase
