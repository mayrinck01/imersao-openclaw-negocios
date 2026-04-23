# Skill: Consulta Base de Conhecimento

> Busca na base de conhecimento e nas transcrições do curso antes de responder qualquer pergunta.

## Quando executar

**Toda vez que um aluno fizer uma pergunta.** Sem exceção. O bot nunca responde "de cabeça" — sempre consulta primeiro.

## Passos

1. **Receber a pergunta** do aluno
2. **Buscar no workspace da Amora** — base de conhecimento oficial (KB + documentação interna do produto)
   - Documentação técnica, guias, configurações, troubleshooting
   - Fonte mais confiável — sempre consultar primeiro
3. **Buscar na base de conhecimento consolidada** — FAQ validado pelo Bruno + perguntas consolidadas do Supabase
   - Base gerada automaticamente a partir das perguntas repetidas mapeadas no Supabase
   - Busca por similaridade no título + conteúdo
4. **Buscar nas transcrições** — conteúdo completo das aulas do curso
   - Transcrições indexadas por módulo e aula
   - Busca semântica por relevância
5. **Se encontrou resposta validada** → usar como base, adaptar pro contexto do aluno
6. **Se encontrou só nas transcrições** → responder com referência ao módulo/aula
7. **Se não encontrou em nenhuma fonte** → executar skill `registro-duvida-pendente`

## Fontes (ordem de prioridade)

1. Workspace da Amora (documentação oficial, KB, guias internos)
2. Base de conhecimento consolidada (respostas já validadas, geradas do Supabase)
3. Transcrições do curso (conteúdo original)
4. Conhecimento geral do modelo (última instância)

## Output

Resposta seguindo o padrão do SOUL.md:
- Contexto → Resposta → Fonte → Prompt pronto (pra colar no agente) → Próximo passo
