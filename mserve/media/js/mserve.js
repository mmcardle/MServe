/*
 * Copyright (c) 2008-2009, Ionut Gabriel Stan. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 *    * Redistributions of source code must retain the above copyright notice,
 *      this list of conditions and the following disclaimer.
 *
 *    * Redistributions in binary form must reproduce the above copyright notice,
 *      this list of conditions and the following disclaimer in the documentation
 *      and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

var Uploader = function() {
};

Uploader.prototype = {
    headers : {},

    /**
     * @return Array
     */
    get elements() {
        return [];
    },

    /**
     * @return String
     */
    generateBoundary : function() {
        return "---------------------------" + (new Date).getTime();
    },

    /**
     * @param  Array elements
     * @param  String boundary
     * @return String
     */
    buildMessage : function(boundary, file) {
        var CRLF  = "\r\n";
        var parts = [];

        part = ""

        var fieldName = "file";
        var fileName  = file.name || file.fileName;

        /*
         * Content-Disposition header contains name of the field used
         * to upload the file and also the name of the file as it was
         * on the user's computer.
         */
        part += 'Content-Disposition: form-data; ';
        part += 'name="' + fieldName + '"; ';
        part += 'filename="'+ fileName + '"' + CRLF;

        /*
         * Content-Type header contains the mime-type of the file to
         * send. Although we could build a map of mime-types that match
         * certain file extensions, we'll take the easy approach and
         * send a general binary header: application/octet-stream.
         */
        part += "Content-Type: application/octet-stream" + CRLF + CRLF;

        /*
         * File contents read as binary data, obviously
         */
        //part += element.files[0].getAsBinary() + CRLF;

        part += file.getAsBinary() + CRLF;

        parts.push(part);

        var request = "--" + boundary + CRLF;
            request+= parts.join("--" + boundary + CRLF);
            request+= "--" + boundary + "--" + CRLF;

        return request;
    },

    /**
     * @return null
     */
    send : function(file,url) {
        var boundary = this.generateBoundary();
        var xhr      = new XMLHttpRequest;

          var info = {
                // properties of standard File object || Gecko 1.9 properties
                type: file.type || '', // MIME type
                size: file.size || file.fileSize,
                name: file.name || file.fileName,
                shortname : file.name.substring(0, 10) + "..." || file.fileName.substring(0, 10) + "..."
          };
          xhr.info = info
          xhr.r = "r-"+parseInt(Math.random()*(2 << 16));
          xhr.upload.addEventListener('loadstart', onloadstartHandler, false);
          xhr.upload.addEventListener('progress', onprogressHandler, false);
          xhr.upload.addEventListener('load', onloadHandler, false);
          xhr.addEventListener('readystatechange', onreadystatechangeHandler, false);

        xhr.open("POST", url, true);
        var contentType = "multipart/form-data; boundary=" + boundary;
        xhr.setRequestHeader("X-File-Name", file.name);
        xhr.setRequestHeader("Content-Type", contentType);

        for (var header in this.headers) {
            xhr.setRequestHeader(header, headers[header]);
        }

        // finally send the request as binary data
        xhr.sendAsBinary(this.buildMessage(boundary, file));

          function onloadstartHandler(evt) {
                shortname=xhr.info.shortname
                size=xhr.info.size
                r=xhr.r

                var uploadHtml = "<div class='upload' id='upload-"+r+"' >"
                uploadHtml +=    "<div id='spinner-"+r+"' >"+shortname+", "+size+"b</div>"
                uploadHtml +=    "<div id='status-"+r+"' ><img src='/mservemedia/images/busy.gif' />Upload Progress</div>"
                uploadHtml +=    "<div style='height:10px;' class='progress' id='progress-"+r+"' ></div>"
                uploadHtml +=    "</div>"

                var p = $(uploadHtml)
                $("#progressbox").append(p);
                p.show('slide');
               $('#upload-status').html('Upload started!');
          }

          function onloadHandler(evt) {
                $("#status-"+xhr.r).html("<img src='/mservemedia/images/busy.gif' />Processing...");
          }

          function onprogressHandler(evt) {
              var percent = parseInt(evt.loaded/evt.total*100);
              $("#spinner-"+xhr.r).html(xhr.info.shortname+", "+size+"b "+percent+"%");
              $("#progress-"+xhr.r).progressbar({
                value: percent
              });
          }

          function onreadystatechangeHandler(evt) {
              var status = null;

              try {
                  status = evt.target.status;
              }
              catch(e) {
                  return;
              }

              if (status == '200' && evt.target.responseText && xhr.readyState == 3) {

              }

              if (status == '200' && evt.target.responseText && xhr.readyState == 4) {// Loaded State
                $("#upload-"+xhr.r).hide('slide');
                var mfile = jQuery.parseJSON(evt.target.responseText);
                load_mfile(mfile.id)
              }
          }
    }
};


function make_drop_upload(el,serviceid){
     $(el).bind(
            'dragover', // dragover behavior should be blocked for drop to invoke.
            function(ev) {
                    return false;
            }
    ).bind(
            'drop',
            function (ev) {
                    if (!ev.originalEvent.dataTransfer.files) {
                            log('ERROR: No FileList object present; user might had dropped text.');
                            return false;
                    }
                    if (!ev.originalEvent.dataTransfer.files.length) {
                            log('ERROR: User had dropped a virual file (e.g. "My Computer")');
                            return false;
                    }
                    if (!ev.originalEvent.dataTransfer.files.length > 1) {
                            log('WARN: Multiple file upload not implemented yet, only first file will be uploaded.');
                    }
                    doUpload(ev.originalEvent.dataTransfer.files[0],serviceid)
                    return false;
            }
    );
}

function doUpload(file,serviceid) {
    var uploader  = new Uploader();
    uploader.send(file,"/serviceapi/create/"+serviceid+"/");
}

function supportAjaxUploadWithProgress() {
    return supportFileAPI() && supportAjaxUploadProgressEvents();

    function supportFileAPI() {
        var fi = document.createElement('INPUT');
        fi.type = 'file';
        return 'files' in fi;
    };

    function supportAjaxUploadProgressEvents() {
        var xhr = new XMLHttpRequest();
        return !! (xhr && ('upload' in xhr) && ('onprogress' in xhr.upload));
    };
}

function doUpload__old(file,serviceid) {


  var xhr = new XMLHttpRequest();
  var info = {
        // properties of standard File object || Gecko 1.9 properties
        type: file.type || '', // MIME type
        size: file.size || file.fileSize,
        name: file.name || file.fileName,
        shortname : file.name.substring(0, 10) + "..." || file.fileName.substring(0, 10) + "..."
  };
  xhr.info = info
  xhr.r = "r-"+parseInt(Math.random()*(2 << 16));
  xhr.upload.addEventListener('loadstart', onloadstartHandler, false);
  xhr.upload.addEventListener('progress', onprogressHandler, false);
  xhr.upload.addEventListener('load', onloadHandler, false);
  xhr.addEventListener('readystatechange', onreadystatechangeHandler, false);
  xhr.open('POST', '/serviceapi/create/'+serviceid+'/', true);
  xhr.setRequestHeader("Content-Type", "application/octet-stream");
  //xhr.setRequestHeader("Content-Type", "multipart/form-data");
  xhr.setRequestHeader("X-File-Name", file.name);
  xhr.send(file); // Simple!

  function onloadstartHandler(evt) {
        shortname=xhr.info.shortname
        size=xhr.info.size
        r=xhr.r

        var uploadHtml = "<div class='upload' id='upload-"+r+"' >"
        uploadHtml +=    "<div id='spinner-"+r+"' >"+shortname+", "+size+"b</div>"
        uploadHtml +=    "<div id='status-"+r+"' ><img src='/mservemedia/images/busy.gif' />Upload Progress</div>"
        uploadHtml +=    "<div style='height:10px;' class='progress' id='progress-"+r+"' ></div>"
        uploadHtml +=    "</div>"

        var p = $(uploadHtml)
        $("#progressbox").append(p);
        p.show('slide');
       $('#upload-status').html('Upload started!');
  }

  function onloadHandler(evt) {
        $("#status-"+xhr.r).html("<img src='/mservemedia/images/busy.gif' />Processing...");
  }

  function onprogressHandler(evt) {
      var percent = parseInt(evt.loaded/evt.total*100);
      $("#spinner-"+xhr.r).html(xhr.info.shortname+", "+size+"b "+percent+"%");
      $("#progress-"+xhr.r).progressbar({
        value: percent
      });
  }

  function onreadystatechangeHandler(evt) {
      var status = null;

      try {
          status = evt.target.status;
      }
      catch(e) {
          return;
      }

      if (status == '200' && evt.target.responseText && xhr.readyState == 3) {

      }

      if (status == '200' && evt.target.responseText && xhr.readyState == 4) {// Loaded State
        $("#upload-"+xhr.r).hide('slide');
        var mfile = jQuery.parseJSON(evt.target.responseText);
        load_mfile(mfile.id)
      }
  }
}

function onprogressHandler(evt) {
    var percent = evt.loaded/evt.total*100;
    $('#testprogress').html(""+percent)
}

function make_drop_upload_webkit(item,serviceid){
    $(item).fileUpload(
            {
                    url: "/serviceapi/create/"+serviceid+"/",
                    type: 'POST',
                    dataType: 'json',
                    beforeSend: function () {
                            name=this.info.name
                            size=this.info.size
                            //showMessage("info",objectToString(this.info))
                            r=this.r
                            if (name.length > 13)
                                name = this.info.name.substring(0, 10) + "..."

                            var p = $("<div class='spinner' id='spinner-"+r+"' >"+name+", "+size+"b</div><div class='progress' id='progress-"+r+"' ></div>")
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
                            load_mfile(result.id);
                            
                    }
            }
    );
}

function load_render_preview(mfileid){
         $.ajax({
           type: "GET",
           url: "/mfileapi/getpreview/"+mfileid+"/",
           success: function(msg){
                for ( i in msg.results){
                    var im = $("<div class='renderpreview fluid'><img style='height:40px;width:40px;' src='/mservedata/"+msg.results[i]+"' /></div>")
                    $("#renderpreview").prepend(im);
                }
                //$("#image-"+mfileid).show('bounce')
           },
           error: function(msg){
                $("#renderpreview").prepend(objectToString(msg));
                //showError( "Failure to get mfile preview ",obmsg );
           }
         });
}

function load_mfile(mfileid){
         $("#emptymfilelist").remove();
         $.ajax({
           type: "GET",
           url: "/mfileapi/thumb/"+mfileid+"/",
           success: function(msg){
                $("#mfilelist").prepend(msg);
                $("#image-"+mfileid).show('bounce')
           },
           error: function(msg){
                showError( "Failure to get mfile thumb " );
           }
         });
}

function objectToStringShallow(ob){
    var output = '';
    for (property in ob) {
        //alert(typeof ob[property])
        output += "<b>"+property + '</b>: ' + ob[property]+'<br /><br /><br />';
    }
    return output;
}

function objectToString(ob){
    var output = '';
    for (property in ob) {
        //alert(typeof ob[property])
      if (typeof ob[property] == "object"){
            output += property + ': ' + objectToString(ob[property]) +'';
      }else{
            output += "<b>"+property + '</b>: ' + ob[property]+'<br /><br /><br />';
      }
      
    }
    return output;
}

function load_jobs_service(serviceid){
     $.ajax({
       type: "GET",
       url: '/serviceapi/getjobs/'+serviceid+"/",
       success: function(msg){
            for (i in msg){
                create_job_holder(msg[i].job)
                check_job(msg[i].job,serviceid)
            }
       },
       error: function(msg){
            showError("Render",objectToString(msg))
       }
     });
}

function load_jobs_mfile(mfileid){
     $.ajax({
       type: "GET",
       url: '/mfileapi/getjobs/'+mfileid+"/",
       success: function(msg){
            for (i in msg){
                create_job_holder(msg[i].job)
                check_job(msg[i].job,mfileid)
            }
       },
       error: function(msg){
            showError("Render",objectToString(msg))
       }
     });
}

function create_job_holder(job){
    var jobholder = $("#job-"+job.id)
    if (jobholder.length == 0){

        icon = "<span id='jobicon-"+job.id+"' class='ui-icon ui-icon-circle-check' ></span>"

        jobholder = $("<div id='job-"+job.id+"' class='job' ><h5>"+job.name+", "+job.created+"</h5>"
                   +"<table style='width:100%'><tr>"
                   +"<td>"+icon+"</td>"
                   +"<td ><div id='jobinfo-"+job.id+"' class='jobinfo' ></div></td>"
                   +"<td width='*' ><div style='height:10px;width:30em' id='progressbar-"+job.id+"'></div></td>"
                    +"<tr><table>"
                    +"</div>")
        $("#jobs").prepend(jobholder);
    }
}

function mfile_render(mfileid){
     $.ajax({
       type: "POST",
       url: '/jobapi/render/'+mfileid+"/",
       success: function(msg){
            check_job(msg.job,mfileid)
       },
       error: function(msg){
            showError("Render",objectToString(msg))
       }
     });
}

function delete_job(jobid){
    $( '#dialog-job-dialog' ).dialog({
            resizable: false,
            modal: true,
            buttons: {
                    "Delete Job?": function() {
                              $.ajax({
                               type: "DELETE",
                               url: '/jobapi/'+jobid+"/",
                               success: function(msg){
                                    $('#job-'+jobid).hide('blind')
                               },
                               error: function(msg){
                                    showError("Job Deleted Error",objectToString(msg))
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

function check_job(job,mfileid){
     $.ajax({
       type: "GET",
       url: '/jobapi/'+job.id+"/",
       success: function(msg){
        var allDone = true

        var jobs = $("#job-"+job.id)
        var percent = (msg.completed_count/msg.total)*100
        var info = $( "#jobinfo-"+job.id )
        var icon = $( "#jobicon-"+job.id )
        var progressbar = $( "#progressbar-"+job.id )

        if(msg.waiting){
            icon.addClass('taskrunning')
        }else{
            icon.addClass('ui-icon-check')
            icon.removeClass('taskrunning')
        }

        info.html("<b>"+msg.completed_count+"</b> frames of <b>"+msg.total+"</b> complete : "+Math.round(percent)+"%" )

        progressbar.progressbar({
                value: percent
        });

        if(msg.waiting){
            window.setTimeout(function(){ check_job(job,mfileid) },3000)
        }

       },
       error: function(msg){
            showError("Render",objectToString(msg))
       }
     });
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


function mfile_file_corrupt(mfileid){
     $.ajax({
       type: "PUT",
       url: '/mfileapi/corrupt/'+mfileid+"/",
       success: function(msg){
            showMessage("File Corrupted","The file has been corrupted.")
       },
       error: function(msg){
            showError("Failed Corruption","Failed to corrupt the file, Status: " + msg.status+ "Response Text:" + msg.responseText)
       }
     });
 }

function mfile_backup_corrupt(mfileid){
     $.ajax({
       type: "PUT",
       url: '/mfileapi/corruptbackup/'+mfileid+"/",
       success: function(msg){
            showMessage("File Corrupted","The file has been corrupted.")
       },
       error: function(msg){
            showError("Failed Corruption","Failed to corrupt the file, Status: " + msg.status+ "Response Text:" + msg.responseText)
       }
     });
 }

function showMessage(title,message){
     var html = "<div id='dialog-message-mfile-delete' title='"+title+"'><p><span class='ui-icon ui-icon-circle-check' style='float:left; margin:0 7px 50px 0;'></span>"+message+"</p></div>"
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
    var html =  "<div id='dialog-message-mfile-delete' title='"+title+"'><div class='ui-state-error ui-corner-all' style='padding: 0 .7em;'><p><span class='ui-icon ui-icon-alert' style='float: left; margin-right: .3em;'></span> <strong>Alert:</strong>"+message+"</p><div></div>"
     $( html ).dialog({
            modal: true,
            buttons: {
                    Ok: function() {
                            $( this ).dialog( "close" );
                    }
            }
    });
}


function getPoster(mfileid){
    url = '/mfile/'+mfileid+'/'
    $.getJSON(url, function(data) {
        if(data.poster!=""){
            $("#mfileposter").attr("src", "/mservethumbs/"+data.poster)
        }else{
            window.setTimeout("getPoster(\'"+mfileid+"\')",1000)
            //id = $("<div >Thumb doesnt exist "+data.thumb.file+" "+data.thumb.file+"</div>&nbsp;")
            //$(id).appendTo("#debug");
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