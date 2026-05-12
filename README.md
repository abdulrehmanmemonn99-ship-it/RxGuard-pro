# RxGuard — Clinical Decision Support System

> **A pharmacist-built, research-grade prescription safety platform for real-world clinical use.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-rxguard--clinical.streamlit.app-brightgreen?style=flat-square&logo=streamlit)](https://rxguard-clinical.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b?style=flat-square&logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## Overview

RxGuard is a Clinical Decision Support System (CDSS) designed to assist pharmacists and physicians in detecting drug-related problems at the point of prescribing. It performs multi-layered safety analysis on patient-specific prescriptions — combining patient demographics, laboratory values, comorbidities, and drug data to generate actionable clinical alerts.

The system was independently designed and developed by **Abdul Rehman**, a PharmD student at **[Liaquat University of Medical and Health Sciences Jamshoro]**, Pakistan — with no institutional infrastructure — as a demonstration of applied clinical informatics and patient safety research.

**Live deployment:** [rxguard-clinical.streamlit.app](https://rxguard-clinical.streamlit.app)

---

## Clinical Features

### 🔬 Prescription Safety Analysis
- **Drug-Drug Interaction (DDI) Detection** — 87+ interaction pairs with severity classification (CRITICAL / Major / Minor), pharmacological mechanism, and cited source
- **Renal Dose Adjustment** — Tiered CrCl/eGFR-based dosing alerts for all renally-cleared drugs, sourced from BNF Renal and Katzung
- **Hepatic Risk Flagging** — Automatic identification of hepatotoxic drugs when ALT is elevated
- **Contraindication Checking** — Drug-disease contraindications cross-referenced against patient comorbidities
- **Allergy Cross-Reactivity** — Penicillin and NSAID allergy alerts including anaphylaxis risk
- **Lifestyle & Drug Interactions** — Flags clinically significant food/substance interactions (alcohol, grapefruit juice, dairy, vitamin K-rich diet)

### 🧪 Patient-Specific Lab Integration
Real-time alerts triggered by laboratory values entered for each patient:

| Lab Parameter | Alert Thresholds |
|---|---|
| INR | ≥3.0 (High), ≥4.0 (CRITICAL) |
| ALT | ≥60 U/L (Mild), ≥100 U/L (CRITICAL) |
| Platelets | <100 (Low), <50 (CRITICAL) |
| Potassium (K+) | ≤3.5 (Hypokalemia), ≥5.5 (Hyperkalemia), with CRITICAL thresholds |
| Serum Creatinine / eGFR | Drives renal dose adjustment engine |

### 💉 IV Reconstitution & Dilution Calculator
Step-by-step parenteral preparation guide for 27 IV drugs including:
- Reconstitution volume and diluent
- Compatible IV fluids
- Infusion rate and administration warnings
- Stability data
- Auto-calculation of volume to draw for any prescribed dose

### 🤖 AI Clinical Copilot *(in development)*
Natural language clinical query interface for complex pharmacotherapy questions beyond the structured database.

---

## Database

| Database | Entries | Sources |
|---|---|---|
| Drug profiles | 92 drugs | BNF 84, Katzung, DiPiro, WHO |
| Drug-drug interactions | 87 pairs | Stockley's, BNF 84, Katzung, DiPiro |
| IV parenteral drugs | 27 preparations | BNF 84, Sanford Guide |

All interaction entries include:
- **Severity level** — CRITICAL / Major / Minor
- **Clinical message** — plain-language alert
- **Mechanism** — pharmacokinetic (PK) or pharmacodynamic (PD) explanation
- **Source** — peer-reviewed or guideline reference

### Drug Classes Covered
Cardiovascular · Antibiotics & Antimicrobials · Antiepileptics · Psychiatry & Neurology · Endocrinology · Gastroenterology · Pain & Musculoskeletal · Respiratory · Obstetrics & Gynaecology · Electrolytes & Supplements

---

## Architecture

```
rxguard/
├── app.py                  # Main application — UI and clinical logic engine
├── drugs.json              # Drug database (92 entries)
├── interactions.json       # Interaction database (87 pairs with mechanisms)
├── parenteral.json         # IV preparation database (27 drugs)
└── requirements.txt        # Python dependencies
```

**Data architecture:** Databases are decoupled from application logic and stored as structured JSON files. This enables independent updates, version control of clinical data, and future integration with external drug databases (DrugBank, OpenFDA).

**Technology stack:**
- Python 3.10+
- Streamlit (UI framework and deployment)
- Pillow + Pytesseract (OCR for prescription image upload)
- JSON (structured clinical data storage)

---

## Safety Logic Engine

The analysis pipeline runs six sequential checks for every prescription:

```
Input (drugs + patient data)
        │
        ▼
1. Lab Value Alerts      ← INR, ALT, Platelets, K+
        │
        ▼
2. Renal Dose Checks     ← CrCl / eGFR tiered thresholds
        │
        ▼
3. Allergy Screening     ← Cross-reactivity classes
        │
        ▼
4. Lifestyle Interactions ← Food, alcohol, supplements
        │
        ▼
5. Contraindications     ← Drug-disease pairs
        │
        ▼
6. Drug-Drug Interactions ← 87-pair database
        │
        ▼
Prescription Safety Score (0–100) + Pharmacist Intervention Note
```

Each flagged issue deducts from the safety score and is appended to a structured pharmacist intervention note for clinical documentation.

---

## Research Context

RxGuard is being developed as the basis for a formal research study investigating the **prevalence and clinical significance of drug-related problems (DRPs) in real-world prescriptions** in Pakistan.

**Planned research objectives:**
1. Prospective validation of RxGuard alerts against clinical pharmacist review
2. Quantification of DRP prevalence in a Pakistani hospital/community pharmacy setting
3. Sensitivity and specificity analysis of the automated detection system
4. Assessment of clinical significance of flagged interactions using established severity scales

This work is being prepared for submission to peer-reviewed journals in clinical pharmacy and medical informatics.

---

## Limitations & Disclaimer

- RxGuard is a **clinical decision support aid only**. All alerts must be verified by a qualified clinician.
- The system does not replace clinical judgement, therapeutic drug monitoring, or patient assessment.
- Drug interaction databases are curated manually and may not reflect the most recent literature. Users should verify critical decisions against primary sources.
- OCR-based prescription reading is dependent on image quality and may miss drugs in poor-quality scans.
- Full clinical responsibility remains with the prescribing clinician.

---

## Roadmap

- [ ] Expand drug database to 300+ drugs using DrugBank Open / OpenFDA
- [ ] Drug class-level interaction detection (multiplicative coverage)
- [ ] Polypharmacy risk score
- [ ] Audit log for research data collection
- [ ] Validation framework (sensitivity / specificity against known cases)
- [ ] PDF prescription report export
- [ ] AI Copilot (natural language clinical queries)

---

## Developer

**Abdul Rehman**
PharmD Student | [Your University], Pakistan
Clinical Informatics & Patient Safety Research

> *"Built independently to address a real gap in prescription safety at the point of care in low-resource settings."*

---

## References

Key references underpinning the clinical database:

- Baxter K, Preston CL (eds). *Stockley's Drug Interactions.* Pharmaceutical Press.
- *British National Formulary (BNF) 84.* BMJ Group and Pharmaceutical Press, 2022.
- Katzung BG. *Basic & Clinical Pharmacology*, 15th ed. McGraw-Hill.
- DiPiro JT et al. *Pharmacotherapy: A Pathophysiologic Approach*, 11th ed.
- *Sanford Guide to Antimicrobial Therapy.* Antimicrobial Therapy Inc.
- WHO Model Formulary. World Health Organization.

---

*RxGuard © 2026 | Developed in Pakistan 🇵🇰*
