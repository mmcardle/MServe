
import settings
tw = settings.thumbsize[0]
th = settings.thumbsize[1]
pw = settings.postersize[0]
ph = settings.postersize[1]

hd_w = settings.wuxga[0]
hd_h = settings.wuxga[1]

default_profiles = {
    "default": {
            "ingest" : [

                # Standard Ingest
                {"task":"md5file",            "args": {} },

                # Images
                {"task":"thumbimage",         "condition": "mfile.mimetype.startswith('image')",  "args": {"width":tw,"height":th} },
                {"task":"posterimage",        "condition": "mfile.mimetype.startswith('image')",  "args": {"width":pw,"height":ph} },

                ],
            "access" : [

                # Standard Access Tasks
                {"task":"dataservice.tasks.mfilefetch",         "args": {}    , "outputs" : [ {"name":"mfileoutput"} ] },

                ],
            "update" : [

                {"task":"md5file",            "args": {} },

                # Images
                {"task":"thumbimage",         "condition": "mfile.mimetype.startswith('image')",  "args": {"width":tw,"height":th} },
                {"task":"posterimage",        "condition": "mfile.mimetype.startswith('image')",  "args": {"width":pw,"height":ph} },

            ],
            "periodic" : []
            },
    "web-delivery": {
            "ingest" : [

                # Standard Ingest 
                {"task":"md5file",            "args": {} },

                # Images
                {"task":"thumbimage",         "condition": "mfile.mimetype.startswith('image')",  "args": {"width":tw,"height":th} },
                {"task":"posterimage",        "condition": "mfile.mimetype.startswith('image')",  "args": {"width":pw,"height":ph} },

                # Video
                {"task":"thumbvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"width":tw,"height":th} },
                {"task":"postervideo",        "condition": "mfile.mimetype.startswith('video')",  "args": {"width":pw,"height":ph} },
                {"task":"proxyvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] } },

                # MXF Ingest
                {"task":"thumbvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"width":tw,"height":th} },
                {"task":"proxyvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] } },
                {"task":"postervideo",        "condition": "mfile.name.endswith('mxf')",          "args": {"width":pw,"height":ph} },

                ],
            "access" : [

                # Standard Access Tasks
                {"task":"dataservice.tasks.mfilefetch",         "args": {}    , "outputs" : [ {"name":"mfileoutput"} ] },

                ],
            "update" : [
                 
                # Standard Ingest (images/videos)
                {"task":"md5file",            "args": {} },

                # Images
                {"task":"thumbimage",         "condition": "mfile.mimetype.startswith('image')",  "args": {"width":tw,"height":th} },
                {"task":"posterimage",        "condition": "mfile.mimetype.startswith('image')",  "args": {"width":pw,"height":ph} },

                # Video
                {"task":"thumbvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"width":tw,"height":th} },
                {"task":"postervideo",        "condition": "mfile.mimetype.startswith('video')",  "args": {"width":pw,"height":ph} },
                {"task":"proxyvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] } },

                # MXF Ingest
                {"task":"thumbvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"width":tw,"height":th} },
                {"task":"proxyvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] } },
                {"task":"postervideo",        "condition": "mfile.name.endswith('mxf')",          "args": {"width":pw,"height":ph} },

            ],
            "periodic" : []
            },
    "hd-delivery": {
            "ingest" : [

                # Standard Ingest (images/videos)
                {"task":"md5file",  "args": {} },
                {"task":"dataservice.tasks.backup_mfile",       "args": {} },

                # Images
                {"task":"thumbimage",   "condition": "mfile.mimetype.startswith('image')",  "args": {"width":tw,"height":th} },
                {"task":"posterimage",  "condition": "mfile.mimetype.startswith('image')",  "args": {"width":pw,"height":ph} },

                # Video
                {"task":"thumbvideo",   "condition": "mfile.mimetype.startswith('video')",  "args": {"width":tw,"height":th} },
                {"task":"postervideo",  "condition": "mfile.mimetype.startswith('video')",  "args": {"width":pw,"height":ph} },
                {"task":"proxyvideo",   "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] } },

                # HD
                {"task":"transcodevideo",   "allowremote" :True,  "remotecondition" : "numlocal >= 0", "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-s","%s:%s"%(hd_w,hd_h),"-r","24","-vcodec","dnxhd","-f","mov","-pix_fmt","rgb32","-b","120000k","-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] }, "outputs" : [ {"name":"HD.mov","mimetype":"video/quicktime"} ] },
                {"task":"transcodevideo",   "allowremote" :True,  "remotecondition" : "numlocal >= 0", "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-s","%s:%s"%(hd_w,hd_h),"-r","24","-vcodec","dnxhd","-f","mov","-pix_fmt","rgb32","-b","120000k","-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] }, "outputs" : [ {"name":"HD.mov","mimetype":"video/quicktime"} ]  },

                # MXF Ingest
                {"task":"proxyvideo",   "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] } },
                {"task":"postervideo",  "condition": "mfile.name.endswith('mxf')",          "args": {"width":tw,"height":th} },

                ],
            "access" : [

                # Standard Access Tasks
                {"task":"dataservice.tasks.mfilefetch",         "args": {}    , "outputs" : [ {"name":"mfileoutput"} ] },

                ],
            "update" : [

                # Standard Ingest (images/videos)
                {"task":"md5file",            "args": {} },
                {"task":"dataservice.tasks.backup_mfile",       "args": {} },

                # Images
                {"task":"thumbimage",                           "condition": "mfile.mimetype.startswith('image')",  "args": {"width":tw,"height":th} },
                {"task":"posterimage",        "condition": "mfile.mimetype.startswith('image')",  "args": {"width":pw,"height":ph} },

                # Video
                {"task":"thumbvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"width":tw,"height":th} },
                {"task":"postervideo",        "condition": "mfile.mimetype.startswith('video')",  "args": {"width":pw,"height":ph} },
                {"task":"proxyvideo",         "condition": "mfile.mimetype.startswith('video')",  "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","2","-ab","64","-ar","44100"] } },

                # MXF Ingest
                {"task":"thumbvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"width":tw,"height":th} },
                {"task":"proxyvideo",         "condition": "mfile.name.endswith('mxf')",          "args": {"ffmpeg_args": ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(pw,ph),"-acodec","libfaac","-ac","1","-ab","64","-ar","44100"] } },
                {"task":"postervideo",        "condition": "mfile.name.endswith('mxf')",          "args": {"width":pw,"height":ph} },

            ],
            "periodic" : []
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