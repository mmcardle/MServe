MServe Overview
###############

The problem MServe is trying to solve
*************************************

You require a web interface to a web service/application that needs to do one or all of the following

* Allow users to upload data to the service
* Allow users access to predefined datasets
* Process that data at particular times

 * on upload
 * on demand from user
 * scheduled

* Allow users to configure how data is processed
* Allow users to view/download the results
* Allow different users access to different levels of quality of service
* Allow different standard interfaces to the service

What the characteristics of the service should be
-------------------------------------------------

* Distributed - The system should be able to run across distinct nodes on one or more machines
* Scalable - Allow extra compute capacity to be added to the system on demand
* Performance - Under load the system should remain responsive to the end user
* Manageable - The system should be controllable by the system admin to set up different quality of service
* Accountable - The system should record usage of compute resources

How this should NOT be done
------------------------------

Spawning processes in the web server/framework and recording the process id (say in a database), this kills performance, essentially don't use a database to pass messages (use Messaging, see below)

How can this be achieved properly
---------------------------------

* Messaging - Passing of messages in a distributed system means the user experience should not be affected by computationally intensive tasks
* Queuing - Queues enable the front end to respond to the client, while the back end processed this queue when ready
* Scheduling - Processing of data when there is free capacity
* Monitoring - The system monitors processes to allow decisions to be taken on how data is processed in the future

What technology is used in MServe
-----------------------------------

* Web UI - jquery  (http://jquery.com/) and jqueryui (http://jqueryui.com/)
* Web Server - Apache2 (http://httpd.apache.org/)
* Web framework - Django (https://www.djangoproject.com/)
* Task Queuing/ Job Scheduler - Celery (http://celeryproject.org/)
* Message Broker - RabbitMQ (http://www.rabbitmq.com/)

Why was that technology choosen
-----------------------------------

All the technology used was choosen with a simple concept in mind, saving development time by using pre-existing software that is allready known to work well together.Conforming as much as possible to the DRY principle (http://c2.com/cgi/wiki?DontRepeatYourself)
For example: You should not be rewriting html forms for login, change password, update details, registration and all other user management facilities.The same applies to forms for your own database models, this is where django steps in and this is where it excels.

* JQuery - A great web framework, plugin based and a great community of support. Client side templating, form handling, ajax requests.
* JQuery UI - works nicely with JQuery giving a consistent look and feel to the system. Its widget provide excellent use of your browser real-estate.
* Apache2 - We found apache2 to have best balance of performance for upload and download when proxying to a web backend (Django in this case)
* Django - For shear speed of development django is great, its Object Relational Mapper saves endless hours of database debugging. Other features include built-in handling of file uploads, static files, and extensible server side templating. A simple well defined URL dispatcher allows you to build a Restful URL structure for your site.	Add to that plugins for OpenID, OAuth, 4Stor, Sparql and more (https://code.djangoproject.com/wiki/DjangoResources).	Also has great links to celery using django-celery
* Celery - Started off as a Django plugin, now can be used standalone, an obvious choice for a task manager when using django. Provides scaleability and  works in a distributed environment.
* RabbitMQ - An exellent open source implementations of the AMQP protocol, "Messaging that just works" says it all. Language independant means producers and consumers  of messages can use different implementations, http://www.rabbitmq.com/devtools.html. Has tools for Java, C#, Python, Ruby. .NET, erlang, Haskel, C/C++, and can be deployed into Amazon EC2

How the user accesses their data
-----------------------------------

* HTML/Web interface: this is the simplest way of getting data into the service, ajax file uploads and http downloads allow an interactive UI
* Webdav: A standard way of accessing data on the web, multiple clients on all major operating systems means data should be assessible from many locations.

Controlling the usage of users accessing their data
---------------------------------------------------

The first step is bandwidth throttling, we can dynamically control access to the system and restrict the rate of downloads. This is achieived using Apache2 mod_bw and dynamic url rewriting. Secondly we can control the time users are allowed to access data, with each dataset we can restrict access with a start time and end time, and can create temporary access to datasets each with their own independant start time, end time, and bandwidth capacities.

So how can we scale even further
--------------------------------

Next step is to allow the deployment into the 'cloud', so a new worker node could be deployed into a virtual environment and connect to our broker to start processing jobs, this would allow scalability on demand.

How can this be achieved
------------------------



Further Reading
---------------

* http://celeryproject.org/
* http://django-celery.readthedocs.org/en/latest/getting-started/first-steps-with-django.html
* http://blogs.digitar.com/jjww/2009/01/rabbits-and-warrens/
* http://ask.github.com/celery/getting-started/introduction.html
* http://old.nabble.com/Ubuntu-%2B-RabbitMQ-2.4.0-EC2-AMI-td31280970.html