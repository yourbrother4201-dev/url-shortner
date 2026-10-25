# URL Shortener

A URL Shortener built with Python and FastAPI that converts long URLs into short, easy-to-share links. It stores URL mappings in SQLite, redirects users to the original destination, handles short-code collisions, and uses popularity-based in-memory caching to improve redirect performance.

## Features

- **Create Short URLs:** Convert long URLs into short links.
- **URL Redirection:** Redirect users to the original URL using HTTP 302.
- **Short-Code Generation:** Generate random, seven-character alphanumeric codes.
- **Collision Handling:** Check for duplicate codes using a database unique constraint and retry when a collision occurs.
- **SQLite Database:** Store short codes and original URLs persistently.
- **Popularity-Based Caching:** Cache frequently accessed links for five minutes.
- **API Documentation:** Explore and test endpoints through FastAPI's Swagger UI.
- **Error Handling:** Return HTTP 404 when a short code does not exist.

## Tech Stack

- **Language:** Python
- **Backend Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **Database:** SQLite
- **Caching:** In-memory Python dictionary
- **Validation:** Pydantic

## Project Structure

```text
url-shortener/
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
├── urls.db          # Created automatically
└── .venv/           # Virtual environment
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd url-shortener
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Start the application

```bash
python -m uvicorn main:app --reload
```

The server will run at:

`http://127.0.0.1:8000`

## API Endpoints

### 1. Create a Short URL

**Endpoint:** `POST /api/urls`

Creates a short URL for a valid HTTP or HTTPS destination.

**Request Body:**

```json
{
  "long_url": "https://www.python.org/"
}
```

**Example Response — 201 Created:**

```json
{
  "short_code": "aB32xY7",
  "short_url": "http://127.0.0.1:8000/aB32xY7",
  "long_url": "https://www.python.org/"
}
```

The short code and short URL shown above are illustrative. Actual values are generated when the endpoint is called.

### 2. Redirect to the Original URL

**Endpoint:** `GET /{short_code}`

Redirects the browser to the original URL associated with the supplied short code.

**Example:**

```http
GET /aB32xY7
```

**Successful response:** `302 Found`, with a `Location` header containing the original URL.

**Error response:** `404 Not Found` if the short code does not exist.

## Short-Code Generation and Collision Handling

The application generates random seven-character codes using uppercase letters, lowercase letters, and digits.

When generating a code:

1. Generate a random code.
2. Attempt to insert it into the SQLite database.
3. If the unique constraint detects a collision, generate another code.
4. Retry up to ten times.
5. Return an error if a unique code cannot be generated.

The database's unique constraint ensures that two records cannot use the same short code.

## Database Schema

The application creates a SQLite table named `urls` automatically.

| Column | Description |
|---|---|
| `id` | Auto-incrementing primary key |
| `short_code` | Unique identifier for the short URL |
| `long_url` | Original destination URL |
| `created_at` | Record creation timestamp |

## Caching Strategy

The application uses an in-memory dictionary to cache popular URLs.

- Each short code has an access counter.
- A link becomes eligible for caching after three requests.
- Cached URLs remain available for five minutes.
- Cache hits avoid repeated SQLite lookups.
- Expired entries are removed when accessed.

**Limitation:** The cache and access counters are stored in application memory. They are lost when the application restarts and are not shared between multiple server workers. Redis could be introduced for a scalable, shared cache in a production deployment.

## Testing the API

After starting the server, open:

`http://127.0.0.1:8000/docs`

Use the interactive Swagger documentation to:

1. Create a short URL using `POST /api/urls`.
2. Copy the generated short URL.
3. Open it in a browser and verify the redirect.
4. Test an unknown short code and verify the `404` response.

## Future Improvements

- Integrate Redis for shared caching.
- Add URL expiration and deletion.
- Add click analytics.
- Add custom short codes.
- Introduce user accounts and link management.
- Deploy the application to a hosting platform.

## License

This project is developed for learning and educational purposes. Add a license file if you intend to distribute it under a specific open-source license.
