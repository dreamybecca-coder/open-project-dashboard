#!/usr/bin/env python3
"""构建嵌入数据的dashboard_v3.html"""

import json

def build_html():
    # 读取数据
    with open('evaluated_projects_v3.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    projects = data['projects']

    # 读取HTML模板
    with open('dashboard_v3.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 替换fetch为内嵌数据
    embedded_data = f'''
        let allProjects = {json.dumps(projects, ensure_ascii=False)};

        // Load data
        async function loadData() {{
            updateStats();
            applyFilters();
        }}
    '''

    # 替换loadData函数
    html = html.replace(
        "async function loadData() {\n            const response = await fetch('evaluated_projects_v3.json');\n            const data = await response.json();\n            allProjects = data.projects;\n            updateStats();\n            applyFilters();\n        }",
        embedded_data
    )

    # 保存
    output_path = 'dashboard_v3_embedded.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"已生成: {output_path}")
    print(f"包含 {len(projects)} 个项目")

if __name__ == '__main__':
    build_html()
