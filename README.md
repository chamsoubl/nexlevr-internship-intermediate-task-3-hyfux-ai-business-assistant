# Nexlevr Internship – Intermediate Task 3: Connect an AI to Business Data

**Organization:** [Nexlevr](https://github.com/Nexlevr)  
**Internship Track:** Intermediate  
**Task:** 3 of 3 – Connect an AI to Business Data  
**Project:** HYFUX MIXBAR AI Business Assistant  
**Developer:** Chems Eddine Blada  
**Business:** HYFUX MIXBAR  
**Website:** https://hyfux-mixbar.vercel.app

---

## 1. Project Overview

This project connects an AI assistant to real business data using a REST API and AI function calling.

The assistant is designed for **HYFUX MIXBAR**, a non-alcoholic drinks business serving university accommodation students in Algeria.

Instead of relying on manually written or invented information, the AI retrieves actual business information through API endpoints before answering customer questions.

The project uses:

- **Python** for the application logic.
- **FastAPI** to build the business data API.
- **Groq** to provide AI inference.
- **Function Calling** to allow the AI to request business information.
- **JSON** to store the exported business data.
- **HTTPX** to communicate with the API.

## 2. Project Objectives

The main objectives of this task are to:

- Connect an AI assistant to real business data.
- Expose business information through a FastAPI REST API.
- Implement AI function calling to retrieve relevant information.
- Allow customers to search products and check prices.
- Filter products by category and maximum price.
- Ensure the AI does not invent products, prices, or availability.

## 3. Architecture

The application follows this workflow:

1. Business data is exported from Supabase.
2. The exported product data is converted into JSON.
3. FastAPI exposes endpoints to retrieve and filter the data.
4. The AI receives customer questions.
5. Groq determines which function should be called.
6. The function communicates with FastAPI using HTTPX.
7. FastAPI returns the requested business information.
8. The AI uses the retrieved information to generate its response.

```text
          Customer
              |
              v
       AI Assistant
          (Groq)
              |
              v
      Function Calling
              |
              v
        HTTPX Client
              |
              v
        FastAPI API
              |
              v
         menu.json
              |
              v
       Business Data
```

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | REST API development |
| Groq | AI inference provider |
| OpenAI Python SDK | Groq-compatible API client |
| HTTPX | HTTP requests |
| JSON | Business data storage |
| python-dotenv | Environment variable management |
| Uvicorn | ASGI server |

## 5. Project Structure

```text
hyfux-ai-business-assistant/
│
├── data/
│   └── menu.json
│
├── src/
│   ├── main.py
│   └── ai_assistant.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 6. Business Data

The project uses real product data exported from the HYFUX MIXBAR Supabase database.

The JSON dataset contains **20 products**.

Each product includes information such as:

- Product ID
- Product name
- Description
- Price
- Image URL
- Category
- Availability status
- Sold-out status
- Orderability status

### Availability Logic

A product is considered orderable only when:

```python
is_orderable = available and not sold_out
```

The dataset was verified:

| Status | Result |
|---|---:|
| Total products | 20 |
| Orderable products | 13 |
| Not orderable products | 7 |
| Availability inconsistencies | 0 |

Internal business cost information is not exposed through the customer-facing dataset.

## 7. FastAPI Endpoints

The API provides the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/health` | Health check |
| GET | `/menu` | Retrieve the complete menu |
| GET | `/products` | Retrieve products with optional filters |
| GET | `/products/search?q=latte` | Search products by name |
| GET | `/products/{product_id}` | Retrieve a specific product |
| GET | `/categories` | Retrieve available categories |

### Product Filtering

The `/products` endpoint supports:

- Filtering by category.
- Filtering by maximum price.
- Returning only orderable products.

Example:

```text
GET /products?category=Coffee&orderable_only=true
```

Example:

```text
GET /products?max_price=200&orderable_only=true
```

### API Documentation

FastAPI automatically generates interactive API documentation.

After starting the server, visit:

```text
http://127.0.0.1:8000/docs
```

## 8. AI Function Calling

The AI assistant uses function calling to retrieve information from the business API.

Three functions are implemented:

### `search_products`

Searches products by name or keyword.

### `get_products`

Retrieves products with optional category, maximum-price, and availability filters.

### `get_categories`

Retrieves the product categories available in the business dataset.

The AI selects the appropriate function based on the customer's question, receives the API response, and uses that information to formulate an answer.

### AI Accuracy Rules

The assistant is instructed to:

- Use real business data when answering business-related questions.
- Never invent products or prices.
- Never claim an unavailable product is orderable.
- State prices in Algerian dinars (DZD).
- Clearly indicate when requested information is unavailable.

## 9. Installation and Setup

### Prerequisites

- Python 3.10 or newer.
- A Groq API key.
- Git (optional, for repository management).

### Step 1: Clone the Repository

```bash
git clone https://github.com/chamsoubl/nexlevr-internship-intermediate-task-3-hyfux-ai-business-assistant.git
cd nexlevr-internship-intermediate-task-3-hyfux-ai-business-assistant
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get an API key from:

https://console.groq.com/keys

Never commit your actual `.env` file or API key to GitHub.

## 10. Running the Application

The project uses two processes.

### Terminal 1 – Start the FastAPI Server

From the project root:

```bash
uvicorn src.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### Terminal 2 – Start the AI Assistant

Keep the API server running, open another terminal, activate the virtual environment, and run:

```bash
python -m src.ai_assistant
```

The assistant will start in interactive mode.

Enter a customer question to receive an AI-generated response.

Type `exit` to stop the assistant.

## 11. Testing

The assistant was tested with the following customer questions:

| Test Question | Expected Function |
|---|---|
| What drinks do you have? | `get_products` |
| Show me all drinks under 200 DZD. | `get_products` |
| Do you have a latte? | `search_products` |
| What categories are available? | `get_categories` |
| Which products can I order right now? | `get_products` |

All five test scenarios were successfully executed.

The API was also tested through FastAPI's interactive documentation.

### Data Validation

A separate verification checked all 20 products to ensure that:

```python
is_orderable == (available and not sold_out)
```

Result: **20 correct, 0 inconsistent.**

## 12. Security and Configuration

- API keys are stored in environment variables.
- `.env` is excluded from Git tracking.
- `.env.example` provides a configuration template.
- Customer-facing business data excludes internal cost information.

## 13. Conclusion

This project demonstrates how an AI assistant can interact with real business data through a REST API and function calling.

By combining FastAPI, Groq, and structured JSON data, HYFUX MIXBAR can provide customers with accurate information about its products, prices, categories, and availability.

The implementation fulfills the main objectives of **Nexlevr Intermediate Internship – Task 3: Connect an AI to Business Data**.

---

**Developed as part of the Nexlevr Intermediate Internship Program.**