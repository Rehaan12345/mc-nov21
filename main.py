from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import io
import re
import PyPDF2
from nltk.tokenize import sent_tokenize

app = FastAPI()

PDF_PAGE_URL = "https://mayor.lacity.gov/ExecutiveDirectives"


def extract_pdf_links(page_url):
    """Scrape all PDF URLs from the Executive Directives page."""
    resp = requests.get(page_url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            # Convert to absolute URL if needed
            href = requests.compat.urljoin(page_url, href)
            links.append(href)

    return links


def extract_pdf_text_pypdf2(pdf_url):
    """Download the PDF and extract text using PyPDF2."""
    resp = requests.get(pdf_url)
    resp.raise_for_status()

    pdf_bytes = io.BytesIO(resp.content)

    try:
        reader = PyPDF2.PdfReader(pdf_bytes)
    except Exception:
        return ""

    text = []
    for page in reader.pages:
        try:
            text.append(page.extract_text() or "")
        except:
            pass

    return "\n".join(text)


def simple_summary(text, max_sentences=3):
    """Basic summary: first N sentences."""
    sentences = sent_tokenize(text)
    return " ".join(sentences[:max_sentences]).strip()


def extract_dates(text):
    """Find common English + numerical dates."""
    date_re = (
        r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?)[ ]\d{1,2},[ ]\d{4}\b"
        r"|\b\d{1,2}/\d{1,2}/\d{4}\b"
        r"|\b\d{4}-\d{2}-\d{2}\b"
    )
    return list(set(re.findall(date_re, text)))


def extract_addresses(text):
    """Very naive address matcher for LA addresses."""
    addr_re = (
        r"\d{1,5}\s+[A-Za-z0-9\.]+\s+"
        r"(?:Street|St\.|Avenue|Ave\.|Boulevard|Blvd\.|Road|Rd\.)"
        r"\s*,?\s*Los Angeles, CA\s*\d{5}"
    )
    return list(set(re.findall(addr_re, text)))


@app.get("/directives")
async def get_directives():
    try:
        pdf_links = extract_pdf_links(PDF_PAGE_URL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load page: {e}")

    results = []

    for url in pdf_links:
        try:
            text = extract_pdf_text_pypdf2(url)
        except Exception:
            continue

        summary = simple_summary(text)
        dates = extract_dates(text)
        addresses = extract_addresses(text)

        results.append({
            "url": url,
            "summary": summary,
            "dates": dates,
            "addresses": addresses
        })

    return JSONResponse(content={"directives": results})
