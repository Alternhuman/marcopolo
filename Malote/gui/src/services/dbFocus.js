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
