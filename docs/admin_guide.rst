MServe Admin Guide
###################

Welcome to the MServe Admin Guide

Administration of an MServe installation
*****************************************

You must have an administration login to edit an MServe Installation.

If you have just installed MServe login details will be stored at /opt/mserve/.installation_summary.txt


Creating a Container
********************

A *Hosting Container* is a logical object for grouping sets of services together.

Login to MServe and click **New Container**, containers control groups of services. A service must be created under a container.


Configure a Container
*********************

Login to MServe and choose the container to edit. The name of the container can be changed, and the default profile for newly created services can be set.

Advanced configuration allows files to be saved under a non default path (leave this blank).

Click **Update** to save changes


Creating a Service
********************

Login to MServe and choose the container under which the new service will be created.

Click **New Service** and input a service name, start and end time in the relevant dialog boxes.

In order to give a customer access to the new service, click on the service and open the **Access Control** tab copy the customer link and send this to the customer.
