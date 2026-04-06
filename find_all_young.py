#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
寻找所有32岁以下的人（通过任何方式推断）
"""
import json
import re

with open('records_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

young_candidates = []

for person in raw_data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    intro = fields.get('案主个人介绍', '')
    
    if not intro or len(intro) < 20:
        continue
    
    age_info = []
    
    # 1. 明确的当前年龄
    current_age_patterns = [
        (r'(?:目前|现在|今年)\s*(\d{1,2})\s*岁', '明确年龄'),
        (r'年龄[：:]\s*(\d{1,2})', '明确年龄'),
        (r'现年\s*(\d{1,2})\s*岁', '明确年龄'),
        (r'^(\d{1,2})\s*岁$', '明确年龄'),
        (r'，\s*(\d{1,2})\s*岁[。，]', '明确年龄'),
    ]
    
    for pattern, source in current_age_patterns:
        match = re.search(pattern, intro, re.MULTILINE)
        if match:
            age = int(match.group(1))
            if age <= 32:
                age_info.append((age, source, match.group(0)))
            break
    
    # 2. 在读状态（必须是"在读"）
    if not age_info:
        if re.search(r'大[一二三四]\s*(?:在读|学生)', intro):
            if '大一' in intro:
                age_info.append((19, '大学生', ''))
            elif '大二' in intro:
                age_info.append((20, '大学生', ''))
            elif '大三' in intro:
                age_info.append((21, '大学生', ''))
            elif '大四' in intro:
                age_info.append((22, '大学生', ''))
        elif re.search(r'研究生在读', intro):
            age_info.append((24, '研究生', ''))
        elif re.search(r'博士在读', intro):
            age_info.append((26, '博士生', ''))
    
    # 3. 出生年份
    if not age_info:
        birth_match = re.search(r'(\d{4})\s*年?\s*(?:出生|生)', intro)
        if birth_match:
            birth_year = int(birth_match.group(1))
            age = 2026 - birth_year
            if 18 <= age <= 32:
                age_info.append((age, '出生年份', f'{birth_year}年'))
    
    # 4. 毕业年份（本科）
    if not age_info:
        grad_match = re.search(r'(\d{4})\s*年?\s*(?:本科)?毕业', intro)
        if grad_match:
            grad_year = int(grad_match.group(1))
            age = 2026 - grad_year + 22
            if 18 <= age <= 35:  # 毕业年份推断误差较大
                age_info.append((age, '毕业年份', f'{grad_year}年毕业'))
    
    # 5. 排除：工作年限>8年 或 工作经验明显超过年龄
    exp_match = re.search(r'(\d{1,2})\s*年\s*(?:经验|工作|从业)', intro)
    if exp_match:
        years = int(exp_match.group(1))
        if years > 8:
            age_info = []  # 清除之前的推断
            continue  # 跳过这个人
    
    # 5.1 排除：职业生涯或工作经历明显很长
    if re.search(r'(\d{1,2})\s*年.*?(?:建筑师|工程师|经理|从业|职业生涯)', intro):
        years_match = re.search(r'(\d{1,2})\s*年', intro)
        if years_match:
            years = int(years_match.group(1))
            if years > 10:
                age_info = []
                continue
    
    if age_info:
        young_candidates.append({
            'name': name,
            'age': age_info[0][0],
            'source': age_info[0][1],
            'evidence': age_info[0][2],
            'intro': intro[:200]
        })

# 按年龄排序
young_candidates.sort(key=lambda x: x['age'])

print(f"找到 {len(young_candidates)} 个32岁以下的候选人：\n")
for i, p in enumerate(young_candidates, 1):
    print(f"{i}. {p['name']} - {p['age']}岁 ({p['source']}: {p['evidence']})")
    print(f"   简介：{p['intro'][:100]}...")
    print()
