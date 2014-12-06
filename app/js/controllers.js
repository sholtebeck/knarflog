'use strict';

/* Controllers */
var knarflog = angular.module('knarflog', []);
knarflog.controller('playersController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('rankings.json').success(function(data) {
      $scope.players = data;
    });

    $scope.orderProp = 'Rank';
  }]);

