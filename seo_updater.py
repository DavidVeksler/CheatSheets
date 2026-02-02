import os
from bs4 import BeautifulSoup, Tag # Ensure Tag is imported if used, though it's not explicitly in this snippet

# SEO_TAGS_CONFIG remains the same
SEO_TAGS_CONFIG = [
    {'type': 'canonical', 'tag_name': 'link', 'attrs': {'rel': 'canonical'}, 'content_attr': 'href'},
    {'type': 'meta_description', 'tag_name': 'meta', 'attrs': {'name': 'description'}, 'content_attr': 'content'},
    {'type': 'og_url', 'tag_name': 'meta', 'attrs': {'property': 'og:url'}, 'content_attr': 'content'},
    {'type': 'twitter_url', 'tag_name': 'meta', 'attrs': {'name': 'twitter:url'}, 'content_attr': 'content'},
    {'type': 'twitter_creator', 'tag_name': 'meta', 'attrs': {'name': 'twitter:creator'}, 'content_attr': 'content', 'expected_content': '@heroiclife'},
]

def find_html_files(directory="."):
    html_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            html_files.append(os.path.join(directory, filename))
    return html_files

def extract_title_from_soup(soup):
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return None

def generate_url(html_file_path):
    base_url = "https://cheatsheets.davidveksler.com/"
    filename = os.path.basename(html_file_path)
    return base_url + filename

def check_seo_tags(soup, title, generated_url):
    head = soup.find('head')
    if not head:
        # Create a results dictionary with all tags marked as missing if no head tag exists
        results_if_no_head = {}
        for tag_def in SEO_TAGS_CONFIG:
            results_if_no_head[tag_def['type']] = 'missing'
        return results_if_no_head


    results = {}
    for tag_def in SEO_TAGS_CONFIG:
        status = 'missing' # Default to missing
        # Ensure find_all is called on a valid Tag object (head)
        candidate_tags = head.find_all(tag_def['tag_name'], attrs=tag_def['attrs'])
        
        for tag_candidate in candidate_tags:
            content_value = tag_candidate.get(tag_def['content_attr'])
            expected_value = ''
            if tag_def['type'] == 'canonical' or tag_def['type'] == 'og_url' or tag_def['type'] == 'twitter_url':
                expected_value = generated_url
            elif tag_def['type'] == 'meta_description':
                if content_value: 
                    status = 'present_correct' 
                else: 
                    status = 'present_incorrect'
                break 
            elif tag_def['type'] == 'twitter_creator':
                expected_value = tag_def['expected_content']
            
            if status == 'present_correct': 
                break

            if content_value == expected_value:
                status = 'present_correct'
                break
            else:
                status = 'present_incorrect' 
        results[tag_def['type']] = status
    return results

def add_missing_tags(soup, title, generated_url, tags_status):
    head = soup.find('head')
    html_tag = soup.find('html')

    if not html_tag:
        print("Error: No <html> tag found. Cannot process file.")
        # It's good practice to return an empty list or handle this error appropriately
        return [], soup 

    if not head:
        head = soup.new_tag('head')
        # Insert head at the beginning of html tag's children
        # Correctly handle if html_tag has no children or only NavigableString
        first_child = html_tag.find(True, recursive=False) # Find first actual tag child
        if first_child:
            first_child.insert_before(head)
        else: # No children or only string content
            html_tag.insert(0, head) # Insert at the beginning

        # Add a newline after the new head tag for formatting if it's the first element
        if head.previous_sibling is None:
             html_tag.insert(1, soup.new_string('\n'))
        else: # Insert newline after head
            head.insert_after(soup.new_string('\n'))
        print("Info: Created <head> tag.")
        
    tags_added = []

    # Find the last element in head to append after, or append to head directly
    # This helps in placing newlines more predictably.
    # We'll append all new tags, then newlines after them if needed.
    
    elements_to_add_to_head = []

    for tag_def in SEO_TAGS_CONFIG:
        if tags_status.get(tag_def['type']) == 'missing':
            if tag_def['type'] == 'meta_description' and (not title or not title.strip()):
                print(f"Warning: Title is missing or empty for {tag_def['type']}. Skipping.")
                continue

            new_tag = soup.new_tag(tag_def['tag_name'], attrs=tag_def['attrs'])
            
            content_to_set = ""
            if tag_def['type'] in ['canonical', 'og_url', 'twitter_url']:
                content_to_set = generated_url
            elif tag_def['type'] == 'meta_description':
                content_to_set = title.strip() 
            elif tag_def['type'] == 'twitter_creator':
                content_to_set = tag_def['expected_content']
            
            new_tag[tag_def['content_attr']] = content_to_set
            
            elements_to_add_to_head.append(new_tag)
            tags_added.append(tag_def['type'])
            print(f"Action: Prepared to add {tag_def['type']} tag.")

    # Append all new tags and their trailing newlines to the head
    for el in elements_to_add_to_head:
        head.append(el)
        head.append(soup.new_string('\n')) # Add a newline text node after the tag

    return tags_added, soup


def main():
    # Determine the best available parser
    DEFAULT_PARSER = "html.parser" # Fallback parser
    PREFERRED_PARSERS = ["lxml", "html5lib"] # In order of preference
    
    active_parser = DEFAULT_PARSER
    for parser_name in PREFERRED_PARSERS:
        try:
            BeautifulSoup("<html></html>", parser_name) # Test if parser is available
            active_parser = parser_name
            print(f"Info: Using '{active_parser}' parser.")
            break
        except Exception: # bs4.FeatureNotFound if parser not installed/functional
            pass # Try next parser
    
    if active_parser == DEFAULT_PARSER:
        print(f"Warning: Neither 'lxml' nor 'html5lib' parsers were found. "
              f"Falling back to Python's built-in '{DEFAULT_PARSER}'. "
              f"This parser may struggle with malformed HTML, potentially leading to "
              f"incorrect processing or output. For best results, consider installing 'lxml' "
              f"(e.g., 'pip install lxml') or 'html5lib' (e.g., 'pip install html5lib').")


    html_files = find_html_files()
    if not html_files:
        print("No HTML files found in the current directory.")
        return

    print(f"\nProcessing HTML files for SEO metadata updates (using {active_parser} parser):")
    for f_path in html_files:
        print(f"--- Processing: {os.path.basename(f_path)} ---")
        try:
            with open(f_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
            # Use the determined active_parser
            soup = BeautifulSoup(content, active_parser)
        except FileNotFoundError:
            print(f"Error: File not found - {f_path}")
            continue
        except Exception as e: # Catch other exceptions like bs4.FeatureNotFound if test failed
            print(f"Error: Could not read or parse file {f_path} with {active_parser}: {e}")
            continue

        title = extract_title_from_soup(soup)
        generated_url = generate_url(f_path)

        if not title:
            print(f"Warning: No title found in {os.path.basename(f_path)}. Meta description cannot be added if missing.")

        tags_status = check_seo_tags(soup, title if title else "", generated_url)
        
        status_summary = []
        needs_addition_check = False
        for tag_type, status_val in tags_status.items():
            formatted_status = status_val.replace('_', ' ').capitalize()
            status_summary.append(f"{tag_type.replace('_', ' ').title()}: {formatted_status}")
            
            if status_val == 'missing':
                 if tag_type == 'meta_description' and not title:
                     pass 
                 else:
                    needs_addition_check = True
        
        print(f"  Current SEO Status: {'; '.join(status_summary)}")

        if needs_addition_check:
            tags_added, soup = add_missing_tags(soup, title if title else "", generated_url, tags_status) # soup can be reassigned
            if tags_added:
                try:
                    # Use prettify with a specific HTML formatter for cleaner and more standard output
                    # This ensures HTML void elements are handled correctly (e.g., <meta ...> not <meta ...></meta>)
                    output_html = soup.prettify(formatter="html")
                    with open(f_path, 'w', encoding='utf-8') as file:
                        file.write(output_html) 
                    print(f"  SUCCESS: Updated {os.path.basename(f_path)}. Added: {', '.join(tags_added)}.")
                except Exception as e:
                    print(f"  ERROR: Could not write changes to {f_path}: {e}")
            else:
                print(f"  Info: No tags were added to {os.path.basename(f_path)} (e.g., title missing for description, or all necessary tags already present in some form).")
        else:
            all_correct = all(s == 'present_correct' for s in tags_status.values())
            if all_correct:
                 print(f"  Info: {os.path.basename(f_path)} is already fully compliant with SEO tag requirements.")
            else:
                 print(f"  Info: No missing tags eligible for automatic addition in {os.path.basename(f_path)} (e.g. some tags might be 'present_incorrect' but not 'missing').")
        print("-" * 30)


if __name__ == "__main__":
    main()