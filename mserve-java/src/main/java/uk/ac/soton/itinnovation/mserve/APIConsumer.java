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
import org.apache.commons.httpclient.Credentials;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.UsernamePasswordCredentials;
import org.apache.commons.httpclient.auth.AuthScope;
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

    public static void main(String[] args){
        try {
            APIConsumer consumer = new APIConsumer();
            String cid = consumer.createContainer();


            System.out.println("makeServiceURL");
            String sid = consumer.makeServiceURL(cid);
            //String sid = consumer.makeServiceREST(cid);
            String mid = consumer.makeEmptyMFileREST(sid);
            consumer.putToEmptyMFile(mid, new File("/home/mm/Pictures/muppits/DSC_0676.jpg"));
            
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
        }

    }

    public APIConsumer(){}

    public APIConsumer(String protocol,String host){
        this.protocol = protocol;
        this.host = host;
    }

    public String putToEmptyMFile(String id, File file) throws MalformedURLException {
        try {
            URL url = new URL(protocol + host + "/mfile/" + id  +"/");
            String json = doFilePutToURL(url.toString(), id, file);
            System.out.println("putToEmptyMFileURL " + json);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }


    public String makeServiceURL(String id) throws MalformedURLException {
        URL url = new URL(protocol + host + "/containerapi/makeserviceinstance/" + id  +"/");
        String content = "name=ServiceFromJava";
        return makeService(url,content);
    }

    public String  makeServiceREST(String id) throws MalformedURLException {
        URL url = new URL(protocol + host + "/service/" );
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

    public String makeMFileURL(String id, File file) throws MalformedURLException {
        try{
            String url = protocol + host + "/serviceapi/create/" + id  +"/";
            String json = doFilePostToURL(url,id,file);
            JSONObject ob = new JSONObject(json);
            return ob.getString("id");
        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public String  makeEmptyMFileREST(String id) throws MalformedURLException {
        try {
            String url = new String(protocol + host + "/mfile/");
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
        String url = new String(protocol + host + "/mfile/");
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
            URL getresourcesurl = new URL(protocol + host + "/api/" + id +"/getmanagedresources/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob = new JSONObject(output);

            JSONArray arr = ob.getJSONArray("dataservice_set");

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
            URL getresourcesurl = new URL(protocol + host + "/mfile/" + id +"/");

            String output = getOutputFromURL(getresourcesurl);

            JSONArray arr = new JSONArray(output);
            JSONObject ob = arr.getJSONObject(0);

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

            JSONArray arr = new JSONArray(output);
            JSONObject ob = arr.getJSONObject(0);

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

    public List<String> getMFiles(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/api/" + id +"/getmanagedresources/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob  = new JSONObject(output);

            JSONArray arr = ob.getJSONArray("mfile_set");

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

            String url = new String(protocol + host + "/container/"+containerid+"/");

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

            String url = new String(protocol + host + "/service/"+serviceid+"/");

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

            String url = new String(protocol + host + "/mfile/"+mfileid+"/");

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
      return getUsageSummary(id);
    }
    public JSONArray getServiceUsageSummary(String id) {
      return getUsageSummary(id);
    }
    public JSONArray getMFileUsageSummary(String id) {
      return getUsageSummary(id);
    }

    public JSONArray getUsageSummary(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/api/" + id +"/getusagesummary/");

            String output = getOutputFromURL(getresourcesurl);

            JSONObject ob  = new JSONObject(output);

            System.out.println("Report Number "+ob.getString("reportnum"));

            JSONArray usages_arr = ob.getJSONArray("usages");

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
      return getManagementProperty(id);
    }
    public JSONArray getServiceManagementProperty(String id) {
      return getManagementProperty(id);
    }

    public JSONArray getManagementProperty(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/api/" + id +"/getmanagementproperties/");

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
      return getAuths(id);
    }
    public JSONArray getServiceAuths(String id) {
      return getAuths(id);
    }
    public JSONArray getMFileAuths(String id) {
      return getAuths(id);
    }

    public JSONArray getAuths(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/auth/" + id +"/");

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