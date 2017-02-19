(function() {
    class LocustLineChart {
        constructor(container, title, unit) {
            this.container = $(container);
            this.title = title;
            
            this.element = $('<div class="chart"></div>').css("width", "100%").appendTo(container);
            this.data = [];
            this.dates = [];
            
            this.chart = echarts.init(this.element[0], 'vintage');
            this.chart.setOption({
                title: {
                    text: this.title,
                    x: 10,
                    y: 10,
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        if (!!params && params.length > 0 && !!params[0].value) {
                            var param = params[0];
                            return param.name + ': ' + param.value + ' ' + unit;
                        } else {
                            return "No data";
                        }
                    },
                    axisPointer: {
                        animation: true
                    }
                },
                xAxis: {
                    type: 'category',
                    splitLine: {
                        show: false
                    },
                    data: this.dates,
                },
                yAxis: {
                    type: 'value',
                    boundaryGap: [0, '100%'],
                    splitLine: {
                        show: false
                    }
                },
                series: [{
                    name: 'RPS',
                    type: 'line',
                    showSymbol: true,
                    hoverAnimation: false,
                    data: this.data,
                }],
                grid: {x:60, y:70, x2:40, y2:40},
            })
        }
        
        addValue(value) {
            value = Math.round(value * 100) / 100;
            this.dates.push(new Date().toLocaleTimeString());
            this.data.push(value);
            this.chart.setOption({
                xAxis: {
                    data: this.dates,
                },
                series: [{
                    data: this.data,
                }]
            });
        }
        
        resize() {
            this.chart.resize();
        }
    }
    window.LocustLineChart = LocustLineChart;
})();
