# Formato — Estático para Feed

## Especificações Técnicas

| Parâmetro | Valor |
|-----------|-------|
| Dimensão | 1080 x 1080 px (quadrado) |
| Formato de arquivo | JPG ou PNG |
| Tamanho máximo | 30 MB |
| Proporção | 1:1 |
| Limite de texto na imagem | máx. 20% da área |
| DPI | 72 dpi (para digital) |

---

## Elementos Obrigatórios

### 1. Hook Visual
- Deve parar o scroll em < 1,5 segundos
- Opções: número grande, contraste forte, rosto humano, "antes x depois"
- O texto do hook deve ser lido em até 3 palavras
- Exemplos eficientes: "3 horas/dia", "R$4.800 economizados", "Antes → Depois"

### 2. Corpo (Subtexto)
- Máximo 2 linhas legíveis na imagem
- Completar o hook, não repetir
- Fonte: mínimo 28pt para leitura em celular

### 3. CTA (Call to Action)
- Elemento visual obrigatório: botão ou seta indicativa
- Texto: "Saiba como", "Ver como funciona", "Agendar diagnóstico"
- Localização: canto inferior direito ou centro inferior

### 4. Logo / Branding
- Logo TechFlow no canto superior direito ou inferior esquerdo
- Tamanho: 10–15% da largura
- Versão branca em fundos escuros, versão colorida em fundos claros

---

## Estrutura de Layout Recomendada

```
┌─────────────────────────────────┐
│  LOGO                           │
│                                 │
│    [ELEMENTO VISUAL DE HOOK]    │
│    (número, ícone, contraste)   │
│                                 │
│  TEXTO HOOK (grande)            │
│  subtexto complementar          │
│                                 │
│                    [BOTÃO CTA]  │
└─────────────────────────────────┘
```

---

## Dicas de Performance

✅ **O que funciona:**
- Números específicos no hook (ex: "3h → 0h", "R$4.800/mês")
- Contraste extremo (preto no branco, amarelo no escuro)
- Rosto humano olhando para o CTA (eye-tracking)
- "Antes x Depois" visual claro
- Background limpo, sem poluição visual

❌ **O que não funciona:**
- Mais de 3 cores diferentes
- Texto menor que 24pt
- Muita informação na imagem (guarda o resto para o copy da legenda)
- Bordas decorativas desnecessárias
- Stock photos genéricas de pessoas sorrindo

---

## Referência de Copy (Legenda)

O criativo captura o clique — a legenda fecha a venda.

Estrutura recomendada para a legenda:
1. Linha 1: Repete e expande o hook (primeiras 2 linhas aparecem sem expandir)
2. Parágrafo 2: A dor em detalhe
3. Parágrafo 3: Como resolvemos
4. Parágrafo 4: Prova (número ou case)
5. CTA final com link

---

## Criativos TechFlow que usam este formato

- [C002 — estatico-roi-numeros](../criativos/c002-estatico-roi.md) → ROAS 7,1x ✅
- [C005 — estatico-hook-horas](../criativos/) → ROAS 3,1x ❌ (descartado, hook fraco)

---

*Formato v1.0 | TechFlow Solutions*
