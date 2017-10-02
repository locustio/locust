(function() {
    class LocustLineChart {
        /**
         * lines should be an array of line names
         */
        constructor(container, title, lines, unit) {
            this.container = $(container);
            this.title = title;
            this.lines = lines;
            this.unit = unit;
            this.element = $('<div class="chart"></div>').css("width", "100%").appendTo(container);
            this.init();
        }
        
        addValue(values) {
            this.dates.push(new Date().toLocaleTimeString());
            
            var seriesData = [];
            this.lines = values.map(function(x) { return x.name })
            for (var i=0; i<values.length; i++) {
                var value = Math.round(values[i].value * 100) / 100;
                this.data[values[i].name] = this.data[values[i].name] || new Array(this.dates.length);
                this.data[values[i].name].push(value);
                seriesData.push(this.seriesDataLine(values[i].name, this.data[this.lines[i]]));
            }

            this.chart.setOption({
                legend: {
                    data: this.lines
                },
                xAxis: {
                    data: this.dates,
                },
                series: seriesData
            });
        }
        
        resize() {
            this.chart.resize();
        }

        reset () {
            this.init();
        }

        seriesDataLine (name, data) {
            return {
                name: name,
                type: 'line',
                showSymbol: true,
                hoverAnimation: false,
                data: data,
            }
        }

        init () {
            this.data = {};
            this.dates = [];

            var seriesData = [];
            for (var i=0; i<this.lines.length; i++) {
                seriesData.push(this.seriesDataLine(this.lines[i], []));
                this.data[this.lines[i]] = []
            }

            this.chart = echarts.init(this.element[0], 'vintage');
            this.chart.setOption({
                title: {
                    text: this.title,
                    x: 10,
                    y: 10,
                },
                legend: {
                    data: this.lines
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        if (!!params && params.length > 0 && !!params[0].value) {
                            var str = params[0].name;
                            for (var i=0; i<params.length; i++) {
                                var param = params[i];
                                str += '<br><span style="color:' + param.color + ';">' + param.seriesName + ': ' + param.data + '</span>';
                            }
                            return str;
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
                    axisLine: {
                        lineStyle: {
                            color: '#5b6f66',
                        },
                    },
                    data: this.dates,
                },
                yAxis: {
                    type: 'value',
                    boundaryGap: [0, '100%'],
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
            })
        }
    }
    window.LocustLineChart = LocustLineChart;
})();
