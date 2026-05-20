import streamlit as st
from datetime import datetime
import gspread
from google.oauth2 import service_account
import re
import pytz

# ---------------------------
# CONFIG GOOGLE SHEETS (SECRETS)
# ---------------------------

google_secrets = dict(st.secrets["google"])
google_secrets["private_key"] = (
    google_secrets["private_key"]
    .replace("\\n", "\n")
    .replace("\r\n", "\n")
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = service_account.Credentials.from_service_account_info(
    google_secrets, scopes=SCOPES)
client = gspread.authorize(creds)

SHEET_ID = "1RFsEMgRx-nfnVxKLTGt_hzB_BmLspqJb9GIRusd8dKM"
sheet = client.open_by_key(SHEET_ID).get_worksheet(0)

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="Sistema de Novedades",
    page_icon="🛡️",
    layout="centered"
)

# ---------------------------
# GLOBAL STYLES
# ---------------------------

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container {
    background-color: #0b1120 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(20,184,166,0.12) 0%, transparent 70%),
        linear-gradient(180deg, #0b1120 0%, #0d1526 100%) !important;
    min-height: 100vh;
}

/* ── HIDE STREAMLIT CHROME ── */
header[data-testid="stHeader"],
footer,
#MainMenu,
[data-testid="stBottomBlockContainer"],
[class*="_profileContainer"],
[class*="_profilePreview"],
[class*="_viewerBadge"],
[class*="_imageMove"],
[data-testid="appCreatorAvatar"],
.stDeployButton {
    display: none !important;
}

/* ── BLOCK CONTAINER ── */
.block-container {
    max-width: 780px !important;
    padding: 2.5rem 2rem 4rem !important;
}

/* ── TYPOGRAPHY ── */
p, label, .stMarkdown p {
    font-family: 'DM Sans', sans-serif !important;
    color: #94a3b8 !important;
    font-size: 0.875rem !important;
}

/* ── SECTION HEADER LABELS ── */
.stSelectbox label,
.stTextInput label,
.stDateInput label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #64748b !important;
    margin-bottom: 4px !important;
}

/* ── INPUTS & SELECTS ── */
.stTextInput input,
.stDateInput input {
    background-color: #111827 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.875rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    height: 44px !important;
}

.stTextInput input:focus,
.stDateInput input:focus {
    border-color: #14b8a6 !important;
    box-shadow: 0 0 0 3px rgba(20,184,166,0.15) !important;
    outline: none !important;
}

.stTextInput input::placeholder {
    color: #334155 !important;
    font-family: 'DM Mono', monospace !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background-color: #111827 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    min-height: 44px !important;
    transition: border-color 0.2s ease !important;
}

.stSelectbox > div > div:hover {
    border-color: #334155 !important;
}

.stSelectbox > div > div:focus-within {
    border-color: #14b8a6 !important;
    box-shadow: 0 0 0 3px rgba(20,184,166,0.15) !important;
}

.stSelectbox [data-baseweb="select"] span {
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Dropdown menu */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="select"] ul {
    background-color: #1a2640 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 8px !important;
}

[data-baseweb="option"] {
    background-color: transparent !important;
    color: #cbd5e1 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
}

[data-baseweb="option"]:hover,
[data-baseweb="option"][aria-selected="true"] {
    background-color: rgba(20,184,166,0.15) !important;
    color: #14b8a6 !important;
}

/* SVG icons in selectbox */
.stSelectbox svg { color: #475569 !important; }

/* ── DATE PICKER ── */
[data-baseweb="calendar"] {
    background-color: #1a2640 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 12px !important;
}

[data-baseweb="calendar"] * { color: #cbd5e1 !important; }

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid #1e2d45 !important;
    margin: 1.5rem 0 !important;
}

/* ── CONTAINER / CARD ── */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: linear-gradient(145deg, #111827 0%, #0f1e30 100%) !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    box-shadow: 0 4px 40px rgba(0,0,0,0.4), 0 1px 0 rgba(255,255,255,0.03) inset !important;
    position: relative !important;
    overflow: hidden !important;
}

[data-testid="stVerticalBlockBorderWrapper"] > div::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(20,184,166,0.4), transparent);
}

/* ── BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    height: 48px !important;
    padding: 0 2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(20,184,166,0.3) !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(20,184,166,0.45) !important;
    background: linear-gradient(135deg, #0f9d91 0%, #2dd4bf 100%) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 12px rgba(20,184,166,0.3) !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
}

/* Success */
[data-testid="stAlert"][data-baseweb="notification"][kind="positive"],
div[class*="stSuccess"] > div {
    background-color: rgba(20,184,166,0.12) !important;
    border-left: 3px solid #14b8a6 !important;
    color: #5eead4 !important;
}

/* Error */
[data-testid="stAlert"][data-baseweb="notification"][kind="negative"],
div[class*="stError"] > div {
    background-color: rgba(239,68,68,0.1) !important;
    border-left: 3px solid #ef4444 !important;
    color: #fca5a5 !important;
}

/* ── COLUMNS GAP ── */
[data-testid="stHorizontalBlock"] { gap: 1.25rem !important; }

/* ── BADGE HEADER ── */
.badge-header {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(20,184,166,0.1);
    border: 1px solid rgba(20,184,166,0.25);
    border-radius: 100px;
    padding: 5px 14px 5px 10px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5eead4;
    margin-bottom: 1.25rem;
}

.badge-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #14b8a6;
    box-shadow: 0 0 6px #14b8a6;
    animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px #14b8a6; }
    50% { opacity: 0.6; box-shadow: 0 0 12px #14b8a6; }
}

.main-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 2rem;
    font-weight: 600;
    color: #f1f5f9;
    margin: 0 0 0.35rem;
    letter-spacing: -0.025em;
    line-height: 1.2;
}

.main-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.875rem;
    font-weight: 400;
    color: #475569;
    margin: 0 0 2rem;
}

.section-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #334155;
    margin: 1.5rem 0 0.85rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e2d45;
}

.field-hint {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #334155;
    margin-top: 3px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------

col_logo, col_text = st.columns([1, 8])

with col_logo:
    st.image("logo_izquierda.png", width=64)

with col_text:
    st.markdown("""
    <div style="padding-top: 6px;">
        <div class="badge-header">
            <span class="badge-dot"></span>
            Sistema activo
        </div>
        <div class="main-title">Carga de Novedades</div>
        <div class="main-subtitle">Registro de incidentes — Partido de Lomas de Zamora</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# CONFIG DATOS
# ---------------------------

categorias = {
    "Robo":                    ["Moto", "Auto", "Via pública", "Finca", "Comercio", "Tentativa"],
    "Hurto":                   ["Moto", "Auto", "Via pública", "Finca", "Comercio", "Escuela", "Tentativa"],
    "Accidente de tránsito":   ["Daños materiales", "Con lesiones"],
    "Conflicto":               ["Vecinal", "Familiar", "Pareja"],
    "Violencia":               ["Violencia de Género", "Maltrato animal", "Violencia Infantil", "Violencia Familia"],
    "Heridos":                 ["Arma de fuego", "Arma blanca"],
    "Persecución":             ["Con aprendido", "Fugó"],
    "Obito":                   ["Homicidio", "Natural", "Suicidio"],
    "Incendios":               ["Via pública", "Comercio", "Automotor", "Finca", "Escuela"],
    "Otros":                   []
}

comisarias = [
    "Cria 1ra", "Cria 2da", "Cria 3ra", "Cria 4ta", "Cria 5ta",
    "Cria 6ta", "Cria 7ma", "Cria 8va", "Cria 9na", "Cria 10ma",
    "Dto Turdera", "Dto Banfield", "Dto Villa Rita"
]

cgm_opciones = [
    "Banfield", "Ingeniero Budge", "Llavallol", "Lomas de Zamora",
    "Parque Barón", "San José", "Santa Catalina", "Santa Marta",
    "Temperley", "Turdera", "Villa Albertina", "Villa Centenario",
    "Villa Fiorito", "Villa Lamadrid"
]

# ---------------------------
# SESSION STATE
# ---------------------------

if "form_key" not in st.session_state:
    st.session_state.form_key = 0
if "success_msg" not in st.session_state:
    st.session_state.success_msg = None
if "error_msg" not in st.session_state:
    st.session_state.error_msg = None

# ---------------------------
# MENSAJES DE ESTADO
# ---------------------------

if st.session_state.success_msg:
    st.success(st.session_state.success_msg)
    st.session_state.success_msg = None

if st.session_state.error_msg:
    st.error(st.session_state.error_msg)
    st.session_state.error_msg = None

# ---------------------------
# FORMULARIO
# ---------------------------

fk = st.session_state.form_key

with st.container(border=True):

    # — Bloque 1: Temporalidad —
    st.markdown('<div class="section-label">① Temporalidad</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input(
            "Fecha del evento",
            datetime.today(),
            key=f"fecha_{fk}"
        )
    with col2:
        horario = st.text_input(
            "Horario",
            value="",
            placeholder="HH:MM",
            key=f"horario_{fk}"
        )
        st.markdown('<div class="field-hint">Formato 24 h — ej: 08:30 / 21:45</div>',
                    unsafe_allow_html=True)

    # — Bloque 2: Jurisdicción —
    st.markdown('<div class="section-label">② Jurisdicción</div>', unsafe_allow_html=True)

    col3, col4, col5 = st.columns(3)
    with col3:
        comisaria = st.selectbox(
            "Comisaría",
            options=["Seleccione"] + comisarias,
            index=0,
            key=f"comisaria_{fk}"
        )
    with col4:
        cgm = st.selectbox(
            "CGM",
            options=["Seleccione"] + cgm_opciones,
            index=0,
            key=f"cgm_{fk}"
        )
    with col5:
        camara_flag = st.selectbox(
            "¿Se ve por cámara?",
            options=["Seleccione", "SI", "NO"],
            index=0,
            key=f"camara_{fk}"
        )

    if camara_flag == "SI":
        numero_camara = st.text_input(
            "Número de cámara",
            placeholder="Ej: CAM-047",
            key=f"num_camara_{fk}"
        )

    # — Bloque 3: Tipo de incidente —
    st.markdown('<div class="section-label">③ Tipo de incidente</div>', unsafe_allow_html=True)

    col6, col7 = st.columns(2)
    with col6:
        categoria = st.selectbox(
            "Categoría",
            options=["Seleccione"] + list(categorias.keys()),
            index=0,
            key=f"categoria_{fk}"
        )
    with col7:
        if categoria not in ["Seleccione", "Otros"]:
            subcategoria = st.selectbox(
                "Subcategoría",
                options=["Seleccione"] + categorias[categoria],
                index=0,
                key=f"subcat_{categoria}_{fk}"
            )
        elif categoria == "Otros":
            subcategoria = "Otros"
            st.selectbox(
                "Subcategoría",
                options=["—  No aplica  —"],
                disabled=True,
                key=f"subcat_disabled_{fk}"
            )
        else:
            subcategoria = "Seleccione"
            st.selectbox(
                "Subcategoría",
                options=["Seleccione categoría primero"],
                disabled=True,
                key=f"subcat_empty_{fk}"
            )

# Botón de guardado
st.markdown("<div style='height: 1.25rem'></div>", unsafe_allow_html=True)
submitted = st.button(
    "Guardar Novedad  →",
    use_container_width=True,
    key=f"submit_{fk}"
)

# ---------------------------
# VALIDACIÓN + GUARDADO
# ---------------------------

if submitted:

    fk = st.session_state.form_key

    categoria_val  = st.session_state.get(f"categoria_{fk}", "Seleccione")
    subcat_key     = f"subcat_{categoria_val}_{fk}"
    subcat_val     = st.session_state.get(subcat_key, "Seleccione")
    if categoria_val == "Otros":
        subcat_val = "Otros"

    horario_input  = st.session_state.get(f"horario_{fk}", "").strip()
    fecha_val      = st.session_state.get(f"fecha_{fk}", datetime.today())
    comisaria_val  = st.session_state.get(f"comisaria_{fk}", "Seleccione")
    cgm_val        = st.session_state.get(f"cgm_{fk}", "Seleccione")
    camara_val     = st.session_state.get(f"camara_{fk}", "Seleccione")
    num_camara_val = st.session_state.get(f"num_camara_{fk}", "")

    errores = []
    horario_valido = re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", horario_input)

    if not horario_valido:
        errores.append("Horario inválido — usar formato HH:MM (ej: 08:30)")
    if comisaria_val == "Seleccione":
        errores.append("Debe seleccionar una Comisaría")
    if cgm_val == "Seleccione":
        errores.append("Debe seleccionar un CGM")
    if categoria_val == "Seleccione":
        errores.append("Debe seleccionar una Categoría")
    if categoria_val not in ["Seleccione", "Otros"] and subcat_val == "Seleccione":
        errores.append("Debe seleccionar una Subcategoría")
    if camara_val == "Seleccione":
        errores.append("Debe indicar si se ve por cámara")

    if errores:
        st.session_state.error_msg = "  ·  ".join(errores)
        st.rerun()
    else:
        try:
            tz_argentina   = pytz.timezone("America/Argentina/Buenos_Aires")
            marca_temporal = datetime.now(tz_argentina).strftime("%d/%m/%Y %H:%M:%S")
            fecha_str      = fecha_val.strftime("%d/%m/%Y")
            hora_obj       = datetime.strptime(horario_input, "%H:%M")
            horario_str    = hora_obj.strftime("%H:%M:%S")

            nueva_fila = {
                "Marca temporal":     marca_temporal,
                "Fecha evento":       fecha_str,
                "Horario":            horario_str,
                "¿Se ve por cámara?": camara_val,
                "Camara del Evento":  num_camara_val,
                "CGM":                cgm_val,
                "Categoria":          categoria_val,
                "Comisaria":          comisaria_val,
                "Subcategoria":       subcat_val if subcat_val != "Seleccione" else ""
            }

            sub_cols = {
                "Subcategoria Robo":                  "",
                "Subcategoria Hurto":                 "",
                "Subcategoria Accidente de tránsito": "",
                "Subcategoria Conflicto":             "",
                "Subcategoria Violencia":             "",
                "Subcategoria Heridos":               "",
                "Subcategoria Persecución":           "",
                "Subcategoria Obito":                 "",
                "Subcategoria Otros":                 "",
                "Subcategoria Incendios":             ""
            }

            col_sub = f"Subcategoria {categoria_val}"
            if col_sub in sub_cols:
                sub_cols[col_sub] = nueva_fila["Subcategoria"]

            nueva_fila.update(sub_cols)

            columnas   = sheet.row_values(1)
            fila_final = [nueva_fila.get(col, "") for col in columnas]

            sheet.append_row(fila_final)

            st.session_state.success_msg = "Novedad registrada correctamente."
            st.session_state.form_key += 1
            st.rerun()

        except Exception as e:
            st.session_state.error_msg = f"Error al guardar: {str(e)}"
            st.rerun()
