# FastAPI Application

A basic FastAPI application setup.

## Installation

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the server with:

```bash
uvicorn main:app --reload
```

The API will be available at:
- http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Endpoints

- `GET /` - Returns a hello world message
- `GET /health` - Health check endpoint

