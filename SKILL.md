---
name: long-form-writing-quality
description: 长文本写作质量控制Skill。专门用于防止大模型在生成超长篇文本（小说、剧本、报告等，单篇超过5000字）时出现的"长文本退化"现象——包括碎片化断句、机械重复句式、不必要的逗号插入、对话僵硬、语言流畅度下降等问题。提供分批生成工作流、退化模式检测规则、质量检查闸门、字数验证方法、场次顺序验证和时间线验证。适用于所有需要生成超过5000字连续文本的创作任务，特别是多场次剧本创作。
---

# 长文本写作质量控制 Skill

版本：2.0.0

## 核心问题

大模型在单次连续生成超过5000字的文本时，会出现**"长文本退化"（long-text degradation）**现象。这不是内容问题，而是生成方式的问题。退化的典型表现包括：

### 退化模式清单（绝对禁止）

| 退化模式 | 错误示例 | 正确写法 |
|---------|---------|---------|
| **主语后插逗号** | "裴砚，说""钢哥，点了点头""徐萱，坐在，旁边" | "裴砚说""钢哥点了点头""徐萱坐在旁边" |
| **句子碎片化** | "也可能，是，老挝当地的，警察。""我们，现在，在，老挝境内。" | "也可能是老挝当地的警察。""我们现在在老挝境内。" |
| **副词/助词后插逗号** | "然后，转身，走了。""实在，不行，再，考虑。" | "然后转身走了。""实在不行再考虑。" |
| **机械重复句式** | 连续多段都是"他，的心跳，开始，加速。""他，的心里，很，紧张。" | 句式要有变化，长短句交替 |
| **对话标签僵硬** | ""明白吗？""明白。"钢哥，点了点头，"我，这就，去安排。"" | ""明白吗？""明白。"钢哥点头，"我这就去安排。"" |
| **每句都加逗号停顿** | "他，看着，窗外，的，雨，心里，很，难过。" | "他看着窗外的雨，心里很难过。" |
| **段落过短过碎** | 每段只有1-2句话，且都是碎片句 | 段落长度要有变化，动作描写和心理描写可以合并 |
| **空行密度过高** | 每段之间都有2个以上空行，一页没几行字 | 段落之间最多1个空行，连续空行是"注水"行为 |
| **英文名后插逗号** | "Karen，坐在""David，说" | "Karen坐在""David说"，英文名同样适用主语逗号规则 |

### 场次顺序错乱（剧本专用，绝对禁止）

| 错误模式 | 错误示例 | 正确做法 |
|---------|---------|---------|
| **文件按文件名排序导致场次错乱** | act2_part10.txt（第84场）排在act2_part2.txt（第58场）前面 | 合并时必须按场次编号排序，不能按文件名排序 |
| **补充场次未放在对应主场次下方** | 第55场补充场排在第83场之后 | 补充场次必须紧跟在对应主场次的下方 |
| **补充场次时间戳超出对应主场次时间范围** | 第55场补充场时间是9月6日，而第56场是9月5日 | 补充场次时间必须在对应主场次之后、下一个主场次之前 |
| **主场次时间戳倒流** | 第1场是4月5日，第2场是4月7日，第3场是4月6日 | 所有场次时间戳必须严格单调递增 |

### 退化的根本原因

1. 单次生成太长，模型注意力被稀释
2. 没有分批控制，每批生成后没有质量检查
3. 为了凑字数而"注水"，用碎片句填充
4. 为了凑页数而"注水"，用大量空行撑开篇幅
5. 缺少对自然语言节奏的感知——中文不是每两个字就要停顿一次，段落之间也不是每段都要空两行
6. 合并时按文件名排序而非按场次编号排序，导致场次顺序错乱
7. 补充场次时间戳设置不合理，导致时间线倒流

## 工作流（必须严格遵守）

### 第一步：任务拆解

在开始任何超过5000字的写作任务前，必须先拆解：

1. **确定总字数目标**（如：85000字）
2. **拆分为独立单元**（如：每集一个单元，每集约10000字）
3. **每个单元再拆分为批次**（每批不超过4000字，约2-3场戏）
4. **建立批次清单**，明确每批的内容范围、时间线、出场人物、场次编号
5. **建立全局场次编号表**，明确所有主场次和补充场次的编号、时间戳、对应关系

### 第二步：分批生成

**每批生成严格控制在4000字以内**（中文字符）。生成时必须遵守：

1. **自然语言节奏**：中文句子的逗号停顿应该在语义自然的地方，不是每两个字就停一次。正常的一句话应该是完整的主谓宾结构，中间不需要插入不必要的逗号。
2. **对话标签规范**："XX说"后面直接跟冒号和引号，不要在"说"前面加逗号。动作描写可以放在对话前后，但要自然。
3. **句式变化**：长短句交替，不要连续使用相同的句式。动作描写用短句，心理描写和环境描写可以用长句。
4. **段落长度变化**：不要每段都是1-2句话。动作密集的场景可以用短段落，心理活动和环境描写可以用长段落。
5. **空行控制**：段落之间最多1个空行（即两个段落之间有且仅有一个空白行）。绝对禁止每段之间都有2个以上空行——这是用空行"注水"凑页数的退化行为。场景切换、时间跳转可以用空行+分隔线，但普通段落之间不得连续空行。
6. **禁止注水**：不要为了凑字数而重复描写、用碎片句填充。每一句话都应该有信息增量。不要为了凑页数而插入大量空行。
7. **场次编号连续**：每批生成的场次编号必须与全局场次编号表一致，不得跳号、重号。
8. **时间戳严格递增**：每批生成的场次时间戳必须严格递增，不得倒流。补充场次时间戳必须在对应主场次之后、下一个主场次之前。

### 第三步：每批质量检查（闸门）

**每批生成完成后，必须进行质量检查，通过后才能继续下一批。**

检查清单：

- [ ] **退化模式扫描**：搜索是否存在"主语，动词"模式（如"裴砚，说""徐萱，坐在""Karen，坐在"）
- [ ] **碎片句检查**：是否存在超过3个逗号的短句（如"也可能，是，老挝，的，警察"）
- [ ] **对话标签检查**：对话标签是否自然，有没有"XX，说"这种错误
- [ ] **空行密度检查**：段落之间是否有连续2个以上空行，一页内容是否过于稀疏
- [ ] **句式重复检查**：连续5段以上是否使用了相同的句式开头
- [ ] **流畅度朗读测试**：默读一段，是否通顺自然，有没有卡顿感
- [ ] **时间线检查**：本场的时间是否严格递增，有没有倒流
- [ ] **场次编号检查**：本场的场次编号是否与全局场次编号表一致，有没有跳号、重号
- [ ] **补充场次位置检查**：补充场次是否放在了对应主场次的下方
- [ ] **人物一致性检查**：人物的年龄、身份、性格是否与设定一致

**如果任何一项不通过，必须重写该批，不能带着问题继续。**

### 第四步：合并与最终验证

所有批次完成后：

1. **使用标准合并脚本合并所有批次**（必须按场次编号排序，不能按文件名排序）
2. **全量退化模式扫描**（用脚本检测，见下方）
3. **场次顺序验证**（所有主场次按编号递增，补充场次在对应主场次下方）
4. **字数验证**（中文字符数必须达到目标）
5. **时间线全量检查**（所有场次的时间戳严格单调递增）
6. **通读流畅度检查**（至少通读全文一遍，标记不通顺的地方并修改）

## 标准合并脚本（剧本专用，必须使用）

**绝对禁止使用简单的文件名字典序排序合并！** 必须使用以下脚本，按场次编号排序，补充场次放在对应主场次下方：

```python
import re
import os

def merge_scenes(files_dir, output_path, file_prefixes=['act_part', 'act_supplement']):
    """
    标准剧本合并脚本
    按场次编号排序，补充场次放在对应主场次下方
    
    参数：
        files_dir: 分片文件所在目录
        output_path: 输出文件路径
        file_prefixes: 要合并的文件前缀列表
    """
    all_files = []
    
    # 读取所有分片文件
    for filename in os.listdir(files_dir):
        for prefix in file_prefixes:
            if filename.startswith(prefix) and filename.endswith('.txt'):
                filepath = os.path.join(files_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                all_files.append((filename, content))
                break
    
    print(f"读取了 {len(all_files)} 个文件")
    
    # 解析每个文件中的场次
    all_scenes = []
    
    for filename, content in all_files:
        lines = content.split('\n')
        current_scene_lines = []
        current_scene_title = None
        current_scene_number = None
        current_is_supplement = False
        current_supplement_number = None
        
        for line in lines:
            stripped = line.strip()
            
            # 检测主场次标题（如"第55场"）
            main_scene_match = re.match(r'^第(\d+)场$', stripped)
            # 检测补充场标题（如"第55场补充场（一）"）
            supplement_match = re.match(r'^第(\d+)场补充场（([一二三四五六七八九十]+)）', stripped)
            
            if main_scene_match and not supplement_match:
                # 保存上一个场次
                if current_scene_title:
                    all_scenes.append({
                        'title': current_scene_title,
                        'number': current_scene_number,
                        'is_supplement': current_is_supplement,
                        'supplement_order': current_supplement_number,
                        'content': '\n'.join(current_scene_lines)
                    })
                
                current_scene_title = stripped
                current_scene_number = int(main_scene_match.group(1))
                current_is_supplement = False
                current_supplement_number = None
                current_scene_lines = [line]
            
            elif supplement_match:
                # 保存上一个场次
                if current_scene_title:
                    all_scenes.append({
                        'title': current_scene_title,
                        'number': current_scene_number,
                        'is_supplement': current_is_supplement,
                        'supplement_order': current_supplement_number,
                        'content': '\n'.join(current_scene_lines)
                    })
                
                current_scene_title = stripped
                current_scene_number = int(supplement_match.group(1))
                current_is_supplement = True
                # 将中文数字转换为排序值
                cn_num = supplement_match.group(2)
                cn_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
                          '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
                current_supplement_number = cn_map.get(cn_num, 0)
                current_scene_lines = [line]
            
            else:
                current_scene_lines.append(line)
        
        # 保存最后一个场次
        if current_scene_title:
            all_scenes.append({
                'title': current_scene_title,
                'number': current_scene_number,
                'is_supplement': current_is_supplement,
                'supplement_order': current_supplement_number,
                'content': '\n'.join(current_scene_lines)
            })
    
    print(f"解析出 {len(all_scenes)} 个场次")
    
    # 按场次编号排序，主场次在前，补充场次在后（按补充场顺序）
    def sort_key(scene):
        if scene['is_supplement']:
            return (scene['number'], 1, scene['supplement_order'])
        else:
            return (scene['number'], 0, 0)
    
    all_scenes.sort(key=sort_key)
    
    # 打印排序后的场次顺序
    print("\n排序后的场次顺序：")
    for i, scene in enumerate(all_scenes):
        print(f"  {i+1:3d}. {scene['title']}")
    
    # 合并所有场次
    merged_content = ""
    for scene in all_scenes:
        merged_content += scene['content']
        merged_content += "\n\n"
    
    # 保存合并后的文本
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(merged_content)
    
    print(f"\n合并后的文本已保存到: {output_path}")
    
    return merged_content

# 使用方法
# merge_scenes('你的分片文件目录', '输出文件路径', ['act2_part', 'act2_supplement'])
```

## 退化模式自动检测脚本

生成完成后，必须运行以下Python脚本进行自动检测：

```python
import re

def detect_degradation(text):
    """检测长文本退化模式，返回问题列表"""
    issues = []
    
    # 模式1：主语+逗号+单字动词（如"裴砚，说""钢哥，点头"）
    pattern1 = re.compile(r'[\u4e00-\u9fff]{1,4}，[\u4e00-\u9fff]{1,2}[。，！？]')
    matches1 = pattern1.findall(text)
    if matches1:
        issues.append(f"发现{len(matches1)}处'主语，动词'碎片化断句，示例：{matches1[:5]}")
    
    # 模式2：一句话中超过4个逗号（碎片句）
    lines = text.split('\n')
    fragment_lines = []
    for i, line in enumerate(lines):
        if line.count('，') >= 4 and len(line) < 50:
            fragment_lines.append((i+1, line.strip()))
    if fragment_lines:
        issues.append(f"发现{len(fragment_lines)}处碎片句（逗号过多且句子过短），示例：{fragment_lines[:3]}")
    
    # 模式3：对话标签中的逗号（如"XX，说："）
    pattern3 = re.compile(r'[""][\u4e00-\u9fff]{1,4}，[说道问回答喊叫][：，]')
    matches3 = pattern3.findall(text)
    if matches3:
        issues.append(f"发现{len(matches3)}处对话标签逗号错误，示例：{matches3[:5]}")
    
    # 模式4：连续相同句式开头
    sentences = re.split(r'[。！？]', text)
    repeated_starts = []
    for i in range(len(sentences)-5):
        starts = [s.strip()[:3] for s in sentences[i:i+6] if s.strip()]
        if len(set(starts)) <= 2 and len(starts) >= 5:
            repeated_starts.append((i, starts))
    if repeated_starts:
        issues.append(f"发现{len(repeated_starts)}处连续相同句式开头，示例位置：{repeated_starts[:3]}")
    
    # 模式5：连续空行（超过2个）
    max_consecutive_empty = 0
    current_empty = 0
    for line in lines:
        if line.strip() == '':
            current_empty += 1
            max_consecutive_empty = max(max_consecutive_empty, current_empty)
        else:
            current_empty = 0
    if max_consecutive_empty > 2:
        issues.append(f"发现连续{max_consecutive_empty}个空行（超过2个即为注水）")
    
    return issues
```

## 场次顺序和时间线验证脚本（剧本专用，必须运行）

```python
import re

def verify_scene_order_and_timeline(text):
    """
    验证场次顺序和时间线
    返回问题列表
    """
    issues = []
    
    # 解析所有场次
    lines = text.split('\n')
    scenes = []
    current_scene = None
    current_time = None
    
    for line in lines:
        stripped = line.strip()
        
        # 检测主场次标题
        main_scene_match = re.match(r'^第(\d+)场$', stripped)
        # 检测补充场标题
        supplement_match = re.match(r'^第(\d+)场补充场（([一二三四五六七八九十]+)）', stripped)
        
        if main_scene_match and not supplement_match:
            if current_scene:
                scenes.append((current_scene, current_time))
            current_scene = stripped
            current_time = None
        elif supplement_match:
            if current_scene:
                scenes.append((current_scene, current_time))
            current_scene = stripped
            current_time = None
        
        # 检测时间戳
        time_match = re.match(r'^时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2})[：:](\d{2})', stripped)
        if time_match:
            year, month, day, hour, minute = map(int, time_match.groups())
            current_time = (year, month, day, hour, minute)
    
    if current_scene:
        scenes.append((current_scene, current_time))
    
    # 验证场次编号顺序
    scene_numbers = []
    for scene, time in scenes:
        match = re.match(r'^第(\d+)场', scene)
        if match:
            scene_numbers.append(int(match.group(1)))
    
    # 检查主场次编号是否递增
    main_scene_numbers = []
    for i, (scene, time) in enumerate(scenes):
        if '补充场' not in scene:
            match = re.match(r'^第(\d+)场', scene)
            if match:
                num = int(match.group(1))
                if main_scene_numbers and num <= main_scene_numbers[-1]:
                    issues.append(f"主场次编号倒流：第{num}场在第{main_scene_numbers[-1]}场之后")
                main_scene_numbers.append(num)
    
    # 检查补充场次是否在对应主场次之后
    last_main_scene_num = None
    for i, (scene, time) in enumerate(scenes):
        if '补充场' in scene:
            match = re.match(r'^第(\d+)场补充场', scene)
            if match:
                supplement_num = int(match.group(1))
                if last_main_scene_num is None or supplement_num != last_main_scene_num:
                    issues.append(f"补充场{scene}不在对应主场次第{supplement_num}场之后（上一个主场次是第{last_main_scene_num}场）")
        else:
            match = re.match(r'^第(\d+)场', scene)
            if match:
                last_main_scene_num = int(match.group(1))
    
    # 验证时间线严格递增
    timestamps = [time for scene, time in scenes if time]
    for i in range(1, len(timestamps)):
        if timestamps[i] <= timestamps[i-1]:
            issues.append(f"时间线倒流：第{i+1}个时间戳{timestamps[i]}不大于前一个{timestamps[i-1]}")
    
    return issues
```

## 写作风格规范（剧本专用）

### 对话描写规范

**正确写法：**
```
裴砚说："我们必须在天亮前越过边境。"
钢哥点头："明白，我这就去安排。"
徐萱坐在旁边，把他们的对话都听在了耳朵里。他的心跳开始加速——有人在跟踪他们，而且已经跟了六个小时了。
```

**错误写法（绝对禁止）：**
```
裴砚，说："我们，必须，在，天亮前，越过，边境。"
钢哥，点了点头："明白，我，这就，去，安排。"
徐萱，坐在，旁边，把，他们的，对话，都，听在了，耳朵里。
他，的心跳，开始，加速。
有人，在，跟踪，他们。
而且，已经，跟了，六个小时了。
```

### 动作描写规范

- 动作描写用短句，但不要把一个完整的动作拆成碎片
- 连续动作可以合并在一句话里，用逗号分隔不同的动作
- 心理活动和动作可以交替，但不要每句都是"他，的心里，很，XX"

### 环境描写规范

- 环境描写可以用长句，营造氛围
- 感官细节（视觉、听觉、嗅觉、触觉）要有，但不要堆砌
- 环境描写要服务于剧情和人物心情，不要为了描写而描写

### 场次格式规范

- 主场次标题格式：`第XX场`（如"第55场"）
- 补充场标题格式：`第XX场补充场（一）`（如"第55场补充场（一）"）
- 每场必须包含：时间戳、地点、出场人物、详细剧情
- 时间戳格式：`时间：YYYY年MM月DD日 HH:MM`（如"时间：2026年9月3日 08:00"）
- 补充场次必须紧跟在对应主场次的下方
- 补充场次时间戳必须在对应主场次之后、下一个主场次之前

## 字数验证方法

```python
def count_chinese_chars(text):
    """统计中文字符数（不含标点、空格、英文）"""
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff')

def count_total_chars(text):
    """统计总字符数（含标点、空格、英文）"""
    return len(text)
```

**验证标准：**
- 剧情核心场次的中文字符数必须达到目标（如80000字）
- 总字符数（含标点）必须达到目标（如85000字）
- 每场的字数分布要均匀，不要某场特别长、某场特别短

## 时间线验证方法

见上方"场次顺序和时间线验证脚本"。

## 准出条件

在交付任何长文本作品前，必须同时满足以下所有条件：

1. ✅ 退化模式自动检测通过（0个问题，含空行密度检测）
2. ✅ 中文字符数达到目标
3. ✅ 总字符数达到目标
4. ✅ 时间线严格单调递增（0个倒流）
5. ✅ 场次编号严格递增（0个倒流，0个跳号，0个重号）
6. ✅ 所有补充场都放在了对应场次的下方
7. ✅ 空行密度正常（段落之间最多1个空行，无连续空行注水）
8. ✅ 全文通读至少一遍，标记的不通顺处已全部修改
9. ✅ 人物年龄、身份、性格与设定一致
10. ✅ 使用标准合并脚本合并（禁止按文件名字典序排序）

**任何一项不通过，不得交付。**

## 常见问题

### Q：为什么不能一次生成全部内容？
A：大模型的注意力机制有限，单次生成超过4000字后质量会开始下降。分批生成+每批检查是保证质量的唯一可靠方式。

### Q：每批4000字会不会太慢？
A：质量比速度重要。一次生成8000字但后半段全是碎片句，反而需要花更多时间重写。分批4000字+检查，总时间反而更短。

### Q：退化模式检测脚本会误报吗？
A：可能会有少量误报（比如某些特殊的文学风格确实需要短句子）。但检测到的每一处都应该人工确认，不能直接忽略。如果确实是有意为之的风格，可以标注后保留。

### Q：已经生成了有退化问题的文本怎么办？
A：不要试图在原文上逐句修改（效率太低）。应该定位到退化开始的位置，从那个位置开始重新分批生成，前面质量好的部分可以保留。

### Q：为什么合并时不能按文件名排序？
A：因为文件名的字典序与场次编号的数值序不一致。例如：act2_part10.txt（第84场）在字典序中会排在act2_part2.txt（第58场）前面，导致场次顺序错乱。必须使用标准合并脚本，按场次编号排序。

### Q：补充场次的时间戳应该怎么设置？
A：补充场次的时间戳必须在对应主场次之后、下一个主场次之前。例如：第55场是9月3日，第56场是9月5日，那么第55场补充场的时间戳必须在9月3日之后、9月5日之前（如9月4日）。绝对不能设置成9月6日，否则会导致时间线倒流。

### Q：如何避免场次编号跳号或重号？
A：在任务拆解阶段，必须建立全局场次编号表，明确所有主场次和补充场次的编号、时间戳、对应关系。每批生成时，必须与全局场次编号表核对，确保编号连续、不跳号、不重号。

