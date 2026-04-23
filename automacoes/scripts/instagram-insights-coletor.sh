#!/bin/bash
# Instagram Insights — Coleta automática mensal
# Cake & Co | @cakecooficial

set -u

export OP_SERVICE_ACCOUNT_TOKEN=$(cat /root/.openclaw/credentials/1password-token.txt)
export GOG_KEYRING_PASSWORD=""

# IDs fixos
IG_ID="17841401308047001"
PAGE_ID="112027372209332"

# Datas
PT_FILTER="python3 /root/workspaces/cake-brain/automacoes/scripts/filter_pt.py"
PT_AUDIT="python3 /root/workspaces/cake-brain/automacoes/scripts/audit_pt.py"
TODAY=$(date +"%d/%m/%Y")
TIMESTAMP=$(date +"%Y-%m-%d")
REPORT_DIR="/root/workspaces/cake-brain/relatorios/instagram"
mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/instagram-$TIMESTAMP.md"

read_1p_field() {
  local item="$1"
  local field="$2"
  op item get "$item" --vault BigDog --fields "$field" --reveal 2>/dev/null || true
}

json_has_error() {
  python3 -c 'import json,sys
raw=sys.stdin.read().strip()
if not raw:
    raise SystemExit(1)
try:
    data=json.loads(raw)
except Exception:
    raise SystemExit(1)
raise SystemExit(0 if isinstance(data, dict) and data.get("error") else 1)
'
}

json_error_message() {
  python3 -c 'import json,sys
raw=sys.stdin.read().strip()
msg="Erro desconhecido na API"
try:
    data=json.loads(raw)
    err=data.get("error", {}) if isinstance(data, dict) else {}
    msg=err.get("message") or msg
except Exception:
    pass
print(msg)
'
}

json_extract_basic() {
  python3 -c 'import json,sys
raw=sys.stdin.read().strip()
try:
    data=json.loads(raw)
except Exception:
    print("N/D\nN/D\nN/D")
    raise SystemExit
print(data.get("followers_count", "N/D"))
print(data.get("follows_count", "N/D"))
print(data.get("media_count", "N/D"))
'
}

json_extract_total_metric() {
  local metric="$1"
  python3 -c 'import json,sys
metric=sys.argv[1]
raw=sys.stdin.read().strip()
try:
    data=json.loads(raw)
except Exception:
    print("N/D")
    raise SystemExit
for item in data.get("data", []):
    if item.get("name") == metric:
        print(item.get("total_value", {}).get("value", "N/D"))
        raise SystemExit
print("N/D")
' "$metric"
}

json_extract_follows_breakdown() {
  python3 -c 'import json,sys
raw=sys.stdin.read().strip()
try:
    data=json.loads(raw)
except Exception:
    print("N/D,N/D,N/D")
    raise SystemExit
follows=0
unfollows=0
found=False
for item in data.get("data", []):
    total_value=item.get("total_value", {})
    for breakdown in total_value.get("breakdowns", []):
        for result in breakdown.get("results", []):
            dims=result.get("dimension_values", [])
            val=result.get("value", 0)
            if "FOLLOW" in str(dims):
                follows += val
                found=True
            if "UNFOLLOW" in str(dims):
                unfollows += val
                found=True
if not found:
    print("N/D,N/D,N/D")
else:
    print(f"{follows},{unfollows},{follows-unfollows}")
'
}

json_extract_posts_table() {
  python3 -c 'import json,sys
raw=sys.stdin.read().strip()
try:
    data=json.loads(raw)
except Exception:
    print("| N/D | N/D | Não foi possível carregar os posts recentes |")
    raise SystemExit
posts=data.get("data", [])
if not posts:
    print("| N/D | N/D | Nenhum post retornado pela API |")
    raise SystemExit
rows=[]
for post in posts[:10]:
    dt=(post.get("timestamp") or "")[:10] or "N/D"
    likes=post.get("like_count", 0)
    comments=post.get("comments_count", 0)
    caption=(post.get("caption") or "Sem legenda").replace("\n", " ").strip()
    caption=caption[:60] + ("..." if len(caption) > 60 else "")
    rows.append(f"| {dt} | {likes:,} ❤️ {comments:,} 💬 | {caption} |")
print("\n".join(rows))
'
}

fmt_num() {
  local value="${1:-N/D}"
  if [[ "$value" =~ ^[0-9]+$ ]]; then
    printf "%'.0f" "$value" 2>/dev/null || printf "%s" "$value"
  else
    printf "%s" "$value"
  fi
}

load_token_from_file() {
  python3 - <<'PY'
import json, pathlib
path = pathlib.Path('/root/.openclaw/credentials/instagram-page-token.json')
if not path.exists():
    raise SystemExit
try:
    data = json.loads(path.read_text())
except Exception:
    raise SystemExit
print(data.get('page_token', ''))
PY
}

BASIC_FIELDS_URL="username,followers_count,follows_count,media_count,biography"

try_basic_with_token() {
  local candidate_token="$1"
  curl -s "https://graph.facebook.com/v19.0/$IG_ID?fields=$BASIC_FIELDS_URL&access_token=$candidate_token" 2>/dev/null
}

# Ordem de preferência:
# 1) token específico de Instagram Insights
# 2) token salvo no item Facebook
# 3) token salvo em arquivo local legado
CANDIDATE_SOURCES=(
  "1Password / Instagram Insights Token"
  "1Password / Facebook.Token_Api"
  "arquivo local instagram-page-token.json"
)
CANDIDATE_TOKENS=(
  "$(read_1p_field "Instagram Insights Token" "label=token")"
  "$(read_1p_field "Facebook" "label=Token_Api")"
  "$(load_token_from_file)"
)

TOKEN=""
TOKEN_SOURCE=""
BASIC=""
LAST_BASIC_ERROR=""

echo "🐕 Coletando dados Instagram @cakecooficial..."

for i in "${!CANDIDATE_SOURCES[@]}"; do
  candidate_token="${CANDIDATE_TOKENS[$i]}"
  candidate_source="${CANDIDATE_SOURCES[$i]}"

  if [ -z "$candidate_token" ]; then
    continue
  fi

  candidate_basic=$(try_basic_with_token "$candidate_token")
  if printf '%s' "$candidate_basic" | json_has_error; then
    LAST_BASIC_ERROR=$(printf '%s' "$candidate_basic" | json_error_message)
    echo "⚠️ Token inválido para dados básicos: $candidate_source"
    continue
  fi

  TOKEN="$candidate_token"
  TOKEN_SOURCE="$candidate_source"
  BASIC="$candidate_basic"
  break
done

if [ -z "$TOKEN" ]; then
  if [ -n "$LAST_BASIC_ERROR" ]; then
    echo "❌ Falha nos dados básicos do Instagram: $LAST_BASIC_ERROR"
  else
    echo "❌ Nenhum token do Instagram/Meta disponível."
  fi
  exit 2
fi

mapfile -t BASIC_FIELDS < <(printf '%s' "$BASIC" | json_extract_basic)
FOLLOWERS="${BASIC_FIELDS[0]:-N/D}"
FOLLOWS="${BASIC_FIELDS[1]:-N/D}"
POSTS="${BASIC_FIELDS[2]:-N/D}"

echo "✅ Dados básicos coletados | Seguidores: $FOLLOWERS"

# ============ INSIGHTS 30 DIAS ============
INSIGHTS=$(curl -s "https://graph.facebook.com/v19.0/$IG_ID/insights?metric=reach,total_interactions,accounts_engaged,profile_views&metric_type=total_value&period=day&access_token=$TOKEN" 2>/dev/null)
INSIGHTS_STATUS="✅ Insights completos coletados"
INSIGHTS_NOTE=""

if printf '%s' "$INSIGHTS" | json_has_error; then
  INSIGHTS_STATUS="⚠️ Insights indisponíveis"
  INSIGHTS_NOTE=$(printf '%s' "$INSIGHTS" | json_error_message)
  REACH="N/D"
  INTERACTIONS="N/D"
  ENGAGED="N/D"
  PROFILE_VIEWS="N/D"
else
  REACH=$(printf '%s' "$INSIGHTS" | json_extract_total_metric "reach")
  INTERACTIONS=$(printf '%s' "$INSIGHTS" | json_extract_total_metric "total_interactions")
  ENGAGED=$(printf '%s' "$INSIGHTS" | json_extract_total_metric "accounts_engaged")
  PROFILE_VIEWS=$(printf '%s' "$INSIGHTS" | json_extract_total_metric "profile_views")
fi

echo "$INSIGHTS_STATUS"

# ============ FOLLOWS/UNFOLLOWS ============
FOLLOWS_DATA=$(curl -s "https://graph.facebook.com/v19.0/$IG_ID/insights?metric=follows_and_unfollows&metric_type=total_value&period=day&breakdown=follow_type&access_token=$TOKEN" 2>/dev/null)

if printf '%s' "$FOLLOWS_DATA" | json_has_error; then
  FOLLOW_SALDO="N/D,N/D,N/D"
  FOLLOWS_NOTE=$(printf '%s' "$FOLLOWS_DATA" | json_error_message)
else
  FOLLOW_SALDO=$(printf '%s' "$FOLLOWS_DATA" | json_extract_follows_breakdown)
  FOLLOWS_NOTE=""
fi

NEW_FOLLOWS=$(echo "$FOLLOW_SALDO" | cut -d',' -f1)
NEW_UNFOLLOWS=$(echo "$FOLLOW_SALDO" | cut -d',' -f2)
NET_FOLLOWERS=$(echo "$FOLLOW_SALDO" | cut -d',' -f3)

# ============ TOP POSTS ============
echo "📸 Buscando posts recentes..."
POSTS_DATA=$(curl -s "https://graph.facebook.com/v19.0/$IG_ID/media?fields=id,caption,media_type,timestamp,like_count,comments_count,permalink&limit=10&access_token=$TOKEN" 2>/dev/null)

if printf '%s' "$POSTS_DATA" | json_has_error; then
  TOP_POSTS="| N/D | N/D | Não foi possível carregar os posts recentes |"
  POSTS_NOTE=$(printf '%s' "$POSTS_DATA" | json_error_message)
else
  TOP_POSTS=$(printf '%s' "$POSTS_DATA" | json_extract_posts_table)
  POSTS_NOTE=""
fi

AUTH_NOTES=""
if [ -n "$INSIGHTS_NOTE" ]; then
  AUTH_NOTES+="- Insights 30 dias: $INSIGHTS_NOTE\n"
fi
if [ -n "$FOLLOWS_NOTE" ]; then
  AUTH_NOTES+="- Follows/unfollows: $FOLLOWS_NOTE\n"
fi
if [ -n "$POSTS_NOTE" ]; then
  AUTH_NOTES+="- Posts recentes: $POSTS_NOTE\n"
fi
if [ -z "$AUTH_NOTES" ]; then
  AUTH_NOTES="- Nenhuma falha de autenticação detectada nesta coleta.\n"
fi

# ============ GERAR RELATÓRIO ============
cat > "$REPORT" << REPORT
# 📊 INSTAGRAM @cakecooficial — Relatório Mensal

**Gerado em:** $TODAY  
**Período:** Últimos 30 dias  
**Fonte do token nesta execução:** $TOKEN_SOURCE  

---

## 👥 AUDIÊNCIA

| Métrica | Valor |
|---------|-------|
| **Seguidores totais** | **$(fmt_num "$FOLLOWERS")** |
| Seguindo | $(fmt_num "$FOLLOWS") |
| Posts publicados | $(fmt_num "$POSTS") |

### Variação de Seguidores (30 dias)
- ✅ Novos seguidores: **${NEW_FOLLOWS}**
- ❌ Deixaram de seguir: **${NEW_UNFOLLOWS}**
- 📈 Saldo líquido: **${NET_FOLLOWERS}**

---

## 📈 PERFORMANCE (30 dias)

| Métrica | Valor |
|---------|-------|
| 👁️ Alcance (contas únicas) | $(fmt_num "$REACH") |
| ❤️ Interações totais | $(fmt_num "$INTERACTIONS") |
| 🙋 Contas engajadas | $(fmt_num "$ENGAGED") |
| 🔍 Visitas ao perfil | $(fmt_num "$PROFILE_VIEWS") |

---

## 📸 POSTS RECENTES

| Data | Engajamento | Legenda |
|------|-------------|---------|
$TOP_POSTS

---

## 🔐 STATUS DE AUTENTICAÇÃO / API

$INSIGHTS_STATUS

$(printf "%b" "$AUTH_NOTES")
---

## 🎯 ANÁLISE

### Leitura rápida
- Perfil com **$(fmt_num "$FOLLOWERS") seguidores**
- Quando algum bloco aparecer como **N/D**, significa falha real de permissão/token — não ausência de dados
- Este relatório foi endurecido para **não inventar zero** quando a API falhar

### Próximo passo recomendado
1. Reautenticar o token da Meta/Instagram com permissão de insights
2. Validar novamente alcance, interações, demografia e follows/unfollows
3. Só então expandir o relatório mensal detalhado

---

*Relatório gerado automaticamente por BigDog 🐕*  
*Próxima coleta: 1º de $(date -d "+1 month" +"%B/%Y" 2>/dev/null || echo "próximo mês")*
REPORT

echo ""
$PT_FILTER --file "$REPORT" --inplace >/dev/null
$PT_AUDIT --file "$REPORT" --strict

echo "✅ RELATÓRIO GERADO: $REPORT"
echo ""
cat "$REPORT"
