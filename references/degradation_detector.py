#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长文本退化模式检测器 v4.2.0
用于检测大模型生成超长篇文本时出现的碎片化断句、机械重复、空行注水、
时间线错乱、年龄-生日不匹配、相对时间表述错误、年龄对比写反等退化问题。

用法:
  python degradation_detector.py <文件路径>
  python degradation_detector.py <文件路径> --config <配置文件.json>

配置文件格式（可选）:
{
  "characters": {
    "徐萱": {"birth": "2016-04-08", "grade": "高三"},
    "苏晚": {"birth": "2016-08-15", "grade": "高三"}
  },
  "key_events": {
    "逃亡": "2026-07-01",
    "回国": "2033-11-01",
    "父母空难": "2026-01-15"
  },
  "classmates": ["苏晚", "郑好", "周鼎思"]
}
"""

import re
import sys
import json
import os
from collections import Counter
from datetime import datetime, date


# ============================================================
# 基础退化模式检测
# ============================================================

def detect_subject_verb_comma(text):
    """检测'主语，动词'碎片化断句模式"""
    issues = []
    lines = text.split('\n')
    for line_num, line in enumerate(lines, 1):
        pattern_cn = re.compile(r'([\u4e00-\u9fff]{1,4})，([\u4e00-\u9fff]{1,2})([。，！？：；在了着过到上下进出])')
        matches_cn = pattern_cn.findall(line)
        for subj, verb, suffix in matches_cn:
            common_verbs = ['说', '问', '答', '道', '喊', '叫', '笑', '哭', '点', '摇', '坐', '站', '走', '跑', '看', '听', '想', '知', '穿', '戴', '拿', '放', '开', '关']
            if verb in common_verbs or (verb + suffix) in ['点头', '摇头', '说道', '问道', '答道', '坐在', '站在', '走了', '跑了', '看着', '听着', '想着']:
                issues.append({'type': '主语动词逗号', 'line': line_num, 'content': f"{subj}，{verb}{suffix}", 'suggestion': f"{subj}{verb}{suffix}"})
        pattern_en = re.compile(r'([A-Z][a-zA-Z]{1,14})，([\u4e00-\u9fff]{1,3})([。，！？：；在了着过到上下进出])')
        matches_en = pattern_en.findall(line)
        for name, verb, suffix in matches_en:
            issues.append({'type': '英文名主语逗号', 'line': line_num, 'content': f"{name}，{verb}{suffix}", 'suggestion': f"{name}{verb}{suffix}"})
    return issues


def detect_fragment_sentences(text):
    """检测碎片句（逗号过多且句子过短）"""
    issues = []
    lines = text.split('\n')
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        if line.count('，') >= 3 and len(line) < 50:
            issues.append({'type': '碎片句', 'line': line_num, 'content': line, 'suggestion': '合并为完整句子，减少不必要的逗号停顿'})
    return issues


def detect_dialogue_tag_comma(text):
    """检测对话标签中的逗号错误"""
    issues = []
    pattern = re.compile(r'[”"]([\u4e00-\u9fff]{1,4})，([说道问回答喊叫])([：，])')
    lines = text.split('\n')
    for line_num, line in enumerate(lines, 1):
        for name, verb, punct in pattern.findall(line):
            issues.append({'type': '对话标签逗号', 'line': line_num, 'content': f'"{name}，{verb}{punct}', 'suggestion': f'"{name}{verb}{punct}'})
    return issues


def detect_excessive_empty_lines(text):
    """检测空行密度过高"""
    issues = []
    lines = text.split('\n')
    empty_run = 0
    run_start = 0
    for i, line in enumerate(lines):
        if line.strip() == '':
            if empty_run == 0:
                run_start = i + 1
            empty_run += 1
        else:
            if empty_run >= 2:
                issues.append({'type': '连续空行', 'line': run_start, 'content': f"第{run_start}-{run_start + empty_run - 1}行连续{empty_run}个空行", 'suggestion': '段落之间最多保留1个空行'})
            empty_run = 0
    if empty_run >= 2:
        issues.append({'type': '连续空行', 'line': run_start, 'content': f"第{run_start}行至末尾连续{empty_run}个空行", 'suggestion': '删除末尾多余空行'})
    total_lines = len(lines)
    empty_lines = sum(1 for l in lines if l.strip() == '')
    if total_lines > 0 and empty_lines / total_lines > 0.4:
        issues.append({'type': '空行占比过高', 'line': '全文', 'content': f"空行占比 {empty_lines/total_lines*100:.1f}%，超过40%阈值", 'suggestion': '大量空行属于注水行为'})
    return issues


def detect_repeated_sentence_starts(text):
    """检测连续相同句式开头"""
    issues = []
    sentences = [s.strip() for s in re.split(r'[。！？]', text) if s.strip()]
    for i in range(len(sentences) - 5):
        window = sentences[i:i+7]
        starts = [s[:3] for s in window if len(s) >= 3]
        if len(starts) < 5:
            continue
        counter = Counter(starts)
        if len(counter) <= 2:
            most_common = counter.most_common(1)[0]
            issues.append({'type': '连续相同句式', 'position': f'第{i+1}句附近', 'content': f'连续7句中有{most_common[1]}句以"{most_common[0]}"开头', 'suggestion': '变化句式开头'})
    return issues


def count_chinese_chars(text):
    """统计中文字符数"""
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff')


def verify_timeline(text):
    """验证时间线是否严格单调递增"""
    issues = []
    pattern = re.compile(r'时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2})[：:](\d{2})')
    matches = pattern.findall(text)
    timestamps = []
    for m in matches:
        timestamps.append(tuple(map(int, m)))
    for i in range(1, len(timestamps)):
        if timestamps[i] <= timestamps[i-1]:
            issues.append({'type': '时间倒流', 'position': f'第{i+1}个时间戳', 'content': f'{timestamps[i]} 不大于前一个 {timestamps[i-1]}', 'suggestion': '调整时间顺序'})
    return issues


# ============================================================
# v4.2.0 新增：人物年龄-生日联动检测
# ============================================================

def parse_date(date_str):
    """解析日期字符串"""
    for fmt in ['%Y-%m-%d', '%Y年%m月%d日', '%Y/%m/%d']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def calc_age(birth_date, scene_date):
    """计算在scene_date时的年龄（未到生日不增岁）"""
    age = scene_date.year - birth_date.year
    if (scene_date.month, scene_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def detect_age_birthday_mismatch(text, config):
    """检测人物年龄未到生日误增岁（v4.2.0新增）
    
    需要config中包含characters配置，格式：
    {"徐萱": {"birth": "2016-04-08"}}
    """
    issues = []
    if not config or 'characters' not in config:
        return issues
    
    characters = config['characters']
    
    # 提取所有场次的时间戳和对应的文本段
    lines = text.split('\n')
    current_scene_date = None
    scene_start_line = 0
    
    for line_num, line in enumerate(lines, 1):
        # 检测场次时间
        time_match = re.match(r'时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日', line.strip())
        if time_match:
            y, m, d = map(int, time_match.groups())
            current_scene_date = date(y, m, d)
            scene_start_line = line_num
            continue
        
        if not current_scene_date:
            continue
        
        # 检测正文中的年龄表述
        for char_name, char_info in characters.items():
            birth_str = char_info.get('birth', '')
            birth_date = parse_date(birth_str)
            if not birth_date:
                continue
            
            correct_age = calc_age(birth_date, current_scene_date)
            
            # 匹配"X岁"或"X十八岁"等表述，且附近有人物名
            age_patterns = [
                rf'{char_name}[，。、：；""''（）\s]{{0,10}}(\d+)岁',
                rf'(\d+)岁[，。、：；""''（）\s]{{0,10}}{char_name}',
                rf'{char_name}.{{0,20}}?(\d+)岁',
            ]
            
            for pattern in age_patterns:
                for match in re.finditer(pattern, line):
                    stated_age = int(match.group(1))
                    if stated_age != correct_age and abs(stated_age - correct_age) <= 2:
                        issues.append({
                            'type': '年龄-生日不匹配',
                            'line': line_num,
                            'content': f"场次日期{current_scene_date}，{char_name}应为{correct_age}岁，文中写{stated_age}岁：{line.strip()[:80]}",
                            'suggestion': f"改为{correct_age}岁（{char_name}生日{birth_str}，未到生日不增岁）"
                        })
    
    return issues


# ============================================================
# v4.2.0 新增：相对时间表述检测
# ============================================================

def detect_relative_time_mismatch(text, config):
    """检测相对时间表述与实际时间线矛盾（v4.2.0新增）
    
    需要config中包含key_events配置，格式：
    {"逃亡": "2026-07-01", "回国": "2033-11-01"}
    """
    issues = []
    if not config or 'key_events' not in config:
        return issues
    
    key_events = config['key_events']
    lines = text.split('\n')
    current_scene_date = None
    
    for line_num, line in enumerate(lines, 1):
        time_match = re.match(r'时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日', line.strip())
        if time_match:
            y, m, d = map(int, time_match.groups())
            current_scene_date = date(y, m, d)
            continue
        
        if not current_scene_date:
            continue
        
        # 检测"X岁时离开/回来/逃亡/失去"等表述
        rel_pattern = re.compile(r'(\d+)岁(那年|时|的时候).{0,15}(离开|回来|走|逃亡|失去|去世|空难|车祸|发生)')
        for match in rel_pattern.finditer(line):
            stated_age = int(match.group(1))
            event_word = match.group(3)
            
            # 尝试匹配关键事件
            for event_name, event_date_str in key_events.items():
                event_date = parse_date(event_date_str)
                if not event_date:
                    continue
                
                # 检查这个事件是否与文中描述的事件相关
                if any(kw in event_word for kw in ['离开', '走', '逃亡']) and '逃亡' in event_name:
                    # 需要人物出生日期来计算
                    if config.get('characters'):
                        for char_name, char_info in config['characters'].items():
                            birth_date = parse_date(char_info.get('birth', ''))
                            if birth_date:
                                correct_age = calc_age(birth_date, event_date)
                                if stated_age != correct_age and abs(stated_age - correct_age) <= 5:
                                    issues.append({
                                        'type': '相对时间表述错误',
                                        'line': line_num,
                                        'content': f"文中写'{stated_age}岁时{event_word}'，但{event_name}发生在{event_date}，{char_name}当时应为{correct_age}岁：{line.strip()[:80]}",
                                        'suggestion': f"改为{correct_age}岁"
                                    })
    
    return issues


# ============================================================
# v4.2.0 新增：人物年龄对比检测
# ============================================================

def detect_age_comparison_mismatch(text, config):
    """检测人物年龄对比写反（v4.2.0新增）
    
    需要config中包含characters配置（含birth字段）
    """
    issues = []
    if not config or 'characters' not in config:
        return issues
    
    characters = config['characters']
    char_names = list(characters.keys())
    
    if len(char_names) < 2:
        return issues
    
    lines = text.split('\n')
    
    # 生成所有人物对的年龄差
    age_diffs = {}
    for i, name1 in enumerate(char_names):
        for name2 in char_names[i+1:]:
            b1 = parse_date(characters[name1].get('birth', ''))
            b2 = parse_date(characters[name2].get('birth', ''))
            if b1 and b2:
                diff_days = (b2 - b1).days
                diff_months = round(diff_days / 30.44)
                age_diffs[(name1, name2)] = diff_months  # name1比name2大diff_months个月
    
    for line_num, line in enumerate(lines, 1):
        # 匹配"A比B大/小X个月/岁"
        comp_pattern = re.compile(r'([\u4e00-\u9fff]{2,4})比([\u4e00-\u9fff]{2,4})(大|小)(\d+)(个月|岁)')
        for match in comp_pattern.finditer(line):
            name1, name2, direction, num, unit = match.groups()
            num = int(num)
            
            if name1 in characters and name2 in characters:
                key = (name1, name2) if (name1, name2) in age_diffs else (name2, name1)
                if key in age_diffs:
                    actual_diff = abs(age_diffs[key])
                    actual_direction = '大' if age_diffs[key] > 0 else '小'
                    actual_older = key[0] if age_diffs[key] > 0 else key[1]
                    
                    if direction != actual_direction or num != actual_diff:
                        issues.append({
                            'type': '年龄对比错误',
                            'line': line_num,
                            'content': f"文中写'{name1}比{name2}{direction}{num}{unit}'，实际{actual_older}更大，相差{actual_diff}个月：{line.strip()[:80]}",
                            'suggestion': f"改为'{actual_older}比{key[1] if actual_older == key[0] else key[0]}大{actual_diff}个月'"
                        })
    
    return issues


# ============================================================
# v4.2.0 新增：同班同学年级一致性检测
# ============================================================

def detect_classmate_grade_mismatch(text, config):
    """检测同班同学年级不一致（v4.2.0新增）
    
    需要config中包含classmates配置，格式：
    ["苏晚", "郑好", "周鼎思"]
    以及characters中的grade字段
    """
    issues = []
    if not config or 'classmates' not in config or 'characters' not in config:
        return issues
    
    classmates = config['classmates']
    characters = config['characters']
    
    # 收集每个同学在文中出现的年级表述
    grade_mentions = {}
    lines = text.split('\n')
    
    grade_pattern = re.compile(r'(高一|高二|高三|大一|大二|大三|大四|初一|初二|初三)')
    
    for line_num, line in enumerate(lines, 1):
        for classmate in classmates:
            if classmate in line:
                for match in grade_pattern.finditer(line):
                    grade = match.group(1)
                    if classmate not in grade_mentions:
                        grade_mentions[classmate] = set()
                    grade_mentions[classmate].add((grade, line_num, line.strip()[:60]))
    
    # 检查是否有同学出现了不同的年级
    all_grades = set()
    for classmate, mentions in grade_mentions.items():
        for grade, _, _ in mentions:
            all_grades.add(grade)
    
    if len(all_grades) > 1:
        issues.append({
            'type': '同班同学年级不一致',
            'line': '全文',
            'content': f"同班同学出现了不同年级：{all_grades}。详情：" + 
                       "; ".join([f"{name}: {[g for g,_,_ in mentions]}" for name, mentions in grade_mentions.items()]),
            'suggestion': '同班同学默认同年级，如有人跳级/留级需在剧情中明确说明'
        })
    
    return issues


# ============================================================
# 主函数
# ============================================================

def load_config(config_path):
    """加载配置文件"""
    if not config_path or not os.path.exists(config_path):
        return None
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)



# ============================================================
# v4.3.0 新增：模板化重复场次检测
# ============================================================

def detect_template_repeated_scenes(text):
    """检测模板化重复场次（v4.3.0新增）
    
    检测同一类情节被拆成多场换汤不换药的模板。
    例如连续多场都是"他帮XX做了个XX事"的同一结构。
    """
    issues = []
    
    # 提取所有场次的标题和前几句
    scene_pattern = re.compile(r'第(\d+)场\s+(.+)')
    scenes = []
    current_scene = None
    current_lines = []
    
    for line in text.split('\n'):
        m = scene_pattern.match(line.strip())
        if m:
            if current_scene:
                scenes.append({'num': current_scene, 'title': current_title, 'lines': current_lines})
            current_scene = int(m.group(1))
            current_title = m.group(2)
            current_lines = []
        elif current_scene:
            current_lines.append(line.strip())
            if len(current_lines) > 10:
                scenes.append({'num': current_scene, 'title': current_title, 'lines': current_lines})
                current_scene = None
                current_lines = []
    
    if current_scene:
        scenes.append({'num': current_scene, 'title': current_title, 'lines': current_lines})
    
    # 检测"他帮XX做了个XX"模板
    help_pattern = re.compile(r'他帮[^，。、]{2,10}(做了|开了|搞了|装了|弄了|建了)[^，。]{2,15}')
    help_scenes = []
    for s in scenes:
        full_text = '\n'.join(s['lines'])
        matches = help_pattern.findall(full_text)
        if matches:
            help_scenes.append({'scene': s['num'], 'title': s['title'], 'matches': matches})
    
    if len(help_scenes) >= 4:
        # 收集所有匹配的动作类型
        all_actions = []
        for hs in help_scenes:
            all_actions.extend(hs['matches'])
        
        # 如果有4场以上都是"他帮XX做了XX"，判定为模板化重复
        issues.append({
            'type': '模板化重复场次',
            'position': f"第{help_scenes[0]['scene']}场至第{help_scenes[-1]['scene']}场",
            'content': f"发现{len(help_scenes)}场'他帮XX做了XX'模板化情节，涉及：{[hs['title'] for hs in help_scenes[:5]]}",
            'suggestion': f"同一类帮助他人情节最多保留2场有具体人物故事的，其余{len(help_scenes)-2}场必须合并或删除"
        })
    
    # 检测"老人学XX"类模板
    elder_pattern = re.compile(r'老人[^，。]{0,5}(学|教|会|弄)(视频|打车|挂号|交费|购物|拍照|发朋友圈|扫码|支付)')
    elder_count = 0
    elder_scenes = []
    for s in scenes:
        full_text = '\n'.join(s['lines'])
        if elder_pattern.search(full_text):
            elder_count += 1
            elder_scenes.append(s['num'])
    
    if elder_count >= 4:
        issues.append({
            'type': '模板化重复-老人学XX',
            'position': f"场次: {elder_scenes[:8]}",
            'content': f"发现{elder_count}场'老人学XX'模板化情节",
            'suggestion': "合并为1-2场有具体人物故事的戏，删除纯模板重复"
        })
    
    return issues


# ============================================================
# v4.3.0 新增：同一情节线重复检测
# ============================================================

def detect_plotline_repeated(text):
    """检测同一情节线重复写了多场（v4.3.0新增）
    
    检测关键情节关键词在多场中重复出现，且内容高度相似。
    """
    issues = []
    
    # 提取场次
    scene_pattern = re.compile(r'第(\d+)场\s+(.+)')
    scenes = []
    current_scene = None
    current_title = ''
    current_text = []
    
    for line in text.split('\n'):
        m = scene_pattern.match(line.strip())
        if m:
            if current_scene:
                scenes.append({'num': current_scene, 'title': current_title, 'text': '\n'.join(current_text)})
            current_scene = int(m.group(1))
            current_title = m.group(2)
            current_text = []
        elif current_scene:
            current_text.append(line)
    
    if current_scene:
        scenes.append({'num': current_scene, 'title': current_title, 'text': '\n'.join(current_text)})
    
    # 常见关键情节关键词
    plot_keywords = {
        '板车': ['板车', '拖车', '运输车上路'],
        'NAS': ['NAS', '存储服务器', '硬盘阵列'],
        '宣判': ['宣判', '判决', '法庭宣判'],
        '导弹': ['导弹', '第二枚', '拦截弹'],
        '安全门被撬': ['安全门', '撬门', '门被撬'],
        '飞机接地': ['接地', '降落', '触地'],
        '武警查验': ['武警', '查验', '检查站'],
        '带话': ['带话', '传话', '捎话'],
    }
    
    for plot_name, keywords in plot_keywords.items():
        matching_scenes = []
        for s in scenes:
            for kw in keywords:
                if kw in s['text']:
                    matching_scenes.append(s['num'])
                    break
        
        if len(matching_scenes) >= 3:
            issues.append({
                'type': f'情节线重复-{plot_name}',
                'position': f"场次: {matching_scenes[:8]}",
                'content': f"'{plot_name}'情节线在{len(matching_scenes)}场中出现",
                'suggestion': f"每个关键情节节点只写1场，多余的{len(matching_scenes)-1}场必须合并或删除"
            })
    
    return issues


# ============================================================
# v4.4.0 新增：同一人物送别情节重复检测
# ============================================================

def detect_repeated_farewells(text):
    """检测同一人物的送别/告别情节被写了多次（v4.4.0新增）"""
    issues = []
    
    # 提取场次
    scene_pattern = re.compile(r'第(\d+)场\s+(.+)')
    scenes = []
    current_scene = None
    current_title = ''
    current_text = []
    
    for line in text.split('\n'):
        m = scene_pattern.match(line.strip())
        if m:
            if current_scene:
                scenes.append({'num': current_scene, 'title': current_title, 'text': '\n'.join(current_text)})
            current_scene = int(m.group(1))
            current_title = m.group(2)
            current_text = []
        elif current_scene:
            current_text.append(line)
    
    if current_scene:
        scenes.append({'num': current_scene, 'title': current_title, 'text': '\n'.join(current_text)})
    
    # 检测"机场送别"模式
    farewell_keywords = ['机场', '候机', '登机', '送别', '送行', '拥抱', '挥手', '安检口', '检票口', '起飞']
    farewell_scenes = []
    for s in scenes:
        match_count = sum(1 for kw in farewell_keywords if kw in s['text'])
        if match_count >= 3:
            farewell_scenes.append({'scene': s['num'], 'title': s['title'], 'match_count': match_count})
    
    if len(farewell_scenes) >= 3:
        issues.append({
            'type': '同一人物送别重复',
            'position': f"场次: {[fs['scene'] for fs in farewell_scenes]}",
            'content': f"发现{len(farewell_scenes)}场机场送别情节",
            'suggestion': "同一人物的送别只写1场，多余的必须合并或改写为其他情节（如911飙车等）"
        })
    
    return issues


# ============================================================
# v4.4.0 新增：主场次与补充场人物去向矛盾检测
# ============================================================

def detect_departure_timeline_conflict(text):
    """检测主场次说人物已离开，补充场又写送别的矛盾（v4.4.0新增）"""
    issues = []
    
    # 提取场次和时间
    scene_pattern = re.compile(r'第(\d+)场.*?补充场|第(\d+)场\s')
    time_pattern = re.compile(r'时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2})[：:](\d{2})')
    
    scenes = []
    current_num = None
    current_is_supp = False
    current_time = None
    current_text = []
    
    for line in text.split('\n'):
        line_stripped = line.strip()
        
        # 检测补充场
        supp_match = re.match(r'^第(\d+)场补充场', line_stripped)
        main_match = re.match(r'^第(\d+)场\s+(.+)', line_stripped)
        
        if supp_match:
            if current_num:
                scenes.append({'num': current_num, 'is_supp': current_is_supp, 'time': current_time, 'text': '\n'.join(current_text)})
            current_num = int(supp_match.group(1))
            current_is_supp = True
            current_time = None
            current_text = []
        elif main_match:
            if current_num:
                scenes.append({'num': current_num, 'is_supp': current_is_supp, 'time': current_time, 'text': '\n'.join(current_text)})
            current_num = int(main_match.group(1))
            current_is_supp = False
            current_time = None
            current_text = []
        
        tm = time_pattern.match(line_stripped)
        if tm:
            y, m, d, h, mi = map(int, tm.groups())
            current_time = (y, m, d, h, mi)
        
        current_text.append(line)
    
    if current_num:
        scenes.append({'num': current_num, 'is_supp': current_is_supp, 'time': current_time, 'text': '\n'.join(current_text)})
    
    # 检测：主场次说"已离开/已起飞"，补充场时间更晚却又写"送别/登机"
    for i, s in enumerate(scenes):
        if not s['is_supp'] or not s['time']:
            continue
        
        # 找同号主场次
        main_scene = None
        for ms in scenes:
            if ms['num'] == s['num'] and not ms['is_supp']:
                main_scene = ms
                break
        
        if not main_scene or not main_scene['time']:
            continue
        
        # 如果补充场时间比主场次晚
        if s['time'] > main_scene['time']:
            # 检查主场次是否说人物已离开
            main_left = any(kw in main_scene['text'] for kw in ['已离开', '已走', '已起飞', '登机了', '走了', '离开了'])
            # 检查补充场是否又写送别
            supp_farewell = any(kw in s['text'] for kw in ['送她', '送他', '送别', '机场', '登机', '安检口', '晚上九点', '航班'])
            
            if main_left and supp_farewell:
                issues.append({
                    'type': '人物去向时间矛盾',
                    'position': f"第{s['num']}场 vs 第{s['num']}场补充场",
                    'content': f"主场次({main_scene['time']})写人物已离开，补充场({s['time']})又写送别/登机",
                    'suggestion': "补充场不得重复送别，应改写为其他情节或调整时间"
                })
    
    return issues

def main():
    if len(sys.argv) < 2:
        print("用法: python degradation_detector.py <文件路径> [--config <配置文件.json>]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    config = None
    
    if '--config' in sys.argv:
        idx = sys.argv.index('--config')
        if idx + 1 < len(sys.argv):
            config = load_config(sys.argv[idx + 1])
    
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("=" * 60)
    print("长文本退化模式检测报告 v4.4.0")
    print("=" * 60)
    print(f"文件: {file_path}")
    print(f"总行数: {len(text.split(chr(10)))}")
    print(f"总字符数: {len(text)}")
    print(f"中文字符数: {count_chinese_chars(text)}")
    if config:
        print(f"配置文件: 已加载（{len(config.get('characters', {}))}个人物，{len(config.get('key_events', {}))}个关键事件，{len(config.get('classmates', []))}个同学）")
    print()
    
    all_issues = []
    test_num = 0
    total_tests = 15
    
    test_num += 1
    print(f"【{test_num}/{total_tests}】主语动词逗号检测（含英文名）...")
    issues = detect_subject_verb_comma(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    test_num += 1
    print(f"【{test_num}/{total_tests}】碎片句检测...")
    issues = detect_fragment_sentences(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    test_num += 1
    print(f"【{test_num}/{total_tests}】对话标签逗号检测...")
    issues = detect_dialogue_tag_comma(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    test_num += 1
    print(f"【{test_num}/{total_tests}】空行密度检测...")
    issues = detect_excessive_empty_lines(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    test_num += 1
    print(f"【{test_num}/{total_tests}】连续相同句式检测...")
    issues = detect_repeated_sentence_starts(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    test_num += 1
    print(f"【{test_num}/{total_tests}】时间线递增检测...")
    issues = verify_timeline(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    if config:
        test_num += 1
        print(f"【{test_num}/{total_tests}】人物年龄-生日联动检测（v4.2.0）...")
        issues = detect_age_birthday_mismatch(text, config)
        print(f"  发现 {len(issues)} 处问题")
        all_issues.extend(issues)
        
        test_num += 1
        print(f"【{test_num}/{total_tests}】相对时间表述检测（v4.2.0）...")
        issues = detect_relative_time_mismatch(text, config)
        print(f"  发现 {len(issues)} 处问题")
        all_issues.extend(issues)
        
        test_num += 1
        print(f"【{test_num}/{total_tests}】人物年龄对比检测（v4.2.0）...")
        issues = detect_age_comparison_mismatch(text, config)
        print(f"  发现 {len(issues)} 处问题")
        all_issues.extend(issues)
        
        test_num += 1
        print(f"【{test_num}/{total_tests}】同班同学年级一致性检测（v4.2.0）...")
        issues = detect_classmate_grade_mismatch(text, config)
        print(f"  发现 {len(issues)} 处问题")
        all_issues.extend(issues)
    
    print()
    print("=" * 60)
    
    if all_issues:
        print(f"检测完成：共发现 {len(all_issues)} 处问题")
        print()
        print("问题详情（前40条）：")
        print("-" * 60)
        for i, issue in enumerate(all_issues[:40], 1):
            print(f"{i}. [{issue['type']}] 位置: {issue.get('line', issue.get('position', '未知'))}")
            print(f"   内容: {issue.get('content', '')}")
            print(f"   建议: {issue.get('suggestion', '')}")
            print()
        
        if len(all_issues) > 40:
            print(f"... 还有 {len(all_issues) - 40} 处问题未显示")
        
        print()
        print("结论：未通过质量检测，请修改后重新检测。")
        sys.exit(1)
    else:
        print("检测完成：未发现退化模式")
        print("结论：通过质量检测！")
        sys.exit(0)


if __name__ == '__main__':
    main()
