Dropzone.autoDiscover = false;

function init_dropzone_from_file(form_id, csrf_token, convention_uuid, accepted_files) {
    if (accepted_files == undefined ) accepted_files = 'image/*,application/pdf'
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
                console.log(file)
                console.log(errorMessage)
                var error = document.createElement("p");
                error.classList.add('fr-error-text')
                error.appendChild(document.createTextNode(errorMessage))
                document.getElementById(form_id + '_errors').appendChild(error)
            })
            this.on("queuecomplete", function() {
                console.log('all_files_uploaded');
            });
            this.on("success", function (file, response) {
                    if (document.querySelector('img[alt="'+file.name+'"]') != null ) {
                    file.thumbnail = document.querySelector('img[alt="'+file.name+'"]').src;
                }
                for (var i = 0; i < response.uploaded_file.length; i++) {
                    if (response.uploaded_file[i].filename == file.name) {
                        file.uuid = response.uploaded_file[i].uuid
                    }
                }
                let files = {};
                if (document.getElementById(form_id).value) files = JSON.parse(document.getElementById(form_id).value);
                if (files.constructor !== Object) files = {}
                if (files[file.uuid] === undefined) files[file.uuid] = {
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
        params: { convention: convention_uuid }
    });
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
