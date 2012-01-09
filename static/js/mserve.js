
(function( $ ){

  var methods = {
    init : function( options ) { 
            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this), data = $this.data('mserve')

                 // If the plugin hasn't been initialized yet

                 if ( ! data ) {
                   $(this).data('mserve', {
                       target : $this,
                       cache : {},
                       contentcache : {}
                   });
                 }
            });

    },
    loadpage : function( page ) {
        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);

            var $this = $(this), data = $this.data('mserve')

            console.log("loading page "+page)
            
            if(!page){
                page="/"
            }
            if(page=='/'){
                if(isStaff){
                    $this.empty()
                    $(this).mserve('loadContainers');
                }else{

                }
            }else if(page.startsWith('/services/')){
                var str = page.split(/\//g)
                var serviceid = str[2]
                var url = "/"+str[1]+"/"+serviceid
                var tab = str[3]

                if(!data.cache[serviceid]){
                    console.log("Service is not cached")
                    $this.empty()
                    $(this).mserve('loadService', url, tab);
                }else{
                    data.allcontent = data.contentcache[serviceid]
                    if($(this).find("#tabs-"+serviceid).length <= 0){
                        console.log("Service is cached - but not on service page")
                        $(this).empty()
                        $(this).mserve('loadService', url, tab);
                    }else{
                        console.log("Service is cached and on service page - showing tab")
                        $(this).mserve('showServiceTab', data[serviceid], tab);
                    }
                }
            }else if(page.startsWith('/auths/')){
                var str2 = page.split(/\//g)
                var authid = str2[2]
                var authurl = "/"+str2[1]+"/"+authid
                var authtab = str2[3]

                if(!data.cache[authid]){
                    console.log("Auth is not cached")
                    $this.empty()
                    $(this).mserve('loadServiceAuth', authurl, authtab, authid);
                }else{
                    data.allcontent = data.contentcache[authid]
                    if($(this).find("#tabs-"+authid).length <= 0){
                        console.log("ServiceAuth is cached - but not on service page")
                        $(this).empty()
                        $(this).mserve('loadServiceAuth', authurl, authtab, authid);
                    }else{
                        console.log("Service is cached and on service page - showing tab")
                        $(this).mserve('showServiceTab', data[authid], authtab, authid);
                    }
                }
            }else if(page.startsWith('/mfiles/')){
                var str = page.split(/\//g)
                url = str[1]+"/"+str[2]
                tab = str[3]
                $this.mserve('showMFile', str[2]);
            }else{
                console.log("dont know how to load "+page)
            }

        });
    },
    initContainer: function(container, isNew) {
        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);
            var $this = $(this), data = $this.data('mserve')

            $("#nocontainers").remove()
            $container = $( "#containerTemplate" ).tmpl( container )
            $container.prependTo( $this.find("#containerholder") );
            $container.find("input[type='text']").addClass("text ui-widget-content ui-corner-all")
            $container.find("input[type='password']").addClass("text ui-widget-content ui-corner-all")
            if(isNew){
                $container.find("#containermessages-"+container.id).prepend(
                    $("#strongMessageTemplate").tmpl({"cl":"container-message-"+container.id,"message":"New Container!"})
                );
            }

            $("#newservicebutton-"+container.id).button().click(
            function(){
                 $("#createserviceholder-"+container.id).toggle()
            })
            $("#createservicebutton-"+container.id).button().click(
            function(){
                data = $("#createserviceform-"+container.id).serialize()
                $.ajax({
                       type: "POST",
                       url: '/containers/'+container.id+'/services/',
                       data: data,
                       success: function(service){
                            $(".container-message-"+container.id).remove()
                            $("#serviceTemplate").tmpl( service, {containerid : container.id} ).prependTo( "#containerserviceholder-"+container.id ).show('slide');
                            $("#newsubservicebutton-"+service.id).button()
                       },
                       error: function(msg){
                            showMessage("Error",msg.responseText)
                        }
                     });
            })

        })
    },
    loadContainers: function() {
        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);

            var $this = $(this), data = $this.data('mserve')

            $.ajax({
               type: "GET",
               url: "/containers/",
               success: function(containers){
                    console.log("loading containers")

                    $this.append("<div id='containertabs' ><ul></ul></div>");
                    $("#containertabs").tabs().tabs( "add", "#tabs-services" , "Container Management" );
                    $servicetab = $("<div><table><tr><td id='td1'></td><td style='width:100%' id='td2'></td></tr></table></div>");
                    $servicetab.appendTo($("#tabs-services"))
                    $servicetab.find('#td1').append( $("#messageTemplate").tmpl({"message":"Welcome to the container managment page of MServe. You can create new containers and manage existing ones from here"})  );
                    $servicetab.find('#td1').append( $("#hostingcontainerformTemplate").tmpl() );
                    $servicetab.find('#td2').append( $("#messageTemplate").tmpl({"message":"Here is a list of Containers in this MServe, scroll with the paginator below to view more"})  );
                    $servicetab.find('#td2').append("<div id='containerpaginator'></div>");
                    $servicetab.find('#td2').append("<div id='containermessages'></div>");
                    $servicetab.find('#td2').append("<div id='containerholder'></div>");

                    $servicetab.find("input[type='text']").addClass("text ui-widget-content ui-corner-all")
                    $servicetab.find("input[type='password']").addClass("text ui-widget-content ui-corner-all")
                    $servicetab.find("select").addClass("ui-widget-content ui-corner-all")

                    $("#createcontainerbutton").button()
                    $("#createcontainerbutton" ).click(function() {
                        data = $("#createcontainerform").serialize()
                         $.ajax({
                           type: "POST",
                           data: data,
                           url: '/containers/',
                           success: function(container){
                               $(obj).mserve('initContainer', container, true)
                           },
                           error: function(msg){
                             showError("Error", ""+msg.responseText );
                           }
                         });
                    });

                    if(containers.length==0){
                         $this.find("#containermessages").append("<div id='nocontainers' class='message'>No Containers</div>");
                        return;
                    }else{
                        $("#containermessages").empty()
                    }

                    function handlePaginationClick(new_page_index, pagination_container) {
                        // This selects elements from a content array
                        //$( "#containerholder" ).empty()
                        start = new_page_index*this.items_per_page
                        end   = (new_page_index+1)*this.items_per_page
                        if(end>containers.length){
                            end=containers.length;
                        }

                        slice = containers.slice(start, end)
                        
                        $(slice.reverse()).each(function(index,container){
                            $(obj).mserve('initContainer', container)
                        })

                        return false;
                    }

                    // First Parameter: number of items
                    // Second Parameter: options object
                    $servicetab.find("#containerpaginator").pagination(containers.length, {
                            items_per_page:4,
                            callback:handlePaginationClick
                    });

               },
               error: function(msg){
                    $("#containermessages").append("<div class='message'>Failed to get containers</div>");
               }
             });

        });
    },
    showServiceTab: function( service, tab ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var $this = $(this),
                data = $this.data('mserve');
                if(tab){
                    $tabs.tabs('select', '#' + tab+"tab-"+service.id);
                }else{
                    $tabs.tabs('select', '#servicetab-'+service.id);
                }
            });
    },
    loadServiceAuth: function(url, tab, authid) {
        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);

            var $this = $(this), data = $this.data('mserve')
             $.ajax({
               type: "GET",
               url: url+"/base/",
               success: function(auth){
                   data[authid] = auth

                   $(auth.mfile_set).each( function(index, mfile){
                        data[mfile.id] = mfile
                   })

                    $tabs = $("#tabsTemplate").tmpl( {"tabid":authid,"tabs":[
                        {name:"Service Data",id:"servicetab-"+authid,url:url},
                        {name:"Jobs",id:"jobstab-"+authid,url:url+"/jobs"},
                        {name:"Usage",id:"usagetab-"+authid,url:url+"/usage"}
                    ]} )

                    $table = $("#mserveTemplate").tmpl()
                    $table.find("#mserve-new-folder-button").button(
                        {icons: {primary: "ui-icon-circle-plus"}}
                        ).click( function(){
                            selected = $("#mfoldertreecontainer").jstree('get_selected')
                            alert("TODO - Create folder at "+selected)
                    })

                    $(obj).append($tabs);
                    $servicetab = $("#servicetab-"+authid);
                    $servicetab.append( $("#messageTemplate").tmpl({"message":"Here is a list of files stored at this MServe Service, click File Upload to upload more files,  or Drag and Drop files"})  );
                    $servicetab.append("<input  type=\"checkbox\" id=\"fileuploadautobutton\" /><label for=\"fileuploadautobutton\">Auto upload</label>");
                    $servicetab.append($table);

                    $usageHolderTemplate  = $("#usageHolderTemplate").tmpl()
                    $("#usagetab-"+authid).append($usageHolderTemplate);

                    $("#jobstab-"+authid).append("<div id='jobspaginator'><div class='spinner'><span class='red'>Loading Jobs...</span></div></div>");

                    $($tabs).tabs()
                    _loadusage = function(){
                        $usageHolderTemplate.find("#mservelast24").mserveusage('stats', ["last24"], '/stats/'+authid+'/' )
                        $usageHolderTemplate.find("#mservelast1").mserveusage('stats', ["last1"], '/stats/'+authid+'/' )
                        $usageHolderTemplate.find("#mservejobs").mserveusage('stats', ["jobs"], '/stats/'+authid+'/' )
                        $usageHolderTemplate.find("#mservejobstype").mserveusage('stats', ["jobsbytype"], '/stats/'+authid+'/' )
                        $usageHolderTemplate.find("#deliverySuccess").mserveusage('stats', ["http://mserve/deliverySuccess"], '/stats/'+authid+'/')
                        $usageHolderTemplate.find("#usagesummary").mserveusage('usagesummary', '/auths/'+authid+'/usagesummary/' )
                    }

                    function do_tab(tab){
                        if (tab == "usagetab-"+authid || tab =="usage") {
                            _loadusage()
                        }else if(tab == "servicetab-"+authid || tab =="" || !tab) {
                            // Fix for fileupload being 0px height when tab changes
                            $("#fileupload").css("height","274px")
                        }else if(tab == "configtab-"+authid || tab =="config") {
                            // Do nothing for config tab
                        }else if(tab == "jobstab-"+authid || tab =="jobs") {
                            loadJobs("/auths/"+authid+"/jobs/")
                        }
                    }

                    $tabs.bind('tabsshow', function(event, ui) {
                        do_tab(ui.panel.id)
                    });

                    if(tab!=undefined){
                        $tabs.tabs('select', '#' + tab+"tab-"+authid);
                    }

                    $this.mserve( "loadMTree", {
                        serviceid : authid ,
                        mfolder_set : auth.mfolder_set,
                        mfile_set : auth.mfile_set,
                        folder_structure : auth.folder_structure
                    } )

                    $.getScript('/mservemedia/js/blueimp-jQuery-File-Upload-cc02381/jquery.fileupload-ui.js');

                    $(".single-accordion").accordion({
			collapsible: true
                    }).accordion( "activate" , false );

                    $uploadbutton = $("#fileuploadautobutton").button()
                    $selectallbutton = $("#selectall").button()
                    $("label[for=fileuploadautobutton] span").text("Autoupload is off")

                    $uploadbutton.click(function(){
                        autoupload = $('#fileupload').fileupload('option','autoUpload');
                        $('#fileupload').fileupload('option','autoUpload',!autoupload);
                        if(autoupload){
                            $("label[for=fileuploadautobutton] span").text("Autoupload is off")
                        }else{
                            $("label[for=fileuploadautobutton] span").text("Autoupload is on")
                        }
                    })

                    $('#fileupload').fileupload({
                        previewMaxWidth: 100,
                        previewMaxHeight: 20,
                        dataType: 'json',
                        url: "/auths/"+authid+"/mfiles/",
                        add: function (e, data) {
                            $("#fileupload-accordion:not(:has(.ui-accordion-content-active))").accordion("activate", 0)
                            var that = $(this).data('fileupload');
                            that._adjustMaxNumberOfFiles(-data.files.length);
                            data.isAdjusted = true;
                            data.isValidated = that._validate(data.files);
                            data.context = that._renderUpload(data.files)
                                .appendTo($(this).find('.files')).fadeIn(function () {
                                    // Fix for IE7 and lower:
                                    $(this).show();
                                }).data('data', data);
                            if ((that.options.autoUpload || data.autoUpload) &&
                                    data.isValidated) {
                                data.jqXHR = data.submit();
                            }
                        },
                        done: function (e, data) {
                            $(obj).mserve('addMFile',data.result)
                            l = $(this).find("#tabs-"+authid).length
                            console.log(l)

                            var that = $(this).data('fileupload');
                            if (data.context) {
                                data.context.each(function (index) {
                                    file=data.result
                                    if (file.error) {
                                        that._adjustMaxNumberOfFiles(1);
                                    }
                                    $(this).fadeOut(function () {
                                        that._renderDownload([file])
                                            .css('display', 'none')
                                            .replaceAll(this)
                                            .fadeIn(function () {
                                                // Fix for IE7 and lower:
                                                $(this).show();
                                            });
                                    });
                                });
                            } else {
                                that._renderDownload(data.result)
                                    .css('display', 'none')
                                    .appendTo($(this).find('.files'))
                                    .fadeIn(function () {
                                        // Fix for IE7 and lower:
                                        $(this).show();
                                    });
                            }
                        }
                    });
                    data["cache"][authid] = $(obj.clone(true,true))
               }
            });

        });
    },
    loadService: function(url, tab) {
        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);

            var $this = $(this), data = $this.data('mserve')
            console.log(url)
             $.ajax({
               type: "GET",
               url: url,
               success: function(service){

                   data[service.id] = service

                   $(service.mfile_set).each( function(index, mfile){
                        data[mfile.id] = mfile
                   })

                    $tabs = $("#tabsTemplate").tmpl( {"tabid":service.id,"tabs":[
                        {name:"Service Data",id:"servicetab-"+service.id,url:url},
                        {name:"Jobs",id:"jobstab-"+service.id,url:url+"/jobs"},
                        {name:"Config",id:"configtab-"+service.id,url:url+"/config"},
                        {name:"Usage",id:"usagetab-"+service.id,url:url+"/usage"}
                    ]} )

                    $table = $("#mserveTemplate").tmpl()
                    $table.find("#mserve-new-folder-button").button(
                        {icons: {primary: "ui-icon-circle-plus"}}
                        ).click( function(){
                            selected = $("#mfoldertreecontainer").jstree('get_selected')
                            alert("TODO - Create folder at "+selected)
                    })

                    $(obj).append($tabs);
                    $servicetab = $("#servicetab-"+service.id);
                    $servicetab.append( $("#messageTemplate").tmpl({"message":"Here is a list of files stored at this MServe Service, click File Upload to upload more files,  or Drag and Drop files"})  );
                    $servicetab.append("<input  type=\"checkbox\" id=\"fileuploadautobutton\" /><label for=\"fileuploadautobutton\">Auto upload</label>");
                    $servicetab.append($table);

                    $usageHolderTemplate  = $("#usageHolderTemplate").tmpl()
                    $("#usagetab-"+service.id).append($usageHolderTemplate);

                    $("#jobstab-"+service.id).append("<div id='jobspaginator'><div class='spinner'><span class='red'>Loading Jobs...</span></div></div>");
                    $serviceConfigTemplate  = $("#serviceConfigTemplate").tmpl( service )
                    $("#configtab-"+service.id).append($serviceConfigTemplate);

                    $serviceConfigTemplate.find("input[type='text']").addClass("text ui-widget-content ui-corner-all")
                    
                    $("input[type=text]").css("border","1").css("color","#f6931f").css("font-weight","bold")
                    $("#webdav").text("dav://"+window.location.hostname+":"+window.location.port+"/webdav/"+service.id+"/")
                    
                    hpmessage = "This service is in high priority"
                    lpmessage = "This service is in low priority"

                    if(service.priority){
                        $("#highprioritybutton").hide()
                        $("#strongMessageTemplate" ).tmpl( {"message": hpmessage} ).appendTo("#prioritymessage")
                    }else{
                        $( "#messageTemplate" ).tmpl( {"message": lpmessage} ).appendTo("#prioritymessage")
                        $("#lowprioritybutton").hide()
                    }

                    function set_high_priority(){
                        update_service_priority(service.url,true)
                        $("#highprioritybutton").hide()
                        $("#lowprioritybutton").show()
                        $("#prioritymessage").empty()
                        $("#strongMessageTemplate" ).tmpl( {"message": hpmessage} ).appendTo("#prioritymessage")
                    }
                    function set_low_priority(){
                        update_service_priority(service.url,false)
                        $("#lowprioritybutton").hide()
                        $("#highprioritybutton").show()
                        $("#prioritymessage").empty()
                        $( "#messageTemplate" ).tmpl( {"message": lpmessage} ).appendTo("#prioritymessage")
                    }

                    $("#lowprioritybutton").button().click(set_low_priority)
                    $("#highprioritybutton").button().click(set_high_priority)
                    
                    $($tabs).tabs()

                    _loadusage = function(){
                        $usageHolderTemplate.find("#mservelast24").mserveusage('stats', ["last24"], '/stats/'+service.id+'/' )
                        $usageHolderTemplate.find("#mservelast1").mserveusage('stats', ["last1"], '/stats/'+service.id+'/' )
                        $usageHolderTemplate.find("#mservejobs").mserveusage('stats', ["jobs"], '/stats/'+service.id+'/' )
                        $usageHolderTemplate.find("#mservejobstype").mserveusage('stats', ["jobsbytype"], '/stats/'+service.id+'/' )
                        $usageHolderTemplate.find("#deliverySuccess").mserveusage('stats', ["http://mserve/deliverySuccess"], service.stats_url )
                        $usageHolderTemplate.find("#usagesummary").mserveusage('usagesummary', service.usage_url )
                    }

                    $("#profilepaginator").mserve( "serviceprofiles", service.id )
                    service_loadmanagementproperties(service.id, service.properties_url );
                    $("#managementpropertybutton").button().click(
                        function(){
                            service_postmanagementproperty_ajax(
                                service.id,
                                service.properties_url,
                                $('#managementpropertyform').serialize()
                            );
                        }
                    )

                    function do_tab(tab){
                        if (tab == "usagetab-"+service.id || tab =="usage") {
                            _loadusage()
                        }else if(tab == "servicetab-"+service.id || tab =="" || !tab) {
                            // Fix for fileupload being 0px height when tab changes
                            $("#fileupload").css("height","274px")
                        }else if(tab == "configtab-"+service.id || tab =="config") {
                            // Do nothing for config tab
                        }else if(tab == "jobstab-"+service.id || tab =="jobs") {
                            loadJobs("/auths/"+service.id+"/jobs/")
                        }
                    }

                    $tabs.bind('tabsshow', function(event, ui) {
                        do_tab(ui.panel.id)
                    });

                    if(tab!=undefined){
                        $tabs.tabs('select', '#' + tab+"tab-"+service.id);
                    }

                    $this.mserve( "loadMTree", {
                        serviceid : service.id ,
                        mfolder_set : service.mfolder_set,
                        mfile_set : service.mfile_set,
                        folder_structure : service.folder_structure
                    } )

                    $.getScript('/mservemedia/js/blueimp-jQuery-File-Upload-cc02381/jquery.fileupload-ui.js');
                    
                    $(".single-accordion").accordion({
			collapsible: true
                    }).accordion( "activate" , false );

                    $uploadbutton = $("#fileuploadautobutton").button()
                    $selectallbutton = $("#selectall").button()
                    $("label[for=fileuploadautobutton] span").text("Autoupload is off")

                    $uploadbutton.click(function(){
                        autoupload = $('#fileupload').fileupload('option','autoUpload');
                        $('#fileupload').fileupload('option','autoUpload',!autoupload);
                        if(autoupload){
                            $("label[for=fileuploadautobutton] span").text("Autoupload is off")
                        }else{
                            $("label[for=fileuploadautobutton] span").text("Autoupload is on")
                        }
                    })
                    
                    $('#fileupload').fileupload({
                        previewMaxWidth: 100,
                        previewMaxHeight: 20,
                        dataType: 'json',
                        url: "/services/"+service.id+"/mfiles/",
                        add: function (e, data) {
                            $("#fileupload-accordion:not(:has(.ui-accordion-content-active))").accordion("activate", 0)
                            var that = $(this).data('fileupload');
                            that._adjustMaxNumberOfFiles(-data.files.length);
                            data.isAdjusted = true;
                            data.isValidated = that._validate(data.files);
                            data.context = that._renderUpload(data.files)
                                .appendTo($(this).find('.files')).fadeIn(function () {
                                    // Fix for IE7 and lower:
                                    $(this).show();
                                }).data('data', data);
                            if ((that.options.autoUpload || data.autoUpload) &&
                                    data.isValidated) {
                                data.jqXHR = data.submit();
                            }
                        },
                        done: function (e, data) {
                            $(obj).mserve('addMFile',data.result)
                            var that = $(this).data('fileupload');
                            if (data.context) {
                                data.context.each(function (index) {
                                    file=data.result
                                    if (file.error) {
                                        that._adjustMaxNumberOfFiles(1);
                                    }
                                    $(this).fadeOut(function () {
                                        that._renderDownload([file])
                                            .css('display', 'none')
                                            .replaceAll(this)
                                            .fadeIn(function () {
                                                // Fix for IE7 and lower:
                                                $(this).show();
                                            });
                                    });
                                });
                            } else {
                                that._renderDownload(data.result)
                                    .css('display', 'none')
                                    .appendTo($(this).find('.files'))
                                    .fadeIn(function () {
                                        // Fix for IE7 and lower:
                                        $(this).show();
                                    });
                            }
                        }
                    });
                    data["cache"][service.id] = $(obj.clone(true,true))
               }
            });

        });
    },
    loadMFile: function(url) {
        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);

            var $this = $(this), data = $this.data('mserve')

             $.ajax({
               type: "GET",
               url: url,
               success: function(mfile){
                    $this.append(mfile.name)
               }
            });

        });
    },
    get_mfile_thumb: function(mfileid, depth){

        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);
            var $this = $(this),
            data = $this.data('mserve');

            if(depth>3){
               return
            }else{
               $.ajax({
                   type: "GET",
                   url: "/mfiles/"+mfileid+"/",
                   success: function(newmfile){
                        if(newmfile.thumb != ""){
                            var mfilecache = $(data.allcontent[0]).find("#mfile-table-"+mfileid)
                            mfilecache.css("background-image", "url('"+newmfile.thumburl+"')");
                            $("#mfile-table-"+mfileid).css("background-image", "url('"+newmfile.thumburl+"')");
                        }else{
                            setTimeout(mservetimeout,3000 ,obj,mfileid, depth+1)
                        }
                   }
               });
            }

        });
    },
    updatemfile : function( mfileid, options ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');

                $("#newjobbutton-"+mfileid ).button({icons: {primary: "ui-icon-transferthick-e-w"}, text: false});
                $('#newjobbutton-'+mfileid).click(function(){
                    $("#mfileid").val(mfileid);
                    $("#dialog-new-job-dialog-form").dialog( "open" );
                });
                $("#deletemfilebutton-"+mfileid ).button({icons: {primary: "ui-icon-trash"}, text: false}).click(function(){
                    obj.mserve('deletemfile', mfileid)
                });

                if(options.pollthumb){
                    obj.mserve('get_mfile_thumb', mfileid, 1)
                }
            });
    },
    deletemfile : function(mfileid) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var $this = $(this),
                data = $this.data('mserve');

                $( '#dialog-mfile-dialog' ).dialog({
                        resizable: false,
                        modal: true,
                        buttons: {
                                "Delete mfile?": function() {
                                     $.ajax({
                                       type: "DELETE",
                                       url: '/mfiles/'+mfileid+"/",
                                       success: function(msg){
                                            $(data.allcontent[0]).find("#mfileholder-"+mfileid).remove()
                                            $("#mfileholder-"+mfileid).hide('slide')
                                            $("#mfoldertreecontainer").jstree('delete_node',"#"+mfileid)
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
            });
    },
    addMFile : function( mfile ){

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');
                $("#nofiles").remove()
                data[mfile.id] = mfile
                var $mft = $("#mfileTemplate" ).tmpl( mfile )

                // Update MFile before cloning
                $(obj).mserve('updatemfile', mfile.id, {"pollthumb":"true"})

                $mft.find("#newjobbutton-"+mfile.id ).button({icons: {primary: "ui-icon-transferthick-e-w"}, text: false});
                $mft.find('#newjobbutton-'+mfile.id).click(function(){
                    $("#mfileid").val(mfile.id);
                    $("#dialog-new-job-dialog-form").dialog( "open" );
                });
                $mft.find("#deletemfilebutton-"+mfile.id ).button({icons: {primary: "ui-icon-trash"}, text: false}).click(function(){
                    obj.mserve('deletemfile', mfile.id)
                });

                data.allcontent.prepend($mft.clone(true,true))
               
                selected = $("#mfoldertreecontainer").jstree("get_selected")
                if($(selected).hasClass("service")){
                    $('#qscontainer').prepend($mft)
                    $mft.show('slide');
                }

                pnode = $("#mfoldertreecontainer .service")

                $("#mfoldertreecontainer").jstree("create", pnode, "first",
                    {"data" : {
                            "title" : mfile.name,
                            "icon" : mfile.thumburl
                            },
                        "attr" : {
                            "id": mfile.id,
                            "class" : "mfile"
                            }
                    }, null, true    );
            });
    },
    showService: function( serviceid ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var $this = $(this),
                data = $this.data('mserve');
                $("#mfilejobcontainer").hide()
                var $filteredData = data.allcontent.find('li.rootfolder');
                $('#qscontainer').quicksand($filteredData, {
                  duration: 800,
                  easing: 'easeInOutQuad'
                });
            });
    },
    showMFolder : function( mfolderid ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var $this = $(this),
                data = $this.data('mserve');

                var $filteredData = $(data.allcontent[0]).find('li.'+mfolderid);
                $("#mfilejobcontainer").hide()
                $('#qscontainer').quicksand($filteredData, {
                  duration: 800,
                  easing: 'easeInOutQuad'
                });
            });
    },
    showMFile : function( id ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {

                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');

                var $filteredData = data.allcontent.find('#mfileposterholder-'+id);

                if(!$filteredData.length>0){
                    var $mfpt = $("#mfilePosterTemplate" ).tmpl( data[id] )
                    data.allcontent.append($mfpt)
                    $mfpt.find("#mfile_download_button-"+id).button()
                    $filteredData = $mfpt
                }

                $("#mfilejobcontainer").show()
                $("#mfilecreatejobcontainer").empty().append($("#jobSubmitTemplate").tmpl())
                var $form = $("#mfilecreatejobcontainer").find("form")

                $("#mfilecreatejobcontainer").find(".jobsubmit").button().click(function(){
                        var postdata =  $form.serialize()
                        $(obj).mserve('createMFileJob', id, postdata)
                })

                $(obj).mserve()
                $.ajax({
                   type: "GET",
                   url: '/mfiles/'+id+"/jobs/",
                   success: function(msg){
                        if(msg.length > 0){
                            $("#mfilecurrentjobscontainer").empty()
                        }

                        $(msg).each(function(index,job){
                            $(obj).mserve("createJobHolder", job, $("#mfilecurrentjobscontainer"))
                            if(!job.tasks.ready){
                                check_job(job,id)
                            }
                        });
                   }
                 });

                $('#qscontainer').quicksand($filteredData, {
                    adjustHeight: 'dynamic',
                    duration: 800,
                    easing: null
                });

                $.ajax({
                   type: "GET",
                   url: "/tasks/",
                   success: function(jobdescriptions){
                        var job = $form.find(".jobtype")
                        var args = $form.find(".args" )
                        var inputs = $form.find(".inputs" )
                        jobtypes = jobdescriptions['regular']

                        $filteredData.find(".jobtype").empty()
                        for( t in jobtypes){
                            $(".jobtype").append("<option value='"+jobtypes[t]+"'>"+jobtypes[t]+"</option>")
                        }

                        $form.find(".jobtype").change(function() {
                            selected = job.val()

                            $form.find(".args").empty()
                            $form.find(".argsmessage").empty()
                            $form.find(".inputs").empty()
                            $form.find(".inputsmessage").empty()

                            if(jobdescriptions['descriptions'][selected]){
                               var targs = jobdescriptions['descriptions'][selected]['options']
                               var nbinputs = jobdescriptions['descriptions'][selected]['nbinputs']

                               if(targs.length == 0){
                                    $form.find(".argsmessage").append($( "#messageTemplate" ).tmpl( {"message":"This Job type takes no arguements"} ))
                               }

                               for(t in targs){
                                    $form.find(".args").append("<label for="+targs[t]+">"+targs[t]+"</label><input type='text' name="+targs[t]+" id="+targs[t]+"  value=''></input>")
                               }

                                if(nbinputs == 0){
                                    $form.find(".inputsmessage").append("<em>No inputs</em>")
                                }

                                $form.find(".job-extra-input-preview").empty();
                                ia = []
                                for (var i=0;i<nbinputs;i++){
                                    ia.push(i)
                                }
                                $(ia).each(function(index,i)
                                {
                                    inputkey = 'input-'+i
                                    inputlabel = 'input-'+(i+1)
                                    input = jobdescriptions['descriptions'][inputkey]
                                    initialvalue = ""
                                    if(i==0){
                                        value=mfileid
                                        $("#inputs").append("<input type='hidden' name="+inputkey+" id="+inputkey+"  value='"+value+"'></input>")
                                    }else{
                                        var $chooser = $( "#mfileChooserTemplate" ).tmpl( {"id" : "mfile-chooser-"+i} )
                                        $chooser.appendTo("#job-extra-input-preview");
                                        $chooser.find("button").button().click(function( ){
                                            $.ajax({
                                               type: "GET",
                                               url: "/users/",
                                               success: function(user){
                                                    $("#dialog-choose-mfile-dialog-form #dialog-choose-mfile-mfileholder").empty()
                                                    create_new_choose_mfile_ui_dialog()
                                                    $(user.mfiles).each(function(index,mfile){
                                                        tmpl = $( "#mfileNoActionTemplate" ).tmpl( mfile )
                                                        tmpl.appendTo( "#dialog-choose-mfile-dialog-form #dialog-choose-mfile-mfileholder")
                                                        tmpl.click(function(){
                                                            $("#mfile-chooser-"+i).replaceWith(this)
                                                            $("#dialog-choose-mfile-dialog-form").dialog( "close" )
                                                            $("input[name='"+inputkey+"']").val(mfile.id)
                                                        })

                                                    })
                                                    $(user.myauths).each(function(index,auth){
                                                        tmpl = $( "#mfileNoActionTemplate" ).tmpl( auth )
                                                        tmpl.appendTo( "#dialog-choose-mfile-dialog-form #dialog-choose-mfile-mfileholder")
                                                        tmpl.click(function(){
                                                            $("#mfile-chooser-"+i).replaceWith(this)
                                                            $( "#dialog-choose-mfile-dialog-form").dialog( "close" )
                                                            $("input[name='"+inputkey+"']").val(auth.id)
                                                        })

                                                    })


                                                }
                                            });
                                        })
                                        $("#inputs").append("<input type='hidden' name="+inputkey+" id="+inputkey+"  value=''></input>")
                                    }

                                });
                            }
                         });
                   }
                 });
                

            });
    },
    createJobHolder : function( job, paginator, prepend ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {

                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');

                var tasks = job.tasks
                var jobholder = $("#job-"+job.id)
                if (jobholder.length == 0){

                    if(prepend){
                        $( "#jobTemplate" ).tmpl( job ).prependTo( paginator );
                    }else{
                        $( "#jobTemplate" ).tmpl( job ).appendTo( paginator );
                    }
                    
                    if(job.joboutput_set.length>0){
                        create_job_output_paginator(job)
                    };

                    var percent = (job.tasks.completed_count/job.tasks.total)*100
                    var icon = $( "#jobicon-"+job.id )
                    var progressbar = $( "#jobprogressbar-"+job.id )

                    if(job.tasks.waiting){
                        icon.addClass('taskrunning')
                    }else{
                        icon.addClass('ui-icon-check')
                        icon.removeClass('taskrunning')
                    }

                    progressbar.progressbar({
                            value: percent
                    });

                    $('#jobpreviewpaginator-'+job.id).hide()
                    $("#joboutputs-"+job.id).hide()

                    $('#jobheader-'+job.id+", #jobicon-"+job.id+", "+'#jobinfo-'+job.id+', #jobprogressbar-'+job.id).click(
                        function() {$(obj).mserve("toggleJob",job)}
                    );

                    $("#jobdeletebutton-"+job.id ).button({icons: {primary: "ui-icon-circle-close"}, text: false});
                    $("#jobdeletebutton-"+job.id ).click(function() {delete_job(job.id)});

                    $(obj).mserve("updateJobOutput",job)

                    if(job.tasks.failed){
                        $('#jobinfo-'+job.id).addClass('ui-state-error ui-corner-all')
                    }
                }

            });
    },
    toggleJob: function( job ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');
                $('#joboutputs-'+job.id).toggle('slide');
                $('#jobpreviewpaginator-'+job.id).toggle('blind');

            });
    },
    updateJobOutput: function( job ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');

                $("#joboutputs-"+job.id).empty()
                $( "#jobTaskResultTemplate" ).tmpl(job.tasks.result).appendTo("#joboutputs-"+job.id)

            });
    },
    createMFileJob : function( mfileid, postdata ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');

                url = "/mfiles/"+mfileid+"/jobs/",

                 $.ajax({
                   type: "POST",
                   data: postdata,
                   url: url,
                   success: function(msg){
                        $(obj).mserve("createJobHolder",msg, $("#mfilecurrentjobscontainer"), true)
                        if(!msg.ready){
                            check_job(msg)
                        }
                   },
                   error: function(msg){
                        json_response = eval('(' + msg.responseText + ')');
                        if(json_response.error){
                            showError("Error creating Job",json_response.error)
                        }else{
                            showError("Error creating Job",msg.responseText)
                        }
                   }
                 });
            });
    },
    serviceprofiles : function(serviceid){

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);
                var $this = $(this),
                data = $this.data('mserve');

                $.ajax({
                   type: "GET",
                   url: "/tasks/",
                   success: function(tasks){
                        $.ajax({
                           type: "GET",
                           url: "/services/"+serviceid+"/profiles/",
                           success: function(profiles){

                                if(profiles.length==0){
                                     $("#profilemessages").append("<div id='noprofiles' class='message' >No profiles</div>");
                                    return False;
                                }else{
                                    $("#noprofiles").remove()
                                }
                                
                                var profiletabs = $( "<div></div>")
                                $( "#profileTabsTemplate" ).tmpl( {"profiles":profiles} ) .appendTo( profiletabs );
                                $( "#profileTemplate" ).tmpl( profiles ) .appendTo( profiletabs );
                                profiletabs.appendTo("#profilepaginator")
                                profiletabs.tabs()

                                $(".workflow-accordian").accordion({
                                    collapsible: true,
                                    autoHeight: false,
                                    navigation: true
                                }).accordion( "activate" , false )

                                $(profiles).each(function(pindex,profile){
                                    $(profile.workflows).each(function(windex,workflow){
                                        $("#addbutton-taskset-"+workflow.id).button({icons: {primary: "ui-icon-disk"}}).click(
                                        function(){
                                                 data = $("#newtasksetform-workflow-"+workflow.id).serialize()
                                                 $.ajax({
                                                   type: "POST",
                                                   data: data,
                                                   url: '/services/'+serviceid+'/profiles/'+profile.id+'/tasksets/',
                                                   success: function(newtaskset){
                                                        var tasksettmpl = $("#taskSetTemplate" ).tmpl( newtaskset, {"workflowid" : workflow.id} )
                                                        tasksettmpl.appendTo("#workflowbody-"+workflow.id );
                                                        updatetasksetbuttons(serviceid, profile.id, workflow.id, newtaskset)
                                                   },
                                                   error: function(msg){
                                                        showError("Error Adding Task Set",msg.responseText)
                                                    }
                                                 });
                                            }
                                        )
                                        $("#workflowbody-"+workflow.id).sortable({
                                            update : function(event, ui){
                                                var tasksetid = $(ui.item[0]).attr("data-taskid")

                                                $("#workflowsavedmsg-"+workflow.id).show()
                                            }
                                        })
                                        $("#workflowbody-savebutton-"+workflow.id).button().click(
                                            function(){
                                                $("#workflowbody-"+workflow.id).find(".taskset").each( function(tindex,taskset){
                                                    $("#workflowsavedmsg-"+workflow.id).hide()
                                                    var tasksetid = $(taskset).attr("data-taskid")
                                                    var index = $(taskset).parent().children().index(taskset)
                                                    form = $(taskset).find("#tasksetupdateform-taskset-"+tasksetid)
                                                    form.find("input[name=order]").val(index)
                                                    data = form.serialize()
                                                     $.ajax({
                                                           type: "PUT",
                                                           data: data,
                                                           url: '/services/'+serviceid+'/profiles/'+profile.id+'/tasksets/'+tasksetid+'/',
                                                           success: function(updatedtaskset){
                                                               var tasksettmpl = $("#taskSetTemplate").tmpl( updatedtaskset , {"workflowid":workflow.id} )
                                                               $( "#taskset-"+updatedtaskset.id ).replaceWith(tasksettmpl);
                                                               updatetasksetbuttons(serviceid, profile.id, workflow.id, updatedtaskset)
                                                               $(updatedtaskset.tasks).each(function(newtindex, task){
                                                                    updatetaskbuttons(serviceid, profile.id, updatedtaskset.id, task.id)
                                                                });
                                                           },
                                                           error: function(msg){
                                                                showError("Error Updating TaskSet ", "")
                                                            }
                                                         });

                                                    })
                                                }
                                        )

                                        $(workflow.tasksets).each(function(tsindex,taskset){
                                            updatetasksetbuttons(serviceid, profile.id, workflow.id, taskset)
                                            $(taskset.tasks).each(function(tindex, task){
                                                updatetaskbuttons(serviceid, profile.id, taskset.id, task.id)
                                            });
                                        });
                                    });
                                });

                                $(".task_name").autocomplete({
                                        source: tasks.regular
                                });

                                return false;
                           }
                         });
                    }
                });
            });

    },
    loadMTree : function( options ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);
                var $this = $(this),
                data = $this.data('mserve');

                var serviceid = o.serviceid
                var mfolder_set = o.mfolder_set
                var mfile_set =  o.mfile_set
                var folder_structure = o.folder_structure

                $("#mfolderTemplate").tmpl(mfolder_set).appendTo("#hiddenqscontainer")
                $("#mfileTemplate").tmpl(mfile_set).appendTo("#hiddenqscontainer")

                $(mfile_set).each( function(index, mfile) {
                    $(obj).mserve( 'updatemfile', mfile.id, {"pollthumb":"false"})
                });

                var servicecontent = $('#hiddenqscontainer').clone(true,true)
                data.contentcache[serviceid] = servicecontent
                data["allcontent"]= servicecontent

                var $filteredData = servicecontent.find('li.rootfolder');
                $('#qscontainer').quicksand($filteredData, {
                  duration: 800,
                  easing: 'easeInOutQuad'
                });
                
                $("#mfoldertreecontainer").jstree({
                     "json_data" : folder_structure,
                     "themes" : {"theme" : "default"},
                     "plugins" : [ "themes", "json_data", "ui", "crrm"]
                    }
                ).bind("select_node.jstree", function (event, data) {
                        id = data.rslt.obj.attr('id');
                        if(id==serviceid){
                            $(obj).mserve('showService', id)
                        }else{
                            mfile = servicecontent.find("#mfileholder-"+id)
                            if(mfile.length>0){
                                $(obj).mserve('showMFile', id)
                            }else{
                                $(obj).mserve('showMFolder', id)
                            }
                        }
                }).bind("loaded.jstree", function (event, data) {
                    $("#mfoldertreecontainer").jstree("open_all");
                });
            });
    }
  };

  $.fn.mserve = function( method ) {

    // Method calling logic
    if ( methods[method] ) {
      return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
      return methods.init.apply( this, arguments );
    } else {
      $.error( 'Method ' +  method + ' does not exist on jQuery.tooltip' );
    }

  };

})( jQuery );

function load_user(userurl,consumerurl,template){
     $.ajax({
       type: "GET",
       url: userurl,
       success: function(msg){
            
            if(msg.mfiles.length==0){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Resources"} )
                message.css("width","400px")
                message.appendTo( "#user_mfilemessages" );
                $( "#user-request-service" ).show()
            }else{
                $("#user_mfilemessages").empty()
            }

            if(msg.myauths.length==0){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Auths - Request a service using the form below "} )
                message.css("width","400px")
                message.appendTo( "#user_authmessages" );
                $( "#user-request-service" ).show()
            }else{
                $("#user_authmessages").empty()
            }

            var mfiles = msg.mfiles

            function handlePaginationClick(new_page_index, pagination_container) {
                // This selects elements from a content array
                start = new_page_index*this.items_per_page
                end   = (new_page_index+1)*this.items_per_page
                if(end>mfiles.length){
                    end=mfiles.length;
                }

                $( template ).tmpl( mfiles.slice(start,end) ) .appendTo( "#user_mfileholder" );
                return false;
            }


            // First Parameter: number of items
            // Second Parameter: options object
            $("#user_mfileholder").pagination(mfiles.length, {
                    items_per_page:4,
                    callback:handlePaginationClick
            });

            var myauths = msg.myauths

            function handlePaginationClick2(new_page_index, pagination_container) {
                // This selects elements from a content array
                start = new_page_index*this.items_per_page
                end   = (new_page_index+1)*this.items_per_page
                if(end>myauths.length){
                    end=myauths.length;
                }

                $( "#authTemplate" ).tmpl( myauths.slice(start,end) ) .appendTo( "#user_authholder" );
                return false;
            }

            // First Parameter: number of items
            // Second Parameter: options object
            $("#user_authholder").pagination(myauths.length, {
                    items_per_page:4,
                    callback:handlePaginationClick2
            });

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

       }
     });
}



function mservetimeout(obj,mfileid,depth){
    $(obj).mserve('get_mfile_thumb', mfileid , depth )
}

function updatetasksetbuttons(serviceid, profileid, workflowid, taskset){

    $("#addbutton-task-"+taskset.id).button({icons: {primary: "ui-icon-disk"}}).click(
        function(){
                 data = $("#newtaskform-taskset-"+taskset.id).serialize()
                 $.ajax({
                   type: "POST",
                   data: data,
                   url: '/services/'+serviceid+'/profiles/'+profileid+'/tasks/',
                   success: function(newtask){
                        var tasktmpl = $("#taskTemplate" ).tmpl( newtask, {"tasksetid" : taskset.id} )
                        tasktmpl.appendTo( "#tasksetbody-"+taskset.id );
                        updatetaskbuttons(serviceid, profileid, taskset.id, newtask.id)
                   },
                   error: function(msg){
                        showError("Error Adding Task",msg.responseText)
                    }
                 });
        }
    )

    deletefunction = function(){
         $.ajax({
           type: "DELETE",
           url: '/services/'+serviceid+'/profiles/'+profileid+'/tasksets/'+taskset.id+'/',
           success: function(msg){
               $( "#taskset-"+taskset.id ).remove();
           },
           error: function(msg){
                showError("Error Deleting Task", "")
            }
         });
    }
    $("#deletetasksetbutton-"+taskset.id).button({icons: {primary: "ui-icon-trash"}}).click(deletefunction)
}

function updatetaskbuttons(serviceid, profileid, tasksetid, taskid){
    deletefunction = function(){
         $.ajax({
           type: "DELETE",
           url: '/services/'+serviceid+'/profiles/'+profileid+'/tasks/'+taskid+'/',
           success: function(msg){
               $( "#task-"+taskid ).remove();
           },
           error: function(msg){
                showError("Error Deleting Task",msg.responseText)
            }
         });
    }
    updatefunction = function(){
            data = $("#taskform-task-"+taskid).serialize()
             $.ajax({
               type: "PUT",
               data: data,
               url: '/services/'+serviceid+'/profiles/'+profileid+'/tasks/'+taskid+'/',
               success: function(task){
                   var tasktmpl = $("#taskTemplate" ).tmpl( task, {"tasksetid" : tasksetid} )
                   console.log(task)
                   console.log(tasktmpl)
                    $( "#task-"+taskid ).replaceWith(tasktmpl);
                    updatetaskbuttons(serviceid, profileid, tasksetid, taskid)

               },
               error: function(msg){
                    showError("Error Updating Task",msg.responseText)
                }
             });
        }
    $("#edittaskbutton-"+taskid).button({icons: {primary: "ui-icon-disk"}}).click(updatefunction)
    $("#deletetaskbutton-"+taskid).button({icons: {primary: "ui-icon-trash"}}).click(deletefunction)
}

function user_request_service(requesturl){

    data = $("#user-request-service-form").serialize()

    var errorfield = $("#user-request-service-form-errors")
    errorfield.empty()

    var namefield = $("#user-request-service-form #id_name")
    namefield.removeClass( "ui-state-error" );
    if ( namefield.val() == "" || namefield.val() == null ) {
            namefield.addClass( "ui-state-error" );
            errorfield.text("Name field must not be empty")
            return false;
    }

    var reasonfield = $("#user-request-service-form #id_reason")
    reasonfield.removeClass( "ui-state-error" );
    if ( reasonfield.val() == "" || reasonfield.val() == null ) {S
            reasonfield.addClass( "ui-state-error" );
            errorfield.text("Please enter a reason!")
            return false;
    }

     $.ajax({
       type: "POST",
       url: requesturl,
       data: data,
       success: function(req){
            errorfield.empty()
            namefield.removeClass( "ui-state-error" );
            namefield.val("")
            reasonfield.removeClass( "ui-state-error" );
            reasonfield.val("")
            $("#requestTemplate").tmpl(req).prependTo("#pending-requests")
            $("#pending-requests .amessage").remove()
            make_request_buttons(requesturl,req)
            
       }
     });
}

function delete_service_request(url,request){

     $.ajax({
       type: "DELETE",
       url: url+request.id+"/",
       success: function(msg){
            $("#request-"+request.id).remove()
       }
     });
}
function update_service_request(requesturl,request,data){

     $.ajax({
       type: "PUT",
       url: requesturl+request.id+"/",
       data: data,
       success: function(request){
            $("#request-"+request.id).remove()
            if(!$("#pending-requests").html().trim()){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Pending Requests","cl":"amessage","isStaff": isStaff})
                message.appendTo( "#pending-requests" );
            }
            $("#requestTemplate").tmpl(request).prependTo("#done-requests")
            make_request_buttons(requesturl,request)
       }
     });
}

function load_user_requests(requesturl){

     $.ajax({
       type: "GET",
       url: requesturl,
       success: function(requests){

            pending = []
            done = []

            $(requests).each(function(index,request){
                if(request.state == "P"){
                    pending.push(request)
                }else{
                    done.push(request)
                }
            })

            if(pending.length==0){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Pending Requests","cl":"amessage","isStaff": isStaff})
                message.appendTo( "#pending-requests" );
            }

            if(done.length==0){
                message = $( "#messageTemplate" ).tmpl( {"message":"No Requests","cl":"amessage","isStaff": isStaff})
                message.appendTo( "#done-requests" );
            }

            $("#requestTemplate").tmpl(pending).appendTo("#pending-requests")
            $("#requestTemplate").tmpl(done).appendTo("#done-requests")
            $(requests).each(function(index,request){
                make_request_buttons(requesturl,request)
            })
       }
     });
}

function make_request_buttons(requesturl,request){
    $("#delete-button-"+request.id).button().click(function(){
        delete_service_request(requesturl,request)
    })
    $("#approve-button-"+request.id).button().click(function(){
        //update_service_request(requesturl,request,{"state":"A"})

        data = {"requesturl":requesturl,"request":request,"state":"A"}

        chooseContainer(data)
    })
    $("#reject-button-"+request.id).button().click(function(){
        update_service_request(requesturl,request,{"state":"R"})
    })
}

function mycallback(val,data){
    update_service_request(data.requesturl,data.request,{"state":data.state,"cid":val})
}

function chooseContainer(data){
    $.ajax({
       type: "GET",
       url: "/containers/",
       success: function(msg){
            containers = msg;
            choices = []
            $(containers).each(function(index,container){
               choices.push( {"name":container.name,"value":container.id} )
            })
            choose_dialog_ui(choices,"Input Needed", "Choose a Container", mycallback, data)
       }
     });
}

function choose_dialog_ui(choices, title, message, callback, data) {
    // a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
    $( "#dialog:ui-dialog" ).dialog( "destroy" );

    var containers = $( "#containers" ),
    allFields = $( [] ).add( containers ),
    tips = $( ".validateTips" );

    id = "dialog-id-"+Math.floor(Math.random()*1000)

    cdialog = $("#dialogTemplate").tmpl( {"id": id , "message" : message, "title": title} )

    inputbox = $('<select type="radio" >')

    $(choices).each(function(index,choice){
        $('<option value="'+choice.value+'" >'+choice.name+'</option>').appendTo(inputbox)
    })

    cdialog.append(inputbox)

    cdialog.dialog({
            autoOpen: false,
            height: 300,
            width: 350,
            modal: true,
            buttons: {
                    "Choose Container": function() {
                        callback(inputbox.val(),data)
                        $( this ).dialog( "close" );

                    },
                    Cancel: function() {
                            $( this ).dialog( "close" );
                    }
            },
            close: function() {
                    allFields.val( "" ).removeClass( "ui-state-error" );
            }
    });

    cdialog.dialog( "open" );

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
            
       }
     });
}

function ajax_delete_consumer_oauth(id,oauth_token,consumerurl){
     $.ajax({
       type: "DELETE",
       url: consumerurl+"/"+id+"/"+oauth_token+"/",
       success: function(msg){

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
                        mfile_buttons(gmfileid)
                    })();
                }

                if(newfileid != null){
                    $("#image-"+newfileid).show('drop')
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
       }
     });
}

function showMFolder(mfolderid){
    $("#mservetree").mserve( 'showMFolder' , mfolderid);
}

function doMFileButtons(mfile){
    (function() {
        var gid = mfile.id;
        var gmfileid = mfile.id;
        mfile_buttons(gmfileid)
        get_mfile_thumb(mfile)
    })();
}

function showmfiledialog(gmfileid){
        create_new_job_ui_dialog(gmfileid,true)
        $("#mfileid").val(gmfileid);
        $("#dialog-new-job-dialog-form").dialog( "open" );
}

function mfile_buttons(gmfileid){
    $("#newjobbutton-"+gmfileid ).button({icons: {primary: "ui-icon-transferthick-e-w"}, text: false});
    $('#newjobbutton-'+gmfileid).click(function(){
        create_new_job_ui_dialog(gmfileid,true)
        $("#mfileid").val(gmfileid);
        $("#dialog-new-job-dialog-form").dialog( "open" );
    });
    //$("#deletemfilebutton-"+gmfileid ).button({ icons: { primary: "ui-icon-trash"}, text: false });
    //$('#deletemfilebutton-'+gmfileid).click(function(){
    //    $("#mservetree").mserve('deletemfile', gmfileid)
    //});
}

function mfile_delete(mfileid){
        $("#mservetree").mserve('deletemfile', mfileid)
 }

$(document).ready(function(){
	$('.accordion .head').click(function() {
		$(this).next().toggle('slow');
		return false;
	}).next().hide();
});

function mfile_get(mfileid){
        window.open("/mfiles/"+mfileid+"/file/")
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