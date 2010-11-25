

function make_drop_upload(item,serviceid){
    $(item).fileUpload(
            {

                    url: "/serviceapi/create/"+serviceid+"/",
                    type: 'POST',
                    dataType: 'json',
                    beforeSend: function () {
                            var p = $("<div class='spinner' id='spinner-"+this.r+"' >"+this.file.name+", "+this.file.size+" bytes</div>")
                            $("#progressbox").append(p);
                            p.show('slide');
                    },
                    complete: function () {
                            $("#spinner-"+this.r).hide('slide');
                    },
                    success: function (result, status, xhr) {
                            if (!result) {
                                    showError('Server error.');
                                    return;
                            }
                            load_stager(result.id);
                            
                    }
            }
    );
}

function load_stager(stagerid){
         $.ajax({
           type: "GET",
           url: "/stagerapi/thumb/"+stagerid+"/",
           success: function(msg){
                $("#stagerlist").prepend(msg);
                $("#image-"+stagerid).show('bounce')
           },
           error: function(msg){
                showError( "Failure to get stager thumb " );
           }
         });
}

function objectToString(ob){
    var output = '';
    for (property in ob) {
        //alert(typeof ob[property])
      if (typeof ob[property] == 'object'){
            //output += property + ': ' + objectToString(ob[property]) +'';
      }else{
            
      }
      output += "<b>"+property + '</b>: ' + ob[property]+'<br /><br /><br />';
    }
    return output;
}

function stager_delete(stagerid){
    $( '#dialog-stager-dialog' ).dialog({
            resizable: false,
            modal: true,
            buttons: {
                    "Delete stager?": function() {
                         $.ajax({
                           type: "DELETE",
                           url: '/stager/'+stagerid+"/",
                           success: function(msg){
                                showMessage("File Deleted","The Stager has been deleted.")
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

function stager_get(stagerid){
        window.open("/stagerapi/get/"+stagerid+"/")
}


function stager_file_corrupt(stagerid){
     $.ajax({
       type: "PUT",
       url: '/stagerapi/corrupt/'+stagerid+"/",
       success: function(msg){
            showMessage("File Corrupted","The file has been corrupted.")
       },
       error: function(msg){
            showError("Failed Corruption","Failed to corrupt the file, Status: " + msg.status+ "Response Text:" + msg.responseText)
       }
     });
 }

function stager_backup_corrupt(stagerid){
     $.ajax({
       type: "PUT",
       url: '/stagerapi/corruptbackup/'+stagerid+"/",
       success: function(msg){
            showMessage("File Corrupted","The file has been corrupted.")
       },
       error: function(msg){
            showError("Failed Corruption","Failed to corrupt the file, Status: " + msg.status+ "Response Text:" + msg.responseText)
       }
     });
 }

function showMessage(title,message){
     var html = "<div id='dialog-message-stager-delete' title='"+title+"'><p><span class='ui-icon ui-icon-circle-check' style='float:left; margin:0 7px 50px 0;'></span>"+message+"</p></div>"
     $( html ).dialog({
            modal: true,
            buttons: {
                    Ok: function() {
                            $( this ).dialog( "close" );
                    }
            }
    });
}



function showError(title,message){
    var html =  "<div id='dialog-message-stager-delete' title='"+title+"'><div class='ui-state-error ui-corner-all' style='padding: 0 .7em;'><p><span class='ui-icon ui-icon-alert' style='float: left; margin-right: .3em;'></span> <strong>Alert:</strong>"+message+"</p><div></div>"
     $( html ).dialog({
            modal: true,
            buttons: {
                    Ok: function() {
                            $( this ).dialog( "close" );
                    }
            }
    });
}


function getPoster(stagerid){
    url = '/stager/'+stagerid+'/'
    $.getJSON(url, function(data) {
        if(data.poster!=""){
            $("#stagerposter").attr("src", "/mservethumbs/"+data.poster)
        }else{
            window.setTimeout("getPoster(\'"+stagerid+"\')",1000)
            //id = $("<div >Thumb doesnt exist "+data.thumb.file+" "+data.thumb.file+"</div>&nbsp;")
            //$(id).appendTo("#debug");
        }
    });
 }

 function stager_verify(stagerid){
     url = '/stagerapi/verify/'+stagerid+'/'
     $.getJSON(url, function(data) {
        if(data.md5==data.stager.checksum){
            showMessage("Success: Verification OK","MD5: "+data.md5+"<br>Checksum: "+data.stager.checksum)
            //id = $("<div class='passed'><div>Success: Verification OK</div>"+ data.md5 + "</div>")
            //$(id).appendTo("#message");
        }else{
            showError("Error: Verification has failed","MD5: "+data.md5+"<br>Checksum: "+data.stager.checksum)
        }
    });
 }