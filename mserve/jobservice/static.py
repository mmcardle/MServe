job_descriptions = {}
job_descriptions['dumbtask'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "image/jpeg" },
        "output-0" : { "mimetype" : "text/plain" },
        "options" : [],
        "results" :[]
    }
job_descriptions['dataservice.tasks.dumbtask'] = job_descriptions['dumbtask']
job_descriptions['swirl'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "image/jpg" },
        "output-0" : { "mimetype" : "image/jpg" },
        "options" : [],
        "results" :[]
    }
job_descriptions['dataservice.tasks.swirl'] =  job_descriptions['swirl']
job_descriptions['imodel'] = {
        "nbinputs" : 1,
        "nboutputs" : 2,
        "input-0" : { "mimetype" : "application/json" },
        "output-0" : { "mimetype" : "text/csv" },
        "output-1" : { "mimetype" : "text/plain" },
        "options" : [],
        "results" :[]
    }
job_descriptions['dataservice.tasks.imodel'] =  job_descriptions['imodel']
job_descriptions['thumbimage'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "image/png" },
        "options" : ['width','height'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.thumbimage'] = job_descriptions['thumbimage']
job_descriptions['posterimage'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "image/png" },
        "options" : ['width','height'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.posterimage'] = job_descriptions['posterimage']
job_descriptions['thumbvideo'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "video" },
        "options" : ['width','height'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.thumbvideo'] = job_descriptions['thumbvideo']
job_descriptions['postervideo'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "video" },
        "options" : ['width','height'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.postervideo'] = job_descriptions['postervideo']
job_descriptions['proxyvideo'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "video" },
        "options" : ['width','height','ffmpeg_args'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.proxyvideo'] = job_descriptions['proxyvideo']
job_descriptions['transcodevideo'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "video" },
        "output-0" : { "mimetype" : "video/mp4" },
        "options" : ['width','height','ffmpeg_args'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.transcodevideo'] = job_descriptions['transcodevideo']
job_descriptions['dataservice.tasks.mfilefetch'] = {
    "nbinputs" : 1,
    "nboutputs" : 1,
    "input-0" : { "mimetype" : "video" },
    "output-0" : { "mimetype" : "application/octet-stream" },
    "options" : [],
    "results" :[],
}
job_descriptions['dataservice.tasks.md5fileverify'] = {
    "nbinputs" : 1,
    "nboutputs" : 0,
    "input-0" : { "mimetype" : "application/octet-stream" },
    "options" : [],
    "results" :[],
}
job_descriptions['jobservice.tasks.copyfromurl'] = {
        "nbinputs" : 0,
        "nboutputs" : 1,
        "output-0" : { "mimetype" : "application/octet-stream" },
        "options":['url'],
        "results" :[]
    }
job_descriptions['md5file'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "options": [] ,
        "results" : ['md5']
}
job_descriptions['dataservice.tasks.md5file'] = job_descriptions['md5file']
job_descriptions['mimefile'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "options": [] ,
        "results" : ['mimetype']
}
job_descriptions['jobservice.tasks.render_blender'] =    {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "output-0" : { "mimetype" : "image/png"},
        "options":['frame'],
        "results" : []
    }
job_descriptions['prestoprime.tasks.mxftechmdextractor'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "output-0" : { "mimetype" : "text/plain"},
        "options":[],
        "results" : []
    }
job_descriptions['prestoprime.tasks.d10mxfchecksum'] =    {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "output-0" : { "mimetype" : "text/plain"},
        "options":[],
        "results" : []
    }
job_descriptions['prestoprime.tasks.mxfframecount'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "options":[],
        "results" : ["lines"]
    }
job_descriptions['prestoprime.tasks.extractd10frame'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "output-0" : { "mimetype" : "image/png" },
        "options":['frame'],
        "results" : []
    }
job_descriptions['digitalrapids'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "video" },
        "output-0" : { "mimetype" : "video/mp4" },
        "options":[],
        "results" : []
}
job_descriptions['red3dmux'] = {
        "nbinputs" : 2,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "video" },
        "input-1" : { "mimetype" : "video" },
        "output-0" : { "mimetype" : "image/tiff" },
        "options":["start_frame","end_frame"],
        "results" : []
}
job_descriptions['red2dtranscode'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "video" },
        "input-1" : { "mimetype" : "video" },
        "output-0" : { "mimetype" : "application/octet-stream" },
        "options":["export_type","start_frame","end_frame"],
        "results" : []
}
job_descriptions_admin = {}

job_descriptions_admin['dataservice.tasks.backup_mfile'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "options":[],
        "results" : []
}
