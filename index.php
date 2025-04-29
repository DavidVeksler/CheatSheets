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
    global $baseUrl; // Access the base URL for resolving relative paths

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
                 // Check if the relative image file actually exists locally first
                 $absoluteImagePath = realpath(dirname(__FILE__)) . '/' . $imageUrl;
                 if (file_exists($absoluteImagePath)) {
                    $metadata['image'] = $baseUrl . $imageUrl;
                 } else {
                     error_log("Relative image path specified in " . $filename . " not found: " . $imageUrl);
                     // Keep image as null if local file doesn't exist
                 }
             }
        } else {
             // It's an absolute URL, use as is
            $metadata['image'] = $imageUrl;
        }
    }

     // Limit description length for display consistency
    if (strlen($metadata['description']) > 150) {
        $metadata['description'] = mb_substr($metadata['description'], 0, 147) . '...'; // Use mb_substr for multi-byte safety
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
    // Optional: Sort cheatsheets alphabetically by title
    // usort($cheatsheets, fn($a, $b) => strcmp(strtolower($a['title']), strtolower($b['title'])));

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
    <!-- === SEO Metadata for the Gallery Page === -->
    <title>Browse Cheatsheets - DavidVeksler.com</title>
    <meta name="description" content="A visually rich gallery of useful cheatsheets covering topics like AI Safety, Bitcoin, Leadership, Programming, Philosophy, and more, created by David Veksler.">
    <meta name="keywords" content="cheatsheets, reference, guide, programming, tech, philosophy, ai safety, bitcoin, leadership, david veksler, gallery, visual browser">
    <meta name="author" content="David Veksler">
    <link rel="canonical" href="<?php echo htmlspecialchars($baseUrl); ?>"> <!-- Canonical URL for the gallery root -->

    <!-- Open Graph / Facebook / LinkedIn -->
    <meta property="og:title" content="Browse Cheatsheets - DavidVeksler.com">
    <meta property="og:description" content="A visually rich gallery of useful cheatsheets covering various topics like AI Safety, Bitcoin, Leadership, and more.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="<?php echo htmlspecialchars($baseUrl); ?>">
    <meta property="og:image" content="<?php echo htmlspecialchars($baseUrl); ?>images/cheatsheets-og.png"> <!-- Suggest creating a specific OG image for the gallery -->
    <meta property="og:image:alt" content="David Veksler Cheatsheets Gallery">
    <meta property="og:site_name" content="David Veksler's Cheatsheets">
    <meta property="og:locale" content="en_US">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Browse Cheatsheets - DavidVeksler.com">
    <meta name="twitter:description" content="Explore a collection of handy cheatsheets on tech, philosophy, and more in a visual gallery.">
    <meta name="twitter:url" content="<?php echo htmlspecialchars($baseUrl); ?>">
    <meta name="twitter:image" content="<?php echo htmlspecialchars($baseUrl); ?>images/cheatsheets-og.png"> <!-- Use the same default image -->
    <meta name="twitter:image:alt" content="David Veksler Cheatsheets Gallery">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">

    <style>
        :root {
             --card-lift-height: -8px;
             --card-shadow-intensity: rgba(0, 0, 0, .18);
        }
        body {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-color: #f8f9fa; /* Slightly off-white background */
        }
        .main-content {
            flex: 1;
        }
        .navbar {
            /* Subtle gradient */
             background-image: linear-gradient(to bottom, #343a40, #212529);
        }
        .card {
            transition: transform .25s ease-in-out, box-shadow .25s ease-in-out;
            border: none; /* Cleaner look */
            border-radius: .375rem; /* Bootstrap's default rounded corners */
            overflow: hidden; /* Ensure content respects border-radius */
            background-color: #fff; /* Ensure card background is white */
        }
        .card:hover {
            transform: translateY(var(--card-lift-height));
            box-shadow: 0 1rem 2rem var(--card-shadow-intensity);
        }
        .card-img-top, .iframe-preview-container {
            aspect-ratio: 16 / 9; /* Maintain aspect ratio */
            object-fit: cover; /* Cover the area for images */
            background-color: #e9ecef; /* Background for placeholder/iframe loading */
            border-bottom: 1px solid #dee2e6; /* Subtle separator */
        }
        .iframe-preview-container {
            position: relative;
            overflow: hidden; /* Hide iframe scrollbars if they appear briefly */
        }
        .iframe-preview-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0;
            background-color: #fff; /* Background while loading */
        }
        .card-title a {
            text-decoration: none;
            color: inherit;
            font-weight: 600; /* Slightly bolder title */
        }
        .card-title a:hover {
            color: #0d6efd; /* Bootstrap primary */
            text-decoration: underline;
        }
        .card-body {
            display: flex;
            flex-direction: column;
            padding: 1.25rem; /* Standard Bootstrap card padding */
        }
        .card-text {
             flex-grow: 1;
             margin-bottom: 1.25rem;
             color: #495057; /* Slightly softer text color */
             font-size: 0.9rem;
        }
        .card-footer {
            background-color: transparent; /* Make footer blend with card body */
            border-top: 1px solid #eee; /* Separator line */
            padding: 0.75rem 1.25rem;
        }
        .footer {
             background-color: #e9ecef; /* Footer distinct from main content */
             color: #6c757d;
        }
        .display-5 {
            font-weight: 300;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="<?php echo htmlspecialchars($baseUrl); ?>">
                 <i class="bi bi-journal-richtext me-2"></i>DavidVeksler.com Cheatsheets
            </a>
            <!-- Add navbar toggler if needed for smaller screens -->
             <!-- <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                 Add nav items here if needed
            </div> -->
        </div>
    </nav>

    <main class="main-content container mt-4 mb-5">
        <header class="text-center mb-5">
            <h1 class="display-5">Browse Cheatsheets</h1>
            <p class="lead text-muted">A collection of guides and references.</p>
        </header>


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

        <?php if (empty($cheatsheets) && empty($errors)): ?>
            <div class="alert alert-info text-center" role="alert">
                <i class="bi bi-info-circle me-2"></i>No cheatsheets found in this directory.
            </div>
        <?php elseif (!empty($cheatsheets)): ?>
            <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
                <?php foreach ($cheatsheets as $sheet): ?>
                    <div class="col d-flex align-items-stretch">
                        <div class="card h-100 shadow-sm">
                            <?php if (!empty($sheet['image'])): ?>
                                <!-- Display OG Image if available -->
                                <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener" aria-label="Preview image for <?php echo htmlspecialchars($sheet['title']); ?>">
                                    <img src="<?php echo htmlspecialchars($sheet['image']); ?>" class="card-img-top" alt="Preview for <?php echo htmlspecialchars($sheet['title']); ?>" loading="lazy">
                                </a>
                            <?php else: ?>
                                <!-- Fallback: Display iframe preview -->
                                <div class="iframe-preview-container">
                                    <iframe src="<?php echo htmlspecialchars($sheet['url']); ?>"
                                            title="Preview of <?php echo htmlspecialchars($sheet['title']); ?>"
                                            loading="lazy"
                                            frameborder="0"
                                            scrolling="no"
                                            referrerpolicy="no-referrer"
                                            >
                                            <!-- Optional: Add sandbox attribute if needed, but it might break functionality -->
                                            <!-- sandbox="allow-scripts allow-same-origin" -->
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
                                <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener" class="btn btn-sm btn-primary">
                                    View Cheatsheet <i class="bi bi-box-arrow-up-right ms-1"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </main>

    <footer class="footer py-4 mt-auto border-top">
        <div class="container text-center">
            <span class="text-muted">Cheatsheets by David Veksler © <?php echo date("Y"); ?></span>
             <!-- Optional: Add links -->
             <!-- <small class="d-block mt-2"><a href="#">About</a> | <a href="#">Contact</a></small> -->
        </div>
    </footer>

    <!-- Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
</body>
</html>