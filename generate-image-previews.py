from playwright.sync_api import sync_playwright
from pathlib import Path
from bs4 import BeautifulSoup
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def analyze_html_files(directory: Path) -> List[Tuple[Path, str]]:
    """Return (html_path, image_filename) for files missing og/twitter images."""
    missing_images = []
    
    for html_file in directory.glob('*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            has_og = soup.find('meta', property='og:image') is not None
            has_twitter = soup.find('meta', attrs={'name': 'twitter:image'}) is not None
            
            if not (has_og and has_twitter):
                image_name = f"{html_file.stem}.png"
                missing_images.append((html_file, image_name))
                logging.info(f"Missing images: {html_file.name}")
        
        except Exception as e:
            logging.error(f"Error parsing {html_file.name}: {e}")
    
    return missing_images

def generate_screenshots(files_to_process: List[Tuple[Path, str]], images_dir: Path):
    """Generate screenshots for HTML files."""
    images_dir.mkdir(exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1200, 'height': 630})
        page.set_extra_http_headers({'User-Agent': 'Mozilla/5.0 (compatible; PreviewBot/1.0)'})
        
        for html_path, image_name in files_to_process:
            try:
                page.goto(f'file://{html_path.absolute()}', wait_until='networkidle')
                
                # Hide common overlays that might interfere
                page.evaluate("""
                    ['cookie-banner', 'cookie-notice', 'gdpr-banner'].forEach(cls => {
                        document.querySelectorAll(`.${cls}`).forEach(el => el.style.display = 'none');
                    });
                """)
                
                image_path = images_dir / image_name
                page.screenshot(path=image_path, type='png')  # Removed quality parameter
                logging.info(f"Generated: {image_name}")
                
            except Exception as e:
                logging.error(f"Screenshot failed for {html_path.name}: {e}")
        
        browser.close()

def update_html_files(files_to_process: List[Tuple[Path, str]]):
    """Add og:image and twitter:image meta tags to HTML files."""
    for html_path, image_name in files_to_process:
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Ensure head exists
            if not soup.head:
                if soup.html:
                    soup.html.insert(0, soup.new_tag('head'))
                else:
                    logging.warning(f"No html tag in {html_path.name}, skipping")
                    continue
            
            image_url = f"images/{image_name}"
            
            # Add og:image if missing
            if not soup.find('meta', property='og:image'):
                og_tag = soup.new_tag('meta', property='og:image', content=image_url)
                soup.head.append(og_tag)
            
            # Add twitter:image if missing
            if not soup.find('meta', attrs={'name': 'twitter:image'}):
                twitter_tag = soup.new_tag('meta', attrs={'name': 'twitter:image', 'content': image_url})
                soup.head.append(twitter_tag)
            
            # Write back with minimal formatting changes
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            logging.info(f"Updated: {html_path.name}")
            
        except Exception as e:
            logging.error(f"Update failed for {html_path.name}: {e}")

def process_directory(directory: str = '.'):
    """Main pipeline: analyze, screenshot, update."""
    dir_path = Path(directory).resolve()
    images_dir = dir_path / 'images'
    
    logging.info(f"Processing directory: {dir_path}")
    
    files_to_process = analyze_html_files(dir_path)
    
    if not files_to_process:
        logging.info("No files need processing")
        return
    
    logging.info(f"Found {len(files_to_process)} files to process")
    
    generate_screenshots(files_to_process, images_dir)
    update_html_files(files_to_process)
    
    logging.info("Processing complete")

if __name__ == "__main__":
    process_directory()