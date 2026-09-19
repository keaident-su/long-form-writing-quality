---
name: long-form-writing-quality
description: 长文本写作质量控制Skill。专门用于防止大模型在生成超长篇文本（小说、剧本、报告、长文、文档等，单篇超过5000字）时出现的"长文本退化"现象——包括碎片化断句、机械重复句式、不必要的逗号插入、对话僵硬、语言流畅度下降、剧情重复、时间线矛盾、人物年龄错误等问题。提供分批生成工作流、退化模式检测规则、质量检查闸门、字数验证方法、时间线验证、剧情逻辑连贯性检测、人物年龄-生日联动检测、情节重复检测。适用于所有需要生成超过5000字连续文本的创作任务（小说、剧本、报告、长文档、白皮书等）。
---

# 长文本写作质量控制 Skill

版本：4.5.0

## 适用范围

本 Skill 适用于**所有类型的长文本创作**，包括但不限于：
- **剧本创作**（多场次、多集数）
- **小说创作**（长篇、多章节）
- **报告/文档**（白皮书、研究报告、年度总结）
- **任何超过5000字的连续文本**

核心规则是**通用的**（适用于所有长文本类型）；标注"剧本专用"的规则仅在剧本创作时启用。

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

### 剧情逻辑错乱（剧本专用，绝对禁止，v3.0.0新增）

| 错误模式 | 错误示例 | 正确做法 |
|---------|---------|---------|
| **人物在事件发生前就出现在目的地** | 第96场（8月3日）老K已在曼谷见王子，但第98场（8月5日）车队才从泰缅边境出发 | 必须解释人物如何提前到达（如乘私人飞机先去），或调整时间线 |
| **不同人物使用相同名字** | 第95场中国驻泰国大使叫"王建国"，第95场补充场公安部国际合作局局长也叫"王建国" | 不同人物必须使用不同的名字，避免混淆 |
| **主场次与补充场内容严重重复** | 第116场和第116场补充场都是公司账目处理，内容几乎完全一样 | 补充场必须提供与主场次不同的内容、视角或情节 |
| **主场次与补充场情节矛盾** | 第101场说定位器在车机系统主机里面，第101场补充场说定位器在汽车底盘下面 | 同一事件的细节必须保持一致，不能前后矛盾 |
| **"第一次"类情节前后不一致** | 第100场说7月28日在缅甸第一次开车，第98场说8月5日第一次开车 | "第一次"类情节必须前后一致，明确区分不同场景的"第一次" |
| **星期几错误** | 2027年8月5日说是星期三（实际是星期四） | 必须根据日期自动计算正确的星期几 |
| **相邻场次情节相似度太高** | 第107场和第109场都是堵车+主角私自离队买东西+车队走了+安保人员留下等他 | 相邻场次必须有不同的情节和冲突，不能重复使用相同的桥段 |
| **集数标注缺失（v4.0.0新增）** | 第三幕、第四幕完全没有"第X集"标注，只有场次编号 | 每集开始时必须有集数标题（如"第5集：标题"）和时间线，多幕剧本必须标注季数（如"第二季 第1集"） |
| **集数编号断裂或重复（v4.0.0新增）** | 第4集之后直接跳到第6集，或同一集号出现两次 | 集数编号必须连续、不重复，跨文档时必须衔接（如上集第8集，下集从第8集续或第9集开始） |
| **日本学制错误（v4.0.0新增）** | 2029年3月说"你才大二"（实际仍是大一，4月才升大二）；说"三年硕士"（日本修士为2年） | 日本大学学年4月开始、翌年3月结束；本科4年、修士（硕士）2年；3月仍是当前学年，4月才升新学年 |
| **年龄与时间线不匹配（v4.0.0新增）** | 主角2016年5月生，2029年7月的场景写"十五岁"（实际13岁） | 必须根据出生日期和场景日期计算实际年龄，未到生日前不增岁 |
| **年级与时间线不匹配（v4.0.0新增）** | 2028年4月入学，2029年9月写"大四开学"（实际应为大二） | 必须根据入学年份和场景日期计算当前年级；提前毕业/跳级必须有明确情节说明 |
| **场次必填字段缺失（v4.1.0新增）** | 第203场只有正文，缺"时间：""地点：""出场人物："任一字段，或缺"大纲锚点（作者口径）" | 每场必须包含：大纲锚点（作者口径）、时间：、地点：、出场人物：（可写"人物："）四个必填字段，字段名照抄不得改写 |
| **集头必填字段缺失（v4.1.0新增）** | 某集只有"第X集：标题"一行，缺"本集概要（按作者更正口径）"或"本集场次"说明 | 每集集头必须包含：集标题（推荐格式"第二季·第X集《集名》"）、本集概要（按作者更正口径）、本集场次（起止场号）三个必填字段 |
| **日本9月误写为新学期（v4.1.0新增）** | 2028年9月日本校园场景写"新学期开始""新学年开学""九月开学" | 日本学年4月才开始，9月是前期末尾/暑假结束，只能写"暑假结束""回到学校""後期即将开始"等，禁止写"新学期/新学年开学" |
| **人物年龄未到生日误增岁（v4.2.0新增）** | 主角2016年4月8日生，2034年3月的场景写"十八岁"（实际还没到4月生日，应为17岁） | 必须根据出生日期和场景日期精确计算年龄，未到生日不增岁。生日在场景日期之前才增岁 |
| **相对时间表述与实际时间线矛盾（v4.2.0新增）** | 主角2026年7月（10岁）逃亡，2033年11月回国，文中写"七岁走，十七岁回来"（应为"十岁走"） | 所有"X年前/后""X岁时离开/回来"等相对时间表述，必须与实际事件日期和人物出生日期核对一致 |
| **人物年龄对比写反（v4.2.0新增）** | 徐萱2016年4月生，苏晚2016年8月生，文中写"他比苏晚小两个月"（实际大四个月） | "A比B大/小X个月/岁"必须与两人的出生日期精确核对，不得写反 |
| **关键事件年龄与事件日期矛盾（v4.2.0新增）** | 主角2026年1月（9岁）父母空难、2026年4月（10岁）其他亲人车祸，文中写"十二岁失去所有长辈"（应为十岁） | "X岁时失去亲人/父母去世/发生某事"必须与事件实际发生日期和人物出生日期核对一致 |
| **同班同学年级不一致（v4.2.0新增）** | 主角的小学同学，有的写"读高三"，有的写"读高二"，无跳级/留级说明 | 主角的同班同学默认都是同年级的；如有人跳级/留级/提前毕业，必须在剧情中有明确说明 |
| **模板化重复场次（v4.3.0新增）** | 连续8场都是"他帮社区开了个老人学XX小课"（视频通话、进阶班、发朋友圈、拍照、交水电费、打车、买东西、挂号看病），每场结构完全相同，只换具体事项 | 同一类"帮助老人"情节最多保留1-2场有具体人物故事的，其余必须合并或删除；禁止用"万能帮助模板"凑场次数量 |
| **同一情节线重复写（v4.3.0新增）** | 板车上路写2场、NAS检查写2场、宣判写2场、导弹发射写2场、安全门被撬写2场、飞机接地写2场 | 每个关键情节节点只写1场；如需多角度呈现，用补充场但必须提供新信息（不同人物视角/新发现/转折），不能重复同一动作 |
| **"万能帮助"桥段滥用（v4.3.0新增）** | 主角在社区里连续帮不同老人做不同小事（学视频通话、学打车、学挂号、学交水电费…），每场都是"老人有困难→主角帮忙→老人感谢"的同一结构 | 社区帮助类情节必须合并为1-2场有具体人物故事的戏（如陈奶奶和深圳儿子视频、刘爷爷半夜按钮响、王大爷交了一辈子现金），不能拆成N场换汤不换药的模板 |
| **同集内情节雷同度超标（v4.3.0新增）** | 同一集里连续多场的情节骨架相同（都是遇到困难主角解决对方感谢），只是场景和道具换了 | 同集内必须有不同的情节类型（冲突/转折/人物揭示/动作戏/情感戏），不能全是同一结构的流水账 |
| **同一事件重复叙述（通用，v4.5.0升级）** | 同一事件（送别/会议/战斗/事件）在不同章节/段落中被写了2-3遍，内容高度相似 | 同一事件只叙述1次；如需多角度呈现，用不同视角或新信息补充，不能重复同一事件的同一过程 |
| **人物去向前后矛盾（通用，v4.5.0升级）** | 前文写某人已离开/已到达，后文又写送他/接他，导致时间线自相矛盾 | 人物去向（离开/到达）必须前后一致；如有变动必须有明确的情节说明 |
| **时间线自相矛盾（通用，v4.5.0升级）** | 同一事件的时间在不同章节中说法不一（一场说下午的飞机，另一场说明天晚上的飞机） | 同一事件的时间在所有章节中必须一致；如有变动必须有明确说明 |
| **跨年引用错误（通用，v4.5.0升级）** | 引用年度事件（年度赛事、跨年晚会、年度颁奖等）时，年份与实际时间线不符 | 引用年度事件时，年份必须与文本中的时间线一致，不得把2033年的事件写成2034年 |
| **模板化重复段落（通用，v4.5.0升级）** | 连续多段使用相同结构（如"他帮XX做了XX事"），只换具体事项 | 同一模板最多出现1-2次，且第2次必须有新的信息增量 || **同一事件多场重复送别（v4.4.0新增）** | 180补3、181场、181补2三场都在机场送小晚，同一对人物的离别戏被拆成三场 | 同一对人物的送别/离别戏只写1场；如需多角度呈现，用补充场但必须提供新信息（如送别后的反应、另一个人的视角），不能重复同一送别动作 |
| **主场次与补充场事件状态矛盾（v4.4.0新增）** | 181场（7月8日13:00）写小晚已在机场离开，但181补2（7月9日21:30）又写送她上晚上九点的航班 | 补充场的事件状态必须与主场次一致：如果主场次说人已经走了，补充场不能又写送她走；补充场时间戳必须在主场次之前或之后，不能出现人已经走了又正在送的矛盾 |
| **同一事件的送别/离别在多场中重复出现（v4.4.0新增）** | 送A去机场写了2场、送B去车站写了2场、告别戏写了3场 | 每个送别/离别事件只写1场；如需要写送别后的余韵，用主角的内心独白或后续反应来呈现，不能再写一遍送别过程 |

### 退化的根本原因

1. 单次生成太长，模型注意力被稀释
2. 没有分批控制，每批生成后没有质量检查
3. 为了凑字数而"注水"，用碎片句填充
4. 为了凑页数而"注水"，用大量空行撑开篇幅
5. 缺少对自然语言节奏的感知——中文不是每两个字就要停顿一次，段落之间也不是每段都要空两行
6. 合并时按文件名排序而非按场次编号排序，导致场次顺序错乱
7. 补充场次时间戳设置不合理，导致时间线倒流
8. 分批生成时缺少全局剧情一致性检查，导致人物名字冲突、情节矛盾、内容重复等问题
9. 缺少星期几自动校验机制，导致大量星期几错误
10. 缺少集数标注规划，导致多幕剧本中部分幕完全丢失"第X集"标注（v4.0.0新增）
11. 缺少外国学制校验，日本等国的学年起止、年级升降、学制年限容易写错（v4.0.0新增）
12. 缺少人物年龄与时间线的联动校验，导致年龄不随场景日期变化（v4.0.0新增）
13. 缺少场次/集头必填字段的格式校验，导致生成时随意省略"时间/地点/人物/大纲锚点""本集概要/本集场次"等结构字段（v4.1.0新增）
14. 对日本学年的认识停留在"春季入学"粗粒度，未区分9月（前期末/暑假结束）与4月（新学年开始），导致9月被误写为"新学期/新学年开学"（v4.1.0新增）
15. 缺少人物出生日期与场景日期的精确联动校验，导致未到生日就误增岁（如3月写18岁，实际4月才生日）（v4.2.0新增）
16. 缺少相对时间表述（"X年前离开""X岁时发生"）与实际时间线的交叉校验，导致逃亡年龄、失去长辈年龄等关键数字写错（v4.2.0新增）
17. 缺少人物年龄对比（"A比B大/小X个月"）与出生日期的联动校验，导致年龄对比写反（v4.2.0新增）
18. 缺少同班同学年级一致性校验，默认同班同学应同年级，跳级/留级必须有明确情节说明（v4.2.0新增）
19. 缺少模板化重复场次检测：AI为了凑场次数量，把同一类情节拆成N场换汤不换药的模板（如"帮老人学XX"连续8场），每场结构相同只换具体事项（v4.3.0新增）
20. 缺少同一情节线重复检测：AI把关键情节节点（板车上路、NAS入库、宣判、导弹发射等）重复写2场以上，内容高度重复（v4.3.0新增）
21. 缺少"万能帮助"桥段滥用检测：主角连续帮不同人做同类小事，每场都是"遇到困难→帮忙→感谢"的同一结构（v4.3.0新增）
22. 缺少同一人物送别/告别情节重复检测：同一人物的送别被写了2-3场，每场都是"机场告别/拥抱/流泪"的同一结构（v4.4.0新增）
23. 缺少主场次与补充场人物去向矛盾检测：主场次说人物已离开，补充场又写送别，导致时间线自相矛盾（v4.4.0新增）
24. 缺少跨年引用年份校验：跨年事件（年度赛事、跨年晚会等）的年份引用与实际时间线不符（v4.4.0新增）

## 工作流（必须严格遵守）

### 第一步：任务拆解

在开始任何超过5000字的写作任务前，必须先拆解：

1. **确定总字数目标**（如：85000字）
2. **拆分为独立单元**（如：每集一个单元，每集约10000字）
3. **每个单元再拆分为批次**（每批不超过4000字，约2-3场戏）
4. **建立批次清单**，明确每批的内容范围、时间线、出场人物、场次编号
5. **建立全局场次编号表**，明确所有主场次和补充场次的编号、时间戳、对应关系
6. **建立全局人物表**（v3.0.0新增），明确所有人物的姓名、身份、年龄、性格特征，确保不同人物不使用相同名字
7. **建立全局剧情一致性检查表**（v3.0.0新增），记录关键情节节点（如"第一次开车"、"定位器位置"等），确保前后一致
8. **建立全局集数编号表**（v4.0.0新增），明确每集的编号、标题、时间线范围、对应的场次编号区间，跨文档时标注季数和衔接关系
9. **建立全局人物年龄-年级对应表**（v4.0.0新增），记录每个人物的出生日期，并根据时间线推算每个关键时间点的年龄和在读年级；涉及日本学校时必须标注"4月入学、3月毕业"的学制规则
10. **建立外国学制参考表**（v4.0.0新增），如剧情涉及日本、美国、英国等国的教育系统，必须记录该国的学年起止月份、各阶段学制（本科几年、硕士几年），作为生成时的硬约束
11. **锁定场次与集头标准格式模板**（v4.1.0新增）：在拆解阶段就把"每场四字段（大纲锚点/时间/地点/出场人物）"和"每集三字段（集标题/本集概要（按作者更正口径）/本集场次）"写成模板，后续每批照模板填充，不得自由发挥字段名
12. **建立全局人物出生日期精确表**（v4.2.0新增）：记录每个人物的精确出生日期（年-月-日），而不仅仅是出生年份。后续所有年龄计算都基于精确出生日期，未到生日不增岁
13. **建立全局关键事件日期表**（v4.2.0新增）：记录所有关键事件的精确日期（如父母去世、逃亡、回国、自首等），用于校验正文中"X岁时发生了某事"的相对时间表述是否正确
14. **建立全局人物关系与年龄对比表**（v4.2.0新增）：记录人物之间的年龄差（如"A比B大X个月"），用于校验正文中的年龄对比表述是否正确、是否写反
15. **建立全局同学年级一致性表**（v4.2.0新增）：记录主角的同班同学名单及其年级，默认所有同班同学同年级；如有跳级/留级/提前毕业，必须在表中注明并在剧情中有明确说明
16. **建立全局情节去重表**（v4.3.0新增）：列出所有关键情节节点及其对应的场次编号，确保每个节点只写1场；同时列出"模板化情节"（如帮老人做小事、板车运输、NAS检查、宣判等），明确标注哪些情节只写1次、哪些可以展开但必须有新信息
17. **建立同集情节多样性检查**（v4.3.0新增）：每集的场次必须包含不同类型的情节（冲突/转折/人物揭示/动作戏/情感戏/动作戏），不能全是同一结构的流水账；在拆解阶段就规划好每集的情节类型分布
18. **建立人物去向时间统一表**（v4.4.0新增）：记录每个主要人物的离开/到达时间（航班/车次/出发地/目的地），确保所有提到该人物去向的场次都指向同一个时间点；如有变动必须有明确情节说明
19. **建立送别/告别情节去重表**（v4.4.0新增）：记录每个主要人物的送别/告别情节只写1场，补充场不得重复送别动作；补充场只能写送别后的其他人物视角或新信息
20. **建立跨年事件年份对照表**（v4.4.0新增）：记录所有跨年事件（年度赛事、跨年晚会、年度颁奖等）的实际年份，确保引用时年份正确

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
9. **人物名字一致性**（v3.0.0新增）：每批生成的人物名字必须与全局人物表一致，不得擅自更改人物名字，不同人物不得使用相同名字。
10. **剧情一致性**（v3.0.0新增）：每批生成的情节必须与全局剧情一致性检查表一致，关键情节节点不得前后矛盾，"第一次"类情节必须明确区分场景。
11. **星期几正确性**（v3.0.0新增）：每批生成的星期几必须与日期对应，必须使用工具计算正确的星期几，不得凭印象填写。
12. **补充场内容独特性**（v3.0.0新增）：补充场次必须提供与主场次不同的内容、视角或情节，不得简单重复主场次的内容。
13. **集数标注完整性**（v4.0.0新增）：每集开始的第一场之前必须有集数标题（格式："第X集：标题"或"第X季 第X集：标题"）和集时间线（格式："【第X集时间线】开始时间 — 结束时间"）。跨文档续写时，集数编号必须与前文衔接，不得断裂或重复。
14. **外国学制正确性**（v4.0.0新增）：涉及日本学校时，学年从4月开始、翌年3月结束，3月仍是当前学年（如3月说"大一即将结束"而非"大二"），4月才升新学年；本科4年、修士（硕士）2年；提前毕业/跳级必须有明确情节说明。涉及其他国家时同理，必须按该国实际学制书写。
15. **年龄-年级对应正确性**（v4.0.0新增）：每个人物的年龄必须根据其出生日期和场景日期计算，未到生日不增岁；年级必须根据入学年份和场景日期推算，与全局年龄-年级对应表一致。
16. **场次四字段完整性**（v4.1.0新增）：每场开头必须依次出现"大纲锚点（作者口径）：…""时间：YYYY年M月D日 HH:MM""地点：…""出场人物：…"（"出场人物："可写作"人物："）。缺任一字段即为不合格，不得只写正文。
17. **集头三字段完整性**（v4.1.0新增）：每集集头必须有集标题（推荐格式"第二季·第X集《集名》"，兼容旧格式"第二季 第X集：标题"）、"本集概要（按作者更正口径）：…"、"本集场次：第X场—第Y场"。跨文档续写集次标注"第X集（续）"。
18. **日本9月表述正确性**（v4.1.0新增）：日本校园剧情在9月时，只能写"暑假结束""回到学校""前期最后一周""後期即将开始"，禁止写"新学期""新学年开学""九月开学"——日本新学年是4月。
19. **人物年龄精确到生日**（v4.2.0新增）：每个人物的年龄必须根据精确出生日期（年-月-日）和场景日期计算，未到生日不增岁。例如主角2016年4月8日生，2034年3月的场景仍是17岁，2034年4月8日之后才是18岁。
20. **相对时间表述必须与实际时间线一致**（v4.2.0新增）：正文中所有"X年前/后""X岁时离开/回来/失去亲人/发生某事"等相对时间表述，必须与全局关键事件日期表和人物出生日期核对一致。例如主角2026年7月（10岁）逃亡，2033年11月回国，应写"十岁走，十七岁回来"，不能写"七岁走"。
21. **人物年龄对比必须正确**（v4.2.0新增）：正文中"A比B大/小X个月/岁"的表述，必须与全局人物关系与年龄对比表核对，不得写反。例如A（4月生）比B（8月生）大4个月，不能写"A比B小两个月"。
22. **同班同学年级一致性**（v4.2.0新增）：主角的同班同学默认都是同年级的；如有人跳级/留级/提前毕业，必须在剧情中有明确说明，且在全局同学年级一致性表中注明。
23. **禁止模板化重复场次**（v4.3.0新增）：同一类情节（如"帮老人做小事""板车运输""NAS检查"等）不得拆成多场换汤不换药的模板。同一模板最多出现1-2场，且第2场必须有新的人物故事、新的转折或新的信息增量，不能只换具体事项。
24. **同一情节线只写一次**（v4.3.0新增）：每个关键情节节点（如板车上路、NAS入库、宣判、导弹发射、安全门被撬、飞机接地等）只写1场。如需多角度呈现，用补充场但必须提供新信息（不同人物视角/新发现/情节转折），不能重复同一动作。
25. **禁止"万能帮助"桥段滥用**（v4.3.0新增）：主角帮助他人的情节必须合并为少数几场有具体人物故事的戏，不能拆成N场"老人有困难→主角帮忙→老人感谢"的同一结构。
26. **同集情节多样性**（v4.3.0新增）：同一集内必须包含不同类型的情节（冲突/转折/人物揭示/动作戏/情感戏），不能全是同一结构的流水账。
27. **同一人物送别只写一次**（v4.4.0新增）：同一人物的送别/告别情节只写1场。补充场不得重复送别动作（机场告别/拥抱/流泪），只能写送别后的其他人物视角或新信息。
28. **补充场人物状态必须与主场次一致**（v4.4.0新增）：如果主场次说某人物已离开/已到达，补充场不能再写送别/出发/到达的情节。补充场时间必须在主场次之前或之后，不能出现"先说走了，后说才送"的矛盾。
29. **跨年事件年份引用必须正确**（v4.4.0新增）：引用跨年事件（年度赛事、跨年晚会、年度颁奖等）时，年份必须与时间线一致，不得把2033年的赛事写成2034年或反之。
30. **同一人物离开时间必须统一**（v4.4.0新增）：同一人物的离开时间（航班/车次时间）在所有场次中必须一致；如有变动，必须有明确的情节说明（如"航班取消改签到明天"）。

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
- [ ] **人物名字冲突检查**（v3.0.0新增）：本场人物名字是否与全局人物表一致，有没有不同人物使用相同名字
- [ ] **剧情一致性检查**（v3.0.0新增）：本场情节是否与全局剧情一致性检查表一致，有没有前后矛盾
- [ ] **星期几检查**（v3.0.0新增）：本场的星期几是否与日期对应正确
- [ ] **补充场内容独特性检查**（v3.0.0新增）：补充场次内容是否与主场次不同，有没有简单重复
- [ ] **集数标注检查**（v4.0.0新增）：本批涉及的集是否有集数标题和时间线，集数编号是否与全局集数编号表一致
- [ ] **外国学制检查**（v4.0.0新增）：涉及日本等外国学校时，学年起止、年级升降、学制年限是否正确；3月是否误写为"新学期/升年级"
- [ ] **年龄-年级对应检查**（v4.0.0新增）：本场人物年龄是否与出生日期和场景日期匹配，年级是否与入学年份匹配
- [ ] **场次四字段检查**（v4.1.0新增）：本场是否含"大纲锚点（作者口径）""时间：""地点：""出场人物：/人物："四字段，字段名是否照抄
- [ ] **集头三字段检查**（v4.1.0新增）：本批涉及的集是否含集标题、"本集概要（按作者更正口径）"、"本集场次"
- [ ] **日本9月表述检查**（v4.1.0新增）：9月日本校园场景是否误写"新学期/新学年开学"，应为"暑假结束/前期末/後期即将开始"
- [ ] **人物年龄精确到生日检查**（v4.2.0新增）：本场人物年龄是否根据精确出生日期和场景日期计算，未到生日是否误增岁
- [ ] **相对时间表述检查**（v4.2.0新增）：本场"X年前/后""X岁时发生某事"等相对时间表述是否与全局关键事件日期表一致
- [ ] **人物年龄对比检查**（v4.2.0新增）：本场"A比B大/小X个月/岁"是否与出生日期一致，有没有写反
- [ ] **同班同学年级一致性检查**（v4.2.0新增）：本场出现的主角同班同学年级是否一致，跳级/留级是否有明确说明
- [ ] **模板化重复场次检查**（v4.3.0新增）：本批是否与前面场次使用了相同的情节模板（如"帮老人做XX"连续多场），是否只换了具体事项
- [ ] **同一情节线重复检查**（v4.3.0新增）：本批是否重复写了已经写过的关键情节节点（板车上路、NAS入库、宣判等）
- [ ] **"万能帮助"桥段检查**（v4.3.0新增）：本批是否又是"某人有困难→主角帮忙→对方感谢"的同一结构
- [ ] **同集情节多样性检查**（v4.3.0新增）：本集已写场次是否类型单一，是否需要增加冲突/转折/动作戏等不同类型
- [ ] **同一人物送别重复检查**（v4.4.0新增）：本批是否又写了同一人物的送别/告别情节，前面是否已经写过
- [ ] **补充场人物状态一致性检查**（v4.4.0新增）：补充场的人物状态是否与主场次一致，有没有"主场次说走了，补充场又写送别"的矛盾
- [ ] **跨年事件年份检查**（v4.4.0新增）：引用跨年事件的年份是否与时间线一致
- [ ] **同一人物离开时间一致性检查**（v4.4.0新增）：同一人物的离开时间在所有场次中是否统一，有没有前后矛盾

**如果任何一项不通过，必须重写该批，不能带着问题继续。**

### 第四步：合并与最终验证

所有批次完成后：

1. **使用标准合并脚本合并所有批次**（必须按场次编号排序，不能按文件名排序）
2. **全量退化模式扫描**（用脚本检测，见下方）
3. **场次顺序验证**（所有主场次按编号递增，补充场次在对应主场次下方）
4. **字数验证**（中文字符数必须达到目标）
5. **时间线全量检查**（所有场次的时间戳严格单调递增）
6. **剧情逻辑全量检查**（v3.0.0新增，用脚本检测，见下方）
7. **集数标注全量检查**（v4.0.0新增，用脚本检测，见下方）：所有集是否有标题和时间线，集数编号是否连续，跨文档是否衔接
8. **外国学制与年龄-年级全量检查**（v4.0.0新增，用脚本检测，见下方）：日本学年4月起止、年级升降、学制年限、人物年龄与出生日期匹配
9. **场次/集头格式全量检查**（v4.1.0新增，用脚本检测，见下方）：每场四字段齐全、每集三字段齐全、日本9月无"新学期"误写、补充场紧跟主场次且序号连续
10. **通读流畅度检查**（至少通读全文一遍，标记不通顺的地方并修改）

## 标准合并脚本（剧本专用，必须使用）

**绝对禁止使用简单的文件名字典序排序合并！** 必须使用以下脚本，按场次编号排序，补充场次放在对应主场次下方：

```python
import re
import os

def merge_scenes(files_dir, output_path, file_prefixes=['act_part', 'act_supplement']):
    """
    标准剧本合并脚本
    按场次编号排序，补充场次放在对应主场次下方
    """
    all_files = []
    
    for filename in os.listdir(files_dir):
        for prefix in file_prefixes:
            if filename.startswith(prefix) and filename.endswith('.txt'):
                filepath = os.path.join(files_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                all_files.append((filename, content))
                break
    
    print(f"读取了 {len(all_files)} 个文件")
    
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
            
            main_scene_match = re.match(r'^第(\d+)场$', stripped)
            supplement_match = re.match(r'^第(\d+)场补充场（([一二三四五六七八九十]+)）', stripped)
            
            if main_scene_match and not supplement_match:
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
                cn_num = supplement_match.group(2)
                cn_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
                          '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
                current_supplement_number = cn_map.get(cn_num, 0)
                current_scene_lines = [line]
            
            else:
                current_scene_lines.append(line)
        
        if current_scene_title:
            all_scenes.append({
                'title': current_scene_title,
                'number': current_scene_number,
                'is_supplement': current_is_supplement,
                'supplement_order': current_supplement_number,
                'content': '\n'.join(current_scene_lines)
            })
    
    print(f"解析出 {len(all_scenes)} 个场次")
    
    def sort_key(scene):
        if scene['is_supplement']:
            return (scene['number'], 1, scene['supplement_order'])
        else:
            return (scene['number'], 0, 0)
    
    all_scenes.sort(key=sort_key)
    
    print("\n排序后的场次顺序：")
    for i, scene in enumerate(all_scenes):
        print(f"  {i+1:3d}. {scene['title']}")
    
    merged_content = ""
    for scene in all_scenes:
        merged_content += scene['content']
        merged_content += "\n\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(merged_content)
    
    print(f"\n合并后的文本已保存到: {output_path}")
    
    return merged_content
```

## 退化模式自动检测脚本

生成完成后，必须运行以下Python脚本进行自动检测：

```python
import re

def detect_degradation(text):
    """检测长文本退化模式，返回问题列表"""
    issues = []
    
    pattern1 = re.compile(r'[\u4e00-\u9fff]{1,4}，[\u4e00-\u9fff]{1,2}[。，！？]')
    matches1 = pattern1.findall(text)
    if matches1:
        issues.append(f"发现{len(matches1)}处'主语，动词'碎片化断句，示例：{matches1[:5]}")
    
    lines = text.split('\n')
    fragment_lines = []
    for i, line in enumerate(lines):
        if line.count('，') >= 4 and len(line) < 50:
            fragment_lines.append((i+1, line.strip()))
    if fragment_lines:
        issues.append(f"发现{len(fragment_lines)}处碎片句（逗号过多且句子过短），示例：{fragment_lines[:3]}")
    
    pattern3 = re.compile(r'[""][\u4e00-\u9fff]{1,4}，[说道问回答喊叫][：，]')
    matches3 = pattern3.findall(text)
    if matches3:
        issues.append(f"发现{len(matches3)}处对话标签逗号错误，示例：{matches3[:5]}")
    
    sentences = re.split(r'[。！？]', text)
    repeated_starts = []
    for i in range(len(sentences)-5):
        starts = [s.strip()[:3] for s in sentences[i:i+6] if s.strip()]
        if len(set(starts)) <= 2 and len(starts) >= 5:
            repeated_starts.append((i, starts))
    if repeated_starts:
        issues.append(f"发现{len(repeated_starts)}处连续相同句式开头，示例位置：{repeated_starts[:3]}")
    
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
    """验证场次顺序和时间线，返回问题列表"""
    issues = []
    
    lines = text.split('\n')
    scenes = []
    current_scene = None
    current_time = None
    
    for line in lines:
        stripped = line.strip()
        
        main_scene_match = re.match(r'^第(\d+)场$', stripped)
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
        
        time_match = re.match(r'^时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2})[：:](\d{2})', stripped)
        if time_match:
            year, month, day, hour, minute = map(int, time_match.groups())
            current_time = (year, month, day, hour, minute)
    
    if current_scene:
        scenes.append((current_scene, current_time))
    
    main_scene_numbers = []
    for i, (scene, time) in enumerate(scenes):
        if '补充场' not in scene:
            match = re.match(r'^第(\d+)场', scene)
            if match:
                num = int(match.group(1))
                if main_scene_numbers and num <= main_scene_numbers[-1]:
                    issues.append(f"主场次编号倒流：第{num}场在第{main_scene_numbers[-1]}场之后")
                main_scene_numbers.append(num)
    
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
    
    timestamps = [time for scene, time in scenes if time]
    for i in range(1, len(timestamps)):
        if timestamps[i] <= timestamps[i-1]:
            issues.append(f"时间线倒流：第{i+1}个时间戳{timestamps[i]}不大于前一个{timestamps[i-1]}")
    
    return issues
```

## 剧情逻辑连贯性检测脚本（剧本专用，v3.0.0新增，必须运行）

```python
import re
import datetime
from difflib import SequenceMatcher

def verify_plot_logic(text):
    """
    验证剧情逻辑连贯性，返回问题列表
    检测内容：人物名字冲突、星期几错误、主场次与补充场内容重复、相邻场次情节相似度
    """
    issues = []
    
    lines = text.split('\n')
    
    # ============================================
    # 1. 解析所有场次
    # ============================================
    scenes = []
    current_scene_title = None
    current_scene_content = []
    current_scene_time = None
    current_is_supplement = False
    
    for line in lines:
        stripped = line.strip()
        
        main_scene_match = re.match(r'^第(\d+)场$', stripped)
        supplement_match = re.match(r'^第(\d+)场补充场（([一二三四五六七八九十]+)）', stripped)
        
        if main_scene_match and not supplement_match:
            if current_scene_title:
                scenes.append({
                    'title': current_scene_title,
                    'content': '\n'.join(current_scene_content),
                    'time': current_scene_time,
                    'is_supplement': current_is_supplement
                })
            current_scene_title = stripped
            current_scene_content = [line]
            current_scene_time = None
            current_is_supplement = False
        elif supplement_match:
            if current_scene_title:
                scenes.append({
                    'title': current_scene_title,
                    'content': '\n'.join(current_scene_content),
                    'time': current_scene_time,
                    'is_supplement': current_is_supplement
                })
            current_scene_title = stripped
            current_scene_content = [line]
            current_scene_time = None
            current_is_supplement = True
        else:
            current_scene_content.append(line)
            time_match = re.match(r'^时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2})[：:](\d{2})', stripped)
            if time_match:
                year, month, day, hour, minute = map(int, time_match.groups())
                current_scene_time = (year, month, day, hour, minute)
    
    if current_scene_title:
        scenes.append({
            'title': current_scene_title,
            'content': '\n'.join(current_scene_content),
            'time': current_scene_time,
            'is_supplement': current_is_supplement
        })
    
    # ============================================
    # 2. 星期几自动校验
    # ============================================
    weekday_map = {
        0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四',
        4: '星期五', 5: '星期六', 6: '星期日'
    }
    
    cn_num_map = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
        '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
        '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
        '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
        '三十一': 31
    }
    
    pattern = re.compile(r'([一二三四五六七八九十]+)月([一二三四五六七八九十]+)日[，,\s]+(星期[一二三四五六日天])')
    matches = pattern.findall(text)
    
    weekday_errors = []
    for match in matches:
        month_cn, day_cn, old_weekday = match
        month = cn_num_map.get(month_cn, 0)
        day = cn_num_map.get(day_cn, 0)
        
        if month == 0 or day == 0:
            continue
        
        try:
            date = datetime.date(2027, month, day)
            correct_weekday = weekday_map[date.weekday()]
            
            if old_weekday != correct_weekday:
                weekday_errors.append(f"{month_cn}月{day_cn}日 {old_weekday} (正确: {correct_weekday})")
        except ValueError:
            pass
    
    if weekday_errors:
        issues.append(f"发现 {len(weekday_errors)} 处星期几错误：")
        for error in weekday_errors:
            issues.append(f"  ✗ {error}")
    else:
        issues.append("✓ 所有星期几都正确")
    
    # ============================================
    # 3. 主场次与补充场内容重复检测
    # ============================================
    supplement_duplicate_issues = []
    
    for i, scene in enumerate(scenes):
        if scene['is_supplement']:
            # 找到对应的主场次
            supplement_num_match = re.match(r'^第(\d+)场补充场', scene['title'])
            if supplement_num_match:
                supplement_num = int(supplement_num_match.group(1))
                # 找到对应的主场次
                for j, main_scene in enumerate(scenes):
                    if not main_scene['is_supplement']:
                        main_num_match = re.match(r'^第(\d+)场', main_scene['title'])
                        if main_num_match and int(main_num_match.group(1)) == supplement_num:
                            # 计算相似度
                            similarity = SequenceMatcher(None, main_scene['content'], scene['content']).ratio()
                            if similarity > 0.6:
                                supplement_duplicate_issues.append(
                                    f"{main_scene['title']} 与 {scene['title']} 内容相似度高达 {similarity:.2%}，可能存在严重重复"
                                )
                            break
    
    if supplement_duplicate_issues:
        issues.append(f"发现 {len(supplement_duplicate_issues)} 处主场次与补充场内容重复：")
        for issue in supplement_duplicate_issues:
            issues.append(f"  ✗ {issue}")
    else:
        issues.append("✓ 未发现主场次与补充场内容严重重复")
    
    # ============================================
    # 4. 相邻场次情节相似度检测
    # ============================================
    adjacent_similarity_issues = []
    
    for i in range(len(scenes) - 1):
        if not scenes[i]['is_supplement'] and not scenes[i+1]['is_supplement']:
            # 只检查相邻的两个主场次
            similarity = SequenceMatcher(None, scenes[i]['content'], scenes[i+1]['content']).ratio()
            if similarity > 0.4:
                adjacent_similarity_issues.append(
                    f"{scenes[i]['title']} 与 {scenes[i+1]['title']} 内容相似度高达 {similarity:.2%}，可能存在情节重复"
                )
    
    if adjacent_similarity_issues:
        issues.append(f"发现 {len(adjacent_similarity_issues)} 处相邻场次情节相似度太高：")
        for issue in adjacent_similarity_issues:
            issues.append(f"  ✗ {issue}")
    else:
        issues.append("✓ 未发现相邻场次情节严重重复")
    
    # ============================================
    # 5. 人物名字冲突检测（简单检测）
    # ============================================
    # 提取所有"XX说"的人物名字
    name_pattern = re.compile(r'([\u4e00-\u9fff]{2,4})说[：:]')
    all_names = name_pattern.findall(text)
    
    # 统计每个名字出现的场次
    name_scenes = {}
    for name in set(all_names):
        name_scenes[name] = set()
        for i, scene in enumerate(scenes):
            if name in scene['content']:
                name_scenes[name].add(i)
    
    # 检测是否有名字在不同的上下文中被用作不同的人物
    # 这是一个简单的启发式检测，可能会有误报
    name_conflict_issues = []
    
    # 检测常见的姓氏+名字组合是否在不同场次中被赋予不同的身份
    # 这里只做简单的提示，需要人工确认
    common_names = ['王建国', '李建国', '张建国', '刘建国', '陈建国']
    for name in common_names:
        if name in text:
            # 检查这个名字出现的场次
            name_scene_indices = [i for i, scene in enumerate(scenes) if name in scene['content']]
            if len(name_scene_indices) > 1:
                # 检查这些场次中这个名字的身份描述
                identity_descriptions = []
                for idx in name_scene_indices:
                    scene = scenes[idx]
                    # 查找名字附近的身份描述
                    name_pos = scene['content'].find(name)
                    if name_pos != -1:
                        context = scene['content'][max(0, name_pos-50):name_pos+50]
                        identity_descriptions.append(context)
                
                # 简单检查身份描述是否有明显差异
                if len(set(identity_descriptions)) > 1:
                    name_conflict_issues.append(
                        f"名字 '{name}' 在多个场次中出现，且身份描述可能存在差异，请人工确认是否为同一人物"
                    )
    
    if name_conflict_issues:
        issues.append(f"发现 {len(name_conflict_issues)} 处可能的人物名字冲突：")
        for issue in name_conflict_issues:
            issues.append(f"  ⚠ {issue}")
    else:
        issues.append("✓ 未发现明显的人物名字冲突")
    
    return issues
```

## 集数标注与学制检测脚本（剧本专用，v4.0.0新增，必须运行）

```python
import re
import datetime

def verify_episodes_and_academic_system(text, character_birth_dates=None, japan_univ_scenes=None):
    """
    集数标注完整性检测 + 日本学制检测 + 年龄-年级对应检测
    返回问题列表。

    参数:
    - text: 剧本文本
    - character_birth_dates: dict, 如 {'徐萱': (2016, 5), '苏晚': (2016, 5)}
    - japan_univ_scenes: list of scene numbers that involve Japanese universities,
      如 [146, 149, 153, 188, 189, 192, 193, 212, 214, 219, 220, 221, 222]
    """
    issues = []
    if character_birth_dates is None:
        character_birth_dates = {}
    if japan_univ_scenes is None:
        japan_univ_scenes = []

    lines = text.split('\n')

    # ============================================
    # 1. 集数标注检测
    # ============================================
    episode_pattern = re.compile(r'^第[一二三四五六七八九十\d]+集[：:]?\s*(.*)')
    episodes = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        m = episode_pattern.match(stripped)
        if m and '补充场' not in stripped and '场' not in stripped[:6]:
            episodes.append((i+1, stripped))

    if not episodes:
        issues.append("✗ 未发现任何集数标注（'第X集'），多幕剧本必须标注每集的标题和时间线")
    else:
        issues.append(f"✓ 发现 {len(episodes)} 个集数标注")
        # 检查集数编号连续性
        episode_numbers = []
        for line_no, ep_text in episodes:
            num_match = re.match(r'^第([一二三四五六七八九十\d]+)集', ep_text)
            if num_match:
                num_str = num_match.group(1)
                if num_str.isdigit():
                    episode_numbers.append(int(num_str))
                else:
                    cn_map = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
                    episode_numbers.append(cn_map.get(num_str, 0))
        for i in range(1, len(episode_numbers)):
            if episode_numbers[i] != episode_numbers[i-1] + 1 and episode_numbers[i] != episode_numbers[i-1]:
                issues.append(f"  ✗ 集数编号不连续：第{episode_numbers[i-1]}集之后直接跳到第{episode_numbers[i]}集")
        # 检查是否有集时间线
        for line_no, ep_text in episodes:
            has_timeline = False
            for j in range(line_no, min(line_no+3, len(lines))):
                if '时间线' in lines[j] if j < len(lines) else False:
                    has_timeline = True
                    break
            if not has_timeline:
                issues.append(f"  ⚠ 第{line_no}行的集数标注'{ep_text}'缺少集时间线说明")

    # ============================================
    # 2. 解析所有场次及时间戳
    # ============================================
    scenes = []
    current_scene = None
    current_time = None
    current_content = []

    for line in lines:
        stripped = line.strip()
        main_match = re.match(r'^第(\d+)场', stripped)
        supp_match = re.match(r'^第(\d+)场补充场', stripped)
        if main_match and not supp_match:
            if current_scene:
                scenes.append({'num': current_scene, 'time': current_time, 'content': '\n'.join(current_content)})
            current_scene = int(main_match.group(1))
            current_time = None
            current_content = [line]
        else:
            if current_scene:
                current_content.append(line)
            tm = re.match(r'^时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2})[：:](\d{2})', stripped)
            if tm:
                current_time = tuple(map(int, tm.groups()))
    if current_scene:
        scenes.append({'num': current_scene, 'time': current_time, 'content': '\n'.join(current_content)})

    # ============================================
    # 3. 日本学制检测
    # ============================================
    japan_issues = []
    for scene in scenes:
        if not scene['time']:
            continue
        year, month, day, hour, minute = scene['time']
        content = scene['content']
        scene_num = scene['num']

        # 检测3月是否误写为"新学期开始"/"开学"（日本学年4月开始）
        if month == 3:
            if re.search(r'新学期开始', content) or re.search(r'开学', content):
                # 排除"即将开学"/"下学期"等正确表述
                if not re.search(r'即将|下学期|四月|下个月', content):
                    japan_issues.append(f"第{scene_num}场({year}年{month}月): 日本3月是学年末尾，不应写'新学期开始'或'开学'，应写'学年即将结束'")

        # 检测"你才大二"等年级表述是否与入学年份匹配
        # 需要知道入学年份，这里做通用检测：3月说"大二"应提示检查
        if month == 3 and japan_univ_scenes and scene_num in japan_univ_scenes:
            grade_matches = re.findall(r'你才(大[一二三四])', content)
            for grade in grade_matches:
                japan_issues.append(f"第{scene_num}场({year}年{month}月): 3月仍属当前学年，'{grade}'可能有误，请核对入学年份（4月才升新学年）")

        # 检测"三年硕士"（日本修士为2年）
        if re.search(r'三年硕士|硕士.*三年', content):
            japan_issues.append(f"第{scene_num}场: 日本修士（硕士）学制为2年，不应写'三年硕士'")

        # 检测"大四开学"在9月（日本大四学年从4月开始）
        if month == 9 and re.search(r'大四开学', content):
            japan_issues.append(f"第{scene_num}场({year}年9月): 日本学年4月开始，9月是大四的后半学期（後期），不应写'大四开学'")

    if japan_issues:
        issues.append(f"发现 {len(japan_issues)} 处日本学制问题：")
        for iss in japan_issues:
            issues.append(f"  ✗ {iss}")
    else:
        issues.append("✓ 未发现明显的日本学制问题")

    # ============================================
    # 4. 年龄-年级对应检测
    # ============================================
    age_issues = []
    for scene in scenes:
        if not scene['time'] or not character_birth_dates:
            continue
        year, month, day, _, _ = scene['time']
        content = scene['content']
        scene_num = scene['num']

        for char_name, (birth_year, birth_month) in character_birth_dates.items():
            # 计算该场景时人物的实际年龄
            age = year - birth_year
            if month < birth_month:
                age -= 1
            # 检测文本中声明的年龄
            age_patterns = [
                (rf'{char_name}[^。]{{0,30}}?(\d+)岁', f'{char_name}的年龄表述'),
                (rf'(\d+)岁[^。]{{0,30}}?{char_name}', f'{char_name}的年龄表述'),
                (rf'他今年(\d+)岁', '主角年龄表述'),
                (rf'她今年(\d+)岁', '女主角年龄表述'),
                (rf'那个(\d+)岁的', '年龄表述'),
            ]
            for pattern, desc in age_patterns:
                matches = re.findall(pattern, content)
                for stated_age_str in matches:
                    stated_age = int(stated_age_str)
                    if abs(stated_age - age) > 1:
                        age_issues.append(
                            f"第{scene_num}场({year}年{month}月): {desc}写'{stated_age}岁'，"
                            f"但{char_name}生于{birth_year}年{birth_month}月，此时实际{age}岁"
                        )

    if age_issues:
        issues.append(f"发现 {len(age_issues)} 处年龄-时间线不匹配：")
        for iss in age_issues:
            issues.append(f"  ✗ {iss}")
    else:
        if character_birth_dates:
            issues.append("✓ 未发现明显的年龄-时间线不匹配")
        else:
            issues.append("⚠ 未提供人物出生日期，跳过年龄检测")

    return issues
```

## 场次与集头格式完整性检测脚本（剧本专用，v4.1.0新增，必须运行）

```python
import re

def verify_format_and_supplement(text):
    """
    场次四字段 + 集头三字段 + 日本9月"新学期"误写 + 补充场位置增强检测
    返回问题列表。
    场次四字段：大纲锚点（作者口径）/ 时间：/ 地点：/ 出场人物：（兼容"人物："）
    集头三字段：集标题 / 本集概要（按作者更正口径）/ 本集场次
    """
    issues = []
    lines = text.split('\n')

    # ============================================
    # 1. 解析所有场次块（含时间戳）
    # ============================================
    scenes = []
    cur_title = None
    cur_content = []
    cur_time = None
    cur_is_supp = False
    cur_supp_ord = 0
    cn_supp = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}

    for line in lines:
        s = line.strip()
        m_main = re.match(r'^第(\d+)场$', s)
        m_supp = re.match(r'^第(\d+)场补充场（([一二三四五六七八九十]+)）', s)
        if m_main and not m_supp:
            if cur_title:
                scenes.append({'title':cur_title,'content':'\n'.join(cur_content),
                               'time':cur_time,'is_supp':cur_is_supp,'supp_ord':cur_supp_ord})
            cur_title = s; cur_content=[line]; cur_time=None; cur_is_supp=False; cur_supp_ord=0
        elif m_supp:
            if cur_title:
                scenes.append({'title':cur_title,'content':'\n'.join(cur_content),
                               'time':cur_time,'is_supp':cur_is_supp,'supp_ord':cur_supp_ord})
            cur_title = s; cur_content=[line]; cur_time=None; cur_is_supp=True
            cur_supp_ord = cn_supp.get(m_supp.group(2), 0)
        else:
            if cur_title:
                cur_content.append(line)
            tm = re.match(r'^时间[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2})[：:](\d{2})', s)
            if tm and cur_title:
                cur_time = tuple(map(int, tm.groups()))
    if cur_title:
        scenes.append({'title':cur_title,'content':'\n'.join(cur_content),
                       'time':cur_time,'is_supp':cur_is_supp,'supp_ord':cur_supp_ord})

    # ============================================
    # 2. 场次四字段完整性检测
    # ============================================
    field_issues = []
    for sc in scenes:
        c = sc['content']
        missing = []
        if not re.search(r'时间[：:]', c):
            missing.append('时间：')
        if not re.search(r'地点[：:]', c):
            missing.append('地点：')
        if not re.search(r'(出场人物|人物)[：:]', c):
            missing.append('出场人物：/人物：')
        # 大纲锚点为v4.1.0新立强制字段；旧稿缺则给警告，新稿缺则给错误
        if '大纲锚点' not in c:
            missing.append('大纲锚点（作者口径）')
        if missing:
            level = '✗' if any(m != '大纲锚点（作者口径）' for m in missing) else '⚠'
            field_issues.append(f"{level} {sc['title']} 缺字段：{'、'.join(missing)}")
    if field_issues:
        issues.append(f"场次字段问题 {len(field_issues)} 处：")
        issues.extend('  ' + x for x in field_issues)
    else:
        issues.append("✓ 所有场次四字段齐全")

    # ============================================
    # 3. 集头三字段完整性检测
    # ============================================
    # 找所有集标题行
    ep_idx = []
    for i, line in enumerate(lines):
        s = line.strip()
        if re.match(r'^第[一二三四五六七八九十\d]+集', s) and '场' not in s[:6] \
           and not re.search(r'补充场|时间线|本集', s):
            ep_idx.append(i)
    ep_field_issues = []
    for k, i in enumerate(ep_idx):
        end = ep_idx[k+1] if k+1 < len(ep_idx) else len(lines)
        # 集头块到第一个"第X场"为止
        block_end = end
        for j in range(i+1, end):
            if re.match(r'^第\d+场', lines[j].strip()):
                block_end = j
                break
        block = '\n'.join(lines[i:block_end])
        miss = []
        if not re.search(r'本集概要', block):
            miss.append('本集概要（按作者更正口径）')
        if not re.search(r'本集场次', block):
            miss.append('本集场次')
        if miss:
            ep_field_issues.append(f"✗ 第{i+1}行集头'{lines[i].strip()}' 缺：{'、'.join(miss)}")
    if ep_field_issues:
        issues.append(f"集头字段问题 {len(ep_field_issues)} 处：")
        issues.extend('  ' + x for x in ep_field_issues)
    else:
        issues.append("✓ 所有集头三字段齐全")

    # ============================================
    # 4. 日本9月"新学期/新学年开学"误写检测
    # ============================================
    japan_sep_issues = []
    for sc in scenes:
        if not sc['time']:
            continue
        year, month, day, _, _ = sc['time']
        if month != 9:
            continue
        c = sc['content']
        # 命中"新学期/新学年/开学"类词，但排除"暑假结束/前期末/後期即将开始"等正确表述
        if re.search(r'新学期|新学年|开学|九月开学|新学期伊始', c):
            # 已含正确语境则降级为提示
            soft = re.search(r'暑假结束|暑假后|前期.*(结束|最后)|後期即将|回到学校', c)
            mark = '⚠' if soft else '✗'
            japan_sep_issues.append(
                f"{mark} {sc['title']}({year}年9月): 9月是日本前期末/暑假结束，"
                f"不是新学年开始；应写'暑假结束''前期最后阶段''後期即将开始'，"
                f"勿写'新学期/新学年/开学'（新学年在4月）"
            )
    if japan_sep_issues:
        issues.append(f"日本9月表述问题 {len(japan_sep_issues)} 处：")
        issues.extend('  ' + x for x in japan_sep_issues)
    else:
        issues.append("✓ 未发现日本9月误写'新学期'")

    # ============================================
    # 5. 补充场位置增强检测（紧跟主场次 + 序号连续 + 时间夹在主场次之间）
    # ============================================
    supp_issues = []
    # 5a. 补充场紧跟同号主场次（复用顺序校验逻辑）
    last_main = None
    for sc in scenes:
        if sc['is_supp']:
            num = int(re.match(r'^第(\d+)场补充场', sc['title']).group(1))
            if last_main is None or num != last_main:
                supp_issues.append(f"✗ {sc['title']} 未紧跟对应主场次（上一个主场次是第{last_main}场）")
        else:
            last_main = int(re.match(r'^第(\d+)场', sc['title']).group(1))
    # 5b. 同一主场次下补充场序号(一)(二)...必须连续不重号
    main_to_supp = {}
    for sc in scenes:
        if sc['is_supp']:
            num = int(re.match(r'^第(\d+)场补充场', sc['title']).group(1))
            main_to_supp.setdefault(num, []).append(sc['supp_ord'])
    for num, ords in main_to_supp.items():
        if ords != sorted(ords):
            supp_issues.append(f"✗ 第{num}场的补充场序号顺序错乱：{ords}")
        if len(set(ords)) != len(ords):
            supp_issues.append(f"✗ 第{num}场的补充场序号重复：{ords}")
        expected = list(range(1, len(ords)+1))
        if sorted(ords) != expected:
            supp_issues.append(f"⚠ 第{num}场的补充场序号 {sorted(ords)} 与预期 {expected} 不完全连续，请确认是否漏号")
    # 5c. 补充场时间必须晚于其主场次、早于下一主场次
    main_time = {}
    main_order = []
    for sc in scenes:
        if not sc['is_supp'] and sc['time']:
            num = int(re.match(r'^第(\d+)场', sc['title']).group(1))
            main_time[num] = sc['time']; main_order.append(num)
    for sc in scenes:
        if not sc['is_supp'] or not sc['time']:
            continue
        num = int(re.match(r'^第(\d+)场补充场', sc['title']).group(1))
        if num in main_time and sc['time'] <= main_time[num]:
            supp_issues.append(f"✗ {sc['title']} 时间{sc['time']}不晚于其主场次第{num}场时间{main_time[num]}")
        # 找下一主场次
        next_mains = [n for n in main_order if n > num]
        if next_mains and num in main_time:
            nxt = min(next_mains)
            if nxt in main_time and sc['time'] >= main_time[nxt]:
                supp_issues.append(f"✗ {sc['title']} 时间{sc['time']}晚于下一主场次第{nxt}场时间{main_time[nxt]}")
    if supp_issues:
        issues.append(f"补充场位置问题 {len(supp_issues)} 处：")
        issues.extend('  ' + x for x in supp_issues)
    else:
        issues.append("✓ 所有补充场紧跟主场次，序号连续，时间区间正确")

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
- 每场必须包含四个必填字段（v4.1.0起强制执行）：
  ```
  第131场
  大纲锚点（作者口径）：此处用一句话写明本场在全剧大纲中的位置/作用
  时间：2027年10月22日 09:00
  地点：日本东京，新宿区，某著名语言学校，高级班教室
  出场人物：徐萱（田中萱）、小林美咲、山田太郎、同学若干
  ```
  - 字段名照抄，不得改写（如不得把"地点："写成"场景："，不得把"出场人物："写成"人物表："）
  - "出场人物："可写作"人物："，但全文应统一
  - 时间戳格式：`时间：YYYY年MM月DD日 HH:MM`（如"时间：2026年9月3日 08:00"）
- 补充场次必须紧跟在对应主场次的下方
- 补充场次时间戳必须在对应主场次之后、下一个主场次之前
- 补充场次必须提供与主场次不同的内容、视角或情节，不得简单重复主场次内容（v3.0.0新增）
- 同一主场次下有多个补充场时，按（一）（二）（三）顺序排列，不得跳号、重号（v4.1.0新增）

### 集数标注格式规范（v4.0.0新增，v4.1.0强化）

- 每集开始的第一场之前必须插入集头块
- 集头必须包含三个必填字段（v4.1.0起强制执行）：
  1. **集标题**：推荐格式 `第二季·第X集《集名》`（书名号包裹集名）；兼容旧格式 `第二季 第X集：标题`、`第X集（续）：标题`
  2. **本集概要（按作者更正口径）：…**——一句话到一段话概括本集主线，措辞必须与作者最终口径一致
  3. **本集场次：第X场—第Y场**——本集覆盖的主场次起止编号
- 集时间线格式：`【第X集时间线】YYYY年M月D日 HH:MM — YYYY年M月D日 HH:MM`
- 跨文档续写时，下集开头如承接上集的同一集，标注`第X集（续）：标题`
- 集数编号必须全局连续，不得跳号、重号
- 推荐格式示例：
  ```
  ═══════════════════════════════════════════
  第二季·第4集《联盟重启与扩张》
  【第4集时间线】2027年10月22日 09:00 — 2028年3月25日 10:00
  本集概要（按作者更正口径）：徐萱在日本稳住语言学校与技术室双线，联盟启动东南亚扩张。
  本集场次：第131场—第145场
  ═══════════════════════════════════════════
  ```

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

## 剧情逻辑验证方法（v3.0.0新增）

见上方"剧情逻辑连贯性检测脚本"。

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
11. ✅ 剧情逻辑连贯性检测通过（v3.0.0新增）：
    - 所有星期几都正确
    - 未发现主场次与补充场内容严重重复
    - 未发现相邻场次情节严重重复
    - 未发现明显的人物名字冲突
12. ✅ 全局人物表一致性检查通过（v3.0.0新增）：所有人物名字与全局人物表一致
13. ✅ 全局剧情一致性检查表检查通过（v3.0.0新增）：关键情节节点前后一致，无矛盾
14. ✅ 集数标注完整性检查通过（v4.0.0新增）：每集有标题和时间线，集数编号连续，跨文档衔接
15. ✅ 外国学制检查通过（v4.0.0新增）：日本学年4月起止、年级升降、学制年限正确；其他国家学制同理
16. ✅ 年龄-年级对应检查通过（v4.0.0新增）：人物年龄与出生日期和场景日期匹配，年级与入学年份匹配
17. ✅ 场次四字段完整性检查通过（v4.1.0新增）：每场均含"大纲锚点（作者口径）""时间：""地点：""出场人物：/人物："
18. ✅ 集头三字段完整性检查通过（v4.1.0新增）：每集均含集标题、"本集概要（按作者更正口径）"、"本集场次"
19. ✅ 日本9月表述检查通过（v4.1.0新增）：9月日本校园场景未误写"新学期/新学年开学"
20. ✅ 补充场位置增强检查通过（v4.1.0新增）：补充场紧跟同号主场次、序号(一)(二)连续不重号、时间夹在主场次与下一主场次之间
21. ✅ 人物年龄精确到生日检查通过（v4.2.0新增）：所有人物年龄根据精确出生日期和场景日期计算，未到生日不增岁，无"3月写18岁但4月才生日"类错误
22. ✅ 相对时间表述检查通过（v4.2.0新增）：所有"X年前/后""X岁时离开/回来/失去亲人"等相对时间表述与全局关键事件日期表一致，无"七岁走（实际十岁走）"类错误
23. ✅ 人物年龄对比检查通过（v4.2.0新增）：所有"A比B大/小X个月/岁"表述与出生日期一致，无写反
24. ✅ 同班同学年级一致性检查通过（v4.2.0新增）：主角同班同学年级一致，跳级/留级有明确情节说明
25. ✅ 模板化重复场次检查通过（v4.3.0新增）：无同一情节模板拆成多场换汤不换药的情况
26. ✅ 同一情节线重复检查通过（v4.3.0新增）：每个关键情节节点只写1场，无重复
27. ✅ "万能帮助"桥段检查通过（v4.3.0新增）：帮助他人情节合并为少数有具体故事的戏，无模板化流水账
28. ✅ 同集情节多样性检查通过（v4.3.0新增）：每集包含不同类型情节，不全是同一结构
29. ✅ 同一人物送别重复检查通过（v4.4.0新增）：同一人物的送别/告别情节只写1场，无重复
30. ✅ 补充场人物状态一致性检查通过（v4.4.0新增）：补充场人物状态与主场次一致，无"先说走了后说才送"的矛盾
31. ✅ 跨年事件年份检查通过（v4.4.0新增）：跨年事件引用年份正确，无跨年错误
32. ✅ 同一人物离开时间一致性检查通过（v4.4.0新增）：同一人物离开时间在所有场次中统一，无矛盾

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

### Q：如何避免人物名字冲突？（v3.0.0新增）
A：在任务拆解阶段，必须建立全局人物表，明确所有人物的姓名、身份、年龄、性格特征。每批生成时，必须与全局人物表核对，确保不同人物不使用相同名字，同一人物的名字不随意更改。

### Q：如何避免主场次与补充场内容重复？（v3.0.0新增）
A：补充场次必须提供与主场次不同的内容、视角或情节。可以从以下角度设计补充场：
1. 不同人物的视角（主场次写主角，补充场写配角）
2. 同一事件的不同阶段（主场次写事件开始，补充场写事件后续）
3. 平行发生的其他事件（主场次写主线，补充场写副线）
4. 事件的背景或前因（主场次写结果，补充场写原因）
5. 人物的内心活动或回忆（主场次写外部行动，补充场写内心世界）

### Q：如何避免星期几错误？（v3.0.0新增）
A：必须使用工具计算正确的星期几，不得凭印象填写。可以使用Python的datetime模块计算：
```python
import datetime
date = datetime.date(2027, 8, 5)
weekday = date.strftime('%A')  # 输出英文星期几
# 或者手动映射
weekday_map = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期日'}
correct_weekday = weekday_map[date.weekday()]
```

### Q：如何检测"第一次"类情节前后不一致？（v3.0.0新增）
A：在任务拆解阶段，必须建立全局剧情一致性检查表，记录所有关键情节节点（如"第一次开车"、"第一次见某人"、"第一次使用某设备"等）。每批生成时，必须与全局剧情一致性检查表核对，确保"第一次"类情节前后一致。如果需要在不同场景中使用"第一次"，必须明确区分场景（如"第一次在训练场试驾" vs "第一次在真实道路上驾驶"）。

### Q：如何避免集数标注丢失？（v4.0.0新增）
A：在任务拆解阶段必须建立全局集数编号表，明确每集的编号、标题、时间线范围和对应的场次区间。每批生成时，如果该批包含某集的第一场，必须在该场之前插入集数标题和时间线。合并后必须运行集数标注检测脚本，确认所有集都有标注、编号连续。跨文档（如上集/下集）时，集数编号必须衔接，下集开头应标注"第X集（续）"或从下一集开始。

### Q：日本大学学制有哪些容易出错的地方？（v4.0.0新增）
A：日本大学学制的核心规则：
1. 学年从4月1日开始，翌年3月31日结束——3月仍是当前学年，不是"新学期"
2. 4月才升新学年（如4月从大一升大二）
3. 本科（学部）4年，修士（硕士）2年，博士3年
4. 一年分前期（4-9月）和後期（10-翌年3月），後期通常10月开始
5. 毕业在3月，入学在4月
常见错误：3月写"大二"（实际仍是大一）、写"三年硕士"（应为2年）、9月写"大四开学"（实际大四学年4月已开始）。

### Q：如何确保人物年龄与时间线一致？（v4.0.0新增）
A：在任务拆解阶段建立全局人物年龄-年级对应表，记录每个人物的出生日期。每批生成时，根据场景日期计算人物实际年龄（未到生日不增岁），与文本中声明的年龄核对。例如主角2016年5月生，2029年3月的场景中他仍是12岁（5月才满13岁），2029年7月才是13岁。交付前必须运行年龄-年级对应检测脚本。

### Q：提前毕业/跳级需要注意什么？（v4.0.0新增）
A：如果设定人物提前毕业或跳级，必须：
1. 在剧情中有明确的说明情节（如教授提到"学分已修满，可以提前毕业"）
2. 在全局剧情一致性检查表中记录该设定
3. 后续所有年级表述都要按调整后的时间线计算
4. 集数标注和时间线中要能看出学制的变化
例如主角2028年4月入大一，2030年3月提前本科毕业（2年修完4年学分），2030年4月入硕士，2032年3月硕士毕业——这个时间线必须在剧情中明确交代。


## 更新日志

### v4.5.0
- **通用化升级**：将原剧本专用规则泛化为所有长文本通用规则（小说、报告、剧本、长文档等）。
- 新增**同一事件重复叙述**通用检测：同一事件在不同章节/段落中被重复叙述，内容高度相似。适用于所有叙事类长文本。
- 新增**人物去向前后矛盾**通用检测：前文说某人已离开，后文又写送别，导致时间线自相矛盾。
- 新增**时间线自相矛盾**通用检测：同一事件的时间在不同章节中说法不一。
- 新增**跨年引用错误**通用检测：引用年度事件时年份与实际时间线不符。
- 新增**模板化重复段落**通用检测：连续多段使用相同结构，只换具体事项。
- 明确标注"适用范围"：核心规则通用，剧本专用规则仅在剧本创作时启用。
- 同步更新description和版本号。
### v4.4.0
- 新增**同一人物送别情节重复检测**：同一人物的送别/告别情节被写了2-3场（如三场都在机场送小晚），每场都是"机场告别/拥抱/流泪"的同一结构。送别只写1场，补充场不得重复送别动作。
- 新增**主场次与补充场人物去向矛盾检测**：主场次说人物已离开，补充场又写送别，导致"先说走了，后说才送"的时间线自相矛盾。补充场人物状态必须与主场次一致。
- 新增**跨年引用年份校验**：跨年事件（年度赛事、跨年晚会等）的年份引用与实际时间线不符（如把2033年的夜莺之夜写成2034年）。
- 新增**同一人物离开时间自相矛盾检测**：同一人物的离开时间在不同场次中说法不一（一场说下午的飞机，另一场说明天晚上的飞机）。所有场次必须指向同一个航班时间。
- 新增任务拆解阶段的3张全局表：人物去向时间统一表、送别/告别情节去重表、跨年事件年份对照表。
- 同步工作流闸门（第27—30条）与准出条件（第29—32条）。
### v4.3.0
- 新增**模板化重复场次检测**：AI为凑场次数量，把同一类情节拆成N场换汤不换药的模板（如"帮老人学XX"连续8场），每场结构相同只换具体事项。同一模板最多1-2场，且第2场必须有新信息增量。
- 新增**同一情节线重复检测**：关键情节节点（板车上路、NAS入库、宣判、导弹发射、安全门被撬、飞机接地等）每个只写1场，不得重复。如需多角度呈现，用补充场但必须提供新信息。
- 新增**"万能帮助"桥段滥用检测**：主角帮助他人的情节必须合并为少数几场有具体人物故事的戏，不能拆成N场"遇到困难→帮忙→感谢"的同一结构流水账。
- 新增**同集情节多样性检查**：每集必须包含不同类型情节（冲突/转折/人物揭示/动作戏/情感戏），不能全是同一结构。
- 新增任务拆解阶段的全局情节去重表和同集情节多样性规划。
- 同步工作流闸门（第23—26条）与准出条件（第25—28条）。
### v4.2.0
- 新增**人物年龄精确到生日检测**：根据人物精确出生日期（年-月-日）和场景日期计算实际年龄，未到生日不增岁。防止"3月写18岁但4月才生日"类错误。
- 新增**相对时间表述与实际时间线交叉校验**：所有"X年前/后""X岁时离开/回来/失去亲人/发生某事"等相对时间表述，必须与全局关键事件日期表和人物出生日期核对一致。防止"七岁走（实际十岁走）""十二岁失去长辈（实际十岁）"类错误。
- 新增**人物年龄对比校验**："A比B大/小X个月/岁"必须与两人精确出生日期核对，防止写反（如4月生的人被写成比8月生的人小）。
- 新增**同班同学年级一致性校验**：主角的同班同学默认同年级，跳级/留级/提前毕业必须有明确情节说明。
- 新增任务拆解阶段的4张全局表：人物出生日期精确表、关键事件日期表、人物关系与年龄对比表、同学年级一致性表。
- 同步工作流闸门（第19—22条）与准出条件（第21—24条）。

### v4.1.0
- 新增**场次四字段完整性检测**：每场必须含"大纲锚点（作者口径）""时间：""地点：""出场人物：/人物："，字段名照抄不得改写。
- 新增**集头三字段完整性检测**：每集必须含集标题（推荐"第二季·第X集《集名》"，兼容旧格式）、"本集概要（按作者更正口径）"、"本集场次（第X场—第Y场）"。
- 新增**日本9月"新学期"误写硬规则**：日本新学年在4月，9月是前期末/暑假结束，只能写"暑假结束""前期最后阶段""後期即将开始"；命中"新学期/新学年/开学"即报错。
- 增强**补充场位置检测**：补充场紧跟同号主场次、（一）（二）序号连续不重号、时间戳夹在主场次与下一主场次之间。
- **修复** `verify_format_and_supplement()` 解析器 bug：关闭旧场次时原先硬编码 `is_supp=False/True`，导致主场次被误标为补充场、脚本在真实文档上抛 `AttributeError`；改为统一使用 `cur_is_supp`/`cur_supp_ord`。
- 新增检测脚本 `verify_format_and_supplement()`，并同步工作流闸门（第16—18条）与准出条件（第17—20条）。

### v4.0.0
- 新增集数标注完整性检测、集数编号连续性校验、跨文档衔接检查。
- 新增日本学制校验（4月入学/3月毕业、本科4年/修士2年）。
- 新增人物年龄-年级对应检测（未到生日不增岁、按入学年份推算年级）。

### v3.0.0
- 新增剧情逻辑连贯性检测：星期几自动校验、主场次与补充场内容重复检测、相邻场次情节相似度检测、人物名字冲突检测。
- 新增全局人物表与全局剧情一致性检查表。
