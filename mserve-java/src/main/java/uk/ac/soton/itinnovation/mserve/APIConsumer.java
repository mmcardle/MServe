package uk.ac.soton.itinnovation.mserve;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.methods.DeleteMethod;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.httpclient.methods.PostMethod;
import org.apache.commons.httpclient.methods.PutMethod;
import org.apache.commons.httpclient.methods.multipart.FilePart;
import org.apache.commons.httpclient.methods.multipart.MultipartRequestEntity;
import org.apache.commons.httpclient.methods.multipart.Part;
import org.apache.commons.httpclient.methods.multipart.StringPart;

public class APIConsumer {

    private String protocol = "http://";
    private String host = "localhost";

    public APIConsumer(){}

    public APIConsumer(String protocol,String host){
        this.protocol = protocol;
        this.host = host;
    }

    public String putToEmptyStagerURL(String id, File file) throws MalformedURLException {
        try {
            URL url = new URL(protocol + host + "/stagerapi/update/" + id  +"/");
            String json = doFilePutToURL(url.toString(), id, file);
            System.out.println("putToEmptyStagerURL " + json);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public String putToEmptyStagerREST(String id, File file) throws MalformedURLException {
        try {
            URL url = new URL(protocol + host + "/stager/");
            String json = doFilePutToURL(url.toString(), id, file);
            System.out.println(""+json);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public String makeServiceURL(String id) throws MalformedURLException {
        URL url = new URL(protocol + host + "/containerapi/makeserviceinstance/" + id  +"/");
        String content = "name=ServiceFromJava";
        return makeService(url,id,content);
    }

    public String  makeServiceREST(String id) throws MalformedURLException {
        URL url = new URL(protocol + host + "/service/" );
        String content = "name=ServiceFromJava&cid="+id;
        return makeService(url,id,content);
    }

    public String makeService(URL url, String id, String content) {
        try {

            String output = doPostToURL(url,id, content);

            System.out.println("output =" + output);


            JSONObject ob = new JSONObject(output);

            System.out.println("New Service " + ob);

            return ob.getString("id");


        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public String makeStagerURL(String id, File file) throws MalformedURLException {
        try{
            String url = protocol + host + "/serviceapi/create/" + id  +"/";
            String json = doFilePostToURL(url,id,file);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public String  makeEmptyStagerREST(String id) throws MalformedURLException {
        try {
            String url = new String(protocol + host + "/stager/");
            String json = doFilePostToREST(url, id, null);
            System.out.println("makeEmptyStagerREST output "+json);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public String  makeStagerREST(String id, File file) throws MalformedURLException {
        String url = new String(protocol + host + "/stager/");
        String output = doFilePostToREST(url, id, file);
        try {

            System.out.println("makeStagerREST output "+output);
            //JSONArray arr = new JSONArray(output);
            JSONObject ob = new JSONObject(output);
            return ob.getString("id");
        } catch (JSONException ex) {
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

            return output;

        }catch(IOException ex){
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
            URL getresourcesurl = new URL(protocol + host + "/containerapi/getmanagedresources/" + id +"/-1/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob = new JSONObject(output);

            JSONArray arr = ob.getJSONArray("services");

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

    public JSONObject getStagerInfo(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/stager/" + id +"/");

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
            URL getresourcesurl = new URL(protocol + host + "/service/" + id +"/");

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
            URL getresourcesurl = new URL(protocol + host + "/container/"+id+"/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob  = new JSONObject(output);

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
            URL getresourcesurl = new URL(protocol + host + "/api/getcontainers/");

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

    public List<String> getStagers(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/serviceapi/getmanagedresources/" + id +"/-1/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob  = new JSONObject(output);

            JSONArray arr = ob.getJSONArray("stagers");

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

    public String doPostToURL(URL url, String id, String content) {
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
            throw new RuntimeException(ex);
        }
    }

    public String getOutputFromURL(URL url) {
        try {

            HttpClient client = new HttpClient();
            HttpMethod method = new GetMethod(url.toString());
            method.setRequestHeader("Accept", "application/json");;

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
                throw new RuntimeException("Response is "+method.getStatusText()+" code="+method.getStatusCode());
            }

            return output;

        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public String deleteContainer(String containerid) {
        try{

            String url = new String(protocol + host + "/container/"+containerid+"/");

            HttpClient client = new HttpClient();
            DeleteMethod filePost = new DeleteMethod(url);
            filePost.setRequestHeader("Accept", "application/json");

            int result = client.executeMethod(filePost);

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
    public String deleteService(String serviceid) {
        try{

            String url = new String(protocol + host + "/service/"+serviceid+"/");

            HttpClient client = new HttpClient();
            DeleteMethod filePost = new DeleteMethod(url);
            filePost.setRequestHeader("Accept", "application/json");

            int result = client.executeMethod(filePost);

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

    public String deleteStager(String stagerid1) {
        try{

            String url = new String(protocol + host + "/stager/"+stagerid1+"/");

            HttpClient client = new HttpClient();
            DeleteMethod filePost = new DeleteMethod(url);
            filePost.setRequestHeader("Accept", "application/json");

            int result = client.executeMethod(filePost);

            InputStream stream = filePost.getResponseBodyAsStream();

            BufferedReader buf = new BufferedReader(new InputStreamReader(stream));
            String output = "";
            String str;
            while (null != ((str = buf.readLine()))) {
                output += str;
            }
            System.out.println(output);
            buf.close();
            filePost.releaseConnection();

            return output;

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }

    public String createContainer() {
        try{
            String name = "ContainerFromJava ";

            String url = this.protocol + this.host + "/container/";

            String output = doPostToURL(url, name );

            JSONObject ob = new JSONObject(output);

            return  ob.getString("id");

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public void getContainerUsageReport(String id) {
      try {
            URL getresourcesurl = new URL(protocol + host + "/containerapi/getusagesummary/" + id +"/-1/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob  = new JSONObject(output);

            System.out.println("Report Number "+ob.getString("reportnum"));

            JSONArray inp_arr = ob.getJSONArray("inprogress");

            ArrayList<String> ids = new ArrayList<String>();
            if(inp_arr.length()>0){
                for (int i = 0; i < inp_arr.length(); i++) {
                    JSONObject jsonob = inp_arr.getJSONObject(i);
                    System.out.println("In Progress "+jsonob);
                }
            }

            JSONArray sum_arr = ob.getJSONArray("inprogress");

            if(sum_arr.length()>0){
                for (int i = 0; i < sum_arr.length(); i++) {
                    JSONObject jsonob = sum_arr.getJSONObject(i);
                    System.out.println("In Progress "+jsonob);
                }
            }

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }
}