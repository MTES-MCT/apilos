// class to manage the comment behaviour
class CommentFactory {
    constructor({container_id, convention_uuid, object_name, object_field, object_uuid=null, loading_img, dialog_title='Title', input_div_id} = {}) {
        this.container_id = container_id
        this.container = document.getElementById(container_id)
        this.convention_uuid = convention_uuid
        this.object_name = object_name
        this.object_field = object_field
        this.object_uuid = object_uuid
        this.loading_img = loading_img
        this.dialog_title = dialog_title
        this.input_div_id = input_div_id
        this.comment_dialog_id = 'main_comment_modal'
        this.comment_icon_id = this.object_name + '__' + this.object_field + '__' + this.object_uuid + '_comment'
        this._add_comment_icon()
    }

    // add the icon in the container
    _add_comment_icon() {
        this.container.innerHTML = '\
<div id="' + this.comment_icon_id + '" class="content__icons--darkgrey">\
    <div class="content__icons"\
        id="' + this.comment_icon_id + '-img"\
        data-fr-opened="false"\
        aria-controls="' + this.comment_dialog_id + '-dialog">\
        <svg role="img" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewbox="0 0 24 24" aria-labelledby="chatIconTitle">\
            <title id="chatIconTitle">Annexes comments</title>\
            <path d="M8.82388455,18.5880577 L4,21 L4.65322944,16.4273939 C3.00629211,15.0013 2,13.0946628 2,11 C2,6.581722 6.4771525,3 12,3 C17.5228475,3 22,6.581722 22,11 C22,15.418278 17.5228475,19 12,19 C10.8897425,19 9.82174472,18.8552518 8.82388455,18.5880577 Z"></path>\
        </svg>\
    </div>\
</div>\
'
        if (document.getElementById(this.comment_dialog_id) === null) {
            //create dialog: Can be improved
            const dialog_modal = document.createElement('dialog');
            dialog_modal.classList.add('fr-modal')
            dialog_modal.setAttribute('id', this.comment_dialog_id + '-dialog')
            dialog_modal.setAttribute('aria-labelledby', '' + this.comment_dialog_id + '-title')
            dialog_modal.setAttribute('role', 'dialog')
            const comment_dialog_content = '<div class="fr-container fr-container--fluid fr-container-md">\
    <div class="fr-grid-row fr-grid-row--center">\
        <div class="fr-col-12 fr-col-md-8 fr-col-lg-6">\
            <div id="loading">\
                <img id="loading-image" src="'+this.loading_img+'" alt="Loading..." />\
            </div>\
            <div class="fr-modal__body">\
                <div class="fr-modal__header">\
                    <button type="button" class="fr-link--close fr-link" aria-controls="' + this.comment_dialog_id + '-dialog">Fermer</button>\
                </div>\
                <div class="fr-modal__content fr-mb-1w" id="global_in_page_modal_comment">\
                    <h3 id="' + this.comment_dialog_id + '-title" class="fr-modal__title">\
                        <span class="fr-fi-arrow-right-line fr-fi--lg"></span>\
                        <span id="' + this.comment_dialog_id + '-title_text"></span>\
                    </h3>\
                    <div id="' + this.comment_dialog_id + '_comments">\
                    </div>\
                    <div id="global_in_page_new_comment">\
                        <div class="fr-mt-3w fr-mb-1w"><b>Ajouter un commentaire :</b></div>\
                        <textarea\
                            class="fr-input"\
                            aria-describedby="text-input-error-desc-error"\
                            type="text"\
                            id="textarea_' + this.comment_dialog_id + '"\
                            name="textarea_' + this.comment_dialog_id + '"></textarea>\
                        <ul class="fr-mt-1w fr-btns-group fr-btns-group--right fr-btns-group--inline-reverse fr-btns-group--inline-lg fr-btns-group--icon-left fr-btns-group--sm">\
                            <li>\
                                <button id="' + this.comment_dialog_id + '-submit" type="button" class="fr-btn fr-btn--sm">\
                                    Commenter\
                                </button>\
                            </li>\
                        </ul>\
                    </div>\
                </div>\
            </div>\
       </div>\
    </div>\
</div>\
'
            dialog_modal.innerHTML = comment_dialog_content
            document.body.append(dialog_modal)
            document.getElementById('textarea_' + this.comment_dialog_id).addEventListener('input', function() {
                var rows = this.value.split(/\r\n|\r|\n/).length
                this.setAttribute('rows', rows)
            })
        }

        this.display_global_comment_icon('{{convention.uuid}}','{{main_comment_id}}')

        this.container.onclick = e => {
            this.display_modal_comments()
        }
    }

    display_modal_comments() {
        document.getElementById('loading').hidden = false
        this.update_global_modal_title()
        this.remove_previous_comments()

        this.get_comments( res => {
            for (var i = 0; i < res.comments.length; i++) {
                this.create_global_comment_input(res.comments[i], res.user.is_instructeur)
            }
            document.getElementById(this.comment_dialog_id + '-submit').onclick = e => {
                this.create_comment()
            }
            document.getElementById('loading').hidden = true
        })
    }

    finish_display_modal_comments(res) {
        for (var i = 0; i < res.comments.length; i++) {
            this.create_global_comment_input(res.comments[i], res.user.is_instructeur)
        }
        document.getElementById(this.comment_dialog_id + '-submit').onclick = e => {
            this.create_comment()
        }
        document.getElementById('loading').hidden = true
    }


    // update title
    update_global_modal_title(){
        document.getElementById(this.comment_dialog_id + '-title_text').innerText = this.dialog_title
    }

    // remove comments inside global modal
    remove_previous_comments() {
        document.getElementById(this.comment_dialog_id + '_comments').innerHTML = "";
    }


    create_global_comment_input(comment, is_instructeur=false) {
        var inside_id = this.comment_dialog_id + "_comments"

        var comments_block = document.getElementById(inside_id)
        const container_div = this.create_comment_container(comment.uuid)
        const owner_div = this.create_comment_owner(comment.uuid,comment.username, comment.is_owner, comment.statut);
        container_div.appendChild(owner_div)
        const date_div = this.create_comment_date(comment.uuid,comment.mis_a_jour_le);
        container_div.appendChild(date_div)
        const uuid_div = this.create_comment_uuid(comment.uuid);
        container_div.appendChild(uuid_div)
        const statut_div = this.create_comment_statut(comment.uuid, comment.statut);
        container_div.appendChild(statut_div)
        const textarea_div = this.create_comment_textarea(comment.uuid, comment.message, comment.statut, comment.is_owner);
        container_div.appendChild(textarea_div)
        const ul_buttons = this.create_comment_button(comment.uuid)
        container_div.appendChild(ul_buttons)
        document.getElementById(inside_id).append(container_div)

        this.init_comment_button(comment.uuid, comment.statut, comment.is_owner, is_instructeur)

        if (comment.statut == 'CLOS') {
            this._hide_textarea_for_close_comment(comment.uuid)
        }
    }



    init_comment_button(uuid, comment_statut, is_owner, is_instructeur) {
        // button 'Marquer comme clos'
        if (is_instructeur && comment_statut != 'CLOS') {
            document.getElementById('div_button_close_' + this.comment_icon_id + '_' + uuid).classList.remove('button-hidden')
        }
        else {
            document.getElementById('div_button_close_' + this.comment_icon_id + '_' + uuid).classList.add('button-hidden')
        }
        document.getElementById('button_close_' + this.comment_icon_id + '_' + uuid).onclick = e => {
            this.update_comment(uuid, 'CLOS')
        }

        // button 'Marquer comme résolu'
        if (comment_statut == 'OUVERT') {
            document.getElementById('div_button_resolve_' + this.comment_icon_id + '_' + uuid).classList.remove('button-hidden')
        }
        else {
            document.getElementById('div_button_resolve_' + this.comment_icon_id + '_' + uuid).classList.add('button-hidden')
        }
        document.getElementById('button_resolve_' + this.comment_icon_id + '_' + uuid).onclick = e => {
            this.update_comment(uuid, 'RESOLU')
        }

        // button 'Ré-ouvrir'
        if (comment_statut == 'RESOLU') { //  || (comment_statut == 'CLOS' && is_instructeur)
            document.getElementById('div_button_reopen_' + this.comment_icon_id + '_' + uuid).classList.remove('button-hidden')
        }
        else {
            document.getElementById('div_button_reopen_' + this.comment_icon_id + '_' + uuid).classList.add('button-hidden')
        }
        document.getElementById('button_reopen_' + this.comment_icon_id + '_' + uuid).onclick = e => {
            this.update_comment(uuid, 'OUVERT')
        }

        // button 'Enregistrer'
        if (comment_statut == 'OUVERT' && (is_owner && is_owner != 'False')) {
            document.getElementById('div_button_save_' + this.comment_icon_id + '_' + uuid).classList.remove('button-hidden')
        }
        else {
            document.getElementById('div_button_save_' + this.comment_icon_id + '_' + uuid).classList.add('button-hidden')
        }
        document.getElementById('button_save_' + this.comment_icon_id + '_' + uuid).onclick = e => {
            this.update_comment(uuid)
        }
    }



    disable_textarea(uuid, status, is_owner) {
        const textarea_div = document.getElementById("comment_" + this.comment_icon_id + '_' + uuid)
        if (is_owner && is_owner != 'False' && status == 'OUVERT') {
            textarea_div.disabled = false
        }
        else {
            textarea_div.disabled = true
        }
    }

    update_status(uuid, status) {
        const status_span = document.getElementById("comment_status_" + this.comment_icon_id + '_' + uuid)
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

    _hide_textarea_for_close_comment(comment_uuid) {
        var common_textarea_div = document.getElementById("comment_textarea_div_" + this.comment_icon_id + '_' + comment_uuid)
        var comment_container = document.getElementById("comment_container_" + this.comment_icon_id + '_' + comment_uuid)
        common_textarea_div.hidden = true
        comment_container.classList.add('clickable')
        comment_container.addEventListener('click', function(){
            common_textarea_div.hidden = !common_textarea_div.hidden
        })
    }

    display_comment_icon() {
        status_name = this.comment_icon_id + "_comment_statut"
        statuts = document.getElementsByName(status_name)
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

        this.update_comment_icon(nb_open, nb_resolu, nb_clos)
    }

    display_global_comment_icon() {
        this.get_comments( res => {
            if (res.success) {
                var nb_open = 0
                var nb_resolu = 0
                var nb_clos = 0
                for (var i = 0; i < res.comments.length; i++) {
                    if (res.comments[i].statut == 'OUVERT') {
                        nb_open += 1
                    }
                    if (res.comments[i].statut == 'RESOLU') {
                        nb_resolu += 1
                    }
                    if (res.comments[i].statut == 'CLOS') {
                        nb_clos += 1
                    }
                }

                this.update_comment_icon(nb_open, nb_resolu, nb_clos)

            }
        })

    }

    update_comment_icon(nb_open, nb_resolu, nb_clos){
        var comment_icon = document.getElementById(this.comment_icon_id)
        var parent_parent = comment_icon.parentNode.parentNode
        if (nb_open) { // blue & displayed
            comment_icon.classList.add('content__icons--blue')
            comment_icon.classList.remove('content__icons--green')
            comment_icon.classList.remove('content__icons--grey')
            comment_icon.classList.remove('content__icons--darkgrey')
            comment_icon.hidden = false
            // specific, pourrait être passé en callback
            if ((parent_parent.tagName == 'TR' || parent_parent.tagName == 'TH') && document.getElementById('download_upload_block') !== null) {
                    document.getElementById('download_upload_block').hidden = false
            }
            if (document.getElementById('save_after_comments') !== null) {
                document.getElementById('save_after_comments').hidden = false
                document.getElementById('back_to_recap').hidden = true
            }

            // NOT APPLICABLE FOR GLOBAL COMMENT
            // if (document.getElementById(input_id) !== null) {
            //     document.getElementById(input_id).disabled = false
            // }
            // else {
            //     // manage checkbox
            //     inputs = comment_icon.parentNode.getElementsByTagName('input')
            //     for (var i = 0; i< inputs.length;i++) {
            //         inputs[i].disabled = false
            //     }
            // }

            // // row in a table
            // parent_parent = comment_icon.parentNode.parentNode
            // if (parent_parent.tagName == 'TR') {
            //     inputs = parent_parent.getElementsByTagName('input')
            //     for (var i = 0; i< inputs.length;i++) {
            //         inputs[i].disabled = false
            //     }
            //     inputs = parent_parent.getElementsByTagName('select')
            //     for (var i = 0; i< inputs.length;i++) {
            //         inputs[i].disabled = false
            //     }
            //     if (document.getElementById('download_upload_block') !== null) {
            //         document.getElementById('download_upload_block').hidden = false
            //     }
            // }
            // if (document.getElementById(this.input_div_id) !== null) {
            //     document.getElementById(this.input_div_id).onclick = null
            //     document.getElementById(this.input_div_id).onmouseover = null
            //     document.getElementById(this.input_div_id).onmouseleave = null
            // }

        }
        else if (nb_resolu && !nb_open) { // green & displayed
            comment_icon.classList.remove('content__icons--blue')
            comment_icon.classList.add('content__icons--green')
            comment_icon.classList.remove('content__icons--grey')
            comment_icon.classList.remove('content__icons--darkgrey')
            comment_icon.hidden = false
            if ((parent_parent.tagName == 'TR' || parent_parent.tagName == 'TH') && document.getElementById('download_upload_block') !== null) {
                document.getElementById('download_upload_block').hidden = false
            }
            // NOT APPLICABLE FOR GLOBAL COMMENT
            // parent_parent = comment_icon.parentNode.parentNode
            // if (document.getElementById(this.input_div_id) !== null) {
            //     document.getElementById(this.input_div_id).onclick = null
            //     document.getElementById(this.input_div_id).onmouseover = null
            //     document.getElementById(this.input_div_id).onmouseleave = null
            // }

        }
        else if (nb_clos && !nb_resolu && !nb_open) { // grey & displayed
            comment_icon = document.getElementById(this.comment_icon_id)
            comment_icon.classList.remove('content__icons--blue')
            comment_icon.classList.remove('content__icons--green')
            comment_icon.classList.add('content__icons--grey')
            comment_icon.classList.remove('content__icons--darkgrey')
            comment_icon.hidden = false
            // NOT APPLICABLE FOR GLOBAL COMMENT
            // parent_parent = comment_icon.parentNode.parentNode
            // if (document.getElementById(this.input_div_id) !== null) {
            //     document.getElementById(this.input_div_id).onclick = null
            //     document.getElementById(this.input_div_id).onmouseover = null
            //     document.getElementById(this.input_div_id).onmouseleave = null
            // }
        }
        else { // blue & hidden
            comment_icon = document.getElementById(this.comment_icon_id)
            comment_icon.classList.add('content__icons--blue')
            comment_icon.classList.remove('content__icons--green')
            comment_icon.classList.remove('content__icons--grey')
            comment_icon.classList.remove('content__icons--darkgrey')
            // NOT APPLICABLE FOR GLOBAL COMMENT
            // if (document.getElementById(this.input_div_id) !== null) {
            //     document.getElementById(this.input_div_id).onclick = e => {
            //         document.getElementById(this.comment_icon_id).hidden=false
            //     }
            //     document.getElementById(this.input_div_id).onmouseover = e => {
            //         document.getElementById(this.comment_icon_id).hidden=false
            //     }
            //     document.getElementById(this.input_div_id).onmouseleave = function(){
            //         document.getElementById(this.comment_icon_id).hidden=true
            //     }
            // }
        }
    }

    /*
    * Functions which call backend
    */

    // get comments
    get_comments(callback) {
        var headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        fetch('/comments/convention/'+this.convention_uuid+'?'+ new URLSearchParams({
            object_name: this.object_name,
        }) , {
            method: 'get',
            headers: headers,
        }).then(function(response) {
            if (response.status == 200) {
                var res = response.json()
                return res;
            }
        }).then(res => {
            callback(res)
        });
    }


    // Create a new comment
    create_comment() {
        var comment =  document.getElementById('textarea_' + this.comment_dialog_id)
        var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value

        var headers = {
            'X-CSRFToken': csrf_token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        fetch('/comments/', {
            method: 'post',
            headers: headers,
            body: JSON.stringify({
                comment: comment.value,
                object_name : this.object_name,
                object_field : this.object_field,
                object_uuid : this.object_uuid,
                convention_uuid : this.convention_uuid
            })
        }).then(function(response) {
            if (response.status == 200) {
                var res = response.json()
                return res;
            }
        }).then(res => {
            if (res.success) {
                this.create_global_comment_input(res.comment, res.user.is_instructeur)
                this.display_comment_icon()
            }
            comment.value = ''
        });

    }

    // update comment (including status)
    update_comment(uuid, status) {
        var message = document.getElementById("comment_" + this.comment_icon_id + '_' + uuid).value
        var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value
        var body_content = {
            'message': message
        }
        if (status !== null) {
            body_content['statut'] = status
        }

        var headers = {
            'X-CSRFToken': csrf_token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        fetch('/comments/' + uuid, {
            method: 'post',
            headers: headers,
            body: JSON.stringify(body_content)
        }).then(function(response) {
            if (response.status == 200) {
                return response.json();
            }
        }).then(res => {
            if (res.success)
            {
                var comment = res.comment
                document.getElementById('comment_statut_' + this.comment_icon_id + '_' + comment.uuid).value = res.comment.statut
                this.init_comment_button(comment.uuid, comment.statut, comment.is_owner, res.user.is_instructeur)
                this.disable_textarea(comment.uuid, comment.statut, comment.is_owner)
                this.update_status(comment.uuid, comment.statut)
                if (comment.is_owner && comment.statut == 'CLOS') {
                    document.getElementById('textarea_' + this.comment_dialog_id).value = ''
                }
                if (status == 'CLOS') {
                    this._hide_textarea_for_close_comment(comment.uuid)
                }
                this.display_comment_icon()

                document.getElementById('comment_date_' + this.comment_icon_id + '_' + uuid).innerText = 'le ' + this.format_french_date(res.comment.mis_a_jour_le) + ' (Enregistré)'
                setTimeout(e => {
                    document.getElementById('comment_date_' + this.comment_icon_id + '_' + uuid).innerText = 'le ' + this.format_french_date(res.comment.mis_a_jour_le)
                }, 5000);


            }
        });
    }


    /*
    * End functions which call backend
    */

    format_french_date(date) {
        return new Date(date).toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour:'2-digit', minute:'2-digit' })
    }

    /*
     * Create html blocks
     */

    //div container
    create_comment_container(uuid) {
        const container_div = document.createElement('div');
        container_div.setAttribute('id','comment_container_' + this.comment_icon_id + '_' + uuid)
        return container_div
    }

    //<div class="fr-mt-3w"><b>Raphaëlle Neyton (vous) :</b></div>
    create_comment_owner(uuid, username, is_owner, status) {
        const owner_div = document.createElement('div');
        owner_div.classList.add('fr-mt-3w')
        owner_div.classList.add('block--row-strech')

        const owner_span = document.createElement('span');
        owner_span.classList.add('block--row-strech-1')
        owner_span.classList.add('text-bold')
        var inner_text = username
        if (is_owner && is_owner != 'False') {
            inner_text = inner_text + " (vous)"
        }
        inner_text = inner_text + " : "
        owner_span.innerText = inner_text
        owner_div.appendChild(owner_span)

        const status_span = document.createElement('span');
        status_span.setAttribute('id','comment_status_' + this.comment_icon_id + '_' + uuid)
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
    create_comment_date(uuid, date) {
        const date_div = document.createElement('div');
        date_div.setAttribute('id','comment_date_' + this.comment_icon_id + '_' + uuid)
        date_div.classList.add('fr-text-sm')
        date_div.classList.add('text-italic')
        date_div.innerText = "le " + this.format_french_date(date)
        return date_div
    }

    //<input type="hidden" value="fb7d6bf9-291a-4b3d-b2a6-25fea7e20dcb">
    create_comment_uuid(uuid) {
        const uuid_div = document.createElement('input');
        uuid_div.setAttribute('type', "hidden")
        uuid_div.value = uuid
        return uuid_div
    }

    //<input type="hidden" value="fb7d6bf9-291a-4b3d-b2a6-25fea7e20dcb">
    create_comment_statut(uuid, statut) {
        const statut_div = document.createElement('input');
        statut_div.setAttribute('id','comment_statut_' + this.comment_icon_id + '_' + uuid)
        statut_div.setAttribute('name', this.comment_icon_id + "_comment_statut")
        statut_div.setAttribute('type', "hidden")
        statut_div.value = statut
        return statut_div
    }

    //<textarea class="fr-input" aria-describedby="text-input-error-desc-error" type="text" id="comment_fb7d6bf9-291a-4b3d-b2a6-25fea7e20dcb" rows="5">tt</textarea>
    create_comment_textarea(uuid, message, status, is_owner=false) {
        const textarea_div = document.createElement('div');
        textarea_div.setAttribute('id', "comment_textarea_div_" + this.comment_icon_id + '_' + uuid)
        const textarea_textarea = document.createElement('textarea');
        textarea_textarea.classList.add('fr-input')
        textarea_textarea.setAttribute('aria-describedby', "text-input-error-desc-error")
        textarea_textarea.setAttribute('type', "text")
        if (is_owner && is_owner != 'False' && status == 'OUVERT') {
            textarea_textarea.disabled = false
        }
        else {
            textarea_textarea.disabled = true
        }
        textarea_textarea.setAttribute('id', "comment_" + this.comment_icon_id + '_' + uuid)

        textarea_textarea.addEventListener('input', function() {
            var rows = this.value.split(/\r\n|\r|\n/).length
            this.setAttribute('rows', rows)
        })

        textarea_textarea.value = message
        textarea_textarea.setAttribute('rows', message.split(/\r\n|\r|\n/).length)

        textarea_div.appendChild(textarea_textarea)
        return textarea_div
    }

    // <ul class="fr-mt-1w fr-btns-group fr-btns-group--right fr-btns-group--inline-reverse fr-btns-group--inline-lg fr-btns-group--icon-left fr-btns-group--sm">
    //     <li id="div_button_close_96c201c0-c0ce-4400-9b73-09803961e6a1" class="button-hidden">
    //         <button id="comment_close_96c201c0-c0ce-4400-9b73-09803961e6a1" type="button" class="fr-btn fr-btn--sm fr-btn--grey">Marquer comme clos</button>
    //     </li>
    //     .....
    // </ul>
    create_comment_button(uuid) {
        const ul_buttons = document.createElement('ul')
        ul_buttons.classList.add('fr-mt-1w', 'fr-btns-group', 'fr-btns-group--right', 'fr-btns-group--inline-reverse', 'fr-btns-group--inline-lg', 'fr-btns-group--icon-left', 'fr-btns-group--sm')
        ul_buttons.appendChild(this.create_li_button(uuid, 'close', 'Marquer comme clos', 'fr-btn--grey'))
        ul_buttons.appendChild(this.create_li_button(uuid, 'resolve', 'Marquer comme résolu', 'fr-btn--green'))
        ul_buttons.appendChild(this.create_li_button(uuid, 'reopen', 'Ré-ouvrir'))
        ul_buttons.appendChild(this.create_li_button(uuid, 'save', 'Modifier'))
        return ul_buttons
    }

    // <li id="div_button_close_96c201c0-c0ce-4400-9b73-09803961e6a1" class="button-hidden">
    //     <button id="button_close_96c201c0-c0ce-4400-9b73-09803961e6a1" type="button" class="fr-btn fr-btn--sm fr-btn--grey">Marquer comme clos</button>
    // </li>
    create_li_button(uuid, action, label, additionalButtonClass=null) {
        const button_action = document.createElement('button')
        button_action.setAttribute('id', 'button_' + action + '_' + this.comment_icon_id + '_' + uuid)
        button_action.setAttribute('type', 'button')
        button_action.classList.add('fr-btn', 'fr-btn--sm')
        if (additionalButtonClass != null) {
            button_action.classList.add(additionalButtonClass)
        }
        button_action.innerText = label
        const li_action = document.createElement('li')
        li_action.setAttribute('id', 'div_button_' + action + '_' + this.comment_icon_id + '_' + uuid)
        li_action.appendChild(button_action)
        return li_action
    }

    /*
     * End create html blocks
     */

}
