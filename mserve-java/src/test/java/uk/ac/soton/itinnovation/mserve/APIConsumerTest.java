/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package uk.ac.soton.itinnovation.mserve;

import java.util.ArrayList;
import java.io.File;
import java.net.URL;
import java.util.List;
import java.util.UUID;
import org.json.JSONObject;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author mm
 */
public class APIConsumerTest {

    public APIConsumerTest() {
    }

    private static String[] files;
    private static File file;
    private static File file2;
    private static APIConsumer consumer;
    private static ArrayList<String> containersToDelete;

    @BeforeClass
    public static void setUpClass() throws Exception {
        consumer = new APIConsumer("http://", "localhost");
        file = new File(APIConsumer.class.getClassLoader().getResource("test_bird.jpg").toURI());
        file2 = new File(APIConsumer.class.getClassLoader().getResource("test_bird_large.jpg").toURI());
        containersToDelete = new ArrayList<String>();
        files = new String[]{"test_bird.jpg","test_bird_large.jpg","test_bird_large.png","test.mp4"};
    }

    @AfterClass
    public static void tearDownClass() throws Exception {
        for(String container : containersToDelete){
            consumer.deleteContainer(container);
        }
    }

    @Before public void setUp() {    }

    @After  public void tearDown() {    }


    @Test
    public void testAPI() {
        try {
            System.out.println("testAPI");

            String containerid = consumer.createContainer();
            String serviceid1 = consumer.makeServiceREST(containerid);
            consumer.getServices(containerid);
            String stagerid1 = consumer.makeMFileREST(serviceid1, file);
            String emptystagerid1 = consumer.makeEmptyMFileREST(serviceid1);
            consumer.putToEmptyMFileREST(emptystagerid1,file);
            consumer.putToEmptyMFileURL(emptystagerid1, file2);
            consumer.getMFiles(serviceid1);
            String serviceid2 = consumer.makeServiceREST(containerid);
            consumer.getServices(containerid);
            String stagerid2 = consumer.makeMFileURL(serviceid2,file);
            consumer.getMFiles(serviceid2);
            consumer.deleteMFile(stagerid1);
            consumer.deleteMFile(emptystagerid1);
            consumer.deleteMFile(stagerid2);
            consumer.deleteService(serviceid1);
            consumer.deleteService(serviceid2);
            consumer.deleteContainer(containerid);

        } catch (Exception ex) {
            ex.printStackTrace(System.out);
            throw new RuntimeException(ex);
        }
    }

    @Test
    public void testFormats() {
        try {

            String containerid = consumer.createContainer();
            String serviceid1 = consumer.makeServiceREST(containerid);

            for (String f : files) {
                System.out.println(""+f);
                URL url = getClass().getClassLoader().getResource(f);
                File filef = new File(url.toURI());
                String stagerid1 = consumer.makeMFileREST(serviceid1, filef);
                consumer.deleteMFile(stagerid1);
            }

            consumer.deleteService(serviceid1);
            consumer.deleteContainer(containerid);

        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }

    @Test
    public void testServices() {
        try {

            String containerid = consumer.createContainer();
            String serviceid1 = consumer.makeServiceREST(containerid);
            consumer.getServices(containerid);
            consumer.deleteService(serviceid1);
            consumer.deleteContainer(containerid);

        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }
    @Test
    public void testMFilesRest() {
        try {

            String containerid = consumer.createContainer();
            String serviceid1 = consumer.makeServiceREST(containerid);
            consumer.getServices(containerid);
            String stagerid1 = consumer.makeMFileREST(serviceid1, file);
            String emptystagerid1 = consumer.makeEmptyMFileREST(serviceid1);
            consumer.putToEmptyMFileREST(emptystagerid1,file);
            consumer.getMFiles(serviceid1);
            String serviceid2 = consumer.makeServiceREST(containerid);
            consumer.getServices(containerid);
            consumer.getMFiles(serviceid2);
            consumer.deleteMFile(stagerid1);
            consumer.deleteMFile(emptystagerid1);
            consumer.deleteService(serviceid1);
            consumer.deleteService(serviceid2);
            consumer.deleteContainer(containerid);

        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }
   // @Test
    public void testMFilesStress() {
        try {

            String containerid = consumer.createContainer();
            String serviceid1 = consumer.makeServiceREST(containerid);

            ArrayList<String> stagers = new ArrayList<String>();

            for(int i=0; i< 10; i++){
                stagers.add(consumer.makeMFileREST(serviceid1, file));
            }

            for(String stager : stagers){
                consumer.deleteMFile(stager);
            }

            consumer.getMFiles(serviceid1);
            consumer.deleteService(serviceid1);
            consumer.deleteContainer(containerid);

        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }

    /**
     * Test of putToEmptyMFileURL method, of class APIConsumer.
     */
    @Test
    public void testPutToEmptyMFileURL() throws Exception {
        System.out.println("putToEmptyMFileURL");
        String containerid = consumer.createContainer();
        String serviceid1 = consumer.makeServiceREST(containerid);
        String stagerid1 = consumer.makeMFileREST(serviceid1, file);
        consumer.putToEmptyMFileURL(stagerid1, file);
        List<String> stagers = consumer.getMFiles(serviceid1);
        consumer.deleteMFile(stagerid1);
        consumer.deleteService(serviceid1);
        containersToDelete.add(containerid);
        assertEquals(stagers.size(), 1);
    }

    /**
     * Test of putToEmptyMFileREST method, of class APIConsumer.
     */
    @Test
    public void testPutToEmptyMFileREST() throws Exception {
        System.out.println("putToEmptyMFileREST");
        String containerid = consumer.createContainer();
        String serviceid1 = consumer.makeServiceREST(containerid);
        String stagerid1 = consumer.makeMFileREST(serviceid1, file);
        consumer.putToEmptyMFileREST(stagerid1, file);
        List<String> stagers = consumer.getMFiles(serviceid1);
        consumer.deleteMFile(stagerid1);
        consumer.deleteService(serviceid1);
        containersToDelete.add(containerid);
        assertEquals(stagers.size(), 1);
    }

    /**
     * Test of makeServiceURL method, of class APIConsumer.
     */
    @Test
    public void testMakeServiceURL() throws Exception {
        System.out.println("makeServiceURL");
        APIConsumer instance = new APIConsumer();
        String id = instance.createContainer();
        instance.makeServiceURL(id);
        containersToDelete.add(id);
    }

    /**
     * Test of makeServiceREST method, of class APIConsumer.
     */
    @Test
    public void testMakeServiceREST() throws Exception {
        System.out.println("makeServiceREST");
        APIConsumer instance = new APIConsumer();
        String id = instance.createContainer();
        String result = instance.makeServiceREST(id);
        containersToDelete.add(id);
    }

    /**
     * Test of makeService method, of class APIConsumer.
     */
    @Test
    public void testMakeService() throws Exception {
        System.out.println("makeService");
        URL url = new URL("http://" + "localhost" + "/service/" );
        APIConsumer instance = new APIConsumer();
        String id = instance.createContainer();
        String content = "name=ServiceFromJava&cid="+id;
        instance.makeService(url, content);
        containersToDelete.add(id);
    }

    /**
     * Test of makeMFileURL method, of class APIConsumer.
     */
    @Test
    public void testMakeMFileURL() throws Exception {
        System.out.println("makeMFileURL");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        String sid = instance.makeServiceREST(cid);
        instance.makeMFileURL(sid, file);
        containersToDelete.add(cid);
    }

    /**
     * Test of makeEmptyMFileREST method, of class APIConsumer.
     */
    @Test
    public void testMakeEmptyMFileREST() throws Exception {
        System.out.println("makeEmptyMFileREST");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        String sid = instance.makeServiceREST(cid);
        instance.makeEmptyMFileREST(sid);
        containersToDelete.add(cid);
    }

    /**
     * Test of makeMFileREST method, of class APIConsumer.
     */
    @Test
    public void testMakeMFileREST() throws Exception {
        System.out.println("makeMFileREST");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        String sid = instance.makeServiceREST(cid);
        instance.makeMFileREST(sid, file);
        containersToDelete.add(cid);
    }

    /**
     * Test of doFilePutToURL method, of class APIConsumer.
     */
    @Test
    public void testDoFilePutToURL() throws Exception {
        System.out.println("doFilePutToURL");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        String sid = instance.makeServiceREST(cid);
        String url = "http://" + "localhost" + "/mfile/";
        instance.doFilePutToURL(url, sid, file);
        containersToDelete.add(cid);
    }

    /**
     * Test of doFilePostToREST method, of class APIConsumer.
     */
    @Test
    public void testDoFilePostToREST() throws Exception {
        System.out.println("doFilePostToREST");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        String sid = instance.makeServiceREST(cid);
        String url = "http://" + "localhost" + "/mfile/";
        instance.doFilePostToREST(url, sid, file);
        containersToDelete.add(cid);
    }

    /**
     * Test of doFilePostToURL method, of class APIConsumer.
     */
    @Test
    public void testDoFilePostToURL() throws Exception {
        System.out.println("doFilePostToURL");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        String sid = instance.makeServiceREST(cid);
        String url = "http://" + "localhost" + "/mfile/";
        instance.doFilePostToURL(url,sid, file);
        containersToDelete.add(cid);
    }

    /**
     * Test of doPostToURL method, of class APIConsumer.
     */
    @Test
    public void testDoPostToURL_String_String() throws Exception {
        System.out.println("doPostToURL");
        String name = "ContainerFromJava ";
        String url = "http://" + "localhost" + "/container/";
        APIConsumer instance = new APIConsumer();
        String output = instance.doPostToURL(url, name);
        JSONObject ob = new JSONObject(output);
        containersToDelete.add(ob.getString("id"));
    }

    /**
     * Test of getServices method, of class APIConsumer.
     */
    @Test
    public void testGetServices() throws Exception {
        System.out.println("getServices");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        instance.makeServiceREST(cid);
        instance.makeServiceREST(cid);
        List result = instance.getServices(cid);
        assertEquals(result.size(), 2);
        containersToDelete.add(cid);
    }

    /**
     * Test of getMFileInfo method, of class APIConsumer.
     */
    @Test
    public void testGetMFileInfo() throws Exception {
        System.out.println("getMFileInfo");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        String sid = instance.makeServiceREST(cid);
        String mid = instance.makeMFileURL(sid, file);
        JSONObject result = instance.getMFileInfo(mid);
        assertEquals(result.getString("name"), file.getName());
        assertEquals(result.getLong("size"), file.length());
        assertEquals(result.getString("id"), mid);
        assertTrue(result.getString("mimetype").startsWith("image"));
        containersToDelete.add(cid);
    }

    /**
     * Test of getServiceInfo method, of class APIConsumer.
     */
    @Test
    public void testGetServiceInfo() throws Exception {
        System.out.println("getServiceInfo");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        String sid = instance.makeServiceREST(cid);
        JSONObject result = instance.getServiceInfo(sid);
        assertEquals(result.getString("id"), sid);
        containersToDelete.add(cid);
    }

    /**
     * Test of getContainerInfo method, of class APIConsumer.
     */
    @Test
    public void testGetContainerInfo()  throws Exception{
        System.out.println("getContainerInfo");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        JSONObject result = instance.getContainerInfo(cid);
        assertEquals(result.getString("id"), cid);
        containersToDelete.add(cid);
    }

    /**
     * Test of getContainers method, of class APIConsumer.
     */
    @Test
    public void testGetContainers() {
        System.out.println("getContainers");
        APIConsumer instance = new APIConsumer();
        String cid1 = instance.createContainer();
        String cid2 = instance.createContainer();
        List result = instance.getContainers();
        assert(result.contains(cid1));
        assert(result.contains(cid2));
        containersToDelete.add(cid1);
        containersToDelete.add(cid2);
    }

    /**
     * Test of getMFiles method, of class APIConsumer.
     */
    @Test
    public void testGetMFiles() throws Exception {
        System.out.println("getMFiles");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        String sid = instance.makeServiceREST(cid);
        String mid1 = instance.makeMFileURL(sid, file);
        String mid2 = instance.makeMFileURL(sid, file);
        String mid3 = instance.makeMFileURL(sid, file);

        List result = instance.getMFiles(sid);

        assertEquals(3,result.size());
        assert(result.contains(mid1));
        assert(result.contains(mid2));
        assert(result.contains(mid3));

        containersToDelete.add(cid);
    }

    /**
     * Test of doPostToURL method, of class APIConsumer.
     */
    @Test
    public void testDoPostToURL_3args() throws Exception {
        System.out.println("doPostToURL");
        APIConsumer instance = new APIConsumer();
        URL url = new URL("http://" + "localhost" + "/container/");
        String content = "name=ContainerFromJavaTest";
        String output = instance.doPostToURL(url, content);
        JSONObject ob = new JSONObject(output);
        containersToDelete.add(ob.getString("id"));
    }

    /**
     * Test of deleteContainer method, of class APIConsumer.
     */
    @Test
    public void testDeleteContainer() {
        System.out.println("deleteContainer");
        String containerid = consumer.createContainer();
        boolean result = consumer.deleteContainer(containerid);
        assertTrue(result);
    }

    /**
     * Test of deleteService method, of class APIConsumer.
     */
    @Test
    public void testDeleteService() throws Exception{
        System.out.println("deleteService");
        String containerid = consumer.createContainer();
        String serviceid = consumer.makeServiceREST(containerid);
        APIConsumer instance = new APIConsumer();
        boolean result = instance.deleteService(serviceid);
        containersToDelete.add(containerid);
        assert(result);
    }

    /**
     * Test of deleteMFile method, of class APIConsumer.
     */
    @Test
    public void testDeleteMFile() throws Exception {
        System.out.println("deleteMFile");
        String containerid = consumer.createContainer();
        String serviceid = consumer.makeServiceREST(containerid);
        String stagerid1 = consumer.makeMFileREST(serviceid, file);
        boolean result = consumer.deleteMFile(stagerid1);
        containersToDelete.add(containerid);
        assert(result);
    }

    /**
     * Test of createContainer method, of class APIConsumer.
     */
    @Test
    public void testCreateContainer() {
        System.out.println("createContainer");
        APIConsumer instance = new APIConsumer();
        String cid = instance.createContainer();
        containersToDelete.add(cid);
    }

    /**
     * Test of getContainerUsageReport method, of class APIConsumer.
     */
    @Test
    public void testGetContainerUsageReport() {
        System.out.println("getContainerUsageReport");
        APIConsumer instance = new APIConsumer();
        String cid = consumer.createContainer();
        instance.getContainerUsageReport(cid);
        containersToDelete.add(cid);
    }

}