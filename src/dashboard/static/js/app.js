/**
 * Created by manoj on 26/10/15.
 */

var app = angular.module("locaterApp", ["ngRoute"]).
    config([ "$routeProvider", function($routeProvider){
        $routeProvider.when("/first",
            {
                templateUrl: "book.html",
                controller: firstController

            }
        ).when("/addregion",
            {
                templateUrl: "/static/templates/addregion.html",
                controller: searchCityController

            }
        );
    }
]);

var firstController = function($scope) {
    $scope.book = "test pass";
};

var searchCityController = function($scope, $http){
    $scope.showData=false
    $scope.searchRegion = function (){
        if ($scope.citysearchbox != "") {
            searchRegion($scope, $http)
        }

    }
}
app.controller('searchCityController', ['$scope','$http', searchCityController])
