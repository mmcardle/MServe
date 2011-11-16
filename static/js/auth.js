
function load_auths(authid){
     $.ajax({
       type: "GET",
       url: '/auths/'+authid+'/',
       success: function(msg){
           $( "#authTemplate" ).tmpl( msg.auth_set  ).appendTo( "#authcontent" );
            
       }
     });
}

function load_usage_auth(authid){
     $.ajax({
       type: "GET",
       url: '/auths/'+authid+'/usages/?full=True',
       success: function(msg){

           $( "#usageTemplate" ).tmpl( msg.usages  ).appendTo( "#usagecontent" );
       }
     });
}
function load_usagesummary_auth(authid){
     $.ajax({
       type: "GET",
       url: '/auths/'+authid+'/usagesummary/',
       success: function(summary){
           $( "#usageSummaryTemplate" ).tmpl( summary.usages ).appendTo( "#usagesummarycontent" );
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
       }
     });
 }

function load_mfiles_auth(authid){
     $.ajax({
       type: "GET",
       url: "/auths/"+authid+"/base/",
       success: function(auth){
            $("#mservetree").mserve( "load", {
                    serviceid : authid ,
                    mfolder_set : auth.mfolder_set,
                    mfile_set : auth.mfile_set,
                    folder_structure : auth.folder_structure
                })
            create_jobs_paginator(auth.job_set)
       }
     });
}

function load_jobs_auth(authid){
     $.ajax({
       type: "GET",
       url: '/auths/'+authid+"/jobs/",
       success: function(msg){
        $(msg).each(function(index,job){
            create_job_holder(job)
                if(!job.tasks.ready){
                    check_job(job,serviceid)
                }
        });
       }
     });
}
