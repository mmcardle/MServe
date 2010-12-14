/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package uk.ac.soton.itinnovation.mserve;

import java.util.ArrayList;
import java.io.File;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
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
    private static APIConsumer consumer;
    private static ArrayList<String> containersToDelete;

    @BeforeClass
    public static void setUpClass() throws Exception {
        consumer = new APIConsumer("http://", "localhost");
        try {
            file = new File(APIConsumer.class.getClassLoader().getResource("test_bird.jpg").toURI());
        } catch (URISyntaxException ex) {
            Logger.getLogger(APIConsumerTest.class.getName()).log(Level.SEVERE, null, ex);
        }
        containersToDelete = new ArrayList<String>();
        files = new String[]{"test_bird.jpg","test_bird.png","test.mp4"};
    }

    @AfterClass
    public static void tearDownClass() throws Exception {
        for(String container : containersToDelete){
            consumer.deleteContainer(container);
        }
    }

    @Before public void setUp() {    }

    @After  public void tearDown() {    }

    /**
     * Test of putToEmptyStagerURL method, of class APIConsumer.
     */
    @Test
    public void testPutToEmptyStagerURL() throws Exception {
        System.out.println("putToEmptyStagerURL");
        String containerid = consumer.createContainer();
        String serviceid1 = consumer.makeServiceREST(containerid);
        String stagerid1 = consumer.makeStagerREST(serviceid1, file);
        consumer.putToEmptyStagerURL(stagerid1, file);
        List<String> stagers = consumer.getStagers(serviceid1);
        consumer.deleteStager(stagerid1);
        consumer.deleteService(serviceid1);
        containersToDelete.add(containerid);
        assertEquals(stagers.size(), 1);
    }

    /**
     * Test of putToEmptyStagerREST method, of class APIConsumer.
     */
    @Test
    public void testPutToEmptyStagerREST() throws Exception {
        System.out.println("putToEmptyStagerREST");
        String containerid = consumer.createContainer();
        String serviceid1 = consumer.makeServiceREST(containerid);
        String stagerid1 = consumer.makeStagerREST(serviceid1, file);
        consumer.putToEmptyStagerREST(stagerid1, file);
        List<String> stagers = consumer.getStagers(serviceid1);
        consumer.deleteStager(stagerid1);
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
        String id = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.makeServiceURL(id);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of makeServiceREST method, of class APIConsumer.
     */
    @Test
    public void testMakeServiceREST() throws Exception {
        System.out.println("makeServiceREST");
        String id = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.makeServiceREST(id);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of makeService method, of class APIConsumer.
     */
    @Test
    public void testMakeService() {
        System.out.println("makeService");
        URL url = null;
        String id = "";
        String content = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.makeService(url, id, content);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of makeStagerURL method, of class APIConsumer.
     */
    @Test
    public void testMakeStagerURL() throws Exception {
        System.out.println("makeStagerURL");
        String id = "";
        File file = null;
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.makeStagerURL(id, file);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of makeEmptyStagerREST method, of class APIConsumer.
     */
    @Test
    public void testMakeEmptyStagerREST() throws Exception {
        System.out.println("makeEmptyStagerREST");
        String id = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.makeEmptyStagerREST(id);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of makeStagerREST method, of class APIConsumer.
     */
    @Test
    public void testMakeStagerREST() throws Exception {
        System.out.println("makeStagerREST");
        String id = "";
        File file = null;
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.makeStagerREST(id, file);
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
     * Test of getStagerInfo method, of class APIConsumer.
     */
    @Test
    public void testGetStagerInfo() {
        System.out.println("getStagerInfo");
        String id = "";
        APIConsumer instance = new APIConsumer();
        JSONObject expResult = null;
        JSONObject result = instance.getStagerInfo(id);
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
     * Test of getStagers method, of class APIConsumer.
     */
    @Test
    public void testGetStagers() {
        System.out.println("getStagers");
        String id = "";
        APIConsumer instance = new APIConsumer();
        List expResult = null;
        List result = instance.getStagers(id);
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
        String containerid = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.deleteContainer(containerid);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
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
        String result = instance.deleteService(serviceid);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of deleteStager method, of class APIConsumer.
     */
    @Test
    public void testDeleteStager() {
        System.out.println("deleteStager");
        String stagerid1 = "";
        APIConsumer instance = new APIConsumer();
        String expResult = "";
        String result = instance.deleteStager(stagerid1);
        assertEquals(expResult, result);
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