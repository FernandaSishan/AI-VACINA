import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
import base64
from database import (init_db, add_person, list_people, add_vaccination,
                      list_vaccinations, dashboard_data, delete_person)
from intelligence import classify_vaccination, generate_reminder

st.set_page_config(
    page_title="VaciIA | Sistema de Vacinação",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()

# ----------------------------------------------------------------------------
# Estilo: visual de sistema de saúde (SUS / Caderneta digital)
# ----------------------------------------------------------------------------
def load_css(path="style.css"):
    """Carrega o CSS externo (fica na mesma pasta do app.py)."""
    css_file = Path(__file__).parent / path
    if not css_file.exists():
        st.warning(f"Arquivo de estilo não encontrado: {css_file}. "
                   "Copie o style.css para a mesma pasta do app.py.")
        return
    st.markdown(f"<style>{css_file.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


load_css()


def logo_html(path="assets/logo.png"):
    img = Path(__file__).parent / path
    if not img.exists():
        return '<div class="brand-logo">💉</div>'
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".svg": "image/svg+xml"}.get(img.suffix.lower(), "image/png")
    b64 = base64.b64encode(img.read_bytes()).decode()
    return f'<div class="brand-logo has-img"><img src="data:{mime};base64,{b64}" alt="Logo VaciIA"></div>'

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
    html(f"""
    <div class="brand">
      {logo_html()}
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