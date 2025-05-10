<?php
// Set content type and encoding
header('Content-Type: text/html; charset=utf-8');

// --- Configuration ---
$excludedItems = [
    '.',
    '..',
    'index.php', // Exclude this script itself
    // Add any other specific files or directories to exclude by name:
    // 'old_gallery.html',
    'images',    // Example: Exclude images directory if it's in the root
    'LICENSE',
    'README.md',
    'PROMPT.txt',    
    // Add any other files/directories to exclude by name
];

$cheatsheetDir = '.'; // Current directory where cheatsheet HTML files are located

// --- Base URL Calculation ---
$scheme = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
$host = $_SERVER['HTTP_HOST'];
// Calculate script directory, ensuring it's correct even if index.php is in a subdirectory
$scriptName = $_SERVER['SCRIPT_NAME']; // e.g., /index.php or /path/to/index.php
$scriptDir = dirname($scriptName);
// If script is in root, dirname might return '\' or '.', normalize to empty string for base URL
$scriptDir = ($scriptDir === '.' || $scriptDir === DIRECTORY_SEPARATOR) ? '' : $scriptDir;
$baseUrl = rtrim($scheme . '://' . $host . $scriptDir, '/') . '/';


// --- Helper Function: Extract Metadata ---
function extractMetadata(string $filepath): array {
    global $baseUrl, $scheme, $host; // Access global vars needed for URL construction

    $filename = basename($filepath);
    $metadata = [
        'title' => pathinfo($filename, PATHINFO_FILENAME), // Default title from filename
        'description' => 'Explore this cheatsheet to learn more.', // Default description
        'image' => null, // Default image
        'url' => $baseUrl . $filename, // Construct full URL for the cheatsheet page
        'error' => null
    ];

    // Suppress warnings for potentially malformed HTML and file access issues
    $content = @file_get_contents($filepath);
    if ($content === false) {
        $metadata['error'] = "Could not read file: " . htmlspecialchars($filename);
        return $metadata;
    }

    // Use DOMDocument for robust parsing
    $dom = new DOMDocument();
    // Suppress warnings during loading of potentially invalid HTML
    @$dom->loadHTML('<?xml encoding="utf-8" ?>' . $content, LIBXML_NOERROR | LIBXML_NOWARNING); // Added XML encoding hint
    $xpath = new DOMXPath($dom);

    // Extract Title
    $titleNode = $xpath->query('//title')->item(0);
    if ($titleNode) {
        $metadata['title'] = trim($titleNode->textContent);
    }

    // Extract Meta Description (prefer name="description", fallback to og:description)
    $descNode = $xpath->query('//meta[@name="description"]/@content')->item(0);
    if ($descNode) {
        $metadata['description'] = trim($descNode->nodeValue);
    } else {
        $ogDescNode = $xpath->query('//meta[@property="og:description"]/@content')->item(0);
        if ($ogDescNode) {
            $metadata['description'] = trim($ogDescNode->nodeValue);
        }
    }

    // Extract Open Graph Image and ensure it's an absolute URL
    $imgNode = $xpath->query('//meta[@property="og:image"]/@content')->item(0);
    if ($imgNode) {
        $imageUrl = trim($imgNode->nodeValue);
        if (preg_match('/^https?:\/\//i', $imageUrl)) { // Already absolute
            $metadata['image'] = $imageUrl;
        } elseif (str_starts_with($imageUrl, '/')) { // Root-relative URL (e.g., /images/foo.png)
            $metadata['image'] = $scheme . '://' . $host . $imageUrl;
        } else { // Document-relative URL (e.g., images/foo.png or ../images/foo.png)
                 // This path is relative to the cheatsheet file itself.
                 // Base URL of the cheatsheet: dirname($metadata['url'])
            $baseCheatsheetWebPath = dirname($metadata['url']);
            $resolvedImageUrl = rtrim($baseCheatsheetWebPath, '/') . '/' . $imageUrl;

            // Basic normalization: resolve . and .. segments
            $parts = explode('/', $resolvedImageUrl);
            $absolutes = [];
            foreach ($parts as $part) {
                if ('.' == $part) continue;
                if ('..' == $part) {
                    array_pop($absolutes);
                } else {
                    $absolutes[] = $part;
                }
            }
            // Reconstruct, ensuring "scheme://" is not duplicated if it was part of $baseCheatsheetWebPath
            $finalPath = implode('/', $absolutes);
            if (strpos($finalPath, $scheme . '://') === 0) {
                 $metadata['image'] = $finalPath;
            } else {
                 // This case should ideally not happen if $baseCheatsheetWebPath was correct.
                 // Fallback or reconstruct carefully. For now, assume $scheme needed.
                 // This might occur if $baseCheatsheetWebPath was just a path without scheme/host.
                 // However, $metadata['url'] (and thus $baseCheatsheetWebPath) should be absolute.
                 $urlParts = parse_url($metadata['url']); // $metadata['url'] is the cheatsheet's absolute URL
                 $metadata['image'] = $urlParts['scheme'] . '://' . $urlParts['host'] . (isset($urlParts['port']) ? ':' . $urlParts['port'] : '') . '/' . trim(implode('/', array_slice(explode('/', $finalPath),3)), '/'); // Rebuild from scheme/host + normalized path
            }
             // A simple way to re-assemble if parse_url was used on $resolvedImageUrl
             $parsedResolved = parse_url($resolvedImageUrl);
             if ($parsedResolved && isset($parsedResolved['scheme']) && isset($parsedResolved['host']) && isset($parsedResolved['path'])) {
                $path = $parsedResolved['path'];
                $newPathParts = [];
                $pathSegments = explode('/', $path);
                foreach ($pathSegments as $segment) {
                    if ($segment === '.' || $segment === '') continue;
                    if ($segment === '..') {
                        if (count($newPathParts) > 0) array_pop($newPathParts);
                    } else {
                        $newPathParts[] = $segment;
                    }
                }
                $metadata['image'] = $parsedResolved['scheme'] . '://' . $parsedResolved['host'] . (isset($parsedResolved['port']) ? ':' . $parsedResolved['port'] : '') . '/' . implode('/', $newPathParts);
             } else {
                // Fallback if parse_url failed or basic reconstruction not possible.
                // This might indicate an issue with $resolvedImageUrl formation.
                // For safety, could log an error here.
                $metadata['image'] = $resolvedImageUrl; // Use as is, hoping browser resolves
             }
        }
    }


     // Limit description length for display consistency
    if (mb_strlen($metadata['description']) > 150) { // Use mb_strlen for multi-byte safety
        $metadata['description'] = mb_substr($metadata['description'], 0, 147) . '...'; // Use mb_substr
    }

    return $metadata;
}

// --- Main Logic: Scan Directory and Build Cheatsheet List ---
$cheatsheets = [];
$errors = [];

try {
    $files = scandir($cheatsheetDir);
    if ($files === false) {
        throw new Exception("Could not scan directory: " . htmlspecialchars($cheatsheetDir));
    }

    foreach ($files as $file) {
        $filePath = $cheatsheetDir . '/' . $file;
        // Skip excluded items, non-files, non-readable files, and non-HTML files
        if (in_array($file, $excludedItems, true) || !is_file($filePath) || !is_readable($filePath) || !str_ends_with(strtolower($file), '.html')) {
            continue;
        }
        $meta = extractMetadata($filePath);
        if ($meta['error']) {
            $errors[] = $meta['error'];
        } else {
            $cheatsheets[] = $meta;
        }
    }
    // Optional: Sort cheatsheets alphabetically by title for consistent initial order
    usort($cheatsheets, fn($a, $b) => strcasecmp($a['title'], $b['title']));

} catch (Exception $e) {
    $errors[] = "An error occurred: " . $e->getMessage();
}

// --- HTML Output ---
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧠</text></svg>">
    
    <!-- === Refined SEO & Portfolio Metadata === -->
    <title>David Veksler's Cheatsheet Portfolio | Custom Cheatsheet Design Services</title>
    <meta name="description" content="Explore a portfolio of expertly crafted cheatsheets by David Veksler covering tech, philosophy, AI safety, and more. Hire David to create custom, visually engaging reference guides tailored to your needs.">
    <meta name="keywords" content="cheatsheets, portfolio, custom cheatsheets, information design, technical writing, data visualization, reference guide, programming, tech, philosophy, ai safety, bitcoin, leadership, david veksler, hire, freelance, consultant">
    <meta name="author" content="David Veksler">
    <link rel="canonical" href="<?php echo htmlspecialchars($baseUrl); ?>">

    <!-- === Open Graph / Facebook / LinkedIn === -->
    <meta property="og:title" content="David Veksler's Cheatsheet Portfolio | Custom Design Services">
    <meta property="og:description" content="Showcasing expertise in creating clear, visually appealing, and interactive cheatsheets. Hire David Veksler for custom reference guide design.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="<?php echo htmlspecialchars($baseUrl); ?>">
    <meta property="og:image" content="<?php echo htmlspecialchars(rtrim($baseUrl, '/')); ?>/images/cheatsheets-og-portfolio.png">
    <meta property="og:image:alt" content="David Veksler Cheatsheet Portfolio Showcase">
    <meta property="og:site_name" content="David Veksler's Cheatsheets">
    <meta property="og:locale" content="en_US">

    <!-- === Twitter Card === -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="David Veksler's Cheatsheet Portfolio | Custom Design Services">
    <meta name="twitter:description" content="Showcasing expertise in creating clear, interactive cheatsheets. Hire David Veksler for custom reference guide design.">
    <meta name="twitter:url" content="<?php echo htmlspecialchars($baseUrl); ?>">
    <meta name="twitter:image" content="<?php echo htmlspecialchars(rtrim($baseUrl, '/')); ?>/images/cheatsheets-og-portfolio.png">
    <meta name="twitter:image:alt" content="David Veksler Cheatsheet Portfolio Showcase">
    <meta name="twitter:creator" content="@DavidVeksler">


    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">

    <style>
        :root {
             --card-lift-height: -7px;
             --card-shadow-intensity: rgba(0, 0, 0, .15);
        }
        html {
            scroll-behavior: smooth;
        }
        body {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-color: #f8f9fa;
        }
        .main-content {
            flex: 1;
        }
        .navbar {
             background-image: linear-gradient(to bottom, #343a40, #212529);
        }
        .card {
            transition: transform .25s ease-in-out, box-shadow .25s ease-in-out;
            border: 1px solid #dee2e6;
            border-radius: .375rem;
            overflow: hidden;
            background-color: #fff;
        }
        .card:hover {
            transform: translateY(var(--card-lift-height));
            box-shadow: 0 0.8rem 1.6rem var(--card-shadow-intensity);
        }
        .card-img-top, .iframe-preview-container {
            aspect-ratio: 16 / 9;
            object-fit: cover;
            background-color: #e9ecef;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #adb5bd;
            position: relative; /* Needed for iframe positioning and ::before icon */
        }
         .card-img-top::before, .iframe-preview-container::before {
             font-family: 'bootstrap-icons';
             content: "\F48B"; /* bi-image-alt */
             font-size: 2.5rem;
             display: block;
             position: absolute; /* Center the icon */
             top: 50%;
             left: 50%;
             transform: translate(-50%, -50%);
        }
         .card-img-top[src]:not([src=""])::before, /* Hide icon if img src is valid */
         .iframe-preview-container iframe.loaded::before { /* Hide icon if iframe is loaded */
             display: none;
        }
        /* Ensure iframe content also hides its own ::before if it's an .iframe-preview-container */
         .iframe-preview-container iframe[src]:not([src=""])::before {
            display: none;
         }


        .iframe-preview-container {
            /* position: relative; */ /* Already set above */
            overflow: hidden;
        }
        .iframe-preview-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0;
            background-color: #fff; /* Background for iframe before it loads */
            opacity: 0; /* Start hidden */
            transition: opacity 0.5s ease-in-out;
        }
        .iframe-preview-container iframe.loaded {
             opacity: 1; /* Fade in when loaded */
        }
        .card-title a {
            text-decoration: none;
            color: inherit;
            font-weight: 600;
        }
        .card-title a:hover {
            color: #0d6efd;
            text-decoration: underline;
        }
        .card-body {
            display: flex;
            flex-direction: column;
            padding: 1.25rem;
        }
        .card-text {
             flex-grow: 1;
             margin-bottom: 1.25rem;
             color: #495057;
             font-size: 0.9rem;
             min-height: 60px; /* Ensure consistent card body height */
        }
        .card-footer {
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            padding: 0.75rem 1.25rem;
        }
        .footer {
             background-color: #e9ecef;
             color: #6c757d;
             border-top: 1px solid #ced4da;
        }
        .display-5.fw-bold {
            color: #343a40;
        }
        #filterInput:focus {
            border-color: #86b7fe;
            box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
        }
        .cta-scroll-link {
            font-size: 0.9rem;
            text-decoration: none;
        }
        .cta-scroll-link:hover {
            text-decoration: underline;
        }
        .cta-section-bottom {
            border-top: 1px solid #dee2e6;
            padding-top: 2rem;
            padding-bottom: 1rem;
            margin-top: 3rem;
        }
    </style>
</head>
<body class="d-flex flex-column min-vh-100">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="<?php echo htmlspecialchars($baseUrl); ?>">
                 <i class="bi bi-journal-richtext me-2"></i>David Veksler's Cheatsheet Portfolio
            </a>
        </div>
    </nav>

    <main class="main-content container mt-4 mb-5">
        <header class="text-center mb-5">
            <h1 class="display-5 fw-bold">Cheatsheet Design Showcase</h1>
            <p class="lead text-muted">Explore examples of clear, concise, and interactive reference guides.</p>
            <a href="#custom-cheatsheets" class="cta-scroll-link link-secondary">
                <i class="bi bi-tools me-1"></i>Need a custom cheatsheet?
            </a>
        </header>

        <div class="row mb-4 justify-content-center">
            <div class="col-md-8 col-lg-6">
                <div class="input-group input-group-lg shadow-sm">
                    <span class="input-group-text bg-white border-end-0" id="filter-addon"><i class="bi bi-search text-primary"></i></span>
                    <input type="search" id="filterInput" class="form-control border-start-0" placeholder="Filter cheatsheets by title or topic..." aria-label="Filter cheatsheets" aria-describedby="filter-addon">
                </div>
            </div>
        </div>

        <?php if (!empty($errors)): ?>
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                <h4 class="alert-heading">Notice</h4>
                <p>There were some issues loading details for all cheatsheets:</p>
                <ul>
                    <?php foreach ($errors as $error): ?>
                        <li><?php echo $error; /* Already htmlspecialchars'd in extractMetadata if needed */ ?></li>
                    <?php endforeach; ?>
                </ul>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        <?php endif; ?>

        <?php if (empty($cheatsheets) && empty($errors)): ?>
            <div class="alert alert-info text-center mt-4" role="alert">
                <i class="bi bi-info-circle me-2"></i>No cheatsheet examples found. Check back soon!
            </div>
        <?php endif; ?>

        <div id="cheatsheetGrid" class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
            <?php foreach ($cheatsheets as $sheet): ?>
                <div class="col d-flex align-items-stretch portfolio-item">
                    <div class="card h-100 shadow-sm">
                        <?php if (!empty($sheet['image'])): ?>
                            <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener" aria-label="Preview image for <?php echo htmlspecialchars($sheet['title']); ?>">
                                <img src="<?php echo htmlspecialchars($sheet['image']); ?>" class="card-img-top" alt="Preview for <?php echo htmlspecialchars($sheet['title']); ?>" loading="lazy"
                                     onerror="this.style.display='none'; this.parentElement.nextElementSibling.style.display='block'; this.parentElement.nextElementSibling.querySelector('iframe').classList.add('loaded');">
                            </a>
                            <div class="iframe-preview-container" style="display: none;"> <!-- Initially hidden if image exists -->
                                <iframe src="<?php echo htmlspecialchars($sheet['url']); ?>"
                                        title="Interactive preview of <?php echo htmlspecialchars($sheet['title']); ?>"
                                        loading="lazy"
                                        frameborder="0"
                                        scrolling="no"
                                        referrerpolicy="no-referrer"
                                        onload="this.classList.add('loaded');">
                                </iframe>
                            </div>
                        <?php else: ?>
                            <!-- Fallback: Display iframe preview directly if no image -->
                            <div class="iframe-preview-container">
                                <iframe src="<?php echo htmlspecialchars($sheet['url']); ?>"
                                        title="Interactive preview of <?php echo htmlspecialchars($sheet['title']); ?>"
                                        loading="lazy"
                                        frameborder="0"
                                        scrolling="no"
                                        referrerpolicy="no-referrer"
                                        onload="this.classList.add('loaded');">
                                </iframe>
                            </div>
                        <?php endif; ?>
                        <div class="card-body">
                            <h5 class="card-title">
                                <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener">
                                    <?php echo htmlspecialchars($sheet['title']); ?>
                                </a>
                            </h5>
                            <p class="card-text text-muted small">
                                <?php echo htmlspecialchars($sheet['description']); ?>
                            </p>
                        </div>
                        <div class="card-footer text-center">
                            <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary">
                                View Cheatsheet <i class="bi bi-box-arrow-up-right ms-1"></i>
                            </a>
                        </div>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>

        <div id="noResults" class="alert alert-warning text-center mt-4 d-none" role="alert">
            <i class="bi bi-emoji-frown me-2"></i>No cheatsheets match your filter criteria. Try broadening your search.
        </div>

         <section id="custom-cheatsheets" class="cta-section-bottom text-center">
              <h3 class="h4 fw-normal mb-3">Need a Custom Cheatsheet?</h3>
              <p class="text-muted mb-3 mx-auto" style="max-width: 600px;">I can help design professional, tailored cheatsheets for your specific needs – documentation, training, marketing, and more.</p>
              <a href="https://www.linkedin.com/in/davidveksler/" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary btn-sm">
                  <i class="bi bi-linkedin me-1"></i> Discuss Your Project on LinkedIn
              </a>
          </section>
    </main>

    <footer class="footer py-4 mt-auto border-top bg-light">
        <div class="container text-center">
            <p class="mb-2 text-muted">
                Cheatsheet Portfolio & Design by David Veksler © <?php echo date("Y"); ?>
            </p>
            <div>
              <a href="https://www.linkedin.com/in/davidveksler/" title="David Veksler on LinkedIn" target="_blank" rel="noopener noreferrer" class="mx-2 link-secondary">
                <i class="bi bi-linkedin"></i> LinkedIn Profile
              </a>
              <span class="text-muted mx-1">|</span>
              <a href="<?php echo htmlspecialchars($baseUrl); ?>" title="Browse All Cheatsheets" class="mx-2 link-secondary">
                <i class="bi bi-collection"></i> View All Examples
              </a>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const filterInput = document.getElementById('filterInput');
            const grid = document.getElementById('cheatsheetGrid');
            const noResultsMessage = document.getElementById('noResults');
            // Get items only if grid exists
            const items = grid ? grid.querySelectorAll('.portfolio-item') : [];


            if (!filterInput || !grid || items.length === 0) {
                if(filterInput) filterInput.disabled = true;
                // If no items at all (e.g. $cheatsheets was empty), don't show "no results" from filter.
                // The PHP part will show a "No cheatsheet examples found" message.
                // So, we only want the filter's "noResults" message if there were items to begin with.
                if (items.length > 0 && noResultsMessage) noResultsMessage.classList.add('d-none');
                return;
            }

            filterInput.addEventListener('input', function() {
                const filterText = filterInput.value.toLowerCase().trim();
                let itemsVisible = 0;

                items.forEach(item => {
                    const card = item.querySelector('.card');
                    if (!card) return;

                    const titleElement = card.querySelector('.card-title a');
                    const descriptionElement = card.querySelector('.card-text');

                    const title = titleElement ? titleElement.textContent.toLowerCase() : '';
                    const description = descriptionElement ? descriptionElement.textContent.toLowerCase() : '';
                    const isVisible = filterText === '' || title.includes(filterText) || description.includes(filterText);

                    if (isVisible) {
                        item.classList.remove('d-none'); // Ensure item is displayed
                        itemsVisible++;
                    } else {
                        item.classList.add('d-none'); // Hide item
                    }
                });

                if (noResultsMessage) {
                    if (itemsVisible === 0 && filterText !== '') {
                        noResultsMessage.classList.remove('d-none');
                    } else {
                        noResultsMessage.classList.add('d-none');
                    }
                }
            });

            // Ensure iframes in initially hidden containers load correctly when revealed by image error
            document.querySelectorAll('img.card-img-top').forEach(img => {
                img.addEventListener('error', function() {
                    const iframeContainer = this.parentElement.nextElementSibling;
                    if (iframeContainer && iframeContainer.classList.contains('iframe-preview-container')) {
                        const iframe = iframeContainer.querySelector('iframe');
                        // Force load or ensure visibility triggers load - modern browsers are usually good
                        // but explicitly adding 'loaded' ensures CSS transition if needed.
                        if (iframe) iframe.classList.add('loaded');
                    }
                });
            });
        });
    </script>
</body>
</html>