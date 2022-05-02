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
    for (i = 1; i<=8; i++) {
        document.getElementById('type2_lgts_concernes_option' + i).addEventListener('change', e => strike_checked_option(e));

    }
}
