'use strict';

/* Controllers */
var knarflog = angular.module('knarflog', []);
knarflog.controller('playersController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/rankings').success(function(data) {
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

