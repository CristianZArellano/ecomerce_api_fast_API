
# GEMINI Analysis for E-commerce API

## Project Overview

This is a professional e-commerce API built with FastAPI. It features a robust set of functionalities including JWT authentication with refresh tokens, rate limiting using Redis, structured JSON logging, and Redis caching for products and user sessions. The API is designed to be production-ready with Docker containerization, a CI/CD pipeline using GitHub Actions, and configurations for deployment on Railway and Render.

The architecture consists of a FastAPI application connected to a PostgreSQL database for data persistence and a Redis instance for caching and session management. The project uses SQLAlchemy as the ORM with asynchronous support, Pydantic for data validation, and follows a clean and modular structure.

## Building and Running

The project can be run in two ways: using Docker or locally.

### Docker (Recommended)

1.  **Build and start all services:**
    ```bash
    docker-compose up -d
    ```
2.  **View logs:**
    ```bash
    docker-compose logs -f api
    ```
3.  **Access the API:**
    *   API: `http://localhost:8000`
    *   API Documentation: `http://localhost:8000/docs`

### Local Development

1.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **Start PostgreSQL and Redis using Docker:**
    ```bash
    docker-compose up -d postgres redis
    ```
3.  **Run the API:**
    ```bash
    uvicorn main:app --reload
    ```

## Development Conventions

*   **Coding Style:** The project follows the PEP 8 style guide.
*   **Type Hinting:** All functions are expected to have type hints.
*   **Testing:** New features should be accompanied by tests. The testing framework used is `pytest`.
*   **Documentation:** The API is documented using OpenAPI, and the documentation is automatically generated and available at the `/docs` endpoint.
*   **Commits:** Commit messages should be clear and descriptive.
*   **CI/CD:** A CI/CD pipeline is set up using GitHub Actions to automate testing and deployment.
