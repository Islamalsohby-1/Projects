XSS Scanner
Description
A Python script to detect Cross-Site Scripting (XSS) vulnerabilities in web pages by parsing forms and injecting payloads.
Requirements

Python 3.8+
Install dependencies: pip install -r requirements.txt

Usage

Ensure sample_urls.txt contains target URLs (one per line).
Run the script: python xss_scanner.py
Check vulnerabilities.txt for results.

Notes

Uses requests and BeautifulSoup for web scraping and form submission.
Tests common XSS payloads.
Logs vulnerable URLs, input fields, payloads, and response details.
Simulates scans for inaccessible sites; use test sites for real results.
