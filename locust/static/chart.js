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
