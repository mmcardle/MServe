########################################################################
#
# University of Southampton IT Innovation Centre, 2011
#
# Copyright in this library belongs to the University of Southampton
# University Road, Highfield, Southampton, UK, SO17 1BJ
#
# This software may not be used, sold, licensed, transferred, copied
# or reproduced in whole or in part in any manner or form or in or
# on any media by any person other than in accordance with the terms
# of the Licence Agreement supplied with the software, or otherwise
# without the prior written consent of the copyright owners.
#
# This software is distributed WITHOUT ANY WARRANTY, without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE, except where stated in the Licence Agreement supplied with
# the software.
#
#	Created By :			Mark McArdle
#	Created Date :			2011-03-25
#	Created for Project :		PrestoPrime
#
########################################################################

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