#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查特定人员的详细信息
"""
import json

with open('records_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 需要检查的人
target_names = ['伊乔', '李姬韧', '赵海森', '陈怡', '王一', '李颖']

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
