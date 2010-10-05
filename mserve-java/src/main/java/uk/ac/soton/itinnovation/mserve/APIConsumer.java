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
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.httpclient.methods.PostMethod;
import org.apache.commons.httpclient.methods.multipart.FilePart;
import org.apache.commons.httpclient.methods.multipart.MultipartRequestEntity;
import org.apache.commons.httpclient.methods.multipart.Part;
import org.apache.commons.httpclient.methods.multipart.StringPart;

public class APIConsumer {

    private static String protocol = "http://";
    private static String host = "localhost:8000";
    private static File file = new File("/home/mm/Pictures/muppits/DSC_0676.jpg");

    public static void main(String[] args) {
        try {

            String path = "/container/";
            String resource = "216be7ae-d6e9-4dce-991b-3d8499cb56b0";
            URL containerurl = new URL(protocol + host + path + resource);

            String output = getOutputFromURL(containerurl);

            System.out.println("Container " + output);

            JSONObject jsonObject = new JSONObject(output);

            String id = jsonObject.getString("id");

            String serviceid1 = makeServiceREST(id);

            getServices(id);

            String stagerid1 = makeStagerREST(serviceid1);

            System.out.println("New Stager from REST" + stagerid1);

            String emptystagerid1 = makeEmptyStagerREST(serviceid1);

            System.out.println("New Empty Stager from REST" + emptystagerid1);

            getStagers(serviceid1);

            String serviceid2 = makeServiceREST(id);

            getServices(id);

            String stagerid2 = makeStagerURL(serviceid2);

            getStagers(serviceid2);

            System.out.println("New Stager from URL " + stagerid2);

            //deleteStager(stagerid1);

            //deleteService(serviceid1);

            //deleteStager(stagerid2);

            //deleteService(serviceid2);

            /*List<String> services = getServices(id);

            for(String serviceid : services){
                printServiceInfo(serviceid);
                List<String> stagerids = getStagers(serviceid);
                if(stagerids.size()>0){
                    System.out.println("REST");
                    System.out.println("====");
                    for(String stagerid : stagerids){
                        printStagerInfo(stagerid);
                    }
                    System.out.println("====");
                }
            }*/
            

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
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
            String url = new String(protocol + host + "/stager/");
            String json = doFilePostToREST(url, id, null);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static String  makeStagerREST(String id) throws MalformedURLException {
        try {
            String url = new String(protocol + host + "/stager/");
            String json = doFilePostToREST(url, id, file);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
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
                System.out.println(str);
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
                System.out.println(str);
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
                System.out.println("Services from /containerapi/getmanagedresources/");
                System.out.println("==================");
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject ob = arr.getJSONObject(i);
                    System.out.println("\t"+ob);
                    String serviceid = ob.getString("pk");
                    ids.add(serviceid);
                }
                System.out.println("==================");
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
            URL getresourcesurl = new URL(protocol + host + "/stager/" + id +"/");

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
                System.out.println("Stagers from /serviceapi/getmanagedresources/");
                System.out.println("==================");
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject ob = arr.getJSONObject(i);
                    System.out.println("Stager  " + ob);
                    ids.add(ob.getString("pk"));
                }
                System.out.println("==================");
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

            InputStream stream = method.getResponseBodyAsStream();

            BufferedReader buf = new BufferedReader(new InputStreamReader(stream));
            String output = "";
            String str;
            while (null != ((str = buf.readLine()))) {
                System.out.println(str);
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
}
