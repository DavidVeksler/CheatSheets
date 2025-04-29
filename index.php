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
$baseUrl = rtrim(dirname($_SERVER['SCRIPT_NAME']), '/') . '/'; // Base URL path for links

// --- Helper Function: Extract Metadata ---
function extractMetadata(string $filename): array {
    $metadata = [
        'title' => pathinfo($filename, PATHINFO_FILENAME), // Default title from filename
        'description' => 'Click to view this cheatsheet.', // Default description
        'image' => null, // Default image (none)
        'url' => $filename,
        'error' => null
    ];

    // Suppress warnings for potentially malformed HTML and file access issues
    $content = @file_get_contents($filename);
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
         // Check if the image URL is absolute or relative
        $imageUrl = trim($imgNode->nodeValue);
        if (!preg_match('/^https?:\/\//i', $imageUrl) && !str_starts_with($imageUrl, '/')) {
            // If relative and not starting with /, prepend base URL path
             global $baseUrl;
             // Construct absolute path based on the script's location
             $absoluteImagePath = realpath(dirname(__FILE__)) . '/' . $imageUrl;
             // Check if the relative image file actually exists
             if (file_exists($absoluteImagePath)) {
                 $metadata['image'] = $baseUrl . ltrim($imageUrl, '/');
             } else {
                 // If relative image doesn't exist locally, maybe it's hosted elsewhere or invalid
                 // Keep it null or log an error
                 error_log("Relative image path specified in " . $filename . " not found: " . $imageUrl);
             }
        } else {
            // Use absolute URL or root-relative URL as is
            $metadata['image'] = $imageUrl;
        }
    }

     // Limit description length for display
    if (strlen($metadata['description']) > 150) {
        $metadata['description'] = substr($metadata['description'], 0, 147) . '...';
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
        // Skip excluded items and directories
        if (in_array($file, $excludedItems, true) || is_dir($cheatsheetDir . '/' . $file)) {
            continue;
        }

        // Only process .html files
        if (str_ends_with(strtolower($file), '.html')) {
            $meta = extractMetadata($cheatsheetDir . '/' . $file);
            if ($meta['error']) {
                $errors[] = $meta['error'];
            } else {
                $cheatsheets[] = $meta;
            }
        }
    }
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
    <meta name="description" content="A gallery of useful cheatsheets covering topics like AI Safety, Bitcoin, Leadership, Programming, Philosophy, and more, created by David Veksler.">
    <meta name="keywords" content="cheatsheets, reference, guide, programming, tech, philosophy, ai safety, bitcoin, leadership, david veksler">
    <meta name="author" content="David Veksler">
    <link rel="canonical" href="https://cheatsheets.davidveksler.com/"> <!-- Assuming this index.php is the root -->

    <!-- Open Graph / Facebook / LinkedIn -->
    <meta property="og:title" content="Browse Cheatsheets - DavidVeksler.com">
    <meta property="og:description" content="A gallery of useful cheatsheets covering various topics like AI Safety, Bitcoin, Leadership, and more.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://cheatsheets.davidveksler.com/">
    <meta property="og:image" content="https://cheatsheets.davidveksler.com/images/og-image-default.png"> <!-- Suggest creating a default OG image for the gallery page -->
    <meta property="og:image:alt" content="David Veksler Cheatsheets Gallery">
    <meta property="og:site_name" content="David Veksler's Cheatsheets">
    <meta property="og:locale" content="en_US">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Browse Cheatsheets - DavidVeksler.com">
    <meta name="twitter:description" content="Explore a collection of handy cheatsheets on tech, philosophy, and more.">
    <meta name="twitter:url" content="https://cheatsheets.davidveksler.com/">
    <meta name="twitter:image" content="https://cheatsheets.davidveksler.com/images/og-image-default.png"> <!-- Use the same default image -->
    <meta name="twitter:image:alt" content="David Veksler Cheatsheets Gallery">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">

    <style>
        body {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .main-content {
            flex: 1;
        }
        .card {
            transition: transform .2s ease-in-out, box-shadow .2s ease-in-out;
            border: none; /* Cleaner look, rely on shadow */
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
        }
        .card-img-top {
            aspect-ratio: 16 / 9; /* Maintain aspect ratio for images */
            object-fit: cover; /* Cover the area, might crop */
            border-bottom: 1px solid #eee;
        }
        .card-title a {
            text-decoration: none;
            color: inherit;
        }
        .card-title a:hover {
            text-decoration: underline;
            color: #0d6efd; /* Bootstrap primary color */
        }
        .card-body {
            display: flex;
            flex-direction: column;
        }
        .card-text {
             flex-grow: 1; /* Allow description to take available space */
             margin-bottom: 1rem; /* Ensure spacing before footer */
        }
        .card-footer {
            background-color: #f8f9fa; /* Light background for footer */
            border-top: none; /* Remove default top border */
        }
        .placeholder-image {
            aspect-ratio: 16 / 9;
            background-color: #e9ecef;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6c757d;
            font-size: 0.9rem;
             border-bottom: 1px solid #eee;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="<?php echo htmlspecialchars($baseUrl); ?>">DavidVeksler.com Cheatsheets</a>
            <!-- Add navbar toggler if needed -->
        </div>
    </nav>

    <main class="main-content container mt-4 mb-5">
        <h1 class="mb-4 display-5 border-bottom pb-2">Browse Cheatsheets</h1>

        <?php if (!empty($errors)): ?>
            <div class="alert alert-warning" role="alert">
                <h4 class="alert-heading">Notice</h4>
                <p>There were some issues loading cheatsheet details:</p>
                <ul>
                    <?php foreach ($errors as $error): ?>
                        <li><?php echo htmlspecialchars($error); ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        <?php endif; ?>

        <?php if (empty($cheatsheets) && empty($errors)): ?>
            <div class="alert alert-info" role="alert">
                No cheatsheets found in this directory.
            </div>
        <?php elseif (!empty($cheatsheets)): ?>
            <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
                <?php foreach ($cheatsheets as $sheet): ?>
                    <div class="col d-flex align-items-stretch">
                        <div class="card h-100 shadow-sm">
                            <?php if (!empty($sheet['image'])): ?>
                                <a href="<?php echo htmlspecialchars($sheet['url']); ?>" target="_blank" rel="noopener">
                                    <img src="<?php echo htmlspecialchars($sheet['image']); ?>" class="card-img-top" alt="Preview for <?php echo htmlspecialchars($sheet['title']); ?>" loading="lazy">
                                </a>
                            <?php else: ?>
                                <!-- Placeholder if no image -->
                                <div class="placeholder-image">
                                    <span>No Image Preview</span>
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
                                    View Cheatsheet
                                </a>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </main>

    <footer class="py-4 bg-light text-center border-top">
        <div class="container">
            <span class="text-muted">Cheatsheets by David Veksler &copy; <?php echo date("Y"); ?></span>
        </div>
    </footer>

    <!-- Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
</body>
</html>