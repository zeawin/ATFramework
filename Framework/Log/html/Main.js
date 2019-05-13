String.prototype.format = function(args) {
    var result = this;
    if (arguments.length > 0) {
        if (arguments.length > 1) {
            if (args instanceof Array) {
                for (var i = 0; i < args.length; i++) {
                    if (args[i] != undefined) {
                        var reg = new RegExp("({[" + i + "]})", "g");
                        result = result.replace(reg, args[i])
                    }S
                }
            } else {
                if (typeof (args) == "object") {
                    for (var key in args) {
                        if (args[key] != undefined) {
                            var reg = new RegExp("({" + key + "})", "g");
                            result = result.replace(reg, args[key]);
                        }
                    }
                }
            }
        } else {
            for (var i = 0; i < arguments.length; i++) {
                var reg = new RegExp("({[" + i + "]})", "g");
                result = result.replace(reg, arguments[i]);
            }
        }
    }
    return result;
}

var filterOption = ["ALL", "ERROR", "WARN", "INFO", "DEBUG", "CMD", "CMD_RESPONSE", "PASS", "FAIL", "SECTION"];

var scoreNames = ["Total", "Pass", "Fail", "ConfigError", "NotRun", "Kill", "Running"];
//设置日志显示宽度
function setContentWidth() {
    if ($('#slideButton').text() == ">>") {
        var width = $(this).width() - 300;
    } else {
        var width = $(this).width();
    }
    $('#content').width(width);
}

//创建隐藏按钮
function createHideButton() {
    return $('<button name="slide" value="Slide" id="slideButton">>></button>');
}

//创建过滤器
function createFilter() {
    var tableHead = '<tr><td><strong>Filter Options:</strong></td></tr>';
    var filterTemp = '<tr><td><input type="checkbox" value="{filterName}" id="filter_{filterName}" checked="true" disabled="true"/></td></tr>';
    var hrHtml = '<tr><td><hr /></td></tr>';
    var filterHtml = '';
    for (var i = 0, len = filterOption.length; i < len; i++) {
        filterHtml = filterHtml + filterTemp.format({filterName:filterOption[i]});
    }
    var threadID = '<tr><td>ThreadID: <input id="threadID" type="text"/></td></tr>';
    var submitButton = '<tr><td><button value="Submit" id="filterButton"><strong>Submit</strong></button></td></tr>';
    var filters = $('<div id="filters">');
    var filterTable = $('<table id="filterTable">').html(tableHead+hrHtml+filterHtml+hrHtml+threadID+submitButton).appendTo(filters);
    return filters;
}

//创建执行结果界面
function createScorecard() {
    var scorecard = $('<div id="scorecard">');
    var scoreTable = $('<table id=scoreTable>');
    var scoreHead = '<tr id="scoreHead"><th>{0}</th><th>{1}</th><th>{2}</th><th>{3}</th><th>{4}</th><th>{5}</th><th>{6}</th></tr>';
    var scoreVal = '<tr id="scoreVal"><th>score_{0}</th><th>score_{1}</th><th>score_{2}</th><th>score_{3}</th><th>score_{4}</th><th>score_{5}</th><th>score_{6}</th><tr>';
    scoreTable.html(scoreHead.format(scoreNames)+scoreVal.format(scoreNames)).appendTo(scorecard);
    return scorecard;
}

//创建执行结果饼图

function createGraph() {
    var graph = $('<div id="graph">');
    return graph
}

//向页面添加工具面板
function addPanel(isLoadGraph) {
    var panel = $('<div id="panel">');
    createHideButton().appendTo(panel);
    createFilter().appendTo(panel);
    if (isLoadGraph) {
        createGraph().appendTo(panel);
    }
    panel.appendTo($('body'));
    $('#slideButton').click(function() {
        var text = $(this).text();
        if (text==">>") {
            $(this).text("<<");
            $(this).parent().animate({"right": "-=300px"}, "normal");
            setContentWidth();
        } else {
            $(this).text(">>");
            $(this).parent().animate({"right": "-=300px"}, "normal");
            setContentWidth();
        }
    })
}

//初始化过滤器
function initFilter() {
    $('#filter_ALL').removeAttr('disabled').click(function() {
        var checkedStatus = this.checked;
        $("input[type=checkbox]").each(function() {
            if (checkedStatus) {
                this.disabled = true;
            } else {
                this.disabled = false;
            }
            this.checked = checkedStatus;
        });
        this.disabled = false;
    });
    $('#filterButton').click(function() {
        var filterClass = "";
        var threadID = $("#threadID").val();
        var filterClassList = new Array();
        $("input[type=checkbox]").each(function() {
            if ($(this).attr("checked")) {
                filterClassList.push($(this).attr('value'))
            }
        })
        $('table#log tr').each(function() {
            var trClass = $(this).attr('class')
            if ($.inArray(trClass, filterClassList) >= 0) {
                if (threadID == "") {
                    $(this).show()
                } else {
                    if ($(this).find('td.thread').text() == ("ThreadID:"+threadID)) {
                        $(this).show()
                    } else {
                        $(this).hide()
                    }
                }
            } else {
                $(this).hide()
            }
        })
    });
}

//初始化执行结果面板
function initScorecade() {
    $("td#total").text(stats[0]);
    $("td#pass").text(stats[1]);
    $("td#fail").text(stats[2]);
    $("td#configError").text(stats[3]);
    $("td#notrun").text(stats[4]);
}

function initGraph() {
    var myChart = echarts.init(document.getElementById('graph'));
    var data = [];
    var color = [];
    var label = [];
    var t = {};
    for (var i=0; i<testData.length; i++) {
        var name = testData[i].label;
        var value = testData[i].data;
        t[name] = value;
        color.push(testData[i].color);
        label.push(name);
        data.push({'name':name, 'value':value});
    }
    var option = {
        title : {
            text: '用例执行结果统计',
            subtext: '用例总数:'+stats[0],
            x: 'center'
        },
        tooltip : {
            trigger: 'item',
            formatter: '总执行用例数:'+stats[0]+" <br/>{b} : {c} ({d}%)"
        },
        legend : {
            orient: 'horizontal',
            x: 'center',
            y: 'bottom',
            formatter: function(name) {
                var temp = "{name}:{num}"
                return temp.format({name:name, num:t[name]})
            },
            data: label
        },
        series : [
            {
                name: '执行结果',
                type: 'pie',
                radius: '60%',
                center: ['50%', '50%'],
                data: data
            }
        ],
        color: color
    };
    myChart.setOption(option)
}

//收起cmdResponse Msg de 内容
function createExpandButton() {
    $(".cmd_response td pre").each(function() {
        $(this).parent().prepend("<button class='expandButton' value='command Response'>+ Command Response</button><br />")
    })
    $(".cmd response td pre").hide()
    $(".expandButton").click(function() {
        if (this.innerText == '+ Command Response') {
            this.innerText == '- Command Response'
        } else {
            this.innerText == '+ Command Response'
        }
        $(this).next().next().toggle()
    });
}

$(document).ready(function(){
    var temp = window.location.href.split("/")
    var href = temp[temp.length - 1]
    var isLoadGraph = false;
    if (href.indexOf("Main_Rollup---", 0) >= 0) {
        isLoadGraph = true;
    }
    createExpandButton();
    addPanel(isLoadGraph);
    initFilter();
    if (isLoadGraph && typeof testData != "undefined") {
        initGraph();
    }

    $(window).resize(function() {
        setContentWidth();
    });
    setContentWidth();
})