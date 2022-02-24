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
<div id="' + this.comment_icon_id + '">\
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
        const container_div = create_comment_container(comment.uuid)
        const owner_div = create_comment_owner(comment.uuid,comment.username, comment.is_owner, comment.statut);
        container_div.appendChild(owner_div)
        const date_div = create_comment_date(comment.uuid,comment.mis_a_jour_le);
        container_div.appendChild(date_div)
        const uuid_div = create_comment_uuid(comment.uuid);
        container_div.appendChild(uuid_div)
        const statut_div = create_comment_statut(this.comment_dialog_id, comment.uuid, comment.statut);
        container_div.appendChild(statut_div)
        const textarea_div = create_comment_textarea(comment.uuid, comment.message, comment.statut, comment.is_owner);
        container_div.appendChild(textarea_div)
        const ul_buttons = create_comment_button(comment.uuid)
        container_div.appendChild(ul_buttons)
        document.getElementById(inside_id).append(container_div)

        this.init_comment_button(comment.uuid, comment.statut, comment.is_owner, is_instructeur)

        if (comment.statut == 'CLOS') {
            _hide_textarea_for_close_comment(comment.uuid)
        }
    }


    init_comment_button(uuid, comment_statut, is_owner, is_instructeur) {
        // button 'Marquer comme clos'
        if (is_instructeur && comment_statut != 'CLOS') {
            document.getElementById('block_comment_close_' + uuid).classList.remove('button-hidden')
        }
        else {
            document.getElementById('block_comment_close_' + uuid).classList.add('button-hidden')
        }
        document.getElementById('comment_close_' + uuid).onclick = e => {
            this.update_status_comment(uuid, 'CLOS')
        }

        // button 'Marquer comme résolu'
        if (comment_statut == 'OUVERT') {
            document.getElementById('block_comment_resolve_' + uuid).classList.remove('button-hidden')
        }
        else {
            document.getElementById('block_comment_resolve_' + uuid).classList.add('button-hidden')
        }
        document.getElementById('comment_resolve_' + uuid).onclick = e => {
            this.update_status_comment(uuid, 'RESOLU')
        }

        // button 'Ré-ouvrir'
        if (comment_statut == 'RESOLU') { //  || (comment_statut == 'CLOS' && is_instructeur)
            document.getElementById('block_comment_reopen_' + uuid).classList.remove('button-hidden')
        }
        else {
            document.getElementById('block_comment_reopen_' + uuid).classList.add('button-hidden')
        }
        document.getElementById('comment_reopen_' + uuid).onclick = e => {
            this.update_status_comment(uuid, 'OUVERT')
        }

        // button 'Enregistrer'
        if (comment_statut == 'OUVERT' && (is_owner && is_owner != 'False')) {
            document.getElementById('block_comment_save_' + uuid).classList.remove('button-hidden')
        }
        else {
            document.getElementById('block_comment_save_' + uuid).classList.add('button-hidden')
        }
        document.getElementById('comment_save_' + uuid).onclick = e => {
            save_comment(uuid)
        }
    }



    disable_textarea(uuid, status, is_owner) {
        const textarea_div = document.getElementById("comment_" + uuid)
        if (is_owner && is_owner != 'False' && status == 'OUVERT') {
            textarea_div.disabled = false
        }
        else {
            textarea_div.disabled = true
        }
    }

    update_status(uuid, status) {
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

    _hide_textarea_for_close_comment(comment_uuid) {
        document.getElementById("comment_textarea_div_" + comment_uuid).hidden = true
        document.getElementById("comment_container_" + comment_uuid).classList.add('clickable')
            document.getElementById("comment_container_" + comment_uuid).addEventListener('click', function(){
                document.getElementById("comment_textarea_div_" + comment_uuid).hidden = !document.getElementById("comment_textarea_div_" + comment_uuid).hidden
        })
    }

    display_comment_icon() {
        status_name = this.comment_dialog_id + "_comment_statut"
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
 * Functions to call backend
 *
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
    update_status_comment(uuid, status) {
        var message = document.getElementById("comment_" + uuid).value
        var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value

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
            }
        });
    }

}


