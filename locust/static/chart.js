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

    class LocustAdvanceLineChart{
        /**
         * lines should be an array of line names
         * units should be an array of unit names
         */
        constructor(container, title, subtitle, yAxes, units, width) {
            this.container = $(container);
            this.title = title;
            this.subtitle = subtitle;
            this.lines = [];
            this.yAxes = yAxes;
            this.units = units;
            this.width = width;
            this.xIndex = 0;
            this.activeFilter = []
            this.activeLegend = []

            this.element = $('<div class="chart"></div>').css("width", width).css("float","left").css("height", "430px").appendTo(container);
            this.multiData = [];
            this.dates = [];
            this.seriesData = [];
            this.chartOption = {
                title: {
                    text: this.title,
                    subtext: this.subtitle,
                    x: 20,
                    y: 30,
                    padding: [-7, 0, 0, 0],
                    textStyle: {
                        fontSize:20
                    }
                },
                legend: {
                    type:'scroll',
                    bottom:15,
                    textStyle:{
                        color:'white'
                    },
                    inactiveColor: "#4d4d4d",
                    itemWidth: 30,
                    itemHeight: 19,
                    pageIconColor: "white",
                    pageIconInactiveColor: "#4d4d4d",
                    pageTextStyle: {
                        color:'white'
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    confine: true,
                    axisPointer: {
                        animation: true
                    },
                    backgroundColor: 'rgba(0,0,0,0.3)',
                    hideDelay:2000,
                    formatter: function (params) {
                        if (!!params && params.length > 0 && !!params[0].name) {
                            let str = params[0].name;
                            for (let i = 0; i < params.length; i++) {
                                let param = params[i];
                                str += '<br><span style="color:' + param.color + ';">' + param.seriesName + ': ' + param.data + '</span>';
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
                    }
                },
                toolbox: {
                    feature: {
                        saveAsImage: {
                            name:'advance-chart',
                            title:'save',
                            iconStyle:{
                                normal: {
                                    borderWidth:3
                                }
                            }
                        }
                    },
                    top: 20,
                    right: 10
                },
                dataZoom: [
                    {
                        orient: 'vertical',
                        type: 'slider',
                        show: false,
                        filterMode: 'none',
                        width: 10,
                        left: 10,
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
                        show: false,
                        filterMode: 'none',
                        width: 10,
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
                        orient: 'horizontal',
                        type: 'slider',
                        show: true,
                        filterMode: 'none',
                        height: 10,
                        xAxisIndex: [0],
                        top: 70,
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
                grid: {x:60, y:120, x2:80, y2:70},
                color: ['#e6194b','#3cb44b','#ffe119','#0082c8','#f58231','#911eb4','#46f0f0','#f032e6','#d2f53c','#fabebe','#008080','#aa6e28','#fffac8','#800000','#aaffc3','#808000','#ffd8b1','#a199ff','#808080','#FFFFFF','#fc6c6c']
            }

            this.yAxesFormat = []
            for (let i=0; i < yAxes.length; i++) {
                this.yAxesFormat.push({
                    name: yAxes[i],
                    type: 'value',
                    show: false,
                    splitLine: {
                        show: false
                    },
                    nameTextStyle: {
                        color: 'white'
                    },
                    axisLine: {
                        lineStyle: {
                            color: 'white'
                        }
                    }
                })
                this.lines[i]=[]
                this.multiData[i]=[]
                this.seriesData[i]=[]
            }
            this.chart = echarts.init(this.element[0], 'vintage');
            let initChartOption = this.chartOption
            initChartOption.xAxis.data = this.dates
            initChartOption.yAxis = this.yAxesFormat
            this.chart.setOption(initChartOption)
        }

        addLine(yIndex, key, name) {
            let protomatch = /^(https?|http):\/\//;
            name = '['+this.yAxes[yIndex]+'] '+name.substring(0, 64).replace(protomatch, "");
            this.lines[yIndex].push({'name':name,'key':key})
            this.multiData[yIndex].push({
              key : key,
              name : name,
              values : []
            })
            if(this.multiData[yIndex].length > 1) {
              this.multiData[yIndex] = this.multiData[yIndex].sort(function(a, b) {
                let keyA = a.key.toUpperCase(); // ignore upper and lowercase
                let keyB = b.key.toUpperCase(); // ignore upper and lowercase
                if (keyA < keyB) return -1;
                if (keyA > keyB) return 1;
                return 0;
              })
            }
            this.seriesData[yIndex].push({
                key : key,
                name: name,
                type: 'line',
                yAxisIndex: yIndex,
                showSymbol: true,
                hoverAnimation: false,
                data: [],
            });
            if(this.multiData[yIndex].length > 1) {
              this.seriesData[yIndex] = this.seriesData[yIndex].sort(function(a, b) {
                let keyA = a.key.toUpperCase(); // ignore upper and lowercase
                let keyB = b.key.toUpperCase(); // ignore upper and lowercase
                if (keyA < keyB) return -1;
                if (keyA > keyB) return 1;
                return 0;
              })
            }
            for (let i=0; i<this.activeFilter.length; i++){
                for (let j=0; j<this.seriesData[this.activeFilter[i]].length; j++){
                    this.activeLegend.push(this.lines[this.activeFilter[i]][j].name)
                }
            }
            this._refreshChart()
        }

        addValue(values) {
            this.dates.push(new Date().toLocaleTimeString());
            for(let i=0; i<values.length; i++) {
                for(let j=0; j<values[i].length; j++) {
                    let value = Math.round(values[i][j] * 100) / 100;
                    this.multiData[i][j].values[this.xIndex] = value;
                    this.seriesData[i][j].data = this.multiData[i][j].values;
                }
            }
            this.xIndex++;
            this._refreshChart();
        }

        isLineExist(yAxis, value) {
            for(let i=0; i < this.lines[yAxis].length; i++) {
              if ( value == this.lines[yAxis][i].key) return true;
            }
            return false;
        }
  
        resize() {
            this.chart.resize();
        }
  
        dispose() {
            this.chart.dispose();
        }

        setFilter(yAxisIndexes) {
            this.activeFilter = yAxisIndexes
            this.activeLegend = []
            for(let i=0; i < this.yAxesFormat.length; i++) {
                if(this.activeFilter.includes(i)) {
                    this.yAxesFormat[i].show = true
                    this.yAxesFormat[i].position = (this.activeFilter[0] == i ) ? 'left' : 'right'
                    for (let j=0; j<this.seriesData[this.activeFilter[i]].length; j++){
                        this.activeLegend.push(this.lines[this.activeFilter[i]][j].name)
                    }
                }
                else this.yAxesFormat[i].show = false
            }
            for(let i=0; i< this.activeFilter.length; i++) {
                this.chartOption.dataZoom[i].show = true
                this.chartOption.dataZoom[i].yAxisIndex = this.activeFilter[i]
            }
            this.chart.clear()
            this._refreshChart()
        }

        addFilter(yAxisIndex) {
            this.activeFilter.push(yAxisIndex)
            this.yAxesFormat[yAxisIndex].show = true
            this.yAxesFormat[yAxisIndex].position = (this.activeFilter.length > 1) ? 'right' : 'left'
            this.chartOption.dataZoom[this.activeFilter.length-1].show = true
            this.chartOption.dataZoom[this.activeFilter.length-1].yAxisIndex = yAxisIndex
            for (let i=0; i<this.activeFilter.length; i++){
                for (let j=0; j<this.seriesData[this.activeFilter[i]].length; j++){
                    this.activeLegend.push(this.lines[this.activeFilter[i]][j].name)
                }
            }
            this.chart.clear()
            this._refreshChart()
        }

        removeFilter(yAxisIndex) {
            let deleted_index = this.activeFilter.indexOf(yAxisIndex)
            if(deleted_index != -1) this.activeFilter.splice(deleted_index, 1)
            this.yAxesFormat[yAxisIndex].show = false
            this.yAxesFormat[this.activeFilter[0]].position = 'left'
            this.chartOption.dataZoom[1].show = false
            for (let i=0; i<this.activeFilter.length; i++){
                for (let j=0; j<this.seriesData[this.activeFilter[i]].length; j++){
                    this.activeLegend.push(this.lines[this.activeFilter[i]][j].name)
                }
            }
            for(let i=0; i<this.activeFilter.length; i++) {
                this.chartOption.dataZoom[i].show = true
                this.chartOption.dataZoom[i].yAxisIndex = this.activeFilter[i]
            }
            this.chart.clear()
            this._refreshChart()
        }

        getActiveFilter(){
            return this.activeFilter
        }

        _refreshChart() {
            let dataSet = []
            for (let i=0; i<this.activeFilter.length; i++){
                for (let j=0; j<this.seriesData[this.activeFilter[i]].length; j++){
                    dataSet.push(this.seriesData[this.activeFilter[i]][j])
                }
            }
            let newOption = this.chartOption
            newOption.xAxis.data = this.dates
            newOption.legend.data = this.activeLegend
            newOption.series = dataSet
            this.chart.setOption(newOption)
        }
    }
    window.LocustAdvanceLineChart = LocustAdvanceLineChart;
})();
