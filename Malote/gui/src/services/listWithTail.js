angular.module('listWithTail', [])
.factory('ListWithTail', function() {
   var ListWithTail = function($scope, innerList, blankElement, isBlank) {
      var self = this;
      this.$scope = $scope;
      this.innerList = innerList;

      this.numProxies = 0;
      this.indexTail = -1;
      if (typeof(blankElement) == "function") {
         this.blankFactory = blankElement;
      } else {
         var blankElementCopy = angular.copy(blankElement);
         this.blankFactory = function() {
            return angular.copy(blankElement);
         };
      }
      this.tailItem = this.blankFactory();
      this.isBlank = isBlank || function(item) {
         return angular.equal(item, self.blankFactory());
      };

      if (!this.isBlank(this.tailItem)) {
         throw new Error("isBlank() callback returned false for the blank element");
      }

      this.cancelWatch = $scope.$watch(function() {
         self.update();
      });
      this.update();
   };
   Object.defineProperty(ListWithTail.prototype, 'length', {
      get: function() { return this.numProxies + 1; }
   });
   ListWithTail.prototype.update = function() {
      this.updateProperties();
      this.checkTail();
   };
   ListWithTail.prototype.updateProperties = function() {
      this.updateProxies();
      this.updateTail();
   };
   function makeProxyGetter(i) {
      return function() { return this.innerList[i]; };
   }
   function makeProxySetter(i) {
      return function(val) { this.innerList[i] = val; };
   }
   ListWithTail.prototype.updateProxies = function() {
      var oldNumProxies = this.numProxies;
      var newNumProxies = this.innerList.length;
      var i;

      // Delete now unexisting items
      // [0,1,2,3] oldNumProxies = 4
      // [0,1]     newNumProxies = 2
      for (i = oldNumProxies - 1; i >= newNumProxies; i--) {
         delete this[i];
      }

      // Create new items
      // [0,1]     oldNumProxies = 2
      // [0,1,2,3] newNumProxies = 4
      for (i = oldNumProxies; i < newNumProxies; i++) {
         Object.defineProperty(this, i, {
            get: makeProxyGetter(i),
            set: makeProxySetter(i),
            configurable: true
         });
      }

      this.numProxies = newNumProxies;
   };
   ListWithTail.prototype.updateTail = function() {
      // Move the tail to the correct position
      if (this.indexTail != this.numProxies) {
         // Delete the old tail index, if any
         if (this.indexTail != -1 && this.indexTail > this.numProxies) {
            delete this[this.indexTail];
         }

         this.indexTail = this.numProxies;
         Object.defineProperty(this, this.indexTail, {
            get: this.getTail,
            set: this.setTail,
            configurable: true
         });
      }
   };
   ListWithTail.prototype.getTail = function() {
      return this.tailItem;
   };
   ListWithTail.prototype.setTail = function(val) {
      this.tailItem = val;
   };
   ListWithTail.prototype.checkTail = function() {
      function assert(expr) {
         if (!expr) { console.error("Assertion failed"); }
      }
      assert(this[this.length - 1] == this.tailItem);

      if (!this.isBlank(this.tailItem)) {
         this.innerList.push(this.tailItem);
         this.tailItem = this.blankFactory();
         this.updateProperties();
      }

      // If the penultimate item gets blank, swap it for the last (which will be always blank)
      assert(this.length > 0);
      assert(this.isBlank(this[this.length - 1]));
      if (this.length >= 2 &&
          this.isBlank(this[this.length - 2]))
      {
         this.tailItem = this[this.length - 2];
         this.innerList.pop();
         this.updateProperties();
      }
   };

   return {
      envelope: function($scope, innerList, blankElement, isBlankFn) {
         return new ListWithTail($scope, innerList, blankElement, isBlankFn);
      },
   };
});
