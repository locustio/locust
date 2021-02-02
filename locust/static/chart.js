(function() {
    class LocustLineChart {
        /**
         * lines should be an array of line names
         */
        constructor(container, title, lines, unit, colors) {
            this.container = $(container);
            this.title = title;
            this.lines = lines;
            
            this.element = $('<div class="chart"></div>').css("width", "100%").appendTo(container);
            this.data = [];
            this.dates = [];
            
            var seriesData = [];
            for (var i=0; i<lines.length; i++) {
                seriesData.push({
                    name: lines[i],
                    type: 'line',
                    showSymbol: true,
                    hoverAnimation: false,
                    data: [],
                });
                this.data.push([]);
            }
            
            this.chart = echarts.init(this.element[0], 'vintage');
            this.chart.setOption({
                legend: {
                    icon: 'circle',
                    inactiveColor: '#b3c3bc',
                    textStyle: {
                        color: '#b3c3bc',
                    }
                },
                title: {
                    text: this.title,
                    x: 10,
                    y: 10,
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        if (!!params && params.length > 0 && params.some(param => !!param.value)) {
                            var str = params[0].name;
                            for (var i=0; i<params.length; i++) {
                                var param = params[i];
                                str += '<br><span style="color:' + param.color + ';">' + param.seriesName + ': ' + param.data.value + '</span>';
                            }
                            if(param.data.users != undefined){
                                str += '<br><span style="color:#a3b3ac;">Users: ' + param.data.users + '</span>';
                            }
                            return str;
                        } else {
                            return "No data";
                        }
                    },
                    axisPointer: {
                        animation: true
                    },
                    textStyle: {
                        color: '#b3c3bc',
                        fontSize: 13,
                    },
                    backgroundColor: 'rgba(21,35,28, 0.93)',
                    borderWidth: 0,
                    extraCssText: "z-index:1;",
                },
                xAxis: {
                    type: 'category',
                    splitLine: {
                        show: false
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#5b6f66',
                        },
                    },
                    data: this.dates,
                },
                yAxis: {
                    type: 'value',
                    boundaryGap: [0, '5%'],
                    splitLine: {
                        show: false
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#5b6f66',
                        },
                    },
                },
                series: seriesData,
                grid: {x:60, y:70, x2:40, y2:40},
                color: colors,
                toolbox: {
                    feature: {
                        saveAsImage: {
                            name: this.title.replace(/\s+/g, '_').toLowerCase() + '_' + Date.parse(new Date()) / 1000,
                            title: "Download as PNG"
                        }
                    }
                }
            })
        }
        
        addValue(values, user_count=0) {
            this.dates.push(new Date().toLocaleTimeString());
            var seriesData = [];
            for (var i=0; i<values.length; i++) {
                var value = Math.round(values[i] * 100) / 100;
                this.data[i].push({"value": value, "users": user_count});
                seriesData.push({data: this.data[i]});
            }
            this.chart.setOption({
                xAxis: {
                    data: this.dates,
                },
                series: seriesData
            });
        }
        
        resize() {
            this.chart.resize();
        }
    }
    window.LocustLineChart = LocustLineChart;
})();
