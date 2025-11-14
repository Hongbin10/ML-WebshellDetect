# -*- coding: utf8 -*-

import os
import hashlib
from html import escape

# 报告相关目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'Utils')
REPORT_TEMPLATE_DIR = os.path.join(DATA_DIR, 'report_template')
print(REPORT_TEMPLATE_DIR)

def md5(hash_str):
    return hashlib.md5(hash_str.encode()).hexdigest()

def generate_report(report, result, vuln, output_path):
    """生成检测报告
    
    Args:
        report: 报告基本信息
        result: 检测结果
        vuln: 漏洞详情
        output_path: 输出文件路径
    """
    # 读取模板文件
    try:
        with open(os.path.join(REPORT_TEMPLATE_DIR, 'part_1.html'), 'r', encoding='utf-8') as f:
            part_1 = f.read()
    except Exception as e:
        raise Exception(f"读取报告模板part_1.html失败: {str(e)}")

    # 生成概览部分
    raw_html_1 = '''
      <p class="lead">{start_time} ~ {end_time}<br>
        扫描 PHP 文件 {file_count} 个，发现 {vuln_count} 处隐患。
      </p>
    </div>
    <h2 id="files" class="target">Overview</h2>
    <div class="table-responsive">
      <table id="table-overview" class="table table-striped dataTable" role="grid">
        <thead>
          <tr>
            <th>状态</th>
            <th>文件名</th>
            <th>标签</th>
          </tr>
        </thead>
        <tbody>
    '''.format(**report)

    # 生成文件列表
    raw_html_2 = ''
    for fp, label in result.items():
        raw_html_2 += '<tr><td>'
        if label == 1:
            raw_html_2 += '<span class="label label-danger">高危</span>'
        else:
            raw_html_2 += '<span class="label label-success">正常</span>'
        raw_html_2 += '''</td>
            <td><a href="#{filename}">{filename}</a></td>
            <td>{label}</td>
          </tr>
        '''.format(filename=fp, label=str(label))

    # 生成漏洞详情部分
    raw_html_3 = '''
        </tbody>
      </table>
    </div>
    <h2 id="vulnerabilities" class="target">Vulnerability</h2>
    '''

    for fp, vul in vuln.items():
        raw_html_3 += f'''<div id="{fp}" class="panel panel-default">
      <div class="panel-heading clickable" Data-toggle="collapse" Data-target="#{md5(fp)}">
        <h3 class="panel-title">{fp}</h3>
      </div>
      <div class="panel-body" id="{md5(fp)}">
        <div class="table-responsive">
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Level</th>
                <th>Size</th>
                <th>Last Modify</th>
              </tr>
            </thead>
            <tbody>
              <tr class="success">
                <td title="Level" width="10%"><span class="label label-danger">danger</span></td>
                <td title="Function" width="20%">{vul['fsize']}</td>
                <td title="Description">{vul['flast']}</td>
              </tr>
              <tr>
                <td colspan="3">
                  <h5>Code</h5>
                  <pre style="background-color: #fff !important;"><code class="php">{escape(vul['fcode'])}</code></pre>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    '''

    raw_html_3 += '</div>'

    # 读取结尾模板
    try:
        with open(os.path.join(REPORT_TEMPLATE_DIR, 'part_3.html'), 'r', encoding='utf-8') as f:
            part_3 = f.read()
    except Exception as e:
        raise Exception(f"读取报告模板part_3.html失败: {str(e)}")

    # 组合完整的HTML
    html = part_1 + raw_html_1 + raw_html_2 + raw_html_3 + part_3

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 写入输出文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    except Exception as e:
        raise Exception(f"写入报告文件失败: {str(e)}")