# Transaction Engine 💸

The backend service is responsible for ingesting transaction webhooks, processing them asynchronously, and serving status updates.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Installation

1.  **Create and Activate Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Server**:
    ```bash
    uvicorn app.main:app --reload
    ```
    The server will start at `http://127.0.0.1:8000`.

## 🛠️ Technical Choices

### Framework: FastAPI
Chosen for its high performance (async support), automatic validation (Pydantic), and built-in interactive documentation (Swagger UI). It allows us to handle high-throughput webhook ingestion efficiently.

### Asynchronous Processing: BackgroundTasks
Webhooks require fast acknowledgement. We use FastAPI's `BackgroundTasks` to immediately return a `202 Accepted` response while processing the expensive business logic (simulated by a delay) in the background.

### Database: SQLite & SQLAlchemy
- **SQLite**: Used for simplicity and ease of setup during assessment/development.
- **SQLAlchemy**: Provides a robust ORM layer, allowing us to switch to PostgreSQL or MySQL in production without changing application code.

### Validation: Pydantic V2
Ensures data integrity at the ingress point. We strictly validate transaction payloads (amount, currency, account formats) before they hit our business logic layer.

## 🔌 API Documentation

Once the server is running, visit:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Key Endpoints

- `GET /`: Service health check.
- `POST /v1/webhooks/transactions`: Ingest a new transaction.
- `GET /v1/transactions/{id}`: Check the status of a specific transaction.

## 🧪 Testing

We have provided a **Postman Collection** (`postman_collection.json`) in the root directory to verify the API endpoints manually.

1.  Import `postman_collection.json` into Postman.
2.  Run the requests in order (Health Check -> Ingest -> Status).

