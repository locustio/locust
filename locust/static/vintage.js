(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['exports', 'echarts'], factory);
    } else if (typeof exports === 'object' && typeof exports.nodeName !== 'string') {
        // CommonJS
        factory(exports, require('echarts'));
    } else {
        // Browser globals
        factory({}, root.echarts);
    }
}(this, function (exports, echarts) {
    var log = function (msg) {
        if (typeof console !== 'undefined') {
            console && console.error && console.error(msg);
        }
    };
    if (!echarts) {
        log('ECharts is not Loaded');
        return;
    }
    var colorPalette = ['#00ca5a','#ffca5a', '#d7ab82',  '#6e7074','#61a0a8','#efa18d', '#787464', '#cc7e63', '#724e58', '#4b565b'];
    echarts.registerTheme('vintage', {
        color: colorPalette,
        backgroundColor: '#132b21',
        xAxis: {lineColor: "#f00"},
        graph: {
            color: colorPalette,
        },
        textStyle: {color:"#b3c3bc"},
        title: {
            textStyle:{color:"#b3c3bc"}
        },
    });
}));