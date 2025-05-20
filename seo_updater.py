import os
from bs4 import BeautifulSoup, Tag

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
        return {tag_def['type']: 'missing' for tag_def in SEO_TAGS_CONFIG}

    results = {}
    for tag_def in SEO_TAGS_CONFIG:
        status = 'missing' # Default to missing
        candidate_tags = head.find_all(tag_def['tag_name'], attrs=tag_def['attrs'])
        
        for tag_candidate in candidate_tags:
            content_value = tag_candidate.get(tag_def['content_attr'])
            expected_value = ''
            if tag_def['type'] == 'canonical' or tag_def['type'] == 'og_url' or tag_def['type'] == 'twitter_url':
                expected_value = generated_url
            elif tag_def['type'] == 'meta_description':
                # For meta description, if it exists and has *any* content, we consider it 'present_correct'
                # as per issue "only add it if the tag is missing". We won't update existing descriptions.
                if content_value: # Check if content attribute exists and is not empty
                    status = 'present_correct' 
                else: # Tag exists but content is empty
                    status = 'present_incorrect' # Or 'missing' if we want to treat empty as missing
                break 
            elif tag_def['type'] == 'twitter_creator':
                expected_value = tag_def['expected_content']
            
            if status == 'present_correct': # Already determined for meta_description
                break

            if content_value == expected_value:
                status = 'present_correct'
                break
            else:
                # Tag with same identifying attributes exists but content/href is wrong
                status = 'present_incorrect' 
                # Important: if multiple such tags exist (e.g. two <link rel="canonical">), 
                # finding one 'present_correct' is enough. If all are 'present_incorrect',
                # the last one's status will be kept. This is acceptable as we only add if 'missing'.
        results[tag_def['type']] = status
    return results

def add_missing_tags(soup, title, generated_url, tags_status):
    head = soup.find('head')
    html_tag = soup.find('html')

    if not html_tag:
        print("Error: No <html> tag found. Cannot process file.")
        return []

    if not head:
        head = soup.new_tag('head')
        # Try to insert head at the beginning of html tag's children
        if html_tag.contents:
            html_tag.insert(0, head)
        else:
            html_tag.append(head)
        print("Info: Created <head> tag.")
        
    tags_added = []
    last_added_element = None

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
            
            head.append(new_tag)
            last_added_element = new_tag
            # Add a newline text node after the tag
            head.append(soup.new_string('\n')) 
            
            tags_added.append(tag_def['type'])
            print(f"Action: Prepared to add {tag_def['type']} tag.")

    # This is an attempt to ensure the last added element is properly followed by a newline 
    # before the </head> tag, if newlines are not handled well by default by str() or prettify().
    # However, simply appending a newline after each tag should generally suffice.
    # If there were existing elements in head, this might not place the newline optimally
    # relative to pre-existing last element and the new block of tags.
    # For now, appending newline after each tag is the primary strategy.

    return tags_added

def main():
    html_files = find_html_files()
    if not html_files:
        print("No HTML files found in the current directory.")
        return

    print("Processing HTML files for SEO metadata updates:")
    for f_path in html_files:
        print(f"--- Processing: {os.path.basename(f_path)} ---")
        try:
            with open(f_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
            soup = BeautifulSoup(content, "html.parser")
        except FileNotFoundError:
            print(f"Error: File not found - {f_path}")
            continue
        except Exception as e:
            print(f"Error: Could not read or parse file {f_path}: {e}")
            continue

        title = extract_title_from_soup(soup)
        generated_url = generate_url(f_path)

        if not title:
            print(f"Warning: No title found in {os.path.basename(f_path)}. Meta description cannot be added if missing.")

        tags_status = check_seo_tags(soup, title if title else "", generated_url)
        
        status_summary = []
        needs_addition_check = False # Renamed from needs_update for clarity
        for tag_type, status_val in tags_status.items():
            # Format status for printing
            formatted_status = status_val.replace('_', ' ').capitalize()
            status_summary.append(f"{tag_type.replace('_', ' ').title()}: {formatted_status}")
            
            if status_val == 'missing':
                 if tag_type == 'meta_description' and not title:
                     pass 
                 else:
                    needs_addition_check = True
        
        print(f"  Current SEO Status: {'; '.join(status_summary)}")

        if needs_addition_check:
            tags_added = add_missing_tags(soup, title if title else "", generated_url, tags_status)
            if tags_added:
                try:
                    with open(f_path, 'w', encoding='utf-8') as file:
                        file.write(str(soup)) 
                    print(f"  SUCCESS: Updated {os.path.basename(f_path)}. Added/Modified: {', '.join(tags_added)}.")
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
