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

    private static String protocol = "http://";
    private static String host = "localhost";
    private static File file = new File("/home/mm/Pictures/muppits/DSC_0676.jpg");
    private static File file2 = new File("/home/mm/Pictures/muppits/DSC_0669.jpg");


    public static void main(String[] args) {
        try {
            //deleteStager("7199c292-c39c-4224-8198-e0763fee0b5a");
            deleteStager("2a20f0ec-db1d-4d42-9cfb-55965c017f80");
            deleteStager("97bf19a6-2997-438b-bf02-58606217b32a");

            /*String service = makeServiceREST("a29254f7-eb58-4bbb-8cac-cd134195f739");
            
            sleep();
            
            String stager1 = makeStagerREST(service);
            
            String stager2 = makeStagerURL(service);
            
            sleep();
            
            deleteStager(stager1);
            
            sleep();
            
            deleteStager(stager2);
            
            sleep();
            
            deleteService("ca9078d7-9927-4761-8b40-86eefad90b82");*/


        } catch (Exception ex) {
            Logger.getLogger(APIConsumer.class.getName()).log(Level.SEVERE, null, ex);
        }

    }

    public static void sleep(){
            try{Thread.currentThread().sleep(5000);
            }catch(InterruptedException ie){}
    }
    public static void main2(String[] args) {
        try {

            String path = "/container/";

            URL url = new URL(protocol + host + path);

            String containerid = createContainer(url);

            URL containerurl = new URL(protocol + host + path + containerid);

            String output = getOutputFromURL(containerurl);

            System.out.println("Container " + output);

            JSONObject jsonObject = new JSONObject(output);

            String id = jsonObject.getString("id");

            String serviceid1 = makeServiceREST(id);

            getServices(id);

            String stagerid1 = makeStagerREST(serviceid1);

            System.out.println("New Stager from REST" + stagerid1);

            String emptystagerid1 = makeEmptyStagerREST(serviceid1);
            
            putToEmptyStagerREST(emptystagerid1);
            putToEmptyStagerURL(emptystagerid1);

            System.out.println("New Empty Stager from REST" + emptystagerid1);

            getStagers(serviceid1);

            String serviceid2 = makeServiceREST(id);

            getServices(id);

            String stagerid2 = makeStagerURL(serviceid2);

            getStagers(serviceid2);

            System.out.println("New Stager from URL " + stagerid2);

            deleteStager(stagerid1);
            deleteStager(emptystagerid1);

            try{
              //do what you want to do before sleeping
              Thread.currentThread().sleep(5000);//sleep for 1000 ms
              //do what you want to do after sleeptig
            }
            catch(InterruptedException ie){
                //If this thread was intrrupted by nother thread
            }

            deleteStager(stagerid2);

            deleteService(serviceid1);
            deleteService(serviceid2);

            //deleteContainer(containerid);

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

    public static String putToEmptyStagerURL(String id) throws MalformedURLException {
        try {
            URL url = new URL(protocol + host + "/stagerapi/update/" + id  +"/");
            String json = doFilePutToURL(url.toString(), id, file2);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static String putToEmptyStagerREST(String id) throws MalformedURLException {
        try {
            URL url = new URL(protocol + host + "/stager/");
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
            System.out.println(json);
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

            JSONObject ob = new JSONObject(output);

            System.out.println("Container " + ob);

            return  ob.getString("id");

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }
}
