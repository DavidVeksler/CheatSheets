import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Error as PlaywrightError

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Constants for Meta Tags ---
OG_TYPE_DEFAULT = "website"
TWITTER_CARD_DEFAULT = "summary_large_image"
DEFAULT_DESCRIPTION_PLACEHOLDER = "Read more about {} on our site."

# --- Helper Functions for HTML Manipulation ---

def _ensure_head_exists(soup: BeautifulSoup, html_path: Path) -> Optional[BeautifulSoup]:
    """Ensures a <head> tag exists in the soup, creating it if necessary. Returns head tag or None."""
    if not soup.head:
        if soup.html:
            head_tag = soup.new_tag("head")
            soup.html.insert(0, head_tag)
            logging.debug(f"Created <head> for {html_path.name}")
            return head_tag
        else:
            logging.warning(
                f"No <html> tag in {html_path.name}, cannot create <head>. Skipping meta tag additions for this file."
            )
            return None
    return soup.head

def _get_or_create_meta_tag(
    soup: BeautifulSoup,
    head: BeautifulSoup,
    attributes: Dict[str, str],
    content_value: Optional[str] = None,
) -> Tuple[BeautifulSoup, bool]:
    """
    Finds a meta tag with given attributes or creates it if not found.
    Updates content if content_value is provided, tag exists, and content differs.
    Returns the tag and a boolean indicating if a change was made (created or content updated).
    """
    tag = head.find("meta", attrs=attributes)
    changed = False
    if not tag:
        tag = soup.new_tag("meta", attrs=attributes)
        if content_value is not None:
            tag["content"] = content_value
        head.append(tag)
        changed = True
    elif content_value is not None and tag.get("content") != content_value:
        tag["content"] = content_value
        changed = True
    return tag, changed

def _get_or_create_link_tag(
    soup: BeautifulSoup,
    head: BeautifulSoup,
    attributes: Dict[str, str],
    href_value: Optional[str] = None,
) -> Tuple[BeautifulSoup, bool]:
    """
    Finds a link tag with given attributes or creates it if not found.
    Updates href if href_value is provided, tag exists, and href differs.
    Returns the tag and a boolean indicating if a change was made.
    """
    tag = head.find("link", attrs=attributes)
    changed = False
    if not tag:
        tag = soup.new_tag("link", attrs=attributes)
        if href_value is not None:
            tag["href"] = href_value
        insert_position = 0
        for i, child in enumerate(list(head.children)):
            if hasattr(child, 'name') and child.name == 'meta':
                if child.get('charset') or child.get('name') == 'viewport':
                    insert_position = i + 1
        
        if not head.contents: 
            head.append(tag)
        elif insert_position < len(head.contents):
            head.insert(insert_position, tag)
        else:
            head.append(tag)
        changed = True
    elif href_value is not None and tag.get("href") != href_value:
        tag["href"] = href_value
        changed = True
    return tag, changed


def _extract_content(soup: BeautifulSoup, tag_name: str = "h1", default_text: str = "") -> str:
    """Extracts text content from the first occurrence of a specified tag."""
    element = soup.find(tag_name)
    if element:
        text_content = element.get_text(separator=' ', strip=True)
        if text_content:
            return text_content
    return default_text

# --- Core Logic Functions ---

def analyze_html_file(
    html_file: Path, base_url: str, http_base_url_netloc: str
) -> Dict[str, Any]:
    """
    Analyzes a single HTML file for missing/incorrect SEO and social media meta tags.
    Returns a dictionary with analysis results, including found tag objects.
    """
    analysis: Dict[str, Any] = {"path": html_file, "needs_update": False}
    file_stem = html_file.stem
    expected_image_name = f"{file_stem}.png"
    expected_canonical_url = f"{base_url}{html_file.name}"

    try:
        with open(html_file, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            if not content.strip():
                logging.warning(f"File {html_file.name} is empty or whitespace only. Skipping analysis.")
                analysis["error"] = "Empty file"
                return analysis
            soup = BeautifulSoup(content, "html.parser")

        analysis["soup"] = soup # Store soup for use in update function if needed for extraction

        # --- Find existing tags ---
        analysis["og_image_tag"] = soup.find("meta", property="og:image")
        analysis["twitter_image_tag"] = soup.find("meta", attrs={"name": "twitter:image"})
        analysis["og_title_tag"] = soup.find("meta", property="og:title")
        analysis["twitter_title_tag"] = soup.find("meta", attrs={"name": "twitter:title"})
        analysis["og_description_tag"] = soup.find("meta", property="og:description")
        analysis["twitter_description_tag"] = soup.find("meta", attrs={"name": "twitter:description"})
        analysis["meta_description_tag"] = soup.find("meta", attrs={"name": "description"})
        analysis["og_type_tag"] = soup.find("meta", property="og:type")
        analysis["og_url_tag"] = soup.find("meta", property="og:url")
        analysis["twitter_card_tag"] = soup.find("meta", attrs={"name": "twitter:card"})
        analysis["canonical_link_tag"] = soup.find("link", rel="canonical")

        # --- Determine if updates are needed ---

        # 1. Social Media Images (Add if missing)
        if not analysis["og_image_tag"] or not analysis["twitter_image_tag"]:
            analysis["expected_image_name"] = expected_image_name
            analysis["needs_screenshot"] = True # Screenshot needed if either is missing
            analysis["needs_update"] = True
            if not analysis["og_image_tag"]: analysis["og_image_missing"] = True
            if not analysis["twitter_image_tag"]: analysis["twitter_image_missing"] = True
            logging.info(f"Identified missing social image tags for: {html_file.name}")

        # 2. Title Tags (Add if missing)
        if not analysis["og_title_tag"]:
            analysis["og_title_missing"] = True
            analysis["needs_update"] = True
        if not analysis["twitter_title_tag"]:
            analysis["twitter_title_missing"] = True
            analysis["needs_update"] = True
        
        # 3. Description Tags (Add if missing)
        if not analysis["og_description_tag"]:
            analysis["og_description_missing"] = True
            analysis["needs_update"] = True
        if not analysis["twitter_description_tag"]:
            analysis["twitter_description_missing"] = True
            analysis["needs_update"] = True
        if not analysis["meta_description_tag"]:
            analysis["meta_description_missing"] = True
            analysis["needs_update"] = True

        # 4. Other Social Tags (Add if missing, or update content if present and incorrect)
        if not analysis["og_type_tag"] or analysis["og_type_tag"].get("content") != OG_TYPE_DEFAULT:
            analysis["og_type_needs_update"] = True
            analysis["needs_update"] = True
        if not analysis["og_url_tag"] or analysis["og_url_tag"].get("content") != expected_canonical_url:
            analysis["og_url_needs_update"] = True
            analysis["needs_update"] = True
        if not analysis["twitter_card_tag"] or analysis["twitter_card_tag"].get("content") != TWITTER_CARD_DEFAULT:
            analysis["twitter_card_needs_update"] = True
            analysis["needs_update"] = True
            
        # 5. Canonical URL (Add if missing, or update href if present and incorrect)
        current_canonical_href = analysis["canonical_link_tag"].get("href", "") if analysis["canonical_link_tag"] else ""
        needs_canonical_fix = False
        if not analysis["canonical_link_tag"]:
            needs_canonical_fix = True
            logging.info(f"Missing canonical URL: {html_file.name}")
        else:
            parsed_current_href = urlparse(current_canonical_href)
            is_http_on_base_domain = (parsed_current_href.scheme == "http" and 
                                      parsed_current_href.netloc.lower() == http_base_url_netloc.lower())
            is_different_url = (current_canonical_href != expected_canonical_url)
            if is_http_on_base_domain or is_different_url:
                needs_canonical_fix = True
                logging.info(
                    f"Incorrect canonical URL: {html_file.name} (Current: '{current_canonical_href}', Expected: '{expected_canonical_url}')"
                )
        if needs_canonical_fix:
            analysis["canonical_needs_fix"] = True
            analysis["expected_canonical_url"] = expected_canonical_url
            analysis["needs_update"] = True

    except IOError as e:
        logging.error(f"IOError parsing {html_file.name}: {e}")
        analysis["error"] = str(e)
    except Exception as e: 
        logging.error(f"Unexpected error parsing {html_file.name} ({type(e).__name__}): {e}")
        analysis["error"] = str(e)
        if "soup" in analysis: del analysis["soup"] # Don't pass potentially corrupt soup
        
    return analysis

def generate_screenshots(
    files_for_screenshot: List[Dict[str, Any]], images_dir: Path
):
    """Generate screenshots for HTML files that need them."""
    if not files_for_screenshot:
        logging.info("No screenshots needed.")
        return

    images_dir.mkdir(exist_ok=True)
    logging.info(f"Attempting to launch browser for {len(files_for_screenshot)} screenshots...")

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except PlaywrightError as e:
                logging.error(f"Failed to launch Chromium. Ensure Playwright browsers are installed ('playwright install chromium'). Error: {e}")
                return 

            page = browser.new_page(viewport={"width": 1200, "height": 630})
            page.set_extra_http_headers(
                {"User-Agent": "Mozilla/5.0 (compatible; PreviewBot/1.0; +https://cheatsheets.davidveksler.com/)"}
            )

            for file_info in files_for_screenshot:
                html_path = file_info["path"]
                # Ensure expected_image_name is present; could happen if only one image tag was missing initially
                image_name = file_info.get("expected_image_name", f"{html_path.stem}.png") 
                image_path = images_dir / image_name
                try:
                    page.goto(f"file://{html_path.resolve()}", wait_until="networkidle")
                    page.evaluate(
                        """
                        ['cookie-banner', 'cookie-notice', 'gdpr-banner', 'privacy-popup'].forEach(cls => {
                            document.querySelectorAll(`.${cls}`).forEach(el => el.style.display = 'none');
                        });
                    """
                    )
                    page.screenshot(path=image_path, type="png")
                    logging.info(f"Generated screenshot: {image_path.name}")
                except PlaywrightError as e:
                    logging.error(
                        f"Playwright screenshot failed for {html_path.name}: {e}"
                    )
                except Exception as e: 
                    logging.error(
                        f"Unexpected error during screenshot for {html_path.name} ({type(e).__name__}): {e}"
                    )
            browser.close()
    except PlaywrightError as e: 
        logging.error(f"Playwright context error: {e}. Screenshots may not have been generated.")
    except Exception as e:
        logging.error(f"General error in screenshot generation ({type(e).__name__}): {e}")


def update_html_file_meta(file_analysis: Dict[str, Any], base_url: str):
    """Updates a single HTML file based on its analysis results."""
    html_path = file_analysis["path"]
    
    # Retrieve the soup object from analysis if it's clean, otherwise re-read
    soup = file_analysis.get("soup")
    if not soup: # If soup wasn't stored or an error occurred during analysis parsing
        try:
            with open(html_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                if not content.strip(): # Should have been caught by analysis, but double check
                    logging.warning(f"Skipping update for empty file: {html_path.name}")
                    return
                soup = BeautifulSoup(content, "html.parser")
        except IOError as e:
            logging.error(f"IOError re-reading {html_path.name} for update: {e}")
            return
        except Exception as e:
            logging.error(f"Unexpected error re-reading {html_path.name} for update ({type(e).__name__}): {e}")
            return


    head = _ensure_head_exists(soup, html_path)
    if not head: 
        return

    total_changes_made_to_file = False
    file_stem = html_path.stem
    expected_canonical_url = file_analysis.get("expected_canonical_url", f"{base_url}{html_path.name}")

    # --- Default Content Derivation ---
    # (Do this once, used if tags are missing)
    default_title_text = _extract_content(soup, "h1", default_text=file_stem.replace('-', ' ').title())
    default_description_text = DEFAULT_DESCRIPTION_PLACEHOLDER.format(file_stem.replace('-', ' '))


    # --- Social Media Image Tags (Add if missing) ---
    if file_analysis.get("og_image_missing") or file_analysis.get("twitter_image_missing"):
        image_name_for_meta = file_analysis.get("expected_image_name", f"{file_stem}.png")
        image_url_for_meta = f"images/{image_name_for_meta}"
        if file_analysis.get("og_image_missing"):
            _, changed = _get_or_create_meta_tag(soup, head, {"property": "og:image"}, image_url_for_meta)
            if changed: total_changes_made_to_file = True
        if file_analysis.get("twitter_image_missing"):
            _, changed = _get_or_create_meta_tag(soup, head, {"name": "twitter:image"}, image_url_for_meta)
            if changed: total_changes_made_to_file = True
    
    # --- Title Tags (Add if missing, preserve content if exists) ---
    if file_analysis.get("og_title_missing"):
        _, changed = _get_or_create_meta_tag(soup, head, {"property": "og:title"}, default_title_text)
        if changed: total_changes_made_to_file = True
    if file_analysis.get("twitter_title_missing"):
        _, changed = _get_or_create_meta_tag(soup, head, {"name": "twitter:title"}, default_title_text)
        if changed: total_changes_made_to_file = True

    # --- Description Tags (Add if missing, preserve content if exists) ---
    if file_analysis.get("og_description_missing"):
        _, changed = _get_or_create_meta_tag(soup, head, {"property": "og:description"}, default_description_text)
        if changed: total_changes_made_to_file = True
    if file_analysis.get("twitter_description_missing"):
        _, changed = _get_or_create_meta_tag(soup, head, {"name": "twitter:description"}, default_description_text)
        if changed: total_changes_made_to_file = True
    if file_analysis.get("meta_description_missing"): # Standard meta description
        _, changed = _get_or_create_meta_tag(soup, head, {"name": "description"}, default_description_text)
        if changed: total_changes_made_to_file = True
        
    # --- Other Social Tags (Add if missing, or update content if present and incorrect) ---
    if file_analysis.get("og_type_needs_update"):
        _, changed = _get_or_create_meta_tag(soup, head, {"property": "og:type"}, OG_TYPE_DEFAULT)
        if changed: total_changes_made_to_file = True
    if file_analysis.get("og_url_needs_update"):
         _, changed = _get_or_create_meta_tag(soup, head, {"property": "og:url"}, expected_canonical_url)
         if changed: total_changes_made_to_file = True
    if file_analysis.get("twitter_card_needs_update"):
        _, changed = _get_or_create_meta_tag(soup, head, {"name": "twitter:card"}, TWITTER_CARD_DEFAULT)
        if changed: total_changes_made_to_file = True

    # --- Canonical URL (Add if missing, or update href if present and incorrect) ---
    if file_analysis.get("canonical_needs_fix"):
        _, changed = _get_or_create_link_tag(soup, head, {"rel": "canonical"}, expected_canonical_url)
        if changed: 
            total_changes_made_to_file = True
            logging.info(f"Updated canonical URL in {html_path.name} to: {expected_canonical_url}")
        
    if total_changes_made_to_file:
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(str(soup)) 
            logging.info(f"Successfully updated meta tags for: {html_path.name}")
        except IOError as e:
            logging.error(f"IOError during final write of {html_path.name}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during final write of {html_path.name} ({type(e).__name__}): {e}")


def process_directory(directory: str = ".", base_url: str = "https://cheatsheets.davidveksler.com/"):
    """
    Main pipeline: Validates inputs, analyzes HTML files, generates screenshots, and updates HTML files.
    """
    dir_path = Path(directory).resolve()

    if not dir_path.exists() or not dir_path.is_dir():
        logging.error(
            f"Error: Provided directory '{directory}' does not exist or is not a directory."
        )
        return
    
    try:
        parsed_base_url = urlparse(base_url)
    except ValueError as e:
        logging.error(f"Error: Invalid base_url '{base_url}'. Could not parse. {e}")
        return

    if not (parsed_base_url.scheme in ["http", "https"] and parsed_base_url.netloc):
        logging.error(f"Error: Invalid base_url '{base_url}'. Must be a valid HTTP/HTTPS URL.")
        return
    if not base_url.endswith("/"):
        base_url += "/"
        logging.warning(f"Base URL did not end with '/', appended it: {base_url}")
        parsed_base_url = urlparse(base_url) 

    http_base_url_netloc = parsed_base_url.netloc


    images_dir = dir_path / "images"
    logging.info(f"Processing directory: {dir_path}")
    logging.info(f"Using base URL: {base_url}")

    all_html_files = list(dir_path.glob("*.html"))
    if not all_html_files:
        logging.info(f"No HTML files found in {dir_path}.")
        return

    processed_files_info: List[Dict[str, Any]] = []
    for html_file in all_html_files:
        logging.debug(f"Analyzing {html_file.name}...")
        analysis = analyze_html_file(html_file, base_url, http_base_url_netloc)
        if analysis.get("error"):
            logging.warning(f"Skipping {html_file.name} due to analysis error: {analysis['error']}")
            if "soup" in analysis: del analysis["soup"] # Don't keep potentially bad soup
            continue # Skip files with analysis errors for further processing
        
        if analysis.get("needs_update") or analysis.get("needs_screenshot"):
            processed_files_info.append(analysis)


    if not processed_files_info:
        logging.info("No files need processing after analysis.")
        return

    files_needing_screenshots = [
        res for res in processed_files_info if res.get("needs_screenshot")
    ]
    # Files that need HTML modification
    files_needing_html_updates = [
        res for res in processed_files_info if res.get("needs_update")
    ] 
    
    logging.info(f"Found {len(files_needing_screenshots)} files potentially needing screenshots.")
    logging.info(f"Found {len(files_needing_html_updates)} files needing HTML meta tag updates.")

    if files_needing_screenshots:
        generate_screenshots(files_needing_screenshots, images_dir)

    if files_needing_html_updates:
        for file_analysis in files_needing_html_updates:
            update_html_file_meta(file_analysis, base_url) 
    
    logging.info("Processing complete.")


if __name__ == "__main__":
    # To test this specific change, you might create files like:
    # test_dir = Path("test_html_preserve")
    # test_dir.mkdir(exist_ok=True)
    # (test_dir / "test_preserve.html").write_text(
    #     "<html><head><title>Original Title</title>"
    #     "<meta property='og:title' content='My Custom OG Title'>"
    #     "<meta name='twitter:title' content='My Custom Twitter Title'>"
    #     "<meta property='og:description' content='My Custom OG Desc'>"
    #     "<meta name='twitter:description' content='My Custom Twitter Desc'>"
    #     "<meta name='description' content='My Custom Meta Desc'>"
    #     # Missing og:type, og:url, twitter:card, canonical, images - these should be added/updated
    #     "</head><body><h1>Page H1 For Defaults</h1></body></html>"
    # )
    # (test_dir / "test_add_new.html").write_text(
    #    "<html><head><title>New Page</title></head><body><h1>H1 For New Page</h1></body></html>"
    # )
    # process_directory(str(test_dir), "https://example.com/docs/")
    process_directory()