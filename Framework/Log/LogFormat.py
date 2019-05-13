# -*- coding: utf-8 -*-

"""
    Effect: provide the template of format log
"""

import Enum

__all__ = ['logFormatDic', 'timeFormat', 'traceDicFormat', 'traceFormat']

logFormatDic = {
    'general': '<tr class="{level}">'
               '<td class="timestamp">{timestamp}</td>'
               '<td class="level">{level}</td>'
               '<td class="thread">ThreadID: {threadID}</td>'
               '<td class="hierarchy" title="{trace}">{className}--line:{lineno}</td>'
               '<td class="message"><pre>{msg}</pre></td></tr>',
    'htmlHead': '<html><head><title>Log File</title>'
                '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>'
                '{css}'
                '{script}'
                '<body><div id="content"><table id="log">',
    'styleLink': '<link rel="stylesheet" type="text/css" href="{cssPath}"/>',
    'script': '<script type="text/javascript" src="{scriptPath}"></script>',
    'nextFileLink': '<tr><td colspan="5"><center><a href="{fileName}">Next LogFile</a></center></td></tr>',
    'htmlTail': '</table></div></body></html>'
}
fileLink = '<a href="{href}" target="_blank">{msg}</a>'
timeFormat = '%Y-%m-%d %H:%M:%S:%f'
traceDicFormat = ['fileName', 'lineNumber', 'functionName', 'text']
traceFormat = '{functionName}::{text} at {fileName} line {lineNumber}'


def formatHtmlHead(logType):
    """To generate different html head according to the different logType)
    """
    cssList = ['MainStyle.css']
    scriptList = ['jquery-1.6.1.js', 'Main.js', 'echarts-all.js']
    scriptPath = ''
    if logType is Enum.LogType.TestCase:
        scriptPath = '..\\'
    isLoadGraph = False
    if logType is Enum.LogType.Main:
        isLoadGraph = True
    cssHtml = ''
    for cssPath in cssList:
        cssHtml += logFormatDic['styleLink'].format(cssPath=scriptPath+cssPath)

    scriptHtml = ''
    if isLoadGraph:
        scriptHtml += logFormatDic['script'].format(scriptPath='status.js')
    else:
        scriptList = scriptList[:-1]

    for script in scriptList:
        scriptHtml += logFormatDic['script'].format(scriptPath=scriptPath+script)

    return logFormatDic['htmlHead'].format(css=cssHtml, script=scriptHtml)
