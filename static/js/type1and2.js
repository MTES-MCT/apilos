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
