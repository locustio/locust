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
            this.xIndex = 0;

            this.element = $('<div class="chart"></div>').css("width", width).css("float","left").appendTo(container);
            this.data = [];
            this.dates = [];

            this.seriesData = [];
            for (let i=0; i<lines.length; i++) {
                this.data.push({
                  key : lines[i],
                  name : lines[i],
                  values : []
                });
                this.seriesData.push({
                    key : lines[i],
                    name: lines[i],
                    type: 'line',
                    showSymbol: true,
                    hoverAnimation: false,
                    data: this.data[i].values,
                });
            }

            this.chart = echarts.init(this.element[0], 'vintage');
            this.chart.setOption({
                title: {
                    text: this.title,
                    subtext: this.subtitle,
                    x: 10,
                    y: 10,
                    padding: [-7, 0, 0, 0]
                },
                tooltip: {
                    trigger: 'axis',
                    confine: true,
                    axisPointer: {
                        animation: true
                    },
                    formatter: function (params) {
                        if (!!params && params.length > 0 && !!params[0].name) {
                            let protomatch = /^(https?|http):\/\//;
                            let str = params[0].name;
                            for (let i = 0; i < params.length; i++) {
                                let param = params[i];
                                let seriesNameFiltered = param.seriesName.substring(0, 64).replace(protomatch, "");
                                str += '<br><span style="color:' + param.color + ';">' + seriesNameFiltered + ': ' + param.data + '</span>';
                            }
                            return str;
                        } else {
                            return "No data";
                        }
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
                        filterMode: 'none',
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
                        filterMode: 'none',
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
                    }
                ],
                series: this.seriesData,
                grid: {x:60, y:70, x2:40, y2:40},
            })
        }

        addValue(values) {
            this.dates.push(new Date().toLocaleTimeString());
            for(let i=0; i<values.length; i++) {
              let value = Math.round(values[i] * 100) / 100;
              this.data[i].values[this.xIndex] = value;
              this.seriesData[i].data = this.data[i].values;
            }
            this.xIndex++;
            this.chart.setOption({
                xAxis: {
                    data: this.dates,
                },
                series: this.seriesData
            });
        }

        addLine(key, name) {
          this.lines.push(key)
          this.data.push({
            key : key,
            name : name,
            values : []
          })
          if(this.data.length > 1) {
            this.data = this.data.sort(function(a, b) {
              let keyA = a.key.toUpperCase(); // ignore upper and lowercase
              let keyB = b.key.toUpperCase(); // ignore upper and lowercase
              if (keyA < keyB) return -1;
              if (keyA > keyB) return 1;
              return 0;
            })
          }
          this.seriesData.push({
              key : key,
              name: name,
              type: 'line',
              showSymbol: true,
              hoverAnimation: false,
              data: [],
          });
          if(this.data.length > 1) {
            this.seriesData = this.seriesData.sort(function(a, b) {
              let keyA = a.key.toUpperCase(); // ignore upper and lowercase
              let keyB = b.key.toUpperCase(); // ignore upper and lowercase
              if (keyA < keyB) return -1;
              if (keyA > keyB) return 1;
              return 0;
            })
          }
          this.chart.setOption({
              series: this.seriesData
          });
        }

        isLineExist(value) {
          for(let i=0; i < this.lines.length; i++) {
            if ( value == this.lines[i]) return true;
          }
          return false;
        }

        resize() {
            this.chart.resize();
        }

        dispose() {
            this.chart.dispose();
        }
    }
    window.LocustLineChart = LocustLineChart;
})();
