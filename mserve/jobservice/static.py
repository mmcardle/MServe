job_descriptions = {}
job_descriptions['dataservice.tasks.thumbimage'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "image/png" },
        "options" : ['width','height'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.posterimage'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "image/png" },
        "options" : ['width','height'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.thumbvideo'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "video" },
        "options" : ['width','height'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.postervideo'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "video" },
        "options" : ['width','height'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.mfilefetch'] = {
    "nbinputs" : 1,
    "nboutputs" : 1,
    "input-0" : { "mimetype" : "video" },
    "output-0" : { "mimetype" : "application/octet-stream" },
    "options" : [],
    "results" :[]
}
job_descriptions['jobservice.tasks.copyfromurl'] = {
        "nbinputs" : 0,
        "nboutputs" : 1,
        "output-0" : { "mimetype" : "application/octet-stream" },
        "options":['url'],
        "results" :[]
    }
job_descriptions['dataservice.tasks.md5file'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "options": [] ,
        "results" : ['md5']
}
job_descriptions['dataservice.tasks.mimefile'] = {
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