from playwright.sync_api import sync_playwright

def log_request(request):
    # Filter for common API data formats
    if request.resource_type in ["fetch", "xhr"]:
        print(f"API Call Detected: {request.url}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Listen for network requests
    page.on("request", log_request)
    
    page.goto("https://byucougars.com/sports/football/roster")
    page.wait_for_load_state("networkidle")
    browser.close()
