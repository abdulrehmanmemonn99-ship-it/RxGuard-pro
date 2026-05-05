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

# =========================================================
# RXGUARD ULTIMATE — EXPANDED DATABASES
# Replace the entire "# --- 2. DATABASES ---" section
# in your main app.py with this code.
# =========================================================

# --- 2. DATABASES ---

# A. MAIN DRUG DATABASE
drug_db = {

    # ── EXISTING DRUGS (kept + reviewed) ──────────────────

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
        "adr": "Dry cough, hyperkalemia, angioedema.", "adr_source": "DiPiro",
        "hepatic_risk": False, "contra_diseases": ["Angioedema", "Hyperkalemia"],
        "preg_cat": "X", "lifestyle_risk": ["Potassium Supplements"],
        "renal_logic": [{"cutoff": 30, "msg": "Reduce dose. Initiate 2.5mg.", "source": "BNF Renal"}]
    },
    "digoxin": {
        "class": "Antiarrhythmic", "indication": "Heart Failure, Arrhythmia",
        "adr": "Nausea, yellow halos, bradycardia.", "adr_source": "Katzung",
        "hepatic_risk": False, "contra_diseases": ["VFib"],
        "preg_cat": "C", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 50, "msg": "Reduce dose 50%.", "source": "Katzung"}]
    },
    "amiodarone": {
        "class": "Antiarrhythmic", "indication": "Arrhythmia",
        "adr": "Pulmonary fibrosis, thyroid dysfunction, hepatotoxicity.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Thyroid Dysfunction"],
        "preg_cat": "D", "lifestyle_risk": ["Grapefruit Juice"], "renal_logic": []
    },
    "propranolol": {
        "class": "Beta Blocker", "indication": "Hypertension, Anxiety",
        "adr": "Bradycardia, bronchospasm, fatigue.", "adr_source": "Katzung",
        "hepatic_risk": True, "contra_diseases": ["Asthma", "COPD", "Bradycardia"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "amoxicillin": {
        "class": "Penicillin", "indication": "Bacterial Infection",
        "adr": "Diarrhea, rash, hypersensitivity.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Penicillin Allergy"],
        "preg_cat": "B", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 30, "msg": "Max 500mg BID.", "source": "BNF 84"}]
    },
    "gentamicin": {
        "class": "Aminoglycoside", "indication": "Gram-negative Infection",
        "adr": "Nephrotoxicity, ototoxicity.", "adr_source": "Katzung",
        "hepatic_risk": False, "contra_diseases": ["Myasthenia Gravis"],
        "preg_cat": "D", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 60, "msg": "Extend dosing interval.", "source": "Sanford"}, {"cutoff": 30, "msg": "Avoid unless essential; therapeutic drug monitoring required.", "source": "Renal Handbook"}]
    },
    "ciprofloxacin": {
        "class": "Fluoroquinolone", "indication": "Urinary/Respiratory Infection",
        "adr": "Tendonitis, QT prolongation, C. difficile risk.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["G6PD Deficiency"],
        "preg_cat": "C", "lifestyle_risk": ["Dairy Products"],
        "renal_logic": [{"cutoff": 30, "msg": "Max 500mg daily.", "source": "Renal Handbook"}]
    },
    "ibuprofen": {
        "class": "NSAID", "indication": "Pain, Inflammation",
        "adr": "GI bleeding, renal impairment, cardiovascular risk.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Peptic Ulcer", "Heart Failure", "CKD"],
        "preg_cat": "C/D", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 30, "msg": "Avoid use.", "source": "Katzung"}]
    },
    "aspirin": {
        "class": "Antiplatelet / NSAID", "indication": "Pain, Antiplatelet Therapy",
        "adr": "GI ulceration, bleeding, Reye's syndrome in children.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Peptic Ulcer", "Hemophilia"],
        "preg_cat": "D", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "paracetamol": {
        "class": "Analgesic / Antipyretic", "indication": "Pain, Fever",
        "adr": "Hepatotoxicity (overdose).", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Severe Hepatic Failure"],
        "preg_cat": "B", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "metformin": {
        "class": "Biguanide", "indication": "Type 2 Diabetes",
        "adr": "Lactic acidosis, GI upset, B12 deficiency.", "adr_source": "DiPiro",
        "hepatic_risk": False, "contra_diseases": ["CKD", "Metabolic Acidosis", "Heart Failure"],
        "preg_cat": "B", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 45, "msg": "Max 1000mg daily.", "source": "Guidelines"}, {"cutoff": 30, "msg": "CONTRAINDICATED.", "source": "BNF 84"}]
    },
    "salbutamol": {
        "class": "Beta2 Agonist", "indication": "Asthma, COPD",
        "adr": "Tremor, palpitations, hypokalemia.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Arrhythmia"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "lithium": {
        "class": "Mood Stabilizer", "indication": "Bipolar Disorder",
        "adr": "Tremor, renal toxicity, hypothyroidism.", "adr_source": "Katzung",
        "hepatic_risk": False, "contra_diseases": ["Dehydration", "CKD"],
        "preg_cat": "D", "lifestyle_risk": ["Low Sodium Diet"],
        "renal_logic": [{"cutoff": 50, "msg": "Reduce dose; monitor levels closely.", "source": "BNF 84"}, {"cutoff": 30, "msg": "AVOID — high toxicity risk.", "source": "Katzung"}]
    },
    "levothyroxine": {
        "class": "Thyroid Hormone", "indication": "Hypothyroidism",
        "adr": "Palpitations, anxiety, bone loss at high doses.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Thyrotoxicosis"],
        "preg_cat": "A", "lifestyle_risk": ["Soy Products"], "renal_logic": []
    },
    "omeprazole": {
        "class": "PPI", "indication": "PUD, GERD",
        "adr": "GI upset, hypomagnesemia, C. difficile risk.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": [],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },

    # ── NEW DRUGS ──────────────────────────────────────────

    # --- CARDIOLOGY ---
    "amlodipine": {
        "class": "Calcium Channel Blocker", "indication": "Hypertension, Angina",
        "adr": "Peripheral edema, flushing, headache.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Cardiogenic Shock"],
        "preg_cat": "C", "lifestyle_risk": ["Grapefruit Juice"], "renal_logic": []
    },
    "bisoprolol": {
        "class": "Beta Blocker (Selective)", "indication": "Hypertension, Heart Failure, Angina",
        "adr": "Bradycardia, fatigue, bronchospasm.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Asthma", "COPD", "Bradycardia", "Cardiogenic Shock"],
        "preg_cat": "C", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 20, "msg": "Max 10mg daily; use with caution.", "source": "BNF Renal"}]
    },
    "metoprolol": {
        "class": "Beta Blocker (Selective)", "indication": "Hypertension, Heart Failure, MI",
        "adr": "Bradycardia, dizziness, fatigue.", "adr_source": "Katzung",
        "hepatic_risk": True, "contra_diseases": ["Asthma", "Bradycardia", "Cardiogenic Shock"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "metoprolol succinate": {
        "class": "Beta Blocker (Selective, Extended-Release)", "indication": "Hypertension, Heart Failure, Angina",
        "adr": "Bradycardia, dizziness, fatigue.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Asthma", "Bradycardia", "Cardiogenic Shock"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "carvedilol": {
        "class": "Alpha/Beta Blocker", "indication": "Heart Failure, Hypertension",
        "adr": "Dizziness, bradycardia, hypotension.", "adr_source": "DiPiro",
        "hepatic_risk": True, "contra_diseases": ["Asthma", "Bradycardia", "Decompensated Heart Failure"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "atenolol": {
        "class": "Beta Blocker (Selective)", "indication": "Hypertension, Angina",
        "adr": "Bradycardia, fatigue, cold extremities.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Asthma", "COPD", "Bradycardia"],
        "preg_cat": "D", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 35, "msg": "Reduce dose to 50mg daily.", "source": "BNF Renal"}, {"cutoff": 15, "msg": "Max 25mg daily.", "source": "BNF Renal"}]
    },
    "nebivolol": {
        "class": "Beta Blocker (Selective, Vasodilatory)", "indication": "Hypertension, Heart Failure",
        "adr": "Headache, dizziness, bradycardia.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Asthma", "Bradycardia", "Severe Hepatic Impairment"],
        "preg_cat": "C", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 30, "msg": "Start at 1.25mg daily; titrate carefully.", "source": "BNF Renal"}]
    },
    "furosemide": {
        "class": "Loop Diuretic", "indication": "Heart Failure, Edema, Hypertension",
        "adr": "Hypokalemia, hyponatremia, ototoxicity (high dose IV).", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Anuria", "Dehydration", "Hypokalemia"],
        "preg_cat": "C", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 30, "msg": "Higher doses may be required for effect; monitor electrolytes.", "source": "BNF Renal"}]
    },
    "spironolactone": {
        "class": "Potassium-Sparing Diuretic", "indication": "Heart Failure, Hyperaldosteronism",
        "adr": "Hyperkalemia, gynecomastia.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Hyperkalemia", "Anuria", "CKD"],
        "preg_cat": "C", "lifestyle_risk": ["Potassium Supplements"],
        "renal_logic": [{"cutoff": 30, "msg": "Avoid — risk of severe hyperkalemia.", "source": "BNF Renal"}]
    },
    "captopril": {
        "class": "ACE Inhibitor", "indication": "Hypertension, Heart Failure",
        "adr": "Dry cough, hyperkalemia, angioedema.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Angioedema", "Hyperkalemia", "Bilateral Renal Artery Stenosis"],
        "preg_cat": "X", "lifestyle_risk": ["Potassium Supplements"],
        "renal_logic": [{"cutoff": 30, "msg": "Reduce dose; monitor renal function and potassium.", "source": "BNF Renal"}]
    },
    "ramipril": {
        "class": "ACE Inhibitor", "indication": "Hypertension, Heart Failure, Post-MI",
        "adr": "Dry cough, hyperkalemia, angioedema.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Angioedema", "Hyperkalemia", "Bilateral Renal Artery Stenosis"],
        "preg_cat": "X", "lifestyle_risk": ["Potassium Supplements"],
        "renal_logic": [{"cutoff": 30, "msg": "Max 5mg daily; monitor renal function.", "source": "BNF Renal"}]
    },
    "losartan": {
        "class": "ARB", "indication": "Hypertension, Heart Failure, Diabetic Nephropathy",
        "adr": "Hyperkalemia, dizziness, renal impairment.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Hyperkalemia", "Bilateral Renal Artery Stenosis"],
        "preg_cat": "X", "lifestyle_risk": ["Potassium Supplements"],
        "renal_logic": [{"cutoff": 30, "msg": "Use with caution; monitor potassium and renal function.", "source": "BNF Renal"}]
    },
    "losartan + hydrochlorothiazide": {
        "class": "ARB + Thiazide Diuretic (Combination)", "indication": "Hypertension",
        "adr": "Hyperkalemia, hyponatremia, dizziness, renal impairment.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Hyperkalemia", "Anuria", "Bilateral Renal Artery Stenosis"],
        "preg_cat": "X", "lifestyle_risk": ["Potassium Supplements"],
        "renal_logic": [{"cutoff": 30, "msg": "AVOID — thiazide component ineffective and ARB risk increases.", "source": "BNF Renal"}]
    },
    "clopidogrel": {
        "class": "Antiplatelet (P2Y12 Inhibitor)", "indication": "ACS, Stroke Prevention, PCI",
        "adr": "Bleeding, rash, TTP (rare).", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Active Bleeding", "Peptic Ulcer"],
        "preg_cat": "B", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "apixaban": {
        "class": "Direct Oral Anticoagulant (Factor Xa Inhibitor)", "indication": "AF, DVT/PE Prevention & Treatment",
        "adr": "Bleeding, anemia.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Active Bleeding", "Severe Hepatic Impairment"],
        "preg_cat": "B", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 25, "msg": "Reduce dose to 2.5mg BD if 2 of: age≥80, weight≤60kg, SCr≥1.5 mg/dL.", "source": "BNF 84"}]
    },
    "enoxaparin": {
        "class": "Low Molecular Weight Heparin", "indication": "DVT/PE Treatment & Prevention, ACS",
        "adr": "Bleeding, heparin-induced thrombocytopenia (HIT), injection site reactions.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Active Bleeding", "HIT"],
        "preg_cat": "B", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 30, "msg": "Reduce dose by 50% (use 1mg/kg once daily for treatment). Monitor anti-Xa levels.", "source": "BNF Renal"}]
    },
    "heparin": {
        "class": "Anticoagulant (Unfractionated Heparin)", "indication": "DVT/PE, ACS, Anticoagulation",
        "adr": "Bleeding, HIT, osteoporosis (long-term).", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Active Bleeding", "HIT", "Hemophilia"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "isosorbide mononitrate": {
        "class": "Nitrate", "indication": "Angina Prophylaxis, Heart Failure",
        "adr": "Headache, hypotension, tolerance.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Hypotension", "Cardiogenic Shock"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "isosorbide dinitrate": {
        "class": "Nitrate", "indication": "Angina, Acute Heart Failure",
        "adr": "Headache, hypotension, tolerance.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Hypotension", "Cardiogenic Shock"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "nitroglycerin": {
        "class": "Nitrate", "indication": "Acute Angina, Hypertensive Emergency",
        "adr": "Severe headache, reflex tachycardia, hypotension.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Hypotension", "Cardiogenic Shock", "Raised ICP"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "hydralazine": {
        "class": "Vasodilator", "indication": "Hypertension, Hypertensive Emergency in Pregnancy",
        "adr": "Reflex tachycardia, lupus-like syndrome, headache.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Coronary Artery Disease", "Tachycardia"],
        "preg_cat": "C", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 30, "msg": "Reduce dose; increase dosing interval.", "source": "BNF Renal"}]
    },
    "ivabradine": {
        "class": "If Channel Inhibitor", "indication": "Chronic Heart Failure, Stable Angina",
        "adr": "Bradycardia, visual disturbances (phosphenes).", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Bradycardia", "Cardiogenic Shock", "AF"],
        "preg_cat": "X", "lifestyle_risk": ["Grapefruit Juice"], "renal_logic": []
    },
    "norepinephrine": {
        "class": "Vasopressor / Catecholamine", "indication": "Septic Shock, Cardiogenic Shock",
        "adr": "Hypertension, tissue necrosis (extravasation), arrhythmia.", "adr_source": "DiPiro",
        "hepatic_risk": False, "contra_diseases": ["Hypovolemia (uncorrected)"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "dobutamine": {
        "class": "Inotrope / Catecholamine", "indication": "Acute Heart Failure, Cardiogenic Shock",
        "adr": "Tachycardia, arrhythmia, hypertension.", "adr_source": "DiPiro",
        "hepatic_risk": False, "contra_diseases": ["Hypertrophic Obstructive Cardiomyopathy"],
        "preg_cat": "B", "lifestyle_risk": [], "renal_logic": []
    },
    "epinephrine": {
        "class": "Catecholamine / Vasopressor", "indication": "Anaphylaxis, Cardiac Arrest, Severe Asthma",
        "adr": "Tachycardia, hypertension, arrhythmia, anxiety.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": [],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "rosuvastatin": {
        "class": "Statin (HMG-CoA Reductase Inhibitor)", "indication": "Dyslipidemia, Cardiovascular Prevention",
        "adr": "Myopathy, rhabdomyolysis (rare), elevated liver enzymes.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Active Liver Disease", "Myopathy"],
        "preg_cat": "X", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 30, "msg": "Max 10mg daily.", "source": "BNF Renal"}]
    },
    "calcium gluconate": {
        "class": "Electrolyte / Calcium Supplement", "indication": "Hypocalcemia, Hyperkalemia (cardiac protection), Hypermag",
        "adr": "Hypercalcemia, bradycardia (rapid IV), constipation.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Hypercalcemia", "Digoxin Toxicity"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "potassium chloride": {
        "class": "Electrolyte Supplement", "indication": "Hypokalemia",
        "adr": "Hyperkalemia, GI irritation (oral), cardiac arrest (rapid IV).", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Hyperkalemia", "CKD"],
        "preg_cat": "A", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 30, "msg": "Use with extreme caution — high risk of hyperkalemia. Monitor closely.", "source": "BNF Renal"}]
    },
    "lidocaine": {
        "class": "Local Anesthetic / Antiarrhythmic", "indication": "Ventricular Arrhythmia, Local Anesthesia",
        "adr": "Seizures, CNS toxicity, bradycardia.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Heart Block", "Severe Hepatic Failure"],
        "preg_cat": "B", "lifestyle_risk": [], "renal_logic": []
    },

    # --- ANTIBIOTICS / ANTIMICROBIALS ---
    "clindamycin": {
        "class": "Lincosamide Antibiotic", "indication": "Anaerobic Infections, Skin & Bone Infections",
        "adr": "C. difficile colitis, diarrhea, rash.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["C. difficile History"],
        "preg_cat": "B", "lifestyle_risk": [], "renal_logic": []
    },
    "azithromycin": {
        "class": "Macrolide Antibiotic", "indication": "Respiratory / STI Infection",
        "adr": "QT prolongation, GI upset, hepatotoxicity.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["QT Prolongation"],
        "preg_cat": "B", "lifestyle_risk": [], "renal_logic": []
    },
    "metronidazole": {
        "class": "Nitroimidazole Antibiotic", "indication": "Anaerobic Infection, H. pylori, C. difficile",
        "adr": "Metallic taste, nausea, peripheral neuropathy (long-term).", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": [],
        "preg_cat": "B", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "doxycycline": {
        "class": "Tetracycline Antibiotic", "indication": "Respiratory / STI / Malaria Prophylaxis",
        "adr": "Photosensitivity, esophageal irritation, tooth discoloration (children).", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Pregnancy", "Children under 8"],
        "preg_cat": "D", "lifestyle_risk": ["Dairy Products"], "renal_logic": []
    },
    "fluconazole": {
        "class": "Azole Antifungal", "indication": "Candidiasis, Cryptococcal Meningitis",
        "adr": "Hepatotoxicity, QT prolongation, nausea.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["QT Prolongation"],
        "preg_cat": "C/D", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 50, "msg": "Reduce dose by 50%.", "source": "BNF Renal"}]
    },
    "linezolid": {
        "class": "Oxazolidinone Antibiotic", "indication": "MRSA, VRE Infection",
        "adr": "Myelosuppression, serotonin syndrome, peripheral neuropathy.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Uncontrolled Hypertension", "Pheochromocytoma"],
        "preg_cat": "C", "lifestyle_risk": ["Tyramine-Rich Foods"], "renal_logic": []
    },
    "ceftriaxone": {
        "class": "Cephalosporin (3rd Generation)", "indication": "Severe Bacterial Infection, Meningitis, Sepsis",
        "adr": "Hypersensitivity, biliary sludge, C. difficile.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Cephalosporin Allergy", "Hyperbilirubinemia (Neonates)"],
        "preg_cat": "B", "lifestyle_risk": [], "renal_logic": []
    },
    "amoxicillin + clavulanic acid": {
        "class": "Penicillin + Beta-Lactamase Inhibitor (Combination)", "indication": "Mixed Bacterial Infections, UTI, Pneumonia",
        "adr": "Diarrhea, cholestatic jaundice, rash.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Penicillin Allergy", "Severe Hepatic Impairment"],
        "preg_cat": "B", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 30, "msg": "Use amoxicillin/clavulanate 500/125mg BD (avoid 875/125mg formulation).", "source": "BNF Renal"}]
    },
    "rifampicin + isoniazid + pyrazinamide": {
        "class": "Anti-TB Combination (FDC)", "indication": "Tuberculosis (Intensive Phase)",
        "adr": "Hepatotoxicity, peripheral neuropathy, red-orange discoloration of urine.", "adr_source": "WHO TB Guidelines",
        "hepatic_risk": True, "contra_diseases": ["Active Liver Disease", "Acute Gout"],
        "preg_cat": "C", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 30, "msg": "Pyrazinamide: reduce dose or extend interval. Monitor closely.", "source": "WHO Guidelines"}]
    },
    "rifampicin": {
        "class": "Rifamycin Antibiotic", "indication": "Tuberculosis, MRSA decolonization",
        "adr": "Hepatotoxicity, red-orange urine/secretions, drug interactions (CYP450 inducer).", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Active Liver Disease", "Jaundice"],
        "preg_cat": "C", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "isoniazid": {
        "class": "Anti-TB Agent", "indication": "Tuberculosis",
        "adr": "Peripheral neuropathy (B6 deficiency), hepatotoxicity.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Active Liver Disease"],
        "preg_cat": "C", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "fosfomycin": {
        "class": "Phosphonic Acid Antibiotic", "indication": "Uncomplicated UTI",
        "adr": "Diarrhea, nausea, headache.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": [],
        "preg_cat": "B", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 10, "msg": "Avoid use.", "source": "BNF Renal"}]
    },
    "fusidic acid": {
        "class": "Steroidal Antibiotic", "indication": "Staphylococcal Skin Infection, Osteomyelitis",
        "adr": "Hepatotoxicity (systemic), GI upset.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": [],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "nystatin": {
        "class": "Polyene Antifungal", "indication": "Oral / GI Candidiasis",
        "adr": "Nausea, vomiting, diarrhea (oral).", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": [],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },

    # --- PSYCHIATRY / NEUROLOGY ---
    "sodium valproate": {
        "class": "Antiepileptic / Mood Stabilizer", "indication": "Epilepsy, Bipolar Disorder, Migraine Prophylaxis",
        "adr": "Hepatotoxicity, pancreatitis, teratogenicity (NTDs), weight gain, tremor.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Active Liver Disease", "Mitochondrial Disease"],
        "preg_cat": "X", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "diazepam": {
        "class": "Benzodiazepine", "indication": "Anxiety, Seizures, Muscle Spasm, Alcohol Withdrawal",
        "adr": "Sedation, respiratory depression, dependence.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Respiratory Depression", "Myasthenia Gravis", "Sleep Apnea"],
        "preg_cat": "D", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "clonazepam": {
        "class": "Benzodiazepine", "indication": "Epilepsy, Panic Disorder",
        "adr": "Sedation, dependence, cognitive impairment.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Respiratory Depression", "Severe Hepatic Failure"],
        "preg_cat": "D", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "midazolam": {
        "class": "Benzodiazepine (Short-acting)", "indication": "Sedation, Pre-medication, Status Epilepticus",
        "adr": "Respiratory depression, hypotension, amnesia.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Respiratory Depression", "Myasthenia Gravis"],
        "preg_cat": "D", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "haloperidol": {
        "class": "Typical Antipsychotic", "indication": "Schizophrenia, Acute Psychosis, Delirium",
        "adr": "EPS, tardive dyskinesia, QT prolongation, NMS.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["QT Prolongation", "Parkinson's Disease"],
        "preg_cat": "C", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "sertraline": {
        "class": "SSRI Antidepressant", "indication": "Depression, Anxiety, OCD, PTSD",
        "adr": "GI upset, insomnia, sexual dysfunction, serotonin syndrome (overdose/interaction).", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Mania"],
        "preg_cat": "C", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "pregabalin": {
        "class": "Gabapentinoid", "indication": "Neuropathic Pain, Epilepsy, Anxiety",
        "adr": "Dizziness, somnolence, weight gain, dependence.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": [],
        "preg_cat": "C", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 60, "msg": "Reduce dose. Max 300mg/day.", "source": "BNF Renal"}, {"cutoff": 30, "msg": "Max 150mg/day.", "source": "BNF Renal"}, {"cutoff": 15, "msg": "Max 75mg/day.", "source": "BNF Renal"}]
    },
    "tramadol": {
        "class": "Opioid Analgesic (Weak)", "indication": "Moderate to Severe Pain",
        "adr": "Nausea, seizures, serotonin syndrome, dependence.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Epilepsy", "Respiratory Depression"],
        "preg_cat": "C", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 30, "msg": "Max 100mg/day; extend dosing interval to 12-hourly.", "source": "BNF Renal"}]
    },

    # --- ENDOCRINOLOGY ---
    "dapagliflozin": {
        "class": "SGLT-2 Inhibitor", "indication": "Type 2 Diabetes, Heart Failure, CKD",
        "adr": "UTI, genital mycotic infection, DKA (euglycemic).", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["T1DM", "DKA", "Recurrent UTI"],
        "preg_cat": "C", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 25, "msg": "AVOID for glycemic control; may continue for HF/CKD indications with caution.", "source": "BNF Renal"}]
    },
    "regular insulin": {
        "class": "Short-Acting Insulin", "indication": "Diabetes (T1DM & T2DM), Hyperkalemia, DKA",
        "adr": "Hypoglycemia, hypokalemia, lipodystrophy.", "adr_source": "DiPiro",
        "hepatic_risk": False, "contra_diseases": ["Hypoglycemia"],
        "preg_cat": "B", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 30, "msg": "Reduce dose — insulin clearance reduced; risk of hypoglycemia.", "source": "Katzung"}]
    },
    "prednisolone": {
        "class": "Corticosteroid", "indication": "Inflammation, Autoimmune Disease, Asthma",
        "adr": "Hyperglycemia, osteoporosis, immunosuppression, Cushingoid features.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Active Infection", "Systemic Fungal Infection"],
        "preg_cat": "C", "lifestyle_risk": ["Alcohol"], "renal_logic": []
    },
    "dexamethasone": {
        "class": "Corticosteroid (Potent)", "indication": "Severe Inflammation, Cerebral Edema, Septic Shock",
        "adr": "Hyperglycemia, immunosuppression, adrenal suppression.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Active Infection", "Systemic Fungal Infection"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
    "vitamin d3": {
        "class": "Vitamin D Supplement", "indication": "Vitamin D Deficiency, Osteoporosis",
        "adr": "Hypercalcemia (overdose), hypercalciuria.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Hypercalcemia", "Hypercalciuria"],
        "preg_cat": "A/C", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 30, "msg": "Avoid high-dose supplementation; use active forms (calcitriol).", "source": "BNF Renal"}]
    },

    # --- GI / HEPATOLOGY ---
    "ondansetron": {
        "class": "5-HT3 Antagonist (Antiemetic)", "indication": "Nausea & Vomiting (Chemo, Post-op)",
        "adr": "Headache, constipation, QT prolongation.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["QT Prolongation", "Congenital Long QT"],
        "preg_cat": "B", "lifestyle_risk": [], "renal_logic": []
    },
    "metoclopramide": {
        "class": "Prokinetic / Antiemetic", "indication": "Nausea, Gastric Stasis, GERD",
        "adr": "EPS, tardive dyskinesia (long-term), drowsiness.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Parkinson's Disease", "GI Obstruction"],
        "preg_cat": "B", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 40, "msg": "Reduce dose by 50%.", "source": "BNF Renal"}]
    },
    "lactulose": {
        "class": "Osmotic Laxative", "indication": "Constipation, Hepatic Encephalopathy",
        "adr": "Flatulence, bloating, diarrhea (excessive dose).", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Galactosemia", "GI Obstruction"],
        "preg_cat": "B", "lifestyle_risk": [], "renal_logic": []
    },
    "bacillus clausii": {
        "class": "Probiotic", "indication": "Intestinal Dysbiosis, Antibiotic-Associated Diarrhea",
        "adr": "Mild GI upset (rare).", "adr_source": "BNF / Manufacturer",
        "hepatic_risk": False, "contra_diseases": ["Severe Immunosuppression"],
        "preg_cat": "B", "lifestyle_risk": [], "renal_logic": []
    },

    # --- PAIN / MUSCULOSKELETAL ---
    "ketorolac": {
        "class": "NSAID (Parenteral/Oral)", "indication": "Short-Term Moderate-to-Severe Pain",
        "adr": "GI bleeding, renal impairment, platelet inhibition. (Max 5 days use)", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Peptic Ulcer", "CKD", "Active Bleeding", "Heart Failure"],
        "preg_cat": "C/D", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 50, "msg": "Reduce dose; max 15mg QDS. Monitor renal function.", "source": "BNF Renal"}, {"cutoff": 30, "msg": "AVOID.", "source": "BNF Renal"}]
    },
    "celecoxib": {
        "class": "COX-2 Inhibitor (NSAID)", "indication": "Arthritis, Acute Pain",
        "adr": "Cardiovascular risk, GI upset, hypertension.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Peptic Ulcer", "Heart Failure", "Ischemic Heart Disease", "CKD"],
        "preg_cat": "C/D", "lifestyle_risk": ["Alcohol"],
        "renal_logic": [{"cutoff": 30, "msg": "Avoid use.", "source": "BNF Renal"}]
    },
    "drotaverine": {
        "class": "Antispasmodic", "indication": "GI & Biliary Colic, Uterine Spasm",
        "adr": "Dizziness, nausea, hypotension.", "adr_source": "Manufacturer data",
        "hepatic_risk": False, "contra_diseases": ["Severe Hepatic/Renal Impairment", "Cardiac Failure"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },

    # --- RESPIRATORY ---
    "tocilizumab": {
        "class": "IL-6 Receptor Antagonist (Biologic)", "indication": "RA, Cytokine Release Syndrome (COVID-19, CAR-T)",
        "adr": "Serious infections, hepatotoxicity, bowel perforation, neutropenia.", "adr_source": "BNF 84",
        "hepatic_risk": True, "contra_diseases": ["Active Infection", "Severe Hepatic Impairment"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },

    # --- OBSTETRICS / GYNECOLOGY ---
    "natural micronised progesterone": {
        "class": "Progestogen", "indication": "Luteal Phase Support, Threatened Miscarriage, HRT",
        "adr": "Drowsiness, dizziness, vaginal discharge (vaginal route).", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Undiagnosed Vaginal Bleeding", "Breast Cancer", "Thromboembolic Disorders"],
        "preg_cat": "B", "lifestyle_risk": [], "renal_logic": []
    },

    # --- NEUROMUSCULAR ---
    "atracurium": {
        "class": "Non-Depolarising Neuromuscular Blocker", "indication": "ICU Sedation, Surgical Muscle Relaxation",
        "adr": "Histamine release, bronchospasm, prolonged block.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Myasthenia Gravis"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },

    # --- VITAMINS / SUPPLEMENTS ---
    "pyridoxine": {
        "class": "Vitamin B6 Supplement", "indication": "B6 Deficiency, INH-Induced Neuropathy Prophylaxis, Nausea",
        "adr": "Peripheral neuropathy (high chronic doses >200mg/day).", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": [],
        "preg_cat": "A", "lifestyle_risk": [], "renal_logic": []
    },
    "methylcobalamin": {
        "class": "Vitamin B12 Supplement", "indication": "B12 Deficiency, Peripheral Neuropathy",
        "adr": "Generally well tolerated; acne (rare).", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": [],
        "preg_cat": "A", "lifestyle_risk": [], "renal_logic": []
    },
    "ferrous sulfate": {
        "class": "Iron Supplement", "indication": "Iron Deficiency Anemia",
        "adr": "Constipation, nausea, dark stools, GI irritation.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Hemochromatosis", "Hemolytic Anemia"],
        "preg_cat": "A", "lifestyle_risk": [],
        "renal_logic": [{"cutoff": 30, "msg": "Use with caution — accumulation risk; monitor iron stores.", "source": "BNF Renal"}]
    },
    "folic acid": {
        "class": "Vitamin B9 Supplement", "indication": "Folate Deficiency, Neural Tube Defect Prevention",
        "adr": "Rarely GI upset; may mask B12 deficiency.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Undiagnosed Megaloblastic Anemia"],
        "preg_cat": "A", "lifestyle_risk": [], "renal_logic": []
    },

    # --- RENAL / ELECTROLYTES ---
    "human albumin": {
        "class": "Plasma Volume Expander", "indication": "Hypoalbuminemia, Cirrhotic Ascites, Septic Shock",
        "adr": "Fluid overload, pulmonary edema, electrolyte disturbances.", "adr_source": "BNF 84",
        "hepatic_risk": False, "contra_diseases": ["Pulmonary Edema", "Severe Anemia"],
        "preg_cat": "C", "lifestyle_risk": [], "renal_logic": []
    },
}

# =========================================================
# B. DRUG-DRUG INTERACTIONS DATABASE
# =========================================================
interactions_db = {

    # ── ORIGINAL INTERACTIONS (kept) ─────────────────────
    ("warfarin", "aspirin"): {"level": "CRITICAL", "msg": "Significantly increased bleeding risk.", "source": "Stockley's"},
    ("warfarin", "ibuprofen"): {"level": "CRITICAL", "msg": "Severe GI bleeding risk.", "source": "Stockley's"},
    ("lisinopril", "ibuprofen"): {"level": "Major", "msg": "Reduced antihypertensive effect + Kidney Risk.", "source": "BNF"},
    ("lisinopril", "lithium"): {"level": "Major", "msg": "Lithium Toxicity Risk.", "source": "Stockley's"},
    ("digoxin", "amiodarone"): {"level": "Major", "msg": "Digoxin levels increase ~50%.", "source": "DiPiro"},
    ("ciprofloxacin", "warfarin"): {"level": "Major", "msg": "Increased INR/Bleeding.", "source": "BNF"},
    ("propranolol", "salbutamol"): {"level": "Major", "msg": "Antagonistic effect.", "source": "Katzung"},
    ("levothyroxine", "warfarin"): {"level": "Major", "msg": "Enhanced Warfarin effect.", "source": "Stockley's"},
    ("methotrexate", "ibuprofen"): {"level": "CRITICAL", "msg": "FATAL Toxicity — NSAIDs block MTX excretion.", "source": "Stockley's"},
    ("methotrexate", "aspirin"): {"level": "CRITICAL", "msg": "FATAL Toxicity — NSAIDs block MTX excretion.", "source": "Stockley's"},
    ("theophylline", "ciprofloxacin"): {"level": "CRITICAL", "msg": "Theophylline Toxicity — risk of seizures.", "source": "Stockley's"},
    ("carbamazepine", "erythromycin"): {"level": "Major", "msg": "Carbamazepine toxicity risk.", "source": "BNF"},
    ("vancomycin", "gentamicin"): {"level": "Major", "msg": "Synergistic Nephrotoxicity.", "source": "Sanford"},
    ("phenytoin", "warfarin"): {"level": "Major", "msg": "Unstable INR.", "source": "Stockley's"},

    # ── NEW INTERACTIONS ──────────────────────────────────

    # Anticoagulants
    ("apixaban", "aspirin"): {"level": "Major", "msg": "Increased bleeding risk; avoid unless benefit outweighs risk.", "source": "BNF 84"},
    ("apixaban", "ibuprofen"): {"level": "CRITICAL", "msg": "Severe bleeding risk — NSAIDs + DOAC combination.", "source": "BNF 84"},
    ("apixaban", "fluconazole"): {"level": "Major", "msg": "Fluconazole increases apixaban levels (CYP3A4/P-gp inhibition).", "source": "Stockley's"},
    ("enoxaparin", "aspirin"): {"level": "Major", "msg": "Increased bleeding risk.", "source": "BNF 84"},
    ("enoxaparin", "ibuprofen"): {"level": "Major", "msg": "Increased bleeding risk — NSAIDs impair platelet function.", "source": "BNF 84"},
    ("heparin", "aspirin"): {"level": "Major", "msg": "Increased bleeding risk.", "source": "BNF 84"},
    ("warfarin", "fluconazole"): {"level": "CRITICAL", "msg": "Fluconazole markedly increases INR — major bleeding risk.", "source": "Stockley's"},
    ("warfarin", "metronidazole"): {"level": "CRITICAL", "msg": "Metronidazole inhibits warfarin metabolism — INR rises sharply.", "source": "Stockley's"},
    ("warfarin", "ciprofloxacin"): {"level": "Major", "msg": "Increased anticoagulation effect.", "source": "BNF 84"},
    ("warfarin", "rifampicin"): {"level": "CRITICAL", "msg": "Rifampicin is a potent CYP inducer — warfarin levels fall dramatically; INR drops.", "source": "Stockley's"},
    ("warfarin", "amiodarone"): {"level": "CRITICAL", "msg": "Amiodarone inhibits warfarin metabolism — risk of severe bleeding.", "source": "Stockley's"},
    ("warfarin", "sodium valproate"): {"level": "Major", "msg": "Valproate displaces warfarin and inhibits its metabolism — increased bleeding risk.", "source": "Stockley's"},
    ("warfarin", "celecoxib"): {"level": "Major", "msg": "Celecoxib may enhance anticoagulant effect.", "source": "BNF 84"},

    # Beta Blockers & Cardiac
    ("bisoprolol", "amiodarone"): {"level": "Major", "msg": "Additive bradycardia and AV block risk.", "source": "BNF 84"},
    ("metoprolol", "amiodarone"): {"level": "Major", "msg": "Increased risk of bradycardia and AV block.", "source": "BNF 84"},
    ("carvedilol", "amiodarone"): {"level": "Major", "msg": "Additive bradycardia and hypotension.", "source": "BNF 84"},
    ("bisoprolol", "verapamil"): {"level": "CRITICAL", "msg": "Risk of asystole — never give together IV.", "source": "BNF 84"},
    ("metoprolol", "salbutamol"): {"level": "Major", "msg": "Beta blocker antagonises bronchodilator effect.", "source": "Katzung"},
    ("atenolol", "verapamil"): {"level": "CRITICAL", "msg": "Risk of complete heart block and asystole.", "source": "BNF 84"},
    ("ivabradine", "amiodarone"): {"level": "Major", "msg": "Additive bradycardia risk.", "source": "BNF 84"},
    ("ivabradine", "fluconazole"): {"level": "Major", "msg": "Azoles increase ivabradine levels via CYP3A4 inhibition.", "source": "BNF 84"},
    ("digoxin", "clarithromycin"): {"level": "Major", "msg": "P-gp inhibition raises digoxin to toxic levels.", "source": "Stockley's"},
    ("digoxin", "furosemide"): {"level": "Major", "msg": "Furosemide-induced hypokalemia potentiates digoxin toxicity.", "source": "Katzung"},

    # ACE Inhibitors / ARBs
    ("lisinopril", "spironolactone"): {"level": "Major", "msg": "Risk of life-threatening hyperkalemia.", "source": "BNF 84"},
    ("ramipril", "spironolactone"): {"level": "Major", "msg": "Risk of life-threatening hyperkalemia.", "source": "BNF 84"},
    ("captopril", "spironolactone"): {"level": "Major", "msg": "Risk of life-threatening hyperkalemia.", "source": "BNF 84"},
    ("lisinopril", "potassium chloride"): {"level": "Major", "msg": "Combined risk of hyperkalemia.", "source": "BNF 84"},
    ("ramipril", "ibuprofen"): {"level": "Major", "msg": "Reduced antihypertensive effect + acute kidney injury risk.", "source": "BNF 84"},
    ("losartan", "ibuprofen"): {"level": "Major", "msg": "Reduced antihypertensive effect + renal impairment risk.", "source": "BNF 84"},

    # Antibiotics
    ("clindamycin", "metronidazole"): {"level": "Major", "msg": "Additive risk of C. difficile colitis — avoid prolonged combined use.", "source": "BNF 84"},
    ("linezolid", "tramadol"): {"level": "CRITICAL", "msg": "Risk of serotonin syndrome — potentially fatal.", "source": "Stockley's"},
    ("linezolid", "sertraline"): {"level": "CRITICAL", "msg": "Risk of serotonin syndrome — AVOID.", "source": "Stockley's"},
    ("metronidazole", "lithium"): {"level": "Major", "msg": "Metronidazole may reduce lithium clearance — toxicity risk.", "source": "Stockley's"},
    ("fluconazole", "amiodarone"): {"level": "CRITICAL", "msg": "Both prolong QT — risk of Torsades de Pointes.", "source": "BNF 84"},
    ("fluconazole", "simvastatin"): {"level": "Major", "msg": "Fluconazole increases statin levels — myopathy/rhabdomyolysis risk.", "source": "Stockley's"},
    ("fluconazole", "ondansetron"): {"level": "Major", "msg": "Both prolong QT — increased risk of arrhythmia.", "source": "BNF 84"},
    ("ciprofloxacin", "ondansetron"): {"level": "Major", "msg": "Additive QT prolongation risk.", "source": "BNF 84"},
    ("azithromycin", "amiodarone"): {"level": "CRITICAL", "msg": "Both prolong QT — high risk of Torsades de Pointes.", "source": "BNF 84"},
    ("azithromycin", "warfarin"): {"level": "Major", "msg": "Azithromycin may increase INR.", "source": "BNF 84"},
    ("rifampicin", "metformin"): {"level": "Major", "msg": "Rifampicin reduces metformin plasma levels.", "source": "Stockley's"},
    ("rifampicin", "dapagliflozin"): {"level": "Major", "msg": "Rifampicin reduces dapagliflozin plasma levels via CYP induction.", "source": "Stockley's"},
    ("rifampicin", "amlodipine"): {"level": "Major", "msg": "Rifampicin induces CYP3A4 — reduces amlodipine significantly.", "source": "Stockley's"},
    ("isoniazid", "phenytoin"): {"level": "Major", "msg": "Isoniazid inhibits phenytoin metabolism — risk of phenytoin toxicity.", "source": "Stockley's"},
    ("isoniazid", "carbamazepine"): {"level": "Major", "msg": "Isoniazid inhibits carbamazepine metabolism — toxicity risk.", "source": "BNF 84"},

    # Diuretics
    ("furosemide", "gentamicin"): {"level": "Major", "msg": "Additive ototoxicity risk.", "source": "Katzung"},
    ("furosemide", "lithium"): {"level": "Major", "msg": "Furosemide reduces lithium excretion — toxicity risk.", "source": "Stockley's"},
    ("spironolactone", "potassium chloride"): {"level": "Major", "msg": "Severe hyperkalemia risk.", "source": "BNF 84"},

    # Antiepileptics / Mood Stabilizers
    ("sodium valproate", "carbamazepine"): {"level": "Major", "msg": "Complex interaction — may reduce valproate levels and increase carbamazepine toxicity.", "source": "BNF 84"},
    ("sodium valproate", "aspirin"): {"level": "Major", "msg": "Aspirin displaces valproate from protein binding — increased free drug and toxicity.", "source": "Stockley's"},
    ("sodium valproate", "methotrexate"): {"level": "Major", "msg": "Risk of increased methotrexate toxicity.", "source": "Stockley's"},
    ("carbamazepine", "amiodarone"): {"level": "Major", "msg": "Carbamazepine reduces amiodarone levels.", "source": "BNF 84"},

    # Diabetes
    ("metformin", "alcohol"): {"level": "Major", "msg": "Increased risk of lactic acidosis.", "source": "BNF 84"},
    ("regular insulin", "propranolol"): {"level": "Major", "msg": "Propranolol masks hypoglycemia symptoms and prolongs hypoglycemic episodes.", "source": "Katzung"},
    ("regular insulin", "metformin"): {"level": "Minor", "msg": "Additive blood glucose lowering; monitor for hypoglycemia.", "source": "DiPiro"},
    ("dapagliflozin", "furosemide"): {"level": "Major", "msg": "Additive risk of dehydration and hypotension.", "source": "BNF 84"},

    # Analgesics / Opioids
    ("tramadol", "sertraline"): {"level": "CRITICAL", "msg": "Risk of serotonin syndrome.", "source": "Stockley's"},
    ("tramadol", "metoclopramide"): {"level": "Major", "msg": "Metoclopramide enhances tramadol absorption and effect.", "source": "BNF 84"},
    ("ketorolac", "warfarin"): {"level": "CRITICAL", "msg": "Significantly increased risk of serious GI bleeding.", "source": "Stockley's"},
    ("ketorolac", "enoxaparin"): {"level": "CRITICAL", "msg": "Simultaneous use contraindicated — high bleeding risk.", "source": "BNF 84"},
    ("ketorolac", "heparin"): {"level": "CRITICAL", "msg": "Simultaneous use contraindicated — high bleeding risk.", "source": "BNF 84"},
    ("celecoxib", "warfarin"): {"level": "Major", "msg": "Celecoxib may enhance anticoagulant effect of warfarin.", "source": "BNF 84"},
    ("methotrexate", "celecoxib"): {"level": "CRITICAL", "msg": "COX-2 inhibitors reduce MTX excretion — toxicity risk.", "source": "Stockley's"},

    # Nitrates & Antihypertensives
    ("isosorbide mononitrate", "sildenafil"): {"level": "CRITICAL", "msg": "ABSOLUTE CONTRAINDICATION — risk of fatal hypotension.", "source": "BNF 84"},
    ("isosorbide dinitrate", "sildenafil"): {"level": "CRITICAL", "msg": "ABSOLUTE CONTRAINDICATION — risk of fatal hypotension.", "source": "BNF 84"},
    ("nitroglycerin", "sildenafil"): {"level": "CRITICAL", "msg": "ABSOLUTE CONTRAINDICATION — risk of fatal hypotension.", "source": "BNF 84"},
    ("hydralazine", "metoprolol"): {"level": "Minor", "msg": "Additive blood pressure lowering — monitor for hypotension.", "source": "DiPiro"},

    # Psych
    ("haloperidol", "amiodarone"): {"level": "CRITICAL", "msg": "Additive QT prolongation — risk of Torsades de Pointes.", "source": "BNF 84"},
    ("haloperidol", "metoclopramide"): {"level": "Major", "msg": "Additive risk of extrapyramidal effects and neuroleptic malignant syndrome.", "source": "BNF 84"},
    ("diazepam", "metronidazole"): {"level": "Major", "msg": "Metronidazole inhibits diazepam metabolism — increased sedation.", "source": "Stockley's"},
    ("midazolam", "fluconazole"): {"level": "CRITICAL", "msg": "Fluconazole markedly increases midazolam levels — risk of profound sedation.", "source": "Stockley's"},
    ("clonazepam", "sodium valproate"): {"level": "Major", "msg": "May induce absence status — use with caution.", "source": "BNF 84"},

    # Miscellaneous
    ("tocilizumab", "methotrexate"): {"level": "Major", "msg": "Combined immunosuppression — risk of serious infection.", "source": "BNF 84"},
    ("rosuvastatin", "amiodarone"): {"level": "Major", "msg": "Amiodarone inhibits rosuvastatin metabolism — myopathy risk.", "source": "BNF 84"},
    ("amlodipine", "rifampicin"): {"level": "Major", "msg": "Rifampicin reduces amlodipine efficacy significantly.", "source": "Stockley's"},
    ("calcium gluconate", "digoxin"): {"level": "CRITICAL", "msg": "IV calcium can precipitate digoxin toxicity and arrhythmia.", "source": "Katzung"},
    ("potassium chloride", "spironolactone"): {"level": "Major", "msg": "High risk of dangerous hyperkalemia.", "source": "BNF 84"},
    ("pregabalin", "tramadol"): {"level": "Major", "msg": "Additive CNS and respiratory depression.", "source": "BNF 84"},
}

# =========================================================
# C. PARENTERAL (IV) DILUTION DATABASE
# =========================================================
parenteral_db = {

    # ── ORIGINAL ENTRIES (kept) ───────────────────────────
    "Ceftriaxone 1g Vial": {
        "strength_mg": 1000, "diluent": "Water for Injection or 1% Lidocaine (IM only)",
        "reconst_vol_ml": 9.6, "final_vol_ml": 10.0, "final_conc": 100.0,
        "compatible_fluids": ["NS", "D5W", "LR"],
        "rate_iv": "Slow IV Push over 2-4 mins OR Infusion over 30 mins",
        "stability": "Use immediately; stable 24h refrigerated"
    },
    "Vancomycin 500mg Vial": {
        "strength_mg": 500, "diluent": "Water for Injection",
        "reconst_vol_ml": 10.0, "final_vol_ml": 10.0, "final_conc": 50.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Intermittent Infusion over at least 60 mins (Red Man Syndrome risk if faster)",
        "stability": "Reconstituted solution stable 14 days refrigerated"
    },
    "Meropenem 1g Vial": {
        "strength_mg": 1000, "diluent": "Water for Injection",
        "reconst_vol_ml": 20.0, "final_vol_ml": 20.0, "final_conc": 50.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "IV Bolus over 3-5 mins OR Infusion over 15-30 mins",
        "stability": "Use within 2-3 hours at room temperature"
    },
    "Hydrocortisone 100mg Vial": {
        "strength_mg": 100, "diluent": "Water for Injection",
        "reconst_vol_ml": 2.0, "final_vol_ml": 2.0, "final_conc": 50.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Slow IV Push over 30 seconds OR IV Infusion",
        "stability": "Use within 3 days if protected from light"
    },
    "Pantoprazole 40mg Vial": {
        "strength_mg": 40, "diluent": "0.9% Sodium Chloride",
        "reconst_vol_ml": 10.0, "final_vol_ml": 10.0, "final_conc": 4.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "IV Push over 2 mins OR Infusion over 15 mins",
        "stability": "Use within 12 hours"
    },
    "Piperacillin/Tazobactam 4.5g": {
        "strength_mg": 4500, "diluent": "NS or Water for Injection",
        "reconst_vol_ml": 20.0, "final_vol_ml": 23.0, "final_conc": 200.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Infusion over 30 mins (Extended infusion 3-4h preferred for severe infection)",
        "stability": "Use within 24h at room temperature"
    },

    # ── NEW IV ENTRIES ────────────────────────────────────
    "Furosemide 20mg/2mL Ampoule": {
        "strength_mg": 20, "diluent": "No reconstitution needed (ready to use)",
        "reconst_vol_ml": 2.0, "final_vol_ml": 2.0, "final_conc": 10.0,
        "compatible_fluids": ["NS", "D5W", "LR"],
        "rate_iv": "Slow IV Push over 1-2 mins (max rate 4mg/min to avoid ototoxicity)",
        "stability": "Use immediately; protect from light"
    },
    "Ondansetron 4mg/2mL Ampoule": {
        "strength_mg": 4, "diluent": "No reconstitution needed (ready to use)",
        "reconst_vol_ml": 2.0, "final_vol_ml": 2.0, "final_conc": 2.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Slow IV Push over 2-5 mins OR dilute in 50mL NS and infuse over 15 mins",
        "stability": "Use immediately once diluted"
    },
    "Metoclopramide 10mg/2mL Ampoule": {
        "strength_mg": 10, "diluent": "No reconstitution needed (ready to use)",
        "reconst_vol_ml": 2.0, "final_vol_ml": 2.0, "final_conc": 5.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Slow IV Push over 3-5 mins (rapid injection causes anxiety/EPS)",
        "stability": "Use immediately"
    },
    "Metronidazole 500mg/100mL Infusion": {
        "strength_mg": 500, "diluent": "Pre-mixed (ready to infuse)",
        "reconst_vol_ml": 100.0, "final_vol_ml": 100.0, "final_conc": 5.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Infusion over 20-30 mins",
        "stability": "Use within 24h at room temperature; protect from light"
    },
    "Dexamethasone 4mg/mL Ampoule": {
        "strength_mg": 4, "diluent": "No reconstitution needed; dilute in NS/D5W for infusion",
        "reconst_vol_ml": 1.0, "final_vol_ml": 1.0, "final_conc": 4.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Slow IV Push over 2-3 mins OR dilute and infuse over 15-30 mins",
        "stability": "Use within 24h once diluted"
    },
    "Omeprazole 40mg Vial": {
        "strength_mg": 40, "diluent": "0.9% Sodium Chloride (reconstitute with 5mL, then dilute to 100mL)",
        "reconst_vol_ml": 5.0, "final_vol_ml": 100.0, "final_conc": 0.4,
        "compatible_fluids": ["NS"],
        "rate_iv": "Infusion over 20-30 mins",
        "stability": "Use within 4 hours of preparation"
    },
    "Calcium Gluconate 10% (10mL Ampoule)": {
        "strength_mg": 1000, "diluent": "Dilute in 100mL NS or D5W",
        "reconst_vol_ml": 10.0, "final_vol_ml": 100.0, "final_conc": 10.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Infusion over 10-20 mins (NEVER rapid IV — risk of cardiac arrest)",
        "stability": "Use immediately once diluted"
    },
    "Potassium Chloride 1.5g in 10mL": {
        "strength_mg": 1500, "diluent": "MUST dilute before use — NEVER give undiluted IV",
        "reconst_vol_ml": 10.0, "final_vol_ml": 250.0, "final_conc": 6.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Max 10 mEq/hour peripheral; max 20 mEq/hour via central line with monitoring",
        "stability": "Use within 24h; do NOT add to hanging bags"
    },
    "Regular Insulin (IV Infusion)": {
        "strength_mg": 100, "diluent": "0.9% Sodium Chloride — add 100 units to 100mL NS (1 unit/mL)",
        "reconst_vol_ml": 100.0, "final_vol_ml": 100.0, "final_conc": 1.0,
        "compatible_fluids": ["NS"],
        "rate_iv": "Continuous infusion — titrate to blood glucose (typically 0.1-0.5 units/kg/hr)",
        "stability": "Use within 24h; flush IV line before use (insulin adsorbs to plastic)"
    },
    "Heparin 5000 IU/mL": {
        "strength_mg": 5000, "diluent": "Add 25,000 units to 250mL NS (100 units/mL) for infusion",
        "reconst_vol_ml": 250.0, "final_vol_ml": 250.0, "final_conc": 100.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Continuous IV infusion — dose by weight-based protocol; monitor aPTT",
        "stability": "Use within 24h"
    },
    "Enoxaparin 60mg/0.6mL Syringe": {
        "strength_mg": 60, "diluent": "Pre-filled syringe — SC injection only (NOT IV bolus)",
        "reconst_vol_ml": 0.6, "final_vol_ml": 0.6, "final_conc": 100.0,
        "compatible_fluids": ["SC only"],
        "rate_iv": "Subcutaneous injection — abdomen preferred; rotate sites",
        "stability": "Store at room temperature; do NOT freeze"
    },
    "Norepinephrine 4mg/4mL Ampoule": {
        "strength_mg": 4, "diluent": "Add 4mg to 46mL D5W or NS (concentration 80 mcg/mL)",
        "reconst_vol_ml": 4.0, "final_vol_ml": 50.0, "final_conc": 0.08,
        "compatible_fluids": ["D5W", "NS"],
        "rate_iv": "Continuous infusion via CENTRAL LINE only — titrate to MAP >65mmHg",
        "stability": "Use within 24h; check colour — discard if brown"
    },
    "Dobutamine 250mg/20mL Vial": {
        "strength_mg": 250, "diluent": "Add 250mg to 230mL D5W (concentration 1mg/mL)",
        "reconst_vol_ml": 20.0, "final_vol_ml": 250.0, "final_conc": 1.0,
        "compatible_fluids": ["D5W", "NS"],
        "rate_iv": "Continuous infusion — start 2.5 mcg/kg/min; titrate to response",
        "stability": "Use within 24h at room temperature"
    },
    "Amiodarone 150mg/3mL Ampoule": {
        "strength_mg": 150, "diluent": "Dilute in D5W ONLY (NOT NS — precipitates)",
        "reconst_vol_ml": 3.0, "final_vol_ml": 100.0, "final_conc": 1.5,
        "compatible_fluids": ["D5W"],
        "rate_iv": "Loading: 150mg over 10 mins; then 1mg/min for 6h; then 0.5mg/min — use CENTRAL LINE for prolonged infusion",
        "stability": "Use within 24h; protect from light; avoid PVC containers"
    },
    "Hydralazine 20mg/mL Ampoule": {
        "strength_mg": 20, "diluent": "Dilute with NS or Water for Injection",
        "reconst_vol_ml": 1.0, "final_vol_ml": 10.0, "final_conc": 2.0,
        "compatible_fluids": ["NS"],
        "rate_iv": "Slow IV Push over 5 mins (Hypertensive emergency); monitor BP every 5 mins",
        "stability": "Use immediately once diluted"
    },
    "Midazolam 5mg/mL Ampoule": {
        "strength_mg": 5, "diluent": "Dilute to 0.5-1mg/mL with NS or D5W",
        "reconst_vol_ml": 1.0, "final_vol_ml": 10.0, "final_conc": 0.5,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Slow IV Push over 2-3 mins for sedation; continuous infusion for ICU",
        "stability": "Use within 24h"
    },
    "Atracurium 50mg/5mL Ampoule": {
        "strength_mg": 50, "diluent": "Dilute in NS or D5W (0.5mg/mL for infusion)",
        "reconst_vol_ml": 5.0, "final_vol_ml": 100.0, "final_conc": 0.5,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "IV Bolus over 10-15 seconds for intubation; continuous infusion in ICU",
        "stability": "Use within 24h if refrigerated; use within 8h at room temperature"
    },
    "Metoprolol 5mg/5mL Ampoule": {
        "strength_mg": 5, "diluent": "No reconstitution needed (ready to use)",
        "reconst_vol_ml": 5.0, "final_vol_ml": 5.0, "final_conc": 1.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Slow IV Push 5mg over 5 mins; max 3 doses at 5-min intervals",
        "stability": "Use immediately"
    },
    "Human Albumin 20% (100mL Bottle)": {
        "strength_mg": 20000, "diluent": "Ready to use (no dilution required)",
        "reconst_vol_ml": 100.0, "final_vol_ml": 100.0, "final_conc": 200.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Infuse over 60-120 mins; rate adjusted based on clinical response",
        "stability": "Use within 3 hours of opening"
    },
    "Magnesium Sulfate 50% (10mL Ampoule)": {
        "strength_mg": 5000, "diluent": "MUST dilute — add to 250mL NS or D5W",
        "reconst_vol_ml": 10.0, "final_vol_ml": 260.0, "final_conc": 19.2,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Loading: 4g over 20 mins (eclampsia); Maintenance: 1-2g/hour — monitor reflexes and respiratory rate",
        "stability": "Use within 24h"
    },
    "Labetalol 100mg/20mL Ampoule": {
        "strength_mg": 100, "diluent": "Add 200mg to 160mL NS or D5W (1mg/mL)",
        "reconst_vol_ml": 20.0, "final_vol_ml": 200.0, "final_conc": 1.0,
        "compatible_fluids": ["NS", "D5W"],
        "rate_iv": "Bolus: 20mg slow IV; or infusion 0.5-2mg/min for hypertensive crisis",
        "stability": "Use within 24h"
    },
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
st.caption("RxGuard Ultimate © 2026 | Clinical Decision Support System | Disclaimer: This tool is decision support aid only, All alerts must be verified by the treating clinician. Do not modify therapy based solely on this output. Full clinical responsibility remains with the prescriber.")
