import streamlit as st
from PIL import Image
import pytesseract
import math
# import openai # NEW: For the AI Engine (Commented out for Demo stability)

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="RxGuard Ultimate | Clinical CDS",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOGIN SYSTEM ---
def check_password():
    """Returns `True` if the user had the correct password."""
    if st.session_state.get("password_correct", False):
        return True

    st.markdown("""
        <style>
        .stTextInput > div > div > input {text-align: center;}
        </style>
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
    .stExpander { border: 1px solid #ddd; border-radius: 5px; background-color: #f0f2f6; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; }
    .section-header { font-size: 1.2rem; font-weight: bold; color: #2e86c1; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# RXGUARD — DATABASE LOADER
# ============================================================
# INSTRUCTIONS:
#   1. Place drugs.json, interactions.json, parenteral.json
#      in the SAME FOLDER as app.py
#   2. Find "# --- 2. DATABASES ---" in your app.py
#   3. DELETE everything from that line down to the end of
#      the parenteral_db = { ... } block (~500 lines)
#   4. PASTE this entire file in its place
#   5. Save and run. Nothing else in your app needs to change.
# ============================================================

import json
import os

# ── Helper: resolve path relative to this script ──────────
_DIR = os.path.dirname(os.path.abspath(__file__))

def _load(filename):
    path = os.path.join(_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- 2. DATABASES ---

# A. Drug database — keyed by lowercase drug name
drug_db = _load("drugs.json")

# B. Interaction database
# JSON keys use "drug1|drug2" format (pipe separator).
# We rebuild the tuple-keyed dict your logic engine already uses,
# so ZERO changes are needed anywhere else in app.py.
_raw_interactions = _load("interactions.json")

interactions_db = {}
for key, value in _raw_interactions.items():
    parts = key.split("|")
    if len(parts) == 2:
        d1, d2 = parts[0].strip(), parts[1].strip()
        interactions_db[(d1, d2)] = value

# C. Parenteral / IV database
parenteral_db = _load("parenteral.json")

# ── Quick sanity check (prints to terminal, not to Streamlit) ──
if __name__ == "__main__":
    print(f"Loaded {len(drug_db)} drugs")
    print(f"Loaded {len(interactions_db)} interaction pairs")
    print(f"Loaded {len(parenteral_db)} IV drugs")

def calculate_crcl(age, weight_kg, gender, scr):
    if scr <= 0: return None
    factor = 0.85 if gender == "Female" else 1.0
    crcl = ((140 - age) * weight_kg) / (72 * scr)
    return round(crcl * factor, 2)

# --- 3. SIDEBAR LAYOUT ---
with st.sidebar:
    st.title("⚕️ RxGuard Ultimate")
    
    # A. Demographics
    st.markdown("### 1. Patient Data")
    age = st.number_input("Age (Years)", 0, 120, 25)
    gender = st.radio("Gender", ["Male", "Female"], horizontal=True)
    c1, c2 = st.columns([2, 1])
    with c1: weight_val = st.number_input("Weight", 1.0, 300.0, 70.0, step=0.5)
    with c2: weight_unit = st.selectbox("Unit", ["kg", "lbs"])
    weight_kg = weight_val if weight_unit == "kg" else weight_val * 0.453592
    
    # B. LAB REPORTS (Expanded)
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
    
    # Logic to select best renal function metric
    if egfr > 0:
        renal_function = egfr
        renal_source = "eGFR (Lab)"
    elif crcl_calc is not None:
        renal_function = crcl_calc
        renal_source = "Calculated CrCl"
    else:
        renal_function = None
        renal_source = "N/A (Invalid SCr)"
    
    # C. History
    with st.expander("📜 History & Allergies"):
        comorbidities = st.multiselect("Conditions:", ["Hypertension", "Diabetes T2DM", "Asthma", "Heart Failure", "Peptic Ulcer", "CKD", "Epilepsy", "Rheumatoid Arthritis"])
        known_allergies = st.multiselect("Allergies:", ["Penicillin", "Sulfa Drugs", "Aspirin/NSAIDs"])
        lifestyle = st.multiselect("Lifestyle:", ["Alcohol", "Smoking", "Vitamin K Rich Diet", "Dairy Products", "Grapefruit Juice"])

    st.divider()
    st.caption(f"Calculated Weight: {round(weight_kg, 1)} kg | CrCl: {crcl_calc if crcl_calc else 'N/A'} mL/min")

# --- 4. MAIN APP TABS ---
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
            if st.button("Analyze Rx"): run_analysis = True
        else:
            uploaded_file = st.file_uploader("Upload Rx", type=["jpg", "png"])
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, use_column_width=True)
                if st.button("Extract Text"):
                    try:
                        text_input = pytesseract.image_to_string(img)
                        if not text_input.strip():
                            st.warning("OCR detected no text. Image might be too blurry.")
                        else:
                            st.success("OCR Done")
                            run_analysis = True
                    except Exception as e:
                        st.error("OCR Error: Tesseract engine not found.")
                        st.info("If running locally, install Tesseract-OCR. If online, ensure packages are installed.")

    with col_out:
        if run_analysis and text_input:
            
            # Display Patient Context
            st.info(f"""
            **Patient Context:**
            * **Renal:** {renal_function if renal_function else 'N/A'} mL/min ({renal_source})
            * **Liver (ALT):** {alt} U/L | **INR:** {inr} | **Platelets:** {platelets}
            """)
            
            text_lower = text_input.lower()
            found_drugs = [d for d in drug_db.keys() if d in text_lower]
            
            safety_score = 100
            intervention_notes = []

            if not found_drugs:
                st.warning("No Formulary Drugs Detected in text.")
            else:
                st.success(f"Detected: {', '.join([d.title() for d in found_drugs])}")
                
               # --- LOGIC ENGINE ---
                # 0. LAB VALUE ALERTS
                if inr >= 4.0:
                    safety_score -= 20
                    st.error(f"🚨 **CRITICAL — INR {inr}:** Supratherapeutic INR detected. Serious bleeding risk. Review all anticoagulants immediately.")
                    intervention_notes.append(f"CRITICAL: INR {inr} — Review anticoagulation urgently")
                elif inr >= 3.0:
                    safety_score -= 10
                    st.warning(f"⚠️ **INR {inr}:** Above therapeutic range. Monitor closely and review anticoagulant dosing.")
                    intervention_notes.append(f"High INR {inr} — Monitor anticoagulation")
                if alt >= 100:
                    safety_score -= 15
                    st.error(f"🚨 **Elevated ALT ({alt} U/L):** Significant hepatotoxicity risk. Review all hepatotoxic drugs.")
                    for drug in found_drugs:
                        if drug_db[drug].get("hepatic_risk"):
                            st.error(f"   ⚠️ {drug.title()} is hepatotoxic — use with caution or avoid.")
                            intervention_notes.append(f"Hepatic Risk: {drug.title()} with ALT {alt}")
                elif alt >= 60:
                    safety_score -= 5
                    st.warning(f"⚠️ **ALT mildly elevated ({alt} U/L):** Monitor liver function. Caution with hepatotoxic drugs.")
                if platelets < 50:
                    safety_score -= 20
                    st.error(f"🚨 **CRITICAL — Platelets {platelets}:** Severe thrombocytopenia. Avoid all antiplatelet and anticoagulant drugs.")
                    intervention_notes.append(f"CRITICAL: Platelets {platelets} — Avoid antiplatelets/anticoagulants")
                elif platelets < 100:
                    safety_score -= 10
                    st.warning(f"⚠️ **Low Platelets ({platelets}):** Increased bleeding risk. Use anticoagulants and NSAIDs with extreme caution.")
                    intervention_notes.append(f"Low Platelets {platelets} — Caution with anticoagulants")
                if potassium >= 6.0:
                    safety_score -= 20
                    st.error(f"🚨 **CRITICAL — K+ {potassium} mEq/L:** Severe hyperkalemia. Avoid potassium-sparing diuretics, ACE inhibitors, ARBs immediately.")
                    intervention_notes.append(f"CRITICAL: K+ {potassium} — Severe hyperkalemia")
                elif potassium >= 5.5:
                    safety_score -= 10
                    st.warning(f"⚠️ **K+ {potassium} mEq/L:** Hyperkalemia detected. Review potassium-raising drugs.")
                    intervention_notes.append(f"High K+ {potassium} — Review potassium-raising drugs")
                elif potassium <= 3.0:
                    safety_score -= 15
                    st.error(f"🚨 **CRITICAL — K+ {potassium} mEq/L:** Severe hypokalemia. High risk of cardiac arrhythmia — especially dangerous with Digoxin.")
                    intervention_notes.append(f"CRITICAL: K+ {potassium} — Severe hypokalemia")
                elif potassium <= 3.5:
                    safety_score -= 5
                    st.warning(f"⚠️ **K+ {potassium} mEq/L:** Mild hypokalemia. Monitor — increases Digoxin toxicity risk.")
                    intervention_notes.append(f"Low K+ {potassium} — Monitor electrolytes")
                # 1. RENAL
                # 1. RENAL
                if renal_function is not None:
                    for drug in found_drugs:
                        tiers = sorted(drug_db[drug].get("renal_logic", []), key=lambda x: x["cutoff"])
                        triggered = False
                        for tier in tiers:
                            if renal_function < tier["cutoff"] and not triggered:
                                triggered = True; safety_score -= 15
                                st.error(f"**{drug.title()} Alert:** {renal_source} < {tier['cutoff']}")
                                st.write(f"👉 {tier['msg']}")
                                intervention_notes.append(f"Renal: Adjust {drug.title()} ({tier['msg']})")
                else:
                    st.warning("⚠️ Skipping Renal Checks: Invalid Creatinine/eGFR data.")

                # 2. ALLERGIES
                for drug in found_drugs:
                    d_class = drug_db[drug]["class"]
                    if "Penicillin" in known_allergies and "Penicillin" in d_class:
                        safety_score -= 50
                        st.error(f"🚨 **ANAPHYLAXIS RISK:** {drug.title()} in Penicillin Allergy!")
                        intervention_notes.append(f"STOP {drug.title()} (Allergy)")
                    if "Aspirin/NSAIDs" in known_allergies and ("NSAID" in d_class or "Aspirin" in drug):
                        safety_score -= 30; st.error(f"🚨 **Allergy:** {drug.title()} (NSAID)"); intervention_notes.append(f"STOP {drug.title()}")

                # 3. LIFESTYLE
                for drug in found_drugs:
                    for factor in lifestyle:
                        if factor in drug_db[drug].get("lifestyle_risk", []):
                            safety_score -= 5
                            st.warning(f"🍎 **Interaction:** {drug.title()} + {factor}")
                            intervention_notes.append(f"Counsel: {drug.title()} + {factor}")

                # 4. CONTRAINDICATIONS
                for drug in found_drugs:
                    for cond in comorbidities:
                        if cond in drug_db[drug]["contra_diseases"]:
                            safety_score -= 20
                            st.error(f"**CONTRAINDICATION:** {drug.title()} in {cond}")
                            intervention_notes.append(f"Contraindicated: {drug.title()} in {cond}")

             # 5. INTERACTIONS
ddi_found = False
for i in range(len(found_drugs)):
    for j in range(i + 1, len(found_drugs)):
        d1, d2 = found_drugs[i], found_drugs[j]
        rule = interactions_db.get((d1, d2)) or interactions_db.get((d2, d1))
        if rule:
            ddi_found = True
            mechanism = rule.get("mechanism", "")
            source = rule.get("source", "")
            if rule['level'] == "CRITICAL":
                safety_score -= 20
                st.error(f"🚨 **CRITICAL — {d1.title()} + {d2.title()}:** {rule['msg']}")
            else:
                safety_score -= 10
                st.warning(f"⚠️ **{rule['level']} — {d1.title()} + {d2.title()}:** {rule['msg']}")
            if mechanism:
                st.caption(f"🔬 **Mechanism:** {mechanism}")
            if source:
                st.caption(f"📖 **Source:** {source}")
            intervention_notes.append(f"Interaction ({rule['level']}): {d1.title()} + {d2.title()} — {rule['msg']}")
# ==========================================
# TAB 2: PARENTERAL (IV) DILUTION
# ==========================================
with tab2:
    st.header("💉 Parenteral (IV) Reconstitution & Dilution")
    
    # Layout: 2 Columns
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
            # Math Logic for IV
            # 1. Final Concentration
            final_conc = iv_data['final_conc']
            
            # 2. Volume to Draw = Dose / Concentration
            vol_to_draw = dose_req / final_conc
            
            # 3. Warning if dose exceeds vial
            vials_needed = dose_req / iv_data['strength_mg']
            
            # DISPLAY RESULTS
            st.success(f"### 👉 Draw: {round(vol_to_draw, 2)} mL")
            
            if vials_needed > 1.0:
                st.warning(f"⚠️ **Note:** Patient needs {round(vials_needed, 2)} vials (Use {math.ceil(vials_needed)} full vials).")
            
            st.markdown(f"""
            **Step-by-Step Instructions:**
            1.  Take **{selected_iv_drug}**.
            2.  Add **{iv_data['reconst_vol_ml']} mL** of {iv_data['diluent']}.
            3.  Shake well. The final concentration is **{iv_data['final_conc']} mg/mL**.
            4.  Withdraw **{round(vol_to_draw, 2)} mL** to get **{dose_req} mg**.
            """)
            
            st.info(f"""
            **ℹ️ Administration:**
            * **Compatible Fluids:** {', '.join(iv_data['compatible_fluids'])}
            * **Rate:** {iv_data['rate_iv']}
            * **Stability:** {iv_data['stability']}
            """)

# ==========================================
# TAB 3: AI CONSULT (DEMO VERSION)
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
        
        # NOTE: The code below is disabled for the demo to prevent crashes without internet.
        # api_key = st.secrets.get("OPENAI_API_KEY") 
        # if not api_key:
        #     st.error("⚠️ AI Key is missing.")
        # else:
        #     try:
        #         client = openai.OpenAI(api_key=api_key)
        #         response = client.chat.completions.create(
        #             model="gpt-4o-mini",
        #             messages=[{"role": "user", "content": user_query}]
        #         )
        #         st.write(response.choices[0].message.content)
        #     except Exception as e:
        #         st.error(f"AI Error: {e}")

# --- 5. FOOTER ---
st.markdown("---")
st.caption("RxGuard Ultimate © 2026 | Clinical Decision Support System | Disclaimer: This tool is decision support aid only, All alerts must be verified by the treating clinician. Do not modify therapy based solely on this output. Full clinical responsibility remains with the prescriber.")
