## 🦜 Process management system xirico (PMS-Xirico)

[![Status: Em Desenvolvimento](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)](https://github.com/Umohau/PSM-xirico)
[![Versão](https://img.shields.io/badge/Versão-0.1.0--alpha-blue)](https://github.com/Umohau/PSM-xirico)
[![Plataforma](https://img.shields.io/badge/Plataforma-Windows_|_Linux-lightgrey)]()
[![Licença](https://img.shields.io/badge/Licença-Uso_Interno-red)]() 



## About the Project

**PMS Xirico** is a desktop system developed to automate and centralize the operational management of Xirico, a company specialized in exporting small birds.

The system eliminates the manual work of writing documents by integrating:
- **Customer and Operator Registration**.
- **Automatic generation of Applications and Receipts** (batch or individual).
- **Secure storage** of all documentation for export processes (certificates, inspection reports, etc.).

> **Current status:** We are finalizing the coding of the use cases and their tests.

## ⚙️ Tech Stack and Prerequisites

- **Python:** 3.10 or higher (tested with 3.11/3.12)
- **Package Manager:** `pip` + `venv` (virtual environment required)
- **Database:** SQLite (development) or PostgreSQL 14+ (production)
- **Documents:** Microsoft Word (.docx) as base templates
- **Operating System:** Windows 10/11 (native) or Linux (Ubuntu/Debian)

## 🚀 Installation and Running

> **Note:** The main application entry point is not available yet.  
> You can still set up the environment and run the existing tests.

### 1. Clone the repository

```bash
git clone https://github.com/Umohau/PSM-xirico
cd PSM-xirico
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the tests

```bash
pytest
```

> Once the main module is implemented, instructions to run the application will be added here.

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.