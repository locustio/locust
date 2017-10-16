(function() {
    class LocustLineChart {
        /**
         * lines should be an array of line names
         */
        constructor(container, title, subtitle, lines, unit, width) {
            this.container = $(container);
            this.title = title;
            this.subtitle = subtitle;
            this.lines = lines;
            this.width = width;

            this.element = $('<div class="chart"></div>').css("width", width).css("float","left").appendTo(container);
            this.data = [];
            this.dates = [];

            this.seriesData = [];
            for (var i=0; i<lines.length; i++) {
                this.seriesData.push({
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
                title: {
                    text: this.title,
                    subtext: this.subtitle,
                    x: 10,
                    y: 10,
                    padding: [-7,0,0,0]
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
                    splitLine: {
                        show: false
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#5b6f66',
                        },
                    },
                },
                dataZoom: [
                    {
                        orient: 'horizontal',
                        type: 'slider',
                        show: true,
                        height: 10,
                        xAxisIndex: [0],
                        bottom: 290,
                        showDetail: false,
                        borderColor : '#5b6f66',
                        fillerColor: 'rgba(255, 255, 255, 0.4)',
                        handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                        handleSize: '175%',
                        handleStyle: {
                            color: '#fff',
                            shadowBlur: 3,
                            shadowColor: 'rgba(0, 0, 0, 0.6)',
                            shadowOffsetX: 2,
                            shadowOffsetY: 2
                        }
                    },
                    {
                        orient: 'vertical',
                        type: 'slider',
                        show: true,
                        width: 10,
                        yAxisIndex: [0],
                        right: 20,
                        showDetail: false,
                        borderColor : '#5b6f66',
                        fillerColor: 'rgba(255, 255, 255, 0.4)',
                        handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                        handleSize: '175%',
                        handleStyle: {
                            color: '#fff',
                            shadowBlur: 3,
                            shadowColor: 'rgba(0, 0, 0, 0.6)',
                            shadowOffsetX: 2,
                            shadowOffsetY: 2
                        }
                    },
                    {
                        type: 'inside',
                        xAxisIndex: [0]
                    },
                    {
                        type: 'inside',
                        yAxisIndex: [0]
                    }
                ],
                toolbox: {
                    feature: {
                        restore: {}
                    }
                },
                series: this.seriesData,
                grid: {x:60, y:70, x2:40, y2:40},
            })
        }

        addValue(values) {
            this.dates.push(new Date().toLocaleTimeString());
            this.seriesData = [];
            var pointX = this.data[0].length;
            for (var i=0; i<values.length; i++) {
                var value = Math.round(values[i] * 100) / 100;
                this.data[i][pointX] = value;
                this.seriesData.push({data: this.data[i]});
            }
            this.chart.setOption({
                xAxis: {
                    data: this.dates,
                },
                series: this.seriesData
            });
        }

        addLine(key) {
          this.lines.push(key)
          this.seriesData.push({
              name: key,
              type: 'line',
              showSymbol: true,
              hoverAnimation: false,
              data: [],
          });
          this.data.push([]);
          this.chart.setOption({
              series: this.seriesData
          });
        }

        isLineExist(value) {
          for(i=0; i < this.lines.length; i++) {
            if ( value == this.lines[i]) return true;
          }
          return false;
        }

        resize() {
            this.chart.resize();
        }
    }
    window.LocustLineChart = LocustLineChart;
})();
