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
    public void testHostingContainer() {

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

            File file = new File("/home/mm/Pictures/muppits/DSC_0676.jpg");
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

            File file = new File("/home/mm/Pictures/muppits/DSC_0676.jpg");
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
        instance.makeService(url, id, content);
    }

    /**
     * Test of makeMFileURL method, of class APIConsumer.
     */
    @Test
    public void testMakeMFileURL() throws Exception {
        System.out.println("makeMFileURL");
        String id = "";
        File file = null;
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.makeMFileURL(id, file);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of makeEmptyMFileREST method, of class APIConsumer.
     */
    @Test
    public void testMakeEmptyMFileREST() throws Exception {
        System.out.println("makeEmptyMFileREST");
        String id = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.makeEmptyMFileREST(id);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of makeMFileREST method, of class APIConsumer.
     */
    @Test
    public void testMakeMFileREST() throws Exception {
        System.out.println("makeMFileREST");
        String id = "";
        File file = null;
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.makeMFileREST(id, file);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of doFilePutToURL method, of class APIConsumer.
     */
    @Test
    public void testDoFilePutToURL() {
        System.out.println("doFilePutToURL");
        String url = "";
        String id = "";
        File f = null;
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.doFilePutToURL(url, id, f);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of doFilePostToREST method, of class APIConsumer.
     */
    @Test
    public void testDoFilePostToREST() {
        System.out.println("doFilePostToREST");
        String url = "";
        String id = "";
        File f = null;
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.doFilePostToREST(url, id, f);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of doFilePostToURL method, of class APIConsumer.
     */
    @Test
    public void testDoFilePostToURL() {
        System.out.println("doFilePostToURL");
        String url = "";
        String id = "";
        File f = null;
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.doFilePostToURL(url, id, f);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of doPostToURL method, of class APIConsumer.
     */
    @Test
    public void testDoPostToURL_String_String() {
        System.out.println("doPostToURL");
        String url = "";
        String name = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.doPostToURL(url, name);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of getServices method, of class APIConsumer.
     */
    @Test
    public void testGetServices() {
        System.out.println("getServices");
        String id = "";
        APIConsumer instance = new APIConsumer();
        List expResult = null;
        List result = instance.getServices(id);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of getMFileInfo method, of class APIConsumer.
     */
    @Test
    public void testGetMFileInfo() {
        System.out.println("getMFileInfo");
        String id = "";
        APIConsumer instance = new APIConsumer();
        JSONObject expResult = null;
        JSONObject result = instance.getMFileInfo(id);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of getServiceInfo method, of class APIConsumer.
     */
    @Test
    public void testGetServiceInfo() {
        System.out.println("getServiceInfo");
        String id = "";
        APIConsumer instance = new APIConsumer();
        JSONObject expResult = null;
        JSONObject result = instance.getServiceInfo(id);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of getContainerInfo method, of class APIConsumer.
     */
    @Test
    public void testGetContainerInfo() {
        System.out.println("getContainerInfo");
        String id = "";
        APIConsumer instance = new APIConsumer();
        JSONObject expResult = null;
        JSONObject result = instance.getContainerInfo(id);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of getContainers method, of class APIConsumer.
     */
    @Test
    public void testGetContainers() {
        System.out.println("getContainers");
        APIConsumer instance = new APIConsumer();
        List expResult = null;
        List result = instance.getContainers();
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of getMFiles method, of class APIConsumer.
     */
    @Test
    public void testGetMFiles() {
        System.out.println("getMFiles");
        String id = "";
        APIConsumer instance = new APIConsumer();
        List expResult = null;
        List result = instance.getMFiles(id);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of doPostToURL method, of class APIConsumer.
     */
    @Test
    public void testDoPostToURL_3args() {
        System.out.println("doPostToURL");
        URL url = null;
        String id = "";
        String content = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.doPostToURL(url, id, content);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of getOutputFromURL method, of class APIConsumer.
     */
    @Test
    public void testGetOutputFromURL() {
        System.out.println("getOutputFromURL");
        URL url = null;
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.getOutputFromURL(url);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
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
    public void testDeleteService() {
        System.out.println("deleteService");
        String serviceid = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        boolean result = instance.deleteService(serviceid);
        assertEquals(true, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of deleteMFile method, of class APIConsumer.
     */
    @Test
    public void testDeleteMFile() {
        System.out.println("deleteMFile");
        String stagerid1 = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        boolean result = instance.deleteMFile(stagerid1);
        assertEquals(expResult, true);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of createContainer method, of class APIConsumer.
     */
    @Test
    public void testCreateContainer() {
        System.out.println("createContainer");
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.createContainer();
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of getContainerUsageReport method, of class APIConsumer.
     */
    @Test
    public void testGetContainerUsageReport() {
        System.out.println("getContainerUsageReport");
        String id = "";
        APIConsumer instance = new APIConsumer();
        instance.getContainerUsageReport(id);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

}