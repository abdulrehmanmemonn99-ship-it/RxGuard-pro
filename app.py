import streamlit as st
from PIL import Image
import pytesseract
import math
import json
import os

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="RxGuard Ultimate | Clinical CDS",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOGIN SYSTEM ---
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    st.markdown("""
        <style>.stTextInput > div > div > input {text-align: center;}</style>
        """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 RxGuard Secure Access")
        st.info("This is a restricted clinical platform. Please enter your Access Key.")
        password = st.text_input("Access Key", type="password")
        if st.button("Login", use_container_width=True):
            if password == "medical2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Invalid Access Key")
    return False

if not check_password():
    st.stop()

# =========================================================
# MAIN APP LOGIC
# =========================================================

st.markdown("""
    <style>
    /* ── Base ── */
    .stExpander { border: 1px solid #ddd; border-radius: 5px; background-color: #f0f2f6; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; }

    /* ── Alert Cards ── */
    .rxcard {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 5px solid;
        line-height: 1.6;
    }
    .rxcard-critical { background-color: #fff0f0; border-color: #c0392b; color: #2c0b0b; }
    .rxcard-major    { background-color: #fff8ee; border-color: #e67e22; color: #3b1f00; }
    .rxcard-minor    { background-color: #fdfde7; border-color: #f1c40f; color: #3b3300; }
    .rxcard-info     { background-color: #eaf4fb; border-color: #2980b9; color: #0a2540; }
    .rxcard-title  { font-weight: 700; font-size: 0.95rem; margin-bottom: 4px; }
    .rxcard-body   { font-size: 0.9rem; }
    .rxcard-meta   { font-size: 0.8rem; margin-top: 6px; opacity: 0.85; }

    /* ── Score Badge ── */
    .score-badge {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 20px;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .score-safe   { background: #eafaf1; color: #1e8449; border: 2px solid #1e8449; }
    .score-warn   { background: #fef9e7; color: #b7950b; border: 2px solid #b7950b; }
    .score-danger { background: #fdedec; color: #c0392b; border: 2px solid #c0392b; }

    /* ── Mobile ── */
    @media (max-width: 768px) {
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        .rxcard { padding: 10px 12px; }
        .rxcard-title { font-size: 0.88rem; }
        .rxcard-body  { font-size: 0.83rem; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE LOADER ---
_DIR = os.path.dirname(os.path.abspath(__file__))

def _load(filename):
    path = os.path.join(_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

drug_db = _load("drugs.json")

_raw_interactions = _load("interactions.json")
interactions_db = {}
for key, value in _raw_interactions.items():
    parts = key.split("|")
    if len(parts) == 2:
        d1, d2 = parts[0].strip(), parts[1].strip()
        interactions_db[(d1, d2)] = value

parenteral_db = _load("parenteral.json")

# --- 3. HELPERS ---
def calculate_crcl(age, weight_kg, gender, scr):
    if scr <= 0: return None
    factor = 0.85 if gender == "Female" else 1.0
    crcl = ((140 - age) * weight_kg) / (72 * scr)
    return round(crcl * factor, 2)

def card(style, title, body, meta=""):
    meta_html = f'<div class="rxcard-meta">{meta}</div>' if meta else ""
    st.markdown(f"""
    <div class="rxcard rxcard-{style}">
        <div class="rxcard-title">{title}</div>
        <div class="rxcard-body">{body}</div>
        {meta_html}
    </div>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚕️ RxGuard Ultimate")
    st.markdown("### 1. Patient Data")
    age = st.number_input("Age (Years)", 0, 120, 25)
    gender = st.radio("Gender", ["Male", "Female"], horizontal=True)
    c1, c2 = st.columns([2, 1])
    with c1: weight_val = st.number_input("Weight", 1.0, 300.0, 70.0, step=0.5)
    with c2: weight_unit = st.selectbox("Unit", ["kg", "lbs"])
    weight_kg = weight_val if weight_unit == "kg" else weight_val * 0.453592

    with st.expander("🧪 Lab Reports (Expanded)", expanded=True):
        st.markdown("**Renal Profile**")
        scr = st.number_input("Serum Creatinine (mg/dL)", 0.0, 15.0, 1.2, step=0.1)
        egfr = st.number_input("eGFR (mL/min)", 0, 200, 0)
        st.markdown("**Liver & Coagulation**")
        col_lab1, col_lab2 = st.columns(2)
        with col_lab1:
            alt = st.number_input("ALT (U/L)", 0, 1000, 40)
            inr = st.number_input("INR", 0.0, 10.0, 1.0, step=0.1)
        with col_lab2:
            bilirubin = st.number_input("Bilirubin", 0.0, 20.0, 1.0)
            platelets = st.number_input("Platelets", 0, 1000, 250)
        st.markdown("**Electrolytes & Endocrine**")
        potassium = st.number_input("Potassium (K+)", 1.0, 10.0, 4.0, step=0.1)
        tsh = st.number_input("TSH (mIU/L)", 0.0, 100.0, 2.5)

    crcl_calc = calculate_crcl(age, weight_kg, gender, scr)
    if egfr > 0:
        renal_function = egfr
        renal_source = "eGFR (Lab)"
    elif crcl_calc is not None:
        renal_function = crcl_calc
        renal_source = "Calculated CrCl"
    else:
        renal_function = None
        renal_source = "N/A (Invalid SCr)"

    with st.expander("📜 History & Allergies"):
        comorbidities = st.multiselect("Conditions:", ["Hypertension", "Diabetes T2DM", "Asthma", "Heart Failure", "Peptic Ulcer", "CKD", "Epilepsy", "Rheumatoid Arthritis"])
        known_allergies = st.multiselect("Allergies:", ["Penicillin", "Sulfa Drugs", "Aspirin/NSAIDs"])
        lifestyle = st.multiselect("Lifestyle:", ["Alcohol", "Smoking", "Vitamin K Rich Diet", "Dairy Products", "Grapefruit Juice"])

    st.divider()
    st.caption(f"Calculated Weight: {round(weight_kg, 1)} kg | CrCl: {crcl_calc if crcl_calc else 'N/A'} mL/min")

# --- 5. MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["🏥 Clinical Analysis", "💉 Parenteral (IV) Dilution", "🤖 AI Consult"])

# ==========================================
# TAB 1: CLINICAL ANALYSIS
# ==========================================
with tab1:
    st.header("Clinical Prescription Audit")
    input_method = st.radio("Input:", ["✍️ Manual Entry", "📷 Image Upload"], horizontal=True)

    col_in, col_out = st.columns([1, 1.2], gap="large")

    with col_in:
        text_input = ""
        run_analysis = False

        if input_method == "✍️ Manual Entry":
            text_input = st.text_area("Medications:", height=150, placeholder="e.g. Methotrexate, Ibuprofen, Warfarin...")
            if st.button("🔍 Analyze Rx", use_container_width=True):
                run_analysis = True
        else:
            uploaded_file = st.file_uploader("Upload Rx", type=["jpg", "png"])
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, use_container_width=True)
                if st.button("📷 Extract & Analyze", use_container_width=True):
                    try:
                        text_input = pytesseract.image_to_string(img)
                        if not text_input.strip():
                            st.warning("OCR detected no text. Image might be too blurry.")
                        else:
                            st.success("OCR Done")
                            run_analysis = True
                    except Exception as e:
                        st.error("OCR Error: Tesseract engine not found.")
                        st.info("If running locally, install Tesseract-OCR.")

    with col_out:
        if run_analysis and text_input:

            # Patient context card
            card("info", "👤 Patient Context",
                f"<b>Renal:</b> {renal_function if renal_function else 'N/A'} mL/min ({renal_source}) &nbsp;|&nbsp; "
                f"<b>ALT:</b> {alt} U/L &nbsp;|&nbsp; <b>INR:</b> {inr} &nbsp;|&nbsp; <b>Platelets:</b> {platelets}")

            text_lower = text_input.lower()
            found_drugs = [d for d in drug_db.keys() if d in text_lower]

            safety_score = 100
            intervention_notes = []

            if not found_drugs:
                st.warning("⚠️ No formulary drugs detected in text.")
            else:
                st.success(f"✅ Detected: {', '.join([d.title() for d in found_drugs])}")
                st.markdown("---")

                # ── 0. LAB VALUE ALERTS ──────────────────────────────
                if inr >= 4.0:
                    safety_score -= 20
                    card("critical", "🚨 CRITICAL — Supratherapeutic INR",
                        f"INR = <b>{inr}</b>. Serious bleeding risk. Review all anticoagulants immediately.")
                    intervention_notes.append(f"CRITICAL: INR {inr} — Review anticoagulation urgently")
                elif inr >= 3.0:
                    safety_score -= 10
                    card("major", "⚠️ High INR",
                        f"INR = <b>{inr}</b>. Above therapeutic range. Monitor closely and review anticoagulant dosing.")
                    intervention_notes.append(f"High INR {inr} — Monitor anticoagulation")

                if alt >= 100:
                    safety_score -= 15
                    card("critical", "🚨 CRITICAL — Elevated ALT",
                        f"ALT = <b>{alt} U/L</b>. Significant hepatotoxicity risk. Review all hepatotoxic drugs.")
                    intervention_notes.append(f"Hepatic Risk: Elevated ALT {alt}")
                    for drug in found_drugs:
                        if drug_db[drug].get("hepatic_risk"):
                            card("critical", f"⚠️ Hepatotoxic Drug — {drug.title()}",
                                f"{drug.title()} carries hepatotoxic risk — use with caution or avoid given ALT {alt} U/L.")
                            intervention_notes.append(f"Hepatic Risk: {drug.title()} with ALT {alt}")
                elif alt >= 60:
                    safety_score -= 5
                    card("major", "⚠️ Mildly Elevated ALT",
                        f"ALT = <b>{alt} U/L</b>. Monitor liver function. Caution with hepatotoxic drugs.")

                if platelets < 50:
                    safety_score -= 20
                    card("critical", "🚨 CRITICAL — Severe Thrombocytopenia",
                        f"Platelets = <b>{platelets}</b>. Avoid all antiplatelet and anticoagulant drugs.")
                    intervention_notes.append(f"CRITICAL: Platelets {platelets} — Avoid antiplatelets/anticoagulants")
                elif platelets < 100:
                    safety_score -= 10
                    card("major", "⚠️ Low Platelets",
                        f"Platelets = <b>{platelets}</b>. Increased bleeding risk. Use anticoagulants and NSAIDs with extreme caution.")
                    intervention_notes.append(f"Low Platelets {platelets} — Caution with anticoagulants")

                if potassium >= 6.0:
                    safety_score -= 20
                    card("critical", "🚨 CRITICAL — Severe Hyperkalemia",
                        f"K+ = <b>{potassium} mEq/L</b>. Avoid potassium-sparing diuretics, ACE inhibitors, and ARBs immediately.")
                    intervention_notes.append(f"CRITICAL: K+ {potassium} — Severe hyperkalemia")
                elif potassium >= 5.5:
                    safety_score -= 10
                    card("major", "⚠️ Hyperkalemia",
                        f"K+ = <b>{potassium} mEq/L</b>. Review potassium-raising drugs.")
                    intervention_notes.append(f"High K+ {potassium} — Review potassium-raising drugs")
                elif potassium <= 3.0:
                    safety_score -= 15
                    card("critical", "🚨 CRITICAL — Severe Hypokalemia",
                        f"K+ = <b>{potassium} mEq/L</b>. High risk of cardiac arrhythmia — especially dangerous with Digoxin.")
                    intervention_notes.append(f"CRITICAL: K+ {potassium} — Severe hypokalemia")
                elif potassium <= 3.5:
                    safety_score -= 5
                    card("minor", "⚠️ Mild Hypokalemia",
                        f"K+ = <b>{potassium} mEq/L</b>. Monitor — increases Digoxin toxicity risk.")
                    intervention_notes.append(f"Low K+ {potassium} — Monitor electrolytes")

                # ── 1. RENAL ─────────────────────────────────────────
                if renal_function is not None:
                    for drug in found_drugs:
                        tiers = sorted(drug_db[drug].get("renal_logic", []), key=lambda x: x["cutoff"])
                        triggered = False
                        for tier in tiers:
                            if renal_function < tier["cutoff"] and not triggered:
                                triggered = True
                                safety_score -= 15
                                card("critical", f"🔴 Renal Alert — {drug.title()}",
                                    f"{renal_source} = <b>{renal_function}</b> mL/min (below cutoff {tier['cutoff']})<br>"
                                    f"👉 {tier['msg']}",
                                    meta=f"📖 Source: {tier['source']}")
                                intervention_notes.append(f"Renal: Adjust {drug.title()} ({tier['msg']})")
                else:
                    st.warning("⚠️ Skipping Renal Checks: Invalid Creatinine/eGFR data.")

                # ── 2. ALLERGIES ─────────────────────────────────────
                for drug in found_drugs:
                    d_class = drug_db[drug]["class"]
                    if "Penicillin" in known_allergies and "Penicillin" in d_class:
                        safety_score -= 50
                        card("critical", f"🚨 ANAPHYLAXIS RISK — {drug.title()}",
                            f"Patient has <b>Penicillin Allergy</b>. {drug.title()} is a Penicillin — STOP immediately.")
                        intervention_notes.append(f"STOP {drug.title()} (Allergy)")
                    if "Aspirin/NSAIDs" in known_allergies and ("NSAID" in d_class or "Aspirin" in drug):
                        safety_score -= 30
                        card("critical", f"🚨 Allergy — {drug.title()}",
                            f"Patient has <b>Aspirin/NSAID Allergy</b>. {drug.title()} is an NSAID — review immediately.")
                        intervention_notes.append(f"STOP {drug.title()} (NSAID Allergy)")

                # ── 3. LIFESTYLE ─────────────────────────────────────
                for drug in found_drugs:
                    for factor in lifestyle:
                        if factor in drug_db[drug].get("lifestyle_risk", []):
                            safety_score -= 5
                            card("minor", f"🍎 Lifestyle Interaction — {drug.title()}",
                                f"{drug.title()} interacts with <b>{factor}</b>. Counsel patient accordingly.")
                            intervention_notes.append(f"Counsel: {drug.title()} + {factor}")

                # ── 4. CONTRAINDICATIONS ─────────────────────────────
                for drug in found_drugs:
                    for cond in comorbidities:
                        if cond in drug_db[drug]["contra_diseases"]:
                            safety_score -= 20
                            card("critical", f"🚫 Contraindication — {drug.title()}",
                                f"{drug.title()} is <b>contraindicated</b> in <b>{cond}</b>. Review prescription urgently.")
                            intervention_notes.append(f"Contraindicated: {drug.title()} in {cond}")

                # ── 5. INTERACTIONS ──────────────────────────────────
                for i in range(len(found_drugs)):
                    for j in range(i + 1, len(found_drugs)):
                        d1, d2 = found_drugs[i], found_drugs[j]
                        rule = interactions_db.get((d1, d2)) or interactions_db.get((d2, d1))
                        if rule:
                            mechanism = rule.get("mechanism", "")
                            source = rule.get("source", "")
                            meta_parts = []
                            if mechanism: meta_parts.append(f"🔬 <b>Mechanism:</b> {mechanism}")
                            if source:    meta_parts.append(f"📖 <b>Source:</b> {source}")
                            meta_str = "<br>".join(meta_parts)

                            if rule['level'] == "CRITICAL":
                                safety_score -= 20
                                card("critical",
                                    f"🚨 CRITICAL INTERACTION — {d1.title()} + {d2.title()}",
                                    rule['msg'], meta=meta_str)
                            elif rule['level'] == "Major":
                                safety_score -= 10
                                card("major",
                                    f"⚠️ Major Interaction — {d1.title()} + {d2.title()}",
                                    rule['msg'], meta=meta_str)
                            else:
                                safety_score -= 5
                                card("minor",
                                    f"ℹ️ Minor Interaction — {d1.title()} + {d2.title()}",
                                    rule['msg'], meta=meta_str)
                            intervention_notes.append(
                                f"Interaction ({rule['level']}): {d1.title()} + {d2.title()} — {rule['msg']}")

                # ── REPORT ───────────────────────────────────────────
                st.markdown("---")
                final_score = max(0, safety_score)
                if final_score >= 80:
                    badge_class, score_label = "score-safe", "✅ Low Risk"
                elif final_score >= 50:
                    badge_class, score_label = "score-warn", "⚠️ Moderate Risk"
                else:
                    badge_class, score_label = "score-danger", "🚨 High Risk"

                st.markdown(
                    f'<div class="score-badge {badge_class}">{score_label} &nbsp;|&nbsp; Safety Score: {final_score}/100</div>',
                    unsafe_allow_html=True)

                with st.expander("📋 Pharmacist Intervention Note"):
                    st.code("\n".join(intervention_notes) if intervention_notes else "No significant issues found.")

# ==========================================
# TAB 2: PARENTERAL (IV) DILUTION
# ==========================================
with tab2:
    st.header("💉 Parenteral (IV) Reconstitution & Dilution")
    iv_col1, iv_col2 = st.columns([1, 1.2])

    with iv_col1:
        st.subheader("1. Drug Selection")
        selected_iv_drug = st.selectbox("Select Vial/Drug:", list(parenteral_db.keys()))
        iv_data = parenteral_db[selected_iv_drug]

        st.markdown(f"""
        <div style="background-color: #e8f8f5; padding: 15px; border-radius: 5px; color:black;">
        <b>📦 Vial Strength:</b> {iv_data['strength_mg']} mg<br>
        <b>💧 Diluent:</b> {iv_data['diluent']}<br>
        <b>➕ Reconstitution Vol:</b> Add <b>{iv_data['reconst_vol_ml']} mL</b>
        </div>
        """, unsafe_allow_html=True)

        st.write("---")
        st.subheader("2. Patient Requirement")
        dose_req = st.number_input("Dose Required (mg):", 1.0, 5000.0, float(iv_data['strength_mg']), step=50.0)

    with iv_col2:
        st.subheader("3. Preparation Guide")
        if st.button("Calculate Preparation ⚗️", use_container_width=True):
            final_conc = iv_data['final_conc']
            vol_to_draw = dose_req / final_conc
            vials_needed = dose_req / iv_data['strength_mg']

            st.success(f"### 👉 Draw: {round(vol_to_draw, 2)} mL")
            if vials_needed > 1.0:
                st.warning(f"⚠️ **Note:** Patient needs {round(vials_needed, 2)} vials (Use {math.ceil(vials_needed)} full vials).")

            st.markdown(f"""
            **Step-by-Step Instructions:**
            1. Take **{selected_iv_drug}**.
            2. Add **{iv_data['reconst_vol_ml']} mL** of {iv_data['diluent']}.
            3. Shake well. Final concentration is **{iv_data['final_conc']} mg/mL**.
            4. Withdraw **{round(vol_to_draw, 2)} mL** to get **{dose_req} mg**.
            """)

            st.info(f"""
            **ℹ️ Administration:**
            * **Compatible Fluids:** {', '.join(iv_data['compatible_fluids'])}
            * **Rate:** {iv_data['rate_iv']}
            * **Stability:** {iv_data['stability']}
            """)

# ==========================================
# TAB 3: AI CONSULT
# ==========================================
with tab3:
    st.header("🤖 AI Clinical Copilot")
    st.info("Ask complex clinical questions that go beyond standard guidelines.")
    user_query = st.text_area("Doctor's Query:", placeholder="e.g. Patient on Warfarin has a toothache. What is the safest painkiller?")

    if st.button("Ask AI Assistant"):
        st.info("⚠️ **Demo Mode:** The AI Neural Engine is currently offline (API Key required).")
        st.markdown("""
        **System Capabilities (when online):**
        1. Analyzes complex drug interactions not in the standard database.
        2. References latest NICE/BNF guidelines dynamically.
        3. Provides dosing adjustments for rare comorbidities.
        """)

# --- FOOTER ---
st.markdown("---")
st.caption("RxGuard Ultimate © 2026 | Clinical Decision Support System | Disclaimer: This tool is decision support aid only. All alerts must be verified by the treating clinician. Do not modify therapy based solely on this output. Full clinical responsibility remains with the prescriber.")
