
import settings
tw = settings.thumbsize[0]
th = settings.thumbsize[1]
pw = settings.postersize[0]
ph = settings.postersize[1]

hd_w = settings.hd1080[0]
hd_h = settings.hd1080[1]

default_profiles = {
    "default": {
            "ingest" : {
                # Standard Ingest
                "tasksets":
                [   {
                        "name" : "taskset1",
                        "tasks" : [ { "name":"A", "task":"dataservice.tasks.mimefile","args": {},},],
                    },
                    {
                        "name" : "taskset2",
                        "tasks" : [
                            {"name":"B","task":"dataservice.tasks.md5file","args": {},},
                            {"name":"C","task":"dataservice.tasks.thumbimage","args": {"width":tw,"height":th},"condition": "mfile.mimetype.startswith('image')",},
                            {"name":"D","task":"dataservice.tasks.posterimage","args": {"width":pw,"height":ph},"condition": "mfile.mimetype.startswith('image')",},
                            {"name":"E","task":"dataservice.tasks.backup_mfile","args": {}},
                        ],
                    },
                   ],
            },
            "update" : {
                # Standard Ingest
                "tasksets":
                [   {
                        "name" : "taskset1",
                        "tasks" : [ { "name":"A", "task":"dataservice.tasks.mimefile","args": {},},],
                    },
                    {
                        "name" : "taskset2",
                        "tasks" : [
                            {"name":"B","task":"dataservice.tasks.md5file","args": {},},
                            {"name":"C","task":"dataservice.tasks.thumbimage","args": {"width":tw,"height":th},"condition": "mfile.mimetype.startswith('image')",},
                            {"name":"D","task":"dataservice.tasks.posterimage","args": {"width":pw,"height":ph},"condition": "mfile.mimetype.startswith('image')",},
                        ],
                    },
                   ],
            },
            "access" : {
                # Standard Ingest
                "tasksets":
                [],
            },
            "periodic" : {
                # Standard Ingest
                "tasksets":
                [],
            },
        },
        "transcode": {
            "ingest" : {
                # Standard Ingest
                "tasksets":
                [   {
                        "name" : "taskset1",
                        "tasks" : [ { "name":"A", "task":"dataservice.tasks.mimefile","args": {},},],
                    },
                    {
                        "name" : "taskset2",
                        "tasks" : [

                            # Image
                            {"name":"B","task":"dataservice.tasks.md5file","args": {},},
                            {"name":"C","task":"dataservice.tasks.thumbimage","args": {"width":tw,"height":th},"condition": "mfile.mimetype.startswith('image')",},
                            {"name":"D","task":"dataservice.tasks.posterimage","args": {"width":pw,"height":ph},"condition": "mfile.mimetype.startswith('image')",},
                            {"name":"K","task":"dataservice.tasks.backup_mfile","args": {},},

                            # Video
                            {"name":"E","task":"dataservice.tasks.thumbvideo",   "condition": "mfile.mimetype.startswith('video')",  "args": {"width":tw,"height":th} },
                            {"name":"F","task":"dataservice.tasks.postervideo",  "condition": "mfile.mimetype.startswith('video')",  "args": {"width":pw,"height":ph} },
                            {"name":"G","task":"dataservice.tasks.proxyvideo",   "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] } },

                            # HD
                            {"name":"H","task":"dataservice.tasks.transcodevideo",  "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-s","%s:%s"%(hd_w,hd_h),"-r","24","-vcodec","dnxhd","-f","mov","-pix_fmt","rgb32","-b","120000k","-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] }, "outputs" : [ {"name":"HD.mov","mimetype":"video/quicktime"} ] },
                            {"name":"L","task":"dataservice.tasks.transcodevideo",  "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-s","%s:%s"%(hd_w,hd_h),"-r","24","-vcodec","dnxhd","-f","mov","-pix_fmt","rgb32","-b","120000k","-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] }, "outputs" : [ {"name":"HD.mov","mimetype":"video/quicktime"} ]  },

                            # MXF Ingest
                            {"name":"I","task":"dataservice.tasks.proxyvideo",   "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] } },
                            {"name":"J","task":"dataservice.tasks.postervideo",  "condition": "mfile.name.endswith('mxf')",          "args": {"width":tw,"height":th} },

                        ],
                    },
                   ],
            },
            "update" : {
                # Standard Ingest
                "tasksets":
                [   {
                        "name" : "taskset1",
                        "tasks" : [ { "name":"A", "task":"dataservice.tasks.mimefile","args": {},},],
                    },
                    {
                        "name" : "taskset2",
                        "tasks" : [
                            # Image
                            {"name":"B","task":"dataservice.tasks.md5file","args": {},},
                            {"name":"C","task":"dataservice.tasks.thumbimage","args": {"width":tw,"height":th},"condition": "mfile.mimetype.startswith('image')",},
                            {"name":"D","task":"dataservice.tasks.posterimage","args": {"width":pw,"height":ph},"condition": "mfile.mimetype.startswith('image')",},

                            # Video
                            {"name":"E","task":"dataservice.tasks.thumbvideo",   "condition": "mfile.mimetype.startswith('video')",  "args": {"width":tw,"height":th} },
                            {"name":"F","task":"dataservice.tasks.postervideo",  "condition": "mfile.mimetype.startswith('video')",  "args": {"width":pw,"height":ph} },
                            {"name":"G","task":"dataservice.tasks.proxyvideo",   "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] } },

                            # HD
                            {"name":"H","task":"dataservice.tasks.transcodevideo",   "allowremote" :True,  "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-s","%s:%s"%(hd_w,hd_h),"-r","24","-vcodec","dnxhd","-f","mov","-pix_fmt","rgb32","-b","36000k","-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] }, "outputs" : [ {"name":"HD.mov","mimetype":"video/quicktime"} ] },
                            {"name":"D","task":"dataservice.tasks.transcodevideo",   "allowremote" :True,  "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-s","%s:%s"%(hd_w,hd_h),"-r","24","-vcodec","dnxhd","-f","mov","-pix_fmt","rgb32","-b","36000k","-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] }, "outputs" : [ {"name":"HD.mov","mimetype":"video/quicktime"} ]  },

                            # MXF Ingest
                            {"name":"I","task":"dataservice.tasks.proxyvideo",   "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] } },
                            {"name":"J","task":"dataservice.tasks.postervideo",  "condition": "mfile.name.endswith('mxf')",          "args": {"width":tw,"height":th} },

                        ],
                    },
                   ],
            },
            "access" : {
                # Standard Ingest
                "tasksets":
                [],
            },
            "periodic" : {
                # Standard Ingest
                "tasksets":
                [],
            },
        },
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
        "mfolders":["GET","POST","PUT","DELETE"],\
        "profiles":["GET"],\
        "base":["GET"],\
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
        "mfolders":["GET","POST","PUT","DELETE"],\
        "base":["GET"],\
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