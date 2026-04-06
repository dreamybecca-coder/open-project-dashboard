#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
先统计有多少人明确提到了年龄
"""
import json
import re

with open('records_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

has_age_info = []
no_age_info = []

for person in raw_data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    intro = fields.get('案主个人介绍', '')
    
    if not intro:
        continue
    
    # 检查是否有明确的当前年龄声明
    current_age_patterns = [
        r'(?:目前|现在|今年)\s*(\d{1,2})\s*岁',
        r'年龄[：:]\s*(\d{1,2})',
        r'现年\s*(\d{1,2})\s*岁',
        r'^(\d{1,2})\s*岁$',
        r'，\s*(\d{1,2})\s*岁[。，]',
    ]
    
    found_current_age = False
    for pattern in current_age_patterns:
        match = re.search(pattern, intro)
        if match:
            age = int(match.group(1))
            has_age_info.append({
                'name': name,
                'age': age,
                'pattern': pattern,
                'match': match.group(0)
            })
            found_current_age = True
            break
    
    if not found_current_age:
        no_age_info.append(name)

print(f"总人数：{len(raw_data)}")
print(f"明确提到当前年龄的人：{len(has_age_info)}")
print(f"没有明确提到年龄的人：{len(no_age_info)}")
print()
print("明确提到年龄的人：")
for i, p in enumerate(has_age_info[:30], 1):  # 只显示前30个
    print(f"{i}. {p['name']} - {p['age']}岁 - 匹配：{p['match']}")
