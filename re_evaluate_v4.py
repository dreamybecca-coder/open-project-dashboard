#!/usr/bin/env python3
"""
重新评估脚本 V4：100分制，包含人评+项评（调整版）
- 人评(50分)：更精准地评估创始人能力
- 项评(50分)：更严格的评估标准

评分标准：
- S+: 85+ 顶尖人才+优质项目
- S:  75-85 优秀人才+好项目
- A:  65-75 值得关注
- B:  55-65 一般
- C:  45-55 偏弱
- D:  <45 不推荐
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
    # 基于实际工作年限和行业专注度
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
    # 评估外企、跨国、国际业务经验
    p2 = 0

    # 500强/顶级外企 (5分)
    global500 = ['500强', 'fortune', '联合利华', '高露洁', '玛氏', '宝洁', '可口可乐',
                 '百事', '微软', 'google', '苹果', '亚马逊', 'IBM', 'Intel', 'Intel',
                 '波士顿', '麦肯锡', '贝恩', '罗兰贝格', '德勤', '普华永道', '安永', '毕马威',
                 '西门子', 'ABB', '蒂森', 'GE', '雀巢', '亿滋', '卡夫']
    for kw in global500:
        if kw.lower() in text:
            p2 += 2
            if p2 >= 5:
                break

    # 海外/国际化经验 (3分)
    overseas = ['海外', '留学', '海归', '跨境', '国际业务', '亚太', '欧洲', '北美',
                'global', 'international', 'overseas']
    for kw in overseas:
        if kw in text:
            p2 += 1
            if p2 >= 8:
                break

    # 国际化视野描述 (2分)
    vision = ['国际', '全球化', '世界观', '海外市场', '多语言']
    for kw in vision:
        if kw in text:
            p2 += 0.5
    scores['p2_intl'] = min(p2, 10)

    # P3 业务成绩 (0-15分)
    # 基于具体数字成果
    p3 = 0

    # 大额营收 (5分)
    revenue = re.findall(r'(\d+)\s*[亿万千]?\s*营[收]?', text)
    for r in revenue:
        val = int(r)
        if val >= 1:  # 亿级
            p3 += 5
            break
        elif val >= 1000:  # 千万级
            p3 += 4
            break
        elif val >= 100:  # 百万级
            p3 += 3
            break

    # 显著增长/提升 (5分)
    growth = re.findall(r'增长\s*(\d+)%', text)
    for g in growth:
        val = int(g)
        if val >= 200:
            p3 += 5
            break
        elif val >= 100:
            p3 += 4
            break
        elif val >= 50:
            p3 += 3
            break
        elif val >= 20:
            p3 += 2
            break

    # 规模覆盖 (5分)
    scale_patterns = [
        (r'(\d+)\s*万\s*用户', 5),
        (r'(\d+)\s*[千萬万]\+?\s*客户', 4),
        (r'(\d+)\s*[千百]\s*家?\s*店', 3),
        (r'覆盖\s*(\d+)\s*个?城', 3),
        (r'(\d+)\s*[千萬万]\s*[营?收]', 4),
    ]
    for p, pts in scale_patterns:
        if re.search(p, text):
            p3 += pts
            break
    scores['p3_achieve'] = min(p3, 15)

    # P4 专业能力 (0-8分)
    p4 = 0

    # 高管职位 (4分)
    exec_kw = ['ceo', 'cto', 'cfo', 'vp', '总经理', '总裁', '总监', '负责人',
                'coo', 'cmO', '首席', '高管', '管理']
    for kw in exec_kw:
        if kw.lower() in text:
            p4 += 2
            if p4 >= 4:
                break

    # 专业背景 (2分)
    prof_kw = ['硕士', '博士', 'mba', '认证', '资质', '专家', '架构师',
                '工程师', '顾问', '咨询师']
    for kw in prof_kw:
        if kw in text:
            p4 += 1
            if p4 >= 6:
                break

    # 技术能力 (2分)
    tech_kw = ['技术', '开发', '代码', '编程', '产品', '运营', '市场', '销售', '财务']
    tech_count = sum(1 for kw in tech_kw if kw in text)
    p4 += min(tech_count // 2, 2)
    scores['p4_prof'] = min(p4, 8)

    # P5 创业基因 (0-7分)
    p5 = 0

    # 创始人身份 (3分)
    if any(kw in text for kw in ['创始人', 'co-founder', '联合创始人', '创业合伙人']):
        p5 += 3
    elif '创业' in text:
        p5 += 2

    # 连续创业 (2分)
    if '连续创业' in text or '多次创业' in text or 'all in' in text:
        p5 += 2
    elif '创业' in text:
        p5 += 1

    # 承担风险/全职投入 (2分)
    if any(kw in text for kw in ['all in', '辞职', '全职创业', '押上', '押注']):
        p5 += 2
    elif '创业' in text:
        p5 += 1
    scores['p5_entre'] = min(p5, 7)

    # 总分
    total = p1 + p2 + p3 + p4 + p5
    scores['score'] = round(total, 1)
    return scores

def calc_project_score(project):
    """计算项目得分(0-50分)"""
    scores = project.get('scores', {})
    original_total = project.get('totalScore', 0)

    # D1 领域相关度 (0-15分) - 使用d4，5分满分映射到15
    d1 = (scores.get('d4', 0) / 5.0) * 15

    # D2 项目成熟度 (0-15分) - d2+d3平均，5分映射到15
    d2 = ((scores.get('d2', 0) + scores.get('d3', 0)) / 2 / 5.0) * 15

    # D3 协同价值 (0-10分) - d6，5分映射到10
    d3 = (scores.get('d6', 0) / 5.0) * 10

    # D4 学习价值 (0-10分) - d5，5分映射到10
    d4 = (scores.get('d5', 0) / 5.0) * 10

    total = d1 + d2 + d3 + d4
    return {
        'score': round(total, 1),
        'd1_related': round(d1, 1),
        'd2_mature': round(d2, 1),
        'd3_collab': round(d3, 1),
        'd4_learn': round(d3, 1),
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
        # 计算人评和项评
        person = calc_person_score(p)
        project_score = calc_project_score(p)

        # 总分 = 人评 + 项评
        total = round(person['score'] + project_score['score'], 1)

        # 确定等级
        grade, grade_reason = determine_grade(total)

        evaluated_p = {
            'id': p['id'],
            'name': p['name'],
            'region': p.get('region', ''),
            'registerType': p.get('registerType', ''),
            'credits': p.get('credits', 0),
            'directions': p.get('directions', []),

            # 100分制评分
            'score100': total,
            'personScore': person['score'],
            'projectScore': project_score['score'],

            # 人评明细 (5维度)
            'personDetail': {
                'p1_exp': person['p1_exp'],      # 实战经验 (0-10)
                'p2_intl': person['p2_intl'],   # 国际视野 (0-10)
                'p3_achieve': person['p3_achieve'],  # 业务成绩 (0-15)
                'p4_prof': person['p4_prof'],    # 专业能力 (0-8)
                'p5_entre': person['p5_entre'],  # 创业基因 (0-7)
            },

            # 项评明细 (4维度)
            'projectDetail': {
                'd1_related': project_score['d1_related'],  # 领域相关 (0-15)
                'd2_mature': project_score['d2_mature'],    # 项目成熟 (0-15)
                'd3_collab': project_score['d3_collab'],    # 协同价值 (0-10)
                'd4_learn': project_score['d4_learn'],       # 学习价值 (0-10)
            },

            # 等级
            'grade': grade,
            'gradeReason': grade_reason,

            # 原有数据
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

    # 按总分排序
    evaluated.sort(key=lambda x: x['score100'], reverse=True)

    # 添加排名
    for i, p in enumerate(evaluated, 1):
        p['rank'] = i

    # 统计各等级数量
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

    # 输出TOP 20
    print(f"\n{'='*120}")
    print(f"{'TOP 20 核心项目 (100分制)':^120}")
    print(f"{'='*120}")
    print(f"{'序号':<4} {'姓名':<8} {'总分':<6} {'人评':<5} {'项评':<5} {'等级':<4} {'说明'}")
    print(f"{'-'*120}")

    for p in evaluated[:20]:
        pd = p['personDetail']
        print(f"{p['rank']:<4} {p['name']:<8} {p['score100']:<6.1f} "
              f"人:{p['personScore']:<4.1f}(经:{pd['p1_exp']:.0f} 国:{pd['p2_intl']:.0f} 绩:{pd['p3_achieve']:.0f} 能:{pd['p4_prof']:.0f} 创:{pd['p5_entre']:.0f}) "
              f"项:{p['projectScore']:<4.1f} "
              f"{p['grade']} {p['gradeReason']}")

    # 保存结果
    result = {'projects': evaluated}
    with open('evaluated_projects_v3.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 evaluated_projects_v3.json")

    return evaluated

if __name__ == '__main__':
    re_evaluate_all()
