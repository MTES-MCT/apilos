Dropzone.autoDiscover = false;

let main_response = undefined;
function init_dropzone_from_file(form_id, csrf_token, convention_uuid) {
    let myDropzone = new Dropzone("div#"+form_id+"_dropzone", {
        url: "/upload/",
        uploadMultiple: true,
        maxFilesize: 4, // 4 Mo = 4194304o
        acceptedFiles: 'image/*,application/pdf',
        addRemoveLinks: true,
        init: function () {
            this.on("removedfile", function (file) {
                let files = {};
                if (document.getElementById(form_id).value) files = JSON.parse(document.getElementById(form_id).value);
                delete files[file.uuid]
                document.getElementById(form_id).value = JSON.stringify(files);
            })
            this.on("success", function (file, response) {
                //console.log(file)
                if (document.querySelector('img[alt="'+file.name+'"]') != null ) {
                    file.thumbnail = document.querySelector('img[alt="'+file.name+'"]').src;
                }
                main_response = response;
                for (var i = 0; i < response.uploaded_file.length; i++) {
                    if (response.uploaded_file[i].filename == file.name) {
                        file.uuid = response.uploaded_file[i].uuid
                    }
                }
                let files = {};
                console.log(form_id)
                if (document.getElementById(form_id).value) files = JSON.parse(document.getElementById(form_id).value);
                if (files.constructor !== Object) files = {}
                if (files[file.uuid] === undefined) files[file.uuid] = {'uuid':file.uuid,'thumbnail' : file.thumbnail};
                document.getElementById(form_id).value = JSON.stringify(files);
            })
        },
        dictInvalidFileType: "Il n'est pas possible de téléverser ce fichier, seul les Images et PDF sont acceptées",
        dictDefaultMessage: "Cliquez dans la zone ou déposez-y vos fichiez",
        dictFallbackMessage: "Votre navigateur ne support pas la fonction drag'n'drop. Nous vous conseillons de changer de navigateur",
        dictFallbackText: "",
        dictFileTooBig: "Le fichier est trop gros, il ne doit pas dépasser 4Mo.",
        dictInvalidFileType: "Il n'est pas possible de téléverser ce fichier, seul les Images et PDF sont acceptées",
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
    myDropzone.options.thumbnail.call(myDropzone, mockFile, thumbnail_url);
    myDropzone.emit("complete", mockFile);
}
