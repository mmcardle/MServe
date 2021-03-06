
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
                    $(this).mserve('loadUser');
                }
            }else if(page.startsWith('/services/')){
                var str = page.split(/\//g)
                var serviceid = str[2]
                var url = "/"+str[1]+"/"+serviceid
                var tab = str[3]
                var mfile = str[4]

                data["currentserviceurl"] = url

                if(!data.cache[serviceid]){
                    console.log("Service is not cached")
                    $this.empty()
                    $(this).mserve('loadService', url, tab, mfile);
                }else{
                    data.allcontent = data.contentcache[serviceid]
                    if($(this).find("#tabs-"+serviceid).length <= 0){
                        console.log("Service is cached - but not on service page")
                        $(this).empty()
                        $(this).mserve('loadService', url, tab, mfile);
                    }else{
                        console.log("Service is cached and on service page - showing tab")
                        $(this).mserve('showServiceTab', data[serviceid], tab, mfile);
                    }
                }
            }else if(page.startsWith('/auths/')){
                var authstr = page.split(/\//g)
                var authid = authstr[2]
                var authurl = "/"+authstr[1]+"/"+authid
                var authtab = authstr[3]
                var authmfile = authstr[4]

                data["currentserviceurl"] = authurl

                if(!data.cache[authid]){
                    console.log("Auth is not cached")
                    $this.empty()
                    $(this).mserve('loadServiceAuth', authurl, authtab, authid, authmfile);
                }else{
                    data.allcontent = data.contentcache[authid]
                    if($(this).find("#tabs-"+authid).length <= 0){
                        console.log("ServiceAuth is cached - but not on service page")
                        $(this).empty()
                        $(this).mserve('loadServiceAuth', authurl, authtab, authid, authmfile);
                    }else{
                        console.log("ServiceAuth is cached and on service page - showing tab")
                        $(this).mserve('showServiceTab', data[authid], authtab, authmfile);
                    }
                }
            }else if(page.startsWith('/mfiles/')){
                console.log("loading MFile page "+page)
                var str = page.split(/\//g)
                url = str[1]+"/"+str[2]
                tab = str[3]
                $this.mserve('showMFile', str[2]);
            }else{
                console.log("dont know how to load "+page)
            }
            data["currentpage"] = page
            $.address.value(page);
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
                       url: container.services_url,
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
               url: hostingcontainers_url,
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

                    $("#containertabs").tabs().tabs( "add", "#tabs-requests" , "Service Requests" );
                    $(this).mserve('loadRequests', $("#tabs-requests"), true);

                    $("#createcontainerbutton").button()
                    $("#createcontainerbutton" ).click(function() {
                        data = $("#createcontainerform").serialize()
                         $.ajax({
                           type: "POST",
                           data: data,
                           url: hostingcontainers_url,
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

                    containersperpage = 2

                    function onChangePage(new_page_index) {
                        $this.find("#containerholder").empty()
                        start = (new_page_index-1)*containersperpage
                        end   = (new_page_index)*containersperpage
                        if(end>containers.length){
                            end=containers.length;
                        }
                        slice = containers.slice(start, end)
                        $(slice.reverse()).each(function(index,container){
                            $(obj).mserve('initContainer', container)
                        })
                        return false;
                    }

                    $servicetab.find("#containerpaginator").smartpaginator({ totalrecords: containers.length, recordsperpage: containersperpage, initval:1 , next: 'Next',
                        prev: 'Prev', first: 'First', last: 'Last', theme: 'smartpagewhite', onchange: onChangePage
                    });

                    onChangePage(1)

               },
               error: function(msg){
                    $("#containermessages").append("<div class='message'>Failed to get containers</div>");
               }
             });

        });
    },
    loadRequests: function( obj, staff ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var $this = $(this),
                data = $this.data('mserve');
                $user = $("#userTemplate").tmpl( {staff : staff} )

                obj.append($user)
                $('#user-request-service-button').click( function(){
                    user_request_service(user_requests_url)
                });
                load_user(users_url, consumer_url,"#mfileTemplate");
                load_user_requests(user_requests_url);
            });
    },
    loadUser: function( obj, staff ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var $this = $(this),
                data = $this.data('mserve');
                $this.append("<div id='usertabs' ><ul></ul></div>");
                $("#usertabs").tabs().tabs( "add", "#tabs-user" , "User" );
                $(this).mserve('loadRequests', $("#tabs-user"), false );
            });
    },
    showServiceTab: function( service, tab, mfile ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var $this = $(this),
                data = $this.data('mserve');
                if(tab == "mfile" && mfile){
                    $($this).mserve('showMFile', mfile)
                }else if(tab == "mfolder" && mfile){
                    $($this).mserve('showMFolder', mfile)
                }else if(tab){
                    $tabs.tabs('select', '#' + tab+"tab-"+service.id);
                }else{
                    $tabs.tabs('select', '#servicetab-'+service.id);
                }
                
            });
    },
    loadRemoteServices: function(authid, accordian) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var $this = $(this),
                data = $this.data('mserve');

                  $.ajax({
                   type: "GET",
                   url: remoteservice_url,
                   success: function(msg){
                       if(msg.length==0){
                            $( "#import-dialog-items" ).append("<div class='ui-widget-content ui-corner-all ui-state-error'>No known Remote Services</div>")
                       }

                       $.each(msg, function(i,remoteservice){
                            service = $("<div><button id='remoteserviceicon'"+remoteservice.id+">Text</button>&nbsp;Import data from <a href='#' id='remoteservicebutton-"+remoteservice.id+"' style='text-decoration:underline' >"+remoteservice.url+"</a></div>")
                            service.appendTo(accordian.find("#remote-services"))
                            service.find("#remoteserviceicon").button({
                                icons: {
                                    primary: "ui-icon-transferthick-e-w"
                                },
                                text: false
                            })
                            
                            $("#remoteservicebutton-"+remoteservice.id+",#remoteserviceicon").click(
                                function() {
                                     var data = $.param({ "url" : remoteservice.url,"authid" : authid })
                                     $.ajax({
                                       type: "POST",
                                       data: data,
                                       url: consumer_url,
                                       success: function(msg){
                                           m = $("<div style='padding:2px;align:left'><button id='aiClose'>Close</button></div><iframe src="+msg.authurl+" width='100%' height='100%'><p>Your browser does not support iframes.</p></iframe>" );
                                            $.blockUI({message: m, css: {
                                                top:  '50px',
                                                left:  '50px',
                                                width: ($(window).width() - 100) + 'px',
                                                height: ($(window).height() - 100) + 'px'
                                            }});
                                            $("#aiClose").button().click(function() {
                                                $.unblockUI();
                                            });
                                       },
                                       error: function(msg){
                                           showError("Error Loading Remote Service", "Sorry the service could not be loaded - "+ msg.responseText)
                                       }
                                     });
                                }
                            );
                       });


                   },
                   error: function(msg){
                       showError("Error Loading Remote Services", msg)
                   }
                 });

            });
    },
    loadServiceAuth: function(url, tab, authid, mfile) {
        var defaults = {};
        var options = $.extend(defaults, options);
        return this.each(function() {
            var o = options;
            var obj = $(this);

            var $this = $(this), data = $this.data('mserve')
            $.ajax({
               type: "GET",
               url: url,
               success: function(auth){
                    $.ajax({
                       type: "GET",
                       url: auth.base_url,
                       success: function(authbase){

                           data[authid] = authbase
                           data["mfiles"] = authbase.mfile_set
                           data["mfolders"] = authbase.mfolder_set

                           $(authbase.mfile_set).each( function(index, mfile){
                                data[mfile.id] = mfile
                           })
                           $(authbase.mfolder_set).each( function(index, mfolder){
                                data[mfolder.id] = mfolder
                           })

                            $tabs = $("#tabsTemplate").tmpl( {"tabid":authid,"tabs":[
                                {name:"Service Data",id:"servicetab-"+authid,url:url},
                                {name:"Jobs",id:"jobstab-"+authid,url:auth.jobs_url},
                                {name:"Usage",id:"usagetab-"+authid,url:auth.usage_url}
                            ]} )

                            $table = $("#mserveTemplate").tmpl()
                            $table.find("#mserve-container-title").html(authbase.name)
                            $this.mserve( "loadRemoteServices", authid, $table.find('#import-accordion') )

                            $table.find("#importbutton").button(
                                {icons: {primary: "ui-icon-circle-plus"}}
                                ).click( function(){
                                    create_new_import_ui_dialog(authid,remoteservice_url,consumer_url)
                            })

                            $table.find("#mserve-new-folder-button").button(
                                {icons: {primary: "ui-icon-circle-plus"}}
                            )

                            $(obj).append($tabs);
                            $servicetab = $("#servicetab-"+authid);
                            $servicetab.append( $("#messageTemplate").tmpl({"message":"Here is a list of files stored at this MServe Service, click File Upload to upload more files,  or Drag and Drop files"})  );
                            $servicetab.append("<input  type=\"checkbox\" id=\"fileuploadautobutton\" /><label for=\"fileuploadautobutton\">Auto upload</label>");
                            $servicetab.append($table);

                            $usageHolderTemplate  = $("#usageHolderTemplate").tmpl()
                            $("#usagetab-"+authid).append($usageHolderTemplate);

                            $("#jobstab-"+authid).append("<div id='jobspaginatorheader'></div><div id='jobspaginator'><div class='spinner'><span class='red'>Loading Jobs...</span></div></div>");

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
                                mfolder_set : authbase.mfolder_set,
                                mfile_set : authbase.mfile_set,
                                folder_structure : authbase.folder_structure
                            } , mfile)

                            data["currentfolderstructure"] = authbase.folder_structure

                            $.getScript(MEDIA_URL+'js/jquery-file-upload/jquery.fileupload-ui.js');

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
                                url: auth.mfiles_url,
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
               }
            })



        });
    },
    loadService: function(url, tab, mfile) {
        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);

            var $this = $(this), data = $this.data('mserve')
             $.ajax({
               type: "GET",
               url: url,
               success: function(service){

                   data[service.id] = service
                   data["mfiles"] = service.mfile_set
                   data["mfolders"] = service.mfolder_set
                   data["service"] = service

                   $(service.mfile_set).each( function(index, mfile){
                        data[mfile.id] = mfile
                   })
                   $(service.mfolder_set).each( function(index, mfolder){
                        data[mfolder.id] = mfolder
                   })

                    $tabs = $("#tabsTemplate").tmpl( {"tabid":service.id,"tabs":[
                        {name:"Service Data",id:"servicetab-"+service.id,url:url},
                        {name:"Jobs",id:"jobstab-"+service.id,url:url+"/jobs"},
                        {name:"Config",id:"configtab-"+service.id,url:url+"/config"},
                        {name:"Usage",id:"usagetab-"+service.id,url:url+"/usage"}
                    ]} )

                    $table = $("#mserveTemplate").tmpl()
                    
                    $table.find("#mserve-container-title").html(service.name)
                    $table.find('#import-accordion').hide()

                    $table.find("#mserve-new-folder-button").button(
                        {icons: {primary: "ui-icon-circle-plus"}}
                    )

                    $(obj).append($tabs);
                    $servicetab = $("#servicetab-"+service.id);
                    $servicetab.append( $("#messageTemplate").tmpl({"message":"Here is a list of files stored at this MServe Service, click File Upload to upload more files,  or Drag and Drop files"})  );
                    $servicetab.append("<input  type=\"checkbox\" id=\"fileuploadautobutton\" /><label for=\"fileuploadautobutton\">Auto upload</label>");
                    $servicetab.append($table);

                    $usageHolderTemplate  = $("#usageHolderTemplate").tmpl()
                    $("#usagetab-"+service.id).append($usageHolderTemplate);

                    $("#jobstab-"+service.id).append("<div id='jobspaginatorheader'></div><div id='jobspaginator'><div class='spinner'><span class='red'>Loading Jobs...</span></div></div>");
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

                    $("#profilepaginator").mserve( "serviceprofiles", service )

                    $.ajax({
                       type: "GET",
                       url: service.properties_url,
                       success: function(properties){
                           $.each(properties, function(i, property){
                                render_managementproperty(service.id, service.properties_url, property)
                           });
                       }
                     });

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
                            loadJobs("/services/"+service.id+"/jobs/")
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
                    } , mfile )

                    data["currentfolderstructure"] = service.folder_structure

                    $.getScript(MEDIA_URL+'js/jquery-file-upload/jquery.fileupload-ui.js');
                    
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
                        url: service.mfiles_url,
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
    get_mfile_thumb: function(mfile, depth){

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
                   url: mfile.url,
                   success: function(newmfile){
                        if(newmfile.thumb != ""){
                            var mfilecache = $(data.allcontent[0]).find("#mfile-table-"+mfile.id)
                            mfilecache.css("background-image", "url('"+newmfile.thumburl+"')");
                            $("#mfile-table-"+mfile.id).css("background-image", "url('"+newmfile.thumburl+"')");
                        }else{
                            setTimeout(mservetimeout, 3000 ,obj, mfile, depth+1)
                        }
                   }
               });
            }

        });
    },
    updateMFolder : function( mfolder) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);
                var $this = $(this),
                data = $this.data('mserve');
                $(data.allcontent).find("#deletemfolderbutton-"+mfolder.id).button()
                $("#deletemfolderbutton-"+mfolder.id).button()
            });
    },
    updatemfile : function( mfile, options ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');

                if (data.allcontent){
                    var poster = $('#mfileposterholder-'+mfile.id);
                    poster.remove()
                    var $mfpt = $("#mfilePosterTemplate" ).tmpl( mfile )
                
                    $mfpt.find(".mfile_download_button-"+mfile.id).button()
                    $mfpt.find(".mfile_delete_button-"+mfile.id).each(function(index, delbut){
                        $(delbut).button().click(function(){ $(obj).mserve('deletemfile', mfile) })
                    })
                    $mfpt.find(".mfile_relationship_button-"+mfile.id).each(function(index, relbut){
                        $(relbut).button().click(function(){ $(obj).mserve('createMFileRelationship', mfile) })
                    })
                    $mfpt.find(".mfile_rename_button-"+mfile.id).each(function(index, renamebut){
                        $(renamebut).button().click(function(){ $(obj).mserve('renameMFile', mfile) })
                    })

                    data.allcontent.remove("#mfileposterholder-"+mfile.id)
                    data[mfile.id] = mfile
                }

                $("#mfoldertreecontainer").jstree('rename_node',"#"+mfile.id, mfile.name)

                if(options.pollthumb){
                    obj.mserve('get_mfile_thumb', mfile, 1)
                }
            });
    },
    deletemfile : function(mfile) {

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
                                       url: mfile.url,
                                       success: function(msg){
                                            $("#mfoldertreecontainer").jstree("remove", "#"+mfile);
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
    addMFolder : function( mfolder ){

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');
                data[mfolder.id] = mfolder

                var $mft = $("#mfolderTemplate" ).tmpl( mfolder )

                $(obj).mserve('updateMFolder', mfolder)

                data.allcontent.prepend($mft.clone(true,true))

                selected = $("#mfoldertreecontainer").jstree("get_selected")
                if($(selected).hasClass("service") || selected == 0){
                    $('#qscontainer').prepend($mft)
                    $mft.show('slide');
                }

                if(mfolder.parent){
                    pnode = $("#mfoldertreecontainer #"+mfolder.parent.id)
                }else{
                    pnode = $("#mfoldertreecontainer .service")
                }

                $("#mfoldertreecontainer").jstree("create", pnode, "first",
                    {"data" : {
                            "title" : mfolder.name,
                            "icon" : mfolder.thumburl
                            },
                        "attr" : {
                            "id": mfolder.id,
                            "class" : "mfolder"
                            }
                    }, null, true    );
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
                $(obj).mserve('updatemfile', mfile, {"pollthumb":true})

                data.allcontent.prepend($mft.clone(true,true))
               
                selected = $("#mfoldertreecontainer").jstree("get_selected")
                if($(selected).hasClass("service") || selected.length ==0){
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
                var obj = $(this);
                var $this = $(this),
                data = $this.data('mserve');
                service = data[serviceid]
                currentservicepage = data["currentserviceurl"]
                $.address.value(currentservicepage);
                $("#mfilejobcontainer").hide()
                $("#mserve-container-title").html(service.name)

                buttons = $("#mserve-title-buttons")
                buttons.empty()
                newfolderbutton = $('<button >New Folder</button>')
                newfolderbutton.button().click(function(){
                        $(obj).mserve("createMFolder", null,  service)
                })
                buttons.append(newfolderbutton)

                $("#mserve-titlebar-container").show()
                var $filteredData = data.allcontent.find('li.rootfolder');
                if($filteredData.length==0){
                    $(".nofiles").show()
                }else{
                    $(".nofiles").hide()
                }
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
                var obj = $(this);
                var $this = $(this),
                data = $this.data('mserve');
                mfolder = data[mfolderid]
                currentservicepage = data["currentserviceurl"]
                $.address.value(currentservicepage+'/mfolder/'+mfolderid);
                var $filteredData = $(data.allcontent[0]).find('li.'+mfolderid);
                if($filteredData.length==0){
                    $(".nofiles").show()
                }else{
                    $(".nofiles").hide()
                }
                $("#mfilejobcontainer").hide()
                $("#mserve-container-title").html("<h3>"+mfolder.name+"</h3>")

                buttons = $("#mserve-title-buttons")
                buttons.empty()
                newfolderbutton = $('<button >New Folder</button>')
                newfolderbutton.button().click(function(){
                        $(obj).mserve("createMFolder", mfolder)
                })
                buttons.append(newfolderbutton)

                $("#mserve-titlebar-container").show()
                $('#qscontainer').quicksand($filteredData, {
                  duration: 800,
                  easing: 'easeInOutQuad'
                });
            });
    },
    selectNode : function( id ) {

        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            $("#mfoldertreecontainer").jstree("deselect_all")
            if(id){
                $("#mfoldertreecontainer").jstree("select_node", $("#"+id))
            }else{
                $("#mfoldertreecontainer").jstree("select_node", $(".service"))
            }
        })
    },
    renameMFile : function( mfile ) {

        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);
            callback = function(name){
                $.ajax({
                   type: "PUT",
                   url: mfile.url,
                   data: "name="+name,
                   success: function(mfile){
                        $(obj).mserve( 'updatemfile', mfile, {"pollthumb":false})
                   }
                });
            }
            $(obj).mserve("getInput", "Enter new name", mfile.name, callback)
        })
    },
    getInput : function( title, value, callback ) {

        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {

            // Build dialog markup
            var win = $('<div><p>'+title+'</p></div>');
            var userInput = $('<input type="text" value="'+value+'" style="width:100%"></input>');
            userInput.appendTo(win);

            // Display dialog
            $(win).dialog({
                'modal': true,
                'buttons': {
                    'Ok': function() {
                        $(this).dialog('close');
                        callback($(userInput).val());
                    },
                    'Cancel': function() {
                        $(this).dialog('close');
                    }
                }
            });


        })
    },
    createMFileRelationship_ajax : function( mfile1, mfileid2, name ) {

        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);
            $.ajax({
               type: "POST",
               url: mfile1.relationships_url,
               data: "mfileid="+mfileid2+"&name="+name,
               success: function(rela){
                   $(obj).mserve('updatemfile', mfile1)
               }
            });
        })
    },
    createMFileRelationship : function( mfile ) {

        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
            var o = options;
            var obj = $(this);
            var $this = $(this),
            data = $this.data('mserve');
            $(obj).mserve('chooseMFile', mfile, "createMFileRelationship_ajax" )
        })
    },
    chooseMFile : function( mfile, callback ) {
        
        var defaults = {};
        var options = $.extend(defaults, options);

        return this.each(function() {
                var o = options;
                var obj = $(this);
                var $this = $(this),
                data = $this.data('mserve');

                cdialog = $("#dialogTemplate").tmpl( {"id": Math.floor(Math.random()*1000) , "message" : "Please input a relationship and choose a file", "title": "Input Required"} )
                errorbox = $("<div></div>")
                namelabel = $('<label for="name" >Relationship</label>')
                relationbox = $('<input style="margin:4px" type="text" id="name" ></input>')
                cdialog.append(errorbox).append(namelabel).append(relationbox)
                choosertree = $('<div id="choosertree">')
                cdialog.append(choosertree)
                choosertree.jstree({
                     "json_data" : data["currentfolderstructure"],
                     "themes" : {"theme" : "default"},
                     "plugins" : [ "themes", "json_data", "ui", "crrm"]
                    }
                ).bind("loaded.jstree", function (event, data) {
                    choosertree.jstree("open_node", ".service");
                });
                
                cdialog.dialog({
                        autoOpen: false, height: 520, width: 400, modal: true,
                        buttons: {
                                "Choose": function() {
                                    errorbox.empty()
                                    relation = relationbox.val()
                                    selected = choosertree.jstree("get_selected")
                                    if(selected.length>1){
                                        errormsg = $( "#strongMessageTemplate" ).tmpl( {"message":"Please choose a single file"} )
                                        errorbox.append(errormsg)
                                    }else{
                                        mfile2 = selected.attr("id")
                                        if(!mfile2){
                                            $(choosertree).addClass( "ui-state-error" );
                                            errormsg = $( "#strongMessageTemplate" ).tmpl( {"message":"Please choose a file"} )
                                            errorbox.append(errormsg)
                                        }else if (relation == ""){
                                            $(relationbox).addClass( "ui-state-error" );
                                            errormsg = $( "#strongMessageTemplate" ).tmpl( {"message":"Please enter a name for the relationship"} )
                                            errorbox.append(errormsg)
                                        }else{
                                            $(obj).mserve(callback, mfile, mfile2 , relation )
                                            $( this ).dialog( "close" );
                                        }
                                    }
                                },
                                Cancel: function() {
                                        $( this ).dialog( "close" );
                                        cdialog.remove()
                                }
                        },
                        close: function() {
                                cdialog.remove()
                        }
                });
                
                cdialog.dialog( "open" );

        })
    },
    showMFile : function( id ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {

                var o = options;
                var obj = $(this);

                var $this = $(this),
                data = $this.data('mserve');

                currentservicepage = data["currentserviceurl"]
                $.address.value(currentservicepage+'/mfile/'+id);
                mfile = data[id]

                var $filteredData = data.allcontent.find('#mfileposterholder-'+id);

                if(!$filteredData.length>0){
                    var $mfpt = $("#mfilePosterTemplate" ).tmpl( data[id] )
                    data.allcontent.append($mfpt)
                    $mfpt.find(".mfile_rename_button-"+id).button()
                    $mfpt.find(".mfile_download_button-"+id).button()
                    $mfpt.find(".mfile_delete_button-"+id).button()
                    $mfpt.find(".mfile_relationship_button-"+id).button()
                    $filteredData = $mfpt
                }

                
                $("#mserve-titlebar-container").hide()
                
                $("#mfilecreatejobcontainer").empty().append($("#jobSubmitTemplate").tmpl())
                var $form = $("#mfilecreatejobcontainer").find("form")

                $("#mfilecreatejobcontainer").find(".jobsubmit").button().click(function(){
                        var postdata =  $form.serialize()
                        $(obj).mserve('createMFileJob', id, postdata)
                })

                $.ajax({
                   type: "GET",
                   url: mfile.jobs_url,
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

                $(".nofiles").hide()
                $('#qscontainer').quicksand($filteredData, {
                    adjustHeight: 'dynamic',
                    duration: 800,
                    easing: null
                }, function(){
                    $(".mfile_delete_button-"+id).each(function(index, delbut){
                        $(delbut).click(function(){ $(obj).mserve('deletemfile', mfile) })
                    })
                    $(".mfile_relationship_button-"+id).each(function(index, delbut){
                        $(delbut).click(function(){ $(obj).mserve('createMFileRelationship', mfile) })
                    })
                    $(".mfile_rename_button-"+id).each(function(index, renamebut){
                        $(renamebut).click(function(){ $(obj).mserve('renameMFile', mfile) })
                    })
                    $("#mfilejobcontainer").show('slow')
                });

                $.ajax({
                   type: "GET",
                   url: tasks_url,
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
                                    $form.find(".argsmessage").append($( "#messageTemplate" ).tmpl( {"message":"This Job type takes no arguments"} ))
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
                                               url: users_url,
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

                    $('#jobpreviewpaginatorheader-'+job.id).hide()
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
                $('#jobpreviewpaginatorheader-'+job.id).toggle('blind');
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
    deleteMFolder : function( id, url, parent) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);
                var $this = $(this),
                data = $this.data('mserve');

                $.ajax({
                    type: "DELETE",
                    url: url,
                    success: function(folder){
                        $("#mfoldertreecontainer").jstree("remove", "#"+id);
                        $(data.allcontent).find("#mfolderholder-"+id).remove()
                        console.log("selectNode "+parent)
                        $(obj).mserve('selectNode', parent)
                    },
                    error: function(msg){
                        showError("Error creating folder", msg.responseText)
                    }
                });
            });
    },
    createMFolder : function( parentfolder, service ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);

                postdata = {}
                if(parentfolder){
                    id = parentfolder.id
                    postdata["parent"] = id
                    url = parentfolder.url
                }else{
                    url = service.mfolders_url
                }

                callback = function(name){
                     postdata["name"] = name
                     $.ajax({
                       type: "POST",
                       data: postdata,
                       url: url,
                       success: function(folder){
                           $(obj).mserve("addMFolder", folder)
                           if(postdata["parent"]){
                              $(obj).mserve("showMFolder", id)
                           }
                       },
                       error: function(msg){
                           showError("Error creating folder", msg.responseText)
                       }
                     });
                }
                $(obj).mserve("getInput", "Enter new folder name", "newfolder", callback)

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
    serviceprofiles : function(service){

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);
                var $this = $(this),
                data = $this.data('mserve');

                $.ajax({
                   type: "GET",
                   url: tasks_url,
                   success: function(tasks){
                        $.ajax({
                           type: "GET",
                           url: service.profiles_url,
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

                                $(profiles).each(function(pindex, profile){
                                    $(profile.workflows).each(function(windex, workflow){
                                        var _tasksets = {}
                                        $(workflow.tasksets).each(function(tsindex, taskset){
                                            _tasksets[taskset.id] = taskset
                                        });
                                        $("#addbutton-taskset-"+workflow.id).button({icons: {primary: "ui-icon-disk"}}).click(
                                        function(){
                                                 data = $("#newtasksetform-workflow-"+workflow.id).serialize()
                                                 $.ajax({
                                                   type: "POST",
                                                   data: data,
                                                   url: profile.tasksets_url,
                                                   success: function(newtaskset){
                                                        var tasksettmpl = $("#taskSetTemplate" ).tmpl( newtaskset, {"workflowid" : workflow.id} )
                                                        tasksettmpl.appendTo("#workflowbody-"+workflow.id );
                                                        updatetasksetbuttons(service, profile, workflow.id, newtaskset)
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
                                                $("#workflowbody-"+workflow.id).find(".taskset").each( function(tindex, taskset){
                                                    $("#workflowsavedmsg-"+workflow.id).hide()
                                                    var tasksetid = $(taskset).attr("data-taskid")
                                                    var index = $(taskset).parent().children().index(taskset)
                                                    form = $(taskset).find("#tasksetupdateform-taskset-"+tasksetid)
                                                    form.find("input[name=order]").val(index)
                                                    data = form.serialize()
                                                     $.ajax({
                                                           type: "PUT",
                                                           data: data,
                                                           url: _tasksets[tasksetid].url,
                                                           success: function(updatedtaskset){
                                                               var tasksettmpl = $("#taskSetTemplate").tmpl( updatedtaskset , {"workflowid":workflow.id} )
                                                               $( "#taskset-"+updatedtaskset.id ).replaceWith(tasksettmpl);
                                                               updatetasksetbuttons(service, profile, workflow.id, updatedtaskset)
                                                               $(updatedtaskset.tasks).each(function(newtindex, task){
                                                                    updatetaskbuttons(service, profile.id, updatedtaskset.id, task)
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
                                            updatetasksetbuttons(service, profile, workflow.id, taskset)
                                            $(taskset.tasks).each(function(tindex, task){
                                                updatetaskbuttons(service, profile.id, taskset.id, task)
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
    loadMTree : function( options, node ) {

            var defaults = {};
            var options = $.extend(defaults, options);

            return this.each(function() {
                var o = options;
                var obj = $(this);
                var $this = $(this),
                mservedata = $this.data('mserve');

                var serviceid = o.serviceid
                var mfolder_set = o.mfolder_set
                var mfile_set =  o.mfile_set
                var folder_structure = o.folder_structure

                $("#mfolderTemplate").tmpl(mfolder_set).appendTo("#hiddenqscontainer")
                $("#mfileTemplate").tmpl(mfile_set).appendTo("#hiddenqscontainer")

                $(mfile_set).each( function(index, mfile) {
                    $(obj).mserve( 'updatemfile', mfile, {"pollthumb":false})
                });
                $(mfolder_set).each( function(index, mfolder) {
                    $(obj).mserve( 'updateMFolder', mfolder)
                });

                var servicecontent = $('#hiddenqscontainer').clone(true,true)
                mservedata.contentcache[serviceid] = servicecontent
                mservedata["allcontent"]= servicecontent

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
                    $("#mfoldertreecontainer").jstree("open_node", "#"+serviceid);
                    $(obj).mserve("selectNode", node);
                });
            });
    }
  };

  $.fn.mserve = function( method ) {

    // Method calling logic
    if ( methods[method] ) {
        console.log(method, arguments)
      return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
      return methods.init.apply( this, arguments );
    } else {
      $.error( 'Method ' +  method + ' does not exist on jQuery.mserve' );
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
            var mfilesperpage= 4

            function onChangePage(new_page_index) {
                start = (new_page_index-1)*mfilesperpage
                end   = (new_page_index)*mfilesperpage
                if(end>mfiles.length){
                    end=mfiles.length;
                }

                $( template ).tmpl( mfiles.slice(start,end) ) .appendTo( "#user_mfileholder" );
                return false;
            }

            $("#user_mfilepager").smartpaginator({ totalrecords: mfiles.length, recordsperpage: mfilesperpage, initval:1 , next: 'Next',
                prev: 'Prev', first: 'First', last: 'Last', theme: 'smartpagewhite', onchange: onChangePage
            });

            onChangePage(1)

            var myauths = msg.myauths
            var authsperpage = 4

            function onChangePage2(new_page_index) {
                start = (new_page_index-1)*authsperpage
                end   = (new_page_index)*authsperpage
                if(end>myauths.length){
                    end=myauths.length;
                }

                $( "#authTemplate" ).tmpl( myauths.slice(start,end) ) .appendTo( "#user_authholder" );
                return false;
            }

            $("#user_authpager").smartpaginator({ totalrecords: myauths.length, recordsperpage: authsperpage, initval:1 , next: 'Next',
                prev: 'Prev', first: 'First', last: 'Last', theme: 'smartpagewhite', onchange: onChangePage2
            });

            onChangePage2(1)

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



function mservetimeout(obj,mfile,depth){
    $(obj).mserve('get_mfile_thumb', mfile , depth )
}

function updatetasksetbuttons(service, profile, workflowid, taskset){
    $("#addbutton-task-"+taskset.id).button({icons: {primary: "ui-icon-disk"}}).click(
        function(){
                 data = $("#newtaskform-taskset-"+taskset.id).serialize()
                 $.ajax({
                   type: "POST",
                   data: data,
                   url: profile.tasks_url,
                   success: function(newtask){
                        var tasktmpl = $("#taskTemplate" ).tmpl( newtask, {"tasksetid" : taskset.id} )
                        tasktmpl.appendTo( "#tasksetbody-"+taskset.id );
                        updatetaskbuttons(service, profile.id, taskset.id, newtask)
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
           url: taskset.url,
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

function updatetaskbuttons(service, profileid, tasksetid, task){
    deletefunction = function(){
         $.ajax({
           type: "DELETE",
           url: task.url,
           success: function(msg){
               $( "#task-"+task.id ).remove();
           },
           error: function(msg){
                showError("Error Deleting Task",msg.responseText)
            }
         });
    }
    updatefunction = function(){
            data = $("#taskform-task-"+task.id).serialize()
             $.ajax({
               type: "PUT",
               data: data,
               url: task.url,
               success: function(task){
                   var tasktmpl = $("#taskTemplate" ).tmpl( task, {"tasksetid" : tasksetid} )
                    $( "#task-"+task.id ).replaceWith(tasktmpl);
                    updatetaskbuttons(serviceid, profileid, tasksetid, task)

               },
               error: function(msg){
                    showError("Error Updating Task",msg.responseText)
                }
             });
        }
    $("#edittaskbutton-"+task.id).button({icons: {primary: "ui-icon-disk"}}).click(updatefunction)
    $("#deletetaskbutton-"+task.id).button({icons: {primary: "ui-icon-trash"}}).click(deletefunction)
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

function delete_service_request(request){
     $.ajax({
       type: "DELETE",
       url: request.url,
       success: function(msg){
            $("#request-"+request.id).remove()
       }
     });
}
function update_service_request(requesturl, request, data){

     $.ajax({
       type: "PUT",
       url: request.url,
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
        delete_service_request(request)
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
       url: hostingcontainers_url,
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

function ajax_delete_consumer_oauth(id, oauth_token, consumerurl){
     $.ajax({
       type: "DELETE",
       url: consumerurl+"/"+id+"/"+oauth_token+"/",
       success: function(msg){

       }
     });
}

$(document).ready(function(){
	$('.accordion .head').click(function() {
		$(this).next().toggle('slow');
		return false;
	}).next().hide();
});
