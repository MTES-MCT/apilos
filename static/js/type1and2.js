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

    // init comments on type I and type II selector
    object_uuid = document.getElementById('convention_uuid').value
    div_id = "convention__type1and2__" +object_uuid
    const comment_div = document.createElement('div');
    comment_div.setAttribute('id',div_id);
    element_id = 'id_type1and2_div';
    element = document.getElementById(element_id);
    element.append(comment_div)

    new CommentFactory({
        container_id : div_id,
        convention_uuid : object_uuid,
        load_initial_status : true,
        object_name : 'convention',
        object_field : 'type1and2',
        object_uuid : object_uuid,
        dialog_title : "Type de convention I ou II",
        empty_toggle_on : "id_type1and2_group",
        callback_click: 'refresh_opened_comments',
        loading_img : '/static/icons/loading.gif'
    })

}



