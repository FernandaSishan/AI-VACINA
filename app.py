import streamlit as st
import pandas as pd
from datetime import date, timedelta
from database import (init_db, add_person, list_people, add_vaccination,
                      list_vaccinations, dashboard_data, delete_person)
from intelligence import classify_vaccination, generate_reminder

st.set_page_config(
    page_title="AI VACINA | Sistema de Vacinação",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()

# ----------------------------------------------------------------------------
# Estilo: visual de sistema de saúde (SUS / Caderneta digital)
# ----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{
  --navy:#075b78; --navy-dark:#053f56; --teal:#27bea7; --teal-dark:#159d8b;
  --ink:#172b38; --muted:#647783; --line:#e1ebef;
  --ok:#0f9d7a; --ok-bg:#e3f6f0; --warn:#b7791f; --warn-bg:#fdf3dc;
  --bad:#c0392b; --bad-bg:#fde8e6; --info:#2b6cb0; --info-bg:#e6f0fb;
}
html, body, [class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:linear-gradient(180deg,#edf6fa 0%,#f8fbfc 48%,#f3f8fa 100%);}
.block-container{max-width:1180px;padding-top:1.4rem;padding-bottom:2rem;}
#MainMenu, footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}

/* Sidebar */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#053f56 0%,#075b78 60%,#0a7a8c 100%);}
section[data-testid="stSidebar"] *{color:#eaf7fa;}
section[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.18);}
.brand{display:flex;align-items:center;gap:12px;margin:4px 0 6px 0;}
.brand-logo{width:44px;height:44px;border-radius:13px;background:linear-gradient(135deg,#27bea7,#5ee0cc);
  display:flex;align-items:center;justify-content:center;font-size:1.5rem;box-shadow:0 6px 14px rgba(0,0,0,.22);}
.brand-name{font-weight:800;font-size:1.25rem;line-height:1.1;color:#fff;}
.brand-sub{font-size:.72rem;opacity:.8;letter-spacing:.05em;}
section[data-testid="stSidebar"] div[role="radiogroup"]{gap:4px;}
section[data-testid="stSidebar"] div[role="radiogroup"] label{
  background:rgba(255,255,255,.06);border-radius:12px;padding:9px 12px;width:100%;
  border:1px solid transparent;transition:.15s;}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:rgba(255,255,255,.14);}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){
  background:rgba(39,190,167,.28);border-color:rgba(94,224,204,.6);}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child{display:none;}
section[data-testid="stSidebar"] div[role="radiogroup"] label p{font-weight:700;font-size:.95rem;}
.side-note{font-size:.75rem;opacity:.75;line-height:1.4;}

/* Topo da página */
.page-head{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:14px;}
.page-title{font-size:1.65rem;font-weight:800;color:#0e3a4f;margin:0;}
.page-sub{color:var(--muted);font-size:.92rem;margin-top:2px;}
.date-chip{background:#fff;border:1px solid var(--line);border-radius:999px;padding:7px 14px;
  font-size:.82rem;font-weight:700;color:#356072;white-space:nowrap;}

/* Hero */
.hero{background:linear-gradient(115deg,#075b78 0%,#087b91 58%,#20b99f 100%);border-radius:22px;
  padding:24px 28px;color:#fff;box-shadow:0 12px 28px rgba(5,91,120,.16);margin:6px 0 20px 0;
  display:flex;justify-content:space-between;align-items:center;gap:18px;}
.hero h2{font-size:clamp(1.3rem,2.6vw,1.9rem);margin:.2rem 0 .4rem 0;color:#fff;line-height:1.2;}
.hero p{margin:0;color:#e4fbf7;font-size:.95rem;max-width:620px;}
.hero-kicker{font-size:.74rem;font-weight:700;letter-spacing:.12em;opacity:.85;text-transform:uppercase;}
.hero-icon{font-size:4rem;opacity:.9;}

/* Métricas */
div[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:18px;
  padding:15px 17px;box-shadow:0 5px 18px rgba(13,75,99,.05);}
div[data-testid="stMetricLabel"]{color:var(--muted);font-weight:600;}
div[data-testid="stMetricValue"]{color:var(--navy);font-weight:800;}

.section-title{font-size:1.12rem;font-weight:800;color:#123c50;margin:.4rem 0 .8rem 0;}

/* Cartão do paciente (caderneta) */
.patient{background:#fff;border:1px solid var(--line);border-radius:20px;padding:18px 20px;
  display:flex;gap:18px;align-items:center;box-shadow:0 6px 20px rgba(13,75,99,.06);margin-bottom:16px;
  border-left:6px solid var(--teal);}
.avatar{width:62px;height:62px;border-radius:50%;background:linear-gradient(135deg,#075b78,#27bea7);
  color:#fff;font-weight:800;font-size:1.35rem;display:flex;align-items:center;justify-content:center;flex:none;}
.patient-name{font-size:1.2rem;font-weight:800;color:#12313f;}
.patient-meta{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:6px;color:#526875;font-size:.88rem;}
.patient-tag{font-size:.7rem;font-weight:800;letter-spacing:.1em;color:var(--teal-dark);text-transform:uppercase;}

/* Linha do tempo de doses */
.timeline{position:relative;margin-left:10px;padding-left:22px;border-left:3px solid #d5e6ec;}
.t-item{position:relative;background:#fff;border:1px solid var(--line);border-radius:16px;
  padding:14px 16px;margin-bottom:12px;box-shadow:0 4px 14px rgba(15,65,82,.045);}
.t-item:before{content:"";position:absolute;left:-33px;top:20px;width:15px;height:15px;border-radius:50%;
  background:var(--teal);border:3px solid #fff;box-shadow:0 0 0 2px var(--teal);}
.t-item.late:before{background:var(--bad);box-shadow:0 0 0 2px var(--bad);}
.t-item.soon:before{background:#e0a21c;box-shadow:0 0 0 2px #e0a21c;}
.t-top{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;flex-wrap:wrap;}
.v-name{font-weight:800;color:#1a2c36;font-size:1.04rem;}
.v-sub{color:#526875;margin-top:3px;font-size:.9rem;}
.v-small{color:#657985;font-size:.8rem;margin-top:4px;}

/* Badges de situação */
.badge{display:inline-block;border-radius:999px;padding:4px 11px;font-size:.74rem;font-weight:800;white-space:nowrap;}
.b-ok{background:var(--ok-bg);color:var(--ok);}
.b-soon{background:var(--warn-bg);color:var(--warn);}
.b-late{background:var(--bad-bg);color:var(--bad);}
.b-none{background:var(--info-bg);color:var(--info);}

/* Cartões de resumo da caderneta */
.mini{background:#fff;border:1px solid var(--line);border-radius:16px;padding:13px 14px;text-align:center;}
.mini-n{font-size:1.6rem;font-weight:800;color:var(--navy);line-height:1;}
.mini-l{font-size:.76rem;color:var(--muted);font-weight:600;margin-top:5px;}

/* Cartões de ação rápida */
.quick-card{background:#fff;border:1px solid #dfe9ed;border-radius:17px;padding:14px 8px 6px 8px;
  text-align:center;}
.quick-icon{font-size:1.7rem;margin-bottom:2px;}
.quick-label{font-size:.83rem;font-weight:700;color:#234454;margin-bottom:6px;}

/* Lembrete */
.rem{background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px 16px;margin-bottom:10px;
  border-left:5px solid var(--teal);}
.rem.late{border-left-color:var(--bad);} .rem.soon{border-left-color:#e0a21c;} .rem.none{border-left-color:#7fb0e0;}
.rem-msg{color:#33505f;font-size:.9rem;margin-top:8px;}

div.stButton > button{border-radius:12px;border:1px solid #dce8ec;font-weight:700;min-height:2.6rem;}
div.stButton > button[kind="primary"]{background:var(--teal);border-color:var(--teal);color:#fff;}
div.stButton > button[kind="primary"]:hover{background:var(--teal-dark);border-color:var(--teal-dark);color:#fff;}
div[data-testid="stForm"]{background:#fff;border:1px solid var(--line);border-radius:18px;padding:18px;}
div[data-testid="stAlert"]{border-radius:13px;}
.small-note{font-size:.82rem;color:#657985;}

@media (max-width:700px){
  .block-container{padding:.65rem .75rem 1.4rem .75rem;}
  .hero{padding:18px;border-radius:18px;} .hero-icon{display:none;}
  .patient{flex-direction:column;align-items:flex-start;}
  .page-head{flex-direction:column;align-items:flex-start;}
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
VACINAS = [
    "BCG", "Hepatite B", "Pentavalente", "VIP (Poliomielite inativada)", "VOP (Poliomielite oral)",
    "Rotavírus", "Pneumocócica 10V", "Pneumocócica 23V", "Meningocócica C", "Meningocócica ACWY",
    "Febre amarela", "Tríplice viral (SCR)", "Tetraviral (SCRV)", "Hepatite A", "Varicela",
    "DTP (tríplice bacteriana)", "dT (dupla adulto)", "dTpa", "HPV", "Influenza (gripe)",
    "COVID-19", "Dengue", "Raiva", "Outra (digitar)",
]
DOSES = ["Dose única", "1ª dose", "2ª dose", "3ª dose", "Reforço", "1º reforço", "2º reforço", "Dose anual"]

NAV = ["📊 Painel", "📒 Caderneta digital", "💉 Registrar vacina", "👥 Pessoas", "🔔 Lembretes"]


def fmt_date(d):
    """ISO (AAAA-MM-DD) -> DD/MM/AAAA."""
    if not d:
        return "—"
    try:
        return date.fromisoformat(str(d)).strftime("%d/%m/%Y")
    except ValueError:
        return str(d)


def age_text(birth_iso):
    try:
        b = date.fromisoformat(str(birth_iso))
    except ValueError:
        return "—"
    t = date.today()
    years = t.year - b.year - ((t.month, t.day) < (b.month, b.day))
    if years >= 2:
        return f"{years} anos"
    months = (t.year - b.year) * 12 + t.month - b.month - (t.day < b.day)
    return f"{max(months, 0)} meses"


def initials(name):
    parts = [p for p in name.split() if p]
    if not parts:
        return "?"
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


def badge(status, applied_only=False):
    if applied_only:
        return '<span class="badge b-ok">✔ Aplicada</span>'
    if status == "Atrasada":
        return '<span class="badge b-late">● Atrasada</span>'
    if status == "Próxima":
        return '<span class="badge b-soon">● Próxima</span>'
    if status == "Sem data":
        return '<span class="badge b-none">● Sem data</span>'
    return '<span class="badge b-ok">● Em dia</span>'


def css_class(status):
    return {"Atrasada": "late", "Próxima": "soon", "Sem data": "none"}.get(status, "")


def html(s):
    """Remove indentação para o Markdown não tratar o HTML como bloco de código."""
    st.markdown("\n".join(line.strip() for line in s.strip().splitlines()), unsafe_allow_html=True)


def go(page):
    st.session_state["nav"] = page


def page_header(title, subtitle):
    hoje = date.today().strftime("%d/%m/%Y")
    html(f"""
    <div class="page-head">
      <div><div class="page-title">{title}</div><div class="page-sub">{subtitle}</div></div>
      <div class="date-chip">📅 {hoje}</div>
    </div>
    """)


# ----------------------------------------------------------------------------
# Navegação lateral
# ----------------------------------------------------------------------------
if "nav" not in st.session_state:
    st.session_state["nav"] = NAV[0]

with st.sidebar:
    html("""
    <div class="brand">
      <div class="brand-logo">💉</div>
      <div><div class="brand-name">AI VACINA</div><div class="brand-sub">SISTEMA DE VACINAÇÃO</div></div>
    </div>
    """)
    st.divider()
    page = st.radio("Menu", NAV, key="nav", label_visibility="collapsed")
    st.divider()
    html("""
    <div class="side-note">
    🔒 Protótipo acadêmico com dados fictícios.<br>
    Não substitui a caderneta oficial nem a orientação de profissionais de saúde.
    </div>
    """)

people = list_people()
records = list_vaccinations()
people_count, records_count, upcoming_count, overdue_count, recent_rows = dashboard_data()

# ----------------------------------------------------------------------------
# PAINEL
# ----------------------------------------------------------------------------
if page == NAV[0]:
    page_header("Painel de vacinação", "Visão geral da cobertura e das próximas doses")

    html("""
    <div class="hero">
      <div>
        <div class="hero-kicker">Acompanhamento inteligente</div>
        <h2>Vacinação em dia começa com informação.</h2>
        <p>Cadastre pessoas, registre doses aplicadas e acompanhe datas previstas e atrasos em um só lugar.</p>
      </div>
      <div class="hero-icon">🛡️</div>
    </div>
    """)

    m = st.columns(4)
    m[0].metric("👥 Pessoas", people_count)
    m[1].metric("💉 Doses registradas", records_count)
    m[2].metric("🗓️ Próximas · 7 dias", upcoming_count)
    m[3].metric("⚠️ Em atraso", overdue_count)

    st.write("")
    st.markdown('<div class="section-title">Ações rápidas</div>', unsafe_allow_html=True)
    quick = [("➕", "Cadastrar pessoa", NAV[3]), ("💉", "Registrar vacina", NAV[2]),
             ("📒", "Abrir caderneta", NAV[1]), ("🔔", "Ver lembretes", NAV[4])]
    qc = st.columns(4)
    for col, (ico, label, target) in zip(qc, quick):
        with col:
            html(f'<div class="quick-card"><div class="quick-icon">{ico}</div><div class="quick-label">{label}</div></div>')
            st.button("Acessar", key=f"q_{target}", on_click=go, args=(target,), use_container_width=True)

    st.write("")
    left, right = st.columns([3, 2])
    with left:
        st.markdown('<div class="section-title">Atividade recente</div>', unsafe_allow_html=True)
        if recent_rows:
            df = pd.DataFrame(recent_rows, columns=["Pessoa", "Vacina", "Dose", "Data aplicada", "Próxima dose"])
            df["Data aplicada"] = df["Data aplicada"].map(fmt_date)
            df["Próxima dose"] = df["Próxima dose"].map(fmt_date)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Cadastre uma pessoa e registre a primeira vacinação para ver os dados aqui.")
    with right:
        st.markdown('<div class="section-title">Situação das doses</div>', unsafe_allow_html=True)
        if records:
            contagem = {"Em dia": 0, "Próxima": 0, "Atrasada": 0, "Sem data": 0}
            for r in records:
                s = classify_vaccination(r[5], date.today())
                contagem[s if s in contagem else "Em dia"] += 1
            st.bar_chart(pd.Series(contagem, name="Doses"), color="#27bea7")
        else:
            st.caption("O gráfico aparece após o primeiro registro.")

# ----------------------------------------------------------------------------
# CADERNETA DIGITAL
# ----------------------------------------------------------------------------
elif page == NAV[1]:
    page_header("Caderneta digital", "Histórico de vacinação por pessoa")
    if not people:
        st.info("Cadastre uma pessoa na área Pessoas para começar.")
    else:
        opts = {f"{p[1]} · cadastro {p[0]}": p for p in people}
        c1, c2 = st.columns([2, 2])
        label = c1.selectbox("Pessoa", list(opts.keys()))
        busca = c2.text_input("Buscar vacina ou dose", placeholder="Ex.: Influenza, reforço…")
        pid, pname, birth, phone, resp = opts[label]

        meta = [f"🎂 {fmt_date(birth)} ({age_text(birth)})"]
        if phone:
            meta.append(f"📞 {phone}")
        meta.append(f"👨‍👩‍👧 Responsável: {resp}" if resp else "👨‍👩‍👧 Sem responsável informado")
        meta_html = "".join(f"<span>{x}</span>" for x in meta)
        html(f"""
        <div class="patient">
          <div class="avatar">{initials(pname)}</div>
          <div>
            <div class="patient-tag">Cartão de vacinação</div>
            <div class="patient-name">{pname}</div>
            <div class="patient-meta">{meta_html}</div>
          </div>
        </div>
        """)

        recs = [r for r in records if r[1] == pname]
        if busca:
            recs = [r for r in recs if busca.lower() in f"{r[2]} {r[3]}".lower()]
        recs.sort(key=lambda r: str(r[4]), reverse=True)

        stats = [classify_vaccination(r[5], date.today()) for r in recs]
        sc = st.columns(4)
        resumo = [(len(recs), "Doses registradas"), (stats.count("Atrasada"), "Em atraso"),
                  (stats.count("Próxima"), "Próximas"), (len({r[2] for r in recs}), "Vacinas diferentes")]
        for col, (n, l) in zip(sc, resumo):
            with col:
                html(f'<div class="mini"><div class="mini-n">{n}</div><div class="mini-l">{l}</div></div>')

        st.write("")
        st.markdown('<div class="section-title">Histórico de doses</div>', unsafe_allow_html=True)
        if recs:
            html('<div class="timeline">')
            for (rid, person, vaccine, dose, applied, next_due, unit), status in zip(recs, stats):
                b = badge(status, applied_only=not next_due)
                cls = css_class(status) if next_due else ""
                unidade = f"🏥 {unit}" if unit else ""
                html(f"""
                <div class="t-item {cls}">
                  <div class="t-top">
                    <div>
                      <div class="v-name">{vaccine}</div>
                      <div class="v-sub">{dose} · aplicada em {fmt_date(applied)}</div>
                    </div>
                    {b}
                  </div>
                  <div class="v-sub">🗓️ Próxima dose: <b>{fmt_date(next_due) if next_due else "não prevista"}</b></div>
                  <div class="v-small">{unidade}</div>
                </div>
                """)
            html('</div>')
        else:
            st.warning("Nenhum registro encontrado para esta pessoa.")

        st.button("＋ Registrar vacina para esta pessoa", on_click=go, args=(NAV[2],), type="primary")

# ----------------------------------------------------------------------------
# REGISTRAR VACINA
# ----------------------------------------------------------------------------
elif page == NAV[2]:
    page_header("Registrar vacinação", "Lance uma dose aplicada na caderneta")
    if not people:
        st.info("Cadastre uma pessoa primeiro na área Pessoas.")
        st.button("Ir para Pessoas", on_click=go, args=(NAV[3],), type="primary")
    else:
        person_map = {f"{p[1]} (ID {p[0]})": p[0] for p in people}
        with st.form("vaccine_form", clear_on_submit=True):
            st.markdown("**1 · Paciente**")
            selected_person = st.selectbox("Pessoa *", list(person_map.keys()))
            st.markdown("**2 · Vacina e dose**")
            c1, c2 = st.columns(2)
            vac_sel = c1.selectbox("Vacina *", VACINAS)
            vac_outra = c1.text_input("Se escolheu “Outra”, digite o nome")
            dose = c2.selectbox("Dose *", DOSES)
            unit = c2.text_input("Unidade de saúde (opcional)", placeholder="Ex.: UBS Centro")
            st.markdown("**3 · Datas**")
            d1, d2 = st.columns(2)
            applied = d1.date_input("Data de aplicação", value=date.today(), max_value=date.today(),
                                    format="DD/MM/YYYY")
            has_next = d2.checkbox("Informar próxima dose prevista?", value=True)
            next_due = d2.date_input("Próxima dose prevista", value=date.today() + timedelta(days=30),
                                     format="DD/MM/YYYY")
            submitted = st.form_submit_button("💾 Salvar vacinação", type="primary", use_container_width=True)
            if submitted:
                vaccine = vac_outra.strip() if vac_sel.startswith("Outra") else vac_sel
                if not vaccine:
                    st.error("Informe o nome da vacina.")
                elif has_next and next_due < applied:
                    st.error("A próxima data não pode ser anterior à aplicação.")
                else:
                    add_vaccination(person_map[selected_person], vaccine, dose,
                                    applied.isoformat(), next_due.isoformat() if has_next else None,
                                    unit.strip())
                    st.toast("Vacinação registrada com sucesso!", icon="✅")
                    st.rerun()

# ----------------------------------------------------------------------------
# PESSOAS
# ----------------------------------------------------------------------------
elif page == NAV[3]:
    page_header("Pessoas cadastradas", "Cadastro de pacientes e responsáveis")
    with st.expander("＋ Cadastrar nova pessoa", expanded=not people):
        with st.form("person_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Nome completo *")
            birth = c2.date_input("Data de nascimento", value=date(2010, 1, 1),
                                  min_value=date(1900, 1, 1), max_value=date.today(), format="DD/MM/YYYY")
            phone = c1.text_input("Telefone (opcional)")
            responsible = c2.text_input("Responsável (quando aplicável)")
            if st.form_submit_button("Cadastrar pessoa", type="primary", use_container_width=True):
                if not name.strip():
                    st.error("Informe o nome.")
                else:
                    add_person(name.strip(), birth.isoformat(), phone.strip(), responsible.strip())
                    st.toast("Cadastro realizado com sucesso.", icon="✅")
                    st.rerun()

    if people:
        filtro = st.text_input("Buscar pessoa", placeholder="Digite o nome…")
        st.markdown(f'<div class="section-title">Lista de pessoas ({len(people)})</div>', unsafe_allow_html=True)
        for pid, pname, birthdate, phone, responsible in people:
            if filtro and filtro.lower() not in pname.lower():
                continue
            n_doses = sum(1 for r in records if r[1] == pname)
            with st.container(border=True):
                a, b, c = st.columns([1, 6, 2])
                a.markdown(f'<div class="avatar" style="width:46px;height:46px;font-size:1rem">{initials(pname)}</div>',
                           unsafe_allow_html=True)
                b.markdown(f"**{pname}**  ·  {age_text(birthdate)}")
                b.caption(f"Nasc.: {fmt_date(birthdate)} · "
                          f"{('Resp.: ' + responsible) if responsible else 'Sem responsável'} · "
                          f"{n_doses} dose(s) registrada(s)")
                if c.button("🗑️ Excluir", key=f"del_{pid}", use_container_width=True):
                    st.session_state["delete_person_id"] = pid
                if st.session_state.get("delete_person_id") == pid:
                    st.warning(f"Confirma excluir {pname} e todos os registros associados?")
                    c1_, c2_ = st.columns(2)
                    if c1_.button("Confirmar", key=f"yes_{pid}", type="primary"):
                        delete_person(pid)
                        del st.session_state["delete_person_id"]
                        st.rerun()
                    if c2_.button("Cancelar", key=f"no_{pid}"):
                        del st.session_state["delete_person_id"]
                        st.rerun()
    else:
        st.caption("Ainda não há pessoas cadastradas.")

# ----------------------------------------------------------------------------
# LEMBRETES
# ----------------------------------------------------------------------------
else:
    page_header("Lembretes de vacinação", "O sistema analisa as datas previstas e prepara orientações")
    if not records:
        st.info("Registre uma vacinação para gerar o primeiro lembrete.")
    else:
        itens = [(r, classify_vaccination(r[5], date.today())) for r in records]
        filtro = st.segmented_control("Filtrar por situação",
                                      ["Todas", "Atrasada", "Próxima", "Em dia", "Sem data"],
                                      default="Todas")
        filtro = filtro or "Todas"
        mostrados = [(r, s) for r, s in itens if filtro == "Todas" or s == filtro]
        st.caption(f"{len(mostrados)} lembrete(s)")
        if not mostrados:
            st.success("Nenhum lembrete nesta situação.")
        for (rid, person, vaccine, dose, applied, next_due, unit), status in mostrados:
            msg = generate_reminder(person, vaccine, dose, next_due, status)
            html(f"""
            <div class="rem {css_class(status)}">
              <div class="t-top">
                <div>
                  <div class="v-name">{person} · {vaccine}</div>
                  <div class="v-sub">{dose} · próxima data: {fmt_date(next_due) if next_due else "não informada"}</div>
                </div>
                {badge(status)}
              </div>
              <div class="rem-msg">{msg}</div>
            </div>
            """)

st.divider()
st.markdown("<div style='text-align:center;color:#718792;font-size:.78rem'>VaciIA · Protótipo acadêmico · Dados fictícios. "
            "A classificação é apenas administrativa; confirme sempre o esquema vacinal com o serviço de saúde.</div>",
            unsafe_allow_html=True)