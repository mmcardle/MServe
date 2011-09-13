// http://aquantum-demo.appspot.com/file-upload

$(function () {
    $('#file_upload').fileUploadUI({
        sequentialUploads : true,
        maxChunkSize:10000000,
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

