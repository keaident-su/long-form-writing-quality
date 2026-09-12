# Long-Form Writing Quality / 长文本写作质量控制

> A quality-control skill for preventing LLM "long-text degradation" — fragmented punctuation, mechanical repetition, stiff dialogue tags, and paragraph atrophy in generated fiction, scripts, and reports.
>
> 一个用于防止大模型"长文本退化"的质量控制技能——解决生成小说、剧本、报告时出现的碎片化断句、机械重复、对话标签僵硬、段落萎缩等问题。

---

## 中文说明

### 解决什么问题

大模型在单次连续生成超过 5000 字的文本时，会出现**"长文本退化"（long-text degradation）**现象。这不是内容问题，而是生成方式的问题。

退化的典型表现：

| 退化模式 | 错误示例 | 正确写法 |
|---------|---------|---------|
| 主语后插逗号 | `裴砚，说` `钢哥，点了点头` | `裴砚说` `钢哥点了点头` |
| 英文名后插逗号 | `Karen，坐在` `David，说` | `Karen坐在` `David说` |
| 句子碎片化 | `也可能，是，老挝当地的，警察。` | `也可能是老挝当地的警察。` |
| 对话标签僵硬 | `"明白。"钢哥，点了点头，"我，这就，去安排。"` | `"明白。"钢哥点头，"我这就去安排。"` |
| 机械重复句式 | 连续多段都是 `他，的心跳，开始，加速。` | 句式要有变化，长短句交替 |
| 段落过短过碎 | 每段只有 1-2 句话，且都是碎片句 | 段落长度要有变化 |
| 空行密度过高 | 每段之间都有 2 个以上空行，一页没几行字 | 段落之间最多 1 个空行 |

### 核心工作流

1. **任务拆解**：总字数目标 → 拆分为独立单元（如每集）→ 每个单元再拆分为批次（每批 ≤ 4000 字）
2. **分批生成**：每批严格控制在 4000 中文字符以内，遵守自然语言节奏
3. **每批质量检查**：8 项检查闸门，不通过则重写该批
4. **合并与最终验证**：全量退化扫描 + 字数验证 + 时间线检查 + 空行密度检查 + 通读修改

### 自动检测脚本

```bash
python references/degradation_detector.py <你的文本文件.txt>
```

检测 7 种退化模式（含空行密度、英文名主语逗号）+ 时间线递增验证，输出详细报告。

### 文件结构

```
long-form-writing-quality/
├── SKILL.md                          # 主技能文件（规则、工作流、准出条件）
├── README.md                         # 本文件（中英文说明）
├── LICENSE                           # MIT 许可证
└── references/
    ├── degradation_detector.py       # 自动检测脚本（可直接运行）
    └── before_after_cases.md         # 5 个 Before/After 对比案例
```

### 准出条件（8 项必须全部通过）

1. ✅ 退化模式自动检测通过（0 个问题，含空行密度检测）
2. ✅ 中文字符数达到目标
3. ✅ 总字符数达到目标
4. ✅ 时间线严格单调递增（0 个倒流）
5. ✅ 空行密度正常（段落之间最多 1 个空行，无连续空行注水）
6. ✅ 全文通读至少一遍，不通顺处已修改
7. ✅ 人物年龄、身份、性格与设定一致
8. ✅ 所有补充场都放在对应场次下方

### 适用场景

- 长篇小说、剧本、剧本杀的批量生成
- 超过 5000 字的报告、白皮书、技术文档
- 任何需要大模型连续生成大量文本的场景

---

## English

### What Problem It Solves

When LLMs generate more than ~5000 characters in a single continuous pass, they exhibit **"long-text degradation"** — a quality collapse caused by attention dilution. This is not a content problem; it is a generation-method problem.

Typical degradation patterns:

| Degradation Pattern | Bad Example | Correct |
|---------------------|-------------|---------|
| Comma after Chinese subject | `Pei Yan, said` `Gang Ge, nodded` | `Pei Yan said` `Gang Ge nodded` |
| Comma after English name | `Karen, sat` `David, said` | `Karen sat` `David said` |
| Sentence fragmentation | `It might, be, the local, police.` | `It might be the local police.` |
| Stiff dialogue tags | `"Understood." Gang Ge, nodded, "I, will, arrange it."` | `"Understood." Gang Ge nodded, "I'll arrange it."` |
| Mechanical repetition | Consecutive paragraphs all start with `His, heart, started, racing.` | Vary sentence structure, mix long and short |
| Atrophied paragraphs | Every paragraph is 1-2 fragmented sentences | Vary paragraph length |
| Excessive empty lines | 2+ blank lines between every paragraph, sparse pages | Max 1 blank line between paragraphs |

### Core Workflow

1. **Decompose**: Total word target → units (e.g., per episode) → batches (≤4000 chars each)
2. **Batch generation**: Each batch ≤ 4000 Chinese characters, following natural language rhythm
3. **Per-batch quality gate**: 8 checks; rewrite the batch if any fails
4. **Merge & final verification**: Full degradation scan + word count + timeline check + empty-line density + read-through

### Auto-Detection Script

```bash
python references/degradation_detector.py <your_text_file.txt>
```

Detects 7 degradation patterns (including empty-line density, English-name subject commas) + verifies monotonic timeline, outputs a detailed report.

### File Structure

```
long-form-writing-quality/
├── SKILL.md                          # Main skill file (rules, workflow, exit criteria)
├── README.md                         # This file (bilingual)
├── LICENSE                           # MIT License
└── references/
    ├── degradation_detector.py       # Runnable detection script
    └── before_after_cases.md         # 5 Before/After comparison cases
```

### Exit Criteria (all 8 must pass)

1. ✅ Degradation auto-detection passes (0 issues, incl. empty-line density)
2. ✅ Chinese character count meets target
3. ✅ Total character count meets target
4. ✅ Timeline strictly monotonic (0 reversals)
5. ✅ Empty-line density normal (max 1 blank line between paragraphs)
6. ✅ Full read-through completed, awkward passages fixed
7. ✅ Character age/identity/personality consistent with设定
8. ✅ All supplementary scenes placed under their corresponding scene

### Use Cases

- Batch generation of novels, scripts, screenplays
- Reports, whitepapers, technical docs over 5000 words
- Any scenario requiring an LLM to generate large volumes of continuous text

---

## License / 许可证

MIT License — see [LICENSE](./LICENSE) for details.

## Contributing / 贡献

Issues and PRs are welcome. If you encounter a new degradation pattern not covered by the detector, please open an issue with examples.

欢迎提交 Issue 和 PR。如果发现检测脚本未覆盖的新退化模式，请带示例提交 Issue。
