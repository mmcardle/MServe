package uk.ac.soton.itinnovation.mserve;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class APIConsumer {

    private static String protocol = "http://";
    private static String host = "localhost:8000";

    public static void main(String[] args) {
        try {

            String path = "/container/";
            String resource = "607cd87c-2b4d-4010-8530-b8311f97ddcd";
            URL containerurl = new URL(protocol + host + path + resource);

            String output = getOutputFromURL(containerurl);

            System.out.println("Container "+output);

            JSONObject jsonObject = new JSONObject(output);

            String id = jsonObject.getString("id");

            getServices(id);

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static void getServices(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/containerapi/getmanagedresources/" + id);

            String output = getOutputFromURL(getresourcesurl);

            JSONArray arr = new JSONArray(output);

            for(int i=0 ; i<arr.length() ; i++){
                JSONObject ob = arr.getJSONObject(i);
                System.out.println("Service "+ob);
                String serviceid = ob.getString("pk");
                getStagers(serviceid);
            }

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static void getStagers(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/serviceapi/getmanagedresources/" + id);

            String output = getOutputFromURL(getresourcesurl);

            JSONArray arr = new JSONArray(output);

            for(int i=0 ; i<arr.length() ; i++){
                JSONObject ob = arr.getJSONObject(i);
                System.out.println("Stager "+ob);
            }

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static String getOutputFromURL(URL url){
        try{

            URLConnection connection = url.openConnection();

            connection.setRequestProperty("Accept", "application/json");

            BufferedReader buf = new BufferedReader(new InputStreamReader(connection.getInputStream()));

            String inputLine = "";
            String output = "";

            while ((inputLine = buf.readLine()) != null) {
                output += inputLine;
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
