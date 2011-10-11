// http://aquantum-demo.appspot.com/file-upload

$(function () {
    $('#file_upload').fileUploadUI({
        sequentialUploads : true,
        maxChunkSize:10000000,
        uploadTable: $('#files'),
        buildUploadRow: function (files, index) {
            mfile = files[index]
            return $( "#mfileUploadTemplate" ).tmpl( mfile )
        },
        buildDownloadRow: function (mfile) {
            if( mfile.error){
                 failed = $( "#mfileUploadFailedTemplate" ).tmpl( mfile )
                 $(failed).find(".ui-icon-cancel").click(function (){ failed.remove() } )
                 return failed
            }
            loadMFile(mfile)
            return $( "#mfileUploadCompleteTemplate" ).tmpl( mfile )
        }
    });
});

