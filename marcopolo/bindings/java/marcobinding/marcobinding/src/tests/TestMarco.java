package tests;

import org.junit.Test;

import marcobinding.Marco;

/*
 * Reference
 * http://www.vogella.com/tutorials/JUnit/article.html
 * http://zeroturnaround.com/rebellabs/how-to-mock-up-your-unit-test-environment-to-create-alternate-realities/
 * http://www.jmock.org/
 * https://www.google.es/search?client=ubuntu&channel=fs&q=mock+junit&ie=utf-8&oe=utf-8&gfe_rd=cr&ei=iVN3VdyLLNiCVIfKgcgI
 */
public class TestMarco {
	@Test
	public void noConnectionShouldReturnMinusOne(){
		Marco tester = new Marco();
		
		//assertEquals(tester.marco(nodes, max_nodes, exclude, params, timeout, retries));
	}
	
}
