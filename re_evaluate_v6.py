#!/usr/bin/env python3
"""
重新评估脚本 V6：100分制，精简版
- 严格筛选，确保TOP 20是真正值得关注的
"""

import json
import re

def extract_years(text):
    if not text:
        return 0
    patterns = [r'(\d+)\s*年', r'经验\s*(\d+)\s*年']
    years = []
    for p in patterns:
        matches = re.findall(p, text)
        years.extend([int(m) for m in matches if int(m) <= 50])
    return max(years) if years else 0

def calc_person_score(project):
    intro = project.get('intro', '') or ''
    project_intro = project.get('projectIntro', '') or ''
    text = (intro + project_intro).lower()

    scores = {}

    # P1 实战经验 (0-10分)
    years = extract_years(intro)
    p1 = min(years / 2, 10)
    scores['p1_exp'] = p1

    # P2 国际视野 (0-10分)
    p2 = 0
    global500 = ['500强', '联合利华', '高露洁', '玛氏', '宝洁', '可口可乐', '百事',
                 '微软', 'google', '苹果', '亚马逊', 'IBM', 'Intel',
                 '波士顿', '麦肯锡', '贝恩', '罗兰贝格', '德勤', '普华永道', '安永', '毕马威']
    for kw in global500:
        if kw.lower() in text:
            p2 += 1.5
            if p2 >= 6:
                break
    overseas = ['海外', '留学', '海归', '跨境', '国际', 'global', 'international']
    for kw in overseas:
        if kw in text:
            p2 += 1
            if p2 >= 9:
                break
    scores['p2_intl'] = min(p2, 10)

    # P3 业务成绩 (0-15分)
    p3 = 0
    pct_changes = []

    # 百分比提升
    matches = re.findall(r'从\s*(\d+)\s*%.*?提升.*?(\d+)\s*%', text)
    for m in matches:
        pct_changes.append(int(m[1]) - int(m[0]))
    matches = re.findall(r'(?:增长|提升|提高|提升至)\s*(\d+)\s*%', text)
    pct_changes.extend([int(m) for m in matches])
    matches = re.findall(r'占比[达从]?\s*(\d+)\s*%', text)
    pct_changes.extend([int(m) for m in matches])

    max_pct = max(pct_changes) if pct_changes else 0
    if max_pct >= 200: p3 += 10
    elif max_pct >= 100: p3 += 7
    elif max_pct >= 50: p3 += 5
    elif max_pct >= 20: p3 += 3
    elif max_pct >= 10: p3 += 2
    elif max_pct > 0: p3 += 1

    # 营收
    revenue = re.findall(r'(\d+)\s*亿', text)
    if revenue: p3 += 5
    else:
        revenue = re.findall(r'(\d+)\s*千万', text)
        if revenue: p3 += 3

    # 规模
    if re.search(r'\d+\s*万\s*用户', text): p3 += 3
    elif re.search(r'\d+\s*千家|\d+\s*千店', text): p3 += 2
    scores['p3_achieve'] = min(p3, 15)

    # P4 专业能力 (0-8分)
    p4 = 0
    if re.search(r'(ceo|cto|cfo|vp|总经理|总裁|总监|负责人|coo)', text): p4 += 3
    if re.search(r'(硕士|博士|mba|认证|资质)', text): p4 += 2
    scores['p4_prof'] = min(p4, 8)

    # P5 创业基因 (0-7分)
    p5 = 0
    if any(kw in text for kw in ['创始人', 'co-founder', '联合创始人']): p5 += 4
    if '连续创业' in text or 'all in' in text: p5 += 2
    elif '创业' in text: p5 += 1
    scores['p5_entre'] = min(p5, 7)

    total = p1 + p2 + p3 + p4 + p5
    scores['score'] = round(total, 1)
    return scores

def calc_project_score(project):
    scores = project.get('scores', {})
    d1 = (scores.get('d4', 0) / 5.0) * 15
    d2 = ((scores.get('d2', 0) + scores.get('d3', 0)) / 2 / 5.0) * 15
    d3 = (scores.get('d6', 0) / 5.0) * 10
    d4 = (scores.get('d5', 0) / 5.0) * 10
    total = d1 + d2 + d3 + d4
    return {
        'score': round(total, 1),
        'd1_related': round(d1, 1),
        'd2_mature': round(d2, 1),
        'd3_collab': round(d3, 1),
        'd4_learn': round(d4, 1),
    }

def determine_grade(total, person):
    """更严格的分级"""
    # 必须人评>=25分才有资格评A级以上
    if total >= 75 and person >= 25:
        return 'S+', '必听'
    elif total >= 70 and person >= 22:
        return 'S', '强烈推荐'
    elif total >= 65:
        return 'A', '优先关注'
    elif total >= 58:
        return 'B', '值得一看'
    elif total >= 50:
        return 'C', '一般'
    else:
        return 'D', '跳过'

def re_evaluate_all():
    with open('evaluated_projects_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    projects = data.get('projects', [])
    print(f"共 {len(projects)} 个项目，开始重新评估...")

    evaluated = []
    for p in projects:
        person = calc_person_score(p)
        project_score = calc_project_score(p)
        total = round(person['score'] + project_score['score'], 1)
        grade, grade_reason = determine_grade(total, person['score'])

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
            'personDetail': person,
            'projectDetail': project_score,
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
            print(f"  {g}: {grade_counts[g]}个")

    # 计算TOP数量
    top_20_cutoff = evaluated[19]['score100'] if len(evaluated) >= 20 else 0
    print(f"\nTOP 20 门槛分数: {top_20_cutoff:.1f}分")

    # 输出TOP 20
    print(f"\n{'='*140}")
    print(f"{'TOP 20 核心项目 (100分制)':^140}")
    print(f"{'='*140}")
    print(f"{'序':<3} {'姓名':<10} {'总分':<6} {'人评':<5} | P1经 P2国 P3绩 P4能 P5创 | {'项评':<5} | D1相 D2熟 D3协 D4学 | {'等级'}")
    print(f"{'-'*140}")

    for p in evaluated[:20]:
        pd = p['personDetail']
        pj = p['projectDetail']
        print(f"{p['rank']:<3} {p['name']:<10} {p['score100']:<6.1f} "
              f"人:{p['personScore']:<4.1f} | {pd['p1_exp']:3.0f}  {pd['p2_intl']:3.0f}  {pd['p3_achieve']:3.0f}  {pd['p4_prof']:3.0f}  {pd['p5_entre']:3.0f} | "
              f"项:{p['projectScore']:<4.1f} | {pj['d1_related']:4.0f}  {pj['d2_mature']:4.0f}  {pj['d3_collab']:4.0f}  {pj['d4_learn']:4.0f} | "
              f"{p['grade']} {p['gradeReason']}")

    # 保存
    result = {'projects': evaluated}
    with open('evaluated_projects_v3.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 evaluated_projects_v3.json")

    return evaluated

if __name__ == '__main__':
    re_evaluate_all()
