
function load_auths(authid){
     $.ajax({
       type: "GET",
       url: '/auths/'+authid+'/',
       success: function(msg){
           $( "#authTemplate" ).tmpl( msg.auth_set  ).appendTo( "#authcontent" );
            
       },
       error: function(msg){
         showError("Error", ""+msg.responseText );
       }
     });
}

function load_usage_auth(authid){
     $.ajax({
       type: "GET",
       url: '/auths/'+authid+'/usages/',
       success: function(msg){
           $( "#usageTemplate" ).tmpl( msg  ).appendTo( "#usagecontent" );
       },
       error: function(msg){
         showError("Error", ""+msg.responseText );
       }
     });
}
function load_usagesummary_auth(authid){
     $.ajax({
       type: "GET",
       url: '/auths/'+authid+'/usagesummary/',
       success: function(msg){
           $( "#usageSummaryTemplate" ).tmpl( msg.usages  ).appendTo( "#usagesummarycontent" );
       },
       error: function(msg){
         showError("Error", ""+msg.responseText );
       }
     });

 }

function load_details_auth(authid){
     $.ajax({
       type: "GET",
       url: '/auths/'+authid+'/base/',
       success: function(msg){
            if(msg.mimetype.startsWith("image")){
                $("#mfileImageDetailsTemplate" ).tmpl( msg  ).appendTo( "#detailscontent" );
                $('#image-preview').show( 'slide', {}, 1000,  function() {} );
            }else if(msg.mimetype.startsWith("video")){
                $("#mfileVideoDetailsTemplate" ).tmpl( msg  ).appendTo( "#detailscontent" );
                var flashvars = { file:"/mservedata/"+msg.file,image:""+msg.posterurl,autostart:"false" };
                var params = { allowfullscreen:"true", allowscriptaccess:"always" };
                var attributes = { id:"player1", name:"player1" };
                swfobject.embedSWF("/mservemedia/js/player.swf","container1","480","270","9.0.115","false",flashvars, params, attributes);
            }else if(msg.name.endsWith(".blend")){
                $("#mfileRenderDetailsTemplate" ).tmpl( msg  ).appendTo( "#detailscontent" );
            }
       },
       error: function(msg){
         showError("Error", ""+msg.responseText );
       }
     });
 }

function load_mfiles_auth(authid){
     $.ajax({
       type: "GET",
       url: '/auths/'+authid+'/mfiles/',
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
                            create_new_job_ui_dialog(gmfileid, serviceid)
                            $("#mfileid").val(gmfileid);
                            $("#serviceid").val(serviceid);
                            $("#dialog-new-job-dialog-form").dialog( "open" );
                        });
                    })();
                }

                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object

            // Render the template with the data and insert
            // the rendered HTML under the "mfilepaginator" element
            $("#managedresourcesmfilespaginator").pagination(mfiles.length, {
                    items_per_page:12,
                    callback:handlePaginationClick
            });

       },
       error: function(msg){
         showError("Error", ""+msg.responseText );
       }
     });
 }
