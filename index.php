<?php
// Set content type and encoding
header('Content-Type: text/html; charset=utf-8');

// --- Configuration ---
$excludedItems = [
    '.',
    '..',
    'index.php', // Exclude this script itself
    'browse.html', // Exclude the old static page
    'images',    // Exclude directories
    'LICENSE',
    'README.md',
    'PROMPT.txt',
    'history_tree_style.css',
    'safety_data.js',
    // Add any other files/directories to exclude by name
];

$cheatsheetDir = '.'; // Current directory
// More robust base URL calculation
$scheme = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
$host = $_SERVER['HTTP_HOST'];
$scriptDir = dirname($_SERVER['SCRIPT_NAME']);
// Ensure base URL ends with a slash
$baseUrl = rtrim($scheme . '://' . $host . $scriptDir, '/') . '/';


// --- Helper Function: Extract Metadata ---
function extractMetadata(string $filepath): array {
    global $baseUrl, $scheme, $host; // Access global vars needed

    $filename = basename($filepath);
    $metadata = [
        'title' => pathinfo($filename, PATHINFO_FILENAME), // Default title
        'description' => 'Explore this cheatsheet to learn more.', // Default description
        'image' => null, // Default image
        'url' => $baseUrl . $filename, // Construct full URL
        'error' => null
    ];

    // Suppress warnings for potentially malformed HTML and file access issues
    $content = @file_get_contents($filepath);
    if ($content === false) {
        $metadata['error'] = "Could not read file: " . $filename;
        return $metadata;
    }

    // Use DOMDocument for robust parsing
    $dom = new DOMDocument();
    // Suppress warnings during loading of potentially invalid HTML
    @$dom->loadHTML($content, LIBXML_NOERROR | LIBXML_NOWARNING);
    $xpath = new DOMXPath($dom);

    // Extract Title
    $titleNode = $xpath->query('//title')->item(0);
    if ($titleNode) {
        $metadata['title'] = trim($titleNode->textContent);
    }

    // Extract Meta Description
    $descNode = $xpath->query('//meta[@name="description"]/@content')->item(0);
    if ($descNode) {
        $metadata['description'] = trim($descNode->nodeValue);
    } else {
        // Fallback to OG description
        $ogDescNode = $xpath->query('//meta[@property="og:description"]/@content')->item(0);
        if ($ogDescNode) {
            $metadata['description'] = trim($ogDescNode->nodeValue);
        }
    }

    // Extract Open Graph Image
    $imgNode = $xpath->query('//meta[@property="og:image"]/@content')->item(0);
    if ($imgNode) {
        $imageUrl = trim($imgNode->nodeValue);
         // Check if the image URL is absolute or relative
        if (!preg_match('/^https?:\/\//i', $imageUrl)) {
             // Handle root-relative (starts with /) or file-relative paths
             if (str_starts_with($imageUrl, '/')) {
                 // Root relative - combine scheme, host, and path
                 $metadata['image'] = $scheme . '://' . $host . $imageUrl;
             } else {
                  // Relative path - combine base URL path and image URL
                 $absoluteImagePath = realpath(dirname(__FILE__)) . '/' . $imageUrl;
                 if (file_exists($absoluteImagePath)) {
                    $metadata['image'] = $baseUrl . $imageUrl;
                 } else {
                     error_log("Relative image path specified in " . $filename . " not found: " . $imageUrl . " (Base URL: " . $baseUrl . ")");
                     // Keep image as null if local file doesn't exist
                 }
             }
        } else {
             // It's an absolute URL, use as is
            $metadata['image'] = $imageUrl;
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
        throw new Exception("Could not scan directory: " . $cheatsheetDir);
    }

    foreach ($files as $file) {
        $filePath = $cheatsheetDir . '/' . $file;
        // Skip excluded items and non-files/non-readable files
        if (in_array($file, $excludedItems, true) || !is_file($filePath) || !is_readable($filePath)) {
            continue;
        }

        // Only process .html files
        if (str_ends_with(strtolower($file), '.html')) {
            $meta = extractMetadata($filePath);
            if ($meta['error']) {
                $errors[] = $meta['error'];
            } else {
                $cheatsheets[] = $meta;
            }
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
    <meta property="og:image" content="<?php echo htmlspecialchars($baseUrl); ?>images/cheatsheets-og-portfolio.png"> <!-- Suggest creating a specific OG image for the portfolio page -->
    <meta property="og:image:alt" content="David Veksler Cheatsheet Portfolio Showcase">
    <meta property="og:site_name" content="David Veksler's Cheatsheets">
    <meta property="og:locale" content="en_US">

    <!-- === Twitter Card === -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="David Veksler's Cheatsheet Portfolio | Custom Design Services">
    <meta name="twitter:description" content="Showcasing expertise in creating clear, interactive cheatsheets. Hire David Veksler for custom reference guide design.">
    <meta name="twitter:url" content="<?php echo htmlspecialchars($baseUrl); ?>">
    <meta name="twitter:image" content="<?php echo htmlspecialchars($baseUrl); ?>images/cheatsheets-og-portfolio.png"> <!-- Use the same portfolio OG image -->
    <meta name="twitter:image:alt" content="David Veksler Cheatsheet Portfolio Showcase">
    <meta name="twitter:creator" content="@DavidVeksler"> <!-- Add if you have a relevant handle -->


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
            scroll-behavior: smooth; /* Enable smooth scrolling for anchor links */
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
        }
         .card-img-top::before, .iframe-preview-container::before {
             font-family: 'bootstrap-icons';
             content: "\F48B"; /* bi-image-alt */
             font-size: 2.5rem;
             display: block;
        }
         .card-img-top[src]:not([src=""])::before,
         .iframe-preview-container iframe[src]:not([src=""])::before {
             display: none;
        }
         .iframe-preview-container iframe::before {
             display: block;
         }
         .iframe-preview-container iframe.loaded::before {
              display: none;
         }

        .iframe-preview-container {
            position: relative;
            overflow: hidden;
        }
        .iframe-preview-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0;
            background-color: #fff;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
        }
        .iframe-preview-container iframe.loaded {
             opacity: 1;
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
             min-height: 60px;
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
        /* Subtle link style for scrolling to CTA */
        .cta-scroll-link {
            font-size: 0.9rem;
            text-decoration: none;
        }
        .cta-scroll-link:hover {
            text-decoration: underline;
        }
        /* More subtle CTA Section */
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
            <!-- Navbar toggler if needed -->
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

        <!-- === Filter Input === -->
        <div class="row mb-4 justify-content-center">
            <div class="col-md-8 col-lg-6">
                <div class="input-group input-group-lg shadow-sm">
                    <span class="input-group-text bg-white border-end-0" id="filter-addon"><i class="bi bi-search text-primary"></i></span>
                    <input type="search" id="filterInput" class="form-control border-start-0" placeholder="Filter cheatsheets by title or topic..." aria-label="Filter cheatsheets" aria-describedby="filter-addon">
                </div>
            </div>
        </div>

        <!-- Error Display -->
        <?php if (!empty($errors)): ?>
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                <h4 class="alert-heading">Notice</h4>
                <p>There were some issues loading details for all cheatsheets:</p>
                <ul>
                    <?php foreach ($errors as $error): ?>
                        <li><?php echo htmlspecialchars($error); ?></li>
                    <?php endforeach; ?>
                </ul>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        <?php endif; ?>

        <!-- No Cheatsheets Message -->
        <?php if (empty($cheatsheets) && empty($errors)): ?>
            <div class="alert alert-info text-center" role="alert">
                <i class="bi bi-info-circle me-2"></i>No cheatsheet examples found in this directory.
            </div>
        <?php endif; ?>

        <!-- Cheatsheet Grid -->
        <div id="cheatsheetGrid" class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
            <?php if (!empty($cheatsheets)): ?>
                <?php foreach ($cheatsheets as $sheet): ?>
                    <div class="col d-flex align-items-stretch portfolio-item">
                        <div class="card h-100 shadow-sm">
                            <?php if (!empty($sheet['image'])): ?>
                                <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener" aria-label="Preview image for <?php echo htmlspecialchars($sheet['title']); ?>">
                                    <img src="<?php echo htmlspecialchars($sheet['image']); ?>" class="card-img-top" alt="Preview for <?php echo htmlspecialchars($sheet['title']); ?>" loading="lazy" onerror="this.style.display='none'; this.parentElement.nextElementSibling.style.display='block';">
                                </a>
                                <div class="iframe-preview-container" style="display: none;">
                                    <iframe src="<?php echo htmlspecialchars($sheet['url']); ?>"
                                            title="Preview of <?php echo htmlspecialchars($sheet['title']); ?>"
                                            loading="lazy"
                                            frameborder="0"
                                            scrolling="no"
                                            referrerpolicy="no-referrer"
                                            onload="this.classList.add('loaded');"
                                            >
                                    </iframe>
                                </div>
                            <?php else: ?>
                                <!-- Fallback: Display iframe preview -->
                                <div class="iframe-preview-container">
                                    <iframe src="<?php echo htmlspecialchars($sheet['url']); ?>"
                                            title="Preview of <?php echo htmlspecialchars($sheet['title']); ?>"
                                            loading="lazy"
                                            frameborder="0"
                                            scrolling="no"
                                            referrerpolicy="no-referrer"
                                            onload="this.classList.add('loaded');"
                                            >
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
            <?php endif; ?>
        </div>

         <!-- No Results Message for Filtering -->
        <div id="noResults" class="alert alert-warning text-center mt-4 d-none" role="alert">
            <i class="bi bi-emoji-frown me-2"></i>No cheatsheets match your filter criteria. Try broadening your search.
        </div>

         <!-- === Call to Action Section (Moved to Bottom) === -->
         <section id="custom-cheatsheets" class="cta-section-bottom text-center">
              <h3 class="h4 fw-normal mb-3">Need a Custom Cheatsheet?</h3>
              <p class="text-muted mb-3 mx-auto" style="max-width: 600px;">I can help design professional, tailored cheatsheets for your specific needs – documentation, training, marketing, and more.</p>
              <a href="https://www.linkedin.com/in/davidveksler/" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary btn-sm">
                  <i class="bi bi-linkedin me-1"></i> Discuss Your Project on LinkedIn
              </a>
          </section>

    </main>

    <!-- Updated Footer -->
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

    <!-- Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>

    <!-- Custom JS for Filtering -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const filterInput = document.getElementById('filterInput');
            const grid = document.getElementById('cheatsheetGrid');
            const items = grid.querySelectorAll('.portfolio-item');
            const noResultsMessage = document.getElementById('noResults');

            if (!filterInput || !grid || items.length === 0) {
                if(filterInput) filterInput.disabled = true;
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
                        item.classList.remove('d-none');
                        itemsVisible++;
                    } else {
                        item.classList.add('d-none');
                    }
                });

                if (itemsVisible === 0 && filterText !== '') {
                    noResultsMessage.classList.remove('d-none');
                } else {
                    noResultsMessage.classList.add('d-none');
                }
            });
        });
    </script>

</body>
</html>