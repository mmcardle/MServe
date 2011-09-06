
var $allcontent

function doQuicksand(itemid) {

    if(itemid){
        var $filteredData = $allcontent.find('li.'+itemid);
    }else{
        console.log("done")
        var $filteredData = $allcontent.find('li.rootfolder');
    }

    // finally, call quicksand
    $('#qscontainer').quicksand($filteredData, {
      duration: 800,
      easing: 'easeInOutQuad'
    });

}

function loadMFolders(serviceid){

     $.ajax({
       type: "GET",
       url: '/services/'+serviceid+"/",
       success: function(service){

            $("#mfolderTemplate").tmpl(service.mfolder_set).appendTo("#qscontainer")
            $("#mfileTemplate").tmpl(service.mfile_set).appendTo("#qscontainer")

            $(service.mfile_set).each( function(index,mfile) { doMFileButtons(mfile) } );

            $allcontent = $('#qscontainer').clone(true);

            doQuicksand()

            $("#mfoldertreecontainer").jstree({
                 "json_data" : service.folder_structure,
                 "themes" : { "theme" : "default" },
                 "plugins" : [ "themes", "json_data", "ui", "crrm"]
                }
            ).bind("select_node.jstree", function (event, data) {
                    id = data.rslt.obj.attr('id');
                    if(id==serviceid){
                        doQuicksand()
                    }else{
                        mfile = $("#mfileholder-"+id)
                        console.log(id)
                        if(mfile.length>0){
                            doQuicksand(id)
                        }else{
                            mfolder = $("#mfolderholder-"+id)
                            if(mfolder){
                                doQuicksand(id)
                            }
                        }
                    }
                    
            }).bind("loaded.jstree", function (event, data) {
                $("#mfoldertreecontainer").jstree("open_all");
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