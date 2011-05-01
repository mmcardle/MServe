
$(function () {
    $('#file_upload').fileUploadUI({
        uploadTable: $('#files'),
        buildUploadRow: function (files, index) {
            return $( "#mfileUploadTemplate" ).tmpl( files[index] )

        },
        buildDownloadRow: function (file) {
            loadMFile(file)
            return $( "#mfileUploadCompleteTemplate" ).tmpl( file )
        }
    });
});

