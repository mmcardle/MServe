

function update_container(url){

 data = $("#containerupdateform").serialize()

 $.ajax({
   type: "PUT",
   data: data,
   url: url,
   success: function(msg){
        $("#containerupdateform").effect("highlight", {}, 3000);   
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 });
}

function create_container(){
 $.ajax({
   type: "POST",
   data: "name=Container",
   url: '/containers/',
   success: function(msg){
       $( "#containerTemplate" ).tmpl( msg ) .prependTo( "#containerholder" );
   },
   error: function(msg){
     showError("Error", ""+msg.responseText );
   }
 });
}