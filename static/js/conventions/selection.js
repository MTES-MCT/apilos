function load_selection_page() {
  document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('selection')
            .addEventListener('click', convention_mode(true));
  });
}

load_selection_page()
