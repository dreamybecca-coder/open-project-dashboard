#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将评估结果转换为dashboard格式
"""

import json

# 读取新的评估数据
with open('evaluated_projects.json', 'r', encoding='utf-8') as f:
    eval_data = json.load(f)

# 读取原始数据
with open('records_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 创建姓名到原始数据的映射
name_to_raw = {}
for person in raw_data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    if name:
        name_to_raw[name] = fields

# 转换为dashboard格式
dashboard_projects = []

for p in eval_data['projects']:
    name = p['name']
    raw_fields = name_to_raw.get(name, {})
    
    # 分数转换：0-5 -> 0-100
    score = p['totalScore'] * 20
    
    # 等级转换：S -> S+, S -> S, A -> A, B -> B, C -> C, D -> D
    grade = p['grade']
    level_map = {
        'S': 'S',
        'A': 'A',
        'B': 'B',
        'C': 'C',
        'D': 'D'
    }
    level = level_map.get(grade, 'D')
    
    # 如果分数 >= 75，升级为 S+
    if score >= 75:
        level = 'S+'
    
    dashboard_projects.append({
        'id': p.get('id', ''),
        'name': name,
        'region': raw_fields.get('所在大区', ''),
        'registerType': raw_fields.get('案主报名形式', ''),
        'credits': raw_fields.get('学分', 0),
        'directions': raw_fields.get('项目想突破的方向', ''),
        'intro': raw_fields.get('案主个人介绍', ''),
        'projectIntro': raw_fields.get('一页纸完整介绍', ''),
        'goal': raw_fields.get('航海目标和计划', ''),
        'introSummary': raw_fields.get('案主个人介绍', '')[:200] if raw_fields.get('案主个人介绍') else '',
        'specialCategories': raw_fields.get('项目想突破的方向', []),
        'totalScore': round(score, 2),
        'level': level,
        'recommendation': p.get('recommendation', '')
    })

# 按分数排序
dashboard_projects.sort(key=lambda x: x['totalScore'], reverse=True)

# 添加排名
for i, p in enumerate(dashboard_projects):
    p['rank'] = i + 1

# 统计
grade_counts = {}
for p in dashboard_projects:
    level = p['level']
    grade_counts[level] = grade_counts.get(level, 0) + 1

# 保存
output_data = {
    'meta': {
        'total': len(dashboard_projects),
        'grade_counts': grade_counts
    },
    'projects': dashboard_projects
}

with open('dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f'转换完成: {len(dashboard_projects)}个项目')
print(f'等级分布: {grade_counts}')

# 检查金融专项案例
target_names = ['张睿', '唐铕泽', '赵海森', '泊成', '王赛']
print(f'\\n金融专项案例检查:')
for name in target_names:
    for p in dashboard_projects:
        if p['name'] == name:
            print(f'  ✅ {name}: {p["totalScore"]}分 ({p["level"]}级), 排名#{p["rank"]}')
            break
    else:
        print(f'  ❌ {name}: 未找到')
