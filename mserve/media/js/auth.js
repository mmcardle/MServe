
function load_auths(authid){
     $.ajax({
       type: "GET",
       url: '/auth/'+authid+'/',
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
       url: '/api/'+authid+'/usage/',
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
       url: '/api/'+authid+'/getusagesummary/',
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
       url: '/api/'+authid+'/head/',
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

function load_managedresources_auth(authid){
     $.ajax({
       type: "GET",
       url: '/api/'+authid+'/getmanagedresources/',
       success: function(msg){
        for(i in msg.mfile_set){
            $( "#mfileTemplate" ).tmpl( msg.mfile_set[i] ) .appendTo( "#managedresourcesmfilescontent" );
        }
        for(i in msg.job_set){
            $( "#jobTemplate" ).tmpl( msg.job_set[i] ) .appendTo( "#managedresourcesjobscontent" );
        }
       },
       error: function(msg){
         showError("Error", ""+msg.responseText );
       }
     });
 }
