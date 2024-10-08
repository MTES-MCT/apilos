function load_page() {
  // useful link: https://stackoverflow.com/questions/9847580/how-to-detect-safari-chrome-ie-firefox-and-opera-browser
  if (/*@cc_on!@*/ false || !!document.documentMode) {
    document.getElementById("browser_alert").hidden = false;
  }
}

load_page();

document.addEventListener("DOMContentLoaded", () => {
  var dateForm= document.querySelector("#id_gestionnaire_signataire_date_deliberation");
  var blocForm = document.querySelector('#id_gestionnaire_bloc_info_complementaire');
  var datePreview=document.querySelector(".apilos-insert-date-deliberation");
  var blocPreview = document.querySelector(".apilos-insert-info-complementaire");
  if (document.contains(dateForm)) {

    datePreview.innerText = new Date(dateForm.value).toLocaleDateString('fr-FR', {day: 'numeric', month: 'long',  year: 'numeric'});
    blocPreview.innerText = blocForm.value;
    dateForm.addEventListener("change", () => {
      datePreview.innerText = new Date(dateForm.value).toLocaleDateString('fr-FR', {day: 'numeric', month: 'long',  year: 'numeric'});
    })
    blocForm.addEventListener("input", () => {
      blocPreview.innerText = blocForm.value;
    })
  }
  const tx = document.querySelector("textarea#id_champ_libre_avenant");
  if (document.contains(tx)) {
    tx.setAttribute("style", "height:" + (tx.scrollHeight) + "px;overflow-y:hidden;");
    tx.addEventListener("input", OnInput, false);
  }
})

function OnInput() {
  this.style.height = 'auto';
  this.style.height = (this.scrollHeight) + "px";
}
