# Skill: Registro de Dúvida Pendente

> Registra dúvidas que o bot não sabe responder e escala pro Bruno.

## Quando executar

Quando a skill `consulta-base-conhecimento` não encontrou resposta confiável na base de conhecimento nem nas transcrições do curso.

## Passos

1. **Responder o que sabe** — nunca deixar o aluno sem resposta
2. **Marcar @Bruno** na conversa com a dúvida específica
3. **Registrar no Supabase** — tabela `duvidas-pendentes`:
   - Pergunta original do aluno
   - Contexto (canal, horário, módulo relacionado se identificado)
   - Status: `pendente`
   - Data de registro
4. **Avisar o aluno**: "Vou verificar com o Bruno e te retorno"

## Regras

- **Nunca inventar** resposta quando não sabe
- **Nunca prometer** prazo de retorno específico
- **Sempre registrar** — mesmo que pareça simples. Se não tá na base, registra.

## Output

- Mensagem pro aluno (transparente, com próximo passo)
- Registro no Supabase (dúvida pendente)
- Menção @Bruno no canal
