function load_page() {
  // useful link: https://stackoverflow.com/questions/9847580/how-to-detect-safari-chrome-ie-firefox-and-opera-browser
  if (/*@cc_on!@*/ false || !!document.documentMode) {
    document.getElementById("browser_alert").hidden = false;
  }
}

load_page();
