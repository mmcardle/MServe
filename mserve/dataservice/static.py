
default_profiles = {
    "default": {
            "ingest" : [
                {"taskname":"dataservice.tasks.md5file",        "args": {} },
                {"taskname":"dataservice.tasks.thumb",          "condition": "mfile.mimetype.startswith('image')", "args": {"width":"210","height":"128"} },
                {"taskname":"dataservice.tasks.poster",         "condition": "mfile.mimetype.startswith('image')", "args": {"width":"420","height":"256"} },
                {"taskname":"dataservice.tasks.proxyvideo",     "condition": "mfile.mimetype.startswith('video')", "args": {"width":"420","height":"256"} },
                {"taskname":"dataservice.tasks.backup_mfile",   "args": {} },
                ],
            "access" : ["check_md5"],
            "update" : ["md5","thumb"],
            "periodic" : ["md5"]
            },
    "hd": {
            "ingest" : ["md5","thumb","ffmpeg"],
            "access" : ["check_md5"],
            "update" : ["md5","thumb"],
            "periodic" : ["md5"]
            }
}

default_roles = {
"containeradmin": {
    "methods" : ["GET","PUT","POST","DELETE"],\
    "urls" : {\
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET","PUT"],\
        "usages":["GET"],\
        "services":["GET","POST"],\
        }
    }
,
"serviceadmin" : {
    "methods" : ["GET","PUT","POST","DELETE"],\
    "urls": {
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET","PUT"],\
        "usages":["GET"],\
        "mfiles":["GET","POST","PUT","DELETE"],\
        "jobs":["GET","POST","PUT","DELETE"],\
        "mfolders":["GET","POST","PUT","DELETE"]\
        }
    }
,
"servicecustomer" : {
    "methods" : ["GET"],\
    "urls": {
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET"],\
        "usages":["GET"],\
        "mfiles":["GET","POST","PUT","DELETE"],\
        "jobs":["GET","POST","PUT","DELETE"],\
        "mfolders":["GET","POST","PUT","DELETE"]\
        }
    }
,
"mfileowner": {
    "methods" : ["GET","PUT","POST","DELETE"],\
    "urls": {
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET"],\
        "usages":["GET"],\
        "file":["GET","PUT","POST","DELETE"],\
        "base":["GET","PUT","POST","DELETE"],\
        }
    }
,
"mfilereadwrite" : {
    "methods" : ["GET","PUT","POST","DELETE"],\
    "urls": {
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET"],\
        "usages":["GET"],\
        "file":["GET","PUT","POST","DELETE"],\
        "base":["GET"],\
        }
    }
,
"mfilereadonly" : {
    "methods" : ["GET"],\
    "urls": {
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET"],\
        "usages":["GET"],\
        "file":["GET"],\
        }
    }
}