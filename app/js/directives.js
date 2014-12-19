var knarflog = angular.module('knarflog', []);
knarflog.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/', {
        templateUrl: 'index.html',
        controller: 'PlayerController'
      }).
      when('/mypicks', {
        templateUrl: 'picks.html',
        controller: 'PickController'
      }).
      otherwise({
        redirectTo: '/'
      });
  }]);
  