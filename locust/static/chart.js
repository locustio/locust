(function() {
    class LocustLineChart {
        /**
         * lines should be an array of line names
         */
        constructor(container, title, lines, unit, yLabelUnit, drawMarkLine) {
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
                    symbolSize: 6,
                    hoverAnimation: false,
                    data: []
                });
                this.data.push([]);
            }

            if (drawMarkLine)
            {
                for (var i=0; i<seriesData.length; i++)
                {
                    seriesData[i]['markLine'] = {
                        silent: true,
                        symbol: 'pin',
                        symbolSize: 8,
                        lineStyle: {
                          normal: {
                              color: '#e7be55'
                          }
                        },
                        data: [
                            {
                                name: 'Max',
                                type: 'max'
                            }
                        ]
                    }
                }
            }

            this.chart = echarts.init(this.element[0], 'vintage');
            this.chart.setOption({
                title: {
                    text: this.title,
                    x: 10,
                    y: 10,
                },
                toolbox: {
                    feature: {
                        dataZoom: {
                            show: true,
                            yAxisIndex: false,
                            title: {
                                zoom: '查看局部',
                                back: '恢复全局显示'
                            }
                        },
                        saveAsImage: {
                            type: 'png',
                            title: '保存为图片',
                            pixelRatio: 8
                        }
                    }
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
                            return '<span style="color:#e7be55">No data</span>';
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
                    axisLabel: {
                        formatter: yLabelUnit ? '{value} ' + yLabelUnit : '{value}'
                    }
                },
                series: seriesData,
                grid: {x:60, y:70, x2:40, y2:40},
            })
        }

        addValue(values) {
            this.dates.push(new Date().toLocaleTimeString());
            var seriesData = [];
            for (var i=0; i<values.length; i++) {
                var value = Math.round(values[i] * 100) / 100;
                this.data[i].push(value);
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
