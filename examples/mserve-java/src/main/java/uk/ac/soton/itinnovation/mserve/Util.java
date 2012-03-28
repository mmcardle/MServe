/////////////////////////////////////////////////////////////////////////
//
// © University of Southampton IT Innovation Centre, 2010
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
//	Created for Project :	PrestoPRIME
//
/////////////////////////////////////////////////////////////////////////
//
//
/////////////////////////////////////////////////////////////////////////

package uk.ac.soton.itinnovation.mserve;

/**
 *
 * @author mm
 */
public class Util {

    public static void sleepSeconds(int seconds) {
        sleep(seconds*1000);
    }

    public static void sleep(int millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException ie) {
            throw new RuntimeException(ie);
        }
    }
}
