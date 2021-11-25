// Manage comment block using JS


// create the icon but doesn't work yet : te be investigated
function create_comment_icon(input_id, messages) {
    const path_icon = document.createElement('path');
    path_icon.setAttribute('d',"M8.82388455,18.5880577 L4,21 L4.65322944,16.4273939 C3.00629211,15.0013 2,13.0946628 2,11 C2,6.581722 6.4771525,3 12,3 C17.5228475,3 22,6.581722 22,11 C22,15.418278 17.5228475,19 12,19 C10.8897425,19 9.82174472,18.8552518 8.82388455,18.5880577 Z")
    const title_icon = document.createElement('title');
    title_icon.setAttribute('id', "chatIconTitle")
    title_icon.innerText = messages
    const svg_icon = document.createElement('svg');
    svg_icon.setAttribute('role', "img")
    svg_icon.setAttribute('xmlns', "http://www.w3.org/2000/svg")
    svg_icon.setAttribute('width', "24")
    svg_icon.setAttribute('height', "24")
    svg_icon.setAttribute('viewBox', "0 0 24 24")
    svg_icon.setAttribute('aria-labelledby', "chatIconTitle")
    svg_icon.appendChild(title_icon)
    svg_icon.appendChild(path_icon)
    const div_icon = document.createElement('div');
    div_icon.classList.add('content__icons', 'fr-px-1w')
    div_icon.setAttribute('id', input_id + "_comment-img")
    div_icon.setAttribute('data-fr-opened', "false")
    div_icon.setAttribute('aria-controls', input_id + "_comment-dialog")
    div_icon.appendChild(svg_icon)
    const main_div_icon = document.createElement('div');
    main_div_icon.setAttribute('id', input_id + "_comment")
    main_div_icon.appendChild(div_icon)
//    main_div_icon.classList.add('content__icons--blue')

    document.getElementById(input_id + "_div").appendChild(main_div_icon)
    display_comment_icon(input_id)
}

function create_comment_input(input_id, comment, has_own_active_comment=true, is_instructeur=false) {
    var before_id = input_id + "_new_comment"
    var comment_modal_id = input_id + "_modal_comment"
    new_comment_block = document.getElementById(before_id)
    if (has_own_active_comment && has_own_active_comment != 'False') {
        new_comment_block.hidden = true
    }
    const container_div = create_comment_container(comment.uuid)
    const owner_div = create_comment_owner(comment.uuid,comment.username, comment.is_owner, comment.statut);
    container_div.appendChild(owner_div)
    const date_div = create_comment_date(comment.uuid,comment.mis_a_jour_le);
    container_div.appendChild(date_div)
    const uuid_div = create_comment_uuid(comment.uuid);
    container_div.appendChild(uuid_div)
    const statut_div = create_comment_statut(input_id, comment.uuid, comment.statut);
    container_div.appendChild(statut_div)
    const textarea_div = create_comment_textarea(comment.uuid, comment.message, comment.statut, comment.is_owner);
    container_div.appendChild(textarea_div)
    const ul_buttons = create_comment_button(comment.uuid)
    container_div.appendChild(ul_buttons)
    document.getElementById(comment_modal_id).insertBefore( container_div, new_comment_block );
    init_comment_button(input_id, comment.uuid, comment.statut, comment.is_owner, is_instructeur)
}

//div container
function create_comment_container(uuid) {
    const container_div = document.createElement('div');
    container_div.setAttribute('id','comment_container_' + uuid)
    return container_div
}

//<div class="fr-mt-3w"><b>Raphaëlle Neyton (vous) :</b></div>
function create_comment_owner(uuid, username, is_owner, status) {
    const owner_div = document.createElement('div');
    owner_div.classList.add('fr-mt-3w')
    owner_div.classList.add('block--row-strech')

    const owner_span = document.createElement('span');
    owner_span.classList.add('block--row-strech-1')
    owner_span.classList.add('text-bold')
    inner_text = username
    if (is_owner && is_owner != 'False') {
        inner_text = inner_text + " (vous)"
    }
    inner_text = inner_text + " : "
    owner_span.innerText = inner_text
    owner_div.appendChild(owner_span)

    const status_span = document.createElement('span');
    status_span.setAttribute('id','comment_status_' + uuid)
    status_span.classList.add('text-bold')
    if (status == 'OUVERT') {
        status_span.classList.add('status_ouvert')
        status_span.innerText = 'Ouvert'
    }
    if (status == 'RESOLU') {
        status_span.classList.add('status_resolu')
        status_span.innerText = 'Résolu'
    }
    if (status == 'CLOS') {
        status_span.classList.add('status_clos')
        status_span.innerText = 'Clos'
    }
    owner_div.appendChild(status_span)
    return owner_div
}

//<div class="fr-text-sm text-italic"><i>le 3 novembre 2021 12:06</i></div>
function create_comment_date(uuid, date) {
    const date_div = document.createElement('div');
    date_div.setAttribute('id','comment_date_' + uuid)
    date_div.classList.add('fr-text-sm')
    date_div.classList.add('text-italic')
    date_div.innerText = "le " + date
    return date_div
}

//<input type="hidden" value="fb7d6bf9-291a-4b3d-b2a6-25fea7e20dcb">
function create_comment_uuid(uuid) {
    const uuid_div = document.createElement('input');
    uuid_div.setAttribute('type', "hidden")
    uuid_div.value = uuid
    return uuid_div
}

//<input type="hidden" value="fb7d6bf9-291a-4b3d-b2a6-25fea7e20dcb">
function create_comment_statut(input_id, uuid, statut) {
    const statut_div = document.createElement('input');
    statut_div.setAttribute('id','comment_statut_' + uuid)
    statut_div.setAttribute('name', input_id + "_comment_statut")
    statut_div.setAttribute('type', "hidden")
    statut_div.value = statut
    return statut_div
}

//<textarea class="fr-input" aria-describedby="text-input-error-desc-error" type="text" id="comment_fb7d6bf9-291a-4b3d-b2a6-25fea7e20dcb" rows="5">tt</textarea>
function create_comment_textarea(uuid, message, status, is_owner=false) {
    const textarea_div = document.createElement('textarea');
    textarea_div.classList.add('fr-input')
    textarea_div.setAttribute('aria-describedby', "text-input-error-desc-error")
    textarea_div.setAttribute('type', "text")
    if (is_owner && is_owner != 'False' && status == 'OUVERT') {
        textarea_div.disabled = false
    }
    else {
        textarea_div.disabled = true
    }
    textarea_div.setAttribute('id', "comment_" + uuid)
    textarea_div.setAttribute('rows', "5")
    textarea_div.value = message
    return textarea_div
}

function disable_textarea(uuid, status, is_owner) {
    const textarea_div = document.getElementById("comment_" + uuid)
    if (is_owner && is_owner != 'False' && status == 'OUVERT') {
        textarea_div.disabled = false
    }
    else {
        textarea_div.disabled = true
    }
}

function update_status(uuid, status) {
    const status_span = document.getElementById("comment_status_" + uuid)
    if (status == 'OUVERT') {
        status_span.classList.add('status_ouvert')
        status_span.classList.remove('status_resolu')
        status_span.classList.remove('status_clos')
        status_span.innerText = 'Ouvert'
    }
    if (status == 'RESOLU') {
        status_span.classList.remove('status_ouvert')
        status_span.classList.add('status_resolu')
        status_span.classList.remove('status_clos')
        status_span.innerText = 'Résolu'
    }
    if (status == 'CLOS') {
        status_span.classList.remove('status_ouvert')
        status_span.classList.remove('status_resolu')
        status_span.classList.add('status_clos')
        status_span.innerText = 'Clos'
    }
}

// <ul class="fr-mt-1w fr-btns-group fr-btns-group--right fr-btns-group--inline-reverse fr-btns-group--inline-lg fr-btns-group--icon-left fr-btns-group--sm">
//     <li id="block_comment_close_96c201c0-c0ce-4400-9b73-09803961e6a1" class="button-hidden">
//         <button id="comment_close_96c201c0-c0ce-4400-9b73-09803961e6a1" type="button" class="fr-btn fr-btn--sm fr-btn--grey">Marquer comme clos</button>
//     </li>
//     .....
// </ul>
function create_comment_button(uuid) {
    const ul_buttons = document.createElement('ul')
    ul_buttons.classList.add('fr-mt-1w', 'fr-btns-group', 'fr-btns-group--right', 'fr-btns-group--inline-reverse', 'fr-btns-group--inline-lg', 'fr-btns-group--icon-left', 'fr-btns-group--sm')
    ul_buttons.appendChild(create_li_button(uuid, 'close', 'Marquer comme clos', 'fr-btn--grey'))
    ul_buttons.appendChild(create_li_button(uuid, 'resolve', 'Marquer comme résolu', 'fr-btn--green'))
    ul_buttons.appendChild(create_li_button(uuid, 'reopen', 'Ré-ouvrir'))
    ul_buttons.appendChild(create_li_button(uuid, 'save', 'Modifier'))
    return ul_buttons
}

// <li id="block_comment_close_96c201c0-c0ce-4400-9b73-09803961e6a1" class="button-hidden">
//     <button id="comment_close_96c201c0-c0ce-4400-9b73-09803961e6a1" type="button" class="fr-btn fr-btn--sm fr-btn--grey">Marquer comme clos</button>
// </li>
function create_li_button(uuid, action, label, additionalButtonClass=null) {
    const button_action = document.createElement('button')
    button_action.setAttribute('id', 'comment_' + action + '_' + uuid)
    button_action.setAttribute('type', 'button')
    button_action.classList.add('fr-btn', 'fr-btn--sm')
    if (additionalButtonClass != null) {
        button_action.classList.add(additionalButtonClass)
    }
    button_action.innerText = label
    const li_action = document.createElement('li')
    li_action.setAttribute('id', 'block_comment_' + action + '_' + uuid)
    //            li_action.classList.add('button-hidden')
    li_action.appendChild(button_action)
    return li_action
}


function display_comment_icon(input_id) {
    statuts = document.getElementsByName(input_id + "_comment_statut")
    var nb_open = 0
    var nb_resolu = 0
    var nb_clos = 0
    for (var i = 0; i < statuts.length; i++) {
        if (statuts[i].value == 'OUVERT') {
            nb_open += 1
        }
        if (statuts[i].value == 'RESOLU') {
            nb_resolu += 1
        }
        if (statuts[i].value == 'CLOS') {
            nb_clos += 1
        }
    }
    if (nb_open) { // blue & displayed
        comment_icon = document.getElementById(input_id + '_comment')
        comment_icon.classList.add('content__icons--blue')
        comment_icon.classList.remove('content__icons--green')
        comment_icon.classList.remove('content__icons--grey')
        document.getElementById(input_id + '_div').onclick = null
        document.getElementById(input_id + '_div').onmouseover = null
        document.getElementById(input_id + '_div').onmouseleave = null
        comment_icon.hidden = false
    }
    else if (nb_resolu && !nb_open) { // green & displayed
        comment_icon = document.getElementById(input_id + '_comment')
        comment_icon.classList.remove('content__icons--blue')
        comment_icon.classList.add('content__icons--green')
        comment_icon.classList.remove('content__icons--grey')
        document.getElementById(input_id + '_div').onclick = null
        document.getElementById(input_id + '_div').onmouseover = null
        document.getElementById(input_id + '_div').onmouseleave = null
        comment_icon.hidden = false
    }
    else if (nb_clos && !nb_resolu && !nb_open) { // grey & displayed
        console.log(input_id + '_comment')
        comment_icon = document.getElementById(input_id + '_comment')
        comment_icon.classList.remove('content__icons--blue')
        comment_icon.classList.remove('content__icons--green')
        comment_icon.classList.add('content__icons--grey')
        document.getElementById(input_id + '_div').onclick = null
        document.getElementById(input_id + '_div').onmouseover = null
        document.getElementById(input_id + '_div').onmouseleave = null
        comment_icon.hidden = false
    }
    else { // blue & hidden
        comment_icon = document.getElementById(input_id + '_comment')
        comment_icon.classList.add('content__icons--blue')
        comment_icon.classList.remove('content__icons--green')
        comment_icon.classList.remove('content__icons--grey')
        document.getElementById(input_id + '_div').onclick = function() {
            document.getElementById(input_id + '_comment').hidden=false
        }
        document.getElementById(input_id + '_div').onmouseover = function() {
            document.getElementById(input_id + '_comment').hidden=false
        }
        document.getElementById(input_id + '_div').onmouseleave = function(){
            document.getElementById(input_id + '_comment').hidden=true
        }
    }
}


function init_comment_button(input_id, uuid, comment_statut, is_owner, is_instructeur) {
    // button 'Marquer comme clos'
    if (is_instructeur && comment_statut != 'CLOS') {
        document.getElementById('block_comment_close_' + uuid).classList.remove('button-hidden')
    }
    else {
        document.getElementById('block_comment_close_' + uuid).classList.add('button-hidden')
    }
    document.getElementById('comment_close_' + uuid).onclick = function() {
        update_status_comment(input_id, uuid, 'CLOS')
    }

    // button 'Marquer comme résolu'
    if (comment_statut == 'OUVERT') {
        document.getElementById('block_comment_resolve_' + uuid).classList.remove('button-hidden')
    }
    else {
        document.getElementById('block_comment_resolve_' + uuid).classList.add('button-hidden')
    }
    document.getElementById('comment_resolve_' + uuid).onclick = function() {
        update_status_comment(input_id, uuid, 'RESOLU')
    }

    // button 'Ré-ouvrir'
    if (comment_statut == 'RESOLU') { //  || (comment_statut == 'CLOS' && is_instructeur)
        document.getElementById('block_comment_reopen_' + uuid).classList.remove('button-hidden')
    }
    else {
        document.getElementById('block_comment_reopen_' + uuid).classList.add('button-hidden')
    }
    document.getElementById('comment_reopen_' + uuid).onclick = function() {
        update_status_comment(input_id, uuid, 'OUVERT')
    }

    // button 'Enregistrer'
    if (comment_statut == 'OUVERT' && (is_owner && is_owner != 'False')) {
        document.getElementById('block_comment_save_' + uuid).classList.remove('button-hidden')
    }
    else {
        document.getElementById('block_comment_save_' + uuid).classList.add('button-hidden')
    }
    document.getElementById('comment_save_' + uuid).onclick = function() {
        save_comment(uuid)
    }
}

// Create a new comment
function create_comment(convention_uuid, input_id, object_field) {
    var [object_name, object_field, object_uuid] = object_field.split('__')
    comment = document.getElementById('textarea_' + input_id + '_comment').value
    csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value

    var headers = {
        'X-CSRFToken': csrf_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    fetch('/comments/', {
        method: 'post',
        headers: headers,
        body: JSON.stringify({
            comment: comment,
            object_name : object_name,
            object_field : object_field,
            object_uuid : object_uuid,
            convention_uuid : convention_uuid
        })
    }).then(function(response) {
        if (response.status == 200) {
            res = response.json()
            return res;
        }
    }).then(res => {
        create_comment_input(input_id, res.comment, true, res.user.is_instructeur)
        display_comment_icon(input_id)
    });

    // Close the dialogbox
    //document.getElementById(input_id + '_comment-img').setAttribute('data-fr-opened',false)
}

// Save an existing comment
function save_comment(uuid) {
    message = document.getElementById("comment_" + uuid).value
    csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value

    var headers = {
        'X-CSRFToken': csrf_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    fetch('/comments/' + uuid, {
        method: 'post',
        headers: headers,
        body: JSON.stringify({
            message: message
        })
    }).then(function(response) {
        if (response.status == 200) {
            return response.json();
        }
    }).then(res => {
        if (res.success) {
            document.getElementById('comment_date_' + uuid).innerText = 'le ' + res.comment.mis_a_jour_le + ' (Enregistré)'
            setTimeout(function(){
                document.getElementById('comment_date_' + uuid).innerText = 'le ' + res.comment.mis_a_jour_le
            }, 5000);
        }
    });
}


// Reopen an existing comment
function update_status_comment(input_id, uuid, status) {
    message = document.getElementById("comment_" + uuid).value
    csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value

    var headers = {
        'X-CSRFToken': csrf_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    fetch('/comments/' + uuid, {
        method: 'post',
        headers: headers,
        body: JSON.stringify({
            statut: status,
            message: message,
        })
    }).then(function(response) {
        if (response.status == 200) {
            return response.json();
        }
    }).then(res => {
        if (res.success)
        {
            var comment = res.comment
            document.getElementById('comment_statut_' + comment.uuid).value = res.comment.statut
            init_comment_button(input_id, comment.uuid, comment.statut, comment.is_owner, res.user.is_instructeur)
            disable_textarea(comment.uuid, comment.statut, comment.is_owner)
            update_status(comment.uuid, comment.statut)
            if (comment.is_owner && comment.statut == 'CLOS') {
                document.getElementById(input_id + "_new_comment").hidden = false
                document.getElementById('textarea_' + input_id + "_comment").value = ''
            }
            display_comment_icon(input_id)
        }
    });
}