#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查之前确认过的年轻人，看看他们的年龄和海外背景如何表达
"""
import json
import re

with open('records_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 之前确认过的人
target_names = ['陈露文', '陈怡']  # 营养师陈怡

for person in raw_data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    intro = fields.get('案主个人介绍', '')
    
    if name in target_names:
        print(f"\n{'='*70}")
        print(f"姓名：{name}")
        print(f"{'='*70}")
        print(intro)
        print()
        
        # 分析年龄信息
        print("年龄相关信息：")
        age_patterns = [
            r'(\d{1,2})\s*岁',
            r'(\d{4})\s*年',
            r'毕业',
            r'博士',
            r'硕士',
        ]
        for pattern in age_patterns:
            matches = re.findall(pattern, intro)
            if matches:
                print(f"  {pattern}: {matches}")
        
        print("\n海外相关信息：")
        overseas_keywords = ['日本', '早稻田', '留学', '海外', '毕业']
        for kw in overseas_keywords:
            if kw in intro:
                print(f"  包含：{kw}")
