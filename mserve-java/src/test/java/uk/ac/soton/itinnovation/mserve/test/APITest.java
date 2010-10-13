/////////////////////////////////////////////////////////////////////////
//
//  University of Southampton IT Innovation Centre, 2010
//
// Copyright in this library belongs to the University of Southampton
// University Road, Highfield, Southampton, UK, SO17 1BJ
//
// This software may not be used, sold, licensed, transferred, copied
// or reproduced in whole or in part in any manner or form or in or
// on any media by any person other than in accordance with the terms
// of the Licence Agreement supplied with the software, or otherwise
// without the prior written consent of the copyright owners.
//
// This software is distributed WITHOUT ANY WARRANTY, without even the
// implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
// PURPOSE, except where stated in the Licence Agreement supplied with
// the software.
//
//	Created By :			Mark McArdle
//	Created Date :			02-Jul-2009
//	Created for Project :
//
/////////////////////////////////////////////////////////////////////////
//
//
/////////////////////////////////////////////////////////////////////////
//
//	Last commit info    :   $ $
//                          $ $
//                          $ $
//
/////////////////////////////////////////////////////////////////////////

package uk.ac.soton.itinnovation.mserve.test;

import java.io.File;
import java.util.ArrayList;
import junit.framework.Test;
import uk.ac.soton.itinnovation.mserve.APIConsumer;
import uk.ac.soton.itinnovation.mserve.Util;

public class APITest {

    public void testAPI() {
        try {

            APIConsumer consumer = new APIConsumer("http://", "localhost");
            File file = new File("/home/mm/Pictures/muppits/DSC_0676.jpg");
            File file2 = new File("/home/mm/Pictures/muppits/DSC_0669.jpg");
            String containerid = consumer.createContainer();
            String serviceid1 = consumer.makeServiceREST(containerid);
            consumer.getServices(containerid);
            String stagerid1 = consumer.makeStagerREST(serviceid1, file);
            String emptystagerid1 = consumer.makeEmptyStagerREST(serviceid1);
            consumer.putToEmptyStagerREST(emptystagerid1,file);
            consumer.putToEmptyStagerURL(emptystagerid1, file2);
            consumer.getStagers(serviceid1);
            String serviceid2 = consumer.makeServiceREST(containerid);
            consumer.getServices(containerid);
            String stagerid2 = consumer.makeStagerURL(serviceid2,file);
            consumer.getStagers(serviceid2);
            consumer.deleteStager(stagerid1);
            consumer.deleteStager(emptystagerid1);
            consumer.deleteStager(stagerid2);
            consumer.deleteService(serviceid1);
            consumer.deleteService(serviceid2);
            consumer.deleteContainer(containerid);

        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }

    public void testHostingContainer() {
        try {

            APIConsumer consumer = new APIConsumer("http://", "localhost");
            String containerid = consumer.createContainer();
            consumer.deleteContainer(containerid);

        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }

    public void testServices() {
        try {

            APIConsumer consumer = new APIConsumer("http://", "localhost");
            String containerid = consumer.createContainer();
            String serviceid1 = consumer.makeServiceREST(containerid);
            consumer.getServices(containerid);
            consumer.deleteService(serviceid1);
            consumer.deleteContainer(containerid);

        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }

    public void testStagersRest() {
        try {

            APIConsumer consumer = new APIConsumer("http://", "localhost");
            File file = new File("/home/mm/Pictures/muppits/DSC_0676.jpg");
            String containerid = consumer.createContainer();
            String serviceid1 = consumer.makeServiceREST(containerid);
            consumer.getServices(containerid);
            String stagerid1 = consumer.makeStagerREST(serviceid1, file);
            String emptystagerid1 = consumer.makeEmptyStagerREST(serviceid1);
            consumer.putToEmptyStagerREST(emptystagerid1,file);
            consumer.getStagers(serviceid1);
            String serviceid2 = consumer.makeServiceREST(containerid);
            consumer.getServices(containerid);
            consumer.getStagers(serviceid2);
            consumer.deleteStager(stagerid1);
            consumer.deleteStager(emptystagerid1);
            consumer.deleteService(serviceid1);
            consumer.deleteService(serviceid2);
            consumer.deleteContainer(containerid);

        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }

    public void testStagersStress() {
        try {

            APIConsumer consumer = new APIConsumer("http://", "localhost");
            File file = new File("/home/mm/Pictures/muppits/DSC_0676.jpg");
            String containerid = consumer.createContainer();
            String serviceid1 = consumer.makeServiceREST(containerid);

            ArrayList<String> stagers = new ArrayList<String>();

            for(int i=0; i< 100; i++){
                stagers.add(consumer.makeStagerREST(serviceid1, file));
            }

            for(String stager : stagers){
                consumer.deleteStager(stager);
            }

            consumer.getStagers(serviceid1);
            consumer.deleteService(serviceid1);
            consumer.deleteContainer(containerid);

        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }

}
