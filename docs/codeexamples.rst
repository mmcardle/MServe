
MServe HTTP Code Examples
==========================

Python
------------------

Get Service Details
++++++++++++++++++++

::

    import StringIO
    import pycurl
    import simplejson as json

    resp = StringIO.StringIO()
    protocol = "http"
    host = "localhost"
    serviceid = ""  ###### Get this from MServe ######

    remoteservice = protocol+"://"+host+"/services/"+serviceid+"/"

    c = pycurl.Curl()
    c.setopt(c.URL, str(remoteservice))
    c.setopt(c.WRITEFUNCTION, resp.write)
    c.perform()
    status = c.getinfo(c.HTTP_CODE)
    c.close()

    print "Return status code '%s' " % (status)
    print "Response '%s' " % (resp.getvalue())
    
    js = json.loads(resp.getvalue())

    print js["id"]
    print js["name"]

Response should contain output similar to
::

    {
        "subservices_url": "/services/HrSsQsQ8rYfca0dELbVoOdZDxyiVLfFzUVHFS4f5GE/subservices/",
        "name": "Service",
        "folder_structure": {
            "data": {
                "data": "Service",
                "attr": {
                    "id": "HrSsQsQ8rYfca0dELbVoOdZDxyiVLfFzUVHFS4f5GE",
                    "class": "service"
                },
                "children": []
            }
        },
        "mfile_set": [],
        "priority": false,
        "thumbs": [
            "/mservemedia/images/package-x-generic.png",
            "/mservemedia/images/package-x-generic.png",
            "/mservemedia/images/package-x-generic.png",
            "/mservemedia/images/package-x-generic.png"
        ],
        "starttime": "2011-11-22 10:09:05",
        "mfolder_set": [],
        "endtime": "2011-11-23 11:09:05",
        "id": "HrSsQsQ8rYfca0dELbVoOdZDxyiVLfFzUVHFS4f5GE",
        "reportnum": 1
    }


Upload a File to a Service
++++++++++++++++++++++++++

::

    import StringIO
    import pycurl
    import simplejson as json

    resp = StringIO.StringIO()
    protocol = "http"
    host = "localhost:8000"
    serviceid = "ZtdoKyUh27lmkG0gnpQKlUhLZw2Ae27GDCTQbch4MA"

    remoteservice = protocol+"://"+host+"/services/"+serviceid+"/mfiles/"
    filename = "/path/to/file"

    c = pycurl.Curl()
    http_post = [ ("newfilename.txt", (c.FORM_FILE, str(filename ))) ]
    c.setopt(c.POST, 1)
    c.setopt(c.HTTPPOST, http_post )
    c.setopt(c.URL, str(remotemfile))
    c.setopt(c.WRITEFUNCTION, resp.write)
    c.perform()
    status = c.getinfo(c.HTTP_CODE)
    c.close()
    
    print "Return status code '%s' " % (status)
    print "Response '%s' " % (resp.getvalue())

    js = json.loads(resp.getvalue())

    print js["id"]
    print js["name"]

Response should contain output similar to
::

    {
        "mimetype": "application/pdf",
        "updated": "2011-11-22 10:09:37",
        "thumburl": "/mservemedia/images/package-x-generic.png",
        "thumb": "",
        "created": "2011-11-22 10:09:36",
        "checksum": null,
        "posterurl": "/mservemedia/images/package-x-generic.png",
        "name": "output.pdf",
        "proxyurl": "",
        "proxy": "",
        "file": "2011/11/22/rKizE5S9U94ZN0Vs1NTzjak71FK2exvLslvMYHaNpZs/output.pdf",
        "poster": "",
        "reportnum": 1,
        "id": "4dOeqysLNdemXEQOEROs3hOIsQNALxrntV7ooHPo",
        "size": 38571
    }


Get jobs for a file
++++++++++++++++++++++++++

::

    import StringIO
    import pycurl
    import simplejson as json

    resp = StringIO.StringIO()
    protocol = "http"
    host = "localhost:8000"

    mfileid = "" ###### Get this from MServe ######
    remotemfile = protocol+"://"+host+"/mfiles/"+mfileid+"/jobs/"

    c = pycurl.Curl()
    c.setopt(c.URL, str(remotemfile))
    c.setopt(c.WRITEFUNCTION, resp.write)
    c.perform()
    status = c.getinfo(c.HTTP_CODE)
    c.close()

    print "Return status code '%s' " % (status)
    print "Response '%s' " % (resp.getvalue())


Response should contain output similar to
::

    [
        {
            "tasks": {
                "completed_count": 0,
                "successful": false,
                "taskset_id": "f01a2ac9-ef5c-4c2b-8b89-8bddd9975326",
                "percent": 0.0,
                "failed": false,
                "waiting": true,
                "result": [
                    {
                        "state": "PENDING",
                        "name": "mimefile",
                        "success": false,
                        "result": null
                    }
                ],
                "ready": false,
                "total": 1
            },
            "name": "Workflow ingest - Task taskset1",
            "joboutput_set": [],
            "created": "2011-11-22 10:49:51",
            "taskset_id": "f01a2ac9-ef5c-4c2b-8b89-8bddd9975326",
            "id": "YNFmcOfXG4LlB45byQufYn3SKDYSVmzPz4SOjCkXMJI"
        }
    ]


Java
------------------

Get Service Details
++++++++++++++++++++

::

    import org.apache.commons.httpclient.HttpClient;
    import org.apache.commons.httpclient.HttpMethod;
    import org.apache.commons.httpclient.methods.GetMethod;
    import java.io.InputStream;
    import java.io.InputStreamReader;
    import java.io.BufferedReader;
    import org.json.JSONObject;
    
    public class Example{

        public static void main(String[] args){
            try{

                String protocol = "http";
                String host = "localhost";
                String id = ""; ###### Get this from MServe ######

                URL url = new URL(protocol + "://" + host + "/services/" + id +"/");
                HttpClient client = new HttpClient();
                HttpMethod method = new GetMethod(url.toString());
                method.setRequestHeader("Accept", "application/json");

                client.executeMethod(method);

                InputStream stream = method.getResponseBodyAsStream();

                BufferedReader buf = new BufferedReader(new InputStreamReader(stream));
                String output = "";
                String str;
                while (null != ((str = buf.readLine()))) {
                    output += str;
                }
                buf.close();

                if(method.getStatusCode()!=200){
                    System.err.println(""+output);
                    throw new RuntimeException("Response is "+method.getStatusText()+" code="+method.getStatusCode());
                }

                JSONObject jsonob = new JSONObject(output);

                System.out.println(jsonob.getString("name"));
                System.out.println(jsonob.getString("id"));

            } catch (MalformedURLException ex) {
                throw new RuntimeException(ex);
            } catch (IOException ex) {
                throw new RuntimeException(ex);
            } catch (JSONException ex) {
                    throw new RuntimeException(ex);
            }
        }
    }

Upload a File to a Service
++++++++++++++++++++++++++

::

    import org.apache.commons.httpclient.HttpClient;
    import org.apache.commons.httpclient.HttpMethod;
    import org.apache.commons.httpclient.methods.PostMethod;
    import org.apache.commons.httpclient.methods.multipart.FilePart;
    import org.apache.commons.httpclient.methods.multipart.MultipartRequestEntity;
    import org.apache.commons.httpclient.methods.multipart.Part;
    import java.io.InputStream;
    import java.io.InputStreamReader;
    import java.io.BufferedReader;
    import org.json.JSONObject;
    import java.io.File;

    public class Example{

        public static void main(String[] args){
            try{

                File f = <some file>

                String protocol = "http";
                String host = "localhost";
                String id = ""; ###### Get this from MServe ######

                URL url = new URL(protocol + "://" + host + "/services/" + id +"/");
                HttpClient client = new HttpClient();
                PostMethod filePost = new PostMethod(url);
                filePost.setRequestHeader("Accept", "application/json");

                Part[] parts = {
                    new FilePart("file", f)
                };

                filePost.setRequestEntity( new MultipartRequestEntity(parts, filePost.getParams()));
                client.executeMethod(filePost);
                InputStream stream = filePost.getResponseBodyAsStream();

                BufferedReader buf = new BufferedReader(new InputStreamReader(stream));
                String output = "";
                String str;
                while (null != ((str = buf.readLine()))) {
                    output += str;
                }
                buf.close();
                filePost.releaseConnection();

                JSONObject jsonob = new JSONObject(output);

                System.out.println(jsonob.getString("name"));
                System.out.println(jsonob.getString("id"));

            } catch (MalformedURLException ex) {
                throw new RuntimeException(ex);
            } catch (IOException ex) {
                throw new RuntimeException(ex);
            } catch (JSONException ex) {
                    throw new RuntimeException(ex);
            }
        }
    }


Submit a Job
++++++++++++++++

::

    String url = protocol + "://" + host + "/mfiles/" + mfileid +"/jobs/"
    PostMethod postMethod = new PostMethod(joburl.toString());
    postMethod.setRequestHeader("Accept", "application/json");

    NameValuePair[] data = {
      new NameValuePair("jobtype", "dataservice.tasks.mimefile"),
    };

    postMethod.setRequestBody(data);
    client.executeMethod(postMethod);

    InputStream poststream = postMethod.getResponseBodyAsStream();

    BufferedReader postbuf = new BufferedReader(new InputStreamReader(poststream));
    String postoutput = "";
    String poststr;
    while (null != ((poststr = postbuf.readLine()))) {
        postoutput += poststr;
    }
    postbuf.close();
    postMethod.releaseConnection();

    JSONObject postjsonob = new JSONObject(postoutput);

    System.out.println("doFilePostToREST output "+postjsonob.toString(4));

    String jobid = postjsonob.getString("id");

Submit a Job with parameters
++++++++++++++++++++++++++++++

::

    ... As Above

    NameValuePair[] data = {
      new NameValuePair("jobtype", "dataservice.tasks.thumbimage"),
      new NameValuePair("width", "100"),
      new NameValuePair("height", "100"),
    };

    ... As Above


Poll for Job status
+++++++++++++++++++++++++

::

    String url = protocol + "://" + host + "/jobs/" + jobid +"/"
    HttpClient client = new HttpClient();
    HttpMethod method = new GetMethod(url);
    method.setRequestHeader("Accept", "application/json");
    Boolean success = Boolean.FALSE;
    while(!success){
        client.executeMethod(method);
        InputStream stream = method.getResponseBodyAsStream();

        BufferedReader buf = new BufferedReader(new InputStreamReader(stream));
        String output = "";
        String str;
        while (null != ((str = buf.readLine()))) {
            output += str;
        }
        buf.close();

        JSONObject postjsonob = new JSONObject(output);
        JSONObject tasks = postjsonob.getJSONObject("tasks");
        success = tasks.getBoolean("successful");
        System.out.println("job "+success);
        Thread.sleep(1000);
    }