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
