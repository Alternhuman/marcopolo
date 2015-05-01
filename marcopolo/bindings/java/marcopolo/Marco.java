package net.martinarroyo.marcopolo;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.util.ArrayList;

public class Marco {
	public static ArrayList<Nodo> getNodeByService(String serviceName){ //public static ArrayList<Nodo> request_for(String service)
		ArrayList<Nodo> nodos = new ArrayList<Nodo>();
		try {
			DatagramSocket s = new DatagramSocket();
			InetAddress a = InetAddress.getByName("127.0.1.1");//getByAddress("127.0.1.1".getBytes());
			DatagramPacket dp = new DatagramPacket(serviceName.getBytes(), serviceName.getBytes().length, a, 1338);
			
			s.send(dp);
			byte[] data = new byte[1024];
			DatagramPacket d = new DatagramPacket(data, 1024);
			s.receive(d);
			//System.out.println(new String(d.getData(), "UTF-8"));
			byte[] datos = new byte[d.getLength()];
			System.arraycopy(d.getData(), 0, datos, d.getOffset(), d.getLength());
			String[] st = new String(datos , "UTF-8").split(",",0);
			//System.out.println(st);
			
			for (String string2 : st) {
				System.out.println(string2);
				Nodo n = new Nodo();
				n.setAddress(string2);
				nodos.add(n);
			}
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		return nodos;
	}
	public static void main(String[] args) {
		getNodeByService("tomcat");
	}
}
