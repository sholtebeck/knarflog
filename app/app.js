'use strict';

// Declare app level module which depends on views, and components
var knarflog = angular.module('knarflog', []);
knarflog.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/', {
        templateUrl: '../app/rankings.html',
        controller: 'playersController'
      when('/mypicks', {
        templateUrl: '../app/mypicks.html',
        controller: 'picksController'
      }).
      otherwise({
        redirectTo: '/'
      });
  }]);
/* Controllers */  
  knarflog.controller('picksController', ['$scope', '$http',
  function($scope, $http) {
     $http.get('/api/mypicks').success(function(data) {
       $scope.picks = data.picks;
       $scope.pageName = 'mypicks';
   });
    
     $scope.addPlayer = function()
    {
//      alert("adding "+ this.player);
      $http.post("/player/add", { player: this.player })
      .success(function(data, status, headers, config) {
                    if (data.success) {
                          $http.get('/api/mypicks').success(function(data) 
                          {
                            $scope.picks = data.picks
                            });
                            } 
                        }).error(function(data, status, headers, config) {});
    };   
    
    $scope.dropPlayer = function()
    {
//      alert("dropping "+ this.player);
      $http.post("/player/drop", { player: this.player })
      .success(function(data, status, headers, config) {
                    if (data.success) {
                          $http.get('/api/mypicks').success(function(data) 
                          {
                            $scope.picks = data.picks
                            });
                            } 
                        }).error(function(data, status, headers, config) {});
    };
  }]);
  
knarflog.controller('playersController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/rankings').success(function(data) {
      $scope.pageName = 'rankings';
      $scope.headers = data.headers;
      $scope.players = data.players;
      $scope.pickers = data.pickers;
    });
    $http.get('/api/user').success(function(data) {
      $scope.user = data.user;
    });      
    
    $scope.orderProp = '-Points';
    $scope.year = new Date().getFullYear();
  }]);

  