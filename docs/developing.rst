#################################
MServe Development Guide
#################################

------------------------
Introduction
------------------------

DataService Models
--------------------

.. automodule:: dataservice.models

Base class
+++++++++++

.. autoclass:: dataservice.models.Base
    :noindex:
    
NamedBase class
+++++++++++++++++

.. autoclass:: dataservice.models.NamedBase
    :noindex:

::

  # Get a NamedBase from the database
  from dataservice.models import NamedBase
  base = NamedBase.object.get(id="baseid")
  
Hosting Container class
++++++++++++++++++++++++

.. autoclass:: dataservice.models.HostingContainer
    :noindex:

::

  # Create a new HostingContainer
  from dataservice.models import HostingContainer
  hostingcontainer = HostingContainer.create_container("New Container")

DataService class
++++++++++++++++++++++++

.. autoclass:: dataservice.models.DataService
    :noindex:

::

  # Create a new DataService
  from dataservice.models import HostingContainer

  # Either Create a new HostingContainer
  hostingcontainer = HostingContainer.create_container("New Container")

  # Or get an existing HostingContainer from the database
  hostingcontainer = HostingContainer.objects.get(id="hostingcontainerid")
  dataservice = hostingcontainer.create_data_service("New DataService")
  

MFile class
++++++++++++++++++++++++

.. autoclass:: dataservice.models.MFile
  :noindex:

::

  # Create a new MFile
  from dataservice.models import DataService

  # First get an existing DataService from the database
  dataservice = DataService.objects.get(id="dataserviceid")

  # Create an Empty Mfile
  mfile = dataservice.create_mfile("New MFile")

  # Or, Create an MFile from some data
  from django.core.files.base import ContentFile
  mfile = dataservice.create_mfile("New MFile", file=ContentFile("some content for the file"))

  # Or, Create an MFile from a file in the POST of a django request object
  mfile = dataservice.create_mfile("New MFile", file=request.POST['fileparam'])

See Django `Request <https://docs.djangoproject.com/en/dev/ref/request-response/>`_ object

Querying
^^^^^^^^^^^^^^

::

  from dataservice.models import MFile

  # Get all MFiles
  mfiles = MFile.objects.all()

  # Get MFiles at a service
  mfiles = MFile.objects.filter(service=somedataservice)
  #or
  mfiles = somedataservice.mfiles_set.all()

  # Search by exact name
  mfiles = MFile.objects.filter(name=="myfile")

  # Search by partial name
  mfiles = MFile.objects.filter(name__contains=="myfile")

  # Search by folder
  mfiles = MFile.objects.filter(folder==somefolder)

  # Search by size
  mfiles = MFile.objects.filter(size__gt==1024)

  # Chaining searches
  mfiles = MFile.objects.filter(folder==somefolder).exclude(name=="myfile")

MFolder class
++++++++++++++++++++++++

.. autoclass:: dataservice.models.MFolder
    :noindex:
    
::

  # Create a new MFolder
  from dataservice.models import DataService

  # First get an existing DataService from the database
  dataservice = DataService.objects.get(id="dataserviceid")

  # Create an MFolder at the root of the service
  mfolder1 = dataservice.create_mfolder("folder1")

  # Create a sub MFolder
  submfolder2 = dataservice.create_mfolder("subfolder1", parent=mfolder1)

  # Create an MFile in a folder
  mfile = dataservice.create_mfile("New MFile", folder=submfolder)

Auth class
++++++++++++++++++++++++

.. autoclass:: dataservice.models.Auth
    :noindex:

DataService Object Model Graph
++++++++++++++++++++++++++++++

.. image:: images/dataservice_dot.png

JobService Models
--------------------

.. automodule:: jobservice.models

.. autoclass:: jobservice.models.TaskDescription
  :noindex:

.. autoclass:: jobservice.models.TaskInput
  :noindex:

.. autoclass:: jobservice.models.TaskOutput
  :noindex:

.. autoclass:: jobservice.models.TaskResult
  :noindex:

.. autoclass:: jobservice.models.Job
  :noindex:

A Job can be created with the following code::

  # Create a new Job
  from dataservice.models import DataService
  from celery.task.sets import subtask
  from celery.task.sets import TaskSet

  # First get an existing MFile from the database
  dataservice = DataService.objects.get(id="dataserviceid")
  mfile = dataservice.mfile_set.get(id=="somemfileid")

  # Create a Job related to the MFile
  job = mfile.create_job("New Job")

  # Define inputs and outputs
  inputs = [mfile.id]
  outputs = []

  # Decide which task to run
  jobtype = "dataservice.tasks.mimefile"

  # Create a celery task
  task = subtask(task=jobtype,args=[inputs,outputs])

  # Add the task to a task set, could create more parallel tasks here
  ts = TaskSet(tasks=[task])
  tsr = ts.apply_async()
  tsr.save()

  # Update the job with the taskset id
  job.taskset_id=tsr.taskset_id
  job.save()

  # Wait to complete
  # .... sleep

  # Get results
  job.tasks()

You can send a tasks to a specific named queue by creating the task liek this::

    # The queue a task goes to is defined by the routing key
    # In a standard MServe service there are 2 queues, normal.# and priority.#
    queue = "priority.%s" % (task_name)
    options = {"routing_key": queue}
    task = subtask(task=task_name, args=[[mfileid], []], options=options)

.. autoclass:: jobservice.models.JobOutput
  :noindex:

JobService Object Model Graph
++++++++++++++++++++++++++++++

.. image:: images/jobservice_dot.png

URLS
----------

.. automodule:: dataservice.urls
.. automodule:: jobservice.urls

Handlers
----------

.. automodule:: dataservice.handlers
.. automodule:: jobservice.handlers

------------------------
Development Environment
------------------------

Assuming you have downloaded the MServe source and extracted into a directory named **mserve**. First install the mserve dependencies::
  
  sudo mserve/scripts/setup-mserve.sh dependencies

Copy the **mserve/scripts/settings_dev.py** file into **mserve/django-mserve/**
  
Edit the **settings_dev.py**

* Set the **MSERVE_HOME** parameter to the directory that the settings.py file is located (DEFAULT=os.getcwd())
* Set the **MSERVE_DATA** to where you want to store MServe files (DEFAULT=/path/to/mserve-test-data)
* Set the **MSERVE_LOG** to the directory where you want to save the development log file (DEFAULT=os.getcwd())
* Set the **DBNAME** to the name of the developement database (DEFAULT=mservedbdev)

Create the dev databases (if not using sqlite)::

 CREATE DATABASE mservedbdev; FLUSH PRIVILEGES;
 CREATE USER 'root'@'%' IDENTIFIED BY 'pass';
 GRANT ALL ON mservedbdev.* TO 'root';

Setup the database::

  python mserve/django-mserve/manage.py syncdb
  python mserve/django-mserve/manage.py migrate dataservice
  python mserve/django-mserve/manage.py migrate jobservice
  python mserve/django-mserve/manage.py migrate celery

Run the development service::

  python mserve/django-mserve/manage.py runserver

Visit `127.0.0.1:8000 <http://127.0.0.1:8000>`_ in your browser, output will be to the console window


Running the FUSE mount daemon
-----------------------------

Run the command::

  sudo python mserve/django-mserve/mservefuse.py /export/mserve

Then browse to::

  ls /export/mserve/<service-customer-auth-id>/

Testing
------------------

There are 3 classes of tests in MServe *django-mserve/dataservice/tests.py*

**ClientTest**
    The Client Tests uses django test client
    `Django Test Client <https://docs.djangoproject.com/en/dev/topics/testing/#module-django.test.client>`_
    It mimics a MServe API user and browser, and its primary function is to test the code in *django-mserve/dataservice/handlers.py* and *django-mserve/dataservice/urls.py*

**ApiTest**
    The Api tests check the internal MServe API, functionality *django-mserve/dataservice/models.py*

**TaskTest**
    This set of tests is to test the running of tasks *django-mserve/dataservice/tasks.py*
    There should be a test for each individual task, and a new test should be added when creating a new task

Test can be run with the command::

  python mserve/django-mserve/manage.py test dataservice


Installing MServe
------------------

MServe has been tested on Ubuntu 10.04-3 LTS, other versions may work but have not been tested

On a fresh 10.04-3 Ubuntu, update and reboot::

  sudo apt-get update
  sudo apt-get -y upgrade
  sudo reboot

Then follow the commands::

  cp mserve/scripts/setup-mserve.sh ~
  cd ~
  ./setup-mserve.sh -a mserve.tar.gz


Building MServe Docs
---------------------

In the docs folder in the MServe checkout run::

 make html

For the full documentation to be build the MServe modules must be importable on the machine doing the build

------------------
Debugging MServe
------------------

Django Shell
------------------

`Django Shell Documentation <https://docs.djangoproject.com/en/dev/ref/django-admin/#shell/>`_

Running the Django Shell::

  python mserve/django-mserve/manage.py shell

Finding an MFile::

  > from dataservice.models import *
  > MFile.objects.filter(id="someid")

Running a task synchronously::

  > from dataservice.tasks import *
  > mimefile([mfileid],[])
  { "mimetype" : "XXXXX" }
  
Running a task asynchronously::

  > from dataservice.tasks import *
  > asyncresult = mimefile.delay([mfileid],[])
  .... wait a second ....
  > asyncresult.result
  { "mimetype" : "XXXXX" }


Where to look for errors
---------------------------

Logs
-------

Development::

  MSERVE_HOME/mserve.log
  MSERVE_HOME/celery{n}.log (where n is the number of the queue)

Live Server::

  /var/log/mserve/mserve.log
  /var/log/mserve/celeryd{n}.log (where n is the number of the queue)
  /var/log/apache/access.log
  /var/log/apache/error.log

Tests being submitted but not running
++++++++++++++++++++++++++++++++++++++

Check the celery tasks are running, by default there should be 5 **normal** queues and 5 **priority** queues plus **celerycam** and **celerybeat**::

 # ps -ef | grep celery
 www-data 24401     1 10:35:27 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q priority_tasks -c 5 -l DEBUG -n priority.mserve
 www-data 24409 24401 00:10:33 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q priority_tasks -c 5 -l DEBUG -n priority.mserve
 www-data 24410 24401 00:10:28 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q priority_tasks -c 5 -l DEBUG -n priority.mserve
 www-data 24411 24401 00:10:31 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q priority_tasks -c 5 -l DEBUG -n priority.mserve
 www-data 24412 24401 00:11:45 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q priority_tasks -c 5 -l DEBUG -n priority.mserve
 www-data 24413 24401 00:10:28 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q priority_tasks -c 5 -l DEBUG -n priority.mserve
 www-data 24424     1 10:40:28 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q normal_tasks -c 5 -l DEBUG -n normal.mserve
 root     24444     1 02:56:19 /usr/bin/python /opt/mserve/manage.py celerycam --detach -f celerycam.log --pidfile=/var/opt/mserve-data/celerycam.pid
 www-data 24447 24424 00:02:41 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q normal_tasks -c 5 -l DEBUG -n normal.mserve
 www-data 24449 24424 00:02:46 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q normal_tasks -c 5 -l DEBUG -n normal.mserve
 www-data 24450 24424 00:02:37 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q normal_tasks -c 5 -l DEBUG -n normal.mserve
 www-data 24451 24424 00:02:54 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q normal_tasks -c 5 -l DEBUG -n normal.mserve
 www-data 24452 24424 00:02:46 /usr/bin/python /opt/mserve/manage.py celeryd -E -Q normal_tasks -c 5 -l DEBUG -n normal.mserve
 root     24467     1 00:00:01 /usr/bin/python /opt/mserve/manage.py celerybeat --detach -f celerybeat.log --pidfile=/var/opt/mserve-data/celerybeat.pid

Tasks not being submitted
++++++++++++++++++++++++++

Check if the task appears in the avaliable tasks list ::

 curl http://mservehost/tasks/

If you are developing your own tasks then make sure they are registered::

 {MSERVE_HOME}/django-mserve/manage.py register_tasks <app-name>