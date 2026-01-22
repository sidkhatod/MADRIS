# Convolve - Disaster Decision Support System

An intelligent decision support system that aggregates multi-modal disaster data (text, geospatial) to provide actionable insights and historical analogies for decision-makers.

## System Architecture

- **Frontend**: React (Vite) + Tailwind CSS + Shadcn UI
- **Backend**: Python (Flask)
- **Database**: Qdrant (Vector Database) for semantic memory
- **AI/LLM**: Groq (Llama 3) for reasoning & HuggingFace for embeddings

## Local Development

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Qdrant Cloud API Key (or local Qdrant instance)

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure Environment Variables:
   - Create a `.env` file in `backend/` (see `.env.example` or use provided keys).
   - Required variables: `GROQ_API_KEY`, `HF_API_TOKEN`, `QDRANT_URL`, `QDRANT_API_KEY`.
5. Run the server:
   ```bash
   python api/app.py
   ```
   Server runs at `http://localhost:5000`.

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   App runs at `http://localhost:5173`.

## Deployment on Render

This project is ready for deployment on [Render](https://render.com).

### Backend Service (Web Service)
1. **Build Command**: `pip install -r backend/requirements.txt`
2. **Start Command**: `gunicorn --chdir backend api.app:app`
   - *Note: using `gunicorn` for production stability.*
3. **Environment Variables**: Add your API keys (`GROQ_API_KEY`, `QDRANT_URL`, etc.) in the Render dashboard.
4. **Root Directory**: `.` (Project Root)

### Frontend Service (Static Site)
1. **Build Command**: `npm install && npm run build`
2. **Publish Directory**: `dist`
3. **Environment Variables**:
   - `VITE_API_BASE_URL`: The URL of your deployed Backend Service (e.g., `https://convolve-backend.onrender.com/api`).
     *Important: You must deploy the Backend first to get this URL.*
4. **Root Directory**: `frontend`
