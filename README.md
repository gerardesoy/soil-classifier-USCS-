#ASTM D2487 Unified Soil Classification System (USCS)

A Python-based tool for automating soil classification according to the **ASTM D2487** standard. This application handles complex geotechnical scenarios including dual symbols, the "hatched zone" (CL-ML), and organic soil detection.

Designed for Civil Engineering students, laboratory professionals, and geotechnical review.

## 🚀 Features

* **Full ASTM D2487 Compliance:** Classifies soils based on Sieve Analysis and Atterberg Limits.
* **Dual Symbol Support:** Correctly handles borderline cases like `SW-SM` (Well-graded sand with silt) and `SP-SC`.
* **Hatched Zone Logic:** Automatically detects and classifies soils in the CL-ML zone.
* **Interactive Plasticity Chart:** Visualizes the soil's position relative to the A-Line and U-Line using Matplotlib.
* **Organic Soil Detection:** Includes logic for organic clays and silts based on oven-dried liquid limits.

## 🛠️ Installation & Usage

### Prerequisites
* Python 3.8+
* pip

### Local Setup
1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/soil-classifier.git](https://github.com/YOUR_USERNAME/soil-classifier.git)
    cd soil-classifier
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the application:
    ```bash
    streamlit run app.py
    ```

## 📊 Standards Reference
This tool implements logic derived from:
* **ASTM D2487:** Standard Practice for Classification of Soils for Engineering Purposes (Unified Soil Classification System).
* **Table 5.2:** Criteria for assigning group symbols.
* **Figure 5.3:** Plasticity Chart logic.

![App Demo](https://github.com/gerardesoy/soil-classifier-USCS-/blob/main/demo_screenshot.PNG?raw=true)

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
