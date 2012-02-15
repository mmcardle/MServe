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
            System.out.println("Deleting Container "+container);
            consumer.deleteContainer(container);
        }
    }

    @Before public void setUp() {    }

    @After  public void tearDown() {    }

    @Test
    public void testAPI() {
        try {
            System.out.println("testAPI createContainer");

            String containerid = consumer.createContainer();
            System.out.println("Container "+containerid);
            System.out.println("testAPI makeServiceREST");
            String serviceid1 = consumer.makeServiceREST(containerid);
            System.out.println("Service "+serviceid1);
            System.out.println("testAPI getServices");
            consumer.getServices(containerid);
            System.out.println("testAPI makeMFileREST "+serviceid1+" file ");
            String stagerid1 = consumer.makeMFileREST(serviceid1, file);
            System.out.println("testAPI makeEmptyMFileRest");
            String emptystagerid1 = consumer.makeEmptyMFileREST(serviceid1);
            System.out.println("testAPI putToEmptyMFileREST");
            consumer.putToEmptyMFile(stagerid1, file);
            //System.out.println("testAPI putToEmptyMFileURL");
            //consumer.putToEmptyMFile(emptystagerid1, file2);
            System.out.println("testAPI getMFiles");
            consumer.getMFiles(serviceid1);
            System.out.println("testAPI makeServiceREST 2");
            String serviceid2 = consumer.makeServiceREST(containerid);
            System.out.println("testAPI getServices 2");
            consumer.getServices(containerid);
            System.out.println("testAPI makeMFileURL");
            String stagerid2 = consumer.makeMFileREST(serviceid2,file);
            System.out.println("testAPI getMFiles2");
            consumer.getMFiles(serviceid2);
            System.out.println("testAPI deleteMFile");
            consumer.deleteMFile(stagerid1);
            System.out.println("testAPI deleteMFile 2");
            consumer.deleteMFile(emptystagerid1);
            System.out.println("testAPI deleteMFile 3");
            consumer.deleteMFile(stagerid2);
            System.out.println("testAPI deleteService");
            consumer.deleteService(serviceid1);
            System.out.println("testAPI deleteService 2");
            consumer.deleteService(serviceid2);
            System.out.println("testAPI deleteContainer");
            consumer.deleteContainer(containerid);

            System.out.println("Done testAPI");

        } catch (Exception ex) {
            ex.printStackTrace(System.out);
            throw new RuntimeException(ex);
        }
    }
}