package marcopolo.binding;

import java.io.IOException;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Map.Entry;

import org.json.JSONException;

public class Main {
	public static void main(String[] args){
		Polo p = null;
		try {
			p = new Polo(0);
		} catch (IOException | KeyManagementException | NoSuchAlgorithmException e) {
			e.printStackTrace();
		}
		try {
			System.out.println(p.publish_service("hola"));
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (PoloException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (PoloInternalException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	public static void main2(String[] args) {
		Marco m = new Marco();
		ArrayList<Node> nodes = new ArrayList<Node>();
		
		m.request_for(nodes, "marcobootstrap2", 0, null, null, 0, 0);
		nodes.clear();
		
		if(-1 == m.marco(nodes, 0, null, null, 0, 0)){
			System.out.println("Error");
			return;
		}
		
		for(Node n : nodes){
			System.out.println(n.getAddress());
			Iterator<Entry<String, Parameter>> it = n.getParams().entrySet().iterator();
			while(it.hasNext()){
				Entry<String, Parameter> pair = it.next();
				
				if(((Parameter)pair.getValue()).type == Marco.TYPE_STRING){
					System.out.println(pair.getKey() + ":"+((Parameter)pair.getValue()).value);
				}
			}
		}

	}

}
