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

# --- 2. DATABASES ---

# A. MAIN DRUG DATABASE
drug_db = {
    "methotrexate": {
        "class": "Antimetabolite", "indication": "RA, Psoriasis, Cancer",
        "adr": "Pulmonary fibrosis, hepatotoxicity, bone marrow suppression.", "adr_source": "BNF 84: Section 10.1.3",
        "hepatic_risk": True, "contra_diseases": ["Active Infection", "Liver Disease", "Immunodeficiency"],
        "preg_cat": "X", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 50, "msg": "Reduce dose by 50%.", "source": "BNF Renal"}, {"cutoff": 20, "msg": "CONTRAINDICATED.", "source": "Katzung"}]
    },
    "phenytoin": {
        "class": "Antiepileptic", "indication": "Epilepsy",
        "adr": "Gingival hypertrophy, nystagmus, ataxia.", "adr_source": "Katzung Ch 24",
        "hepatic_risk": True, "contra_diseases": ["Heart Block"],
        "preg_cat": "D", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "theophylline": {
        "class": "Xanthine", "indication": "Asthma, COPD",
        "adr": "Tachycardia, seizures, nausea.", "adr_source": "BNF 84: Section 3.1.3",
        "hepatic_risk": True, "contra_diseases": ["Arrhythmia", "Peptic Ulcer"],
        "preg_cat": "C", "lifestyle_risk": ["Smoking"], "renal_logic": []
    },
    "carbamazepine": {
        "class": "Antiepileptic", "indication": "Epilepsy, Bipolar",
        "adr": "Hyponatremia (SIADH), agranulocytosis.", "adr_source": "BNF 84: Section 4.8.1",
        "hepatic_risk": True, "contra_diseases": ["Bone Marrow Depression"],
        "preg_cat": "D", "lifestyle_risk": ["Grapefruit Juice"], "renal_logic": []
    },
    "vancomycin": {
        "class": "Glycopeptide", "indication": "MRSA Infection",
        "adr": "Nephrotoxicity, Red Man Syndrome.", "adr_source": "Sanford Guide",
        "hepatic_risk": False, "contra_diseases": ["Hearing Loss"],
        "preg_cat": "C", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 60, "msg": "Check trough levels.", "source": "Sanford"}, {"cutoff": 30, "msg": "Renal Consult required.", "source": "Renal Handbook"}]
    },
    "warfarin": {
        "class": "Anticoagulant", "indication": "Anticoagulation",
        "adr": "Hemorrhage.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Active Bleeding", "Hypertension"],
        "preg_cat": "X", "lifestyle_risk": ["Vitamin K Rich Diet", "Alcohol"], "renal_logic": []
    },
    "lisinopril": {
        "class": "ACE Inhibitor", "indication": "Hypertension, Heart Failure",
        "adr": "Dry cough, hyperkalemia.", "adr_source": "DiPiro",
        "hepatic_risk": False, "contra_diseases": ["Angioedema", "Hyperkalemia"],
        "preg_cat": "X", "lifestyle_risk": ["Potassium Supplements"],
        "renal_logic": [{"cutoff": 30, "msg": "Reduce dose. Initiate 2.5mg.", "source": "BNF Renal"}]
    },
    "digoxin": {
        "class": "Antiarrhythmic", "indication": "Heart Failure, Arrhythmia",
        "adr": "Nausea, yellow halos.", "adr_source": "Katzung",
        "hepatic_risk": False, "contra_diseases": ["VFib"],
        "preg_cat": "C", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 50, "msg": "Reduce dose 50%.", "source": "Katzung"}]
    },
    "amiodarone": {
        "class": "Antiarrhythmic", "indication": "Arrhythmia",
        "adr": "Pulmonary fibrosis, thyroid dysfunction.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Thyroid Dysfunction"],
        "preg_cat": "D", "lifestyle_risk": ["Grapefruit Juice"], "renal_logic": []
    },
    "propranolol": {
        "class": "Beta Blocker", "indication": "Hypertension, Anxiety",
        "adr": "Bradycardia, bronchospasm.", "adr_source": "Katzung",
        "hepatic_risk": True, "contra_diseases": ["Asthma", "COPD", "Bradycardia"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "amoxicillin": {
        "class": "Penicillin", "indication": "Infection",
        "adr": "Diarrhea, rash.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Penicillin Allergy"],
        "preg_cat": "B", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 30, "msg": "Max 500mg BID.", "source": "BNF 84"}]
    },
    "gentamicin": {
        "class": "Aminoglycoside", "indication": "Infection",
        "adr": "Nephrotoxicity, ototoxicity.", "adr_source": "Katzung",
        "hepatic_risk": False, "contra_diseases": ["Myasthenia Gravis"],
        "preg_cat": "D", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 60, "msg": "Extend interval.", "source": "Sanford"}]
    },
    "ciprofloxacin": {
        "class": "Fluoroquinolone", "indication": "Infection",
        "adr": "Tendonitis, QT prolongation.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["G6PD Deficiency"],
        "preg_cat": "C", "lifestyle_risk": ["Dairy Products"],
        "renal_logic": [{"cutoff": 30, "msg": "Max 500mg daily.", "source": "Renal Handbook"}]
    },
    "ibuprofen": {
        "class": "NSAID", "indication": "Pain/Inflammation",
        "adr": "GI bleeding, renal impairment.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Peptic Ulcer", "Heart Failure", "CKD"],
        "preg_cat": "C/D", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 30, "msg": "Avoid use.", "source": "Katzung"}]
    },
    "aspirin": {
        "class": "Antiplatelet", "indication": "Pain/Antiplatelet",
        "adr": "GI ulceration, bleeding.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Peptic Ulcer", "Hemophilia"],
        "preg_cat": "D", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "paracetamol": {
        "class": "Analgesic", "indication": "Pain/Fever",
        "adr": "Hepatotoxicity.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Severe Hepatic Failure"],
        "preg_cat": "B", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "metformin": {
        "class": "Biguanide", "indication": "Diabetes T2DM",
        "adr": "Lactic acidosis, GI upset.", "adr_source": "DiPiro",
        "hepatic_risk": False, "contra_diseases": ["CKD", "Metabolic Acidosis"],
        "preg_cat": "B", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 45, "msg": "Max 1000mg daily.", "source": "Guidelines"}, {"cutoff": 30, "msg": "CONTRAINDICATED.", "source": "BNF 84"}]
    },
    "salbutamol": {
        "class": "Beta2 Agonist", "indication": "Asthma",
        "adr": "Tremor, palpitations.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Arrhythmia"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "lithium": {
        "class": "Mood Stabilizer", "indication": "Bipolar Disorder",
        "adr": "Tremor, renal toxicity.", "adr_source": "Katzung",
        "hepatic_risk": False, "contra_diseases": ["Dehydration"],
        "preg_cat": "D", "lifestyle_risk": ["Low Sodium Diet"],
        "renal_logic": [{"cutoff": 50, "msg": "Reduce dose.", "source": "BNF 84"}]
    },
    "levothyroxine": {
        "class": "Thyroid Hormone", "indication": "Thyroid Dysfunction",
        "adr": "Palpitations.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Thyrotoxicosis"],
        "preg_cat": "A", "lifestyle_risk": ["Soy Products"], "renal_logic": []
    },
    "omeprazole": {
        "class": "PPI", "indication": "PUD, GERD",
        "adr": "GI upset, hypo-Mg.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": [],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    }
}

interactions_db = {
    ("warfarin", "aspirin"): {"level": "CRITICAL", "msg": "Significantly increased bleeding risk.", "source": "Stockley’s"},
    ("warfarin", "ibuprofen"): {"level": "CRITICAL", "msg": "Severe GI bleeding risk.", "source": "Stockley’s"},
    ("lisinopril", "ibuprofen"): {"level": "Major", "msg": "Reduced antihypertensive effect + Kidney Risk.", "source": "BNF"},
    ("lisinopril", "lithium"): {"level": "Major", "msg": "Lithium Toxicity Risk.", "source": "Stockley’s"},
    ("digoxin", "amiodarone"): {"level": "Major", "msg": "Digoxin levels increase ~50%.", "source": "DiPiro"},
    ("ciprofloxacin", "warfarin"): {"level": "Major", "msg": "Increased INR/Bleeding.", "source": "BNF"},
    ("propranolol", "salbutamol"): {"level": "Major", "msg": "Antagonistic effect.", "source": "Katzung"},
    ("levothyroxine", "warfarin"): {"level": "Major", "msg": "Enhanced Warfarin effect.", "source": "Stockley’s"},
    ("methotrexate", "ibuprofen"): {"level": "CRITICAL", "msg": "FATAL Toxicity (NSAIDs block MTX excretion).", "source": "Stockley’s"},
    ("methotrexate", "aspirin"): {"level": "CRITICAL", "msg": "FATAL Toxicity (NSAIDs block MTX excretion).", "source": "Stockley’s"},
    ("theophylline", "ciprofloxacin"): {"level": "CRITICAL", "msg": "Theophylline Toxicity (Seizures).", "source": "Stockley’s"},
    ("carbamazepine", "erythromycin"): {"level": "Major", "msg": "Toxicity risk.", "source": "BNF"},
    ("vancomycin", "gentamicin"): {"level": "Major", "msg": "Synergistic Nephrotoxicity.", "source": "Sanford"},
    ("phenytoin", "warfarin"): {"level": "Major", "msg": "Unstable INR.", "source": "Stockley’s"}
}

# B. PARENTERAL (IV) DILUTION DATABASE
parenteral_db = {
    "Ceftriaxone 1g Vial": {
        "strength_mg": 1000,
        "diluent": "Water for Injection or 1% Lidocaine (IM)",
        "reconst_vol_ml": 9.6,
        "final_vol_ml": 10.0,
        "final_conc": 100.0,
        "compatible_fluids": ["NS", "D5W", "LR"],
        "rate_iv": "Slow IV Push over 2-4 mins or Infusion over 30 mins",
        "stability": "Use immediately (stable 24h in fridge)"
    },
    "Vancomycin 500mg Vial": {
        "strength_mg": 500,
        "diluent": "Water for Injection",
        "reconst_vol_ml": 10.0,
        "final_vol_ml": 10.0,
        "final_conc": 50.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Intermittent Infusion over at least 60 mins (Red Man Syndrome Risk)",
        "stability": "Reconstituted solution is stable for 14 days in fridge"
    },
    "Meropenem 1g Vial": {
        "strength_mg": 1000,
        "diluent": "Water for Injection",
        "reconst_vol_ml": 20.0,
        "final_vol_ml": 20.0,
        "final_conc": 50.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "IV Bolus over 3-5 mins or Infusion over 15-30 mins",
        "stability": "Use within 2-3 hours if stored at room temp"
    },
    "Hydrocortisone 100mg Vial": {
        "strength_mg": 100,
        "diluent": "Water for Injection",
        "reconst_vol_ml": 2.0,
        "final_vol_ml": 2.0,
        "final_conc": 50.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Slow IV Push over 30 seconds or IV Infusion",
        "stability": "Use within 3 days if protected from light"
    },
    "Pantoprazole 40mg Vial": {
        "strength_mg": 40,
        "diluent": "0.9% Sodium Chloride",
        "reconst_vol_ml": 10.0,
        "final_vol_ml": 10.0,
        "final_conc": 4.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "IV Push over 2 mins or Infusion over 15 mins",
        "stability": "Use within 12 hours"
    },
    "Piperacillin/Tazo 4.5g": {
        "strength_mg": 4500,
        "diluent": "NS or WFI",
        "reconst_vol_ml": 20.0,
        "final_vol_ml": 23.0,
        "final_conc": 200.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Infusion over 30 mins (Extended infusion 3-4h preferred)",
        "stability": "Use within 24h at room temp"
    }
}

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
                            if rule['level'] == "CRITICAL": 
                                safety_score -= 20
                                st.error(f"**{d1.title()} + {d2.title()}:** {rule['msg']}")
                            else: 
                                safety_score -= 10
                                st.warning(f"**{d1.title()} + {d2.title()}:** {rule['msg']}")
                            intervention_notes.append(f"Interaction: {d1.title()} + {d2.title()}")
                
                # REPORT
                st.divider()
                m1, m2 = st.columns([1, 2])
                with m1: st.metric("Safety Score", f"{max(0, safety_score)}/100")
                with m2: 
                    with st.expander("📋 Pharmacist Note"): st.code("\n".join(intervention_notes) if intervention_notes else "No significant issues found.")

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
st.caption("RxGuard Ultimate © 2026 | Clinical Decision Support System | Disclaimer: Use clinical judgment.")