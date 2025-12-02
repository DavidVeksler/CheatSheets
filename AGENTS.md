# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a collection of interactive HTML cheatsheets covering various topics including technology, philosophy, AI safety, cryptocurrencies, martial arts, and more. The project consists of standalone HTML files that function as comprehensive reference guides.

## Architecture

### Core Structure
- **Standalone HTML files**: Each cheatsheet is a self-contained HTML file with embedded CSS and JavaScript
- **PHP index file**: `index.php` - Main portfolio gallery with card-based layout and detailed metadata extraction
- **PHP sitemap**: `sitemap.php` - SEO-optimized XML sitemap with dynamic priority and changefreq
- **Image management**: Screenshot generation and metadata extraction using Python (`generate-image-previews.py`)
- **Static assets**: Images stored in `/images/` directory for social media previews and content

### Key Files
- `index.php` - Main portfolio gallery with card-based layout and detailed metadata extraction
- `sitemap.php` - SEO-optimized XML sitemap generator with category-based priorities
- `generate-image-previews.py` - Python script for automated screenshot generation and HTML metadata management
- Individual `.html` files - Self-contained cheatsheets with Bootstrap 5.3.3, custom CSS, and interactive JavaScript

### File Status (Current)
- `index2.php` - Removed (duplicate functionality)
- Total cheatsheets: 47+ HTML files covering technology, finance, philosophy, martial arts, and tools
- Recent additions: `lifestyle-calculator.html`, `clean-architecture-dotnet.html`

### HTML Cheatsheet Pattern
Each cheatsheet follows a consistent structure:
- Bootstrap 5.3.3 framework via CDN
- Bootstrap Icons for visual elements
- Collapsible sections using `<details>`/`<summary>` or Bootstrap collapse
- Interactive elements (filters, toggles, checkboxes with localStorage)
- Responsive design with print-friendly styles
- Comprehensive SEO metadata package
- Semantic HTML5 with accessibility considerations

### Required Metadata Standards
Every cheatsheet must include:

#### Essential SEO Tags
```html
<title>Topic: Descriptive Subtitle</title>
<meta name="description" content="150-200 char comprehensive description"/>
<meta name="keywords" content="primary topic, technology stack, related concepts"/>
<link rel="canonical" href="https://cheatsheets.davidveksler.com/filename.html"/>
```

#### Open Graph Tags
```html
<meta property="og:title" content="Title"/>
<meta property="og:description" content="Description"/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="https://cheatsheets.davidveksler.com/filename.html"/>
<meta property="og:image" content="images/filename.png"/>
<meta property="og:image:alt" content="Descriptive alt text"/>
```

#### Twitter Card Tags
```html
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="Title"/>
<meta name="twitter:description" content="Description"/>
<meta name="twitter:image" content="images/filename.png"/>
<meta name="twitter:creator" content="@heroiclife"/>
```

#### JSON-LD Structured Data (Required)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Title with Version",
  "description": "Detailed description",
  "author": {"@type": "Person", "name": "David Veksler (AI Generated)"},
  "publisher": {"@type": "Organization", "name": "David Veksler Cheatsheets"},
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "keywords": "keyword list"
}
</script>
```

## Common Development Tasks

### Working with PHP Index Files
- The PHP files dynamically scan for `.html` files in the root directory
- They extract metadata from HTML files (title, description, og:image)
- Category assignment is handled via filename pattern matching in `getCategoryForFile()`

### Adding New Cheatsheets
1. Create a new `.html` file in the root directory following the established pattern
2. Include ALL required metadata sections (SEO, Open Graph, Twitter, JSON-LD)
3. Use consistent naming: `topic-subtopic.html` (lowercase, hyphens)
4. The PHP index and sitemap files will automatically discover and include it
5. Run `python generate-image-previews.py` to generate social media preview images

### Image Management
- Social media preview images are stored in `/images/` directory
- The Python script uses Playwright to generate screenshots
- Images follow naming convention: `{filename}.png` (matching HTML filename)
- The script also updates HTML files with missing metadata tags
- Use descriptive alt text for accessibility

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

### Code Quality Standards
- Maintain consistency with existing cheatsheet patterns
- Use semantic HTML with proper accessibility attributes
- Include ALL required metadata sections (no exceptions)
- Test responsiveness and print styles
- Ensure all interactive elements work without JavaScript as fallback
- Use consistent Bootstrap 5.3.3 components and utilities

### SEO Best Practices
- Every new cheatsheet MUST include JSON-LD structured data
- Optimize meta descriptions (150-200 characters)
- Use descriptive, keyword-rich titles
- Include comprehensive keyword lists
- Ensure all images have proper alt text
- Test Open Graph and Twitter Card previews

### Content Guidelines
- Use clear, actionable section headers
- Implement collapsible sections for better UX
- Include interactive elements where appropriate
- Add print-friendly styles
- Ensure content is accessible without JavaScript

### Testing Checklist
- [ ] All metadata tags present and valid
- [ ] Responsive design on mobile/tablet/desktop
- [ ] Print styles work correctly
- [ ] Interactive elements function properly
- [ ] Accessibility standards met
- [ ] Social media previews display correctly
- [ ] Image generated and placed in `/images/` directory