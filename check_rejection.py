#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看被拒绝的原因分布
"""
import json
from collections import Counter

with open('strict_filtered.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"总人数：{data['total_candidates']}")
print(f"被拒绝：{data['rejected_count']}")
print()

# 统计拒绝原因
age_reasons = []
overseas_reasons = []

for r in data['rejected_sample']:
    if r['type'] == 'age':
        age_reasons.append(r['reason'])
    else:
        overseas_reasons.append(r['reason'])

print("年龄拒绝原因（前20个）：")
for i, reason in enumerate(age_reasons[:20], 1):
    print(f"  {i}. {reason}")

print()
print("海外背景拒绝原因（前20个）：")
for i, reason in enumerate(overseas_reasons[:20], 1):
    print(f"  {i}. {reason}")
