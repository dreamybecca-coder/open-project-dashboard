import json
import re

# 读取数据
with open('records_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('evaluated_projects_v3.json', 'r', encoding='utf-8') as f:
    scores = json.load(f)

# 海外学校列表
overseas_unis = [
    '斯坦福', 'Stanford', '哈佛', 'Harvard', 'MIT', '麻省理工',
    '剑桥', 'Cambridge', '牛津', 'Oxford', '宾大', 'Pennsylvania', 
    '哥伦比亚大学', 'Columbia', '耶鲁', 'Yale', '普林斯顿', 'Princeton',
    '芝加哥大学', 'Chicago', '加州理工', 'Caltech',
    '南加州大学', 'USC', '南洋理工', 'NTU', '新加坡国立', 'NUS',
    '早稻田', 'Waseda', '东京大学', 'Tokyo', '京都大学',
    '莱斯大学', 'Rice', '纽约大学', 'NYU', '西北大学', 'Northwestern',
    '杜克', 'Duke', '伯克利', 'Berkeley', '康奈尔', 'Cornell',
    '宾夕法尼亚大学', 'UPenn', '布朗', 'Brown', '达特茅斯', 'Dartmouth',
    '约翰霍普金斯', 'Johns Hopkins', 'UCLA', '加州大学洛杉矶',
    '帝国理工', 'Imperial College', '伦敦政经', 'LSE', '伦敦大学学院', 'UCL',
    '爱丁堡', 'Edinburgh', '曼彻斯特', 'Manchester', '国王学院', 'KCL',
    'HEC', 'INSEAD', '欧洲商学院', '欧洲工商管理学院',
    '苏黎世联邦理工', 'ETH', '洛桑联邦理工', 'EPFL',
    '多伦多大学', 'Toronto', '麦吉尔', 'McGill', 'UBC', '不列颠哥伦比亚',
    '悉尼大学', 'Sydney', '墨尔本大学', 'Melbourne', '澳国立', 'ANU',
    'Parsons', '帕森斯', 'RISD', '罗德岛设计', '圣马丁', 'Central Saint Martins',
    '皇家艺术学院', 'RCA', 'ArtCenter', '艺术中心设计学院',
    '博科尼', 'Bocconi', 'IE商学院', 'IE Business', 'IESE',
    '港大', 'HKU', '香港大学', '港中文', 'CUHK', '香港中文大学',
    '港科大', 'HKUST', '香港科技大学', '港大', '香港大学',
    '清迈大学', 'Chiang Mai', '朱拉隆功', 'Chulalongkorn'
]

# 海归名单（所有有海外留学背景的人）
overseas_names = []

# 32岁以下名单（不要求海归）
young_names = []

for person in data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    intro = fields.get('案主个人介绍', '') or fields.get('一页纸完整介绍', '')
    
    # 获取分数
    score_data = scores.get(name, {})
    score = score_data.get('score', 0)
    grade = score_data.get('grade', 'N/A')
    
    # 检测海外背景
    has_overseas = False
    
    # 1. 直接提到海外学校
    for uni in overseas_unis:
        if uni in intro:
            has_overseas = True
            break
    
    # 2. 留学经历关键词
    if not has_overseas:
        patterns = [
            r'赴[美英日德法澳加新][国]?[留学]',
            r'从[美英日德法澳加新][国]?退学回国',
            r'[美英日德法澳加新][国]?留学',
            r'留学[美英日德法澳加新][国]?',
            r'海外.*?背景',
            r'出国.*?年',
            r'在国外.*?[年学习工作]',
        ]
        for pattern in patterns:
            if re.search(pattern, intro):
                has_overseas = True
                break
    
    # 3. 毕业于海外大学
    if not has_overseas:
        if re.search(r'毕业于.*?(大学|学院)', intro):
            for uni in overseas_unis:
                if uni in intro:
                    has_overseas = True
                    break
    
    if has_overseas:
        overseas_names.append(name)
    
    # 检测年龄（不要求海归）
    age = None
    
    # 1. 直接年龄
    age_match = re.search(r'(\d{1,2})\s*岁', intro)
    if age_match:
        potential_age = int(age_match.group(1))
        context_start = max(0, age_match.start() - 20)
        context = intro[context_start:age_match.end() + 20]
        
        # 排除过去时态和孩子年龄
        if not any(x in context for x in ['那一年', '那年', '赴', '岁时', '的时候', '孩子', '大宝', '宝宝', '儿子', '女儿', '照顾', '带领']):
            if 15 <= potential_age <= 50:
                age = potential_age
    
    # 2. 从毕业年份推断
    if not age:
        grad_match = re.search(r'(\d{4})[年届]?毕业', intro)
        if grad_match:
            grad_year = int(grad_match.group(1))
            if 2010 <= grad_year <= 2025:
                age = 2026 - grad_year + 22
    
    # 3. 从"XX年前回国"推断
    if not age:
        return_match = re.search(r'([十\d]{1,2})\s*年前.*?回国', intro)
        if return_match:
            years_str = return_match.group(1)
            if years_str == '十':
                years_ago = 10
            else:
                years_ago = int(years_str)
            age = 25 + years_ago
    
    # 4. 从工作经验推断
    if not age:
        work_match = re.search(r'(\d{1,2})[年余].*?(经验|从业|工作)', intro)
        if work_match:
            years = int(work_match.group(1))
            if 1 <= years <= 20:
                age = 22 + years
    
    # 如果年龄<=32，加入名单
    if age and age <= 32:
        young_names.append(name)

# 去重
overseas_names = list(set(overseas_names))
young_names = list(set(young_names))

print(f"海归精英（不限年龄）：{len(overseas_names)}人")
print(f"32岁以下精英（不限海归）：{len(young_names)}人")
print(f"\n重叠人数：{len(set(overseas_names) & set(young_names))}人")

# 保存结果
with open('overseas_talents.json', 'w', encoding='utf-8') as f:
    json.dump(overseas_names, f, ensure_ascii=False, indent=2)

with open('young_talents.json', 'w', encoding='utf-8') as f:
    json.dump(young_names, f, ensure_ascii=False, indent=2)

print("\n✓ 已保存到 overseas_talents.json 和 young_talents.json")
