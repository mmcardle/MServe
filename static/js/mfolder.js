function showfolder(folderid){
    if(folderid){
        var items= $('li.'+folderid)
        $('#qscontainer').quicksand( items );
    }else{
        
        $('#qscontainer').quicksand( $('li.rootfolder') );
    }

}

function showfile(fileid){
    if(fileid){
        var items= $('li.'+fileid)
        $('#qscontainer').quicksand( items );
    }else{
        $('#qscontainer').empty()
        $('#qscontainer').quicksand( $('li.rootfolder') );
    }

}

function loadMFolders(serviceid){

     $.ajax({
       type: "GET",
       url: '/services/'+serviceid+"/",
       success: function(service){

            $("#mfileTemplate").tmpl(service.mfile_set).appendTo("#mfilecontainer")
            $("#mfolderTemplate").tmpl(service.mfolder_set).appendTo("#mfoldercontainer")
            showfolder()


            $("#mfoldertreecontainer").jstree({
                 "json_data" : service.folder_structure,
                 "themes" : { "theme" : "default" },
                "plugins" : [ "themes", "json_data", "ui" ]
                }
            ).bind("select_node.jstree", function (event, data) {
                    id = data.rslt.obj.attr('id');
                    mfile = $("#mfileholder-"+id)
                    if(mfile.length>0){
                        showfile(id)
                    }else{
                        mfolder = $("#mfolderholder-"+id)
                        if(mfolder){
                            //$("#mfolderitemcontainer").children().appendTo($("#mfolderhiddencontainer"))
                            //$("#mfolderitemcontainer").append(mfolder)
                            showfolder(id)
                        }
                    }
                    
            });
       }
     });
}

function create_mfolder_paginator(mfolders){

        var mfoldercontainer = $("#mfoldercontainer")
        $(mfolders).each( function(index,mfolder){
            $("#mfolderTemplate").tmpl(mfolder).appendTo(mfoldercontainer)
            $("#mfolderholder-"+mfolder.id).click( function(){ console.log(mfolder) } )
        } )


}