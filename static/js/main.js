function load_page() {
    // useful link: https://stackoverflow.com/questions/9847580/how-to-detect-safari-chrome-ie-firefox-and-opera-browser
    if (/*@cc_on!@*/false || !!document.documentMode) {
        document.getElementById('browser_alert').hidden = false
    }

    document.addEventListener("DOMContentLoaded", function(event) {
        if (localStorage.getItem('scrollloc') == clean_windows_loc()) {
            var scrollpos = localStorage.getItem('scrollpos');
            if (scrollpos) window.scrollTo(0, scrollpos);
            localStorage.setItem('scrollpos', 0);
        }
    });

    window.onbeforeunload = function(e) {
        localStorage.setItem('scrollpos', window.scrollY);
        localStorage.setItem('scrollloc', clean_windows_loc());
    };
}

function clean_windows_loc() {
    return window.location.protocol + '//' + window.location.host + window.location.pathname
}

load_page()

// Additional functions

function toggle(element_id) {
    element = document.getElementById(element_id);
    element.hidden = !element.hidden;
}

function convention_mode(is_select) {
    document.getElementById('programme_selection').hidden = !is_select
    if (document.getElementById('programme_creation') != null) {
        document.getElementById('programme_creation').hidden = is_select
    }
}

// Type 1 and 2 function

function init_type_two_options(){
    document.getElementById('id_type1and2').addEventListener('change', event => {
        if (event.target.value == 'Type2') {
            document.getElementById('type2_options').hidden = false
        }
        else {
            document.getElementById('type2_options').hidden = true
        }
    });
    function strike_checked_option(e) {
        if (!e.target.checked) {
            e.target.parentElement.getElementsByTagName('label')[0].classList.add('apilos-form-label--strike')
        }
        else {
            e.target.parentElement.getElementsByTagName('label')[0].classList.remove('apilos-form-label--strike')
        }
    }
    document.getElementById('type2_lgts_concernes_option1').addEventListener('change', e => strike_checked_option(e));
    document.getElementById('type2_lgts_concernes_option2').addEventListener('change', e => strike_checked_option(e));
    document.getElementById('type2_lgts_concernes_option3').addEventListener('change', e => strike_checked_option(e));
    document.getElementById('type2_lgts_concernes_option4').addEventListener('change', e => strike_checked_option(e));
    document.getElementById('type2_lgts_concernes_option5').addEventListener('change', e => strike_checked_option(e));
    document.getElementById('type2_lgts_concernes_option6').addEventListener('change', e => strike_checked_option(e));
    document.getElementById('type2_lgts_concernes_option7').addEventListener('change', e => strike_checked_option(e));
    document.getElementById('type2_lgts_concernes_option8').addEventListener('change', e => strike_checked_option(e));
}