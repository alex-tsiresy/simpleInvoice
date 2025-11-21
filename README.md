# Compass Document Processing System

A comprehensive document processing system with OCR, invoice extraction, and secure authentication.

## Features

- 📄 **Multi-format Document Support**: PDF, images (PNG, JPG, JPEG, TIFF, BMP)
- 🔒 **Secure Authentication**: Clerk JWT-based authentication
- 🔍 **Advanced OCR**: RapidOCR with ONNX Runtime (multi-page PDF support)
- 🤖 **Invoice Extraction**: OpenAI GPT-4o-mini for structured invoice data extraction
- ☁️ **Object Storage**: MinIO S3-compatible storage
- 🗄️ **PostgreSQL Database**: Metadata and results storage
- 🐳 **Docker Compose**: Production-ready deployment

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Host Machine                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  OCR Microservice (port 8119)                        │  │
│  │  - Python venv                                       │  │
│  │  - RapidOCR (ONNX Runtime - CPU)                    │  │
│  └──────────────────────────────────────────────────────┘  │
│           ▲                                                  │
│           │ host.docker.internal:8119                       │
│           │                                                  │
│  ┌────────┴────────── compass-network (Docker) ─────────┐  │
│  │                                                        │  │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐      │  │
│  │  │ Frontend │◄───│ Backend  │◄───│PostgreSQL│      │  │
│  │  │ (React)  │    │(FastAPI) │    │  :5432   │      │  │
│  │  │  :3000   │    │  :8000   │    └──────────┘      │  │
│  │  └──────────┘    └────┬─────┘                       │  │
│  │                       │                              │  │
│  │                       ▼                              │  │
│  │                  ┌──────────┐    ┌──────────┐      │  │
│  │                  │  MinIO   │    │ pgAdmin  │      │  │
│  │                  │:9000/9001│    │  :5050   │      │  │
│  │                  └──────────┘    └──────────┘      │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Processing Pipeline

```
1. User uploads document → Frontend (React)
2. Frontend → Backend API (FastAPI)
3. Backend → MinIO (file storage)
4. Backend → OCR Service (RapidOCR on host)
5. OCR Service returns text → Backend
6. Backend → OpenAI API (invoice extraction)
7. Backend stores results → PostgreSQL
8. Backend returns data → Frontend
9. User views processed document with invoice data
```

### Technology Stack

**Frontend:**
- React 18.2.0
- Clerk Authentication
- React Dropzone (file uploads)
- Custom CSS styling

**Backend:**
- FastAPI (Python 3.10)
- SQLAlchemy 2.0 (async ORM)
- AsyncPG (PostgreSQL driver)
- MinIO client
- httpx (async HTTP client)

**OCR Service:**
- RapidOCR (ONNX Runtime)
- FastAPI microservice
- CPU-based processing
- Multi-page PDF support

**Infrastructure:**
- PostgreSQL 15 (database)
- MinIO (S3-compatible storage)
- pgAdmin 4 (database management)
- Docker Compose (orchestration)

**AI/ML:**
- OpenAI GPT-4o-mini (invoice extraction)
- Structured JSON outputs

## Prerequisites

- **Docker & Docker Compose**: Container orchestration (Docker Compose v2 plugin)
- **Python 3.10+**: For OCR service (runs on host)
- **Clerk Account**: Authentication (https://clerk.com)
- **OpenAI API Key**: Invoice extraction (https://platform.openai.com)

**Note**:
- The OCR service runs on the host machine (not in Docker) for better compatibility and performance.
- This project uses Docker Compose v2 (plugin version). Commands use `docker compose` (with space) instead of `docker-compose` (with hyphen).

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# 1. Clone repository
git clone <repository-url>
cd compassDemo

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys (see Configuration section below)

# 3. Setup OCR service
cd ocr-service
./setup.sh
cd ..

# 4. Start all services
./scripts/start-all.sh
```

The startup script will:
- Start the OCR service on port 8119
- Wait for OCR health check
- Launch all Docker containers
- Initialize MinIO bucket

### Option 2: Manual Setup

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 2. Setup and start OCR service
cd ocr-service
./setup.sh          # Creates Python venv, installs dependencies
./start.sh          # Starts OCR service on port 8119
cd ..

# 3. Start Docker services
docker compose up --build
```

### Configuration

Edit `.env` with your credentials:

```env
# Clerk Authentication
CLERK_SECRET_KEY=your_clerk_secret_key_here
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
REACT_APP_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here

# Database
POSTGRES_USER=compassuser
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=compassdb
DATABASE_URL=postgresql://compassuser:your_password@postgres:5432/compassdb

# MinIO S3 Storage
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_minio_password_here
MINIO_ENDPOINT=minio:9000
MINIO_BUCKET=documents
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=your_minio_secret_key_here

# OCR Service
PADDLEOCR_VL_URL=http://host.docker.internal:8119

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Backend
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# Frontend
REACT_APP_BACKEND_URL=http://localhost:8000
FRONTEND_PORT=3000
```

**Get API Keys:**
- Clerk: https://dashboard.clerk.com
- OpenAI: https://platform.openai.com/api-keys

### Access Services

Once started, services are available at:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Clerk sign-in |
| **Backend API** | http://localhost:8000 | Bearer token |
| **API Documentation** | http://localhost:8000/docs | (Swagger UI) |
| **MinIO Console** | http://localhost:9001 | minioadmin / [your_password] |
| **pgAdmin** | http://localhost:5050 | alex@example.com / alex |
| **OCR Service** | http://localhost:8119 | No auth |

## Project Structure

```
compassDemo/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Main application & API endpoints
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection & session
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── auth.py            # Clerk JWT authentication
│   │   ├── storage.py         # MinIO S3 client
│   │   ├── ocr_service.py     # OCR microservice client
│   │   ├── invoice_extractor.py  # OpenAI invoice extraction
│   │   ├── summarizer.py      # (Legacy) Document summarization
│   │   └── classifier.py      # (Legacy) Document classification
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── index.js           # Entry point
│   │   ├── App.js             # Main app with auth provider
│   │   └── components/
│   │       ├── Dashboard.js   # Main authenticated view
│   │       ├── FileUpload.js  # Drag-and-drop upload
│   │       ├── DocumentList.js   # Document grid display
│   │       └── DocumentCard.js   # Document detail card
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── ocr-service/                # OCR microservice (runs on host)
│   ├── main.py                # FastAPI OCR service
│   ├── requirements.txt
│   ├── setup.sh               # Setup script
│   ├── start.sh               # Start script
│   └── venv/                  # Python virtual environment
├── scripts/
│   ├── start-all.sh           # Start all services
│   ├── stop-all.sh            # Stop all services
│   └── status.sh              # Check service status
├── docker-compose.yml         # Docker orchestration
└── .env                       # Environment configuration
```

## API Endpoints

### Authentication

All document endpoints require Clerk authentication token:

```bash
Authorization: Bearer <clerk_jwt_token>
```

Get token via Clerk SDK in frontend: `const token = await getToken();`

### Document Management

#### Upload Document

```bash
POST /api/documents/upload
Content-Type: multipart/form-data

curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@invoice.pdf"
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "uuid.pdf",
  "original_filename": "invoice.pdf",
  "status": "uploaded",
  "created_at": "2025-11-21T12:00:00"
}
```

#### Get Document

```bash
GET /api/documents/{document_id}

curl http://localhost:8000/api/documents/{id} \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "uuid.pdf",
  "status": "completed",
  "ocr_text": "Extracted text...",
  "invoice_data": {
    "invoice_number": "INV-001",
    "invoice_date": "2025-11-01",
    "total_amount": 1250.00,
    "currency": "USD",
    "sender": {...},
    "receiver": {...}
  },
  "file_url": "presigned_url"
}
```

#### List Documents

```bash
GET /api/documents?skip=0&limit=50

curl http://localhost:8000/api/documents \
  -H "Authorization: Bearer <token>"
```

#### Delete Document

```bash
DELETE /api/documents/{document_id}

curl -X DELETE http://localhost:8000/api/documents/{id} \
  -H "Authorization: Bearer <token>"
```

#### Download Document

```bash
GET /api/documents/{document_id}/download

curl http://localhost:8000/api/documents/{id}/download \
  -H "Authorization: Bearer <token>"
```

Returns a presigned URL valid for 1 hour.

### Document Processing Statuses

| Status | Description |
|--------|-------------|
| `uploaded` | File uploaded, processing not started |
| `processing` | OCR and extraction in progress |
| `ocr_complete` | OCR completed, invoice extraction may have failed |
| `completed` | Fully processed with invoice data |
| `failed` | Processing error occurred |

## Invoice Data Extraction

The system uses OpenAI GPT-4o-mini with structured outputs to extract invoice information:

**Extracted Fields:**
- Invoice number, date, due date
- Payment terms
- Sender information (name, address, email, phone, tax ID)
- Receiver information (name, address, email, phone, tax ID)
- Financial data (subtotal, tax amount, total amount, currency)
- Additional notes

**Example Invoice Data:**
```json
{
  "invoice_number": "INV-2025-001",
  "invoice_date": "2025-11-15",
  "due_date": "2025-12-15",
  "payment_terms": "Net 30",
  "total_amount": 15750.00,
  "currency": "USD",
  "subtotal": 15000.00,
  "tax_amount": 750.00,
  "sender": {
    "name": "Acme Corp",
    "address": "123 Main St, City, State 12345",
    "email": "billing@acme.com",
    "phone": "+1-555-0123",
    "tax_id": "12-3456789"
  },
  "receiver": {
    "name": "Client Inc",
    "address": "456 Oak Ave, Town, State 67890",
    "email": "ap@client.com",
    "phone": "+1-555-9876",
    "tax_id": "98-7654321"
  },
  "notes": "Payment due within 30 days"
}
```

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Live reload**: Code changes automatically reload the server.

### Frontend Development

```bash
cd frontend
npm install

# Run development server
npm start
```

**Live reload**: Runs on http://localhost:3000 with hot module replacement.

### OCR Service Development

```bash
cd ocr-service
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run development server
python main.py
# Or: uvicorn main:app --reload --host 0.0.0.0 --port 8119
```

### Database Access

**Direct psql connection:**
```bash
psql -h localhost -p 5432 -U compassuser -d compassdb
```

**Via pgAdmin:**
1. Open http://localhost:5050
2. Login: alex@example.com / alex
3. Add server:
   - Name: Compass DB
   - Host: postgres
   - Port: 5432
   - Username: compassuser
   - Password: (from .env)

## Operational Commands

### Check Status

```bash
./scripts/status.sh
```

Shows status of all services and connectivity.

### View Logs

```bash
# All Docker services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend

# OCR service (on host)
tail -f ocr-service/ocr-service.log
```

### Stop Services

```bash
# Stop all (recommended)
./scripts/stop-all.sh

# Stop Docker only
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

### Restart Service

```bash
# Restart specific Docker service
docker compose restart backend

# Rebuild and restart
docker compose up -d --build backend

# Restart OCR service
cd ocr-service
./start.sh
```

## Troubleshooting

### OCR Service Not Starting

**Check if port 8119 is in use:**
```bash
lsof -i :8119
# Kill existing process if needed
```

**Check OCR service logs:**
```bash
tail -f ocr-service/ocr-service.log
```

**Reinstall dependencies:**
```bash
cd ocr-service
rm -rf venv
./setup.sh
./start.sh
```

### Backend Cannot Connect to OCR Service

**Verify OCR service is running:**
```bash
curl http://localhost:8119/health
```

**Check Docker extra_hosts configuration:**
- Ensure `docker-compose.yml` has `host.docker.internal:host-gateway` in backend extra_hosts
- This allows containerized backend to reach host-based OCR service

### Docker Compose Command Not Found

If you see `docker-compose: command not found`:
- This project uses Docker Compose v2 (plugin version)
- Use `docker compose` (with space) instead of `docker-compose` (with hyphen)
- All scripts have been updated to use the v2 syntax
- Verify installation: `docker compose version`

### Database Connection Issues

**Reset database:**
```bash
docker compose down -v
docker compose up -d postgres
```

**Check database health:**
```bash
docker compose exec postgres pg_isready -U compassuser -d compassdb
```

### MinIO Issues

**Access MinIO console:**
http://localhost:9001 (login with credentials from .env)

**Check bucket exists:**
```bash
docker compose exec minio mc ls myminio/
```

**Recreate bucket:**
```bash
docker compose restart minio-init
```

### Frontend Cannot Connect to Backend

**Check CORS configuration:**
- Backend should allow frontend origin in CORS middleware (main.py)

**Verify environment variable:**
```bash
# In frontend container
echo $REACT_APP_BACKEND_URL
```

### Authentication Issues

**Verify Clerk keys:**
- Check `.env` has correct `CLERK_SECRET_KEY` and `CLERK_PUBLISHABLE_KEY`
- Ensure frontend has `REACT_APP_CLERK_PUBLISHABLE_KEY`

**Check Clerk dashboard:**
- Verify application is active at https://dashboard.clerk.com

## Performance Considerations

### OCR Processing

- **CPU-based**: RapidOCR uses ONNX Runtime on CPU (no GPU required)
- **Processing time**: ~2-5 seconds per page for typical documents
- **Concurrency**: Service handles one request at a time (single-threaded)
- **Scalability**: For higher throughput, run multiple OCR service instances on different ports

### OpenAI API

- **Rate limits**: OpenAI has rate limits per account tier
- **Cost optimization**: Invoice extraction uses gpt-4o-mini (cost-effective)
- **Temperature**: Set to 0.0 for deterministic extraction
- **Timeout**: 60 seconds per request

### Database

- **Connection pooling**: Pool size 10, max overflow 20
- **Indexes**: Primary keys and user_id indexed for fast queries
- **Schema**: SQLAlchemy ORM with automatic table creation

### Storage

- **MinIO**: S3-compatible, scales horizontally
- **Presigned URLs**: 1-hour expiration for temporary access
- **Cleanup**: Deleted documents also removed from MinIO

## Security Considerations

⚠️ **Important Security Notes:**

1. **JWT Verification**: Current implementation skips Clerk JWT signature verification (backend/app/auth.py:20). For production, implement full JWKS verification.

2. **Environment Variables**: Never commit `.env` file with real credentials. Always use `.env.example` as template.

3. **API Keys**: Rotate OpenAI and Clerk keys regularly.

4. **Network**: Consider using HTTPS/TLS in production with reverse proxy (nginx, traefik).

5. **Database**: Use strong passwords and restrict network access in production.

## Data Flow

### Upload and Processing Flow

1. **User uploads document** via Frontend drag-and-drop
2. **Frontend** sends file to Backend `/api/documents/upload`
3. **Backend** uploads file to MinIO, creates DB record
4. **Backend** triggers background processing task
5. **Background task** sends file to OCR service at `host.docker.internal:8119`
6. **OCR service** processes with RapidOCR, returns text and metadata
7. **Backend** stores OCR results, updates status to `ocr_complete`
8. **Backend** sends OCR text to OpenAI for invoice extraction
9. **OpenAI** returns structured invoice data
10. **Backend** stores invoice data, updates status to `completed`
11. **Frontend** polls and displays updated document with invoice data

### Auto-Refresh

Frontend auto-refreshes document list every 5 seconds to show processing progress in real-time.

## Technology Choices

### Why RapidOCR?

- **Cross-platform**: Works on CPU without GPU requirements
- **ONNX Runtime**: Fast inference with optimized models
- **Open source**: No licensing costs
- **Multi-language**: Supports 100+ languages
- **Small models**: ~16MB total model size

### Why Separate OCR Service?

- **Isolation**: OCR processing isolated from main backend
- **Scalability**: Can run multiple instances
- **GPU flexibility**: Easier to manage GPU dependencies on host
- **Development**: Simpler debugging and testing

### Why OpenAI for Invoice Extraction?

- **Structured outputs**: Guaranteed JSON schema compliance
- **Accuracy**: High-quality extraction with GPT-4o-mini
- **No training**: No need to train/maintain custom models
- **Flexibility**: Easy to adjust extraction schema

