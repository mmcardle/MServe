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

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package uk.ac.soton.itinnovation.mserve;

import java.awt.Color;
import java.awt.Component;
import java.awt.Container;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.ListCellRenderer;
import javax.swing.ListModel;
import javax.swing.event.ListDataListener;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import org.json.JSONException;
import org.json.JSONObject;

/**
 *
 * @author mm
 */
public class APIGUI extends JFrame {

    APIConsumer consumer;
    DefaultListModel cmodel = new DefaultListModel();
    DefaultListModel smodel = new DefaultListModel();
    DefaultListModel dmodel = new DefaultListModel();
    JList clist = new JList(cmodel);
    JList slist = new JList(smodel);
    JList flist = new JList(dmodel);
    APIGUI apiGUI;
    Map<String, String> nameMap = new HashMap<String, String>();

    public static void main(String args[]) {
        new APIGUI();
    }

    private void setGBC(Component com,
            GridBagLayout gridbag,
            GridBagConstraints c,
            int fill,
            int ipady,
            double weightx,
            double weighty,
            int anchor,
            Insets insets,
            int gridx,
            int gridy,
            int gridwidth) {

        c.fill = fill;
        c.ipady = ipady;       //reset to default
        c.weightx = weighty;   //request any extra vertical space
        c.weighty = weightx;
        c.anchor = anchor; //bottom of space
        c.insets = insets;  //top padding
        c.gridx = gridx;       //aligned with button 2
        c.gridwidth = gridwidth;   //2 columns wide
        c.gridy = gridy;       //third row
        //c.fill = fill;
        //c.ipady = 0;       //reset to default
        //c.weighty = 1.0;   //request any extra vertical space
        //c.anchor = GridBagConstraints.PAGE_END; //bottom of space
        //c.insets = new Insets(10,0,0,0);  //top padding
        //c.gridx = 1;       //aligned with button 2
        //c.gridwidth = 2;   //2 columns wide
        //c.gridy = 2;       //third row
        gridbag.setConstraints(com, c);
    }

    public APIGUI() {
        super("MServe GUI");
        apiGUI = this;
        consumer = new APIConsumer();

        Container contentpane = getContentPane();
        GridBagLayout gridbag = new GridBagLayout();
        GridBagConstraints c = new GridBagConstraints();
        setLayout(gridbag);

        MServeCellRenderer lcr = new MServeCellRenderer();

        clist.setCellRenderer(lcr);
        slist.setCellRenderer(lcr);
        flist.setCellRenderer(lcr);

        JScrollPane cSP = new JScrollPane(clist);
        JScrollPane sSP = new JScrollPane(slist);
        JScrollPane dSP = new JScrollPane(flist);

        JButton refCButton = new JButton("Refresh");

        refCButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                cmodel.clear();
                smodel.clear();
                dmodel.clear();
                CUpdateThread th = new CUpdateThread();
                th.start();
            }
        });

        JButton delCButton = new JButton("Delete Container");
        delCButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                if(clist.isSelectionEmpty()){
                    JOptionPane.showMessageDialog(new JLabel("Nothing Selected"), "Message");
                    return;
                }
                if (JOptionPane.showConfirmDialog(new JLabel("Really Delete"), "Sure?") == JOptionPane.YES_OPTION) {
                    String cid = (String)clist.getSelectedValue();
                    consumer.deleteContainer(cid);
                    cmodel.clear();
                    smodel.clear();
                    dmodel.clear();
                    CUpdateThread th = new CUpdateThread();
                    th.start();
                }
            }
        });

        JButton refSButton = new JButton("Refresh List");
        refSButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                smodel.clear();
                dmodel.clear();
                if(!clist.isSelectionEmpty()){
                    String cid = (String)clist.getSelectedValue();
                    SUpdateThread th = new SUpdateThread(cid);
                    th.start();
                }
            }
        });

        JButton delSButton = new JButton("Delete Service");
        delSButton.addActionListener(new ActionListener() {

            @Override
            public void actionPerformed(ActionEvent ae) {
                if(slist.isSelectionEmpty()){
                    JOptionPane.showMessageDialog(new JLabel("Nothing Selected"), "Message");
                    return;
                }
                if (JOptionPane.showConfirmDialog(new JLabel("Really Delete"), "Sure?") == JOptionPane.YES_OPTION) {
                    String sid = (String) slist.getSelectedValue();
                    consumer.deleteService(sid);
                    if(!clist.isSelectionEmpty()){
                        String cid = (String) clist.getSelectedValue();
                        SUpdateThread th = new SUpdateThread(cid);
                        th.start();
                    }
                }

            }
        });

        JButton refFButton = new JButton("Refresh List");
        refFButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                dmodel.clear();
                if(!slist.isSelectionEmpty()){
                    String sid = (String)slist.getSelectedValue();
                    FUpdateThread th = new FUpdateThread(sid);
                    th.start();
                }
            }
        });

        JButton delFButton = new JButton("Delete File");
        delFButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                if(flist.isSelectionEmpty()){
                    JOptionPane.showMessageDialog(new JLabel("Nothing Selected"), "Message");
                    return;
                }
                if (JOptionPane.showConfirmDialog(new JLabel("Really Delete"), "Sure?") == JOptionPane.YES_OPTION) {
                    String fid = (String)flist.getSelectedValue();
                    consumer.deleteMFile(fid);
                    if(!slist.isSelectionEmpty()){
                        String sid = (String)slist.getSelectedValue();
                        FUpdateThread th = new FUpdateThread(sid);
                        th.start();
                    }
                }
            }
        });

        setGBC(cSP, gridbag, c, GridBagConstraints.BOTH, 0, 1.0, 1.0, GridBagConstraints.CENTER, new Insets(0, 0, 0, 0), 0, 0, 2);
        setGBC(sSP, gridbag, c, GridBagConstraints.BOTH, 0, 1.0, 1.0, GridBagConstraints.CENTER, new Insets(0, 0, 0, 0), 2, 0, 2);
        setGBC(dSP, gridbag, c, GridBagConstraints.BOTH, 0, 1.0, 1.0, GridBagConstraints.CENTER, new Insets(0, 0, 0, 0), 4, 0, 2);

        setGBC(refCButton, gridbag, c, GridBagConstraints.NONE, 0, 1.0, 1.0, GridBagConstraints.CENTER, new Insets(0, 0, 0, 0), 0, 1, 1);
        setGBC(delCButton, gridbag, c, GridBagConstraints.NONE, 0, 1.0, 1.0, GridBagConstraints.CENTER, new Insets(0, 0, 0, 0), 1, 1, 1);
        setGBC(refSButton, gridbag, c, GridBagConstraints.NONE, 0, 1.0, 1.0, GridBagConstraints.CENTER, new Insets(0, 0, 0, 0), 2, 1, 1);
        setGBC(delSButton, gridbag, c, GridBagConstraints.NONE, 0, 1.0, 1.0, GridBagConstraints.CENTER, new Insets(0, 0, 0, 0), 3, 1, 1);
        setGBC(refFButton, gridbag, c, GridBagConstraints.NONE, 0, 1.0, 1.0, GridBagConstraints.CENTER, new Insets(0, 0, 0, 0), 4, 1, 1);
        setGBC(delFButton, gridbag, c, GridBagConstraints.NONE, 0, 1.0, 1.0, GridBagConstraints.CENTER, new Insets(0, 0, 0, 0), 5, 1, 1);

        add(cSP);
        add(sSP);
        add(dSP);
        add(refCButton);
        add(delCButton);
        add(refSButton);
        add(delSButton);
        add(refFButton);
        add(delFButton);

        clist.addListSelectionListener(new CListSelectionListener());
        slist.addListSelectionListener(new SListSelectionListener());

        this.setSize(640, 480);
        this.pack();
        this.setVisible(true);
        this.setLocationRelativeTo(null);
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        CUpdateThread th = new CUpdateThread();

        th.start();
    }

    class MServeCellRenderer extends JLabel implements ListCellRenderer {

        public MServeCellRenderer() {
            super();
            this.setOpaque(true);
        }

        @Override
        public Component getListCellRendererComponent(JList jlist, Object o, int i, boolean isSelected, boolean hasFocus) {
            String name = o.toString();
            if (nameMap.containsKey(o.toString())) {
                name = nameMap.get(o.toString());
            }
            setText(name);
            setBackground(isSelected ? new Color(225, 225, 225) : Color.white);
            setForeground(isSelected ? Color.red : Color.black);
            return this;

        }
    }

    public class CUpdateThread extends Thread {

        private CUpdateThread() {
        }

        @Override
        public void run() {
            List<String> containers = consumer.getContainers();
            for (String c : containers) {
                try {
                    int pos = clist.getModel().getSize();
                    JSONObject ob = consumer.getContainerInfo(c);
                    nameMap.put(ob.getString("id"), ob.getString("name"));
                    cmodel.add(pos, c);
                } catch (Exception ex) {
                    throw new RuntimeException(ex);
                }
            }
        }
    }

    public class SUpdateThread extends Thread {

        String con;

        private SUpdateThread(String container) {
            this.con = container;
        }

        @Override
        public void run() {
            smodel.clear();
            dmodel.clear();
            List<String> services = consumer.getServices(con);
            for (String s : services) {
                try {
                    int pos = slist.getModel().getSize();
                    JSONObject ob = consumer.getServiceInfo(s);
                    nameMap.put(ob.getString("id"), ob.getString("name"));

                    smodel.add(pos, s);
                } catch (Exception ex) {
                    throw new RuntimeException(ex);
                }
            }
        }
    }

    public class FUpdateThread extends Thread {

        String service;

        private FUpdateThread(String service) {
            this.service = service;
        }

        @Override
        public void run() {
            dmodel.clear();
            List<String> stagers = consumer.getMFiles(service);
            for (String d : stagers) {
                try {
                    int pos = flist.getModel().getSize();
                    JSONObject ob = consumer.getMFileInfo(d);
                    nameMap.put(ob.getString("id"), ob.getString("name"));

                    dmodel.add(pos, ob.getString("id"));
                } catch (JSONException ex) {
                    throw new RuntimeException(ex);
                }
            }
        }
    }

    class CListSelectionListener implements ListSelectionListener {

        @Override
        public void valueChanged(ListSelectionEvent e) {
            if (e.getValueIsAdjusting() == false) {
                int i = e.getFirstIndex();
                if(i!=-1 && i<cmodel.getSize()){
                    String container = (String) cmodel.getElementAt(i);
                    SUpdateThread th = new SUpdateThread(container);
                    th.start();
                }
            }
        }
    }

    class SListSelectionListener implements ListSelectionListener {

        @Override
        public void valueChanged(ListSelectionEvent e) {
            if (e.getValueIsAdjusting() == false) {
                System.out.print(e.getSource());
                int i = e.getFirstIndex();
                if(i!=-1 && i<smodel.getSize()){
                    String service = (String) smodel.getElementAt(i);
                    FUpdateThread th = new FUpdateThread(service);
                    th.start();
                }
            }
        }
    }
}
