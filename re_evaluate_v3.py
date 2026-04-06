#!/usr/bin/env python3
"""
重新评估脚本：100分制，包含人评+项评
人评(50分)：P1实战经验、P2国际视野、P3业务成绩、P4专业能力、P5创业基因
项评(50分)：D1领域相关、D2项目成熟、D3协同价值、D4学习价值
"""

import json
import re

def extract_years(text):
    """提取工作年限"""
    if not text:
        return 0
    # 匹配 "20年"、"16年+"、"10年以上" 等模式
    patterns = [
        r'(\d+)\s*年\s*(?:以上|实战|经验|深耕)?',
        r'(\d+)\s*年以上',
        r'(\d+)\s*年\s*(?:大|届)?',
    ]
    years = []
    for p in patterns:
        matches = re.findall(p, text)
        years.extend([int(m) for m in matches if int(m) <= 50])
    return max(years) if years else 0

def extract_international_score(text):
    """评估国际视野得分(0-8分)"""
    if not text:
        return 0
    score = 0
    text_lower = text.lower()

    # 世界500强、外企 (3分)
    global_keywords = [
        '500强', 'fortune', '外企', '跨国', '外资', '合资',
        '联合利华', '高露洁', '玛氏', '宝洁', '可口可乐', '百事',
        ' Unilever', 'P&G', 'Nestle', 'coca-cola',
        '微软', 'google', '苹果', '亚马逊', 'IBM', 'Intel',
        '波士顿', '麦肯锡', '贝恩', '罗兰贝格', '四大',
        '德勤', '普华永道', '安永', '毕马威', 'KPMG', 'PwC', 'EY',
        '联合技术', 'GE', '西门子', 'ABB', '蒂森克虏伯',
        '腾讯', '阿里', '字节', '字节跳动', '华为',
    ]
    for kw in global_keywords:
        if kw.lower() in text_lower:
            score += 1
            if score >= 3:
                break

    # 海外经历 (2分)
    overseas_keywords = ['海外', '出境', '留学', '海归', '跨境', ' international', 'global', 'overseas']
    for kw in overseas_keywords:
        if kw.lower() in text_lower:
            score += 1
            if score >= 5:
                break

    # 国际化业务 (2分)
    intl_biz = ['全球', '国际市场', '海外市场', '亚太', '欧洲', '北美业务', 'worldwide']
    for kw in intl_biz:
        if kw.lower() in text_lower:
            score += 1
            if score >= 7:
                break

    return min(score, 8)

def extract_achievement_score(text):
    """评估业务成绩得分(0-12分) - 基于具体数字"""
    if not text:
        return 0
    score = 0
    text_lower = text.lower()

    # 营收/流水 (4分)
    revenue_patterns = [
        r'(\d+)\s*[亿万千百]?\s*营收',
        r'年?营[业收]?\s*[达]?\s*(\d+)\s*[亿万千]?',
        r'(\d+)\s*[亿万千]?\s*流水',
        r'gmv\s*(\d+)',
        r'交易额\s*(\d+)',
    ]
    for p in revenue_patterns:
        matches = re.findall(p, text_lower)
        for m in matches:
            val = int(m)
            if val >= 1:  # 1亿以上
                score += 4
                break
            elif val >= 1000:  # 1000万以上
                score += 3
                break
            elif val >= 100:  # 100万以上
                score += 2
                break

    # 增长/提升百分比 (3分)
    growth_patterns = [
        r'增长\s*(\d+)%',
        r'提升\s*(\d+)%',
        r'提高\s*(\d+)%',
        r'增长\s*(\d+)\s*倍',
        r'提升\s*(\d+)\s*倍',
    ]
    for p in growth_patterns:
        matches = re.findall(p, text_lower)
        for m in matches:
            val = int(m)
            if val >= 100:  # 100%以上
                score += 3
                break
            elif val >= 50:  # 50%以上
                score += 2
                break
            elif val >= 10:  # 10%以上
                score += 1
                break

    # 规模/覆盖 (3分)
    scale_keywords = [
        (r'(\d+)\s*[千萬万]\+?\s*客户', 3),
        (r'(\d+)\s*[千百]\s*家?\s*[企业门店]', 2),
        (r'覆盖\s*(\d+)\s*个?城', 2),
        (r'(\d+)\s*万\s*用户', 2),
        (r'(\d+)\s*[千百]\s*人\s*团', 1),
    ]
    for p, pts in scale_keywords:
        if re.search(p, text_lower):
            score += pts

    # MVP/付费/商业化 (2分)
    biz_keywords = ['付费', '收费', '营收', '变现', '商业化', '盈利', '赚钱', '月收入', '年收']
    for kw in biz_keywords:
        if kw in text_lower:
            score += 1
            break

    return min(score, 12)

def extract_professional_score(text):
    """评估专业能力得分(0-10分)"""
    if not text:
        return 0
    score = 0
    text_lower = text.lower()

    # 高管/管理层 (4分)
    exec_keywords = ['ceo', 'cto', 'cfo', 'coo', 'vp', '总经理', '总裁', '总监', '负责人', '合伙人', '创始人', ' CMO']
    for kw in exec_keywords:
        if kw.lower() in text_lower:
            score += 1
            if score >= 4:
                break

    # 专业背景/资质 (3分)
    cert_keywords = [
        '认证', '资质', '专家', '资深', '高级',
        'mba', '硕士', '博士', '研究生',
        'cto', '架构师', '技术', '工程师',
        '顾问', '咨询师', '分析师',
    ]
    for kw in cert_keywords:
        if kw.lower() in text_lower:
            score += 0.5
            if score >= 7:
                break

    # 行业经验 (3分)
    if extract_years(text) >= 10:
        score += 3
    elif extract_years(text) >= 5:
        score += 2
    elif extract_years(text) >= 2:
        score += 1

    return min(score, 10)

def extract_entrepreneur_score(text, project_intro):
    """评估创业基因得分(0-10分)"""
    if not text:
        return 0
    score = 0
    text_lower = (text or '').lower()
    project_lower = (project_intro or '').lower()

    # 创始人/合伙人 (4分)
    founder_keywords = ['创始人', 'co-founder', '联合创始人', '创业', '创业中']
    for kw in founder_keywords:
        if kw.lower() in text_lower or kw.lower() in project_lower:
            score += 2
            if score >= 4:
                break

    # 连续创业 (3分)
    if '连续创业' in text_lower or '多次创业' in text_lower or 'all in' in text_lower:
        score += 3
    elif '创业' in text_lower:
        score += 2

    # 内部创业/创新 (2分)
    innovation_keywords = ['内部创业', '创新项目', '内部创新', '新业务']
    for kw in innovation_keywords:
        if kw in text_lower:
            score += 1
            break

    # 承担风险 (1分)
    risk_keywords = ['all in', '押注', '辞职创业', '全职创业', '放弃', '押上']
    for kw in risk_keywords:
        if kw in text_lower:
            score += 1
            break

    return min(score, 10)

def calc_person_score(project):
    """计算人的综合得分(0-50分)"""
    intro = project.get('intro', '') or ''
    project_intro = project.get('projectIntro', '') or ''

    p1_exp = min(extract_years(intro) / 2, 10)  # 20年=10分
    p2_intl = extract_international_score(intro)
    p3_achieve = extract_achievement_score(intro + project_intro)
    p4_prof = extract_professional_score(intro)
    p5_entre = extract_entrepreneur_score(intro, project_intro)

    person_score = p1_exp + p2_intl + p3_achieve + p4_prof + p5_entre

    return {
        'score': round(person_score, 1),
        'p1_exp': round(p1_exp, 1),
        'p2_intl': round(p2_intl, 1),
        'p3_achieve': round(p3_achieve, 1),
        'p4_prof': round(p4_prof, 1),
        'p5_entre': round(p5_entre, 1),
    }

def calc_project_score(project, rebecca_keywords):
    """计算项目得分(0-50分)"""
    scores = project.get('scores', {})
    total = project.get('totalScore', 0)

    # D1: 领域相关度 - 使用原有的d4分数，映射到15分
    d1_related = (scores.get('d4', 0) / 5.0) * 15

    # D2: 项目成熟度 - 使用原有的d2和d3，映射到10分
    d2_mature = ((scores.get('d2', 0) + scores.get('d3', 0)) / 2 / 5.0) * 10

    # D3: 协同价值 - 使用原有的d6，映射到10分
    d3_collab = (scores.get('d6', 0) / 5.0) * 10

    # D4: 学习价值 - 使用原有的d5，映射到15分
    d4_learn = (scores.get('d5', 0) / 5.0) * 15

    project_score = d1_related + d2_mature + d3_collab + d4_learn

    return {
        'score': round(project_score, 1),
        'd1_related': round(d1_related, 1),
        'd2_mature': round(d2_mature, 1),
        'd3_collab': round(d3_collab, 1),
        'd4_learn': round(d4_learn, 1),
    }

def determine_grade_v3(total_score, person_score, project_score):
    """基于100分制确定等级"""
    if total_score >= 90:
        return 'S+', '必听'
    elif total_score >= 80:
        return 'S', '强烈推荐'
    elif total_score >= 70:
        return 'A', '优先关注'
    elif total_score >= 60:
        return 'B', '值得一看'
    elif total_score >= 50:
        return 'C', '一般'
    else:
        return 'D', '跳过'

def re_evaluate_all():
    """重新评估所有项目"""
    # 读取数据
    with open('evaluated_projects_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    projects = data.get('projects', [])
    print(f"共 {len(projects)} 个项目，开始重新评估...")

    # Rebecca的关键方向
    rebecca_keywords = ['AI', '出海', '创业', '产品', '增长', '内容', 'B2B', 'SaaS', '工具']

    evaluated = []

    for p in projects:
        # 计算人评和项评
        person = calc_person_score(p)
        project = calc_project_score(p, rebecca_keywords)

        # 总分 = 人评50% + 项评50%
        total = round(person['score'] + project['score'], 1)

        # 确定等级
        grade, grade_reason = determine_grade_v3(total, person['score'], project['score'])

        evaluated_p = {
            'id': p['id'],
            'name': p['name'],
            'region': p.get('region', ''),
            'registerType': p.get('registerType', ''),
            'credits': p.get('credits', 0),
            'directions': p.get('directions', []),

            # 新的100分制评分
            'score100': total,
            'personScore': person['score'],  # 人评总分
            'projectScore': project['score'],  # 项评总分

            # 人评明细
            'personDetail': {
                'p1_exp': person['p1_exp'],  # 实战经验
                'p2_intl': person['p2_intl'],  # 国际视野
                'p3_achieve': person['p3_achieve'],  # 业务成绩
                'p4_prof': person['p4_prof'],  # 专业能力
                'p5_entre': person['p5_entre'],  # 创业基因
            },

            # 项评明细
            'projectDetail': {
                'd1_related': project['d1_related'],  # 领域相关
                'd2_mature': project['d2_mature'],  # 项目成熟度
                'd3_collab': project['d3_collab'],  # 协同价值
                'd4_learn': project['d4_learn'],  # 学习价值
            },

            # 原有的scores保留
            'scores': p.get('scores', {}),
            'reasons': p.get('reasons', {}),

            # 等级
            'grade': grade,
            'gradeReason': grade_reason,

            # 原有内容
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

    print("\n=== 评估完成 ===")
    print(f"总项目数: {len(evaluated)}")
    print("\n等级分布:")
    for g in ['S+', 'S', 'A', 'B', 'C', 'D']:
        if g in grade_counts:
            print(f"  {g}: {grade_counts[g]}个")

    # 输出TOP 20
    print("\n=== TOP 20 核心项目 ===")
    for p in evaluated[:20]:
        print(f"{p['rank']:2}. {p['name']:8} | 总分:{p['score100']:5.1f} | "
              f"人:{p['personScore']:4.1f}(经:{p['personDetail']['p1_exp']:.0f} 国:{p['personDetail']['p2_intl']:.0f} "
              f"绩:{p['personDetail']['p3_achieve']:.0f} 能:{p['personDetail']['p4_prof']:.0f} 创:{p['personDetail']['p5_entre']:.0f}) | "
              f"项:{p['projectScore']:4.1f}(相:{p['projectDetail']['d1_related']:.0f} 熟:{p['projectDetail']['d2_mature']:.0f} "
              f"协:{p['projectDetail']['d3_collab']:.0f} 学:{p['projectDetail']['d4_learn']:.0f}) | {p['grade']} {p['gradeReason']}")

    # 保存结果
    result = {'projects': evaluated}
    with open('evaluated_projects_v3.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 evaluated_projects_v3.json")

    return evaluated

if __name__ == '__main__':
    re_evaluate_all()
