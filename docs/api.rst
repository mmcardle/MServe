
MServe REST API
=======================

Container URLs
+++++++++++++++++

Root Container URL
------------------
::

 /containers/



GET ``Requires Staff Login`` - Returns a list of containers  ::

 [
     {
        "dataservice_set": [],
        "name": "Container",
        "thumbs": [],
        "default_profile": null,
        "id": "AUdhFvIhwVqHJpfYbH1F4YXy17HAZUYhEYdRVrNa4",
        "reportnum": 14
     }
 ]

POST - Creates a new container

* ``name`` (*str*) : Name of the the container **Required**

PUT - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

Container Instance URL 
----------------------

::

 /containers/<container-id>/

GET - Returns the container::

     {
        "dataservice_set": [],
        "name": "Container",
        "thumbs": [],
        "default_profile": null,
        "id": "AUdhFvIhwVqHJpfYbH1F4YXy17HAZUYhEYdRVrNa4",
        "reportnum": 14
     }

PUT - updates the container with id **<containerid>**

* ``name`` : str : New name for the the container **Required**

POST - **405 - Method Not Allowed**

DELETE - Deletes the container with id **<containerid>**

Container Properties URL
-------------------------
::

 /<container-id>/properties/

GET - Returns the properties for the specified container::

    [
        {
            "property": "accessspeed",
            "values": {
                "type": "enum",
                "choices": [
                    "100",
                    "1000",
                    "10000",
                    "100000",
                    "1000000",
                    "100000000",
                    "unlimited"
                ]
            },
            "id": 1,
            "value": "unlimited"
        }
    ]

PUT - updates the property **<property>** of the container **<containerid>**

* ``property`` (*str*) : The name of the property **Required**
* ``value`` (*str*) : The new value for the the property **Required**

POST - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

Container Usage URL
-------------------------
::

 /<container-id>/usages/

GET - Returns the usage for the specified container::

    {
        "usages": [
            {
                "squares": 0.0,
                "nInProgress": 1,
                "metric": "http://mserve/container",
                "reports": 1,
                "rate": 1.0,
                "rateTime": "2011-11-16 09:05:42",
                "rateCumulative": 0.0,
                "total": 0.0
            }
        ],
        "reportnum": 62
    }

PUT - **405 - Method Not Allowed**

POST - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

Container Usage Summary URL
----------------------------
::

 /<container-id>/usagesummary/

GET - Returns the usage for the specified container::

    {
        "usages": [
            {
                "min": 0.0,
                "max": 0.0,
                "sum": 0.0,
                "n": 2,
                "stddev": 0.0,
                "variance": 0.0,
                "avg": 0.0,
                "metric": "http://mserve/service"
            },
            {
                "min": 1534.0,
                "max": 776408.0,
                "sum": 1356672.0,
                "n": 3,
                "stddev": 328745.347238051,
                "variance": 108073503330.667,
                "avg": 452224.0,
                "metric": "http://mserve/disc_space"
            },
            {
                "min": 1534.0,
                "max": 776408.0,
                "sum": 1356672.0,
                "n": 3,
                "stddev": 328745.347238051,
                "variance": 108073503330.667,
                "avg": 452224.0,
                "metric": "http://mserve/ingest"
            }
        ]
    }

PUT - **405 - Method Not Allowed**

POST - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

Container Authority URL
-------------------------
::

 /<container-id>/auths/

GET - Returns the authoritys for the specified container::

    [
        {
            "thumburl": "/mservemedia/images/package-x-generic.png",
            "methods": [],
            "roles": [
                "containeradmin"
            ],
            "basename": "Container",
            "auth_set": [],
            "urls": {
                "auths": [
                    "GET",
                    "PUT",
                    "POST",
                    "DELETE"
                ],
                "services": [
                    "GET",
                    "POST"
                ],
                "usages": [
                    "GET"
                ],
                "properties": [
                    "GET",
                    "PUT"
                ]
            },
            "authname": "full",
            "id": "5vCDBKE8ae0BNtvTaaa1m27CEbyXFOul0hjy2bAbRU4"
        }
    ]

PUT - **405 - Method Not Allowed**

POST - Creates a new Authority for this container

* ``name`` (*str*) : The name for the new authority **Required**
* ``roles`` (*str*) : A comma separated list of role names for the new authority **Required**

DELETE - **405 - Method Not Allowed**

Container Service URL
-------------------------
::

 /<container-id>/services/

GET - Returns the services in the specified container::

    [
        {
            "subservices_url": "/services/ZtdoKyUh27lmkG0gnpQKlUhLZw2Ae27GDCTQbch4MA/subservices/",
            "name": "Service",
            "folder_structure": {
                "data": {
                    "data": "Service",
                    "attr": {
                        "id": "ZtdoKyUh27lmkG0gnpQKlUhLZw2Ae27GDCTQbch4MA",
                        "class": "service"
                    },
                    "children": [
                        {
                            "data": "folder1",
                            "attr": {
                                "id": "VRegf1RpEAZiFP2EOnd6iQRkxfbEPl7NIU4fT8A4"
                            },
                            "children": []
                        },
                    ]
                }
            },
            "mfile_set": [
                "..."
            ],
            "priority": false,
            "thumbs": [
                "/mservethumbs/2011/11/16/MyUU1BItYBMWCP8Q437cytjR06mIDF9RbDQoSPL5WcE/tmpN80Kyq.png",
                "/mservemedia/images/package-x-generic.png",
                "/mservemedia/images/package-x-generic.png",
                "/mservemedia/images/package-x-generic.png"
            ],
            "starttime": "2011-11-16 09:05:44",
            "mfolder_set": [
                {
                    "name": "folder1",
                    "parent": null,
                    "id": "VRegf1RpEAZiFP2EOnd6iQRkxfbEPl7NIU4fT8A4"
                },
                {
                    "name": "folder1",
                    "parent": null,
                    "id": "qs5iSmoRzCNY9Ltmn4daoCwE48XifgreSVlsIxIeFY"
                },
                {
                    "name": "folder1dup",
                    "parent": null,
                    "id": "w65EDcnQcePHkXNLbGFZUR5JaS7q6VPrz0Pot3Yqg"
                }
            ],
            "endtime": "2011-11-16 10:05:44",
            "id": "ZtdoKyUh27lmkG0gnpQKlUhLZw2Ae27GDCTQbch4MA",
            "reportnum": 21
        },
        {
            "subservices_url": "/services/lpEBSX3Ip8W0pGvRGn1BHtJ5AEwnCFjcQtXKsQLNt8/subservices/",
            "name": "Service 2",
            "..."
        }
    ]

PUT - **405 - Method Not Allowed**

POST - Creates a new Service in this container

* ``name`` (*str*) : The name for the new service **Required**
* ``starttime`` (*str*) : The start date/time for the service in  YYYY-MM-DD HH:MM[:ss[.uuuuuu]] format.
* ``endtime`` (*str*) : The end date/time for the service in YYYY-MM-DD HH:MM[:ss[.uuuuuu]] format.

DELETE - **405 - Method Not Allowed**

Container Sub Service URL
-------------------------
::

 /<container-id>/subservices/

GET - Returns the subservices in the specified container::

    [
        {
            "subservices_url": "/services/ZtdoKyUh27lmkG0gnpQKlUhLZw2Ae27GDCTQbch4MA/subservices/",
            "name": "Service",
            "folder_structure": {
                "data": {
                    "data": "Service",
                    "attr": {
                        "id": "ZtdoKyUh27lmkG0gnpQKlUhLZw2Ae27GDCTQbch4MA",
                        "class": "service"
                    },
                    "children": [
                        {
                            "data": "folder1",
                            "attr": {
                                "id": "VRegf1RpEAZiFP2EOnd6iQRkxfbEPl7NIU4fT8A4"
                            },
                            "children": []
                        },
                    ]
                }
            },
            "..."
    ]

PUT - **405 - Method Not Allowed**

POST - Creates a new Service in this container

* ``name`` (*str*) : The name for the new service **Required**
* ``serviceid`` (*str*) : The serviceid of the parent service **Required**
* ``starttime`` (*date*) : The start date/time for the service in  YYYY-MM-DD HH:MM[:ss[.uuuuuu]] format.
* ``endtime`` (*date*) : The end date/time for the service in YYYY-MM-DD HH:MM[:ss[.uuuuuu]] format.

DELETE - **405 - Method Not Allowed**

Service URLs
+++++++++++++++++

Root Service URL
------------------
::

 /services/

GET - **Not Allowed**

PUT - **405 - Method Not Allowed**

POST - Creates a new service

* ``name`` (*str*) : The name for the new service **Required**
* ``containerid`` (*str*) : The ID of the container in which to create this serivice **Required**
* ``starttime`` (*date*) : The start date/time for the service in  YYYY-MM-DD HH:MM[:ss[.uuuuuu]] format.
* ``endtime`` (*date*) : The end date/time for the service in YYYY-MM-DD HH:MM[:ss[.uuuuuu]] format.

DELETE - **405 - Method Not Allowed**

Service Properties URL
-------------------------
::

 /<service-id>/properties/

GET - Returns the properties for the specified service::

    [
        {
            "property": "accessspeed",
            "values": {
                "type": "enum",
                "choices": [
                    "100",
                    "1000",
                    "10000",
                    "100000",
                    "1000000",
                    "100000000",
                    "unlimited"
                ]
            },
            "id": 1,
            "value": "unlimited"
        }
    ]

PUT - updates the property **<property>** of the service **<service-id>**

* ``property`` (*str*) : The name of the property **Required**
* ``value`` (*str*) : The new value for the the property **Required**

POST - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

Service Usage URL
-------------------------
::

 /<service-id>/usages/

GET - Returns the usage for the specified service::

    {
        "usages": [
            {
                "squares": 0.0,
                "nInProgress": 1,
                "metric": "http://mserve/service",
                "reports": 1,
                "rate": 1.0,
                "rateTime": "2011-11-16 09:05:42",
                "rateCumulative": 0.0,
                "total": 0.0
            }
        ],
        "reportnum": 62
    }

PUT - **405 - Method Not Allowed**

POST - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

Service Usage Summary URL
----------------------------
::

 /<service-id>/usagesummary/

GET - Returns the usage for the specified service::

    {
        "usages": [
            {
                "min": 0.0,
                "max": 0.0,
                "sum": 0.0,
                "n": 2,
                "stddev": 0.0,
                "variance": 0.0,
                "avg": 0.0,
                "metric": "http://mserve/service"
            },
            {
                "min": 1534.0,
                "max": 776408.0,
                "sum": 1356672.0,
                "n": 3,
                "stddev": 328745.347238051,
                "variance": 108073503330.667,
                "avg": 452224.0,
                "metric": "http://mserve/disc_space"
            },
            {
                "min": 1534.0,
                "max": 776408.0,
                "sum": 1356672.0,
                "n": 3,
                "stddev": 328745.347238051,
                "variance": 108073503330.667,
                "avg": 452224.0,
                "metric": "http://mserve/ingest"
            }
        ]
    }

PUT - **405 - Method Not Allowed**

POST - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

Service Authority URL
-------------------------
::

 /<service-id>/auths/

GET - Returns the authoritys for the specified service::

    [
        {
            "thumburl": "/mservemedia/images/text-x-generic.png",
            "methods": [],
            "roles": [
                "serviceadmin"
            ],
            "basename": "Service",
            "auth_set": [],
            "urls": {
                "usages": [
                    "GET"
                ],
                "jobs": [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE"
                ],
                "auths": [
                    "GET",
                    "PUT",
                    "POST",
                    "DELETE"
                ],
                "mfiles": [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE"
                ],
                "profiles": [
                    "GET"
                ],
                "base": [
                    "GET"
                ],
                "mfolders": [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE"
                ],
                "properties": [
                    "GET",
                    "PUT"
                ]
            },
            "authname": "full",
            "id": "pbMK6cytEco7jPi3ymdRCpwYRTKSbt9bgkpmWF78"
        },
        {
            "thumburl": "/mservemedia/images/text-x-generic.png",
            "methods": [],
            "roles": [
                "servicecustomer"
            ],
            "basename": "Service",
            "auth_set": [],
            "urls": {
                "usages": [
                    "GET"
                ],
                "jobs": [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE"
                ],
                "auths": [
                    "GET",
                    "PUT",
                    "POST",
                    "DELETE"
                ],
                "mfiles": [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE"
                ],
                "base": [
                    "GET"
                ],
                "mfolders": [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE"
                ],
                "properties": [
                    "GET"
                ]
            },
            "authname": "customer",
            "id": "aFDbGmf5uHB4SZfQmohQI6gmpzhFPHIRF2mip3ZQ"
        }
    ]

PUT - **405 - Method Not Allowed**

POST - Creates a new Authority for this service

* ``name`` (*str*) : The name for the new authority **Required**
* ``roles`` (*str*) : A comma separated list of role names for the new authority **Required**

DELETE - **405 - Method Not Allowed**

Service MFiles URL
-------------------------
::

 /<service-id>/mfiles/

GET - Returns the MFiles stored in the service::

    [
        {
            "mimetype": "text/html",
            "updated": "2011-11-16 12:57:56",
            "thumburl": "/mservemedia/images/text-x-generic.png",
            "thumb": "",
            "created": "2011-11-16 12:56:48",
            "checksum": "36f748ec655dbf49e755f8cc2c45beb7",
            "posterurl": "/mservemedia/images/text-x-generic.png",
            "name": "file.html",
            "proxyurl": "",
            "proxy": "",
            "file": "2011/11/16/eAHFsWne14LYISNUsaFGaBbIBPLrJuq5xQ8ZRKzQ/manage.py",
            "poster": "",
            "reportnum": 28,
            "id": "gL6flsQ82wCCuL6vGXWeeLSzcWMhAC0qVUKAYDc8E",
            "size": 1534
        }
    ]

PUT - **405 - Method Not Allowed**

POST - Creates a new MFile at this service

* ``name`` (*str*) : The name for the new file **Required**
* ``file`` (*file*) : The file to store

DELETE - **405 - Method Not Allowed**

Service MFolders URL
-------------------------
::

 /<service-id>/mfolders/

GET - Returns the MFolders stored in the service::

    [
        {
            "name": "folder1",
            "parent": null,
            "id": "VRegf1RpEAZiFP2EOnd6iQRkxfbEPl7NIU4fT8A4"
        },
        {
            "name": "folder2",
            "parent": null,
            "id": "qs5iSmoRzCNY9Ltmn4daoCwE48XifgreSVlsIxIeFY"
        },
        {
            "name": "folder3",
            "parent": null,
            "id": "w65EDcnQcePHkXNLbGFZUR5JaS7q6VPrz0Pot3Yqg"
        }
    ]

PUT - **405 - Method Not Allowed**

POST - ** Not Implemented Yet** - Folders can be created/ and updated via the WEBDAV interface

DELETE - **405 - Method Not Allowed**

Service Sub Service URL
-------------------------
::

 /<service-id>/subservices/

GET - Returns the subservices in the specified service::

    [
        {
            "subservices_url": "/services/ZtdoKyUh27lmkG0gnpQKlUhLZw2Ae27GDCTQbch4MA/subservices/",
            "name": "Service",
            "folder_structure": {
                "data": {
                    "data": "Service",
                    "attr": {
                        "id": "ZtdoKyUh27lmkG0gnpQKlUhLZw2Ae27GDCTQbch4MA",
                        "class": "service"
                    },
                    "children": [
                        {
                            "data": "folder1",
                            "attr": {
                                "id": "VRegf1RpEAZiFP2EOnd6iQRkxfbEPl7NIU4fT8A4"
                            },
                            "children": []
                        },
                    ]
                }
            },
            "..."
    ]

PUT - **405 - Method Not Allowed**

POST - Creates a new Service under this service

* ``name`` (*str*) : The name for the new service **Required**
* ``serviceid`` (*str*) : The serviceid of the parent service **Required**
* ``starttime`` (*date*) : The start date/time for the service in  YYYY-MM-DD HH:MM[:ss[.uuuuuu]] format.
* ``endtime`` (*date*) : The end date/time for the service in YYYY-MM-DD HH:MM[:ss[.uuuuuu]] format.

DELETE - **405 - Method Not Allowed**

Service Profiles URL
-------------------------
::

 /<service-id>/profiles/

GET - Returns the profiles in the specified service::

    [
        {
            "id": 1,
            "name": "default",
            "workflows": [
                {
                    "tasksets": [],
                    "name": "access",
                    "id": 1
                },
                {
                    "tasksets": [
                        {
                            "id": 1,
                            "tasks": [
                                {
                                    "args": "{}",
                                    "condition": "",
                                    "name": "A",
                                    "task_name": "mimefile",
                                    "id": 1
                                }
                            ],
                            "name": "taskset1",
                            "order": 0
                        },
                        {
                            "id": 2,
                            "tasks": [
                                {
                                    "args": "{}",
                                    "condition": "",
                                    "name": "B",
                                    "task_name": "md5file",
                                    "id": 2
                                },
                                {
                                    "args": "{'width': 210, 'height': 128}",
                                    "condition": "mfile.mimetype.startswith('image')",
                                    "name": "C",
                                    "task_name": "thumbimage",
                                    "id": 3
                                },
                                {
                                    "args": "{'width': 420, 'height': 256}",
                                    "condition": "mfile.mimetype.startswith('image')",
                                    "name": "D",
                                    "task_name": "posterimage",
                                    "id": 4
                                },
                                {
                                    "args": "{}",
                                    "condition": "",
                                    "name": "E",
                                    "task_name": "dataservice.tasks.backup_mfile",
                                    "id": 5
                                }
                            ],
                            "name": "taskset2",
                            "order": 1
                        }
                    ],
                    "name": "ingest",
                    "id": 2
                },
                {
                    "tasksets": [],
                    "name": "periodic",
                    "id": 3
                },
                {
                    "tasksets": [
                        {
                            "id": 3,
                            "tasks": [
                                {
                                    "args": "{}",
                                    "condition": "",
                                    "name": "A",
                                    "task_name": "mimefile",
                                    "id": 6
                                }
                            ],
                            "name": "taskset1",
                            "order": 0
                        },
                        {
                            "id": 4,
                            "tasks": [],
                            "name": "taskset2",
                            "order": 1
                        }
                    ],
                    "name": "update",
                    "id": 4
                }
            ]
        },
        {
            "id": 2,
            "name": "transcode",
            "workflows": [
                {
                    "tasksets": [],
                    "name": "access",
                    "id": 5
                },
                {
                    "tasksets": [],
                    "name": "ingest",
                    "id": 6
                },
                {
                    "tasksets": [],
                    "name": "periodic",
                    "id": 7
                },
                {
                    "tasksets": [],
                    "name": "update",
                    "id": 8
                }

            ]
        }
    ]

PUT - **405 - Method Not Allowed**

POST - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

Service Profile TaskSets URL
----------------------------
::

 /<service-id>/profiles/<profile-id>/tasksets/

GET - Returns the tasksets in the specified profile <profile-id>::

    [
        {
            "id": 3,
            "tasks": [
                {
                    "args": "{}",
                    "condition": "",
                    "name": "A",
                    "task_name": "mimefile",
                    "id": 6
                }
            ],
            "name": "taskset1",
            "order": 0
        },
        {
            "id": 2,
            "tasks": [
                {
                    "args": "{}",
                    "condition": "",
                    "name": "B",
                    "task_name": "md5file",
                    "id": 2
                },
                {
                    "args": "{'width': 210, 'height': 128}",
                    "condition": "mfile.mimetype.startswith('image')",
                    "name": "C",
                    "task_name": "thumbimage",
                    "id": 3
                },
                {
                    "args": "{'width': 420, 'height': 256}",
                    "condition": "mfile.mimetype.startswith('image')",
                    "name": "D",
                    "task_name": "posterimage",
                    "id": 4
                },
                {
                    "args": "{}",
                    "condition": "",
                    "name": "E",
                    "task_name": "dataservice.tasks.backup_mfile",
                    "id": 5
                }
            ],
            "name": "taskset2",
            "order": 1
        },
    ]
    
PUT - **405 - Method Not Allowed**

POST - **405 - Method Not Allowed**

* ``name`` (*str*) : The name for the taskset **Required**
* ``workflow`` (*str*) : The id of the workflow to add the taskset to **Required**
* ``order`` (*str*) : The ordering of the taskset **Required**

DELETE - **405 - Method Not Allowed**


Service Profile TaskSet URL
----------------------------
::

 /<service-id>/profiles/<profile-id>/tasksets/<taskset-id>/

GET - Returns the taskset <taskset-id> in the specified profile <profile-id>::

    {
        "id": 1,
        "tasks": [
            {
                "args": "{}",
                "condition": "",
                "name": "A",
                "task_name": "mimefile",
                "id": 1
            }
        ],
        "name": "taskset1",
        "order": 0
    }

PUT - Updates the taskset

* ``name`` (*str*) : The name for the taskset **Required**
* ``workflow`` (*str*) : The id of the workflow the taskset belongs to **Required**
* ``order`` (*str*) : The ordering of the taskset **Required**

POST - **405 - Method Not Allowed**

DELETE - Deletes the taskset

Service Profile Tasks URL
----------------------------
::

 /<service-id>/profiles/<profile-id>/tasks/

GET - Returns the tasks in the specified profile <profile-id>::

    [
        {
            "args": "{}",
            "condition": "",
            "name": "A",
            "task_name": "mimefile",
            "id": 1
        },
        {
            "args": "{}",
            "condition": "",
            "name": "B",
            "task_name": "md5file",
            "id": 2
        },
        {
            "args": "{'width': 210, 'height': 128}",
            "condition": "mfile.mimetype.startswith('image')",
            "name": "C",
            "task_name": "thumbimage",
            "id": 3
        },
        {
            "args": "{'width': 420, 'height': 256}",
            "condition": "mfile.mimetype.startswith('image')",
            "name": "D",
            "task_name": "posterimage",
            "id": 4
        },
        {
            "args": "{}",
            "condition": "",
            "name": "E",
            "task_name": "dataservice.tasks.backup_mfile",
            "id": 5
        },
        {
            "args": "{}",
            "condition": "",
            "name": "A",
            "task_name": "mimefile",
            "id": 6
        },
        {
            "args": "{}",
            "condition": "",
            "name": "B",
            "task_name": "md5file",
            "id": 7
        },
        {
            "args": "{'width': 210, 'height': 128}",
            "condition": "mfile.mimetype.startswith('image')",
            "name": "C",
            "task_name": "thumbimage",
            "id": 8
        },
        {
            "args": "{'width': 420, 'height': 256}",
            "condition": "mfile.mimetype.startswith('image')",
            "name": "D",
            "task_name": "posterimage",
            "id": 9
        }
    ]

PUT - **405 - Method Not Allowed**

POST - Creats a new Task

* ``name`` (*str*) : The descriptive name for the tasks **Required**
* ``task_name`` (*str*) : The name of the task to run (ie thumbimage) **Required**
* ``taskset`` (*str*) : The id of the taskset **Required**
* ``condition`` (*str*) : A condition that the task must satisfy to run in the context of the mfile passed to it (ie mfile.name.endswith(".dat"))
* ``args`` (*str*) : A JSON encoded list of arguments

DELETE - **405 - Method Not Allowed**


Service Profile Task URL
----------------------------
::

 /<service-id>/profiles/<profile-id>/tasksets/<task-id>/

GET - Returns the task <task-id> in the specified profile <profile-id>::

    {
        "args": "{}",
        "condition": "",
        "name": "A",
        "task_name": "mimefile",
        "id": 1
    }

PUT - Updates the task

* ``name`` (*str*) : The desciptive name for the task **Required**
* ``task_name`` (*str*) : The name of task to run **Required**
* ``taskset`` (*str*) : The id of the taskset **Required**
* ``condition`` (*str*) : A condition that the task must satisfy to run in the context of the mfile passed to it (ie mfile.name.endswith(".dat"))
* ``args`` (*str*) : A JSON encoded list of arguments


POST - **405 - Method Not Allowed**

DELETE - Deletes the task

MFile URLs
+++++++++++++++++

Root MFile URL
------------------
::

 /mfiles/

GET **405 - Method Not Allowed**

POST - Creates a new MFile

* ``name`` (*str*) : The name for the new file **Required**
* ``file`` (*file*) : The file to store
* ``serviceid`` (*str*) : The id of the service at which to create the MFile

PUT - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

MFiles URL
------------------
::

 /mfiles/<mfile-id>/

GET gets info on the specified MFile <mfile-id>::

    {
        "mimetype": "image/jpeg",
        "updated": "2011-11-16 12:57:57",
        "thumburl": "/mservemedia/images/image-x-generic.png",
        "thumb": "",
        "created": "2011-11-16 09:47:26",
        "checksum": "d9bf0bdc061b74c4b731cb68d5f5cb61",
        "posterurl": "/mservethumbs/2011/11/16/daKS9JpMcTZNNwgBP4XUk0038zX42XIrGfUn8U9EQGg/tmpxy1pf8.png",
        "name": "IMAG0361.jpg",
        "proxyurl": "",
        "proxy": "",
        "file": "2011/11/16/z2cEa1PEG5ilrzaWXs9cHsZvAe3RmV6RLF7ujDTOMA/IMAG0361.jpg",
        "poster": "2011/11/16/daKS9JpMcTZNNwgBP4XUk0038zX42XIrGfUn8U9EQGg/tmpxy1pf8.png",
        "reportnum": 1,
        "id": "VFw8tQ2tHEdSvTBbSnNvoPO41Yti4CrFlg01re3s8",
        "size": 578730
    }

POST - Update the MFile stored with this file

* ``name`` (*str*) : The name for the new file **Required**
* ``file`` (*file*) : The file to store

PUT - Updates the MFile stored with this file **Not Implemented**

``Use POST to updated an MFile file or use the WEBDAV interface``

DELETE - Deletes the MFile

MFiles Thumb URL
------------------
::

 /mfiles/<mfile-id>/thumb/

GET - **405 - Method Not Allowed**

POST - Update the MFile thumbnail with this file

* ``thumb`` (*file*) : The thumb file to store

PUT - Updates the MFile stored with this file **Not Implemented**

``Use POST to updated an MFile thumb ``

DELETE - **405 - Method Not Allowed**

MFiles Poster URL
------------------
::

 /mfiles/<mfile-id>/poster/

GET - **405 - Method Not Allowed**

POST - Update the MFile poster with this file

* ``thumb`` (*file*) : The poster file to store

PUT - Updates the MFile poster with this file **Not Implemented**

``Use POST to updated an MFile poster ``

DELETE - **405 - Method Not Allowed**

MFiles Proxy URL
------------------
::

 /mfiles/<mfile-id>/proxy/

GET - **405 - Method Not Allowed**

POST - Update the MFile proxy with this file

* ``thumb`` (*file*) : The proxy file to store

PUT - Updates the MFile proxy with this file **Not Implemented**

``Use POST to updated an MFile proxy``

DELETE - **405 - Method Not Allowed**

MFile Usage URL
-------------------------
::

 /<mfile-id>/usages/

GET - Returns the usage for the specified mfile::

    {
        "usages": [
            {
                "squares": 627231180.369948,
                "nInProgress": 1,
                "metric": "http://mserve/file",
                "reports": 1,
                "rate": 1.0,
                "rateTime": "2011-11-16 16:44:50",
                "rateCumulative": 25044.583853,
                "total": 0.0
            },
            {
                "squares": 2.10079068025208e+20,
                "nInProgress": 1,
                "metric": "http://mserve/disc",
                "reports": 1,
                "rate": 578730.0,
                "rateTime": "2011-11-16 16:44:50",
                "rateCumulative": 14494104595.497,
                "total": 0.0
            },
            {
                "squares": 334928412900.0,
                "nInProgress": 0,
                "metric": "http://mserve/disc_space",
                "reports": 1,
                "rate": 0.0,
                "rateTime": "2011-11-16 09:47:26",
                "rateCumulative": 0.0,
                "total": 578730.0
            },
            {
                "squares": 334928412900.0,
                "nInProgress": 0,
                "metric": "http://mserve/ingest",
                "reports": 1,
                "rate": 0.0,
                "rateTime": "2011-11-16 09:47:27",
                "rateCumulative": 0.0,
                "total": 578730.0
            }
        ],
        "reportnum": 1
    }

PUT - **405 - Method Not Allowed**

POST - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

MFile Usage Summary URL
----------------------------
::

 /<mfile-id>/usagesummary/

GET - Returns the usage for the specified mfile::

    {
        "usages": [
            {
                "min": 0.0,
                "max": 0.0,
                "sum": 0.0,
                "n": 1,
                "stddev": 0.0,
                "variance": 0.0,
                "avg": 0.0,
                "metric": "http://mserve/file"
            },
            {
                "min": 0.0,
                "max": 0.0,
                "sum": 0.0,
                "n": 1,
                "stddev": 0.0,
                "variance": 0.0,
                "avg": 0.0,
                "metric": "http://mserve/disc"
            },
            {
                "min": 578730.0,
                "max": 578730.0,
                "sum": 578730.0,
                "n": 1,
                "stddev": 0.0,
                "variance": 0.0,
                "avg": 578730.0,
                "metric": "http://mserve/disc_space"
            },
            {
                "min": 578730.0,
                "max": 578730.0,
                "sum": 578730.0,
                "n": 1,
                "stddev": 0.0,
                "variance": 0.0,
                "avg": 578730.0,
                "metric": "http://mserve/ingest"
            }
        ],
        "reportnum": 1
    }

PUT - **405 - Method Not Allowed**

POST - **405 - Method Not Allowed**

DELETE - **405 - Method Not Allowed**

MFile Authority URL
-------------------------
::

 /<mfile-id>/auths/

GET - Returns the authoritys for the specified mfile::

    [
        {
            "thumburl": "/mservemedia/images/package-x-generic.png",
            "methods": [],
            "roles": [
                "mfileowner"
            ],
            "basename": "IMAG0361.jpg",
            "auth_set": [],
            "urls": {
                "auths": [
                    "GET",
                    "PUT",
                    "POST",
                    "DELETE"
                ],
                "usages": [
                    "GET"
                ],
                "base": [
                    "GET",
                    "PUT",
                    "POST",
                    "DELETE"
                ],
                "properties": [
                    "GET"
                ],
                "file": [
                    "GET",
                    "PUT",
                    "POST",
                    "DELETE"
                ]
            },
            "authname": "owner",
            "id": "KD3fP0Pd6L2leaAZggZBBntzrYSVAiMIekFx3hTwliY"
        }
    ]
   
PUT - **405 - Method Not Allowed**

POST - Creates a new Authority for this MFile

* ``name`` (*str*) : The name for the new authority **Required**
* ``roles`` (*str*) : A comma separated list of role names for the new authority **Required**

DELETE - **405 - Method Not Allowed**
