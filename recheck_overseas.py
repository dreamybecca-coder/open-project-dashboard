#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新检查所有可能被遗漏的海外背景"""

import json
import re

def check_overseas(intro, name):
    """更全面的海外背景检查"""
    
    overseas_keywords = [
        '留学', '海外', '国外', '出国', '赴美', '赴英', '赴日', '赴澳', '赴加',
        '留美', '留英', '留日', '留澳', '留加', '留法', '留德',
        '移民', '签证', '护照'
    ]
    
    # 知名海外大学
    overseas_universities = [
        '哈佛', '耶鲁', '斯坦福', '麻省理工', 'MIT', '普林斯顿', '哥伦比亚',
        '芝加哥大学', '宾夕法尼亚', '加州理工', '杜克', '约翰霍普金斯',
        '牛津', '剑桥', '帝国理工', '伦敦政经', 'LSE', 'UCL',
        '早稻田', '东京大学', '京都大学', '大阪大学',
        '南加州大学', 'USC', '加州大学', '伯克利', 'UCLA',
        '纽约大学', 'NYU', '波士顿大学', 'BU',
        '多伦多大学', '麦吉尔大学', 'UBC',
        '墨尔本大学', '悉尼大学', '澳洲国立',
        '新加坡国立', 'NUS', '南洋理工', 'NTU',
        '欧洲工商', 'INSEAD', 'HEC巴黎',
        '清华', '北大', '复旦', '上交', '浙大', '中科大'  # 国内的排除
    ]
    
    # 检查是否有海外关键词
    has_keyword = any(kw in intro for kw in overseas_keywords)
    
    # 检查是否有海外大学（排除国内大学）
    has_overseas_uni = False
    matched_unis = []
    for uni in overseas_universities:
        if uni in intro:
            if uni not in ['清华', '北大', '复旦', '上交', '浙大', '中科大']:
                has_overseas_uni = True
                matched_unis.append(uni)
    
    # 检查是否有"从XX回国"、"XX退学回国"等表述
    has_return_pattern = re.search(r'从[美国英国日本澳洲加拿大].*(?:回国|退学)', intro)
    has_study_abroad = re.search(r'[赴在][美英日澳加].*(?:留学|学习|读书|深造)', intro)
    
    # 判断是否有真实海外背景
    has_overseas = has_keyword or has_overseas_uni or has_return_pattern or has_study_abroad
    
    return {
        'has_overseas': has_overseas,
        'has_keyword': has_keyword,
        'has_overseas_uni': has_overseas_uni,
        'matched_unis': matched_unis,
        'has_return_pattern': bool(has_return_pattern),
        'has_study_abroad': bool(has_study_abroad)
    }

def extract_age(intro, name):
    """提取年龄信息"""
    
    age_info = []
    
    # 1. 明确的当前年龄
    age_patterns = [
        (r'(?:目前|现在|今年)\s*(\d{1,2})\s*岁(?:了)?', 0.95),
        (r'年龄[：:]\s*(\d{1,2})', 0.95),
        (r'现年\s*(\d{1,2})\s*岁', 0.95),
        (r'，\s*(\d{1,2})\s*岁[。，]', 0.90),
    ]
    
    for pattern, confidence in age_patterns:
        match = re.search(pattern, intro)
        if match:
            age = int(match.group(1))
            age_info.append((age, confidence, f"明确年龄: {match.group(0)}"))
    
    # 2. 在读状态
    if re.search(r'大[一二三四]\s*(?:在读|学生)', intro):
        if '大一' in intro:
            age_info.append((19, 0.80, '大学生'))
        elif '大二' in intro:
            age_info.append((20, 0.80, '大学生'))
        elif '大三' in intro:
            age_info.append((21, 0.80, '大学生'))
        elif '大四' in intro:
            age_info.append((22, 0.80, '大学生'))
    
    # 3. 从"XX年前回国"推断年龄
    return_match = re.search(r'(\d{1,2})\s*年前.*?回国', intro)
    if return_match:
        years_ago = int(return_match.group(1))
        # 假设回国时25-30岁
        estimated_age = 25 + years_ago
        age_info.append((estimated_age, 0.60, f'从{years_ago}年前回国推断'))
    
    # 4. 排除工作经验>8年
    exp_match = re.search(r'(\d{1,2})\s*年\s*(?:经验|工作|从业)', intro)
    if exp_match:
        years = int(exp_match.group(1))
        if years > 8:
            return None  # 排除
    
    if age_info:
        # 选择可信度最高的年龄
        age_info.sort(key=lambda x: x[1], reverse=True)
        return age_info[0][0]
    return None

def main():
    # 读取原始数据
    with open('records_raw.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 读取评分数据
    with open('evaluated_final.json', 'r', encoding='utf-8') as f:
        eval_data = json.load(f)
    
    score_map = {}
    for person in eval_data.get('projects', []):
        name = person.get('name', '')
        if name:
            score_map[name] = person
    
    results = []
    
    for person in raw_data:
        fields = person.get('fields', {})
        name = fields.get('姓名', '')
        intro = fields.get('案主个人介绍', '')
        
        if not name or not intro:
            continue
        
        # 检查海外背景
        overseas_info = check_overseas(intro, name)
        
        # 提取年龄
        age = extract_age(intro, name)
        
        # 筛选：有海外背景 + 年龄<=32（或无法确定年龄但有海外背景）
        if overseas_info['has_overseas']:
            person_info = {
                'name': name,
                'age': age,
                'intro': intro[:300],
                'overseas_info': overseas_info,
                'score': score_map.get(name, {}).get('total_score', 0),
                'grade': score_map.get(name, {}).get('grade', 'N/A')
            }
            results.append(person_info)
    
    # 输出结果
    print(f"找到 {len(results)} 个有海外背景的人：\n")
    for i, p in enumerate(results, 1):
        print(f"{i}. {p['name']}")
        print(f"   年龄: {p['age'] if p['age'] else '未确定'}")
        print(f"   海外大学: {', '.join(p['overseas_info']['matched_unis']) if p['overseas_info']['matched_unis'] else '无明确学校'}")
        print(f"   关键词: {'有' if p['overseas_info']['has_keyword'] else '无'}")
        print(f"   回国模式: {'有' if p['overseas_info']['has_return_pattern'] else '无'}")
        print(f"   留学模式: {'有' if p['overseas_info']['has_study_abroad'] else '无'}")
        print(f"   评分: {p['score']} ({p['grade']})")
        print(f"   简介: {p['intro'][:150]}...")
        print()

if __name__ == '__main__':
    main()
