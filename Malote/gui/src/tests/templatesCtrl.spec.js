xdescribe('template controller', function() {
   var $scope;
   beforeEach(module('maloteCtrl'));
   beforeEach(inject(function($rootScope, $controller) {
      $scope = $rootScope.$new();
      $controller('MaloteCtrl', {
         $scope: $scope,
      });
      $scope.templates = [
         $scope.makeTemplate({
            title: "Servidor de logs",
            tasks: [
               {command: "python -m logs.logger -s 192.168.0.2 -p 2000"},
               {command: "python -m logs.logger -s 192.168.0.2 -p 2001"}
            ]
         })
      ];
   }));

   it('should have templates', inject(function($controller) {
      expect($scope.templates[0].title).toEqual("Servidor de logs");
      expect($scope.templates[0].tasksWithTail.length).toEqual(3);
   }));

   it('should add new fields when the last one is written', inject(function() {
      expect($scope.templates[0].tasksWithTail.length).toEqual(3);

      $scope.templates[0].tasksWithTail[2].command = "foo";
      $scope.$digest();
      expect($scope.templates[0].tasksWithTail.length).toEqual(4);

      // It should not enlarge now if we continue editing the same field
      $scope.templates[0].tasksWithTail[2].command = "foobar";
      $scope.$digest();
      expect($scope.templates[0].tasksWithTail.length).toEqual(4);
   }));
});
