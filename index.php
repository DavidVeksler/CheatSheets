<?php
// Set content type and encoding
header('Content-Type: text/html; charset=utf-8');

// --- Configuration ---
$excludedItems = [
    '.',
    '..',
    'index.php', // Exclude this script itself
    'images',    // Exclude images directory if it's in the root
    'LICENSE',
    'README.md',
    'PROMPT.txt', // Assuming this was part of your dev files
    // Add any other specific files or directories to exclude by name:
    // 'old_gallery.html',    
];

$cheatsheetDir = '.'; // Current directory where cheatsheet HTML files are located

// --- Base URL Calculation ---
$scheme = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
$host = $_SERVER['HTTP_HOST'];
$scriptName = $_SERVER['SCRIPT_NAME'];
$scriptDir = dirname($scriptName);
$scriptDir = ($scriptDir === '.' || $scriptDir === DIRECTORY_SEPARATOR) ? '' : $scriptDir;
$baseUrl = rtrim($scheme . '://' . $host . $scriptDir, '/') . '/';


// --- Helper Function: Extract Metadata ---
function extractMetadata(string $filepath): array {
    global $baseUrl, $scheme, $host; // Access global vars

    $filename = basename($filepath);
    $defaultTitle = preg_replace('/\.html$/i', '', $filename); // Remove .html extension
    $defaultTitle = ucwords(str_replace(['-', '_'], ' ', $defaultTitle)); // Capitalize and replace hyphens/underscores

    $metadata = [
        'title' => $defaultTitle,
        'description' => 'Explore this ' . htmlspecialchars($defaultTitle) . ' cheatsheet for a concise overview of key concepts.',
        'image' => null,
        'url' => $baseUrl . $filename,
        'error' => null
    ];

    $content = @file_get_contents($filepath);
    if ($content === false) {
        $metadata['error'] = "Could not read file: " . htmlspecialchars($filename);
        return $metadata;
    }

    $dom = new DOMDocument();
    // Suppress warnings during loading of potentially invalid HTML, and add XML encoding hint for better parsing
    @$dom->loadHTML('<?xml encoding="utf-8" ?>' . $content, LIBXML_NOERROR | LIBXML_NOWARNING);
    $xpath = new DOMXPath($dom);

    $titleNode = $xpath->query('//title')->item(0);
    if ($titleNode) {
        $metadata['title'] = trim($titleNode->textContent);
    }

    $descNode = $xpath->query('//meta[@name="description"]/@content')->item(0);
    if ($descNode) {
        $metadata['description'] = trim($descNode->nodeValue);
    } else {
        $ogDescNode = $xpath->query('//meta[@property="og:description"]/@content')->item(0);
        if ($ogDescNode) {
            $metadata['description'] = trim($ogDescNode->nodeValue);
        }
    }

    $imgNode = $xpath->query('//meta[@property="og:image"]/@content')->item(0);
    if ($imgNode) {
        $imageUrl = trim($imgNode->nodeValue);
        if (preg_match('/^https?:\/\//i', $imageUrl)) { // Absolute URL
            $metadata['image'] = $imageUrl;
        } elseif (str_starts_with($imageUrl, '/')) { // Root-relative URL
            $metadata['image'] = $scheme . '://' . $host . $imageUrl;
        } else { // Relative URL to the cheatsheet's path
            $baseCheatsheetWebPath = dirname($metadata['url']);
            $resolvedImageUrl = rtrim($baseCheatsheetWebPath, '/') . '/' . $imageUrl;

            // Normalize path (e.g., /path/../image.png to /image.png)
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
                $finalPath = '/' . implode('/', $newPathParts);
                 // Correct for cases like /../ resolving to root
                if (empty($newPathParts) && str_starts_with($path, '/')) {
                    $finalPath = '/';
                }

                $metadata['image'] = $parsedResolved['scheme'] . '://' . $parsedResolved['host'] .
                                     (isset($parsedResolved['port']) ? ':' . $parsedResolved['port'] : '') .
                                     $finalPath;
            } else {
                $metadata['image'] = $resolvedImageUrl; // Fallback if parsing or normalization fails
            }
        }
    }

    // Ensure description isn't excessively long for the card display
    if (mb_strlen($metadata['description']) > 150) {
        $metadata['description'] = mb_substr($metadata['description'], 0, 147) . '...';
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
        $filePath = rtrim($cheatsheetDir, '/') . '/' . $file;
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

    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧠</text></svg>">
    
    <!-- === SEO & Portfolio Metadata === -->
    <title>David Veksler's Cheatsheet Portfolio | Custom Cheatsheet Design Services</title>
    <meta name="description" content="Explore a portfolio of expertly crafted cheatsheets by David Veksler covering tech, philosophy, AI safety, and more. Hire David to create custom, visually engaging reference guides tailored to your needs.">
    <meta name="keywords" content="cheatsheets, portfolio, custom cheatsheets, information design, technical writing, data visualization, reference guide, programming, tech, philosophy, ai safety, bitcoin, leadership, david veksler, hire, freelance, consultant, interactive, learning, development, web design">
    <meta name="author" content="David Veksler">
    <link rel="canonical" href="<?php echo htmlspecialchars($baseUrl); ?>">

    <!-- === Open Graph / Facebook / LinkedIn === -->
    <meta property="og:title" content="David Veksler's Cheatsheet Portfolio | Custom Design Services">
    <meta property="og:description" content="Showcasing expertise in creating clear, visually appealing, and interactive cheatsheets. Hire David Veksler for custom reference guide design.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="<?php echo htmlspecialchars($baseUrl); ?>">
    <meta property="og:image" content="<?php echo htmlspecialchars(rtrim($baseUrl, '/')); ?>/images/cheatsheets-og-portfolio.png">
    <meta property="og:image:alt" content="A collage showcasing various cheatsheets from David Veksler's portfolio against a clean background.">
    <meta property="og:site_name" content="David Veksler's Cheatsheets">
    <meta property="og:locale" content="en_US">

    <!-- === Twitter Card === -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="David Veksler's Cheatsheet Portfolio | Custom Design Services">
    <meta name="twitter:description" content="Showcasing expertise in creating clear, interactive cheatsheets. Hire David Veksler for custom reference guide design.">
    <meta name="twitter:url" content="<?php echo htmlspecialchars($baseUrl); ?>">
    <meta name="twitter:image" content="<?php echo htmlspecialchars(rtrim($baseUrl, '/')); ?>/images/cheatsheets-og-portfolio.png">
    <meta name="twitter:image:alt" content="A collage showcasing various cheatsheets from David Veksler's portfolio.">
    <!-- <meta name="twitter:creator" content="@YourTwitterHandle"> --> <!-- Uncomment if David Veksler has a relevant Twitter handle -->

    <!-- Schema.org Markup for CollectionPage -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      "name": "David Veksler's Cheatsheet Portfolio | Custom Cheatsheet Design Services",
      "description": "A curated collection of cheatsheets designed by David Veksler, showcasing expertise in information design and technical communication. Available for custom cheatsheet creation projects.",
      "url": "<?php echo htmlspecialchars($baseUrl); ?>",
      "author": {
        "@type": "Person",
        "name": "David Veksler",
        "url": "https://www.linkedin.com/in/davidveksler/"
      },
      "publisher": {
        "@type": "Person", 
        "name": "David Veksler",
        "url": "https://www.linkedin.com/in/davidveksler/"
      },
      "mainEntity": {
        "@type": "ItemList",
        "itemListElement": [
          <?php foreach ($cheatsheets as $index => $sheet): ?>
          {
            "@type": "ListItem",
            "position": <?php echo $index + 1; ?>,
            "item": {
              "@type": "CreativeWork",
              "name": "<?php echo htmlspecialchars($sheet['title']); ?>",
              "url": "<?php echo htmlspecialchars($sheet['url']); ?>",
              "description": "<?php echo htmlspecialchars($sheet['description']); ?>"
              <?php if (!empty($sheet['image'])): ?>
              ,"image": "<?php echo htmlspecialchars($sheet['image']); ?>"
              <?php endif; ?>
            }
          }<?php if ($index < count($cheatsheets) - 1) echo ','; ?>
          <?php endforeach; ?>
        ]
      }
    }
    </script>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">

    <style>
        :root {
             --card-lift-height: -5px; /* Slightly more subtle lift */
             --card-shadow-intensity: rgba(0, 0, 0, .1); /* Softer shadow */
        }
        html { scroll-behavior: smooth; }
        body { display: flex; flex-direction: column; min-height: 100vh; background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }
        .main-content { flex: 1; }
        .navbar { background-image: linear-gradient(to bottom, #343a40, #2c3034); } /* Darker, less contrast gradient */
        .navbar-brand { font-weight: 500; color: #f8f9fa !important; }
        .card {
            transition: transform .15s ease-out, box-shadow .15s ease-out; /* Quicker, smoother transition */
            border: 1px solid #dee2e6; border-radius: .3rem; overflow: hidden; background-color: #fff; display: flex; flex-direction: column;
        }
        .card:hover { transform: translateY(var(--card-lift-height)); box-shadow: 0 0.5rem 1rem var(--card-shadow-intensity); }
        .card-img-top-container { /* New container for fixed aspect ratio */
            aspect-ratio: 16 / 9;
            width: 100%;
            overflow: hidden;
            background-color: #e9ecef;
            border-bottom: 1px solid #dee2e6;
            position: relative; /* For ::before pseudo-element */
            display: flex; align-items: center; justify-content: center;
        }
        .card-img-top-container::before { /* Placeholder icon, improved */
             font-family: 'bootstrap-icons'; content: "\F31F"; /* bi-card-image or F48B bi-image-alt */
             font-size: 3rem; color: #adb5bd; position: absolute;
        }
        .card-img-top-container img {
            width: 100%; height: 100%; object-fit: cover; display: block;
        }
        .card-img-top-container img[src]:not([src=""]):not(.error) { /* Hide icon if img src is valid and not errored */
             position: relative; /* To ensure it covers the ::before */
             z-index: 1;
        }
        .card-img-top-container img[src]:not([src=""]):not(.error) + ::before,
        .card-img-top-container img.error + ::before {
            display: block; /* Show icon if image errors */
        }
        .card-img-top-container img:not(.error)::before {
             display:none; /* Hide icon if image loaded */
        }
        .iframe-preview-container { /* Used when image fails or is not primary */
            aspect-ratio: 16 / 9; width: 100%; position: relative; display: flex; align-items: center; justify-content: center;
            background-color: #e9ecef; border-bottom: 1px solid #dee2e6; color: #adb5bd;
        }
        .iframe-preview-container::before { /* Placeholder icon for iframe */
             font-family: 'bootstrap-icons'; content: "\F423"; /* bi-window-fullscreen or similar */
             font-size: 2.5rem; display: block; position: absolute; top: 50%; left: 50%;
             transform: translate(-50%, -50%);
        }
        .iframe-preview-container iframe {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            border: 0; background-color: #fff; opacity: 0;
            transition: opacity 0.4s ease-in-out .1s; /* Slight delay for smoother visual */
        }
        .iframe-preview-container iframe.loaded { opacity: 1; z-index: 2; /* Ensure iframe is above ::before when loaded */ }
        .iframe-preview-container iframe.loaded + ::before { display: none; } /* Hide icon when iframe loaded */

        .card-title a { text-decoration: none; color: #1a508b; font-weight: 600; } /* Darker blue */
        .card-title a:hover { color: #003d73; text-decoration: underline; }

        /* --- UPDATED CARD TEXT AND TITLE STYLES --- */
        .card-title { /* Affects the <h5> element used for titles */
            /* Original Bootstrap H5 styles: font-size: 1.25rem; margin-bottom: .5rem; (line-height approx 1.2) */
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 2; /* Allow up to 2 lines for the title */
            overflow: hidden;
            text-overflow: ellipsis;
            /* If you want to enforce exact height for the title area:
               height: calc(1.25rem * 1.2 * 2); /* Assumes Bootstrap's h5 font-size and typical line-height */
            */
        }

        .card-body {
            flex-grow: 1; /* This is critical for allowing card-body to take up space */
            display: flex;
            flex-direction: column;
            padding: 1rem; /* Keep padding as is */
        }

        .card-text {
            /* Original styles from your code:
            flex-grow: 1;
            margin-bottom: .8rem;
            color: #495057;
            font-size: 0.875rem;
            line-height: 1.5;
            min-height: calc(0.875rem * 1.5 * 3); /* Approx 3 lines */
            */
            flex-grow: 1; /* Allows description to take available space in card-body */
            margin-bottom: .8rem; /* Original margin */
            color: #495057; /* Original color */
            font-size: 0.875rem; /* Original font-size */
            line-height: 1.5; /* Original line-height, important for min-height calculation */
            min-height: calc(0.875rem * 1.5 * 3); /* Reserve space for 3 lines */

            /* Add line clamping for description */
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 3; /* Allow up to 3 lines for the description */
            overflow: hidden;
            text-overflow: ellipsis;
            /* Fallback max-height for browsers not supporting -webkit-line-clamp (rare)
               max-height: calc(0.875rem * 1.5 * 3 + 0.1rem); /* +0.1rem for buffer */
            */
        }
        /* --- END UPDATED CARD TEXT AND TITLE STYLES --- */


        .card-footer {
            background-color:transparent;
            border-top: 1px solid #e9ecef;
            padding: 0.75rem 1rem;
            text-align:center;
            margin-top: auto; /* This is critical for pushing footer to bottom */
        }
        .footer { background-color: #343a40; color: #adb5bd; border-top: 1px solid #495057; }
        .footer a { color: #f8f9fa; } .footer a:hover { color: #ced4da; }
        .page-hero { padding: 3rem 0; margin-bottom: 2rem; background-color: #e9ecef; border-bottom: 1px solid #dee2e6;}
        .page-hero h1 { color: #212529; font-weight: 600;}
        .page-hero .lead { color: #495057; font-size: 1.1rem; margin-bottom: 1.25rem;}
        #filterInput { border-radius: .25rem; font-size: 1rem; padding: .6rem 1rem; }
        #filterInput:focus { border-color: #86b7fe; box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25); }
        .cta-scroll-link { font-size: 0.9rem; text-decoration: none; color: #0056b3; font-weight:500; }
        .cta-scroll-link:hover { text-decoration: underline; }
        .cta-section { background-color: #ffffff; border-top: 1px solid #dee2e6; border-bottom: 1px solid #dee2e6; padding: 3rem 0; margin: 3rem 0;}
        .cta-section h3 {font-weight: 600; color: #212529;}
        .portfolio-item .card {
            height: 100%; /* This is critical for making cards in a row the same height */
        }
    </style>    
</head>
<body class="d-flex flex-column min-vh-100">
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="<?php echo htmlspecialchars($baseUrl); ?>">
                 <i class="bi bi-journal-richtext me-2"></i>David Veksler's Cheatsheet Portfolio
            </a>
        </div>
    </nav>

    <main class="main-content">
        <header class="page-hero text-center">
            <div class="container">
                <h1 class="display-5">Cheatsheet Design Showcase</h1>
                <p class="lead">Explore examples of clear, concise, and interactive reference guides meticulously crafted by David Veksler.</p>
                <a href="#custom-cheatsheet-cta" class="cta-scroll-link">
                    <i class="bi bi-tools me-1"></i>Need Custom Cheatsheet Design Services? Let's Talk!
                </a>
            </div>
        </header>

        <div class="container mt-4 mb-5">
            <div class="row mb-4 justify-content-center">
                <div class="col-md-8 col-lg-6">
                    <div class="input-group input-group-lg shadow-sm">
                        <span class="input-group-text bg-white border-end-0 text-primary" id="filter-addon"><i class="bi bi-search"></i></span>
                        <input type="search" id="filterInput" class="form-control border-start-0" placeholder="Filter by title or topic (e.g., Buddhism, Python)..." aria-label="Filter cheatsheets" aria-describedby="filter-addon">
                    </div>
                </div>
            </div>

            <?php if (!empty($errors)): ?>
                <div class="alert alert-warning alert-dismissible fade show" role="alert">
                    <h4 class="alert-heading"><i class="bi bi-exclamation-triangle-fill me-2"></i>Notice</h4>
                    <p>There were some issues loading details for all cheatsheets:</p>
                    <ul class="mb-0">
                        <?php foreach ($errors as $error): ?>
                            <li><?php echo $error; ?></li>
                        <?php endforeach; ?>
                    </ul>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            <?php endif; ?>

            <?php if (empty($cheatsheets) && empty($errors)): ?>
                <div class="alert alert-info text-center mt-4 py-4" role="alert">
                    <i class="bi bi-info-circle-fill me-2 fs-4 align-middle"></i>No cheatsheet examples found. Please check back soon for updates!
                </div>
            <?php endif; ?>

            <div id="cheatsheetGrid" class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
                <?php foreach ($cheatsheets as $sheet): ?>
                    <div class="col portfolio-item">
                        <article class="card shadow-sm">
                            <?php if (!empty($sheet['image'])): ?>
                                <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener" class="card-img-top-container" aria-label="Preview image for <?php echo htmlspecialchars($sheet['title']); ?>">
                                    <img src="<?php echo htmlspecialchars($sheet['image']); ?>" alt="Preview for <?php echo htmlspecialchars($sheet['title']); ?>" loading="lazy"
                                         onerror="this.classList.add('error'); this.style.display='none'; this.closest('.card').querySelector('.iframe-preview-container').style.display='flex';">
                                </a>
                                <div class="iframe-preview-container" style="display: none;"> <!-- Initially hidden if image exists and loads -->
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
                                <div class="iframe-preview-container" style="display: flex;"> <!-- Display flex to show ::before icon as no image provided -->
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
                                <p class="card-text">
                                    <?php echo htmlspecialchars($sheet['description']); ?>
                                </p>
                            </div>
                            <div class="card-footer">
                                <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary w-100">
                                    View Cheatsheet <i class="bi bi-box-arrow-up-right ms-1"></i>
                                </a>
                            </div>
                        </article>
                    </div>
                <?php endforeach; ?>
            </div>

            <div id="noResults" class="alert alert-warning text-center mt-4 py-3 d-none" role="alert">
                <i class="bi bi-emoji-frown me-2"></i>No cheatsheets match your filter. Try a different term.
            </div>
        </div>
    </main>

    <section id="custom-cheatsheet-cta" class="cta-section text-center">
        <div class="container">
              <h3 class="mb-3">Need a Custom-Designed Cheatsheet?</h3>
              <p class="text-muted mb-4 mx-auto" style="max-width: 700px;">
                  Leverage David Veksler's expertise to get professional, engaging, and easy-to-understand cheatsheets tailored for your specific needs — perfect for technical documentation, educational material, marketing content, or internal training programs.
              </p>
              <a href="https://www.linkedin.com/in/davidveksler/" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-lg px-4 py-3">
                  <i class="bi bi-linkedin me-2"></i>Discuss Your Project on LinkedIn
              </a>
        </div>
    </section>

    <footer class="footer py-4 mt-auto">
        <div class="container text-center">
            <p class="mb-2 small">
                Cheatsheet Portfolio © <?php echo date("Y"); ?> David Veksler. All rights reserved.
            </p>
            <div>
              <a href="https://www.linkedin.com/in/davidveksler/" title="David Veksler on LinkedIn" target="_blank" rel="noopener noreferrer" class="mx-2 small">
                <i class="bi bi-linkedin"></i> LinkedIn
              </a>
              <span class="mx-1 small">|</span>
              <a href="<?php echo htmlspecialchars($baseUrl); ?>" title="Browse All Cheatsheet Examples" class="mx-2 small">
                <i class="bi bi-collection-fill"></i> View All Examples
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
        const items = grid ? Array.from(grid.querySelectorAll('.portfolio-item')) : [];

        if (filterInput && grid && items.length > 0) {
            filterInput.addEventListener('input', function() {
                const filterText = filterInput.value.toLowerCase().trim();
                let itemsVisible = 0;

                items.forEach(item => {
                    const titleElement = item.querySelector('.card-title a');
                    const descriptionElement = item.querySelector('.card-text');
                    const title = titleElement ? titleElement.textContent.toLowerCase() : '';
                    const description = descriptionElement ? descriptionElement.textContent.toLowerCase() : '';
                    
                    const isVisible = filterText === '' || title.includes(filterText) || description.includes(filterText);

                    if (isVisible) {
                        item.style.display = ''; 
                        itemsVisible++;
                    } else {
                        item.style.display = 'none';
                    }
                });
                noResultsMessage.classList.toggle('d-none', itemsVisible > 0 || filterText === '');
            });
        } else if (filterInput) {
             filterInput.disabled = true; 
             filterInput.placeholder = "No cheatsheets available to filter.";
        }

        // Enhanced image error handling for images within card-img-top-container
        document.querySelectorAll('.card-img-top-container img').forEach(img => {
            img.addEventListener('error', function() {
                this.classList.add('error'); // Mark as errored
                this.style.display = 'none'; // Hide broken image
                const card = this.closest('.card');
                if (card) {
                    const iframeContainer = card.querySelector('.iframe-preview-container');
                    if (iframeContainer) {
                        iframeContainer.style.display = 'flex'; // Show iframe container
                    }
                }
            });
             // If image loads, but was previously hidden by error fallback, ensure it's shown
            img.addEventListener('load', function() {
                if (!this.classList.contains('error')) { // Only if it didn't error before
                    this.style.display = 'block';
                    const card = this.closest('.card');
                     if (card) {
                        const iframeContainer = card.querySelector('.iframe-preview-container');
                        // If an image loads successfully, we might want to hide the iframe container if it was only a fallback
                        // This depends on the desired logic: always show image if available, or primary iframe?
                        // The current setup implies image is primary if present.
                        // if (iframeContainer && this.src && this.src !== '') {
                        //    iframeContainer.style.display = 'none';
                        // }
                    }
                }
            });
        });
    });
    </script>
</body>
</html>