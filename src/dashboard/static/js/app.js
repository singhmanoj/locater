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
        ).otherwise(
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
    $scope.selectCity = function (data){
        console.log(data.name)
        console.log(data.point[0])

    }
}
app.controller('searchCityController', ['$scope','$http', searchCityController])
