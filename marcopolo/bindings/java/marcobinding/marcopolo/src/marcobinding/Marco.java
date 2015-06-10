package marcobinding;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashMap;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class Marco {
	private static final int PORT = 1338;
	private static final String ADDR = "127.0.1.1";
	private static final int DEFAULT_TIMEOUT = 2000;
	private static final String DEFAULT_GROUP = "224.0.0.112";
	public static final int TYPE_NULL = 0;
	public static final int TYPE_FALSE = 1;
	public static final int TYPE_TRUE = 2;
	public static final int TYPE_OBJECT = 3;
	public static final int TYPE_ARRAY = 4;
	public static final int TYPE_STRING = 5;
	public static final int TYPE_NUMBER = 6;
	
	public Marco(){
		this.group = DEFAULT_GROUP;
		this.timeout = DEFAULT_TIMEOUT;
	}
	
	public Marco(int timeout, String group){
		this.timeout = timeout;
		this.group = group;
	}
	
	
	public int marco(ArrayList<Node> nodes, int max_nodes, ArrayList<String> exclude, HashMap<String, Parameter> params, int timeout, int retries){
		timeout = timeout > 0 ? timeout : this.timeout;
		byte[] data_recv = new byte[2048];
		
		JSONObject send_object = new JSONObject();
		try{
			send_object.put("Command", "Marco");
		
			send_object.put("max-nodes", max_nodes);
			if(exclude != null){
				JSONArray exclude_arr = new JSONArray(exclude);
				send_object.put("exclude", exclude_arr);
			}
			if(params != null){
				JSONObject params_obj = new JSONObject(params);
				send_object.put("params", params_obj);
			}
			
			send_object.put("timeout", timeout);
			send_object.put("group", this.group);
		}catch(JSONException j){
			return -1;
		}
		DatagramSocket s=null;
		InetAddress addr;
		try{
			s = new DatagramSocket();
			addr = InetAddress.getByName(ADDR);
			s.setSoTimeout((int) (1.4*timeout));
		}catch(SocketException e){
			e.printStackTrace();
			return -1;
		} catch (UnknownHostException e) {
			e.printStackTrace();
			if(s != null) s.close();
			return -1;
		}
		
		byte[] send_object_bytes = send_object.toString().getBytes();
		DatagramPacket dp = new DatagramPacket(send_object_bytes, send_object_bytes.length, addr, PORT);
		
		try {
			s.send(dp);
		} catch (IOException e) {
			e.printStackTrace();
			s.close();
			return -1;
		}
		
		DatagramPacket dp_recv = new DatagramPacket(data_recv, data_recv.length);
		try {
			s.receive(dp_recv);
		} catch (IOException e) {
			e.printStackTrace();
			s.close();
			return -1;
		}
		
		byte[] data_trimmed = new byte[dp_recv.getLength()];
		
		System.arraycopy(dp_recv.getData(), 0, data_trimmed, dp_recv.getOffset(), dp_recv.getLength());
		JSONArray receive_array=null;
		try {
			receive_array = new JSONArray(new String(data_trimmed, "UTF-8"));
		} catch (JSONException | UnsupportedEncodingException e) {
			
			e.printStackTrace();
			s.close();
			return -1;
		}
		
		for (int i = 0; i < receive_array.length(); i++) {
			JSONObject obj = (JSONObject) receive_array.get(i);
			Node n = new Node();
			n.setAddress(obj.getString("Address"));
			JSONObject params_obj = obj.getJSONObject("Params");
			HashMap<String, Parameter> params_map = new HashMap<String, Parameter>();
			String [] names = JSONObject.getNames(params_obj);
			if(names != null && names.length > 0){
				for(String name : JSONObject.getNames(params_obj)){
					Parameter p = new Parameter();
					p.type = induceParameterType(params_obj.get(name));
					p.value = params_obj.get(name).toString();
					params_map.put(name, p);
				}
			}
			
			n.setParams(params_map);
			nodes.add(n);
		}
		
		s.close();
		
		return 0;
	}
	
	public int request_for(ArrayList<Node> nodes, String service, int max_nodes, ArrayList<String> exclude, HashMap<String, Parameter> params, int timeout, int retries){
		timeout = timeout > 0 ? timeout : this.timeout;
		byte[] data_recv = new byte[2048];
		
		if(service == null || service.length() < 1){
			return -1;
		}
		
		JSONObject send_object = new JSONObject();
		try{
			send_object.put("Command", "Request-for");
			send_object.put("Params", service);
			send_object.put("max-nodes", max_nodes);
			if(exclude != null){
				JSONArray exclude_arr = new JSONArray(exclude);
				send_object.put("exclude", exclude_arr);
			}
			if(params != null){
				JSONObject params_obj = new JSONObject(params);
				send_object.put("params", params_obj);
			}
			
			send_object.put("timeout", timeout);
			send_object.put("group", this.group);
		}catch(JSONException j){
			return -1;
		}
		DatagramSocket s=null;
		InetAddress addr;
		try{
			s = new DatagramSocket();
			addr = InetAddress.getByName(ADDR);
			s.setSoTimeout((int) (1.4*timeout));
		}catch(SocketException e){
			e.printStackTrace();
			return -1;
		} catch (UnknownHostException e) {
			e.printStackTrace();
			if(s != null) s.close();
			return -1;
		}
		
		byte[] send_object_bytes = send_object.toString().getBytes();
		DatagramPacket dp = new DatagramPacket(send_object_bytes, send_object_bytes.length, addr, PORT);
		
		try {
			s.send(dp);
		} catch (IOException e) {
			e.printStackTrace();
			s.close();
			return -1;
		}
		
		DatagramPacket dp_recv = new DatagramPacket(data_recv, data_recv.length);
		try {
			s.receive(dp_recv);
		} catch (IOException e) {
			e.printStackTrace();
			s.close();
			return -1;
		}
		
		byte[] data_trimmed = new byte[dp_recv.getLength()];
		
		System.arraycopy(dp_recv.getData(), 0, data_trimmed, dp_recv.getOffset(), dp_recv.getLength());
		JSONArray receive_array=null;
		try {
			receive_array = new JSONArray(new String(data_trimmed, "UTF-8"));
		} catch (JSONException | UnsupportedEncodingException e) {
			
			e.printStackTrace();
			s.close();
			return -1;
		}
		
		for (int i = 0; i < receive_array.length(); i++) {
			JSONObject obj = (JSONObject) receive_array.get(i);
			Node n = new Node();
			n.setAddress(obj.getString("Address"));
			JSONObject params_obj = obj.getJSONObject("Params");
			HashMap<String, Parameter> params_map = new HashMap<String, Parameter>();
			String [] names = JSONObject.getNames(params_obj);
			if(names != null && names.length > 0){
				for(String name : JSONObject.getNames(params_obj)){
					Parameter p = new Parameter();
					p.type = induceParameterType(params_obj.get(name));
					p.value = params_obj.get(name).toString();
					params_map.put(name, p);
				}
			}
			
			n.setParams(params_map);
			nodes.add(n);
		}
		
		s.close();
		
		return 0;
	}
	
	private int timeout=2000;
	private String group="224.0.0.112";
	String kTypeNames[] =  { "Null", "False", "True", "Object", "Array", "String", "Number" };
	
	private static int induceParameterType(Object o){
		if(o == null){
			return TYPE_NULL;
		}
		if(o.getClass().equals(Integer.class) || o.getClass().equals(Float.class)){
			return TYPE_NUMBER;
		}
		if(o.getClass().equals(String.class)){
			return TYPE_STRING;
		}
		if(o.getClass().equals(Boolean.class)){
			if((Boolean) o){
				return TYPE_FALSE;
			}else{
				return TYPE_TRUE;
			}
		}
		
		return -1;
	}
}
