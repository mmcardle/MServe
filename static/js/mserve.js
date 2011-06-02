

function load_user(userurl,consumerurl,template){

     $.ajax({
       type: "GET",
       url: userurl,
       success: function(msg){
            
            if(msg.mfiles.length==0){
                $("#user_mfilemessages" ).append("No Resources")
            }else{
                $("#user_mfilemessages").empty()
            }

            $( template ).tmpl( msg.mfiles ).appendTo( "#user_mfileholder" );
            //$( "#mfolderOAuthTemplate" ).tmpl( msg.mfolders ).appendTo( "#user_mfileholder" );
            //$( "#serviceOAuthTemplate" ).tmpl( msg.dataservices ).appendTo( "#user_mfileholder" );

            oauth_token = getParameterByName("oauth_token")

            $(".infoholder input[type='checkbox']").each(function(index){
                $(this).button().click(
                function(){
                    var id = $(this).attr('id')
                    if($(this).is(':checked')){
                        ajax_update_consumer_oauth(id,oauth_token,consumerurl)
                    }else{
                        ajax_delete_consumer_oauth(id,oauth_token,consumerurl)
                    }
                });
            } );

       },
       error: function(msg){
            showError("Error Loading User",objectToString(msg))
       }
     });
}

function ajax_update_consumer_oauth(id,oauth_token,consumerurl){

    var dataArr = {
        "oauthtoken" : ""+oauth_token+"",
        "id" : ""+id+""
    }

    var data = $.param(dataArr)

     $.ajax({
       type: "PUT",
       url: consumerurl,
       data: data,
       success: function(msg){
            
       },
       error: function(msg){
            showError("Error updating consumer oauth",objectToString(msg))
       }
     });
}

function ajax_delete_consumer_oauth(id,oauth_token,consumerurl){

     $.ajax({
       type: "DELETE",
       url: consumerurl+"/"+id+"/"+oauth_token+"/",
       success: function(msg){

       },
       error: function(msg){
            showError("Error Deleting Consumer OAuth",objectToString(msg))
       }
     });
}

var serviceid = ""
function loadMFiles(sid){
    serviceid = sid
    reloadMFiles();
}

function reloadMFiles(newfileid){
    $.ajax({
       type: "GET",
       url: "/services/"+serviceid+"/mfiles/",
       success: function(msg){
            mfiles = msg;

            if(mfiles.length==0){
                 $("#mfilemessages").append("<div id='nofiles' class='message' >No Files</div>");
                return;
            }else{
                $("#nofiles").remove()
            }

            function handlePaginationClick(new_page_index, pagination_container) {
                // This selects elements from a content array
                start = new_page_index*this.items_per_page
                end   = (new_page_index+1)*this.items_per_page
                if(end>mfiles.length){
                    end=mfiles.length;
                }

                $( "#managedresourcesmfilescontent" ).empty()
                $( "#mfileTemplate" ).tmpl( mfiles.slice(start,end) ) .appendTo( "#managedresourcesmfilescontent" );

                for(var i=start; i<end; i++){
                    (function() {
                        var gid = i;
                        var gmfileid = mfiles[gid].id;
                        $("#newjobbutton-"+gmfileid ).button({ icons: { primary: "ui-icon-transferthick-e-w"}, text: false });
                        $('#newjobbutton-'+gmfileid).click(function(){
                            create_new_job_ui_dialog(gmfileid,true)
                            $("#mfileid").val(gmfileid);
                            $("#dialog-new-job-dialog-form").dialog( "open" );
                        });
                    })();
                }

                if(newfileid != null){
                    $("#image-"+newfileid).show('bounce')
                }

                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object

            // Render the template with the data and insert
            // the rendered HTML under the "mfilepaginator" element
            $("#mfilepaginator").pagination(mfiles.length, {
                    items_per_page:12,
                    callback:handlePaginationClick
            });
       },
       error: function(msg){
            showError( "Failure to get files",msg );
       }
     });
}

function loadMFile(mfile){
    $("#nofiles").remove()
    $("#mfileTemplate" ).tmpl( mfile ) .prependTo( "#managedresourcesmfilescontent" );
    $("#image-"+mfile.id).show('bounce');

    (function() {
        var gid = mfile.id;
        var gmfileid = mfile.id;
        $("#newjobbutton-"+gmfileid ).button({ icons: { primary: "ui-icon-transferthick-e-w"}, text: false });
        $('#newjobbutton-'+gmfileid).click(function(){
            create_new_job_ui_dialog(gmfileid,true)
            $("#mfileid").val(gmfileid);
            $("#serviceid").val(serviceid);
            $("#dialog-new-job-dialog-form").dialog( "open" );
        });
    })();

}

function mfile_delete(mfileid){
    $( '#dialog-mfile-dialog' ).dialog({
            resizable: false,
            modal: true,
            buttons: {
                    "Delete mfile?": function() {
                         $.ajax({
                           type: "DELETE",
                           url: '/mfile/'+mfileid+"/",
                           success: function(msg){
                                showMessage("File Deleted","The mfile has been deleted.")
                           },
                           error: function(msg){
                             alert( "Failure On Delete " + msg );
                           }
                         });
                            $( this ).dialog( "close" );
                    },
                    Cancel: function() {
                            $( this ).dialog( "close" );
                    }
            }
    });
 }

$(document).ready(function(){
	$('.accordion .head').click(function() {
		$(this).next().toggle('slow');
		return false;
	}).next().hide();
});

function mfile_get(mfileid){
        window.open("/mfileapi/get/"+mfileid+"/")
}

function getPoster(mfileid){
    url = '/mfile/'+mfileid+'/'
    $.getJSON(url, function(data) {
        if(data.poster!=""){
            $("#mfileposter").attr("src", "/"+data.posterurl)
        }else{
            window.setTimeout("getPoster(\'"+mfileid+"\')",1000)
        }
    });
 }

 function mfile_verify(mfileid){
     url = '/mfileapi/verify/'+mfileid+'/'
     $.getJSON(url, function(data) {
        if(data.md5==data.mfile.checksum){
            showMessage("Success: Verification OK","MD5: "+data.md5+"<br>Checksum: "+data.mfile.checksum)
            //id = $("<div class='passed'><div>Success: Verification OK</div>"+ data.md5 + "</div>")
            //$(id).appendTo("#message");
        }else{
            showError("Error: Verification has failed","MD5: "+data.md5+"<br>Checksum: "+data.mfile.checksum)
        }
    });
 }

 function add_auth_method(roleid){


    $( '#dialog-mfile-dialog' ).dialog({
            resizable: false,
            modal: true,
            buttons: {
                    "Delete mfile?": function() {
                         $.ajax({
                           type: "DELETE",
                           url: '/mfile/'+mfileid+"/",
                           success: function(msg){
                                showMessage("File Deleted","The mfile has been deleted.")
                           },
                           error: function(msg){
                             alert( "Failure On Delete " + msg );
                           }
                         });
                            $( this ).dialog( "close" );
                    },
                    Cancel: function() {
                            $( this ).dialog( "close" );
                    }
            }
    });

    var methods = prompt("What methods do you wish to add\nComma separated", "");
    if (methods == null)
        return;
    if (methods == "")
        return;
    $.ajax({
       type: "PUT",
       url: '/roles/'+roleid+"/",
       data: "methods="+methods,
       success: function(msg){
           poplulate_methods(roleid,msg["methods"])
       },
       error: function(msg){
         alert( "Failure to add methods '" + methods + "'\nStatus: '" + msg.status+ "'\nResponse Text:\n" + msg.responseText);
       }
     });
 }