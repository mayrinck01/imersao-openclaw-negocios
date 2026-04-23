# Skill: Consolidação de Memória

**Trigger:** Cron diário às 21h BRT (00h UTC) | Também pode ser chamada manualmente

## O que faz

Revisa as notas diárias em `memory/YYYY-MM-DD.md`, extrai informações relevantes e consolida nos arquivos corretos do `cerebro/`, seguido de `git commit + push`.

## Passos

### 1. Listar notas locais
```
ls memory/*.md (exceto MEMORY.md)
```
Se não houver notas → encerrar silenciosamente.

### 2. Para cada nota, classificar e rotear

Ler o conteúdo e identificar o tipo de informação:

| Se contiver... | Gravar em |
|---|---|
| Decisão estratégica | `cerebro/empresa/decisoes/YYYY-MM.md` |
| Lição aprendida / erro / padrão | `cerebro/empresa/gestao/licoes.md` |
| Pendência nova | `cerebro/empresa/gestao/pendencias.md` |
| Projeto criado ou atualizado | `cerebro/empresa/gestao/projetos.md` |
| Pessoa nova ou mudança de papel | `cerebro/empresa/contexto/equipe.md` |
| Métrica atualizada | `cerebro/empresa/contexto/metricas.md` |
| Informação de área específica | `cerebro/areas/[area]/contexto/geral.md` |

**Regra:** Só consolidar o que tem valor persistente. Conversas genéricas, testes e rascunhos sem conclusão → descartar.

### 3. Gravar nos arquivos corretos

- Append no arquivo destino com data e contexto
- Formato: `## [YYYY-MM-DD] Título breve` seguido do conteúdo

### 4. Deletar as notas processadas

```bash
rm memory/YYYY-MM-DD.md
```

Só deletar após confirmar que o conteúdo foi gravado no destino.

### 5. Commit + Push

```bash
cd second-brain/
git add -A
git commit -m "consolidação: notas de YYYY-MM-DD"
git push origin main
```

Se o push falhar: tentar 1x mais. Se falhar 2x → alertar no tópico ⚙️ Operações (topic_id: 6).

### 6. Relatório final

Enviar resumo no tópico ⚙️ Operações (topic_id: 6):

```
🧠 Consolidação concluída — DD/MM/YYYY
• X notas processadas
• Arquivos atualizados: [lista]
• Push: ✅ ok
```

Se não houver nada para consolidar:
```
🧠 Consolidação — DD/MM/YYYY: nenhuma nota nova.
```
