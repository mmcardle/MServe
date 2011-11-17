
MServe REST API
=======================

Containers URL
--------------
::

 /containers/

GET - Returns a list of containers::

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

* name (*str*) : Name of the the container

PUT - **No Such Method**

DELETE - **No Such Method**

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

* name : str : New name for the the container

POST - **No Such Method**

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

* property (*str*) : The name of the property
* value (*str*) : The new value for the the property

POST - **No Such Method**

DELETE - **No Such Method**