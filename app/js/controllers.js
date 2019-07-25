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
    $http.get('/api/players').success(function(data) {
      $scope.event = data.event;
      $scope.players = data.players;
     });
    $scope.orderProp = 'name';
    $scope.year = new Date().getFullYear();
  }]);

knarflog.controller('rankingsController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/rankings').success(function(data) {
      $scope.headers = data.headers;
      $scope.players = data.players;
      $scope.pickers = data.pickers;
    });
    $http.get('/api/user').success(function(data) {
      $scope.user = data.user;
    });      
   $http.get('/api/weeks').success(function(data) {
      $scope.weeks = data.weeks;
	  $scope.week_id = data.week_id;
      $scope.week = data.weeks[0];
    });         
    $scope.orderProp = '-Points';
    $scope.year = new Date().getFullYear();

	$scope.setWeek = function()
    {
	  $scope.week = this.week;
      $http.get('/api/rankings/'+ $scope.week.week_id ).success(function(data) {
			$scope.headers = data.headers;
			$scope.players = data.players;
			$scope.pickers = data.pickers;
		});
    };

  }]);

knarflog.controller('resultsController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/results').success(function(data) {
      $scope.results= data.results;
      $scope.pickers = data.pickers;
    });
    
   $scope.orderProp = '-Points';
   $http.get('/api/weeks').success(function(data) {
      $scope.weeks = data.weeks;
	  $scope.week_id = data.week_id;
      $scope.week = data.weeks[0];
    });         

	$scope.setWeek = function()
    {
	  $scope.week = this.week;
      $http.get('/api/results/'+ $scope.week.week_id ).success(function(data) {
			$scope.results = data.results;
			$scope.pickers = data.pickers;
		});
    };
	
  }]);

knarflog.controller('weeksController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/weeks').success(function(data) {
      $scope.weeks = data.weeks;
      $scope.last_update = data.last_update;
      $scope.week_no = data.week_no;
    });
    
    $scope.orderProp = '-week_id';
	
	$scope.setWeek = function()
    {
      alert("setting "+ this.week.week_date );
	  $scope.week_id = this.week.week_id;
      $http.post("/api/weeks", { "week_id": $scope.week_id });
    };
  }]);
