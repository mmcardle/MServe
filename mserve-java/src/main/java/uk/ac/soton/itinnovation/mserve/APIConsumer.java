package uk.ac.soton.itinnovation.mserve;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import org.apache.commons.httpclient.Header;
import org.apache.commons.httpclient.HostConfiguration;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpConnectionManager;
import org.apache.commons.httpclient.HttpException;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.MultiThreadedHttpConnectionManager;
import org.apache.commons.httpclient.methods.DeleteMethod;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.httpclient.methods.HeadMethod;
import org.apache.commons.httpclient.methods.InputStreamRequestEntity;
import org.apache.commons.httpclient.methods.PostMethod;
import org.apache.commons.httpclient.methods.PutMethod;
import org.apache.commons.httpclient.methods.multipart.FilePart;
import org.apache.commons.httpclient.methods.multipart.MultipartRequestEntity;
import org.apache.commons.httpclient.methods.multipart.Part;
import org.apache.commons.httpclient.methods.multipart.StringPart;
import org.apache.commons.httpclient.params.HttpConnectionManagerParams;

public class APIConsumer {

    private String protocol = "http://";
    private String host = "localhost";

    public static void main(String[] args){



        /*try {
            APIConsumer consumer = new APIConsumer();
            //String cid = consumer.createContainer();
            //String cid = "05ac6c9b-02e7-419b-a9d9-6b70cc76eafa";


            //System.out.println("makeServiceURL");
            //String sid = consumer.makeServiceREST(cid);
            //String mid = consumer.makeEmptyMFileREST(sid);
            //consumer.putToEmptyMFile(mid, new File("/home/mm/Pictures/muppits/DSC_0676.jpg"));


            String path = "http://ogio/webdav/VUpBSGVKZEhxblZVTEhvZlFjM0ZYVkkyTmNQODlKTFNZbGlaVlBXWnRwTT0/";

            File file = new File("/home/mm/Pictures/muppits/DSC_0676.jpg");
            consumer.doChunkedPutToWebdavURL(path, file);


            //consumer.getUsage(cid);
            //consumer.getUsage(sid);
            //consumer.getUsage(mid);
            //consumer.deleteContainer(cid);

            //String mid1 = consumer.makeMFileURL(sid, new File("/home/mm/Pictures/muppits/DSC_0676.jpg"));
            //String mid2 = consumer.makeMFileREST(sid, new File("/home/mm/Pictures/muppits/DSC_0676.jpg"));
            //String mid = consumer.makeEmptyMFileREST(sid);
            //consumer.putToEmptyMFileREST(mid, new File("/home/mm/Pictures/muppits/DSC_0676.jpg"));
            //consumer.putToEmptyMFileURL(mid, new File("/home/mm/Pictures/muppits/DSC_0676.jpg"));

        } catch (MalformedURLException ex) {
            Logger.getLogger(APIConsumer.class.getName()).log(Level.SEVERE, null, ex);
        }*/

            String path = "/pic/somefolder//picture.jpg";

            String[] split = path.replace("//", "/").split("/");


            System.out.println("split " + split);


            ArrayList arr = new ArrayList();
            
            Collections.addAll(arr, split);

            String filename = (String)arr.get(arr.size()-1);
            List<String> folderList = arr.subList(0, arr.size()-1);
            folderList.remove("");

            System.out.println("filename " + filename);
            System.out.println("folderList " + folderList);

            String base = "/";
            for(String folder : folderList){
                base = base +  folder + "/";
                System.out.println("mkcol " + base);
            }




            //APIConsumer consumer = new APIConsumer();
            //System.out.println(""+consumer);
            //String path = "http://ogio/webdav/VUpBSGVKZEhxblZVTEhvZlFjM0ZYVkkyTmNQODlKTFNZbGlaVlBXWnRwTT0/hello.txt";
            //System.out.println(""+path);
            //consumer.partial(path);

            //consumer.doHeadToWebdavURL(path);
            //Header[] hs = consumer.head(path);
            //for (Header h : hs){
            //    System.out.println(""+h);
            //}

            //File file = new File("/home/mm/upload_test");



            /*consumer.doChunkedPutToWebdavURL(path, file, "");


            consumer.doChunkedPutToWebdavURL(path, file, "bytes=2-8");


            for(int i = 1;i<4;i++){
                File cfile = new File("/home/mm/chunk."+i);
                long len = cfile.length();
                long start = (i-1)*len;
                long end = (i)*len;
                consumer.doChunkedPutToWebdavURL(path, cfile,"bytes="+start+"-"+end);
            }*/
    }
    
        public void partial(String url) {
        try{
                HttpClient client = new HttpClient();
                PutMethod putMethod = new PutMethod(url);

                System.out.println(""+url);
                System.out.println(""+putMethod);

                //filePost.setRequestHeader("Accept", "application/json");
                //putMethod.addRequestHeader("Content-Length", "" + (fileOffset + buffer.remaining()) );

                byte[] bytes = "Dull!".getBytes();

                ByteArrayInputStream bis = new ByteArrayInputStream(bytes);

                putMethod.setRequestEntity(new InputStreamRequestEntity(bis));

                putMethod.addRequestHeader("Range", "bytes=6-11");
                //putMethod.addRequestHeader("Content-Length", ""+bis.available());

                client.executeMethod(putMethod);

                System.out.println("exec");

                InputStream stream = putMethod.getResponseBodyAsStream();

                if(stream!= null){
                    BufferedReader buf = new BufferedReader(new InputStreamReader(stream));
                    String output = "";
                    String str;
                    while (null != ((str = buf.readLine()))) {
                        output += str;
                    }
                    buf.close();
                    putMethod.releaseConnection();
                }

            }catch(IOException ex){
                throw new RuntimeException(ex);
            }

	}

    public Header[] head(String path) {
		Header[] headers = new Header[0];

                HostConfiguration hostConfig = new HostConfiguration();
		hostConfig.setHost("localhost:80");

		HttpConnectionManager connManager = new MultiThreadedHttpConnectionManager();
		HttpConnectionManagerParams params = new HttpConnectionManagerParams();
		int maxHostConnections = 20;
		params.setMaxConnectionsPerHost(hostConfig, maxHostConnections);
		connManager.setParams(params);

		HttpClient httpClient = new HttpClient(connManager);
                httpClient.setHostConfiguration(hostConfig);
                
		//HttpClient httpClient = new HttpClient();

		HeadMethod method = new HeadMethod(path);
		try {
			int status = httpClient.executeMethod(method);
			if (!(status >= 400) || status==404) {
				headers = method.getResponseHeaders();
			}
		} catch (HttpException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} finally {
			method.releaseConnection();
		}
		return headers;
	}

    public String doHeadToWebdavURL(String url) {
        try{
            HttpClient client = new HttpClient();
            HeadMethod headMethod = new HeadMethod(url);

            System.out.println(""+url);
            System.out.println(""+headMethod);

            //filePost.setRequestHeader("Accept", "application/json");

            client.executeMethod(headMethod);

            InputStream stream = headMethod.getResponseBodyAsStream();

            if(stream!= null){
                BufferedReader buf = new BufferedReader(new InputStreamReader(stream));
                String output = "";
                String str;
                while (null != ((str = buf.readLine()))) {
                    output += str;
                }
                buf.close();
                headMethod.releaseConnection();
                return output;
            }
            return "";

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }

    public String doChunkedPutToWebdavURL(String url, File f, String range) {
        try{
            HttpClient client = new HttpClient();
            PutMethod putMethod = new PutMethod(url);
            
            System.out.println(""+url);
            System.out.println(""+putMethod);
            
            //filePost.setRequestHeader("Accept", "application/json");
            //putMethod.addRequestHeader("Content-Length", "" + (fileOffset + buffer.remaining()) );

            
            putMethod.setRequestEntity(new InputStreamRequestEntity(new FileInputStream(f)));

            if(!range.equals("")){
                putMethod.addRequestHeader("Range", range);
            }

            boolean chunked = true;
            if(chunked){
                putMethod.addRequestHeader("Transfer-Encoding", "chunked");
                putMethod.setContentChunked(true);
                //long l = 5l+f.length();
                //putMethod.setRequestHeader("Content-Length", ""+l);
            }else{
                putMethod.addRequestHeader("Content-Length", ""+f.length());
            }

            client.executeMethod(putMethod);

            System.out.println("exec");

            InputStream stream = putMethod.getResponseBodyAsStream();

            if(stream!= null){
                BufferedReader buf = new BufferedReader(new InputStreamReader(stream));
                String output = "";
                String str;
                while (null != ((str = buf.readLine()))) {
                    output += str;
                }
                buf.close();
                putMethod.releaseConnection();
                return output;
            }
            return "";

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }


    public APIConsumer(){}

    public APIConsumer(String protocol,String host){
        this.protocol = protocol;
        this.host = host;
    }

    public String putToEmptyMFile(String id, File file) throws MalformedURLException {
        try {
            URL url = new URL(protocol + host + "/mfiles/" + id  +"/");
            String json = doFilePutToURL(url.toString(), id, file);
            System.out.println("putToEmptyMFileURL " + json);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }


    public String  makeServiceREST(String id) throws MalformedURLException {
        URL url = new URL(protocol + host + "/services/" );
        String content = "name=ServiceFromJava&container="+id;
        return makeService(url,content);
    }

    public String makeService(URL url, String content) {
        try {

            String output = doPostToURL(url,content);

            System.out.println("output =" + output);


            JSONObject ob = new JSONObject(output);

            System.out.println("New Service " + ob);

            return ob.getString("id");


        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public String  makeEmptyMFileREST(String id) throws MalformedURLException {
        try {
            String url = new String(protocol + host + "/mfiles/");
            String json = doFilePostToREST(url, id, null);
            System.out.println("makeEmptyMFileREST output "+json);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public String  makeMFileREST(String id, File file) throws MalformedURLException {
        System.out.println("makeMFileREST ");
        String url = new String(protocol + host + "/mfiles/");
        System.out.println("makeMFileREST url "+url);
        String output = doFilePostToREST(url, id, file);
        System.out.println("makeMFileREST output "+output);
        try {

            System.out.println("makeMFileREST output "+output);
            //JSONArray arr = new JSONArray(output);
            JSONObject ob = new JSONObject(output);
            return ob.getString("id");
        } catch (JSONException ex) {
            System.out.println("makeMFileREST "+ex);
            throw new RuntimeException(ex);
        }
    }

    public String doFilePutToURL(String url, String id, File f) {
        try{
            HttpClient client = new HttpClient();
            PutMethod filePost = new PutMethod(url);
            filePost.setRequestHeader("Accept", "application/json");
            Part[] parts = {
                new StringPart("sid", id),
                new FilePart("file", f)
            };
            filePost.setRequestEntity(
                    new MultipartRequestEntity(parts, filePost.getParams()));

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

            return output;

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }

    public String doFilePostToREST(String url, String id, File f) {
        System.out.println("doFilePostToREST url "+url);
        try{
            HttpClient client = new HttpClient();
            PostMethod filePost = new PostMethod(url);
            filePost.setRequestHeader("Accept", "application/json");
            Part[] parts = null;
            if(f!=null){
                parts = new Part[]{
                    new StringPart("sid", id),
                    new FilePart("file", f)
                };
            }else{
                parts = new Part[]{
                    new StringPart("sid", id),
                };
            }
            filePost.setRequestEntity(
                    new MultipartRequestEntity(parts, filePost.getParams()));


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

            System.out.println("doFilePostToREST output "+output);

            return output;

        }catch(Exception ex){
            throw new RuntimeException(ex);
        }
    }

    public String doFilePostToURL(String url, String id, File f) {
        try{
            HttpClient client = new HttpClient();
            PostMethod filePost = new PostMethod(url);
            filePost.setRequestHeader("Accept", "application/json");
            Part[] parts = {
                new FilePart("file", f)
            };
            filePost.setRequestEntity(
                    new MultipartRequestEntity(parts, filePost.getParams()));

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

            return output;

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }

    public String doPostToURL(String url, String name) {
        try{
            HttpClient client = new HttpClient();
            PostMethod filePost = new PostMethod(url);
            filePost.setRequestHeader("Accept", "application/json");
            Part[] parts = {
                new StringPart("name", name)
            };
            filePost.setRequestEntity(
                    new MultipartRequestEntity(parts, filePost.getParams()));

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

            return output;

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }

    public List<String> getServices(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/containers/" + id +"/services/");

            String output = getOutputFromURL(getresourcesurl);

            JSONArray arr = new JSONArray(output);

            //JSONArray arr = ob.getJSONArray("dataservice_set");

            ArrayList<String> ids = new ArrayList<String>();

            if(arr.length()>0){
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject jsonob = arr.getJSONObject(i);
                    String serviceid = jsonob.getString("id");
                    ids.add(serviceid);
                }
            }

            return ids;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public JSONObject getMFileInfo(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/mfiles/" + id +"/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob = new JSONObject(output);

            return ob;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public JSONObject getServiceInfo(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/services/" + id +"/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob = new JSONObject(output);

            return ob;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public JSONObject getContainerInfo(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/containers/"+id+"/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob = new JSONObject(output);

            return ob;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public List<String> getContainers() {
        try {
            URL getresourcesurl = new URL(protocol + host + "/containers/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob  = new JSONObject(output);

            JSONArray arr = ob.getJSONArray("containers");

            ArrayList<String> ids = new ArrayList<String>();
            if(arr.length()>0){
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject jsonob = arr.getJSONObject(i);
                    ids.add(jsonob.getString("id"));
                }
            }
            return ids;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public List<String> getMFiles(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/services/" + id +"/mfiles/");

            String output = getOutputFromURL(getresourcesurl);

            JSONArray arr  = new JSONArray(output);

            //JSONArray arr = ob.getJSONArray("mfile_set");

            ArrayList<String> ids = new ArrayList<String>();
            if(arr.length()>0){
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject jsonob = arr.getJSONObject(i);
                    ids.add(jsonob.getString("id"));
                }
            }
            return ids;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public String doPostToURL(URL url, String content) {
        try {

            URLConnection connection;
            DataOutputStream printout;
            DataInputStream input;
            // URL of CGI-Bin script.
            // URL connection channel.
            connection = url.openConnection();
            // Let the run-time system (RTS) know that we want input.
            connection.setDoInput(true);
            // Let the RTS know that we want to do output.
            connection.setDoOutput(true);
            // No caching, we want the real thing.
            connection.setUseCaches(false);
            // Specify the content type.
            connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
            connection.setRequestProperty("Accept", "application/json");
            // Send POST output.
            printout = new DataOutputStream(connection.getOutputStream());
            printout.writeBytes(content);
            printout.flush();
            printout.close();
            // Get response data.
            input = new DataInputStream(connection.getInputStream());
            String output = "";
            String str;
            while (null != ((str = input.readLine()))) {
                output += str;
            }
            input.close();
            return output;

        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            ex.printStackTrace();
            throw new RuntimeException(ex);
        }
    }

    private String getOutputFromURL(URL url) {
        try {

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

            return output;

        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public boolean deleteContainer(String containerid) {
        try{

            String url = new String(protocol + host + "/containers/"+containerid+"/");

            HttpClient client = new HttpClient();
            DeleteMethod filePost = new DeleteMethod(url);
            filePost.setRequestHeader("Accept", "application/json");

            int result = client.executeMethod(filePost);

            filePost.releaseConnection();

            if(result != 204){
                throw new RuntimeException("Response from DELETE request for container was not 204, but was '"+result+"' ");
            }else{
                return true;
            }

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }
    public boolean deleteService(String serviceid) {
        try{

            String url = new String(protocol + host + "/services/"+serviceid+"/");

            HttpClient client = new HttpClient();
            DeleteMethod filePost = new DeleteMethod(url);
            filePost.setRequestHeader("Accept", "application/json");

            int result = client.executeMethod(filePost);

            filePost.releaseConnection();

            if(result != 204){
                throw new RuntimeException("Response from DELETE for service request was not 204, but was '"+result+"'");
            }else{
                return true;
            }

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }

    public boolean deleteMFile(String mfileid) {
        try{

            String url = new String(protocol + host + "/mfiles/"+mfileid+"/");

            HttpClient client = new HttpClient();
            DeleteMethod filePost = new DeleteMethod(url);
            filePost.setRequestHeader("Accept", "application/json");

            int result = client.executeMethod(filePost);

            filePost.releaseConnection();

            System.out.println("delete Mfile "+result);

            if(result != 204){
                throw new RuntimeException("Response from DELETE request fro mfile was not 204, but was '"+result+"'");
            }else{
                return true;
            }

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }

    public String createContainer() {
        if(true){
            return "S05ac6c9b-02e7-419b-a9d9-6b70cc76eafa";
        }
        try{
            String name = "ContainerFromJava ";

            String url = this.protocol + this.host + "/containers/";

            String output = doPostToURL(url, name );

            JSONObject ob = new JSONObject(output);

            //return  ob.getString("id");

            return "S05ac6c9b-02e7-419b-a9d9-6b70cc76eafa";

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public void getContainerManagedResources(String id) {
        getManagedResources(id);
    }
    public void getServiceManagedResources(String id) {
        getManagedResources(id);
    }
    public void getMFileManagedResources(String id) {
        getManagedResources(id);
    }

    public void getManagedResources(String id) {
      try {
            URL getresourcesurl = new URL(protocol + host + "/api/" + id +"/getmanagedresources/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob  = new JSONObject(output);

            System.out.println("getManaged Resources result='"+ob+"'");
            System.out.println("Report Number "+ob.getString("reportnum"));

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public JSONArray getContainerUsageSummary(String id) {
      return getUsageSummary(id,"containers");
    }
    public JSONArray getServiceUsageSummary(String id) {
      return getUsageSummary(id,"services");
    }
    public JSONArray getMFileUsageSummary(String id) {
      return getUsageSummary(id,"mfiles");
    }

    public JSONArray getUsageSummary(String id,String type) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/"+type+"/" + id +"/usages/");

            String output = getOutputFromURL(getresourcesurl);

            JSONArray usages_arr  = new JSONArray(output);

            if(usages_arr.length()>0){
                for (int i = 0; i < usages_arr.length(); i++) {
                    JSONObject jsonob = usages_arr.getJSONObject(i);
                    System.out.println("Usage "+jsonob);
                }
            }

            return usages_arr;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }
    
    public JSONArray getContainerUsage(String id) {
      return getUsage(id);
    }
    public JSONArray getServiceUsage(String id) {
      return getUsage(id);
    }
    public JSONArray getMFileUsage(String id) {
      return getUsage(id);
    }

    public JSONArray getUsage(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/api/" + id +"/usage/");

            String output = getOutputFromURL(getresourcesurl);

            JSONArray usages_arr  = new JSONArray(output);

            if(usages_arr.length()>0){
                for (int i = 0; i < usages_arr.length(); i++) {
                    JSONObject jsonob = usages_arr.getJSONObject(i);
                    System.out.println("Usage "+jsonob);
                }
            }

            return usages_arr;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }
    
    public JSONArray getContainerRoleInfo(String id) {
      return getRoleInfo(id);
    }
    public JSONArray getServiceRoleInfo(String id) {
      return getRoleInfo(id);
    }
    public JSONArray getMFileRoleInfo(String id) {
      return getRoleInfo(id);
    }

    public JSONArray getRoleInfo(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/api/" + id +"/getroles/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob  = new JSONObject(output);
            
            JSONArray role_arr = ob.getJSONArray("roles");

            if(role_arr.length()>0){
                for (int i = 0; i < role_arr.length(); i++) {
                    JSONObject jsonob = role_arr.getJSONObject(i);
                    System.out.println("Role "+jsonob);
                }
            }

            return role_arr;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public JSONArray getContainerManagementProperty(String id) {
      return getManagementProperty(id,"containers");
    }
    public JSONArray getServiceManagementProperty(String id) {
      return getManagementProperty(id,"services");
    }

    public JSONArray getManagementProperty(String id, String type) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/"+type+"/" + id +"/properties/");

            String output = getOutputFromURL(getresourcesurl);

            JSONArray arr  = new JSONArray(output);

            if(arr.length()>0){
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject jsonob = arr.getJSONObject(i);
                    System.out.println("Management Property "+jsonob);
                }
            }

            return arr;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public JSONArray getContainerAuths(String id) {
      return getAuths(id,"containers");
    }
    public JSONArray getServiceAuths(String id) {
      return getAuths(id,"services");
    }
    public JSONArray getMFileAuths(String id) {
      return getAuths(id,"mfiles");
    }

    public JSONArray getAuths(String id, String type) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/"+type+"/" + id +"/auths/");

            String output = getOutputFromURL(getresourcesurl);

            JSONArray auth_array  = new JSONArray(output);

            if(auth_array.length()>0){
                for (int i = 0; i < auth_array.length(); i++) {
                    JSONObject jsonob = auth_array.getJSONObject(i);
                    System.out.println("Auth "+jsonob);
                }
            }

            return auth_array;

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

}