#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终筛选：32岁以下 + 海外背景"""

import json
import re

def extract_age_v2(intro, name):
    """更准确的年龄提取"""
    
    age_info = []
    
    # 1. 明确的当前年龄（最高优先级）
    patterns_high = [
        r'(?:目前|现在|今年)\s*(\d{1,2})\s*岁(?:了)?',
        r'年龄[：:]\s*(\d{1,2})',
        r'现年\s*(\d{1,2})\s*岁',
    ]
    
    for pattern in patterns_high:
        match = re.search(pattern, intro)
        if match:
            age = int(match.group(1))
            return age, f"明确年龄: {match.group(0)}"
    
    # 2. 在读状态
    if re.search(r'大[一二三四]\s*(?:在读|学生)', intro):
        if '大一' in intro:
            return 19, '大一在读'
        elif '大二' in intro:
            return 20, '大二在读'
        elif '大三' in intro:
            return 21, '大三在读'
        elif '大四' in intro:
            return 22, '大四在读'
    
    if re.search(r'研究生在读', intro):
        return 24, '研究生在读'
    
    if re.search(r'博士在读', intro):
        return 26, '博士在读'
    
    # 3. 从"XX年前...回国"推断（包括退学回国）
    return_match = re.search(r'(\d{1,2})\s*年前.*?(?:退学)?.*?回国', intro)
    if return_match:
        years_ago = int(return_match.group(1))
        # 假设回国时25-28岁
        estimated_age = 25 + years_ago
        return estimated_age, f'从{years_ago}年前回国推断'
    
    # 4. 从"XX年经验"推断（假设22岁开始工作）
    exp_match = re.search(r'(\d{1,2})\s*年\s*(?:经验|工作|从业)', intro)
    if exp_match:
        years = int(exp_match.group(1))
        # 如果工作经验>8年，直接排除
        if years > 8:
            return None, '工作经验过长'
        estimated_age = 22 + years
        return estimated_age, f'从{years}年经验推断'
    
    # 5. 单独出现的年龄（需要排除过去时态和孩子年龄）
    age_matches = list(re.finditer(r'(\d{1,2})\s*岁', intro))
    if age_matches:
        for match in age_matches:
            age = int(match.group(1))
            context_start = max(0, match.start() - 20)
            context = intro[context_start:match.end() + 20]
            
            # 排除过去时态
            if '那一年' in context or '那年' in context or '赴' in context or '岁时' in context or '的时候' in context:
                continue
            
            # 排除"孩子"、"大宝"、"宝宝"等上下文
            if re.search(r'(孩子|大宝|宝宝|儿子|女儿).*?\d{1,2}\s*岁', context):
                continue
            
            # 排除"带领XX岁学生"这种模式
            if re.search(r'带领.*?(\d{1,2})\s*岁', context):
                continue
            
            # 排除"照顾XX岁的大宝"
            if '照顾' in context or '孩子' in context:
                continue
            
            return age, f"年龄: {match.group(0)}"
    
    return None, '未找到年龄信息'

def check_overseas_v2(intro):
    """更全面的海外背景检查"""
    
    # 知名海外大学
    overseas_unis = [
        '哈佛', '耶鲁', '斯坦福', '麻省理工', 'MIT', '普林斯顿', '哥伦比亚',
        '芝加哥大学', '宾夕法尼亚', '加州理工', '杜克', '约翰霍普金斯',
        '牛津', '剑桥', '帝国理工', '伦敦政经', 'LSE', 'UCL',
        '早稻田', '东京大学', '京都大学', '大阪大学',
        '南加州大学', 'USC', '加州大学', '伯克利', 'UCLA',
        '纽约大学', 'NYU', '波士顿大学', 'BU',
        '多伦多大学', '麦吉尔大学', 'UBC',
        '墨尔本大学', '悉尼大学', '澳洲国立',
        '新加坡国立', 'NUS', '南洋理工', 'NTU',
        '欧洲工商', 'INSEAD', 'HEC巴黎', 'Parsons'
    ]
    
    # 检查海外大学
    matched_unis = []
    for uni in overseas_unis:
        if uni in intro:
            matched_unis.append(uni)
    
    # 检查留学相关表述
    has_study_abroad = bool(re.search(r'[赴在留][美英日澳加法德].*(?:留学|学习|读书|深造|毕业)', intro))
    has_return = bool(re.search(r'(?:从|在)[美英日澳加法德].*(?:回国|退学)', intro))
    has_overseas_keyword = any(kw in intro for kw in ['留学', '海外求学', '国外求学'])
    
    # 判断是否有真实海外留学背景
    has_overseas = bool(matched_unis) or has_study_abroad or has_return or has_overseas_keyword
    
    return {
        'has_overseas': has_overseas,
        'matched_unis': matched_unis,
        'has_study_abroad': has_study_abroad,
        'has_return': has_return
    }

def main():
    # 读取数据
    with open('records_raw.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
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
        overseas_info = check_overseas_v2(intro)
        
        if not overseas_info['has_overseas']:
            continue
        
        # 提取年龄
        age, age_source = extract_age_v2(intro, name)
        
        if age is None:
            continue
        
        # 筛选32岁以下
        if age > 32:
            continue
        
        person_info = {
            'name': name,
            'age': age,
            'age_source': age_source,
            'overseas_info': overseas_info,
            'intro': intro[:300],
            'score': score_map.get(name, {}).get('total_score', 0),
            'grade': score_map.get(name, {}).get('grade', 'N/A')
        }
        results.append(person_info)
    
    # 按年龄排序
    results.sort(key=lambda x: x['age'])
    
    # 输出结果
    print(f"找到 {len(results)} 个32岁以下有海外背景的人：\n")
    for i, p in enumerate(results, 1):
        print(f"{i}. {p['name']} - {p['age']}岁 ({p['age_source']})")
        print(f"   海外背景: {', '.join(p['overseas_info']['matched_unis']) if p['overseas_info']['matched_unis'] else '有留学经历'}")
        print(f"   评分: {p['score']} ({p['grade']})")
        print(f"   简介: {p['intro'][:150]}...")
        print()
    
    # 保存结果
    with open('young_overseas_rechecked.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 young_overseas_rechecked.json")

if __name__ == '__main__':
    main()
