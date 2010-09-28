package uk.ac.soton.itinnovation.mserve;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
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

            System.out.println("Container " + output);

            JSONObject jsonObject = new JSONObject(output);

            String id = jsonObject.getString("id");

            getServices(id);

            makeServicePOST(id);
            makeServiceREST(id);

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static void makeServicePOST(String id) throws MalformedURLException {
        URL url = new URL(protocol + host + "/containerapi/makeserviceinstance/" + id  +"/");
        makeService(url,id);
    }

    public static void makeServiceREST(String id) throws MalformedURLException {
        URL url = new URL(protocol + host + "/service/" );
        makeService(url,id);
    }

    public static void makeService(URL url, String id) {
        try {
            

            String output = doPostToURL(url,id);

            JSONObject arr = new JSONObject(output);

            System.out.println("New Service " + arr);


        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static void getServices(String id) {
        try {
            URL getresourcesurl = new URL(protocol + host + "/containerapi/getmanagedresources/" + id);

            String output = getOutputFromURL(getresourcesurl);

            JSONArray arr = new JSONArray(output);

            for (int i = 0; i < arr.length(); i++) {
                JSONObject ob = arr.getJSONObject(i);
                System.out.println("Service " + ob);
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
            URL getresourcesurl = new URL(protocol + host + "/serviceapi/getmanagedresources/" + id +"/");

            String output = getOutputFromURL(getresourcesurl);

            JSONArray arr = new JSONArray(output);

            for (int i = 0; i < arr.length(); i++) {
                JSONObject ob = arr.getJSONObject(i);
                System.out.println("Stager " + ob);
            }

        } catch (JSONException ex) {
            throw new RuntimeException(ex);
        } catch (MalformedURLException ex) {
            throw new RuntimeException(ex);
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }
    }

    public static String doPostToURL(URL url, String id) {
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
            String content = "name=ServiceFromJava&cid="+id;
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
