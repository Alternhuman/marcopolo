package marcopolo.binding;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.nio.charset.Charset;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.X509Certificate;
import java.util.ArrayList;
import java.util.List;

import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class Polo{
	private static final String ADDR = "127.0.0.1";
	private static final int PORT = 1390;
	private SSLSocket sslsocket;
	private String responseString = null;
	DataOutputStream os;
	DataInputStream is;
	private int timeout;
	BufferedWriter bufferedwriter;
	BufferedReader reader;

	public Polo() throws UnknownHostException, IOException, KeyManagementException, NoSuchAlgorithmException{
		this(1000);
	}

	public Polo(int timeout) throws UnknownHostException, IOException, NoSuchAlgorithmException, KeyManagementException{
		this.timeout = timeout;
			TrustManager[] trustAllCerts = new TrustManager[] {new X509TrustManager() {
				public java.security.cert.X509Certificate[] getAcceptedIssuers() {
					return null;
				}
				public void checkClientTrusted(X509Certificate[] certs, String authType) {
				}
				public void checkServerTrusted(X509Certificate[] certs, String authType) {
				}
			}
		};
		SSLContext sc = SSLContext.getInstance("SSL");
		sc.init(null, trustAllCerts, new java.security.SecureRandom());
		SSLSocketFactory factory=(SSLSocketFactory) sc.getSocketFactory();
		sslsocket=(SSLSocket) factory.createSocket(InetAddress.getByName(ADDR), PORT);
		
		sslsocket.setSoTimeout(this.timeout);
		os=new DataOutputStream(this.sslsocket.getOutputStream());
		is=new DataInputStream(this.sslsocket.getInputStream());
		//reader = new BufferedReader(new InputStreamReader(this.sslsocket.getInputStream()));
		
	    
		/*
      InputStream inputstream = System.in;
      InputStreamReader inputstreamreader = new InputStreamReader(inputstream);
      BufferedReader bufferedreader = new BufferedReader(inputstreamreader);*/
      
	}

	String publish_service(String service) throws JSONException, PoloException, PoloInternalException{
		return this.publish_service(service, new ArrayList<String>(), false, false);
	}

	String publish_service(String service, List<String> multicast_groups) throws JSONException, PoloException, PoloInternalException{
		return this.publish_service(service, multicast_groups, false, false);
	}

	String publish_service(String service, List<String> multicast_groups, boolean permanent) throws JSONException, PoloException, PoloInternalException{
		return this.publish_service(service, multicast_groups, permanent, false);
	}

	String publish_service(String service, List<String> multicast_groups, boolean permanent, boolean root) throws JSONException, PoloException, PoloInternalException{

		

		///
		JSONObject send_object = new JSONObject();

		String token = this.get_token();

		try{
			send_object.put("Command", "Publish");

			JSONObject args = new JSONObject();

			args.put("token", token);
			args.put("service", service);

			JSONArray json_multicast_groups = new JSONArray((String[]) multicast_groups.toArray(new String[0]));

			args.put("multicast_groups", json_multicast_groups);

			args.put("permanent", permanent);
			args.put("root", root);

			send_object.put("Args", args);

		}catch(JSONException j){
			j.printStackTrace();
		}

		try {
			//this.sslsocket.sendUrgentData(data);
			os.write(send_object.toString().getBytes(Charset.forName("utf-8")));
			os.flush();
			byte[] b = new byte[4096];
			//
			byte[] buffer = new byte[32];
		    System.out.println("Waiting on read");
		    InputStream in = null;
		    in = this.sslsocket.getInputStream();
		    int bytes_read = in.read(buffer);
		    System.out.println("read " + bytes_read + " bytes" );
		    if(bytes_read > 0) {
		        String port_s = new String(buffer, 0, bytes_read, "UTF-8");  
		        System.out.println(port_s);
		        //port_s = port_s.trim();
		        //port_num = Integer.parseInt(port_s);
		    } 
		    else 
		        System.out.println("------Error in call---------");
		    
			//is.readFully(b);
			System.out.println(b);
			//System.err.println(reader.readLine());
			return responseString;
			/*if(responseString != null){
				JSONObject response_obj = new JSONObject(responseString);
				if(response_obj.has("OK")){
					return response_obj.getString("OK");
				}else if(response_obj.has("Error")){
					throw new PoloException(response_obj.getString("Error"));
				}else{
					throw new PoloException("Bad received message");
				}
			}else{
				throw new PoloInternalException("Something is wrong");
			}*/

		} catch (IOException e) {
			e.printStackTrace();
			throw new PoloInternalException("Internal communication error");
		}
		//return "";

	}

	private String get_token(){
		return "";
		//throw new UnsupportedOperationException();
	}

	public void close() throws IOException{
		os.close();
		is.close();
		this.sslsocket.close();
	}
}


/*class Polo{


    std::string publish_service(std::string service, std::vector<std::string> multicast_groups=std::vector<std::string>(), bool permanent=false, bool root=false);
    int unpublish_service(std::string service, std::vector<std::string> multicast_groups=std::vector<std::string>(), bool delete_file=false);
    /*Service service_info(std::string service);
    bool has_service(service);

    int set_permanent(std::string service, bool permanent=true);

    int reload_services();*/

//private:
//    int polo_socket;
//    SSL *wrappedSocket;
//    std::string get_token();
//    std::string request_token(const struct passwd*);
//    int verify_ip(std::string, std::string&);
//    int verify_common_parameters(const std::string service, const std::vector<std::string> multicast_groups, std::string &reason);
//    
//    /*verify_parameters(std::string service, std::vector<std::string> multicast_groups)*/
//};
//
//#endif*/