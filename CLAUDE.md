# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a collection of interactive HTML cheatsheets covering various topics including technology, philosophy, AI safety, cryptocurrencies, martial arts, and more. The project consists of standalone HTML files that function as comprehensive reference guides.

## Architecture

### Core Structure
- **Standalone HTML files**: Each cheatsheet is a self-contained HTML file with embedded CSS and JavaScript
- **PHP index files**: Two PHP-based gallery interfaces (`index.php` and `index2.php`) that scan the directory and generate interactive portfolio views
- **Image management**: Screenshot generation and metadata extraction using Python (`generate-image-previews.py`)
- **Static assets**: Images stored in `/images/` directory for social media previews and content

### Key Files
- `index.php` - Main portfolio gallery with card-based layout and detailed metadata extraction
- `index2.php` - Interactive gallery with filtering and modal preview functionality  
- `generate-image-previews.py` - Python script for automated screenshot generation and HTML metadata management
- Individual `.html` files - Self-contained cheatsheets with Bootstrap 5.3.3, custom CSS, and interactive JavaScript

### HTML Cheatsheet Pattern
Each cheatsheet follows a consistent structure:
- Bootstrap 5.3.3 framework via CDN
- Bootstrap Icons for visual elements
- Collapsible sections using `<details>`/`<summary>` or Bootstrap collapse
- Interactive elements (filters, toggles, checkboxes with localStorage)
- Responsive design with print-friendly styles
- SEO metadata and Open Graph tags
- Semantic HTML5 with accessibility considerations

## Common Development Tasks

### Working with PHP Index Files
- The PHP files dynamically scan for `.html` files in the root directory
- They extract metadata from HTML files (title, description, og:image)
- Category assignment is handled via filename pattern matching in `getCategoryForFile()`

### Adding New Cheatsheets
1. Create a new `.html` file in the root directory following the established pattern
2. Include proper metadata (title, description, og:image)
3. The PHP index files will automatically discover and include it
4. Run `python generate-image-previews.py` to generate social media preview images

### Image Management
- Social media preview images are stored in `/images/` directory
- The Python script uses Playwright to generate screenshots
- Images follow naming convention: `{filename}.png`
- The script also updates HTML files with missing metadata tags

### Content Structure
Cheatsheets typically include:
- Page header with title and description
- Collapsible information cards
- Interactive elements (search, filters, toggles)
- Print-optimized styles
- External links with proper attributes (`target="_blank" rel="noopener noreferrer"`)

## Theme and Styling Approach
- Clean, modern design with responsive layouts
- Color theming appropriate to subject matter (dark themes for tech, light themes for academic content)
- Consistent use of Bootstrap components
- Custom CSS variables for theming
- Interactive hover effects and animations

## File Organization
- Root directory contains all HTML cheatsheets
- `/images/` for preview images and assets
- No build process - all files are standalone
- Static hosting friendly (can be served directly)

## Development Guidelines
- Maintain consistency with existing cheatsheet patterns
- Use semantic HTML with proper accessibility attributes
- Include comprehensive metadata for SEO and social sharing
- Test responsiveness and print styles
- Ensure all interactive elements work without JavaScript as fallback