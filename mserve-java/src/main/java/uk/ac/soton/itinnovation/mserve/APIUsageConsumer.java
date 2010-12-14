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
import java.util.Date;
import java.util.List;
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

public class APIUsageConsumer {

    private static String protocol = "http://";
    private static String host = "localhost";
    private static File file = new File("/home/mm/Pictures/muppits/DSC_0676.jpg");
    private static File file2 = new File("/home/mm/Pictures/muppits/DSC_0669.jpg");


    public static void main(String[] args) {
        try {

            String path = "/container/";

            URL url = new URL(protocol + host + path);

            String containerid = "a29254f7-eb58-4bbb-8cac-cd134195f739";

            URL containerurl = new URL(protocol + host + "/containerapi/getusagesummary/"+containerid+"/");

            while(true){
                try{

                    Thread.currentThread().sleep(1000);

                    String usage = getOutputFromURL(containerurl);

                    JSONArray ob = new JSONArray(usage);

                    for(int i =0; i< ob.length(); i++){
                      System.out.println(ob.get(i));
                    }

                }
                catch(InterruptedException ie){
                    //If this thread was intrrupted by nother thread
                }catch(JSONException ex){

                }
            }



        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static void main2(String[] args) {
        try {

            String path = "/container/";

            URL url = new URL(protocol + host + path);

            String containerid = createContainer(url);

            URL containerurl = new URL(protocol + host + "/containerapi/getusagesummary/"+containerid+"/");

            int n = 0;
            while(n<10){
                try{

                    String service = makeServiceURL(containerid);

                    String stager = makeStagerURL(service);

                    Thread.currentThread().sleep(10000);

                    deleteStager(stager);
                    deleteService(service);

                    String usage = getOutputFromURL(containerurl);


                    

                    n++;

                }
                catch(InterruptedException ie){
                    //If this thread was intrrupted by nother thread
                }
            }
            

            
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static String putToEmptyStagerURL(String id) throws MalformedURLException {
        try {
            URL url = new URL(protocol + host + "/mfileapi/update/" + id  +"/");
            String json = doFilePutToURL(url.toString(), id, file2);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static String putToEmptyStagerREST(String id) throws MalformedURLException {
        try {
            URL url = new URL(protocol + host + "/mfile/");
            String json = doFilePutToURL(url.toString(), id, file2);
            System.out.println(""+json);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static String makeServiceURL(String id) throws MalformedURLException {
        URL url = new URL(protocol + host + "/containerapi/makeserviceinstance/" + id  +"/");
        String content = "name=ServiceFromJava";
        return makeService(url,id,content);
    }

    public static String  makeServiceREST(String id) throws MalformedURLException {
        URL url = new URL(protocol + host + "/service/" );
        String content = "name=ServiceFromJava&cid="+id;
        return makeService(url,id,content);
    }

    public static String makeService(URL url, String id, String content) {
        try {
            
            String output = doPostToURL(url,id, content);

            JSONObject ob = new JSONObject(output);

            System.out.println("New Service " + ob);

            return ob.getString("id");


        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }
    
    public static String makeStagerURL(String id) throws MalformedURLException {
        try{
            String url = protocol + host + "/serviceapi/create/" + id  +"/";
            String json = doFilePostToURL(url,id,file);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static String  makeEmptyStagerREST(String id) throws MalformedURLException {
        try {
            String url = new String(protocol + host + "/mfile/");
            String json = doFilePostToREST(url, id, null);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static String  makeStagerREST(String id) throws MalformedURLException {
        try {
            String url = new String(protocol + host + "/mfile/");
            String json = doFilePostToREST(url, id, file);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static String doFilePutToURL(String url, String id, File f) {
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

    public static String doFilePostToREST(String url, String id, File f) {
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

    public static String doFilePostToURL(String url, String id, File f) {
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

    public static String doPostToURL(String url, String name) {
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

    public static List<String> getServices(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/containerapi/getmanagedresources/" + id);

            String output = getOutputFromURL(getresourcesurl);

            JSONArray arr = new JSONArray(output);

            ArrayList<String> ids = new ArrayList<String>();

            if(arr.length()>0){
                //System.out.println("Services from /containerapi/getmanagedresources/");
                //System.out.println("==================");
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject ob = arr.getJSONObject(i);
                    //System.out.println("\t"+ob);
                    String serviceid = ob.getString("pk");
                    ids.add(serviceid);
                }
                //System.out.println("==================");
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

    public static void printStagerInfo(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/mfile/" + id +"/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob = new JSONObject(output);

            System.out.println("Stager " + ob);

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static void printServiceInfo(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/service/" + id +"/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob = new JSONObject(output);

            System.out.println("Service " + ob);

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static List<String> getStagers(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/serviceapi/getmanagedresources/" + id +"/");

            String output = getOutputFromURL(getresourcesurl);

            JSONArray arr = new JSONArray(output);

            ArrayList<String> ids = new ArrayList<String>();
            if(arr.length()>0){
                //System.out.println("Stagers from /serviceapi/getmanagedresources/");
                //System.out.println("==================");
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject ob = arr.getJSONObject(i);
                    //System.out.println("Stager  " + ob);
                    ids.add(ob.getString("pk"));
                }
                //System.out.println("==================");
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


    public static String doPostToURL(URL url, String id, String content) {
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
                System.out.println(str);
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

    public static String getOutputFromURL(URL url) {
        try {

            HttpClient client = new HttpClient();
            HttpMethod method = new GetMethod(url.toString());
            method.setRequestHeader("Accept", "application/json");;

            client.executeMethod(method);

            if(method.getStatusCode()!=200){
                throw new RuntimeException("Response is "+method.getStatusText()+" code="+method.getStatusCode());
            }

            InputStream stream = method.getResponseBodyAsStream();

            BufferedReader buf = new BufferedReader(new InputStreamReader(stream));
            String output = "";
            String str;
            while (null != ((str = buf.readLine()))) {
                output += str;
            }
            buf.close();
            return output;

        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    private static String deleteContainer(String containerid) {
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

            System.out.println("Delete Container " + containerid + " result="+result);

            return output;

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }
    private static String deleteService(String serviceid) {
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

            System.out.println("Delete Service " + serviceid + " result="+result);

            return output;

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }

    private static String deleteStager(String stagerid1) {
        try{

            String url = new String(protocol + host + "/mfile/"+stagerid1+"/");

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

            System.out.println("Delete Stager " + stagerid1 + " result="+result);

            return output;

        }catch(IOException ex){
            throw new RuntimeException(ex);
        }
    }

    private static String createContainer(URL url) {
        try{
            Date now = new Date();
            String name = "ContainerFromJava ";

            String output = doPostToURL(url.toString(), name );

            System.out.println("Output " + output);

            JSONObject ob = new JSONObject(output);

            System.out.println("Container " + ob);

            return  ob.getString("id");

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }
}
