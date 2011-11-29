

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

function loadContainers(){
    $.ajax({
       type: "GET",
       url: "/containers/",
       success: function(msg){
            containers = msg;

            if(containers.length==0){
                 $("#containermessages").append("<div id='nocontainers' class='message'>No Containers</div>");
                return;
            }else{
                $("#containermessages").empty()
            }

            function handlePaginationClick(new_page_index, pagination_container) {
                // This selects elements from a content array
                $( "#containerholder" ).empty()
                start = new_page_index*this.items_per_page
                end   = (new_page_index+1)*this.items_per_page
                if(end>containers.length){
                    end=containers.length;
                }

                $( "#containerTemplate" ).tmpl( containers.slice(start,end) ) .prependTo( "#containerholder" );
                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object
            $("#containerpaginator").pagination(msg.length, {
                    items_per_page:4,
                    callback:handlePaginationClick
            });
       },
       error: function(msg){
            $("#containermessages").append("<div class='message'>Failed to get containers</div>");
       }
     });
}
