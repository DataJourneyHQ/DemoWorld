# 🎓 Academy Demo — AI Templates & Demos

A curated collection of ready-to-use AI demo templates built for learning, experimentation, and rapid prototyping. This repository is maintained by [DataJourneyHQ](https://github.com/DataJourneyHQ) as an educational resource for developers, data scientists, and AI enthusiasts.

---

## 📌 Purpose

`academy_demo` provides hands-on, self-contained templates that showcase common AI/ML use cases. Each demo is designed to be:

- **Beginner-friendly** — clear setup instructions and well-commented code
- **Self-contained** — minimal dependencies, runnable in notebooks or scripts
- **Practical** — based on real-world scenarios you can adapt to your own projects

---

## 🗂️ Suggested AI Demos & Templates

Below is the roadmap of demos we plan to add to this repository. Community contributions are welcome!

### 🤖 Natural Language Processing (NLP)

| Template | Description | Status |
|----------|-------------|--------|
| **RAG Chatbot** | Q&A chatbot using Retrieval-Augmented Generation (RAG) with a local document store | 🔜 Planned |
| **Text Summarization** | Summarize long documents using open-source LLMs (e.g., BART, T5) | 🔜 Planned |
| **Sentiment Analysis** | Classify customer reviews or social posts as positive, neutral, or negative | 🔜 Planned |
| **Named Entity Recognition (NER)** | Extract people, organizations, and locations from unstructured text | 🔜 Planned |
| **Text Classification** | Multi-class topic classification pipeline with fine-tuning example | 🔜 Planned |
| **Language Translation** | Translate text between languages using Hugging Face models | 🔜 Planned |

### 🖼️ Computer Vision

| Template | Description | Status |
|----------|-------------|--------|
| **Image Classification** | Classify images using a pre-trained CNN (ResNet/EfficientNet) | 🔜 Planned |
| **Object Detection** | Detect and label objects in images using YOLO | 🔜 Planned |
| **Image Captioning** | Generate natural language descriptions for images | 🔜 Planned |
| **OCR Pipeline** | Extract text from images and PDFs using Tesseract / PaddleOCR | 🔜 Planned |

### 🔊 Audio & Speech

| Template | Description | Status |
|----------|-------------|--------|
| **Speech-to-Text** | Transcribe audio files using OpenAI Whisper | 🔜 Planned |
| **Text-to-Speech** | Convert text into natural-sounding audio | 🔜 Planned |

### 📊 Tabular Data & Predictive Analytics

| Template | Description | Status |
|----------|-------------|--------|
| **Anomaly Detection** | Detect outliers in time series or tabular datasets | 🔜 Planned |
| **Churn Prediction** | Predict customer churn with an end-to-end ML pipeline | 🔜 Planned |
| **Demand Forecasting** | Time series forecasting using Prophet or NeuralForecast | 🔜 Planned |
| **Recommendation System** | Build a content-based or collaborative filtering recommender | 🔜 Planned |

### 🛠️ LLM-Powered Applications

| Template | Description | Status |
|----------|-------------|--------|
| **Code Generation Assistant** | Use an LLM to generate, review, and explain code snippets | 🔜 Planned |
| **Document Q&A** | Answer questions over PDF/HTML documents with an LLM + vector DB | 🔜 Planned |
| **AI Agent with Tool Use** | Build a simple AI agent that can call external APIs/tools | 🔜 Planned |
| **Structured Data Extraction** | Extract structured JSON from free-form text using function calling | 🔜 Planned |
| **Prompt Engineering Playground** | Compare prompting strategies (zero-shot, few-shot, chain-of-thought) | 🔜 Planned |

### 🔗 MLOps & Data Pipelines

| Template | Description | Status |
|----------|-------------|--------|
| **AI-Powered ETL** | Data pipeline with AI-driven transformations and enrichment | 🔜 Planned |
| **Model Evaluation Dashboard** | Visualize and compare ML model metrics interactively | 🔜 Planned |
| **Feature Store Demo** | Manage and serve ML features using an open-source feature store | 🔜 Planned |

---

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/DataJourneyHQ/academy_demo.git
   cd academy_demo
   ```

2. **Navigate to a demo folder** (once templates are added)
   ```bash
   cd demos/rag-chatbot
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the demo**
   ```bash
   jupyter notebook demo.ipynb
   # or
   python main.py
   ```

---

## 📁 Planned Repository Structure

```
academy_demo/
├── demos/
│   ├── rag-chatbot/
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   └── demo.ipynb
│   ├── sentiment-analysis/
│   ├── image-classification/
│   └── ...
├── shared/
│   └── utils/          # Shared helper functions
├── LICENSE
└── README.md
```

Each demo will include:
- A **`README.md`** explaining the concept and how to run it
- A **Jupyter notebook** (`demo.ipynb`) for interactive exploration
- A **`requirements.txt`** for dependencies
- Optionally, a **`main.py`** script for non-notebook usage

---

## 🤝 Contributing

We welcome contributions! If you'd like to add a new demo or improve an existing one:

1. Fork the repository
2. Create a new branch: `git checkout -b feat/your-demo-name`
3. Add your demo under `demos/your-demo-name/`
4. Ensure your demo includes a `README.md` and a working example
5. Open a Pull Request — we'll review and merge it!

Please follow the existing folder structure and keep demos self-contained.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

> **Have a demo idea?** Open an [issue](https://github.com/DataJourneyHQ/academy_demo/issues) and let us know what you'd like to see added!
