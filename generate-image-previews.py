from playwright.sync_api import sync_playwright
from pathlib import Path
from bs4 import BeautifulSoup
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def analyze_html_files(directory: Path, base_url: str = "https://cheatsheets.davidveksler.com/") -> Tuple[List[Tuple[Path, str]], List[Path]]:
    """Return files missing og/twitter images and files needing canonical URL fixes."""
    missing_images = []
    needs_canonical_fix = []
    
    for html_file in directory.glob('*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Check for missing social media images
            has_og = soup.find('meta', property='og:image') is not None
            has_twitter = soup.find('meta', attrs={'name': 'twitter:image'}) is not None
            
            if not (has_og and has_twitter):
                image_name = f"{html_file.stem}.png"
                missing_images.append((html_file, image_name))
                logging.info(f"Missing images: {html_file.name}")
            
            # Check canonical URL
            canonical_link = soup.find('link', rel='canonical')
            expected_canonical = f"{base_url}{html_file.name}"
            needs_fix = False
            
            if not canonical_link:
                needs_fix = True
                logging.info(f"Missing canonical URL: {html_file.name}")
            else:
                current_href = canonical_link.get('href', '')
                # Check if needs http->https fix or incorrect URL
                if (current_href.startswith('http://cheatsheets.davidveksler.com/') or 
                    current_href != expected_canonical):
                    needs_fix = True
                    logging.info(f"Incorrect canonical URL: {html_file.name} ({current_href})")
            
            if needs_fix:
                needs_canonical_fix.append(html_file)
        
        except Exception as e:
            logging.error(f"Error parsing {html_file.name}: {e}")
    
    return missing_images, needs_canonical_fix

def generate_screenshots(files_to_process: List[Tuple[Path, str]], images_dir: Path):
    """Generate screenshots for HTML files."""
    if not files_to_process:
        return
        
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
                page.screenshot(path=image_path, type='png')
                logging.info(f"Generated: {image_name}")
                
            except Exception as e:
                logging.error(f"Screenshot failed for {html_path.name}: {e}")
        
        browser.close()

def update_html_files(files_with_missing_images: List[Tuple[Path, str]], 
                     files_needing_canonical_fix: List[Path], 
                     base_url: str = "https://cheatsheets.davidveksler.com/"):
    """Add og:image, twitter:image meta tags and fix canonical URLs."""
    
    # Process files missing social media images
    for html_path, image_name in files_with_missing_images:
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
            
            logging.info(f"Updated social media tags: {html_path.name}")
            
        except Exception as e:
            logging.error(f"Social media update failed for {html_path.name}: {e}")
    
    # Process files needing canonical URL fixes
    for html_path in files_needing_canonical_fix:
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
            
            expected_canonical = f"{base_url}{html_path.name}"
            
            # Handle canonical URL
            canonical_link = soup.find('link', rel='canonical')
            if canonical_link:
                # Fix existing canonical
                current_href = canonical_link.get('href', '')
                
                # Fix http to https
                if current_href.startswith('http://cheatsheets.davidveksler.com/'):
                    current_href = current_href.replace('http://cheatsheets.davidveksler.com/', 'https://cheatsheets.davidveksler.com/')
                
                # Update if different from expected
                if current_href != expected_canonical:
                    canonical_link['href'] = expected_canonical
                    logging.info(f"Fixed canonical URL in {html_path.name}: {expected_canonical}")
            else:
                # Add missing canonical
                canonical_tag = soup.new_tag('link', rel='canonical', href=expected_canonical)
                # Insert canonical near the top of head, after charset and viewport
                insert_position = 0
                for i, child in enumerate(soup.head.children):
                    if hasattr(child, 'name') and child.name == 'meta':
                        if child.get('charset') or child.get('name') == 'viewport':
                            insert_position = i + 1
                
                if insert_position < len(list(soup.head.children)):
                    soup.head.insert(insert_position, canonical_tag)
                else:
                    soup.head.append(canonical_tag)
                    
                logging.info(f"Added canonical URL to {html_path.name}: {expected_canonical}")
            
            # Write back with minimal formatting changes
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            logging.info(f"Updated canonical URL: {html_path.name}")
            
        except Exception as e:
            logging.error(f"Canonical URL update failed for {html_path.name}: {e}")

def process_directory(directory: str = '.', base_url: str = "https://cheatsheets.davidveksler.com/"):
    """Main pipeline: analyze, screenshot, update."""
    dir_path = Path(directory).resolve()
    images_dir = dir_path / 'images'
    
    logging.info(f"Processing directory: {dir_path}")
    
    files_with_missing_images, files_needing_canonical_fix = analyze_html_files(dir_path, base_url)
    
    if not files_with_missing_images and not files_needing_canonical_fix:
        logging.info("No files need processing")
        return
    
    logging.info(f"Found {len(files_with_missing_images)} files needing screenshots")
    logging.info(f"Found {len(files_needing_canonical_fix)} files needing canonical URL fixes")
    
    # Generate screenshots only for files missing social media images
    if files_with_missing_images:
        generate_screenshots(files_with_missing_images, images_dir)
    
    # Update HTML files (both social media tags and canonical URLs)
    update_html_files(files_with_missing_images, files_needing_canonical_fix, base_url)
    
    logging.info("Processing complete")

if __name__ == "__main__":
    process_directory()