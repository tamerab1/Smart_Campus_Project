# Smart Campus Assistant 🎓🤖

## Overview
Smart Campus Assistant is an intelligent, lightweight web application designed to help students instantly find answers regarding campus facilities, schedules, and general information. It leverages AI to categorize queries, maintain conversational context, and provide accurate answers based on a structured campus database.

## 1. Architecture
The system is built with a modern, modular architecture:
* **Frontend (SSR):** Built using **Jinja2** templates (`app/templates`) and plain CSS (`app/static`). The views are server-side rendered and tightly integrated with the backend.
* **Backend:** Powered by **FastAPI** for high-performance, asynchronous routing and request handling.
* **AI Engine:** Integrates **Google Gemini API** with advanced Prompt Engineering. It features a robust Fallback Mechanism, Context Resolution (remembering previous questions), and query categorization (Schedule, General Info, Technical Issue).
* **Database:** Managed via **SQLAlchemy ORM**, handling structured campus data.

## 2. Environment Variables
To run this project, you must create a `.env` file in the root directory. 
*(Note: The `.env` file is excluded from git via `.gitignore` for security purposes).*

Add the following variables to your `.env` file:

```env
# Your Google Gemini API Key
GEMINI_API_KEY=your_api_key_here

# Database Connection URL (Use sqlite for local testing, or postgresql)
# If using Docker with a local DB, use host.docker.internal instead of localhost
DATABASE_URL=sqlite:///./campus.db
```

## 3. Installation & Local Run

### Option A: Standard Python Environment
1. Clone the repository and navigate to the project root.
2. Ensure you have Python 3.12 installed.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI server using Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Open your browser and navigate to:
   * **Web Interface:** `http://localhost:8000`
   * **API Docs (Swagger):** `http://localhost:8000/docs`

### Option B: Docker (Multi-Stage Build)
The project includes a multi-stage `Dockerfile` optimized for minimal image size.
1. Build the Docker image:
   ```bash
   docker build -t smart-campus-api .
   ```
2. Run the container (injecting the `.env` file):
   ```bash
   docker run -p 8000:8000 --env-file .env smart-campus-api
   ```

## 4. Testing
The project includes automated Unit Tests utilizing `pytest`. The tests cover edge cases such as empty inputs, multi-lingual queries, out-of-scope questions, and fallback mechanisms.

To run the test suite:
```bash
python -m pytest test_main.py
```

## 5. Troubleshooting & Common Issues
* **Database Connection in Docker:** If your database is hosted on your local machine and you are running the app via Docker, replace `localhost` in your `DATABASE_URL` with `host.docker.internal`.
* **Jinja2 Template Errors:** Ensure the `app/templates` folder exists and `jinja2` is listed in your `requirements.txt`.
* **API Rate Limits (Error 429):** If the AI service stops responding, check your Gemini API usage limits.
* **SyntaxError in f-strings:** The Docker image uses Python 3.12. Ensure your local environment matches this version to prevent f-string backslash errors.