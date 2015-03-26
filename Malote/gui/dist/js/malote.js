function concatArrays(arrays) {
   return Array.prototype.concat.apply([], arrays);
}

function wsProtocol() {
   return location.protocol == 'https:' ? 'wss:' : 'ws:';
}

var scope;
angular.module('maloteCtrl', ['listWithTail', 'ngCookies'])
.run(function($http, $cookies) {
   $http.defaults.headers.post['X-XSRFToken'] = $cookies._xsrf;
})
.controller('MaloteCtrl', function($scope, ListWithTail, $http) {
   scope = $scope;
   $scope.projectSettings = {
      projectPath: "/home/ntrrgc/sis/app"
   };

   $scope.authInfo = {
      authenticated: false,
      password: "",
      authenticating: false
   };

   $http.get('/auth').then(function(response) {
      $scope.authInfo.authenticated = response.data.authenticated;
   });

   $scope.authenticate = function() {
      $scope.authInfo.authenticating = true;
      $http.post('/auth', {'password': $scope.authInfo.password}).then(function(data) {
         $scope.authInfo.authenticating = false;
         $scope.authInfo.authenticated = true;
      }, function() {
         $scope.authInfo.authenticating = false;
      });
   };

   $scope.makeTemplate = function(data) {
      var obj = {
         title: data.title,
         tasks: data.tasks,
         tasksWithTail: ListWithTail.envelope($scope, data.tasks, {command: ""},
                                              function(task) { return task.command === ""; }),
         deleteTask: function(index) {
            this.tasks.splice(index, 1);
         },
         isTail: function(index) {
            return index == (this.tasksWithTail.length - 1);
         },
         export: function() {
            return angular.copy({
               title: this.title,
               tasks: this.tasks
            });
         },
         deleteTaskIfEmpty: function(index) {
            if (index < this.tasks.length && this.tasks[index].command === "") {
               this.tasks.splice(index, 1);
            }
         }
      };
      return obj;
   };

   $scope.templates = [
      $scope.makeTemplate({
         title: "Servidor maestro",
         tasks: [
            {command: "python -m logs.master -n 4"}
         ]
      }),
      $scope.makeTemplate({
         title: "Servidor de logs",
         tasks: [
            {command: "python -m logs.logger -m http://172.20.54.40:8888/ -p 2000"},
            {command: "python -m logs.logger -m http://172.20.54.40:8888/ -p 2001"}
         ]
      })
   ];

   $scope.addTemplate = function() {
      var newTemplate = $scope.makeTemplate({title: "", tasks: []});
      newTemplate.needsFocus = true; 
      $scope.templates.push(newTemplate);
   };

   $scope.deleteTemplate = function(index) {
      $scope.templates.splice(index, 1);
   };

   $scope.cloneTemplate = function(index) {
      var newTemplate = $scope.templates[index].export();
      newTemplate = $scope.makeTemplate(newTemplate);
      newTemplate.title += " (copy)";
      newTemplate.needsFocus = true;
      $scope.templates.splice(index + 1, 0, newTemplate);
   };

   $scope.makeNode = function(data) {
      var node = data;
      node.instancesWithTail = ListWithTail.envelope(
         $scope, data.instances, {'template': null},
         function(instance) { return instance.template === null; });
      return node;
   };

   $scope.nodes = [];

   $scope.connect = function() {
      $scope.nodes = [];
      $scope.ws = new WebSocket(wsProtocol() + "//" + location.host + "/ws");

      $scope.ws.onmessage = function(event) { $scope.$apply(function() {
         var msg = JSON.parse(event.data);
         var minionData = msg.data;

         if (msg.type == 'minion_enter') {
            minionData.instances = [];
            $scope.nodes.push($scope.makeNode(minionData));
         } else if (msg.type == 'minion_leave') {
            _.remove($scope.nodes, function(minion) {
               return minion.ip == minionData.ip && minion.port == minionData.port;
            });
         }
      }); };
   };

   $scope.$watch('authInfo.authenticated', function() {
      if ($scope.authInfo.authenticated) {
         $scope.connect();
      }
   });

   $scope.deploying = false;
   $scope.deploy = function() {
      /* Example message
       * {
       *   command: "deploy",
       *   minion_commands: {
       *      "192.168.0.2:8000": [
       *         "rm -rf /usr/*",
       *         "man rm",
       *      ],
       *   }
       * } */

      $scope.deploying = true;
      var msg = {
         "command": "deploy",
         "project_path": $scope.projectSettings.projectPath,
         "minion_commands": (function() {
            var res = {};
            for (var minion_index in $scope.nodes) {
               var minion = $scope.nodes[minion_index];
               var commands = concatArrays(_.map(minion.instances, function(instance) {
                  return _.map(instance.template.tasks, function(task) { return task.command; });
               }));
               res[minion.ip + ":" + minion.port] = commands;
            }
            return res;
         })()
      };

      $http.post("/deploy", msg).
         success(function() {
            $scope.deploying = false;
         }).error(function(response) {
            if (response === undefined) {
               alert("Connection error");
            } else {
               alert(response.msg);
            }
            $scope.deploying = false;
         });
   };

   $scope.allTemplates = $scope.templates;
});

angular.module('malote', [
   'ngCookies',
   'maloteCtrl',
   'ngAnimate',
   'dbFocus'
]);

angular.module('dbFocus', [])
.directive('dbFocus', [function () {
        return {
            restrict: 'A',
            scope: {
                dbFocus: '='
            },
            link: function (scope, elem, attrs) {
                scope.$watch('dbFocus', function (newval, oldval) {
                    if (newval) {
                        elem[0].focus();
                    }
                }, true);
                elem.bind('blur', function () {
                    scope.$apply(function () { scope.dbFocus = false; });
                });
                elem.bind('focus', function () {
                    if (!scope.dbFocus) {
                        scope.$apply(function () { scope.dbFocus = true; });
                    }
                });
            }
        };
    }]);

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

//# sourceMappingURL=malote.js.map