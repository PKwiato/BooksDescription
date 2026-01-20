# Lubimyczytac.pl ISBN Scraper API

A slim and efficient Python backend built with **FastAPI** that scrapes book descriptions, titles, and authors from the popular Polish book portal `lubimyczytac.pl` using an ISBN.

## 🚀 Features

- **ISBN Search**: Automatically finds book pages by ISBN-10 or ISBN-13.
- **Smart Scraper**: Hand-tuned selectors and fallbacks to ensure high accuracy.
- **Clean Output**: Automatically removes UI artifacts like "read more" buttons and extra whitespace.
- **Async Implementation**: Built with `httpx` and `BeautifulSoup4` for high performance.
- **Interactive UI**: Includes automatic Swagger/OpenAPI documentation.

## 🛠️ How It Works

1. **Search**: The API takes an ISBN and performs a search on `lubimyczytac.pl`.
2. **Redirect Detection**: If the search results in a direct hit, the scraper follows the redirect to the book page.
3. **Extraction**: It parses the HTML to extract the book's title, author, and description.
4. **Cleanup**: Polish UI elements like "Rozwiń opis" are stripped to provide a clean JSON response.

## 📦 Installation

### Prerequisites
- Python 3.9 or higher

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/BooksDescription.git
   cd BooksDescription
   ```

2. **Set up a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Usage

### Running the App
Start the server using the following command:
```bash
python3 main.py
```
The API will be available at `http://localhost:8000`.

### API Example
**Endpoint**: `GET /book/{isbn}`

**Example Request**:
```bash
curl http://localhost:8000/book/9788324063255
```

**Example Response**:
```json
{
  "title": "Odyseja kosmiczna 2010",
  "author": "Arthur C. Clarke",
  "description": "Dziewięć lat po katastrofalnej misji Discovery...",
  "url": "https://lubimyczytac.pl/ksiazka/5051954/odyseja-kosmiczna-2010",
  "isbn": "9788324063255"
}
```

## 🛠️ Deployment

### Deploying to GitHub / Production
This project is structured for easy deployment:

- **Environment Variables**: Use the `PORT` variable to specify the listening port.
  ```bash
  PORT=8001 python3 main.py
  ```
- **Docker**: You can easily containerize this by creating a simple `Dockerfile` based on `python:3.9-slim`.
- **CI/CD**: The codebase is clean and modular, making it easy to integrate with GitHub Actions for automated testing.

## 🌟 Use Cases

- **Library Management**: Enrich book databases with detailed descriptions using ISBNs.
- **Book Apps**: Integrate a reliable source of book information for mobile or web applications.
- **E-commerce**: Automatically populate product descriptions for online bookstores.
- **Data Science**: Gather datasets of Polish book summaries for NLP projects.

## 📄 License
This project is open-source and free to use.

---
*Developed with ❤️ by Antigravity*
