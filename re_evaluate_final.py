#!/usr/bin/env python3
"""
最终版评估脚本
- 只评估开源案主（接受开源挑战模式）
- 100分制 = 人评50分 + 项评50分
- 新增三个专项榜：获客/出海/金融投资
"""

import json
import re

OPEN_KEY = '案主是否选择\u201c开源挑战\u201d模式'

# ====== 人评评分函数 (满分50分) ======

def score_experience(intro: str) -> float:
    """P1 实战经验 0-10分：工作年限、行业深耕"""
    score = 0
    text = intro.lower()
    
    # 工作年限
    years_match = re.findall(r'(\d+)\s*[年]', intro)
    max_years = max([int(y) for y in years_match if int(y) <= 40], default=0)
    
    if max_years >= 20:
        score += 10
    elif max_years >= 15:
        score += 8
    elif max_years >= 10:
        score += 6
    elif max_years >= 7:
        score += 5
    elif max_years >= 5:
        score += 4
    elif max_years >= 3:
        score += 2
    
    # 高管职位加分
    if re.search(r'CEO|总裁|董事长|合伙人|创始人|CXO|COO|CFO|CMO|CTO', intro):
        score = min(10, score + 1)
    
    return min(10, score)


def score_global(intro: str) -> float:
    """P2 国际视野 0-10分：500强、跨国、海外、外企经历"""
    score = 0
    
    # 世界500强 / 顶级公司
    if re.search(r'500强|世界500|麦肯锡|高盛|摩根|微软|谷歌|亚马逊|苹果|Meta|字节跳动|腾讯|阿里|百度|华为|宝洁|联合利华|可口可乐|雀巢', intro):
        score += 6
    
    # 外企/跨国
    if re.search(r'外企|跨国|multinational|外资|跨境|海外工作|国际公司|美资|欧资|日资', intro):
        score += 4
    
    # 留学/海外背景  
    if re.search(r'留学|海外|美国|英国|欧洲|日本|新加坡|哈佛|斯坦福|MIT|牛津|剑桥', intro):
        score += 3
    
    # 国际化业务经验
    if re.search(r'出海|全球|global|international|跨境|海外市场|国际市场', intro):
        score += 2
    
    return min(10, score)


def score_achievements(intro: str, project: str) -> float:
    """P3 业务成绩 0-15分：具体数字成果"""
    score = 0
    text = intro + ' ' + project
    
    # 大额营收/销售额
    money_patterns = [
        (r'(\d+)\s*亿', lambda m: int(m.group(1))),
        (r'(\d+\.?\d*)\s*[千万]', lambda m: float(m.group(1))),
    ]
    
    max_revenue = 0
    for p, fn in money_patterns:
        for m in re.finditer(p, text):
            try:
                val = fn(m)
                if '亿' in p:
                    val *= 10000  # 换算为万
                max_revenue = max(max_revenue, val)
            except:
                pass
    
    if max_revenue >= 10000:  # 1亿+
        score += 12
    elif max_revenue >= 5000:  # 5000万+
        score += 10
    elif max_revenue >= 1000:  # 1000万+
        score += 8
    elif max_revenue >= 500:   # 500万+
        score += 6
    elif max_revenue >= 100:   # 100万+
        score += 4
    elif max_revenue >= 10:    # 10万+
        score += 2
    
    # 增长百分比
    pct_match = re.findall(r'(\d+)\s*%|\b(\d+)\s*个百分点', text)
    max_pct = max([int(m[0] or m[1]) for m in pct_match], default=0)
    if max_pct >= 100:
        score = max(score, 8)
    elif max_pct >= 50:
        score = max(score, 6)
    elif max_pct >= 20:
        score = max(score, 4)
    
    # 用户/学员规模
    user_patterns = re.findall(r'(\d+\.?\d*)\s*[万]?\s*(?:用户|学员|客户|粉丝|会员)', text)
    for up in user_patterns:
        try:
            v = float(up)
            if v >= 10:  # 10万+
                score = max(score, 7)
            elif v >= 1:   # 1万+
                score = max(score, 5)
        except:
            pass
    
    # 具体业务成绩关键词
    if re.search(r'从\d+.*?到\d+|增长\d+|提升\d+|翻\d+倍|成为.*?第一|行业.*?领先|市场.*?份额', text):
        score = max(score, 5)
    
    return min(15, score)


def score_expertise(intro: str) -> float:
    """P4 专业能力 0-8分：高管/专业背景"""
    score = 0
    
    # 高管职位
    if re.search(r'CEO|总裁|董事长', intro):
        score += 6
    elif re.search(r'副总裁|联合创始人|合伙人|COO|CFO|CMO|CTO|总经理|VP', intro):
        score += 5
    elif re.search(r'总监|部门负责人|事业部.*?总|区域.*?总|BU.*?负责人', intro):
        score += 4
    elif re.search(r'经理|主管|高级.*?顾问|资深', intro):
        score += 2
    
    # 专业资质
    if re.search(r'博士|MBA|硕士|研究生|教授|讲师', intro):
        score += 2
    elif re.search(r'本科|学士', intro):
        score += 1
    
    # 专业技能深度
    if re.search(r'专家|顾问|咨询|培训师|导师|教练', intro):
        score += 1
    
    return min(8, score)


def score_entrepreneurship(intro: str, project: str) -> float:
    """P5 创业基因 0-7分：创始人身份/创业经历"""
    score = 0
    text = intro + ' ' + project
    
    if re.search(r'创始人|联合创始人', text):
        score += 5
    elif re.search(r'合伙人|联合发起人', text):
        score += 4
    
    if re.search(r'创业|自主创业|独立创业|连续创业', text):
        score = max(score, 3)
    
    # 已有实际业务
    if re.search(r'已.*?跑通|跑通.*?商业|正在.*?运营|已.*?盈利|月.*?营收|稳定.*?收入', text):
        score += 2
    
    return min(7, score)


def score_person(intro: str, project: str) -> dict:
    """综合人评（满分50）"""
    p1 = score_experience(intro)
    p2 = score_global(intro)
    p3 = score_achievements(intro, project)
    p4 = score_expertise(intro)
    p5 = score_entrepreneurship(intro, project)
    total = p1 + p2 + p3 + p4 + p5
    return {
        'p1_experience': round(p1, 1),
        'p2_global': round(p2, 1),
        'p3_achievements': round(p3, 1),
        'p4_expertise': round(p4, 1),
        'p5_entrepreneurship': round(p5, 1),
        'person_total': round(total, 1)
    }


# ====== 项评评分函数 (满分50分) ======

REBECCA_KEYWORDS = {
    'A': ['获客', '增长', '销售', '渠道', '转化', '线索', '流量', '客户'],
    'B': ['出海', '跨境', '海外', '国际', 'global'],
    'C': ['AI', '人工智能', '大模型', '智能化'],
    'D': ['教育', '培训', '学习', '知识'],
    'E': ['金融', '投资', '财富', '资产', '创投', 'VC', '私募'],
    'F': ['医疗', '健康', '养老', '大健康'],
    'G': ['企业服务', 'SaaS', 'B2B', '企业管理']
}

def score_relevance(intro: str, project: str, directions: str) -> float:
    """D1 领域相关 0-15分"""
    text = (intro + ' ' + project + ' ' + directions).lower()
    score = 0
    
    for cat, kws in REBECCA_KEYWORDS.items():
        if any(kw.lower() in text for kw in kws):
            score += 3
    
    return min(15, score)


def score_maturity(goal: str, project: str) -> float:
    """D2 项目成熟 0-15分"""
    score = 0
    text = goal + ' ' + project
    
    # 已有收入/客户
    if re.search(r'已.*?成交|已.*?收入|已有.*?客户|正在.*?运营|跑通|盈利', text):
        score += 8
    elif re.search(r'在跑|测试中|内测|试跑|第.*?期', text):
        score += 5
    elif re.search(r'计划|准备|打算|想法|方向', text):
        score += 2
    
    # 目标明确性
    if re.search(r'\d+.*?目标|\d+万|\d+个客户|保守目标|激进目标', text):
        score += 4
    
    # 具体方案
    if re.search(r'0-1|商业模式|产品内核|单元模型|解决方案', text):
        score += 3
    
    return min(15, score)


def score_synergy(intro: str, project: str) -> float:
    """D3 协同价值 0-10分"""
    score = 0
    text = intro + ' ' + project
    
    # 资源互换
    if re.search(r'渠道|人脉|资源|合作|合伙|BD|对接', text):
        score += 4
    
    # 可学习/可借鉴
    if re.search(r'方法论|体系|框架|工具|模型', text):
        score += 3
    
    # 潜在客户
    if re.search(r'企业服务|B端|ToB|企业客户|大客户', text):
        score += 3
    
    return min(10, score)


def score_learning(intro: str, project: str) -> float:
    """D4 学习价值 0-10分"""
    score = 0
    text = intro + ' ' + project
    
    # 独特方法论
    if re.search(r'方法论|体系|框架|模型|系统|工具箱', text):
        score += 4
    
    # 跨界/创新
    if re.search(r'创新|突破|探索|尝试.*?新|不同.*?方式', text):
        score += 3
    
    # 可复制性
    if re.search(r'可复制|标准化|规模化|流程化|SOP', text):
        score += 3
    
    return min(10, score)


def score_project(intro: str, project: str, goal: str, directions: str) -> dict:
    """综合项评（满分50）"""
    d1 = score_relevance(intro, project, directions)
    d2 = score_maturity(goal, project)
    d3 = score_synergy(intro, project)
    d4 = score_learning(intro, project)
    total = d1 + d2 + d3 + d4
    return {
        'd1_relevance': round(d1, 1),
        'd2_maturity': round(d2, 1),
        'd3_synergy': round(d3, 1),
        'd4_learning': round(d4, 1),
        'project_total': round(total, 1)
    }


def get_grade(total: float, person: float) -> str:
    if total >= 75 and person >= 25:
        return 'S+'
    elif total >= 68 and person >= 22:
        return 'S'
    elif total >= 62 and person >= 18:
        return 'A'
    elif total >= 55 and person >= 12:
        return 'B'
    elif total >= 45:
        return 'C'
    else:
        return 'D'


# ====== 专项分类判断 ======

QUKA_KEYWORDS = ['获客', '拓客', '客户获取', '流量获取', '招生', '线索', '获取客户',
                 '引流', '拉新', '新客', '转化率', '销售转化', '渠道获客', '私域获客',
                 '营销获客', '增长黑客', '冷启动']

CHUGAI_KEYWORDS = ['出海', '跨境', '海外市场', '国际化', '全球化', '外贸', '海外业务',
                   '跨境电商', '海外拓展', '国际市场', '走出去', '东南亚', '欧美市场',
                   'global', 'oversea', '出境', '港澳台', '海外客户']

FINANCE_KEYWORDS = ['金融', '投资', '股票', '基金', '资产管理', '理财', '财富管理',
                    '融资', '风险投资', '创投', 'VC', '私募', '保险', '银行', '证券',
                    '债券', 'PE', '量化', '资本', '财务', '会计', '税务', '审计',
                    '投行', '财富', '资金', '贷款', '信贷', '金融科技', 'fintech']

def classify_special(text: str) -> list:
    """判断属于哪些专项类别"""
    cats = []
    text_lower = text.lower()
    if any(kw in text_lower for kw in QUKA_KEYWORDS):
        cats.append('获客')
    if any(kw in text_lower for kw in CHUGAI_KEYWORDS):
        cats.append('出海')
    if any(kw in text_lower for kw in FINANCE_KEYWORDS):
        cats.append('金融投资')
    return cats


# ====== 主程序 ======

def main():
    with open('records_raw.json', 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    # 筛选开源案主
    open_cases = [item for item in raw if '接受开源' in str(item['fields'].get(OPEN_KEY, ''))]
    print(f'开源案主总数: {len(open_cases)}')
    
    results = []
    
    for item in open_cases:
        f = item['fields']
        
        intro = str(f.get('案主个人介绍', '') or '')
        project = str(f.get('项目课题介绍', '') or '')
        goal = str(f.get('航海目标和计划', '') or '')
        directions = str(f.get('项目想突破的方向', '') or '')
        story = str(f.get('一堂学习故事', '') or '')
        one_page = str(f.get('一页纸完整介绍', '') or '')
        
        # 联系方式提取
        contact_raw = str(f.get('所在城市及联系方式', '') or '')
        wechat_nick = str(f.get('微信昵称', '') or '')
        phones = re.findall(r'1[3-9]\d{9}', contact_raw)
        wechat_ids = re.findall(r'微信[号：:]\s*(\S+)', contact_raw) + re.findall(r'wx\s*[:：]\s*(\S+)', contact_raw, re.I)
        qr_imgs = re.findall(r'https://cdn\.yitang\.top/\S+', contact_raw)
        # 去重手机号和微信号
        phones = list(dict.fromkeys(phones))
        wechat_ids = list(dict.fromkeys(wechat_ids))
        
        # 合并全部文本用于搜索
        full_text = intro + ' ' + project + ' ' + goal + ' ' + one_page + ' ' + story
        
        # 评分
        person_scores = score_person(intro + ' ' + one_page, project)
        project_scores = score_project(intro, project, goal, directions)
        
        total = person_scores['person_total'] + project_scores['project_total']
        grade = get_grade(total, person_scores['person_total'])
        
        # 专项分类
        special_cats = classify_special(full_text)
        
        # 从intro提取摘要（前150字）
        intro_summary = intro[:200].strip() if intro else ''
        
        result = {
            'id': str(f.get('案主编号', item.get('id', ''))),
            'name': str(f.get('姓名', '')),
            'region': str(f.get('所在大区', '')),
            'registerType': str(f.get('案主报名形式', '')),
            'credits': int(f.get('学分', 0) or 0),
            'directions': directions,
            'intro': intro,
            'projectIntro': project,
            'goal': goal,
            'introSummary': intro_summary,
            'specialCategories': special_cats,
            'wechatNick': wechat_nick,
            'phones': phones,
            'wechatIds': wechat_ids,
            'qrImgs': qr_imgs,
            'contactRaw': contact_raw.strip(),
            'totalScore': round(total, 1),
            'grade': grade,
            **person_scores,
            **project_scores
        }
        results.append(result)
    
    # 按总分排序
    results.sort(key=lambda x: -x['totalScore'])
    
    # 统计
    grade_counts = {}
    for r in results:
        grade_counts[r['grade']] = grade_counts.get(r['grade'], 0) + 1
    
    print('\n等级分布:')
    for g in ['S+', 'S', 'A', 'B', 'C', 'D']:
        print(f'  {g}: {grade_counts.get(g, 0)}')
    
    print(f'\nTOP 10:')
    for r in results[:10]:
        cats = '/'.join(r['specialCategories']) if r['specialCategories'] else '-'
        print(f"  {r['name']} | {r['totalScore']}分({r['grade']}) | 人:{r['person_total']} 项:{r['project_total']} | 专项:{cats}")
    
    # 专项榜统计
    for cat in ['获客', '出海', '金融投资']:
        cat_list = [r for r in results if cat in r['specialCategories']]
        print(f'\n{cat}专项: {len(cat_list)}人, TOP3:')
        for r in cat_list[:3]:
            print(f"  {r['name']} | {r['totalScore']}分 | 人:{r['person_total']} 项:{r['project_total']}")
    
    # 保存结果
    output = {
        'meta': {
            'total': len(results),
            'grade_counts': grade_counts,
            'special_counts': {
                '获客': len([r for r in results if '获客' in r['specialCategories']]),
                '出海': len([r for r in results if '出海' in r['specialCategories']]),
                '金融投资': len([r for r in results if '金融投资' in r['specialCategories']])
            }
        },
        'projects': results
    }
    
    with open('evaluated_final.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f'\n✅ 保存到 evaluated_final.json')


if __name__ == '__main__':
    main()
