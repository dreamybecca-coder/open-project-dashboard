#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
严格筛选v2：32岁以下 + 真实海外留学背景
改进年龄提取逻辑，放宽匹配规则
"""
import json
import re
from datetime import datetime

def extract_age_strict(text):
    """
    严格的年龄提取逻辑 v2
    返回：(年龄, 可信度, 推断依据)
    """
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # 1. 检查工作年限，如果>8年直接排除
    exp_patterns = [
        r'(\d{1,2})\s*年\s*经验',
        r'工作\s*(\d{1,2})\s*年',
        r'从业\s*(\d{1,2})\s*年',
        r'有\s*(\d{1,2})\s*年',
        r'行业.*?(\d{1,2})\s*年',  # "XX行业10年"
    ]
    for pattern in exp_patterns:
        match = re.search(pattern, text)
        if match:
            years = int(match.group(1))
            if years > 8:
                return (None, 0, f"工作经验{years}年，排除")
    
    # 2. 收集所有年龄相关数字
    age_candidates = []
    
    # 2.1 明确的当前年龄声明（最优先）
    age_patterns_high = [
        r'(?:目前|现在|今年)\s*(\d{1,2})\s*岁(?:了)?',  # "目前28岁", "现在30岁了"
        r'年龄[：:]\s*(\d{1,2})',
        r'现年\s*(\d{1,2})\s*岁',
        r'^(\d{1,2})\s*岁$',  # 单独一行的年龄
        r'，\s*(\d{1,2})\s*岁[。，]',  # "，19岁。"
    ]
    for pattern in age_patterns_high:
        for match in re.finditer(pattern, text):
            age = int(match.group(1))
            # 这些模式已经足够明确，直接作为当前年龄
            age_candidates.append((age, 0.95, f"明确年龄：{match.group(0).strip()}"))
    
    # 2.1.2 检查"XX岁XXX"模式，需要排除过去时态
    past_context_keywords = ['赴', '留学', '出国', '那一年', '那年', '时', '的时候']
    age_pattern_general = r'(\d{1,2})\s*岁'
    for match in re.finditer(age_pattern_general, text):
        age = int(match.group(1))
        context_start = max(0, match.start() - 15)
        context_end = min(len(text), match.end() + 15)
        context = text[context_start:context_end]
        
        # 检查是否是过去时态
        is_past = False
        for keyword in past_context_keywords:
            if keyword in context:
                is_past = True
                break
        
        if is_past:
            age_candidates.append((age, 0.2, f"过去年龄：{match.group(0).strip()} (上下文：{context})"))
        else:
            age_candidates.append((age, 0.85, f"当前年龄：{match.group(0).strip()}"))
    
    # 2.2 从出生年份推算
    current_year = 2026
    birth_patterns = [
        r'(\d{4})\s*年\s*出生',
        r'出生于\s*(\d{4})',
        r'(\d{4})\s*年生',
    ]
    for pattern in birth_patterns:
        match = re.search(pattern, text)
        if match:
            birth_year = int(match.group(1))
            age = current_year - birth_year
            if 18 <= age <= 32:
                age_candidates.append((age, 0.9, f"从出生年份推算：{birth_year}年，约{age}岁"))
    
    # 2.3 从毕业年份推算
    grad_patterns = [
        r'(\d{4})\s*年\s*毕业',
        r'(\d{4})\s*届\s*毕业',
    ]
    for pattern in grad_patterns:
        match = re.search(pattern, text)
        if match:
            grad_year = int(match.group(1))
            age = (current_year - grad_year) + 22
            if 18 <= age <= 35:  # 毕业年份推算误差较大，放宽上限
                age_candidates.append((age, 0.6, f"从毕业年份推算：{grad_year}年毕业，约{age}岁"))
    
    # 2.4 从在读状态推算
    if re.search(r'大[一二三四]', text):
        # 大学生，通常18-22岁
        if '大一' in text:
            age_candidates.append((19, 0.7, "大一在读，约19岁"))
        elif '大二' in text:
            age_candidates.append((20, 0.7, "大二在读，约20岁"))
        elif '大三' in text:
            age_candidates.append((21, 0.7, "大三在读，约21岁"))
        elif '大四' in text:
            age_candidates.append((22, 0.7, "大四在读，约22岁"))
    
    # 3. 选择最可信的年龄
    if not age_candidates:
        return (None, 0, "未找到有效年龄信息")
    
    # 按可信度排序
    age_candidates.sort(key=lambda x: x[1], reverse=True)
    best_age, confidence, reason = age_candidates[0]
    
    # 最终验证
    if best_age > 32:
        return (None, 0, f"年龄{best_age}岁，超过32岁")
    
    return (best_age, confidence, reason)

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
    
    # 必须有明确的留学国家/地区
    countries = [
        '美国', '英国', '日本', '韩国', '新加坡', '澳大利亚', '澳洲', '加拿大',
        '德国', '法国', '意大利', '荷兰', '瑞士', '香港', '澳门', '台湾',
        '新西兰', '爱尔兰', '西班牙', '俄罗斯', '早稻田', '哈佛', '牛津', '剑桥'
    ]
    
    country_found = []
    for country in countries:
        if country in text:
            country_found.append(country)
    
    if not country_found:
        return (False, ["未提到具体国家/地区或知名学校"])
    
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
    
    # 检查是否有具体学校名称（加分项）
    school_patterns = [
        r'([^\s,，。]{2,15}大学)',
        r'([^\s,，。]{2,15}学院)',
        r'([^\s,，。]{2,15}University)',
    ]
    schools = []
    for pattern in school_patterns:
        matches = re.findall(pattern, text)
        schools.extend(matches)
    
    if schools:
        evidence.append(f"提到学校：{', '.join(set(schools[:3]))}")
    
    evidence.append(f"国家/地区：{', '.join(country_found[:3])}")
    
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
    rejected = []
    
    for person in raw_data:
        fields = person.get('fields', {})
        name = fields.get('姓名', '')
        intro = fields.get('案主个人介绍', '')
        
        if not intro or len(intro) < 10:
            continue
        
        # 提取年龄
        age, confidence, reason = extract_age_strict(intro)
        
        if age is None or age > 32:
            rejected.append({
                'name': name,
                'reason': reason,
                'type': 'age'
            })
            continue
        
        # 验证海外背景
        is_overseas, evidence = verify_overseas_background(intro)
        
        if not is_overseas:
            rejected.append({
                'name': name,
                'reason': '; '.join(evidence),
                'type': 'overseas'
            })
            continue
        
        # 合并评分信息
        score_info = score_map.get(name, {})
        
        results.append({
            'name': name,
            'age': age,
            'age_confidence': confidence,
            'age_reason': reason,
            'overseas_evidence': evidence,
            'score': score_info.get('total_score', 0),
            'grade': score_info.get('grade', 'N/A'),
            'intro': intro[:300] + '...' if len(intro) > 300 else intro
        })
    
    # 按评分排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 保存结果
    output = {
        'total_candidates': len(raw_data),
        'passed_count': len(results),
        'rejected_count': len(rejected),
        'passed': results,
        'rejected_sample': rejected[:50]  # 保存前50个被拒绝的样本
    }
    
    with open('strict_filtered_v2.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"筛选完成：")
    print(f"  总人数：{len(raw_data)}")
    print(f"  通过筛选：{len(results)} 人")
    print(f"  被拒绝：{len(rejected)} 人")
    print(f"\n通过筛选的人员：")
    for i, p in enumerate(results, 1):
        print(f"{i}. {p['name']} - {p['age']}岁 ({p['age_reason']}) - {p['grade']} ({p['score']}分)")
        print(f"   海外背景：{'; '.join(p['overseas_evidence'])}")
        print()

if __name__ == '__main__':
    filter_candidates()
