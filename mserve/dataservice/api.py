
generic_get_methods = ["getauths","getroles"]

generic_post_methods = ["getorcreateauth","addauth"]

generic_put_methods = ["setroles"]

generic_delete_methods = ["revokeauth"]

generic_methods = ["usage","getusagesummary","getroleinfo","getmanagedresources"] + generic_get_methods + generic_post_methods + generic_put_methods + generic_delete_methods

all_container_methods = ["makeserviceinstance","getservicemetadata","getdependencies",
    "getprovides","setresourcelookup", "getstatus","setmanagementproperty","getmanagementproperties"] + generic_methods

service_customer_methods =  ["createmfile"] + generic_methods
service_admin_methods =  service_customer_methods + ["setmanagementproperty","getmanagementproperties"]

all_service_methods = [] + service_admin_methods

mfile_monitor_methods = ["getusagesummary"]
mfile_owner_methods = ["info", "get", "put", "post", "delete", "verify"] + generic_methods

all_mfile_methods = mfile_owner_methods + mfile_monitor_methods