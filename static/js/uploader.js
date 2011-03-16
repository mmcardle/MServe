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

        alert(file.getAsBinary().length + " : "+file.size)

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
          //xhr.r = "r-"+parseInt(Math.random()*(2 << 16));
          //xhr.upload.addEventListener('loadstart', onloadstartHandler, false);
          //xhr.upload.addEventListener('progress', onprogressHandler, false);
          //xhr.upload.addEventListener('load', onloadHandler, false);
          xhr.addEventListener('readystatechange', onreadystatechangeHandler, false);

        xhr.open("POST", url, true);
        var contentType = "multipart/form-data; boundary=" + boundary;
        xhr.setRequestHeader("X-File-Name", file.name);
        xhr.setRequestHeader("Content-Type", contentType);

        for (var header in this.headers) {
            xhr.setRequestHeader(header, headers[header]);
        }

        // finally send the request as binary data
        //xhr.sendAsBinary(this.buildMessage(boundary, file));

        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        //xhr.setRequestHeader("Content-Type", "application/octet-stream");

        xhr.sendAsBinary(this.buildMessage(boundary, file));
        //xhr.sendAsBinary(file);
        //xhr.send(file);

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
               $("#progress-"+xhr.r).progressbar({
                value: 0
              });
          }

          function onloadHandler(evt) {
              $("#status-"+xhr.r).html("<img src='/mservemedia/images/busy.gif' />Processing...");
              var percent = parseInt(evt.loaded/evt.total*100);
              $("#spinner-"+xhr.r).html(xhr.info.shortname+", "+size+"b "+percent+"%");
              $("#progress-"+xhr.r).progressbar({
                value: percent
              });
          }

          function onprogressHandler(evt) {
              $("#testprogress").append("<div>Progress: "+evt.total + " " + evt.loaded + " " + evt.lengthComputable+"</div>");
              var percent = parseInt(evt.loaded/evt.total*100);
              $("#spinner-"+xhr.r).html(xhr.info.shortname+", "+size+"b "+percent+"%");
              $("#progress-"+xhr.r).progressbar({
                value: percentdo
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
                reloadMFiles(mfile.id)
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
                    file = ev.originalEvent.dataTransfer.files[0]
                    
                    //showMessage("message","file.getAsBinary().length "+file.getAsBinary().length +""
                    //    + "<br/>file.getAsText('UTF-8').length"+file.getAsText('UTF-8').length+""
                    //    + "<br/>file.getAsDataURL().length"+file.getAsDataURL().length+""
                    //    + "<br/>file.size "+file.size)

                    if(file.getAsBinary().length == file.size){
                        doUpload(ev.originalEvent.dataTransfer.files[0],serviceid)
                    }else{
                        showError("Upload Error","<p>File of size <b>"+formatSize(file.size)+"</b> cannot be uploaded by Firefox.</p><p>Try using the html form or a different browser (Chrome)");
                    }
                    return false;
            }
    );
}

function TryMozFileUpload(service, file) {
  var xhr = new XMLHttpRequest();
  this.xhr = xhr;
  var self = this;
  xhr.open("POST", service);
  xhr.overrideMimeType('text/plain; charset=x-user-defined-binary');
  xhr.sendAsBinary(file.getAsBinary());
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
                            reloadMFiles(result.id)
                    }
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