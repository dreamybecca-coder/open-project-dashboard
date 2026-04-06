#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更宽松的筛选：包含更多年龄推断方式
"""
import json
import re

with open('records_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

candidates = []

for person in raw_data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    intro = fields.get('案主个人介绍', '')
    
    if not intro or len(intro) < 20:
        continue
    
    age_info = None
    
    # 1. 明确的当前年龄
    patterns = [
        (r'(?:目前|现在|今年)\s*(\d{1,2})\s*岁', '明确'),
        (r'年龄[：:]\s*(\d{1,2})', '明确'),
        (r'，\s*(\d{1,2})\s*岁[。，]', '明确'),
    ]
    
    for pattern, source in patterns:
        match = re.search(pattern, intro, re.MULTILINE)
        if match:
            age = int(match.group(1))
            if 18 <= age <= 32:
                age_info = (age, source)
                break
    
    # 2. 在读状态
    if not age_info:
        if re.search(r'大[一二三四]\s*(?:在读|学生)', intro):
            age = 19 if '大一' in intro else (20 if '大二' in intro else (21 if '大三' in intro else 22))
            age_info = (age, '大学生在读')
        elif re.search(r'研究生在读', intro):
            age_info = (24, '研究生在读')
    
    # 3. 毕业年份（更宽松）
    if not age_info:
        grad_match = re.search(r'(\d{4})\s*年?\s*(?:本科|大学)?毕业', intro)
        if grad_match:
            grad_year = int(grad_match.group(1))
            age = 2026 - grad_year + 22
            if 18 <= age <= 35:
                age_info = (age, f'{grad_year}年毕业推断')
    
    # 4. 出生年份
    if not age_info:
        birth_match = re.search(r'(\d{4})\s*年?\s*(?:出生|生)', intro)
        if birth_match:
            birth_year = int(birth_match.group(1))
            age = 2026 - birth_year
            if 18 <= age <= 32:
                age_info = (age, f'{birth_year}年出生')
    
    # 排除：工作经验>8年
    if age_info:
        exp_match = re.search(r'(\d{1,2})\s*年\s*(?:经验|工作|从业)', intro)
        if exp_match and int(exp_match.group(1)) > 8:
            continue
    
    if age_info and age_info[0] <= 32:
        # 检查海外背景（宽松版）
        countries = ['美国', '英国', '日本', '韩国', '新加坡', '澳大利亚', '澳洲', '加拿大',
                     '德国', '法国', '意大利', '荷兰', '瑞士', '香港', '澳门', '台湾',
                     '新西兰', '爱尔兰', '西班牙', '俄罗斯']
        
        has_country = any(country in intro for country in countries)
        
        # 检查是否有留学关键词
        study_keywords = ['留学', '海外', '国外', '毕业于', '本科.*毕业', '硕士', '博士']
        has_study = any(re.search(kw, intro) for kw in study_keywords)
        
        # 检查是否有知名海外学校
        schools = ['早稻田', '哈佛', '牛津', '剑桥', '斯坦福', 'MIT', '南加州', 
                   '哥伦比亚', 'NYU', 'UCLA', '帝国理工', '东京大学', '京都大学']
        has_school = any(school in intro for school in schools)
        
        if has_country or has_school:
            candidates.append({
                'name': name,
                'age': age_info[0],
                'age_source': age_info[1],
                'has_country': has_country,
                'has_study': has_study,
                'has_school': has_school,
                'intro': intro[:200]
            })

# 按年龄排序
candidates.sort(key=lambda x: x['age'])

print(f"找到 {len(candidates)} 个候选人：\n")
for i, p in enumerate(candidates, 1):
    print(f"{i}. {p['name']} - {p['age']}岁 ({p['age_source']})")
    print(f"   海外背景：国家={p['has_country']}, 留学关键词={p['has_study']}, 学校={p['has_school']}")
    print(f"   简介：{p['intro'][:100]}...")
    print()
