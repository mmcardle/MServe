
import settings
tw = settings.thumbsize[0]
th = settings.thumbsize[1]
pw = settings.postersize[0]
ph = settings.postersize[1]

hd_w = settings.wuxga[0]
hd_h = settings.wuxga[1]

default_profiles = {
    "default": {
            "pre-ingest" : [
                {"task":"dataservice.tasks.mimefile",           "args": {} },
                ],
            "ingest" : [

                # Standard Ingest (images/videos)
                {"task":"dataservice.tasks.md5file",            "args": {} },
                {"task":"dataservice.tasks.backup_mfile",       "args": {} },

                # Images
                {"task":"dataservice.tasks.thumbimage",         "condition": "mfile.mimetype.startswith('image')",  "args": {"width":tw,"height":th} },
                {"task":"dataservice.tasks.posterimage",        "condition": "mfile.mimetype.startswith('image')",  "args": {"width":pw,"height":ph} },

                # Video
                {"task":"dataservice.tasks.thumbvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"width":tw,"height":th} },
                {"task":"dataservice.tasks.postervideo",        "condition": "mfile.mimetype.startswith('video')",  "args": {"width":pw,"height":ph} },
                {"task":"dataservice.tasks.proxyvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","baseline","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] } },

                # MXF Ingest
                {"task":"dataservice.tasks.thumbvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"width":tw,"height":th} },
                {"task":"dataservice.tasks.proxyvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","baseline","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] } },
                {"task":"dataservice.tasks.postervideo",        "condition": "mfile.name.endswith('mxf')",          "args": {"width":pw,"height":ph} },

                ],
            "pre-access" : [

                # Standard Access Check
                {"task":"dataservice.tasks.md5fileverify",    "args": {} },

                ],
            "access" : [

                # Standard Access Tasks
                {"task":"dataservice.tasks.mfilefetch",       "args": {}    , "outputs" : [ {"name":"mfileoutput"} ] },

                ],
            "update" : [
                 
                # Standard Ingest (images/videos)
                {"task":"dataservice.tasks.md5file",            "args": {} },
                {"task":"dataservice.tasks.backup_mfile",       "args": {} },

                # Images
                {"task":"dataservice.tasks.thumbimage",         "condition": "mfile.mimetype.startswith('image')",  "args": {"width":tw,"height":th} },
                {"task":"dataservice.tasks.posterimage",        "condition": "mfile.mimetype.startswith('image')",  "args": {"width":pw,"height":ph} },

                # Video
                {"task":"dataservice.tasks.thumbvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"width":tw,"height":th} },
                {"task":"dataservice.tasks.postervideo",        "condition": "mfile.mimetype.startswith('video')",  "args": {"width":pw,"height":ph} },
                {"task":"dataservice.tasks.proxyvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","baseline","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] } },

                # MXF Ingest
                {"task":"dataservice.tasks.thumbvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"width":tw,"height":th} },
                {"task":"dataservice.tasks.proxyvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","baseline","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] } },
                {"task":"dataservice.tasks.postervideo",        "condition": "mfile.name.endswith('mxf')",          "args": {"width":pw,"height":ph} },

            ],
            "periodic" : ["md5"]
            },
    "hd": {
            "pre-ingest" : [
                {"task":"dataservice.tasks.mimefile",           "args": {} },
                ],
            "ingest" : [

                # Standard Ingest (images/videos)
                {"task":"dataservice.tasks.md5file",            "args": {} },
                {"task":"dataservice.tasks.backup_mfile",       "args": {} },

                # Images
                {"task":"dataservice.tasks.thumbimage",         "condition": "mfile.mimetype.startswith('image')",  "args": {"width":tw,"height":th} },
                {"task":"dataservice.tasks.posterimage",        "condition": "mfile.mimetype.startswith('image')",  "args": {"width":pw,"height":ph} },

                # Video
                {"task":"dataservice.tasks.thumbvideo",        "condition": "mfile.mimetype.startswith('video')",  "args": {"width":tw,"height":th} },
                {"task":"dataservice.tasks.postervideo",        "condition": "mfile.mimetype.startswith('video')",  "args": {"width":pw,"height":ph} },
                {"task":"dataservice.tasks.proxyvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","baseline","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] } },

                # HD
                {"task":"dataservice.tasks.transcodevideo",     "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-s","%s:%s"%(hd_w,hd_h),"-r","24","-vcodec","dnxhd","-f","mov","-pix_fmt","rgb32","-b","120000k","-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] }, "outputs" : [ {"name":"HD.mov","mimetype":"video/quicktime"} ] },
                {"task":"dataservice.tasks.transcodevideo",     "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-s","%s:%s"%(hd_w,hd_h),"-r","24","-vcodec","dnxhd","-f","mov","-pix_fmt","rgb32","-b","120000k","-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] }, "outputs" : [ {"name":"HD.mov","mimetype":"video/quicktime"} ]  },

                # MXF Ingest
                {"task":"dataservice.tasks.proxyvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","baseline","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] } },
                {"task":"dataservice.tasks.postervideo",        "condition": "mfile.name.endswith('mxf')",          "args": {"width":tw,"height":th} },

                ],
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