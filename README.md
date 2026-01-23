# RxGuard Ultimate 🛡️ |Clinical Decision Support System for Medication Safety 

**RxGuard Ultimate**RxGuard Ultimate is a rule-based Clinical Decision Support System (CDSS) designed to assist pharmacists and clinicians in identifying common drug-related problems during prescription screening.

The current system implements transparent, explainable pharmacotherapy logic (e.g., renal dose adjustment rules, drug–drug interactions, contraindications, and IV preparation guidance).

Future development aims to explore the integration of machine learning and large language models to enhance clinical reasoning capabilities while preserving explainability.

## 🚀 Key Features

### 1. 🏥 Clinical Analysis Engine (Rule-Based)

* **Renal Guard:** Automatically flags dose adjustments based on calculated CrCl/eGFR

* **Interaction Checker:** Detects critical drug–drug interactions and lifestyle conflicts

* **Contraindication & Allergy Safety:** Cross-references patient comorbidities and allergy history

### 2. 💉 Parenteral Intelligence
* **IV Reconstitution Calculator:** Precise math for dilution, final concentration, and infusion rates.
* **Stability & Compatibility:** Provides evidence-based data on diluents (NS vs D5W) and storage.

### 3. 🤖 🔬 Planned AI Extension (Future Work)

**Exploration of LLM-assisted clinical query handling**

**Potential integration of machine learning to support complex decision scenarios**

**Focus on maintaining explainability and clinical trust**

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Python)
* **Backend Logic**: Rule-based clinical decision engine
* **OCR:** Tesseract (for reading prescription images)
* **Deployment:** Streamlit Cloud

## 📦 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone [https://github.com/YOUR-USERNAME/RxGuard-Ultimate.git](https://github.com/YOUR-USERNAME/RxGuard-Ultimate.git)

   pip install -r requirements.txt

   streamlit run app.py
## ⚖️ License & Copyright
**© 2026 [Abdul Rehman Memon]. All Rights Reserved.**

This software is the intellectual property of Abdul Rehman Memon. 
- **Academic Use:** Viewable for educational and evaluation purposes (e.g., PhD admissions).
- **Commercial Use:** Strictly prohibited. No part of this code may be copied, modified, or sold without written permission from the author.
