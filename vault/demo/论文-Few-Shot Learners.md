---
title: "论文-Language Model is Few-Shot Learners"
tags:
  - paper
  - nlp
  - few-shot
  - gpt-3
created: 2026-04-18
authors:
  - Tom B. Brown
  - Benjamin Mann
  - Nick Ryder
publication: arXiv
year: 2020
arxiv: "2005.14165"
---

# 论文-Few-Shot Learners

## 基本信息

| 字段 | 内容 |
|-----|------|
| 标题 | Language Models are Few-Shot Learners |
| 作者 | Brown et al. (OpenAI) |
| 发表时间 | 2020 |
| 引用 | 2005.14165 |

## 核心贡献

这篇论文提出了 GPT-3，一个拥有 1750 亿参数的自回归语言模型。论文的核心发现是：**大规模语言模型可以在不进行梯度更新的情况下，通过少量样本（few-shot）学习新任务**。

### 主要发现

1. **Few-Shot 能力**：GPT-3 可以仅通过给定任务的几对输入-输出示例来学习任务，无需任何梯度更新
2. **Scaling Laws**：模型性能与模型大小、数据量成正比
3. **涌现能力**：当模型规模达到临界值时，会涌现出一些小型模型不具备的能力

## 方法论

### Prompt Engineering

GPT-3 使用"语境学习"（In-Context Learning）的方式工作：

```
输入：完成以下任务
示例1：输入 → 输出1
示例2：输入 → 输出2
示例3：输入 → 输出3
测试输入 → [模型预测]
```

### 模型规模

| 模型 | 参数 | Context Length |
|-----|------|----------------|
| GPT-3 Small | 125M | 2048 |
| GPT-3 Medium | 350M | 2048 |
| GPT-3 Large | 760M | 2048 |
| GPT-3 XL | 1.3B | 2048 |
| GPT-3 2.7B | 2.7B | 2048 |
| GPT-3 6.7B | 6.7B | 2048 |
| GPT-3 13B | 13B | 2048 |
| GPT-3 175B | 175B | 2048 |

## 实验结果

### 自然语言任务

在多个 NLP 任务上进行了测试：
- **文本补全**：几乎完美
- **翻译**：接近专业翻译水平
- **问答**：显著优于微调模型
- **常识推理**：存在一定局限

### 发现与局限

1. **长文本处理**：随着文本长度增加，性能下降
2. **数学推理**：复杂数学问题表现不佳
3. **最新知识**：无法获取训练后的信息
4. **偏见问题**：继承了训练数据中的偏见

## 实践意义

### 对个人知识库的启发

1. **RAG 范式**：结合检索和生成，利用模型的 Few-Shot 能力
2. **Prompt 设计**：精心设计的提示可以显著提升输出质量
3. **知识组织**：好的知识结构本身就是好的 Prompt

### 与本项目的关系

本项目计划使用 [[Ollama]] 本地部署类似 GPT-3 的模型，通过 RAG 技术实现基于个人笔记的智能问答。

## 相关链接

- [原论文](https://arxiv.org/abs/2005.14165)
- [OpenAI Blog](https://openai.com/blog/gpt-3-apps/)
- 复现项目：[GPT-Neo](https://github.com/EleutherAI/gpt-neo)

## 相关笔记

- [[项目-知识库搭建]] — 本论文是项目技术选型的参考
- [[概念-第二大脑]] — 知识管理理念
- [[论文-Attention is All You Need]] — Transformer 架构
