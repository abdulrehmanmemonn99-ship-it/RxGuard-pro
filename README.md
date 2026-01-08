# RxGuard Ultimate 🛡️ | AI-Powered Clinical Decision Support

**RxGuard Ultimate** is a hybrid "Neuro-Symbolic" Clinical Decision Support System (CDSS) designed to assist pharmacists and clinicians in optimizing medication safety.

It bridges the gap between **deterministic safety protocols** (hard-coded rules for renal adjustments, interactions, and IV compatibility) and **Generative AI** (LLM-based clinical reasoning for complex case queries).

## 🚀 Key Features

### 1. 🏥 Clinical Analysis Engine (Deterministic)
* **Renal Guard:** Automatically flags dose adjustments based on calculated CrCl/eGFR.
* **Interaction Checker:** Detects critical drug-drug interactions (DDIs) and lifestyle conflicts.
* **Contraindication & Allergy Safety:** Cross-references patient comorbidities and allergy history against formulary data.

### 2. 💉 Parenteral Intelligence
* **IV Reconstitution Calculator:** Precise math for dilution, final concentration, and infusion rates.
* **Stability & Compatibility:** Provides evidence-based data on diluents (NS vs D5W) and storage.

### 3. 🤖 AI Clinical Copilot (Generative)
* **Neuro-Symbolic Integration:** Uses GPT-4o to handle unstructured queries and complex clinical scenarios not covered by standard databases.
* **Reasoning Engine:** capable of explaining *why* an interaction is occurring or suggesting alternatives based on recent guidelines.

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Python)
* **AI/LLM:** OpenAI API (GPT-4o)
* **OCR:** Tesseract (for reading prescription images)
* **Deployment:** Streamlit Cloud

## 📦 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone [https://github.com/YOUR-USERNAME/RxGuard-Ultimate.git](https://github.com/YOUR-USERNAME/RxGuard-Ultimate.git)

   pip install -r requirements.txt

   streamlit run app.py
## ⚖️ License & Copyright
**© 2026 [Your Name]. All Rights Reserved.**

This software is the intellectual property of [Your Name]. 
- **Academic Use:** Viewable for educational and evaluation purposes (e.g., PhD admissions).
- **Commercial Use:** Strictly prohibited. No part of this code may be copied, modified, or sold without written permission from the author.
