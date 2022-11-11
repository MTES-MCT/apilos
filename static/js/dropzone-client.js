
function init_dropzone_from_file(form_id, accepted_files) {
    csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value
    object_name = document.getElementById(form_id + "_object_name").value
    object_uuid = document.getElementById(form_id + "_object_uuid").value
    parameters = {}
    parameters[object_name]= object_uuid
    if (accepted_files == undefined ) {
        accepted_files = 'image/*'
        accepted_files = accepted_files + ',application/pdf'
        // MS: doc, ppt, xls
        accepted_files = accepted_files + ',application/msword,application/vnd.ms-powerpoint,application/vnd.ms-excel'
        // MS openxmlformats : pptx, docx, xlsx
        accepted_files = accepted_files + ',application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        accepted_files = accepted_files + ',application/vnd.openxmlformats-officedocument.presentationml.presentation'
        accepted_files = accepted_files + ',application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        // Opendocument : odp, ods, odt
        accepted_files = accepted_files + ',application/vnd.oasis.opendocument.presentation'
        accepted_files = accepted_files + ',application/vnd.oasis.opendocument.spreadsheet'
        accepted_files = accepted_files + ',application/vnd.oasis.opendocument.text'

    }
    let myDropzone = new Dropzone("div#"+form_id+"_dropzone", {
        url: "/upload/",
        uploadMultiple: true,
        maxFilesize: 100, // 100 Mo
        acceptedFiles: accepted_files,
        addRemoveLinks: true,
        init: function () {
            this.on("removedfile", function (file) {
                let files = {};
                if (document.getElementById(form_id).value) files = JSON.parse(document.getElementById(form_id).value);
                delete files[file.uuid]
                document.getElementById(form_id).value = JSON.stringify(files);
            })
            this.on("error", function (file, errorMessage, xhr) {
                var error = document.createElement("p");
                error.classList.add('fr-error-text')
                error.appendChild(document.createTextNode(errorMessage))
                document.getElementById(form_id + '_errors').appendChild(error)
            })
            this.on("queuecomplete", function() {
                console.log('all_files_uploaded');
            });
            this.on("success", function (file, response) {
                filename = encodeURI(file.name)
                if (document.querySelector('img[alt="'+filename+'"]') != null) {
                    file.thumbnail = document.querySelector('img[alt="'+filename+'"]').src;
                }
                for (var i = 0; i < response.uploaded_file.length; i++) {
                    if (response.uploaded_file[i].filename == filename) {
                        file.uuid = response.uploaded_file[i].uuid
                    }
                }

                let files = {};
                if (document.getElementById(form_id).value) files = JSON.parse(document.getElementById(form_id).value);
                if (files.constructor !== Object) files = {}
                if (files[file.uuid] === undefined && file.uuid !== undefined) files[file.uuid] = {
                    'uuid':file.uuid,
                    'thumbnail' : file.thumbnail,
                    'size': file.size,
                    'filename': file.name
                };
                document.getElementById(form_id).value = JSON.stringify(files);
            })
        },
        dictDefaultMessage: "Cliquez dans la zone ou déposez-y vos fichiers",
        dictFallbackMessage: "Votre navigateur ne support pas la fonction drag'n'drop. Nous vous conseillons de changer de navigateur",
        dictFallbackText: "",
        dictFileTooBig: "Le fichier est trop gros, il ne doit pas dépasser 4Mo.",
        dictInvalidFileType: "Le format du fichier n'est pas accepté",
        dictResponseError: "Le serveur a retourner une erreur, si le problème perpsiste, nous vous prions de contacter votre administration référente",
        dictCancelUpload: "Annuler",
        dictCancelUploadConfirmation: "Etes vous certain de vouloir supprimer ce fichier ?",
        dictRemoveFile: "Supprimer",
        dictMaxFilesExceeded: "Vous ne pouvez plus téléverser d'autres documents",
        headers: {'X-CSRFToken': csrf_token},
        params: parameters
    });
    Dropzone.autoDiscover = false;
    return myDropzone;
}

function init_dropzone_thumbnail(myDropzone, name, size, uuid, thumbnail_url) {
    var mockFile = { name: name, size: size, uuid: uuid };
    myDropzone.options.addedfile.call(myDropzone, mockFile);
    if (thumbnail_url != 'None' && thumbnail_url != undefined) {
        myDropzone.options.thumbnail.call(myDropzone, mockFile, thumbnail_url);
    }
    myDropzone.emit("complete", mockFile);
}

function init_dropzone_list(myDropzone,form_id) {
    let files = {};
    if (document.getElementById(form_id).value) files = JSON.parse(document.getElementById(form_id).value);
    Object.keys(files).forEach(file_uuid => {
        var file = files[file_uuid]
        init_dropzone_thumbnail(myDropzone, file.filename, file.size, file.uuid, file.thumbnail)
    });
}
