#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动检查几个已知年轻人的文本
"""
import json
import re

with open('records_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 之前确认过的年轻人
target_names = ['赵海森', '陈露文', '李颖', '庞鑫龙', '陈怡', '王一']

for person in raw_data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    intro = fields.get('案主个人介绍', '')
    
    if name in target_names:
        print(f"\n{'='*60}")
        print(f"姓名：{name}")
        print(f"{'='*60}")
        print(intro)
        print(f"\n年龄相关文本搜索：")
        # 搜索可能的年龄相关文本
        age_patterns = [
            r'\d{1,2}\s*岁',
            r'\d{4}\s*年',
            r'毕业',
            r'出生',
            r'大一', r'大二', r'大三', r'大四',
            r'本科', r'硕士', r'博士'
        ]
        for pattern in age_patterns:
            matches = re.findall(pattern, intro)
            if matches:
                print(f"  {pattern}: {matches}")
