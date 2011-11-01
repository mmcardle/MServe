MServe Metrics
###################

Usage reports come in this format::

    {
        "total": long,
        "nInProgress": int,
        "metric": str,
        "reports": int,
        "rate": long,
        "rateTime": date,
        "rateCumulative": long,
        "squares": long
    }

For example::

    {
        "total": 1004263202600.64,
        "nInProgress": 1,
        "metric": "http://mserve/disc",
        "reports": 2,
        "rate": 578730.0,
        "rateTime": "2011-10-31 11:29:47",
        "rateCumulative": 502305089855.48,
        "squares": 2.52310403294721e+23
    }

This usage report concerns the metric "http://mserve/disc" which is the amount of data stored on the file system over time.

This is an aggregated report, made up of 2 individual **reports**, one of which is still in progress, shown as **nInProgress**.
In practice, this means there have been two files created, one of which has been deleted.

The current rate of consumption, shown as **rate** is 578730.0,

The last time the rate changed, shown as **rateTime**, is "2011-10-31 11:29:47"

The total recorded before the last time the rate changed, shown as **total**, is 1004263202600.64,

The cumulative total since the last time the rate changed, shown as **rateCumulative**, is 502305089855.48.

The **squares** value, is the sum of the squares of each of the reports, for working out variance and standard deviation.


http://mserve/container
=========================

* **Description** : Number of Containers
* **Unit** : Containers

This is the rate of consumption of hosting containers that currently exist in the MServe deployment.
This rate will always be *1* when usage is requested from the hosting container itself.

http://mserve/service
======================

* **Description** : Number of Services
* **Unit** : Services

This is the rate of consumption of services that currently exist in the MServe deployment.
If the usage is requested at the top level this is the number of services that currently exist under all hosting containers.
If the usage is requested at a hosting container level this will always be the number of services under the specified hosting container.
This will always be *1* when usage is requested from the service itself.

http://mserve/file
======================

* **Description** : Number of Files
* **Unit** : Files

This is the rate of consumption of files that currently exist in the MServe deployment.
If the usage is requested at the top level this is the number of files that currently exist under all services.
If the usage is requested at a service level this will always be the number of files under the specified hosting service.
This will always be *1* when usage is requested from the mfile itself.

http://mserve/backupfile
=========================

* **Description** : Number of Backup Files
* **Unit** : Backup Files

This is the rate of consumption of backup files that currently exist in the MServe deployment.
If the usage is requested at the top level this is the number of backup files that currently exist under all services.
If the usage is requested at a service level this will always be the number of backup files under the specified hosting service.

http://mserve/disc
======================

* **Description** : The amount of data stored
* **Unit** : bytes

This metric records the amount of data being stored as files directly uploaded by a user, and of backup files.

In the future is will include data produced as the result of running jobs.

http://mserve/disc_space
=========================

* **Description** : How much data is currently being stored on disc
* **Unit** : bytes

**DEPRECATED** - Use the rate value of http://mserve/disc for how much data is being stored

http://mserve/responsetime
==========================

* **Description** : Response time to serve a file
* **Unit** : seconds

The time taken from when a file is requested, until when it is available to start download.
This value will vary dependant upon the state, location and type of file.

If the file is currupt, a backup copy (if it exists) needs to be retrieved which may be on a slower medium.

http://mserve/ingest
======================

* **Description** : Bytes ingested into the system
* **Unit** : bytes

This records the number of bytes that have been uploaded to the service.

http://mserve/access
======================

* **Description** : Bytes ingested into the system
* **Unit** : bytes

This records the number of bytes that have been downloaded from the service. It does not include static files (css, javascript, static images)

http://mserve/corruption
=========================

* **Description** : Bytes corrupted on the system
* **Unit** : bytes

This records the number of bytes that have needed to have been replaced from a backup copy, due to an error being flagged when calculating a checksum.

http://mserve/dataloss
======================

* **Description** : Bytes lost in the system
* **Unit** : bytes

This records the number of bytes that have been lost due to corruption, where no backup copy could be located, or all backups where corrupt.

http://mserve/job
======================

* **Description** : Number of Jobs
* **Unit** : Jobs

This is the rate of consumption of jobs that currently exist in the MServe deployment.

Jobs are created on ingest, access, update and periodically. Jobs contain a number of tasks (see below)

If the usage is requested at the top level this is the number of jobs that currently exist under all services.
If the usage is requested at a service level this will always be the number of jobs under the specified hosting service.
This will always be *1* when usage is requested from the job itself.

http://mserve/task
======================

* **Description** : Number of Tasks
* **Unit** : Tasks

This is the rate of consumption of tasks that currently exist in the MServe deployment.

Tasks are always created as part of a Job (see above)

http://mserve/jobruntime
=========================

* **Description** : Job Runtime
* **Unit** : Seconds

This is a report on the runtime of each task in seconds

**It should really be named http://mserve/taskruntime and will renamed in a future release**
