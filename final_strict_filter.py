#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终筛选：只从明确提到年龄或有明确在读状态的人中筛选
32岁以下 + 真实海外留学背景
"""
import json
import re

def verify_overseas_background(text):
    """
    验证真实的海外留学背景
    返回：(是否真实, 证据列表)
    """
    text = text.replace('\n', ' ').replace('\r', ' ')
    evidence = []
    
    # 排除：只是想去留学
    exclude_patterns = [
        r'想.*留学',
        r'准备.*出国',
        r'计划.*留学',
        r'打算.*海外',
    ]
    for pattern in exclude_patterns:
        if re.search(pattern, text):
            return (False, ["只是计划留学，非实际经历"])
    
    # 必须有明确的留学国家/地区或知名海外学校
    countries_or_schools = [
        '美国', '英国', '日本', '韩国', '新加坡', '澳大利亚', '澳洲', '加拿大',
        '德国', '法国', '意大利', '荷兰', '瑞士', '香港', '澳门', '台湾',
        '新西兰', '爱尔兰', '西班牙', '俄罗斯',
        '早稻田', '哈佛', '牛津', '剑桥', '斯坦福', 'MIT', '麻省理工',
        '南加州大学', '哥伦比亚', '纽约大学', 'NYU', 'UCLA', '伯克利',
        '帝国理工', '伦敦大学', 'UCL', 'LSE', '爱丁堡', '曼彻斯特',
        '东京大学', '京都大学', '首尔大学', '国立大学', 'NUS',
        '墨尔本大学', '悉尼大学', '多伦多大学', '麦吉尔'
    ]
    
    country_found = []
    for item in countries_or_schools:
        if item in text:
            country_found.append(item)
    
    if not country_found:
        return (False, ["未提到具体国家/地区或知名海外学校"])
    
    # 必须有明确的留学相关动词或学历
    study_keywords = [
        '留学', '海外', '国外', '出境学习',
        '攻读', '就读', '毕业于', '学士', '硕士', '博士', 'MBA',
        '本科.*毕业', '研究生.*毕业'
    ]
    
    has_study_verb = False
    for keyword in study_keywords:
        if re.search(keyword, text):
            has_study_verb = True
            evidence.append(f"找到留学关键词：{keyword}")
            break
    
    if not has_study_verb:
        return (False, ["未找到留学相关描述"])
    
    evidence.append(f"国家/学校：{', '.join(country_found[:3])}")
    
    return (True, evidence)

def filter_candidates():
    """主筛选逻辑"""
    # 读取原始数据
    with open('records_raw.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 读取评分数据
    with open('evaluated_final.json', 'r', encoding='utf-8') as f:
        eval_data = json.load(f)
    
    # 构建姓名到评分的映射
    score_map = {}
    for person in eval_data.get('projects', []):
        name = person.get('name', '')
        if name:
            score_map[name] = person
    
    results = []
    
    # 明确的当前年龄声明模式
    current_age_patterns = [
        r'(?:目前|现在|今年)\s*(\d{1,2})\s*岁',
        r'年龄[：:]\s*(\d{1,2})',
        r'现年\s*(\d{1,2})\s*岁',
        r'^(\d{1,2})\s*岁$',
        r'，\s*(\d{1,2})\s*岁[。，]',
    ]
    
    # 在读状态模式
    student_patterns = [
        (r'大[一二三四]', '大学生'),
        (r'研究生在读', '研究生'),
        (r'博士在读', '博士生'),
    ]
    
    for person in raw_data:
        fields = person.get('fields', {})
        name = fields.get('姓名', '')
        intro = fields.get('案主个人介绍', '')
        
        if not intro:
            continue
        
        # 提取年龄
        age = None
        age_reason = None
        
        # 1. 检查明确的年龄声明
        for pattern in current_age_patterns:
            match = re.search(pattern, intro, re.MULTILINE)
            if match:
                age = int(match.group(1))
                age_reason = f"明确年龄：{match.group(0).strip()}"
                break
        
        # 2. 检查在读状态
        if age is None:
            for pattern, status in student_patterns:
                if re.search(pattern, intro):
                    if '大一' in intro:
                        age = 19
                    elif '大二' in intro:
                        age = 20
                    elif '大三' in intro:
                        age = 21
                    elif '大四' in intro:
                        age = 22
                    elif '研究生' in intro:
                        age = 24
                    elif '博士' in intro:
                        age = 26
                    age_reason = f"{status}在读，推断年龄"
                    break
        
        # 如果没有年龄信息或年龄超过32，跳过
        if age is None or age > 32:
            continue
        
        # 验证海外背景
        is_overseas, evidence = verify_overseas_background(intro)
        
        if not is_overseas:
            continue
        
        # 合并评分信息
        score_info = score_map.get(name, {})
        
        results.append({
            'name': name,
            'age': age,
            'age_reason': age_reason,
            'overseas_evidence': evidence,
            'score': score_info.get('total_score', 0),
            'grade': score_info.get('grade', 'N/A'),
            'intro': intro[:400]
        })
    
    # 按评分排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 保存结果
    with open('final_strict_filtered.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"筛选完成：")
    print(f"  通过筛选：{len(results)} 人")
    print(f"\n通过筛选的人员：")
    for i, p in enumerate(results, 1):
        print(f"{i}. {p['name']} - {p['age']}岁 ({p['age_reason']}) - {p['grade']} ({p['score']}分)")
        print(f"   海外背景：{'; '.join(p['overseas_evidence'])}")
        print()

if __name__ == '__main__':
    filter_candidates()
