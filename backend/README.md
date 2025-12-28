<h1 align="center">AI Powered Form Filling</h1>

This backend provides multilingual, AI-powered PDF form filling with OCR and hardware acceleration support.

---

## 🚀 Features

- **Multilingual Form Filling**: Supports 80+ languages for form extraction and filling.
- **Plug-n-Play OCR**: Integrates with [plug-n-play-ocr](https://github.com/SaiDhinakar/plug-n-play-ocr) for robust text extraction.
- **Automatic Hardware Detection**: Utilizes available accelerators (OpenVINO, GPU, CPU) for optimal performance.
- **Easy Configuration**: Language support can be customized in `ocr/languages.json`.
- **Modern Python Stack**: Built with Python 3.12+ and [uv](https://github.com/astral-sh/uv) package manager.

---

## 🛠️ Setup & Installation

1. **Clone the repository**
2. **Install dependencies** (requires [uv](https://github.com/astral-sh/uv)):
   ```sh
   uv sync
   ```
3. **Configure OCR languages** (optional):
   - Edit `ocr/languages.json` to add/remove supported languages.

---

## 🏃 Usage

From the `backend` directory:

```sh
./scripts/run_server.sh
```

This will start:

- OCR service (background)
- AI Agent service (background)
- FastAPI backend (background)

To stop all services:

```sh
./scripts/stop_server.sh
```

---

## 📦 Project Structure

- `ocr/` — OCR microservice and language configs
- `ai_agents/` — AI agent service for extraction/filling
- `api/` — FastAPI backend API
- `scripts/` — Automation scripts for running/stopping services

---

## 🤝 Contributors

<table>
   <tr>
      <td align="center">
         <a href="https://github.com/SaiDhinakar">
            <img src="https://avatars.githubusercontent.com/u/89453268?v=4" width="80" style="border-radius:50%"><br/>
            <sub><b>SaiDhinakar</b></sub>
         </a>
      </td>
      <td align="center">
         <a href="https://github.com/Pradeesh1108">
            <img src="https://avatars.githubusercontent.com/u/154534896?v=4"width="80" style="border-radius:50%"><br/>
            <sub><b>Pradeesh1108</b></sub>
         </a>
      </td>
      <td align="center">
         <a href="https://github.com/RUBA-SHREE">
            <img src="https://avatars.githubusercontent.com/u/218800726?v=4"" width="80" style="border-radius:50%"><br/>
            <sub><b>RUBA-SHREE</b></sub>
         </a>
      </td>
   </tr>
</table>

---

## ⚠️ Limitations

- Only works with editable PDF forms (AcroForm/XFA). Support for all PDF types (including scanned/static PDFs) is planned for the future.
