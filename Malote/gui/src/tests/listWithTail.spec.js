describe('ListWithTail of strings', function() {

   beforeEach(module('listWithTail'));
   var $scope;
   beforeEach(inject(function($rootScope) {
      $scope = $rootScope.$new();
   }));

   var myList;
   var myListWithTail;
   var ListWithTail;
   beforeEach(inject(function(_ListWithTail_) {
      ListWithTail = _ListWithTail_;

      myList = ['foo'];
      myListWithTail = ListWithTail.envelope($scope, myList, "", function(item) {
         // isBlank function
         return item === "";
      });
   }));

   it('should have one more elment than the inner list', function() {
      expect(myList.length).toEqual(1);
      expect(myListWithTail.length).toEqual(2);
   });

   it('should have "" as its tail', function() {
      expect(myListWithTail[1]).toEqual("");
   });

   it('should proxy values from the inner list', function() {
      expect(myListWithTail[0]).toEqual('foo');
   });

   describe(', when a non-tail item is edited', function() {
      beforeEach(function() {
         myListWithTail[0] = 'bar';
         $scope.$digest();
      });

      it('should retain it', function() {
         expect(myListWithTail[0]).toEqual('bar');
      });

      it('should set values in the inner list', function() {
         expect(myList[0]).toEqual('bar');
      });

      it('should not alter the lengths', function() {
         expect(myList.length).toEqual(1);
         expect(myListWithTail.length).toEqual(2);
      });
   });

   describe(', when the tail is edited', function() {
      beforeEach(function() {
         myListWithTail[1] = 'new element';
         $scope.$digest();
      });

      it('should retain it', function() {
         expect(myListWithTail[1]).toEqual('new element');
      });

      it('should push it to the inner list', function() {
         expect(myList[1]).toEqual('new element');
      });

      it('should enlarge by one', function() {
         expect(myList.length).toEqual(2);
         expect(myListWithTail.length).toEqual(3);
      });
   });

});

describe('ListWithTail of objects', function() {

   beforeEach(module('listWithTail'));
   var $scope;
   beforeEach(inject(function($rootScope) {
      $scope = $rootScope.$new();
   }));

   var myList;
   var myListWithTail;
   var ListWithTail;
   beforeEach(inject(function(_ListWithTail_) {
      ListWithTail = _ListWithTail_;

      myList = [{command: "foo"}];
      myListWithTail = ListWithTail.envelope($scope, myList, {command: ""}, function(item) {
         // isBlank function
         return item.command === "";
      });
   }));

   it('should have one more elment than the inner list', function() {
      expect(myList.length).toEqual(1);
      expect(myListWithTail.length).toEqual(2);
   });

   it('should have the blank object as its tail', function() {
      expect(myListWithTail[1]).toEqual({command: ""});
   });

   it('should proxy values from the inner list', function() {
      expect(myListWithTail[0]).toEqual({command: "foo"});
      expect(myListWithTail[0].command).toEqual("foo");
   });

   describe(', when a non-tail item is edited', function() {
      beforeEach(function() {
         myListWithTail[0].command = 'bar';
         $scope.$digest();
      });

      it('should retain it', function() {
         expect(myListWithTail[0].command).toEqual('bar');
      });

      it('should set values in the inner list', function() {
         expect(myList[0].command).toEqual('bar');
      });

      it('should not alter the lengths', function() {
         expect(myList.length).toEqual(1);
         expect(myListWithTail.length).toEqual(2);
      });
   });

   describe(', when a non-tail item is swapped', function() {
      beforeEach(function() {
         myListWithTail[0] = {command: "bar"};
         $scope.$digest();
      });

      it('should retain the new item', function() {
         expect(myListWithTail[0].command).toEqual('bar');
      });

      it('should update the inner list', function() {
         expect(myList[0].command).toEqual('bar');
      });

      it('should not alter the lengths', function() {
         expect(myList.length).toEqual(1);
         expect(myListWithTail.length).toEqual(2);
      });
   });

   describe(', when the tail is edited', function() {
      beforeEach(function() {
         myListWithTail[1].command = 'new element';
         $scope.$digest();
      });

      it('should retain it', function() {
         expect(myListWithTail[1].command).toEqual('new element');
      });

      it('should enlarge by one', function() {
         expect(myList.length).toEqual(2);
         expect(myListWithTail.length).toEqual(3);
      });

      it('should set values in the inner list', function() {
         expect(myList[1].command).toEqual('new element');
      });

      it('should not keep enlarging after successive $digest calls', function() {
         $scope.$digest();
         expect(myListWithTail.length).toEqual(3);
      });

      it('should put a blank object in the tail', function() {
         expect(myListWithTail[2]).toEqual({command: ""});
      });

      it('should still allow adding more elements', function() {
         myListWithTail[2].command = "new element 2";
         $scope.$digest();

         expect(myList.length).toEqual(3);
         expect(myListWithTail.length).toEqual(4);
         expect(myList[2]).toEqual({command: "new element 2"});
         expect(myListWithTail[3]).toEqual({command: ""});
      });
   });

   describe(', when the tail is swapped', function() {
      beforeEach(function() {
         myListWithTail[1] = {command: 'new element'};
         $scope.$digest();
      });

      it('should retain it', function() {
         expect(myListWithTail[1].command).toEqual('new element');
      });

      it('should set values in the inner list', function() {
         expect(myList[1].command).toEqual('new element');
      });

      it('should have the same object in both lists', function() {
         expect(myListWithTail[1]).toBe(myList[1]);
      });

      it('should enlarge by one', function() {
         expect(myList.length).toEqual(2);
         expect(myListWithTail.length).toEqual(3);
      });
      
      it('should put a blank object in the tail', function() {
         expect(myListWithTail[2]).toEqual({command: ""});
      });

      it('should still allow adding more elements', function() {
         myListWithTail[2] = {command: "new element 2"};
         $scope.$digest();

         expect(myList.length).toEqual(3);
         expect(myListWithTail.length).toEqual(4);
         expect(myList[2]).toEqual({command: "new element 2"});
         expect(myListWithTail[3]).toEqual({command: ""});
      });
   });

   it('should swap penultimate and last elements if the former gets blank', function() {
      var theSameElement = myListWithTail[1];

      myListWithTail[1].command = "foo";
      $scope.$digest();

      expect(myListWithTail.length).toEqual(3);
      expect(myListWithTail[1]).toBe(theSameElement);

      myListWithTail[1].command = "";
      $scope.$digest();

      expect(myListWithTail.length).toEqual(2);
      expect(myListWithTail[1]).toBe(theSameElement);
   });
   
});
/*
   it('should envelop lists of objects', function() {
      var myList = [{command: "foo"}];
      var myListWithTail = ListWithTail.envelop($scope, myList, {command: ""}, function(item) {
         // is Blank function
         return item.command === "";
      });

      // Blank item exists and is object
      expect(myList.length).toEqual(1);
      expect(myListWithTail.length).toEqual(2);
      expect(myListWithTail[1]).toEqual({command: ""});

      // Items in the list with tail are the same as those of the inner list
      expect(myListWithTail[0]).toEqual(myList[0]);

      // Editing items in the list with tail alters items in the inner list
      myListWithTail[0].command = "bar";
      expect(myListWithTail[0].command).toEqual("bar");
      expect(myList[0].command).toEqual("bar");
      expect(myListWithTail.length).toEqual(2);

      // Replacing items in the list with tail replaces them in the inner list
   });*/

   /* OLD CODE
   xit('should filter blank elements', function() {
      expect(ListWithTail.clean(['foo', '', 'foo', 'bar', '']))
             .toEqual(['foo', 'foo', 'bar']);
   });

   xit('should append an empty element when the last is written', function() {
      var myList = ['foo', ''];

      myList[1] = 'foo';
      ListWithTail.updateTail(myList, function(i) { return i === ""; }, "");

      expect(myList.length).toEqual(3);
      expect(myList[2]).toEqual('');

      // It should not keep adding if we further edit the same element
      myList[1] = 'foobar';
      ListWithTail.updateTail(myList, function(i) { return i === ""; }, "");
      expect(myList.length).toEqual(3);
   });

   xit('should delete the last element if the previous one gets empty', function() {
      var myList = ['foo', 'bar', ''];

      myList[1] = '';
      ListWithTail.updateTail(myList, function(i) { return i === ""; }, "");

      expect(myList.length).toEqual(2);
      expect(myList[1]).toEqual('');
   });

   xit('should create an empty element is the list is empty', function() {
      var myList = [];

      ListWithTail.updateTail(myList, function(i) { return i === ""; }, "");

      expect(myList.length).toEqual(1);
      expect(myList[0]).toEqual("");
   });
   */
