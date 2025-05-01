<?php
// Set content type and encoding
header('Content-Type: text/html; charset=utf-8');

// --- Configuration ---
$excludedItems = [
    '.',
    '..',
    'index.php',
    'browse.html',
    'images',
    'LICENSE',
    'README.md',
    'PROMPT.txt',
    'history_tree_style.css',
    'safety_data.js',
];

$cheatsheetDir = '.';
$scheme = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
$host = $_SERVER['HTTP_HOST'];
$scriptDir = dirname($_SERVER['SCRIPT_NAME']);
$baseUrl = rtrim($scheme . '://' . $host . $scriptDir, '/') . '/';

// --- !!! Action Needed: Define Categories !!! ---
// You need a way to map filenames or metadata to categories.
// Example: Simple mapping (replace with your logic)
function getCategoryForFile(string $filename): string {
    $filenameLower = strtolower($filename);
    if (str_contains($filenameLower, 'ai') || str_contains($filenameLower, 'safety')) return 'ai';
    if (str_contains($filenameLower, 'bitcoin') || str_contains($filenameLower, 'crypto')) return 'crypto';
    if (str_contains($filenameLower, 'leadership')) return 'leadership';
    if (str_contains($filenameLower, 'buddhism') || str_contains($filenameLower, 'judaism') || str_contains($filenameLower, 'philosophy') || str_contains($filenameLower, 'objectivism') || str_contains($filenameLower, 'capitalism')) return 'philosophy';
    if (str_contains($filenameLower, 'database') || str_contains($filenameLower, 'postgres') || str_contains($filenameLower, 'versioncontrol') || str_contains($filenameLower, 'sql')) return 'tech';
    return 'other'; // Default category
}

// --- Helper Function: Extract Metadata ---
function extractMetadata(string $filepath): array {
    global $baseUrl, $scheme, $host;

    $filename = basename($filepath);
    $metadata = [
        'id' => 'cs-' . pathinfo($filename, PATHINFO_FILENAME), // Unique ID for JS targeting
        'title' => pathinfo($filename, PATHINFO_FILENAME),
        'description' => 'Explore this cheatsheet to learn more.',
        'image' => null,
        'url' => $baseUrl . $filename,
        'category' => getCategoryForFile($filename), // Assign category
        'error' => null
    ];

    $content = @file_get_contents($filepath);
    if ($content === false) {
        $metadata['error'] = "Could not read file: " . $filename;
        return $metadata;
    }

    $dom = new DOMDocument();
    @$dom->loadHTML($content, LIBXML_NOERROR | LIBXML_NOWARNING);
    $xpath = new DOMXPath($dom);

    $titleNode = $xpath->query('//title')->item(0);
    if ($titleNode) $metadata['title'] = trim($titleNode->textContent);

    $descNode = $xpath->query('//meta[@name="description"]/@content')->item(0);
    if ($descNode) {
        $metadata['description'] = trim($descNode->nodeValue);
    } else {
        $ogDescNode = $xpath->query('//meta[@property="og:description"]/@content')->item(0);
        if ($ogDescNode) $metadata['description'] = trim($ogDescNode->nodeValue);
    }

    $imgNode = $xpath->query('//meta[@property="og:image"]/@content')->item(0);
    if ($imgNode) {
        $imageUrl = trim($imgNode->nodeValue);
        if (!preg_match('/^https?:\/\//i', $imageUrl)) {
             if (str_starts_with($imageUrl, '/')) {
                 $metadata['image'] = $scheme . '://' . $host . $imageUrl;
             } else {
                 $absoluteImagePath = realpath(dirname(__FILE__)) . '/' . $imageUrl;
                 if (file_exists($absoluteImagePath)) {
                    $metadata['image'] = $baseUrl . $imageUrl;
                 } else {
                     error_log("Relative image path not found: " . $imageUrl . " in " . $filename);
                 }
             }
        } else {
            $metadata['image'] = $imageUrl;
        }
    }

    if (mb_strlen($metadata['description']) > 150) {
        $metadata['description'] = mb_substr($metadata['description'], 0, 147) . '...';
    }

    return $metadata;
}

// --- Main Logic: Scan Directory and Build Cheatsheet List ---
$cheatsheets = [];
$errors = [];
$categories = ['all']; // Start with 'all'

try {
    $files = scandir($cheatsheetDir);
    if ($files === false) throw new Exception("Could not scan directory: " . $cheatsheetDir);

    foreach ($files as $file) {
        $filePath = $cheatsheetDir . '/' . $file;
        if (in_array($file, $excludedItems, true) || !is_file($filePath) || !is_readable($filePath)) continue;

        if (str_ends_with(strtolower($file), '.html')) {
            $meta = extractMetadata($filePath);
            if ($meta['error']) {
                $errors[] = $meta['error'];
            } else {
                $cheatsheets[] = $meta;
                if (!in_array($meta['category'], $categories)) {
                    $categories[] = $meta['category'];
                }
            }
        }
    }
    sort($categories); // Sort categories alphabetically (optional)
    // Sort cheatsheets alphabetically by title
    usort($cheatsheets, fn($a, $b) => strcasecmp($a['title'], $b['title']));

} catch (Exception $e) {
    $errors[] = "An error occurred: " . $e->getMessage();
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Metadata -->
    <title>David Veksler's Interactive Cheatsheet Gallery</title>
    <meta name="description" content="Explore an interactive gallery of expertly crafted cheatsheets by David Veksler. Filter by topic and view details dynamically. Custom design services available.">
    <meta name="keywords" content="interactive cheatsheets, portfolio, gallery, filter, javascript gallery, cheatsheet design, information design, david veksler, tech, philosophy, ai safety, bitcoin, leadership, custom cheatsheets">
    <!-- Other meta tags (author, canonical, OG, Twitter) remain similar -->
    <link rel="canonical" href="<?php echo htmlspecialchars($baseUrl); ?>">
    <meta property="og:title" content="David Veksler's Interactive Cheatsheet Gallery">
    <meta property="og:description" content="Explore an interactive gallery of expertly crafted cheatsheets. Filter by topic, view details dynamically.">
    <meta property="og:image" content="<?php echo htmlspecialchars($baseUrl); ?>images/cheatsheets-og-gallery.png"> <!-- Suggest creating a gallery-specific OG image -->
    <meta property="og:image:alt" content="Interactive Cheatsheet Gallery Showcase">
    <!-- Twitter card meta -->

    <!-- Bootstrap CSS & Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">

    <!-- Custom CSS for Awesome Gallery -->
    <style>
        :root {
            --gallery-bg-start: #f8f9fa;
            --gallery-bg-end: #e9ecef;
            --card-hover-scale: 1.03;
            --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            --card-hover-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
            --expanded-view-bg: rgba(255, 255, 255, 0.98);
            --expanded-view-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            --filter-active-bg: #0d6efd;
            --filter-active-color: #fff;
        }
        html { scroll-behavior: smooth; }
        body {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-image: linear-gradient(135deg, var(--gallery-bg-start) 0%, var(--gallery-bg-end) 100%);
            overflow-x: hidden; /* Prevent horizontal scroll during animations */
        }
        .main-content { flex: 1; }
        .navbar { background-image: linear-gradient(to bottom, #343a40, #212529); }

        /* --- Filter Buttons --- */
        .filter-buttons .btn {
            margin: 0.25rem;
            transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out;
        }
        .filter-buttons .btn.active {
            background-color: var(--filter-active-bg);
            color: var(--filter-active-color);
            border-color: var(--filter-active-bg);
        }

        /* --- Portfolio Grid & Items --- */
        #cheatsheetGrid {
            position: relative; /* Needed for positioning expanded item */
        }
        .portfolio-item {
            /* Styles for the column */
            transition: opacity 0.4s ease-out, transform 0.4s ease-out;
        }
        .portfolio-item.filtered-out {
             opacity: 0;
             transform: scale(0.9);
             /* We'll add d-none via JS after transition */
             pointer-events: none; /* Avoid interacting while hiding */
             position: absolute; /* Take out of flow smoothly */
             z-index: -1;
        }
        .portfolio-card {
            cursor: pointer;
            border-radius: 8px;
            overflow: hidden;
            background-color: #fff;
            box-shadow: var(--card-shadow);
            transition: transform 0.3s ease-out, box-shadow 0.3s ease-out;
            height: 100%; /* Fill the column height */
            display: flex;
            flex-direction: column;
        }
        .portfolio-card:hover {
            transform: scale(var(--card-hover-scale));
            box-shadow: var(--card-hover-shadow);
            z-index: 10; /* Bring slightly forward on hover */
        }
        .card-thumbnail {
            aspect-ratio: 16 / 9;
            background-color: #e9ecef;
            background-size: cover;
            background-position: center;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #adb5bd;
            border-bottom: 1px solid #dee2e6;
        }
         .card-thumbnail::before { /* Placeholder Icon */
             font-family: 'bootstrap-icons';
             content: "\F48B"; /* bi-image-alt */
             font-size: 2.5rem;
             opacity: 0.5;
        }
         /* Hide placeholder if image is set via style */
         .card-thumbnail[style*="background-image"]::before {
             display: none;
         }
        .portfolio-card .card-body {
            padding: 1rem;
            flex-grow: 1; /* Allow body to take remaining space */
        }
        .portfolio-card .card-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0; /* Title is main element here */
        }

        /* --- Expanded View --- */
        .expanded-view-container {
             display: none; /* Hidden initially */
             position: fixed; /* Overlay */
             top: 0; left: 0; right: 0; bottom: 0;
             background-color: rgba(0, 0, 0, 0.6); /* Dim background */
             z-index: 1050; /* Above most content */
             padding: 2rem;
             overflow-y: auto;
             cursor: pointer; /* Indicate clicking outside closes */
        }
        .expanded-view-content {
            position: relative;
            background-color: var(--expanded-view-bg);
            border-radius: 10px;
            box-shadow: var(--expanded-view-shadow);
            max-width: 800px; /* Control max width */
            margin: 2rem auto; /* Centered */
            padding: 1.5rem 2rem;
            cursor: default; /* Standard cursor inside content */
            transform: scale(0.9);
            opacity: 0;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.3s ease-out; /* Nice bounce effect */
        }
        .expanded-view-container.visible {
             display: block;
        }
         .expanded-view-container.visible .expanded-view-content {
             transform: scale(1);
             opacity: 1;
        }

        .expanded-view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #eee; padding-bottom: 0.8rem;}
        .expanded-view-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 0; }
        .expanded-view-close { font-size: 1.8rem; line-height: 1; background: none; border: none; opacity: 0.6; transition: opacity 0.2s; }
        .expanded-view-close:hover { opacity: 1; }

        .expanded-view-body { display: flex; flex-direction: column; gap: 1.5rem; }
        .expanded-preview {
            width: 100%;
            aspect-ratio: 16 / 9;
            background-color: #f0f0f0;
            border-radius: 5px;
            overflow: hidden;
            display: flex; align-items: center; justify-content: center;
        }
        .expanded-preview iframe { width: 100%; height: 100%; border: none; }
        .expanded-preview img { width: 100%; height: 100%; object-fit: cover; }
         .expanded-description { color: #333; line-height: 1.6; }
         .expanded-actions { text-align: center; margin-top: 1rem; }

         /* Spinner for iframe loading */
         .spinner-container { position: absolute; top:0; left:0; right:0; bottom:0; background:rgba(255,255,255,0.8); display: flex; align-items: center; justify-content: center; z-index: 5; opacity:0; transition: opacity 0.3s; pointer-events: none; }
         .spinner-container.loading { opacity: 1; pointer-events: auto;}

        /* Footer & Subtle CTA */
        .footer { background-color: #e9ecef; color: #6c757d; border-top: 1px solid #ced4da; }
        .cta-scroll-link { font-size: 0.9rem; text-decoration: none; }
        .cta-scroll-link:hover { text-decoration: underline; }
        .cta-section-bottom { border-top: 1px solid #dee2e6; padding-top: 2rem; padding-bottom: 1rem; margin-top: 3rem; }
    </style>
</head>
<body class="d-flex flex-column min-vh-100">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="<?php echo htmlspecialchars($baseUrl); ?>">
                 <i class="bi bi-grid-3x3-gap-fill me-2"></i>David Veksler's Interactive Gallery
            </a>
        </div>
    </nav>

    <main class="main-content container mt-4 mb-5">
        <header class="text-center mb-4">
            <h1 class="display-5 fw-bold">Cheatsheet Showcase</h1>
            <p class="lead text-muted">Explore interactive examples. Filter by category or search.</p>
             <a href="#custom-cheatsheets" class="cta-scroll-link link-secondary d-block mb-3"><i class="bi bi-tools me-1"></i>Need a custom cheatsheet?</a>
        </header>

        <!-- Filter Buttons -->
        <div id="filterButtons" class="filter-buttons text-center mb-4">
            <?php foreach ($categories as $category): ?>
                <button class="btn btn-sm <?php echo ($category === 'all') ? 'btn-primary active' : 'btn-outline-secondary'; ?>" data-filter="<?php echo htmlspecialchars($category); ?>">
                    <?php echo htmlspecialchars(ucfirst($category)); ?>
                </button>
            <?php endforeach; ?>
        </div>

         <!-- Text Filter Input (Optional) -->
        <div class="row mb-4 justify-content-center">
            <div class="col-md-8 col-lg-6">
                <div class="input-group shadow-sm">
                    <span class="input-group-text bg-white border-end-0" id="search-addon"><i class="bi bi-search text-primary"></i></span>
                    <input type="search" id="searchInput" class="form-control border-start-0" placeholder="Search within category..." aria-label="Search cheatsheets" aria-describedby="search-addon">
                </div>
            </div>
        </div>

        <!-- Error Display -->
        <?php if (!empty($errors)): ?>
            <div class="alert alert-warning">... errors ...</div>
        <?php endif; ?>
        <?php if (empty($cheatsheets) && empty($errors)): ?>
             <div class="alert alert-info text-center">No cheatsheet examples found.</div>
        <?php endif; ?>

        <!-- Cheatsheet Grid -->
        <div id="cheatsheetGrid" class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4">
            <?php if (!empty($cheatsheets)): ?>
                <?php foreach ($cheatsheets as $sheet): ?>
                    <div class="col portfolio-item" data-category="<?php echo htmlspecialchars($sheet['category']); ?>" data-title="<?php echo htmlspecialchars(strtolower($sheet['title'])); ?>" id="<?php echo htmlspecialchars($sheet['id']); ?>">
                        <div class="portfolio-card" role="button" tabindex="0" aria-label="View details for <?php echo htmlspecialchars($sheet['title']); ?>">
                            <div class="card-thumbnail" <?php if (!empty($sheet['image'])): ?> style="background-image: url('<?php echo htmlspecialchars($sheet['image']); ?>');" <?php endif; ?>>
                                <!-- Placeholder handled by CSS -->
                            </div>
                            <div class="card-body">
                                <h5 class="card-title"><?php echo htmlspecialchars($sheet['title']); ?></h5>
                            </div>
                            <!-- Hidden data for expanded view -->
                            <script type="application/json" class="cheatsheet-data">
                                <?php echo json_encode([
                                    'title' => $sheet['title'],
                                    'description' => $sheet['description'],
                                    'url' => $sheet['url'],
                                    'image' => $sheet['image']
                                ]); ?>
                            </script>
                        </div>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>

         <!-- No Results Message -->
        <div id="noResults" class="alert alert-warning text-center mt-4 d-none" role="alert">
            <i class="bi bi-emoji-frown me-2"></i>No cheatsheets match your criteria.
        </div>

        <!-- Call to Action Section -->
         <section id="custom-cheatsheets" class="cta-section-bottom text-center">
              <h3 class="h4 fw-normal mb-3">Need a Custom Cheatsheet?</h3>
              <p class="text-muted mb-3 mx-auto" style="max-width: 600px;">I design professional, tailored cheatsheets for documentation, training, marketing, and more.</p>
              <a href="https://www.linkedin.com/in/davidveksler/" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary btn-sm">
                  <i class="bi bi-linkedin me-1"></i> Discuss Your Project on LinkedIn
              </a>
          </section>
    </main>

    <!-- Expanded View Structure (Initially Hidden) -->
    <div id="expandedView" class="expanded-view-container">
        <div class="expanded-view-content" role="dialog" aria-modal="true" aria-labelledby="expandedViewTitle">
             <div class="expanded-view-header">
                 <h2 id="expandedViewTitle" class="expanded-view-title">Cheatsheet Title</h2>
                 <button type="button" class="expanded-view-close" aria-label="Close dialog">×</button>
             </div>
             <div class="expanded-view-body">
                 <div class="expanded-preview">
                     <!-- Content (image or iframe) added by JS -->
                      <div class="spinner-container"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>
                 </div>
                 <p class="expanded-description">Description goes here...</p>
             </div>
             <div class="expanded-actions">
                <a href="#" id="expandedViewLink" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
                    View Full Cheatsheet <i class="bi bi-box-arrow-up-right ms-1"></i>
                </a>
            </div>
        </div>
    </div>


    <!-- Footer -->
    <footer class="footer py-4 mt-auto border-top bg-light">
        <div class="container text-center">
            <p class="mb-2 text-muted">
                Interactive Cheatsheet Gallery by David Veksler © <?php echo date("Y"); ?>
            </p>
            <div>
              <a href="https://www.linkedin.com/in/davidveksler/" title="David Veksler on LinkedIn" target="_blank" rel="noopener noreferrer" class="mx-2 link-secondary"><i class="bi bi-linkedin"></i> LinkedIn</a>
              <span class="text-muted mx-1">|</span>
              <a href="<?php echo htmlspecialchars($baseUrl); ?>" title="Reload Gallery" class="mx-2 link-secondary"><i class="bi bi-collection"></i> Gallery Home</a>
            </div>
        </div>
    </footer>

    <!-- Bootstrap Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>

    <!-- Custom JS for Gallery -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const grid = document.getElementById('cheatsheetGrid');
            const items = grid.querySelectorAll('.portfolio-item');
            const filterButtonsContainer = document.getElementById('filterButtons');
            const searchInput = document.getElementById('searchInput');
            const noResultsMessage = document.getElementById('noResults');
            const expandedViewContainer = document.getElementById('expandedView');
            const expandedViewContent = expandedViewContainer.querySelector('.expanded-view-content');
            const expandedViewClose = expandedViewContainer.querySelector('.expanded-view-close');
            const expandedViewTitle = expandedViewContainer.querySelector('#expandedViewTitle');
            const expandedPreview = expandedViewContainer.querySelector('.expanded-preview');
            const expandedDescription = expandedViewContainer.querySelector('.expanded-description');
            const expandedLink = expandedViewContainer.querySelector('#expandedViewLink');
            const spinnerContainer = expandedPreview.querySelector('.spinner-container');

            let currentFilter = 'all'; // Track current category filter
            let currentSearch = '';   // Track current search term

            // --- Filtering Logic ---
            function applyFilters() {
                 let itemsVisible = 0;
                 items.forEach(item => {
                     const categoryMatch = currentFilter === 'all' || item.dataset.category === currentFilter;
                     const searchMatch = currentSearch === '' || item.dataset.title.includes(currentSearch); // Simple title search

                     const shouldShow = categoryMatch && searchMatch;

                     if (shouldShow) {
                         if (item.classList.contains('filtered-out')) {
                             // Make visible: remove d-none first, then transition classes
                             item.classList.remove('d-none');
                             // Use setTimeout to allow the 'd-none' removal to render before starting transition
                             setTimeout(() => {
                                item.classList.remove('filtered-out');
                                item.classList.remove('position-absolute'); // Restore flow
                                item.classList.remove('z-index:-1')
                                item.style.pointerEvents = '';
                            }, 10); // Small delay
                         }
                         itemsVisible++;
                     } else {
                         if (!item.classList.contains('filtered-out')) {
                            item.classList.add('filtered-out');
                            // Add d-none after the transition might have completed
                            item.addEventListener('transitionend', () => {
                                if (item.classList.contains('filtered-out')) { // Check if still filtered out
                                     item.classList.add('d-none');
                                }
                            }, { once: true });
                         }
                     }
                 });

                 noResultsMessage.classList.toggle('d-none', itemsVisible > 0);
            }

            // Category Filter Button Clicks
            filterButtonsContainer.addEventListener('click', function(e) {
                if (e.target.tagName === 'BUTTON') {
                    const filterValue = e.target.dataset.filter;
                    if (filterValue === currentFilter) return; // No change

                    filterButtonsContainer.querySelector('.active').classList.remove('active', 'btn-primary');
                    filterButtonsContainer.querySelector('.active').classList.add('btn-outline-secondary'); // Make previously active outlined
                    e.target.classList.add('active', 'btn-primary');
                    e.target.classList.remove('btn-outline-secondary'); // Make currently active primary

                    currentFilter = filterValue;
                    applyFilters();
                }
            });

            // Search Input
            searchInput.addEventListener('input', function() {
                 currentSearch = searchInput.value.toLowerCase().trim();
                 applyFilters();
            });


            // --- Expanded View Logic ---
            function showExpandedView(itemData) {
                expandedViewTitle.textContent = itemData.title;
                expandedDescription.textContent = itemData.description;
                expandedLink.href = itemData.url;
                expandedPreview.innerHTML = ''; // Clear previous content

                // Re-add spinner
                expandedPreview.appendChild(spinnerContainer.cloneNode(true));
                const currentSpinner = expandedPreview.querySelector('.spinner-container');
                currentSpinner.classList.add('loading'); // Show spinner immediately

                // Decide whether to show image or iframe
                if (itemData.image) {
                    const img = document.createElement('img');
                    img.src = itemData.image;
                    img.alt = `Preview for ${itemData.title}`;
                    img.loading = 'lazy';
                    img.onload = () => currentSpinner.classList.remove('loading'); // Hide spinner on load
                    img.onerror = () => { // Fallback to iframe if image fails
                        console.warn("Image failed to load, trying iframe:", itemData.image);
                        loadIframePreview(itemData.url, currentSpinner);
                    };
                    expandedPreview.appendChild(img);
                } else {
                    // Load iframe directly if no image
                   loadIframePreview(itemData.url, currentSpinner);
                }

                expandedViewContainer.classList.add('visible');
                document.body.style.overflow = 'hidden'; // Prevent background scroll
            }

            function loadIframePreview(url, spinner) {
                 const iframe = document.createElement('iframe');
                 iframe.src = url;
                 iframe.title = `Preview of ${expandedViewTitle.textContent}`;
                 iframe.setAttribute('loading', 'lazy');
                 iframe.setAttribute('frameborder', '0');
                 iframe.setAttribute('referrerpolicy', 'no-referrer');
                 // Hide spinner when iframe is considered loaded (this is not always perfect)
                 iframe.onload = () => spinner.classList.remove('loading');
                 expandedPreview.appendChild(iframe);
            }


            function closeExpandedView() {
                 expandedViewContainer.classList.remove('visible');
                 document.body.style.overflow = ''; // Restore scrolling
                 // Optional: Clear content immediately or after transition
                 // expandedPreview.innerHTML = '';
            }

            // Grid Item Clicks
            grid.addEventListener('click', function(e) {
                const card = e.target.closest('.portfolio-card');
                if (card) {
                    const dataElement = card.querySelector('.cheatsheet-data');
                    if (dataElement) {
                        try {
                            const itemData = JSON.parse(dataElement.textContent);
                            showExpandedView(itemData);
                        } catch (err) {
                            console.error("Failed to parse cheatsheet data:", err);
                        }
                    }
                }
            });

            // Close button click
            expandedViewClose.addEventListener('click', closeExpandedView);

             // Click outside the content to close
            expandedViewContainer.addEventListener('click', function(e) {
                 if (e.target === expandedViewContainer) { // Only if clicking the backdrop itself
                     closeExpandedView();
                 }
            });

            // Keyboard accessibility for closing
             expandedViewContainer.addEventListener('keydown', function(e) {
                 if (e.key === 'Escape') {
                     closeExpandedView();
                 }
            });

             // Keyboard accessibility for opening
             grid.addEventListener('keydown', function(e) {
                  const card = e.target.closest('.portfolio-card');
                  if (card && (e.key === 'Enter' || e.key === ' ')) {
                      e.preventDefault(); // Prevent space from scrolling
                      const dataElement = card.querySelector('.cheatsheet-data');
                       if (dataElement) {
                           try {
                               const itemData = JSON.parse(dataElement.textContent);
                               showExpandedView(itemData);
                           } catch (err) { console.error("Failed to parse cheatsheet data:", err); }
                       }
                  }
             });

        });
    </script>

</body>
</html>