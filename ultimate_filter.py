#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版筛选：32岁以下 + 真实海外留学背景
"""
import json
import re
from datetime import datetime

def extract_age_comprehensive(text):
    """
    综合年龄提取，返回(年龄, 可信度, 依据)
    """
    text = text.replace('\n', ' ')
    
    # 1. 明确的当前年龄
    current_patterns = [
        r'(?:目前|现在|今年)\s*(\d{1,2})\s*岁',
        r'年龄[：:]\s*(\d{1,2})',
        r'，\s*(\d{1,2})\s*岁[。，]',
    ]
    
    for pattern in current_patterns:
        match = re.search(pattern, text)
        if match:
            age = int(match.group(1))
            return (age, 0.95, f"明确年龄：{match.group(0).strip()}")
    
    # 2. 在读状态
    if re.search(r'大[一二三四]\s*(?:在读|学生)', text):
        age = 19 if '大一' in text else (20 if '大二' in text else (21 if '大三' in text else 22))
        return (age, 0.8, "大学生在读")
    
    # 3. 从毕业年份推算
    grad_match = re.search(r'(\d{4})\s*年?\s*(?:本科|大学)?毕业', text)
    if grad_match:
        grad_year = int(grad_match.group(1))
        age = 2026 - grad_year + 22
        if 18 <= age <= 35:
            return (age, 0.7, f"{grad_year}年毕业，推断约{age}岁")
    
    # 4. 从"XX岁那一年"推算（过去年龄）
    past_age_match = re.search(r'(\d{1,2})\s*岁\s*(?:那一年|那年)', text)
    if past_age_match:
        past_age = int(past_age_match.group(1))
        # 假设描述的是1-3年前的事
        current_age = past_age + 2  # 平均加2岁
        if 18 <= current_age <= 32:
            return (current_age, 0.6, f"过去年龄{past_age}岁，推算现在约{current_age}岁")
    
    # 5. 博士在读（通常26-30岁）
    if re.search(r'博士(?:在读|就读)', text):
        # 需要进一步检查工作经验
        exp_match = re.search(r'(\d{1,2})\s*年\s*(?:经验|工作|从业)', text)
        if exp_match:
            return (None, 0, "工作经验过长")
        return (28, 0.6, "博士在读，推断约28岁")
    
    return (None, 0, "未找到有效年龄信息")

def verify_overseas_study(text):
    """
    验证真实的海外留学经历
    """
    text = text.replace('\n', ' ')
    
    # 1. 必须有明确的国家/地区或知名海外学校
    countries_or_schools = [
        '日本', '美国', '英国', '韩国', '新加坡', '澳大利亚', '澳洲', '加拿大',
        '德国', '法国', '意大利', '荷兰', '瑞士', '香港', '澳门', '台湾',
        '早稻田', '东京大学', '京都大学', '哈佛', '牛津', '剑桥', '斯坦福'
    ]
    
    found = []
    for item in countries_or_schools:
        if item in text:
            found.append(item)
    
    if not found:
        return (False, "未提到海外国家/地区或知名学校")
    
    # 2. 必须有留学相关动词或学历
    study_patterns = [
        r'留学',
        r'海外.*?(?:学习|读书)',
        r'毕业于',
        r'本科.*毕业',
        r'(?:硕士|博士)',
    ]
    
    has_study = any(re.search(p, text) for p in study_patterns)
    
    if not has_study:
        return (False, f"提到{found[:2]}，但无留学描述")
    
    # 3. 排除：只是业务涉及海外
    business_patterns = [
        r'做.*?的.*?教育',
        r'聚焦.*?市场',
        r'服务.*?客户',
        r'跨境.*?业务',
    ]
    
    # 只有当只有一个地点且匹配业务模式时才排除
    if len(found) == 1:
        for pattern in business_patterns:
            if re.search(pattern, text):
                return (False, f"可能只是业务涉及海外")
    
    return (True, f"国家/学校：{', '.join(found[:3])}")

def main():
    with open('records_raw.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    with open('evaluated_final.json', 'r', encoding='utf-8') as f:
        eval_data = json.load(f)
    
    # 构建评分映射
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
        
        if not intro or len(intro) < 20:
            continue
        
        # 提取年龄
        age, confidence, reason = extract_age_comprehensive(intro)
        
        if not age or age > 32:
            continue
        
        # 排除工作经验>8年
        exp_match = re.search(r'(\d{1,2})\s*年\s*(?:经验|工作|从业)', intro)
        if exp_match and int(exp_match.group(1)) > 8:
            continue
        
        # 验证海外背景
        is_overseas, overseas_reason = verify_overseas_study(intro)
        
        if not is_overseas:
            continue
        
        # 合并评分
        score_info = score_map.get(name, {})
        
        results.append({
            'name': name,
            'age': age,
            'age_reason': reason,
            'overseas_reason': overseas_reason,
            'score': score_info.get('total_score', 0),
            'grade': score_info.get('grade', 'N/A'),
            'intro': intro[:300]
        })
    
    # 按评分排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 保存结果
    with open('final_young_overseas.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"筛选完成：通过{len(results)}人\n")
    for i, p in enumerate(results, 1):
        print(f"{i}. {p['name']} - {p['age']}岁 ({p['age_reason']})")
        print(f"   海外背景：{p['overseas_reason']}")
        print(f"   评分：{p['grade']} ({p['score']}分)")
        print(f"   简介：{p['intro'][:100]}...")
        print()
    
    return results

if __name__ == '__main__':
    main()
