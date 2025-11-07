function updateHeaderHeight() {
    const header = document.getElementById('apilos-header');
    if (header) {
        document.documentElement.style.setProperty('--header-height', header.offsetHeight + 'px');
    }
}

// Run on load and resize
window.addEventListener('load', updateHeaderHeight);
window.addEventListener('resize', updateHeaderHeight);

// Optional: Also update when content changes (if you have dynamic content)
if (typeof ResizeObserver !== 'undefined') {
    const header = document.getElementById('apilos-header');
    if (header) {
        new ResizeObserver(updateHeaderHeight).observe(header);
    }
}