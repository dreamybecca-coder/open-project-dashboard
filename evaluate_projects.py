#!/usr/bin/env python3
"""
大航海项目筛选评估引擎
基于Rebecca的六维评估体系自动评分
"""

import json
import re
from collections import defaultdict

# 高相关关键词（对应D4）
HIGH_RELEVANCE_KEYWORDS = [
    'ai agent', 'agent', '工作流', 'workflow', 'prompt', 'prompt工程',
    'b2b', '企业服务', 'saas', '企业数字化', '数字化转型',
    '工程', '建筑', '水利', '基建', '招投标', '投标',
    '投资', '金融', '量化', 'crypto', 'defi', '交易', '决策',
    '一人公司', 'solo', '个体创业', 'opc',
    '内容ip', '知识付费', '社群', '私域',
    '信任', '高净值', '校友', 'emba',
    '企业家服务', '企业服务'
]

# 中等相关关键词
MEDIUM_RELEVANCE_KEYWORDS = [
    '跨境电商', '电商',
    '教育', '培训', 'ai赋能',
    '咨询', '方法论',
    '营销', '自动化'
]

# 学习价值关键词
LEARNING_VALUE_KEYWORDS = [
    '冷启动', '零预算', '低成本获客', '获客',
    '单元经济', '单元模型', 'lTV', 'cac',
    '从需求出发', '用户需求',
    'mvp', '最小', '验证',
    '自动化', '工作流', '提效'
]

# 协同潜力关键词
COLLABORATION_KEYWORDS = [
    '工程', '建筑', '水利', '基建',
    '西安', '西北',
    '技术', '开发', '渠道', '人脉',
    '客户', '资源'
]

def extract_text_length(text):
    """获取文本长度"""
    if not text:
        return 0
    return len(str(text))

def count_keywords(text, keywords):
    """统计关键词出现次数"""
    if not text:
        return 0
    text_lower = str(text).lower()
    count = 0
    for kw in keywords:
        count += len(re.findall(kw.lower(), text_lower))
    return count

def has_ai_core(text):
    """检查AI是否是产品核心而非外壳"""
    if not text:
        return False
    text_lower = str(text).lower()

    # AI只是外壳的信号
    shell_signals = [
        'ai赋能', 'ai助力', 'ai加持', 'ai辅助',
        '用ai做', 'ai工具', 'ai技术'
    ]

    # AI是核心的信号
    core_signals = [
        'ai产品', 'ai系统', 'ai平台', 'ai应用',
        'ai驱动', 'ai native', 'ainative',
        'agent', '工作流', '自动化'
    ]

    core_count = sum(1 for s in core_signals if s in text_lower)
    shell_count = sum(1 for s in shell_signals if s in text_lower)

    return core_count > shell_count

def check_b2b(text):
    """检查是否是B2B方向"""
    if not text:
        return False
    text_lower = str(text).lower()
    b2b_signals = ['b2b', '企业', '商家', '客户', 'tob', '商务', '渠道', '代理', 'SaaS']
    return any(sig in text_lower for sig in b2b_signals)

def check_traditional_industry(text):
    """检查是否主要是传统行业"""
    if not text:
        return False
    text_lower = str(text).lower()
    traditional_signals = ['餐饮', '零售', '制造', '农业', '服装', '食品', '美容', '健身']
    return any(sig in text_lower for sig in traditional_signals)

def check_innovation(text):
    """检查是否有创新性打法"""
    if not text:
        return False
    text_lower = str(text).lower()
    innovation_signals = ['创新', '差异化', '独特', '首创', '颠覆', '蓝海', '模式创新']
    return any(sig in text_lower for sig in innovation_signals)

def check_real_demand(text):
    """检查是否有真实需求"""
    if not text:
        return False
    text_lower = str(text).lower()
    demand_signals = ['痛点', '刚需', '需求', '问题', '解决', '麻烦', '困扰']
    vague_signals = ['赋能', '助力', '打通', '生态', '平台化']
    demand_count = sum(1 for s in demand_signals if s in text_lower)
    vague_count = sum(1 for s in vague_signals if s in text_lower)
    return demand_count > vague_count

def evaluate_d1_person_quality(fields):
    """D1: 案主素质评估 (25%)"""
    intro = fields.get('案主个人介绍', '')
    credits = int(fields.get('学分', 0) or 0)

    if not intro or len(intro) < 50:
        return 1.0, "信息严重不足，无法判断"

    score = 3.0  # 基础分

    # 检查经验年限
    experience_patterns = [
        r'(\d+)年', r'(\d+)年\+', r'从业\d+年', r'深耕\d+年',
        r'\d+年.*经验', r'经历.*\d+年'
    ]

    years = 0
    for pattern in experience_patterns:
        matches = re.findall(pattern, intro)
        if matches:
            for m in matches:
                # 提取数字
                nums = re.findall(r'\d+', m)
                if nums:
                    years = max(years, int(nums[0]))

    if years >= 10:
        score = 4.5
    elif years >= 5:
        score = 4.0
    elif years >= 2:
        score = 3.5

    # 检查成功案例/可验证成果
    if re.search(r'(成功|成果|业绩|案例|NB|最.*事|做成)', intro):
        score += 0.5

    # 检查创业经历
    if re.search(r'(创业|从0到1|自己干|离职|辞职)', intro):
        score += 0.3

    # 检查专业资质
    if re.search(r'(ceo|cto|总监|总经理|创始人|负责人)', intro):
        score += 0.2

    # 检查模糊词汇（减分）
    vague_count = count_keywords(intro, ['赋能', '助力', '打通', '闭环', '生态'])
    if vague_count >= 3:
        score -= 0.5

    # 学分加成
    if credits >= 1000:
        score += 0.3
    elif credits >= 500:
        score += 0.2

    return min(5.0, max(1.0, round(score, 1))), f"经验{years}年"

def evaluate_d2_business_value(fields):
    """D2: 商业价值评估 (25%)"""
    intro = fields.get('项目课题介绍', '')
    plan = fields.get('航海目标和计划', '')
    full_text = f"{intro} {plan}"

    if not intro or len(intro) < 30:
        return 1.0, "信息严重不足"

    score = 2.5  # 基础分

    # 硬伤检测
    if check_traditional_industry(full_text) and 'ai' not in full_text.lower():
        # 传统行业但无AI，可能是伪需求
        if not check_real_demand(full_text):
            return 1.5, "传统行业+需求不明确"

    # 检查需求是否清晰
    if check_real_demand(full_text):
        score += 0.5

    # 检查AI是否核心
    if has_ai_core(full_text):
        score += 0.5
    elif 'ai' in full_text.lower() and 'ai赋能' in full_text.lower():
        score -= 0.3  # AI只是外壳

    # 检查目标用户
    user_patterns = [
        r'面向.*用户', r'目标.*客户', r'服务.*企业',
        r'针对.*群体', r'为.*提供', r'帮助.*实现'
    ]
    has_clear_user = any(re.search(p, full_text) for p in user_patterns)
    if has_clear_user:
        score += 0.3

    # 检查商业模式
    biz_patterns = [
        r'收费|付费|商业模式|变现|盈利|收入',
        r'价格|定价|订阅|一次|服务费'
    ]
    has_biz_model = any(re.search(p, full_text) for p in biz_patterns)
    if has_biz_model:
        score += 0.3

    # 检查差异化
    if check_innovation(full_text):
        score += 0.3

    # 检查是否解决方案找需求
    if '先有产品' in full_text or '编造需求' in full_text:
        return 1.5, "明显的解决方案找需求"

    return min(5.0, max(1.0, round(score, 1))), "评分完成"

def evaluate_d3_plan_quality(fields):
    """D3: 计划合理性评估 (15%)"""
    plan = fields.get('航海目标和计划', '')
    intro = fields.get('项目课题介绍', '')

    if not plan or len(plan) < 30:
        return 1.0, "计划信息严重不足"

    score = 3.0  # 基础分

    # 检查目标量化
    if re.search(r'\d+[万千万个]', plan):
        score += 0.3

    # 检查保A争B思维
    if re.search(r'保守|下限|保', plan) and re.search(r'激进|上限|追', plan):
        score += 0.5

    # 检查阶段划分
    if re.search(r'第.*阶段|第一个月|第二个月|第一个月|第二个', plan):
        score += 0.3

    # 检查MVP/最小验证
    if re.search(r'mvp|最小|验证|试点|poc', plan.lower()):
        score += 0.3

    # 检查假设识别
    if re.search(r'假设|前提|核心风险|关键', plan):
        score += 0.3

    # 检查风险预案
    if re.search(r'风险|预案|备选|调整', plan):
        score += 0.2

    # 检查是否是纯愿景
    if len(plan) > 500 and not re.search(r'具体|步骤|计划|目标', plan):
        score -= 0.3

    return min(5.0, max(1.0, round(score, 1))), "评分完成"

def evaluate_d4_relevance(fields):
    """D4: 领域相关度评估 (20%)"""
    intro = fields.get('项目课题介绍', '')
    plan = fields.get('航海目标和计划', '')
    personal_intro = fields.get('案主个人介绍', '')
    full_text = f"{intro} {plan} {personal_intro}"

    if not full_text or len(full_text) < 50:
        return 1.0, "信息严重不足"

    score = 2.0  # 基础分

    # 统计高相关关键词命中
    high_count = count_keywords(full_text.lower(), HIGH_RELEVANCE_KEYWORDS)

    # 统计中等相关关键词命中
    medium_count = count_keywords(full_text.lower(), MEDIUM_RELEVANCE_KEYWORDS)

    # 根据关键词数量调整分数
    if high_count >= 4:
        score = 4.5
    elif high_count >= 2:
        score = 4.0
    elif high_count >= 1:
        score = 3.5
    elif medium_count >= 2:
        score = 3.0
    elif medium_count >= 1:
        score = 2.5

    # 额外加分：Rebecca当前方向高度匹配
    # 1. AI-native OPC模式
    if '一人' in full_text and 'ai' in full_text.lower():
        score = min(5.0, score + 0.5)

    # 2. 升维工坊 - 西安/工程/建筑
    if any(kw in full_text for kw in ['西安', '工程', '建筑', '水利', '基建']):
        score = min(5.0, score + 0.5)

    # 3. Invert-Bot - 投资/决策/逆向
    if any(kw in full_text.lower() for kw in ['投资', '决策', '量化', '金融']):
        score = min(5.0, score + 0.5)

    # 4. 内容IP方向
    if any(kw in full_text for kw in ['内容', 'ip', '自媒体', '公众号', '小红书']):
        score = min(5.0, score + 0.3)

    return min(5.0, max(1.0, round(score, 1))), f"高相关词:{high_count}"

def evaluate_d5_learning_value(fields):
    """D5: 学习借鉴价值评估 (10%)"""
    intro = fields.get('项目课题介绍', '')
    plan = fields.get('航海目标和计划', '')
    story = fields.get('一堂学习故事', '')
    full_text = f"{intro} {plan} {story}"

    if not full_text or len(full_text) < 50:
        return 1.0, "信息严重不足"

    score = 2.5  # 基础分

    # 检查学习价值关键词
    learning_count = count_keywords(full_text.lower(), LEARNING_VALUE_KEYWORDS)

    if learning_count >= 4:
        score = 4.5
    elif learning_count >= 2:
        score = 4.0
    elif learning_count >= 1:
        score = 3.0

    # 检查创新打法
    if check_innovation(full_text):
        score = min(5.0, score + 0.5)

    # 检查有具体方法论
    if re.search(r'方法论|方法|模型|框架|体系', full_text):
        score = min(5.0, score + 0.3)

    # 检查有可复用的AI工作流
    if re.search(r'工作流|自动化|提效|sop', full_text.lower()):
        score = min(5.0, score + 0.3)

    # 检查有冷启动方法
    if re.search(r'冷启动|零成本|低成本|零预算', full_text):
        score = min(5.0, score + 0.5)

    return min(5.0, max(1.0, round(score, 1))), f"学习词:{learning_count}"

def evaluate_d6_collaboration(fields):
    """D6: 网络协同潜力评估 (5%)"""
    intro = fields.get('案主个人介绍', '')
    project = fields.get('项目课题介绍', '')
    region = fields.get('所在大区', [])
    full_text = f"{intro} {project}"

    if not full_text or len(full_text) < 50:
        return 1.0, "信息严重不足"

    score = 2.0  # 基础分

    # 检查协同关键词
    collab_count = count_keywords(full_text.lower(), COLLABORATION_KEYWORDS)

    if collab_count >= 3:
        score = 4.0
    elif collab_count >= 2:
        score = 3.5
    elif collab_count >= 1:
        score = 2.5

    # 检查地理位置协同（西安/西北是Rebecca的目标市场）
    if region:
        region_str = ' '.join(region) if isinstance(region, list) else str(region)
        if any(loc in region_str for loc in ['西安', '西北', '华中']):
            score = min(5.0, score + 0.5)

    # 检查是否有独特资源
    if re.search(r'(技术|渠道|资源|客户|行业)', full_text):
        score = min(5.0, score + 0.3)

    # 检查是否是潜在客户行业
    target_industries = ['工程', '建筑', '水利', '基建', '制造']
    if any(ind in full_text for ind in target_industries):
        score = min(5.0, score + 0.5)

    return min(5.0, max(1.0, round(score, 1))), f"协同词:{collab_count}"

def evaluate_project(fields):
    """评估单个项目"""
    # 提取基本信息
    name = fields.get('姓名', '') or fields.get('微信昵称', '未知')
    project_id = fields.get('案主编号', '')
    region = fields.get('所在大区', [])
    region_str = ' '.join(region) if isinstance(region, list) else str(region)

    register_type = fields.get('案主报名形式', '')
    credits = int(fields.get('学分', 0) or 0)
    tickets = int(fields.get('船票（押券数）', 0) or 0)

    project_directions = fields.get('项目想突破的方向', [])

    intro = fields.get('案主个人介绍', '')
    project_intro = fields.get('项目课题介绍', '')
    plan = fields.get('航海目标和计划', '')
    story = fields.get('一堂学习故事', '')

    # 六维评分
    d1, d1_reason = evaluate_d1_person_quality(fields)
    d2, d2_reason = evaluate_d2_business_value(fields)
    d3, d3_reason = evaluate_d3_plan_quality(fields)
    d4, d4_reason = evaluate_d4_relevance(fields)
    d5, d5_reason = evaluate_d5_learning_value(fields)
    d6, d6_reason = evaluate_d6_collaboration(fields)

    # 计算总分
    total_score = d1*0.25 + d2*0.25 + d3*0.15 + d4*0.20 + d5*0.10 + d6*0.05
    total_score = round(total_score, 2)

    # 评级
    if total_score >= 4.0:
        grade = 'S'
    elif total_score >= 3.5:
        grade = 'A'
    elif total_score >= 3.0:
        grade = 'B'
    elif total_score >= 2.5:
        grade = 'C'
    else:
        grade = 'D'

    # 特别标记
    tags = []
    if d4 >= 4:
        tags.append('战略高相关')
    if d5 >= 4:
        tags.append('创新启发')
    if d6 >= 4:
        tags.append('潜在合作')
    if total_score >= 3.5 and min(d1, d2, d3, d4, d5, d6) <= 2:
        tags.append('高分但有硬伤')

    # 生成一句话总结
    summary = generate_summary(fields, total_score, grade, d4, d5, d6)

    return {
        'id': project_id,
        'name': name,
        'region': region_str,
        'registerType': register_type,
        'credits': credits,
        'tickets': tickets,
        'directions': project_directions if isinstance(project_directions, list) else [project_directions],
        'scores': {
            'd1': d1,
            'd2': d2,
            'd3': d3,
            'd4': d4,
            'd5': d5,
            'd6': d6
        },
        'reasons': {
            'd1': d1_reason,
            'd2': d2_reason,
            'd3': d3_reason,
            'd4': d4_reason,
            'd5': d5_reason,
            'd6': d6_reason
        },
        'totalScore': total_score,
        'grade': grade,
        'tags': tags,
        'summary': summary,
        'intro': intro[:300] + '...' if len(intro) > 300 else intro,
        'projectIntro': project_intro[:500] + '...' if len(project_intro) > 500 else project_intro,
        'plan': plan[:500] + '...' if len(plan) > 500 else plan,
        'story': story[:300] + '...' if len(story) > 300 else story
    }

def generate_summary(fields, total_score, grade, d4, d5, d6):
    """生成一句话总结"""
    intro = fields.get('项目课题介绍', '') or fields.get('案主个人介绍', '')

    if not intro:
        return "信息不足，无法生成推荐理由"

    # 提取项目核心信息
    project_type = ""
    if 'ai' in intro.lower():
        project_type = "AI"
    if 'b2b' in intro.lower() or '企业' in intro:
        project_type += "B2B"
    if '一人' in intro or 'solo' in intro.lower():
        project_type += "一人公司"
    if '内容' in intro or 'ip' in intro.lower():
        project_type += "内容IP"
    if '投资' in intro or '金融' in intro:
        project_type += "金融"

    # 根据评分生成推荐理由
    if grade == 'S':
        return f"高度推荐：{project_type}项目，总分{total_score}，与Rebecca方向高度相关，值得深度跟踪"
    elif grade == 'A':
        if d4 >= 4:
            return f"推荐关注：{project_type}项目，D4={d4}战略相关，有合作潜力"
        elif d5 >= 4:
            return f"推荐学习：{project_type}项目，D5={d5}模式有创新价值"
        else:
            return f"建议关注：{project_type}项目，整体评分良好"
    elif grade == 'B':
        return f"可选关注：{project_type}项目，有一定价值但非优先"
    elif grade == 'C':
        return f"低优先级：{project_type}项目，相关度或质量一般"
    else:
        return f"建议跳过：{project_type}项目，信息不足或价值有限"

def process_all_projects(input_file, output_file):
    """处理所有项目"""
    print(f"读取数据: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"共有 {len(data)} 个项目，开始评估...")

    results = []
    grade_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
    tag_counts = {'战略高相关': 0, '创新启发': 0, '潜在合作': 0, '高分但有硬伤': 0}

    for i, item in enumerate(data):
        fields = item.get('fields', {})
        result = evaluate_project(fields)
        results.append(result)

        grade_counts[result['grade']] += 1
        for tag in result['tags']:
            tag_counts[tag] += 1

        if (i + 1) % 100 == 0:
            print(f"已处理 {i + 1} / {len(data)} 个项目")

    # 排序
    results.sort(key=lambda x: x['totalScore'], reverse=True)

    # 添加排名
    for i, r in enumerate(results):
        r['rank'] = i + 1

    # 输出统计
    print("\n========== 评估统计 ==========")
    print(f"总项目数: {len(results)}")
    print(f"评级分布: S={grade_counts['S']}, A={grade_counts['A']}, B={grade_counts['B']}, C={grade_counts['C']}, D={grade_counts['D']}")
    print(f"特别标记: 战略高相关={tag_counts['战略高相关']}, 创新启发={tag_counts['创新启发']}, 潜在合作={tag_counts['潜在合作']}")
    print(f"Top10平均分: {sum(r['totalScore'] for r in results[:10]) / 10:.2f}")

    # 保存结果
    output_data = {
        'projects': results,
        'stats': {
            'total': len(results),
            'gradeDistribution': grade_counts,
            'tagDistribution': tag_counts,
            'averageScore': round(sum(r['totalScore'] for r in results) / len(results), 2)
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n评估结果已保存到: {output_file}")

    return output_data

if __name__ == '__main__':
    input_file = '/Users/rebecca/WorkBuddy/20260405230835/records_raw.json'
    output_file = '/Users/rebecca/WorkBuddy/20260405230835/evaluated_projects.json'

    result = process_all_projects(input_file, output_file)
    print(f"\nTop 10 项目:")
    for r in result['projects'][:10]:
        print(f"  #{r['rank']} {r['name']} - 总分:{r['totalScore']} ({r['grade']})")
