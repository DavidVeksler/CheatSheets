document.addEventListener('DOMContentLoaded', () => {
    // --- Initial Prism.js highlighting for visible code blocks ---
    if (typeof Prism !== 'undefined') {
        try {
            Prism.highlightAll();
        } catch (e) {
            console.warn("Prism.highlightAll() error on initial load:", e);
        }
    }

    const mainContainer = document.getElementById('main-container');
    const searchBox = document.getElementById('search-box');
    const categoryFiltersContainer = document.getElementById('category-filters');
    const noResultsDiv = document.getElementById('no-results');
    const allSchemaContainers = Array.from(document.querySelectorAll('.schema-container'));

    let currentHoverState = { card: null, line: null };
    let activeFilter = 'all'; // To store the currently active category filter

    // Initialize Bootstrap Tooltips (Defensive Check)
    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Tooltip === 'function') {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    } else {
        console.warn('Bootstrap Tooltip component not found. Static tooltips may not work or might throw errors if initialized later.');
    }


    // --- Initialize Filters & Search ---
    function initializeFiltersAndSearch() {
        // Create filter buttons
        const allButton = document.createElement('button');
        allButton.type = 'button';
        allButton.classList.add('btn', 'btn-outline-secondary', 'filter-btn', 'active');
        allButton.textContent = 'All Categories';
        allButton.dataset.filter = 'all';
        allButton.setAttribute('data-bs-toggle', 'tooltip');
        allButton.setAttribute('data-bs-placement', 'top');
        allButton.setAttribute('title', 'Show all categories');
        categoryFiltersContainer.appendChild(allButton);
        if (typeof bootstrap !== 'undefined' && typeof bootstrap.Tooltip === 'function') { // Dynamic tooltip init
            new bootstrap.Tooltip(allButton);
        }


        const btnGroup = document.createElement('div');
        btnGroup.classList.add('btn-group', 'flex-wrap');
        btnGroup.setAttribute('role', 'group');

        allSchemaContainers.forEach(section => {
            const sectionId = section.dataset.sectionId;
            // Use data-section-name directly for button text, it's cleaner
            const sectionName = section.dataset.sectionName || section.querySelector('.section-title').textContent.trim();
            const button = document.createElement('button');
            button.type = 'button';
            button.classList.add('btn', 'btn-outline-secondary', 'filter-btn');
            button.textContent = sectionName;
            button.dataset.filter = sectionId;
            button.setAttribute('data-bs-toggle', 'tooltip');
            button.setAttribute('data-bs-placement', 'top');
            button.setAttribute('title', `Filter by ${sectionName}`);
            btnGroup.appendChild(button);
            if (typeof bootstrap !== 'undefined' && typeof bootstrap.Tooltip === 'function') { // Dynamic tooltip init
                 new bootstrap.Tooltip(button);
            }
        });
        categoryFiltersContainer.appendChild(btnGroup);

        // Event listener for search box
        searchBox.addEventListener('input', () => {
            applyFiltersAndSearch();
        });

        // Event listener for filter buttons (using event delegation)
        categoryFiltersContainer.addEventListener('click', (event) => {
            if (event.target.classList.contains('filter-btn')) {
                document.querySelectorAll('#category-filters .filter-btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                activeFilter = event.target.dataset.filter;
                applyFiltersAndSearch();
                clearHoverState(true); // Clear lines when filtering
                setTimeout(positionLines, 50); // Allow DOM changes to settle before repositioning if needed
            }
        });
    }

    function applyFiltersAndSearch() {
        const searchTerm = searchBox.value.toLowerCase().trim();
        let itemsFound = 0;

        allSchemaContainers.forEach(section => {
            const sectionId = section.dataset.sectionId;
            const isSectionActiveDueToFilter = (activeFilter === 'all' || sectionId === activeFilter);

            if (!isSectionActiveDueToFilter) {
                section.style.display = 'none'; // Hide section if it doesn't match the category filter
                // Also hide all its card columns to ensure they don't affect layout or future calcs
                Array.from(section.querySelectorAll('.info-card')).forEach(card => {
                    const column = card.closest('.col-lg-4.col-md-6');
                    if (column) column.style.display = 'none';
                });
                return; // Move to the next section
            }

            // If we reach here, the section matches the category filter.
            // Now, check cards within this section against the search term.
            let sectionHasVisibleCardsMatchingSearch = false;
            const cardsInSection = Array.from(section.querySelectorAll('.info-card'));

            cardsInSection.forEach(card => {
                const cardTitle = card.querySelector('h5') ? card.querySelector('h5').textContent.toLowerCase() : '';
                const cardSummary = card.querySelector('p.summary') ? card.querySelector('p.summary').textContent.toLowerCase() : '';
                const cardDetailsCollapse = card.querySelector('.collapse-content');
                // Ensure cardDetailsText is empty string if content is placeholder to avoid matching placeholders
                let cardDetailsText = '';
                if (cardDetailsCollapse) {
                    const tempText = cardDetailsCollapse.textContent.toLowerCase();
                    if (!tempText.includes('<!-- detailed content needed -->') && !tempText.includes('content placeholder for')) {
                        cardDetailsText = tempText;
                    }
                }
                const versionTag = card.querySelector('.version-tag') ? card.querySelector('.version-tag').textContent.toLowerCase() : '';
                const keywords = card.dataset.keywords ? card.dataset.keywords.toLowerCase() : '';

                const cardTextContent = `${cardTitle} ${cardSummary} ${cardDetailsText} ${versionTag} ${keywords}`;
                const cardMatchesSearch = searchTerm === '' || cardTextContent.includes(searchTerm);
                const column = card.closest('.col-lg-4.col-md-6');

                if (cardMatchesSearch) {
                    if (column) column.style.display = ''; // Show column
                    sectionHasVisibleCardsMatchingSearch = true;
                    itemsFound++;
                } else {
                    if (column) column.style.display = 'none'; // Hide column
                }
            });

            // Finally, set the section's visibility
            if (sectionHasVisibleCardsMatchingSearch) {
                section.style.display = ''; // Show section if it has cards matching the search
            } else {
                // Hide section if it's active by filter but has no cards matching search (or if it was empty)
                section.style.display = 'none';
            }
        });

        noResultsDiv.style.display = itemsFound === 0 && (searchTerm !== '' || activeFilter !== 'all') ? 'block' : 'none';

        // Re-highlight code blocks if Prism is loaded and items are visible
        if (typeof Prism !== 'undefined' && (itemsFound > 0 || (searchTerm === '' && activeFilter === 'all'))) {
            try {
                 Prism.highlightAll();
            } catch (e) {
                console.warn("Prism.highlightAll() error during filter/search:", e);
            }
        }
    }


    // --- LeaderLine Drawing Logic ---
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function getElementColor(element) {
        if (!element) return '#6c757d'; // Default tooling color
        let color = window.getComputedStyle(element).getPropertyValue('--db-category-color').trim();
        if (!color || color === 'initial' || color === 'inherit' || color === 'var(--js-color-frameworks)') {
            const section = element.closest('.schema-container');
             if (section) {
                color = window.getComputedStyle(section).getPropertyValue('--db-category-color').trim();
             }
        }
        return color || '#6c757d'; // Fallback to default
    }


    function clearHoverState(forceClear = false) {
        const isMouseStillOverCard = !forceClear && currentHoverState.card && currentHoverState.card.matches(':hover');

        if (forceClear || !isMouseStillOverCard) {
            if (currentHoverState.line) {
                try { currentHoverState.line.remove(); } catch (e) { /* Ignore error if line already gone */ }
                currentHoverState.line = null;
            }
            if (currentHoverState.card) {
                 currentHoverState.card.classList.remove('is-highlighted');
                 currentHoverState.card = null;
            }
        }
    }

    function applyHoverState(card) {
        const column = card.closest('.col-lg-4.col-md-6');
        if (!card || card === currentHoverState.card || (column && column.style.display === 'none')) return;

        clearHoverState(true); 

        const schemaContainer = card.closest('.schema-container');
        if (!schemaContainer || schemaContainer.style.display === 'none') return;

        const sectionHeader = schemaContainer.querySelector('.section-title');
        const canDrawLine = sectionHeader && card.id && sectionHeader.id &&
                            sectionHeader.offsetParent !== null && card.offsetParent !== null &&
                            typeof LeaderLine !== 'undefined';

        currentHoverState.card = card;
        card.classList.add('is-highlighted');

        if (canDrawLine) {
            try {
                const cardColor = getElementColor(card);
                currentHoverState.line = new LeaderLine( 
                    sectionHeader, card,
                    {
                        color: cardColor, size: 2.5, path: 'fluid',
                        startSocket: 'bottom', endSocket: 'top',
                        startSocketGravity: [0, -25], endSocketGravity: [0, 25],
                        dash: { animation: true, len: 8, gap: 4 },
                    }
                );
            } catch (e) {
                console.error("LeaderLine error:", e);
                clearHoverState(true); 
            }
        }
    }

     mainContainer.addEventListener('mouseover', (event) => {
        const targetCard = event.target.closest('.info-card');
        if (targetCard) { // Simplified condition: if it's a card, try to apply hover state. applyHoverState has internal checks.
             applyHoverState(targetCard);
        }
     });

    mainContainer.addEventListener('mouseout', (event) => {
        const currentCard = currentHoverState.card; 
        if (currentCard && event.target.closest('.info-card') === currentCard) { 
            const relatedTarget = event.relatedTarget; 
             if (!currentCard.contains(relatedTarget) && (!relatedTarget || !relatedTarget.closest('.info-card'))) {
                setTimeout(() => { 
                     if (currentHoverState.card && !currentHoverState.card.matches(':hover')) { 
                         clearHoverState(false); 
                     }
                 }, 50);
             }
        } else if (currentCard && !event.target.closest('.info-card')) {
            // If mouseout is from the container but not over a card, clear if current card is no longer hovered
             setTimeout(() => {
                 if (currentHoverState.card && !currentHoverState.card.matches(':hover')) {
                     clearHoverState(false);
                 }
             }, 50);
        }
    });

     const positionLines = debounce(() => {
         if (currentHoverState.line && currentHoverState.card && typeof currentHoverState.line.position === 'function') { 
             try {
                const startElem = currentHoverState.line.start;
                const endElem = currentHoverState.line.end;
                const endElemColumn = endElem ? endElem.closest('.col-lg-4.col-md-6') : null;

                if (startElem && endElem && document.body.contains(startElem) && document.body.contains(endElem) &&
                    startElem.offsetParent !== null && endElem.offsetParent !== null &&
                    window.getComputedStyle(startElem).display !== 'none' && window.getComputedStyle(endElem).display !== 'none' &&
                    endElemColumn && endElemColumn.style.display !== 'none' ) {
                     currentHoverState.line.position();
                } else {
                    clearHoverState(true); 
                }
             } catch (e) {
                 console.warn("LeaderLine reposition error:", e);
                 clearHoverState(true); 
             }
         }
     }, 100);

    window.addEventListener('resize', positionLines);
    window.addEventListener('scroll', positionLines, { passive: true });

    // --- Collapse Handling ---
    const collapseElements = document.querySelectorAll('.collapse');
    collapseElements.forEach(collapseEl => {
        const button = document.querySelector(`.details-toggle[data-bs-target="#${collapseEl.id}"]`);
        const iconEl = button ? button.querySelector('.bi') : null;

        if (button && iconEl) {
            const updateIconStateAndHighlight = () => {
                const isShown = collapseEl.classList.contains('show');
                button.setAttribute('aria-expanded', isShown.toString());
                if (isShown) {
                    iconEl.classList.remove('bi-chevron-down');
                    iconEl.classList.add('bi-chevron-up');
                    if (typeof Prism !== 'undefined') {
                        try {
                            Prism.highlightAllUnder(collapseEl);
                        } catch (e) {
                             console.warn("Prism.highlightAllUnder() error on collapse show:", e);
                        }
                    }
                } else {
                    iconEl.classList.remove('bi-chevron-up');
                    iconEl.classList.add('bi-chevron-down');
                }
            };
            
            // Set initial state based on HTML (none are pre-expanded, so this is fine)
            updateIconStateAndHighlight(); 

            collapseEl.addEventListener('show.bs.collapse', () => {
                updateIconStateAndHighlight();
                setTimeout(positionLines, 50); 
            });
            collapseEl.addEventListener('shown.bs.collapse', positionLines); 
            collapseEl.addEventListener('hide.bs.collapse', () => {
                updateIconStateAndHighlight();
                setTimeout(positionLines, 50);
            });
            collapseEl.addEventListener('hidden.bs.collapse', positionLines);
        }
    });

    // --- Footer Year ---
    const currentYearEl = document.getElementById('currentYear');
    if (currentYearEl) {
        currentYearEl.textContent = new Date().getFullYear();
    }

    // --- Initial Setup Calls ---
    initializeFiltersAndSearch();
    applyFiltersAndSearch(); 
});