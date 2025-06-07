import logging
import argparse
from pathlib import Path
from typing import List, Dict, Set
from urllib.parse import urlparse

# Optional dependency loading
try:
    from playwright.sync_api import sync_playwright, Error as PlaywrightError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from bs4 import BeautifulSoup, FeatureNotFound
except ImportError:
    print("Error: BeautifulSoup is not installed. Please run: python3 -m pip install beautifulsoup4")
    exit(1)

# --- Configuration & Constants ---
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
OG_TYPE_DEFAULT = "website"
TWITTER_CARD_DEFAULT = "summary_large_image"

class Colors:
    HEADER, BLUE, GREEN, YELLOW, RED, ENDC, BOLD, UNDERLINE = '\033[95m', '\033[94m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m', '\033[4m'

def get_parser():
    """Determines the best available HTML parser."""
    try:
        BeautifulSoup("<html></html>", "lxml")
        return "lxml"
    except FeatureNotFound:
        print(f"{Colors.YELLOW}Note: 'lxml' parser not found. Falling back to the built-in 'html.parser'.\nFor better performance, run: {Colors.BOLD}python3 -m pip install lxml{Colors.ENDC}")
        return "html.parser"
HTML_PARSER = get_parser()

class ChangeProposal:
    """Stores all proposed changes for files and images."""
    def __init__(self):
        self.html_additions: Dict[Path, List[Dict]] = {}
        self.html_updates: Dict[Path, List[Dict]] = {}
        self.screenshot_tasks: Set[str] = set()
        self.scanned_files = 0
        self.unparseable_files = 0

    def add_tag(self, file_path: Path, attrs: Dict, content: str, tag_name: str, content_attr: str):
        if file_path not in self.html_additions: self.html_additions[file_path] = []
        self.html_additions[file_path].append({"attrs": attrs, "content": content, "tag_name": tag_name, "content_attr": content_attr})

    def update_tag(self, file_path: Path, attrs: Dict, old_val: str, new_val: str, tag_name: str, content_attr: str):
        if file_path not in self.html_updates: self.html_updates[file_path] = []
        self.html_updates[file_path].append({"attrs": attrs, "old": old_val, "new": new_val, "tag_name": tag_name, "content_attr": content_attr})

    def add_screenshot_task(self, image_name: str): self.screenshot_tasks.add(image_name)
    def file_has_changes(self, file_path: Path) -> bool: return file_path in self.html_additions or file_path in self.html_updates
    def has_changes(self) -> bool: return bool(self.html_additions or self.html_updates or self.screenshot_tasks)

    def print_report(self):
        print(f"\n{Colors.BOLD}{Colors.HEADER}--- Meta Tag Analysis Report ---{Colors.ENDC}")
        changed_file_count = len(set(self.html_additions.keys()) | set(self.html_updates.keys()))
        perfect_files = self.scanned_files - changed_file_count - self.unparseable_files
        print(f"Scanned {self.scanned_files} files: {Colors.GREEN}{perfect_files} perfect{Colors.ENDC}, {Colors.YELLOW}{changed_file_count} with issues{Colors.ENDC}, {Colors.RED}{self.unparseable_files} unparseable.{Colors.ENDC}")

        if not self.has_changes(): return

        all_changed_files = sorted(list(set(self.html_additions.keys()) | set(self.html_updates.keys())))

        for file_path in all_changed_files:
            print(f"\n📄 {Colors.BOLD}{file_path.name}{Colors.ENDC}")
            for change in sorted(self.html_additions.get(file_path, []), key=lambda x: str(x['attrs'])):
                tag_html = f'<{change["tag_name"]} {list(change["attrs"].keys())[0]}="{list(change["attrs"].values())[0]}" {change["content_attr"]}="{change["content"]}">'
                print(f"  {Colors.GREEN}[+] ADD:    {Colors.ENDC}{tag_html}")
            for change in sorted(self.html_updates.get(file_path, []), key=lambda x: str(x['attrs'])):
                tag_html = f'<{change["tag_name"]} {list(change["attrs"].keys())[0]}="{list(change["attrs"].values())[0]}" {change["content_attr"]}="{change["new"]}">'
                print(f"  {Colors.YELLOW}[~] UPDATE: {Colors.ENDC}{tag_html}")
                print(f"            (from: {change['old']})")

        if self.screenshot_tasks:
            print(f"\n{Colors.UNDERLINE}{Colors.BLUE}Required Screenshot Generations:{Colors.ENDC}")
            for image_name in sorted(list(self.screenshot_tasks)):
                print(f"  {Colors.GREEN}[+] GENERATE: {Colors.ENDC}images/{image_name}")
        print("-" * 30)

def analyze_file(html_file: Path, base_url: str, proposal: ChangeProposal):
    proposal.scanned_files += 1
    try:
        content = html_file.read_text(encoding="utf-8")
        if not content.strip(): return
        soup = BeautifulSoup(content, HTML_PARSER)
    except Exception as e:
        logging.error(f"Could not parse {html_file.name}: {e}")
        proposal.unparseable_files += 1
        return

    head = soup.head
    if not head:
        logging.warning(f"No <head> tag in {html_file.name}. Skipping.")
        proposal.unparseable_files += 1
        return

    # --- Analysis Logic ---
    file_stem = html_file.stem
    images_dir = html_file.parent / "images"

    # Determine the correct, final image URL to use for this page
    final_image_url = f"images/{file_stem}.png"  # Default if no valid image is found
    needs_screenshot = True

    # Check for an existing, valid og:image tag
    og_image_tag = soup.find("meta", property="og:image")
    if og_image_tag and og_image_tag.get("content"):
        current_og_image_url = og_image_tag.get("content")

        if "YOUR_IMAGE_URL_HERE" not in current_og_image_url:
            try:
                # Extract filename from a potential full URL or relative path
                image_filename = Path(urlparse(current_og_image_url).path).name
                if (images_dir / image_filename).exists():
                    # A valid, existing image was found! Use it.
                    final_image_url = f"images/{image_filename}"
                    needs_screenshot = False # Don't generate a new one
            except Exception as e:
                logging.warning(f"Could not parse image path '{current_og_image_url}' in {html_file.name}: {e}")

    expected_canonical_url = f"{base_url}{html_file.name}"

    # ADD-ONLY tags (Creative Content - will not overwrite)
    if not soup.find("meta", property="og:title"):
        title = soup.find("title")
        if title and title.get_text(strip=True):
            proposal.add_tag(html_file, {"property": "og:title"}, title.get_text(strip=True), "meta", "content")

    # ADD or UPDATE tags (Technical Content)
    technical_tags = {
        "og:image": ({"property": "og:image"}, final_image_url, "meta", "content"),
        "twitter:image": ({"name": "twitter:image"}, final_image_url, "meta", "content"),
        "og:url": ({"property": "og:url"}, expected_canonical_url, "meta", "content"),
        "canonical": ({"rel": "canonical"}, expected_canonical_url, "link", "href"),
        "og:type": ({"property": "og:type"}, OG_TYPE_DEFAULT, "meta", "content"),
        "twitter:card": ({"name": "twitter:card"}, TWITTER_CARD_DEFAULT, "meta", "content"),
    }
    for _, (attrs, expected_content, tag_name, content_attr) in technical_tags.items():
        tag = soup.find(tag_name, attrs=attrs)
        if not tag:
            proposal.add_tag(html_file, attrs, expected_content, tag_name, content_attr)
        elif tag.get(content_attr) != expected_content:
            proposal.update_tag(html_file, attrs, tag.get(content_attr, "N/A"), expected_content, tag_name, content_attr)

    # Add a screenshot task ONLY if we couldn't find a valid existing image
    # AND the standardized target image doesn't exist either.
    expected_image_path = images_dir / f"{file_stem}.png"
    if needs_screenshot and not expected_image_path.exists():
        proposal.add_screenshot_task(f"{file_stem}.png")

def apply_changes(proposal: ChangeProposal, images_dir: Path):
    if proposal.html_additions or proposal.html_updates:
        print(f"\n{Colors.BLUE}Applying HTML changes...{Colors.ENDC}")
        all_changed_files = sorted(list(set(proposal.html_additions.keys()) | set(proposal.html_updates.keys())))
        for file_path in all_changed_files:
            try:
                soup = BeautifulSoup(file_path.read_text(encoding="utf-8"), HTML_PARSER)
                head = soup.head
                if not head: continue

                updates_for_file = proposal.html_updates.get(file_path, [])
                for update in updates_for_file:
                    old_tag = soup.find(update['tag_name'], attrs=update['attrs'])
                    if old_tag: old_tag.decompose()

                all_tags_to_add = proposal.html_additions.get(file_path, []) + updates_for_file
                for change in all_tags_to_add:
                    new_tag = soup.new_tag(change['tag_name'], attrs=change['attrs'])
                    new_tag[change['content_attr']] = change.get('new', change.get('content'))
                    head.append(new_tag)

                file_path.write_text(str(soup.prettify()), encoding="utf-8")
                print(f"  {Colors.GREEN}Updated:{Colors.ENDC} {file_path.name}")
            except Exception as e:
                print(f"{Colors.RED}Error updating {file_path.name}: {e}{Colors.ENDC}")

    if proposal.screenshot_tasks:
        generate_screenshots(list(proposal.screenshot_tasks), images_dir)

def generate_screenshots(image_names: List[str], images_dir: Path):
    if not PLAYWRIGHT_AVAILABLE:
        print(f"{Colors.RED}\nPlaywright is not installed. Cannot generate screenshots.{Colors.ENDC}")
        print(f"{Colors.YELLOW}To enable, run: {Colors.BOLD}python3 -m pip install playwright && python3 -m playwright install{Colors.ENDC}")
        return

    images_dir.mkdir(exist_ok=True)
    print(f"\n{Colors.BLUE}Generating {len(image_names)} screenshots...{Colors.ENDC}")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1200, "height": 630})
            for image_name in sorted(image_names):
                html_path = (images_dir.parent / f"{Path(image_name).stem}.html").resolve()
                if not html_path.exists():
                    print(f"  {Colors.YELLOW}Warning:{Colors.ENDC} Could not find source file {html_path.name} to generate screenshot.")
                    continue
                try:
                    page.goto(f"file://{html_path}", wait_until="networkidle")
                    page.screenshot(path=images_dir / image_name, type="png")
                    print(f"  {Colors.GREEN}Generated:{Colors.ENDC} {Path('images') / image_name}")
                except PlaywrightError as e:
                    print(f"  {Colors.RED}Error: {Colors.ENDC}Could not screenshot {html_path.name}: {e}")
            browser.close()
        except PlaywrightError as e:
            print(f"{Colors.RED}Playwright Error: {e}. Ensure browsers are installed with: {Colors.BOLD}python3 -m playwright install{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description="Analyzes and fixes meta tags in HTML files.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan (default: current).")
    parser.add_argument("--base-url", default="https://cheatsheets.davidveksler.com/", help="Base URL for canonical links.")
    parser.add_argument("--apply", action="store_true", help="Apply proposed changes to files. Default is a dry-run report.")
    args = parser.parse_args()

    dir_path = Path(args.directory)
    if not dir_path.is_dir():
        print(f"{Colors.RED}Error: Directory '{args.directory}' not found.{Colors.ENDC}")
        return

    proposal = ChangeProposal()
    html_files = sorted(list(dir_path.glob("*.html")))
    if not html_files:
        print(f"{Colors.YELLOW}No HTML files found in '{dir_path.resolve()}' to analyze.{Colors.ENDC}")
        return

    for html_file in html_files:
        analyze_file(html_file, args.base_url, proposal)

    proposal.print_report()
    if not proposal.has_changes():
        return

    if args.apply:
        apply_changes(proposal, dir_path / "images")
        print(f"\n{Colors.GREEN}Processing complete.{Colors.ENDC}")
    else:
        print(f"\n{Colors.YELLOW}This was a dry run. To apply these changes, run again with the {Colors.BOLD}--apply{Colors.YELLOW} flag.{Colors.ENDC}")

if __name__ == "__main__":
    main()