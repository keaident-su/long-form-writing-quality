#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长文本退化模式检测器
用于检测大模型生成超长篇文本时出现的碎片化断句、机械重复等退化问题。
用法: python degradation_detector.py <文件路径>
"""

import re
import sys
from collections import Counter


def detect_subject_verb_comma(text):
    """检测'主语，动词'碎片化断句模式（如'裴砚，说''钢哥，点头'）"""
    issues = []
    # 匹配：1-4个汉字 + 逗号 + 1-2个动词性汉字 + 标点
    pattern = re.compile(r'([\u4e00-\u9fff]{1,4})，([\u4e00-\u9fff]{1,2})([。，！？：；])')
    lines = text.split('\n')
    for line_num, line in enumerate(lines, 1):
        matches = pattern.findall(line)
        for subj, verb, punct in matches:
            # 排除一些合理的情况（如"他，一个人，走了"这种强调句式）
            # 但"XX说""XX点头"这种一定是错误的
            common_verbs = ['说', '问', '答', '道', '喊', '叫', '笑', '哭', '点', '摇', '坐', '站', '走', '跑', '看', '听', '想', '知']
            if verb in common_verbs or (verb + punct) in ['点头', '摇头', '说道', '问道', '答道']:
                issues.append({
                    'type': '主语动词逗号',
                    'line': line_num,
                    'content': f"{subj}，{verb}{punct}",
                    'suggestion': f"{subj}{verb}{punct}"
                })
    return issues


def detect_fragment_sentences(text):
    """检测碎片句（逗号过多且句子过短）"""
    issues = []
    lines = text.split('\n')
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        comma_count = line.count('，')
        # 超过3个逗号且长度小于40字符，很可能是碎片句
        if comma_count >= 3 and len(line) < 40:
            issues.append({
                'type': '碎片句',
                'line': line_num,
                'content': line,
                'comma_count': comma_count,
                'suggestion': '合并为完整句子，减少不必要的逗号停顿'
            })
    return issues


def detect_dialogue_tag_comma(text):
    """检测对话标签中的逗号错误（如'"XX，说："'）"""
    issues = []
    # 匹配引号结束 + 1-4个汉字 + 逗号 + 说/道/问/答 + 冒号
    pattern = re.compile(r'[”"]([\u4e00-\u9fff]{1,4})，([说道问回答喊叫])([：，])')
    lines = text.split('\n')
    for line_num, line in enumerate(lines, 1):
        matches = pattern.findall(line)
        for name, verb, punct in matches:
            issues.append({
                'type': '对话标签逗号',
                'line': line_num,
                'content': f'"{name}，{verb}{punct}',
                'suggestion': f'"{name}{verb}{punct}'
            })
    return issues


def detect_repeated_sentence_starts(text):
    """检测连续相同句式开头"""
    issues = []
    # 按句号、问号、感叹号分割句子
    sentences = re.split(r'[。！？]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    for i in range(len(sentences) - 5):
        window = sentences[i:i+7]
        # 取每句前3个字符
        starts = [s[:3] for s in window if len(s) >= 3]
        if len(starts) < 5:
            continue
        # 如果前3字符的去重数量 <= 2，说明句式高度重复
        counter = Counter(starts)
        if len(counter) <= 2:
            most_common = counter.most_common(1)[0]
            issues.append({
                'type': '连续相同句式',
                'position': f'第{i+1}句附近',
                'content': f'连续7句中有{most_common[1]}句以"{most_common[0]}"开头',
                'suggestion': '变化句式开头，避免机械重复'
            })
    return issues


def detect_excessive_short_paragraphs(text):
    """检测过多过短段落（连续10段以上每段只有1句话）"""
    issues = []
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    short_run = 0
    run_start = 0
    for i, p in enumerate(paragraphs):
        sentence_count = len(re.findall(r'[。！？]', p))
        if sentence_count <= 1 and len(p) < 30:
            if short_run == 0:
                run_start = i
            short_run += 1
        else:
            if short_run >= 8:
                issues.append({
                    'type': '过短段落密集',
                    'position': f'第{run_start+1}段至第{i}段',
                    'content': f'连续{short_run}段每段只有1句话且长度不足30字',
                    'suggestion': '合并相关段落，增加段落长度变化'
                })
            short_run = 0
    
    if short_run >= 8:
        issues.append({
            'type': '过短段落密集',
            'position': f'第{run_start+1}段至末尾',
            'content': f'连续{short_run}段每段只有1句话且长度不足30字',
            'suggestion': '合并相关段落，增加段落长度变化'
        })
    
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
        year, month, day, hour, minute = map(int, m)
        timestamps.append((year, month, day, hour, minute))
    
    for i in range(1, len(timestamps)):
        if timestamps[i] <= timestamps[i-1]:
            issues.append({
                'type': '时间倒流',
                'position': f'第{i+1}个时间戳',
                'content': f'{timestamps[i]} 不大于前一个 {timestamps[i-1]}',
                'suggestion': '调整时间顺序，确保严格递增'
            })
    
    return issues


def main():
    if len(sys.argv) < 2:
        print("用法: python degradation_detector.py <文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("=" * 60)
    print("长文本退化模式检测报告")
    print("=" * 60)
    print(f"文件: {file_path}")
    print(f"总字符数: {len(text)}")
    print(f"中文字符数: {count_chinese_chars(text)}")
    print()
    
    all_issues = []
    
    print("【1/6】主语动词逗号检测...")
    issues = detect_subject_verb_comma(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    print("【2/6】碎片句检测...")
    issues = detect_fragment_sentences(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    print("【3/6】对话标签逗号检测...")
    issues = detect_dialogue_tag_comma(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    print("【4/6】连续相同句式检测...")
    issues = detect_repeated_sentence_starts(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    print("【5/6】过短段落密集检测...")
    issues = detect_excessive_short_paragraphs(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    print("【6/6】时间线递增检测...")
    issues = verify_timeline(text)
    print(f"  发现 {len(issues)} 处问题")
    all_issues.extend(issues)
    
    print()
    print("=" * 60)
    
    if all_issues:
        print(f"检测完成：共发现 {len(all_issues)} 处退化问题")
        print()
        print("问题详情（前20条）：")
        print("-" * 60)
        for i, issue in enumerate(all_issues[:20], 1):
            print(f"{i}. [{issue['type']}] 位置: {issue.get('line', issue.get('position', '未知'))}")
            print(f"   内容: {issue.get('content', '')}")
            print(f"   建议: {issue.get('suggestion', '')}")
            print()
        
        if len(all_issues) > 20:
            print(f"... 还有 {len(all_issues) - 20} 处问题未显示")
        
        print()
        print("结论：未通过质量检测，请修改后重新检测。")
        sys.exit(1)
    else:
        print("检测完成：未发现退化模式")
        print("结论：通过质量检测！")
        sys.exit(0)


if __name__ == '__main__':
    main()
