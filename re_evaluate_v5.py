#!/usr/bin/env python3
"""
重新评估脚本 V5：100分制，包含人评+项评（修复版）
修复了业务成绩的评估逻辑
"""

import json
import re

def extract_years(text):
    """提取工作年限"""
    if not text:
        return 0
    patterns = [
        r'(\d+)\s*年\s*(?:以上|实战|经验|深耕)?',
        r'(\d+)\s*年以上',
        r'经验\s*(\d+)\s*年',
    ]
    years = []
    for p in patterns:
        matches = re.findall(p, text)
        years.extend([int(m) for m in matches if int(m) <= 50])
    return max(years) if years else 0

def calc_person_score(project):
    """计算人的综合得分(0-50分)"""
    intro = project.get('intro', '') or ''
    project_intro = project.get('projectIntro', '') or ''
    text = (intro + project_intro).lower()

    scores = {}

    # P1 实战经验 (0-10分)
    years = extract_years(intro)
    if years >= 20:
        p1 = 10
    elif years >= 15:
        p1 = 8
    elif years >= 10:
        p1 = 6
    elif years >= 5:
        p1 = 4
    elif years >= 2:
        p1 = 2
    else:
        p1 = 1
    scores['p1_exp'] = p1

    # P2 国际视野 (0-10分)
    p2 = 0
    global500 = ['500强', 'fortune', '联合利华', '高露洁', '玛氏', '宝洁', '可口可乐',
                 '百事', '微软', 'google', '苹果', '亚马逊', 'IBM', 'Intel',
                 '波士顿', '麦肯锡', '贝恩', '罗兰贝格', '德勤', '普华永道', '安永', '毕马威',
                 '西门子', 'ABB', '蒂森', 'GE', '雀巢']
    for kw in global500:
        if kw.lower() in text:
            p2 += 2
            if p2 >= 6:
                break

    overseas = ['海外', '留学', '海归', '跨境', '国际业务', '亚太', '欧洲', '北美',
                'global', 'international', 'overseas']
    for kw in overseas:
        if kw in text:
            p2 += 1
            if p2 >= 9:
                break
    scores['p2_intl'] = min(p2, 10)

    # P3 业务成绩 (0-15分) - 修复版
    p3 = 0

    # 提取所有百分比变化
    pct_changes = []

    # 匹配 "从X%提升到Y%" 或 "从X%提升至Y%"
    matches = re.findall(r'从\s*(\d+)\s*%.*?提升.*?(\d+)\s*%', text)
    for m in matches:
        increase = int(m[1]) - int(m[0])
        pct_changes.append(increase)

    # 匹配 "提升到X%" 或 "提升至X%"
    matches = re.findall(r'提升[至到]?\s*(\d+)\s*%', text)
    for m in matches:
        pct_changes.append(int(m))

    # 匹配 "增长X%" 或 "提升X%"
    matches = re.findall(r'(?:增长|提升|提高)\s*(\d+)\s*%', text)
    for m in matches:
        pct_changes.append(int(m))

    # 匹配 "占比X%"
    matches = re.findall(r'占比[达从]?\s*(\d+)\s*%', text)
    for m in matches:
        pct_changes.append(int(m))

    # 匹配 "分销达X%"
    matches = re.findall(r'分销[达]?\s*(\d+)\s*%', text)
    for m in matches:
        pct_changes.append(int(m))

    # 计算业务成绩分数
    max_pct = max(pct_changes) if pct_changes else 0
    if max_pct >= 200:
        p3 += 8
    elif max_pct >= 100:
        p3 += 6
    elif max_pct >= 50:
        p3 += 4
    elif max_pct >= 20:
        p3 += 3
    elif max_pct >= 10:
        p3 += 2
    elif max_pct >= 5:
        p3 += 1

    # 营收数字 (5分)
    revenue = re.findall(r'(\d+)\s*[亿万千]?\s*营[收]?', text)
    for r in revenue:
        val = int(r)
        if val >= 1:
            p3 += 5
            break
        elif val >= 1000:
            p3 += 4
            break
        elif val >= 100:
            p3 += 3
            break
        elif val >= 10:
            p3 += 2
            break

    # 规模覆盖 (4分)
    scale_patterns = [
        (r'(\d+)\s*万\s*用户', 4),
        (r'(\d+)\s*[千萬万]\+?\s*客户', 3),
        (r'(\d+)\s*[千百]\s*家?\s*店', 2),
        (r'(\d{3,})\s*家', 2),  # 3位数以上的"家"
    ]
    for p, pts in scale_patterns:
        if re.search(p, text):
            p3 += pts
            break
    scores['p3_achieve'] = min(p3, 15)

    # P4 专业能力 (0-8分)
    p4 = 0
    exec_kw = ['ceo', 'cto', 'cfo', 'vp', '总经理', '总裁', '总监', '负责人',
                'coo', '首席', '高管']
    for kw in exec_kw:
        if kw.lower() in text:
            p4 += 2
            if p4 >= 4:
                break

    prof_kw = ['硕士', '博士', 'mba', '认证', '资质', '专家', '架构师',
                '工程师', '顾问']
    for kw in prof_kw:
        if kw in text:
            p4 += 1
            if p4 >= 6:
                break
    scores['p4_prof'] = min(p4, 8)

    # P5 创业基因 (0-7分)
    p5 = 0
    if any(kw in text for kw in ['创始人', 'co-founder', '联合创始人', '创业合伙人']):
        p5 += 3
    elif '创业' in text:
        p5 += 2

    if '连续创业' in text or '多次创业' in text or 'all in' in text:
        p5 += 2
    elif '创业' in text:
        p5 += 1

    if any(kw in text for kw in ['all in', '辞职', '全职创业', '押上', '押注']):
        p5 += 2
    elif '创业' in text:
        p5 += 1
    scores['p5_entre'] = min(p5, 7)

    total = p1 + p2 + p3 + p4 + p5
    scores['score'] = round(total, 1)
    return scores

def calc_project_score(project):
    """计算项目得分(0-50分)"""
    scores = project.get('scores', {})

    # D1 领域相关度 (0-15分)
    d1 = (scores.get('d4', 0) / 5.0) * 15

    # D2 项目成熟度 (0-15分)
    d2 = ((scores.get('d2', 0) + scores.get('d3', 0)) / 2 / 5.0) * 15

    # D3 协同价值 (0-10分)
    d3 = (scores.get('d6', 0) / 5.0) * 10

    # D4 学习价值 (0-10分)
    d4 = (scores.get('d5', 0) / 5.0) * 10

    total = d1 + d2 + d3 + d4
    return {
        'score': round(total, 1),
        'd1_related': round(d1, 1),
        'd2_mature': round(d2, 1),
        'd3_collab': round(d3, 1),
        'd4_learn': round(d4, 1),
    }

def determine_grade(total):
    """基于100分制确定等级"""
    if total >= 85:
        return 'S+', '必听'
    elif total >= 75:
        return 'S', '强烈推荐'
    elif total >= 65:
        return 'A', '优先关注'
    elif total >= 55:
        return 'B', '值得一看'
    elif total >= 45:
        return 'C', '一般'
    else:
        return 'D', '跳过'

def re_evaluate_all():
    """重新评估所有项目"""
    with open('evaluated_projects_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    projects = data.get('projects', [])
    print(f"共 {len(projects)} 个项目，开始重新评估...")

    evaluated = []

    for p in projects:
        person = calc_person_score(p)
        project_score = calc_project_score(p)
        total = round(person['score'] + project_score['score'], 1)
        grade, grade_reason = determine_grade(total)

        evaluated_p = {
            'id': p['id'],
            'name': p['name'],
            'region': p.get('region', ''),
            'registerType': p.get('registerType', ''),
            'credits': p.get('credits', 0),
            'directions': p.get('directions', []),

            'score100': total,
            'personScore': person['score'],
            'projectScore': project_score['score'],

            'personDetail': {
                'p1_exp': person['p1_exp'],
                'p2_intl': person['p2_intl'],
                'p3_achieve': person['p3_achieve'],
                'p4_prof': person['p4_prof'],
                'p5_entre': person['p5_entre'],
            },

            'projectDetail': {
                'd1_related': project_score['d1_related'],
                'd2_mature': project_score['d2_mature'],
                'd3_collab': project_score['d3_collab'],
                'd4_learn': project_score['d4_learn'],
            },

            'grade': grade,
            'gradeReason': grade_reason,

            'scores': p.get('scores', {}),
            'reasons': p.get('reasons', {}),
            'summary': p.get('summary', ''),
            'intro': p.get('intro', ''),
            'projectIntro': p.get('projectIntro', ''),
            'plan': p.get('plan', ''),
            'story': p.get('story', ''),
            'tags': p.get('tags', []),
        }

        evaluated.append(evaluated_p)

    evaluated.sort(key=lambda x: x['score100'], reverse=True)

    for i, p in enumerate(evaluated, 1):
        p['rank'] = i

    # 统计
    grade_counts = {}
    for p in evaluated:
        g = p['grade']
        grade_counts[g] = grade_counts.get(g, 0) + 1

    print(f"\n=== 评估完成 ===")
    print(f"总项目数: {len(evaluated)}")
    print(f"\n等级分布:")
    for g in ['S+', 'S', 'A', 'B', 'C', 'D']:
        if g in grade_counts:
            print(f"  {g}: {grade_counts[g]}个 ({grade_counts[g]/len(evaluated)*100:.1f}%)")

    # 输出TOP 25
    print(f"\n{'='*130}")
    print(f"{'TOP 25 核心项目 (100分制)':^130}")
    print(f"{'='*130}")
    print(f"{'序':<3} {'姓名':<8} {'总分':<5} {'人评明细(满分50)':<45} {'项评':<6} {'等级'}")
    print(f"{'-'*130}")

    for p in evaluated[:25]:
        pd = p['personDetail']
        person_detail_str = f"经:{pd['p1_exp']:.0f} 国:{pd['p2_intl']:.0f} 绩:{pd['p3_achieve']:.0f} 能:{pd['p4_prof']:.0f} 创:{pd['p5_entre']:.0f}"
        print(f"{p['rank']:<3} {p['name']:<8} {p['score100']:<5.1f} "
              f"人:{p['personScore']:<4.1f}({person_detail_str}) 项:{p['projectScore']:<4.1f} {p['grade']} {p['gradeReason']}")

    # 保存
    result = {'projects': evaluated}
    with open('evaluated_projects_v3.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 evaluated_projects_v3.json")

    return evaluated

if __name__ == '__main__':
    re_evaluate_all()
