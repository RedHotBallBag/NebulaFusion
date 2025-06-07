from playwright.sync_api import sync_playwright


def get_page_title(url: str) -> str:
    """Return the title of the given URL using a headless browser."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        title = page.title()
        browser.close()
        return title


def demo() -> None:
    """Simple demonstration fetching the title of example.com."""
    title = get_page_title("https://example.com")
    print(f"Fetched page title: {title}")


if __name__ == "__main__":
    demo()
