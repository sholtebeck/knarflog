'use strict';

/* Controllers */
var knarflog = angular.module('knarflog', []);
  knarflog.controller('picksController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/mypicks').success(function(data) {
      $scope.picks = data.picks
    });
    
     $scope.addPlayer = function()
    {
//      alert("adding "+ this.player);
      $http.post("/player/add", { player: this.player })
      .success(function(data, status, headers, config) {
                     $scope.message=data.message;
                     if (data.success) {
                          $http.get('/api/mypicks').success(function(data)  {   $scope.picks = data.picks });
                            } 
                        }).error(function(data, status, headers, config) {});
    };   
    
    $scope.dropPlayer = function()
    {
//      alert("dropping "+ this.player);
      $http.post("/player/drop", { player: this.player })
      .success(function(data, status, headers, config) {
                   $scope.message=data.message;
                   if (data.success) {
                           $http.get('/api/mypicks').success(function(data)  {   $scope.picks = data.picks });
                         } 
                        }).error(function(data, status, headers, config) {});
    };
  }]);
  
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

knarflog.controller('resultsController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/results').success(function(data) {
      $scope.results= data.results;
      $scope.pickers = data.pickers;
    });
    
    $scope.orderProp = 'Rank';
  }]);
