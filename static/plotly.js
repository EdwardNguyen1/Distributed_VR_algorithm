var app = angular.module('myApp', []);
app.controller('myCtrl', function($scope, $http, $interval, $timeout, $q) {
    $scope.iter   = 0;
    $scope.hide_W = true;
    $scope.mu     = 0.8;
    $scope.data_select = {0:true,  1:true,  2:true,  3:true,  4:true,
                          5:false, 6:false, 7:false, 8:false, 9:false}
    $scope.method  = "SVRG";
    $scope.dist_style = "Diffusion"
    $scope.fetched = "Have not fetched data.";
    $scope.cost_value = [];
    $scope.iter_list = [];
    $scope.server_client = "server";
    $scope.one_ip = "192.168.1.102:9999";
    $scope.stop = 1;
    $scope.iter_per_call = 20;

    // for topology plot
    $scope.plotFunc = function(){
        $http({
            method : 'GET',
            url : '/topo/'+$scope.Num_Node
        }).then(
            function mySuccess(response) {
                plot_func(response.data);
                // console.log(response.data);
            }, function myError(response){
                console.log("Some Error happened during plot topology!");
            });
    }

    // for image plot
    $scope.imshowFunc = function(){
        $http({
            method : 'GET',
            url: '/image'
        }).then(
        function success(response){
            var c=document.getElementById("img_tag");
            c.src = response.data['img_addr'];

            //-----------failed pixel manipulated approach--------//
            // var canvas = document.getElementById('image-canvas');
            // var ctx = canvas.getContext('2d');

            // var img_h = response.data['img_shape'][0];
            // var img_w = response.data['img_shape'][1];

            // // Get a pointer to the current location in the image.
            // var palette = ctx.getImageData(0,0,img_w,img_h); //x,y,w,h
            // palette.data.set(new Uint8ClampedArray(response.data['img_data']));
            // // Repost the data.
            // ctx.putImageData(palette,0,0);

            // var imgData = ctx.createImageData(img_h, img_w);
            // var data = imgData.data;

            // for (var i=0; i<img_h*img_w*4; i++) {
            //     data[i] = response.data['img_data'][i]
            // }

            // // now we can draw our imagedata onto the canvas
            // ctx.putImageData(imgData, 0, 0);

            console.log(response.data);
        }, function error(response){
            console.log("Some Error happened during load image!");
        });
    }

    $scope.connect =function() {
        $http({
                method : 'POST',
                url: '/connect',
                data: {'server_client': $scope.server_client,
                       'ip':  $scope.one_ip}
        })
    }
    
    $scope.get_data = function(){
        // stop and reset the running algorithm first
        $scope.stop_alg();
        $scope.rest_alg();
        $scope.fetched="Fetching data now."

        $http({
                method : 'POST',
                url: '/get_data',
                data: {'mask': $scope.data_select}
            }).then(
            function success(response){
                $scope.fetched="Data fetched!";
                $scope.rest_alg();  // used to reset W image
            }, function error(response){
                console.log("Some Error happened during fetched data!");
            })
    }

    $scope.run_alg = function(){
        // $scope.hide_W = false;
        // stop = $interval(function() {
        //     $http({
        //         method : 'POST',
        //         url: '/run_alg',
        //         data: {'mu': parseFloat($scope.mu),
        //                'method':  $scope.method,
        //                'ite': $scope.iter,
        //                'dist_style': $scope.dist_style}
        //    }).then(
        //     function success(response){
        //         $scope.hide_W = false;
        //         var c=document.getElementById("img_tag");
        //         var port = response.data['running_port'];
        //         c.src = '/static/visual_W_'+port+'.jpg?random='+new Date().getTime(); // refresh image
        //         if (response.data['cost_value'] != 'skipped') {
        //             $scope.cost_value.push(response.data['cost_value'])
        //             $scope.iter_list.push($scope.iter)
        //             // console.log($scope.cost_value)
        //             plot_cost($scope.iter_list, $scope.cost_value)
        //         }

        //     }, function error(response){
        //         console.log("Some Error happened during run algorithm!");
        //         $scope.stop_alg();
        //         $scope.hide_W = true;
        //         $scope.iter = 0;
        //         $scope.cost_value = [];
        //         $scope.iter_list = [];
        //     })
        //     $scope.iter = $scope.iter +50;
        // }, 1500);
        $scope.hide_W = false;
        $http({
            method : 'POST',
            url: '/run_alg',
            data: {'mu': parseFloat($scope.mu),
                   'method':  $scope.method,
                   'ite': $scope.iter,
                   'iter_per_call': $scope.iter_per_call,
                   'dist_style': $scope.dist_style}
       }).then(
        function success(response){
            $scope.hide_W = false;
            var c=document.getElementById("img_tag");
            var port = response.data['running_port'];
            c.src = '/static/visual_W_'+port+'.jpg?random='+new Date().getTime(); // refresh image
            if (response.data['cost_value'] != 'skipped') {
                $scope.cost_value.push(response.data['cost_value'])
                $scope.iter_list.push($scope.iter)
                // console.log($scope.cost_value)
                plot_cost($scope.iter_list, $scope.cost_value)
            }
            $scope.iter = $scope.iter + parseInt($scope.iter_per_call);
            // console.log($scope.stop)
            if ($scope.stop === 0) {
                $timeout(function(){$scope.run_alg();},200);
                // console.log("enter run branch at iter " + $scope.iter)
            } else {
                $scope.stop = 0; // re-define it so that next time it will keep running
                // console.log("enter stop branch")
            }
        }, function error(response){
            console.log("Some Error happened during run algorithm!");
            $scope.stop_alg();
            $scope.hide_W = true;
            $scope.iter = 0;
            $scope.cost_value = [];
            $scope.iter_list = [];
        })  
    }

    $scope.stop_alg = function(){
        if ($scope.stop === 1) {
            $scope.stop = 0;
        } else {
            $scope.stop = 1;
        }
    }

    $scope.rest_alg = function(){
        $http({
                method : 'GET',
                url: '/rest_alg'
            }).then(
            function success(response){
                var c=document.getElementById("img_tag");
                var port = response.data['running_port'];
                if (!angular.isDefined(port)){
                    c.src = '/static/visual_W_'+port+'.jpg?random='+new Date().getTime();
                }
                $scope.hide_W = true;
                $scope.iter = 0;
                $scope.cost_value = [];
                $scope.iter_list = [];
            }, function error(response){
                console.log("Some Error happened during reset plot!");
            })
    }

    // $scope.$watch($scope.cost_value, function() {
    //     console.log($scope.cost_value)
        
    // });
});

app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});

plot_func = function(data){

    var x_pos = [];
    var y_pos = [];
    var node_indx = [];
    for (var key in data.node) {
        x_pos.push(data.node[key].pos[0]);
        y_pos.push(data.node[key].pos[1]);
        node_indx.push(key)
    }
    console.log("x_pos:"+x_pos)
    console.log("y_pos:"+x_pos)

    trace = {
        x: x_pos,
        y: y_pos,
        text: node_indx,
        textposition: "bottom center",
        mode: 'markers+text'
    };

    layout = {
        margin: {t:0},
        xaxis: {showline: false,
                showgrid: false,
                zeroline: false,
                ticks: '',
                showticklabels: false},
        yaxis: {showline: false,
                showgrid: false,
                zeroline: false,
                ticks: '',
                showticklabels: false}
    };

    place = document.getElementById('plot-holder');
    Plotly.plot( place, [trace], layout);
}

plot_cost = function(iters, data){
    if (data == []) {
        return 
    }
    trace = {
        x: iters,
        y: data,
    };
    layout = {margin: {t:0, l:25, r:10},
              xaxis: {showline: true,
                      zeroline: false
                     },
              yaxis: {showline: true,
                      zeroline: false
                     }
            }
    place = document.getElementById('plot-holder');
    Plotly.newPlot( place, [trace], layout);
}