(function () {
    function initRegeneration() {
        const form = document.getElementById('regenerate_form');
        const spinnerContainer = document.getElementById('regenerate_spinner_container');
        const alertBox = document.getElementById('regenerate_alert');
        const iframe = document.getElementById('convention_document_iframe');
        if (!form || !spinnerContainer || !alertBox) return;

        const statusUrl = form.dataset.statusUrl;
        if (!statusUrl) return;

        function showRegenerationForm(message) {
            form.style.display = 'block';
            spinnerContainer.style.display = 'none';
            const desc = document.getElementById('regenerate_description');
            if (desc) {
                desc.textContent = message;
            }
        }

        let attempts = 0;
        const maxAttempts = 20; // 20 * 3s = 60s
        const pollIntervalMs = 3000;

        function pollDocumentStatus() {
            attempts++;
            fetch(statusUrl, {
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data && data.ready) {
                    alertBox.className = 'fr-alert fr-alert--success';
                    alertBox.innerHTML = '<h3 class="fr-alert__title">Le document a été généré avec succès</h3><p>Le document est désormais disponible ci-dessous.</p>';
                    if (iframe) {
                        const currentSrc = new URL(iframe.src);
                        currentSrc.searchParams.set('t', Date.now());
                        iframe.src = currentSrc.toString();
                    }
                } else if (attempts < maxAttempts) {
                    setTimeout(pollDocumentStatus, pollIntervalMs);
                } else {
                    showRegenerationForm("La génération prend plus de temps que prévu. Vous pouvez recharger la page ou relancer.");
                }
            })
            .catch(function () {
                if (attempts < maxAttempts) {
                    setTimeout(pollDocumentStatus, pollIntervalMs);
                } else {
                    showRegenerationForm("La génération prend plus de temps que prévu. Vous pouvez recharger la page ou relancer.");
                }
            });
        }

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            form.style.display = 'none';
            spinnerContainer.style.display = 'flex';

            const csrfInput = form.querySelector('[name=csrfmiddlewaretoken]');
            const csrfToken = csrfInput ? csrfInput.value : '';

            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            })
            .then(function (res) {
                if (!res.ok) {
                    throw new Error('Erreur lors du déclenchement de la génération');
                }
                return res.json();
            })
            .then(function () {
                pollDocumentStatus();
            })
            .catch(function () {
                showRegenerationForm("Une erreur est survenue lors du lancement de la génération. Veuillez réessayer.");
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initRegeneration);
    } else {
        initRegeneration();
    }
})();
