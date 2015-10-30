/**
 * Created by manoj on 28/10/15.
 */

function searchRegion($scope, $http) {
    $http({
        method: 'POST',
        url: '/api/citysearch/',
        data: {"city": $scope.citysearchbox },
        headers: {'Content-Type':'application/json'}
    }).then(
        function successcallback(response){
            $scope.results = response.data.data
            $scope.showData = true
            console.log(response.data.message)
        },
        function errorCallback(response) {
            error(response)
        }
    )
}

function error(response) {
    status = response.status
    var text = 'Some Other Error'
    if (status == 500) {
        text = 'INTERNAL ERROR :: Server Error'
    }
    else if (status == 404){
        text = 'Url Not Found'
    }
    else if (status == 400){
        text = 'Bad Request::  ' + response.data.message
    }
    alert("Error:  "+status+ ":   " + text)
}
//function error()