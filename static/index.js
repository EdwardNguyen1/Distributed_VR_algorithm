var app = angular.module('myApp', []);
app.controller('myCtrl', function($scope, $http, $interval, $timeout, $q) {
    $scope.tempIP;
    function askIP() {
        window.RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection;   //compatibility for firefox and chrome
            var pc = new RTCPeerConnection({iceServers:[]}), noop = function(){};      
            pc.createDataChannel("");    //create a bogus data channel
            pc.createOffer(pc.setLocalDescription.bind(pc), noop);    // create offer and set local description
            pc.onicecandidate = function(ice){  //listen for candidate events
                if(!ice || !ice.candidate || !ice.candidate.candidate)  return;
                var myIP = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/.exec(ice.candidate.candidate)[1];
                $scope.tempIP = myIP;
                pc.onicecandidate = noop;
            };
    };
    
    askIP()

    $scope.sendIP =function() {
        $http({
                method : 'POST',
                url: '/sendIP',
                data: {'sentIP': $scope.tempIP},
        }).then(function mySuccess(response) {
                console.log('Sent IP!');
            });
    };
    
    $scope.sendIP =function() {
        $http({
                method : 'POST',
                url: '/sendIP',
                data: {'sentIP': $scope.tempIP},
        }).then(function mySuccess(response) {
                console.log('Sent IP!');
            });
    };
        
});

app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});


