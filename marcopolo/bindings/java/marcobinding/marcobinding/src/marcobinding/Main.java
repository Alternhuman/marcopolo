package marcobinding;

import java.util.ArrayList;

public class Main {

	public static void main(String[] args) {
		Marco m = new Marco(2000, "224.0.0.112");
		ArrayList<Node> nodes = new ArrayList<Node>();
		
		m.marco(nodes, 0, null, null, 0, 0);
		
		for(Node n : nodes){
			System.out.println(n.getAddress());
		}

	}

}
