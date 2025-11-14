# 1. 产品概述（Product Overview）

## 1.1 产品名称

**Meme Agent – AI 驱动的智能梗图助手**

## 1.2 产品一句话介绍

一个能理解用户语言、自动检索最合适的 meme、并在找不到时自动生成新梗图的智能代理系统。

## 1.3 产品目标

将原有 memematch（基于向量检索的梗图搜索器）升级为具备 **自主推理、工具调用、多策略决策** 的完整 AI Agent，提供：

- 语义理解
- 情绪识别
- meme 检索
- meme 生成
- meme 推荐理由解释
- UI 展示

满足课程题目：
 **Creating and Developing LLM Agents for Applications.**

## 1.4 产品痛点（Why）

用户想表达情绪，但：

- 不知道应该找什么 meme
- 无法描述具体图名
- 没有收集很多 meme
- 用搜索引擎找不到精准的梗图
- 聊天中需要快速找到合适的 meme

AI 可以解决：

- 自动理解语义和情绪
- 主动推荐最适合的 meme
- 无相关梗图时生成新的
- 不依赖用户输入精确描述

------

# 2. 用户画像（User Personas）

## Persona A：普通用户（表情包使用者）

- 需求：快速找到/生成合适梗图
- 特征：喜欢社交、喜欢发送 meme

## Persona B：内容创作者（up 主 / 微博博主）

- 需求：快速生成匹配文案情绪的梗图
- 特征：需要大量内容素材

## Persona C：开发者（AI 爱好者）

- 需求：尝试与扩展 meme agent
- 特征：喜欢复用开源系统

------

# 3. 使用场景（User Scenarios）

## 场景 1：输入一句话 → 返回匹配 meme

用户：“我真的不想努力了”
 Agent：找到一张“摆烂 / 放弃 / 厌世”风格的 meme

## 场景 2：情绪驱动

用户：“离谱”
 Agent：识别为“震惊/吐槽”，自动找出合适 meme

## 场景 3：搜索不到 → 自动生成

用户：“帮我来一张‘原地解体’的 meme”
 Agent：
 → 检索失败
 → 自动生成模板梗图

## 场景 4：自动推荐

用户：“我太困了”
 Agent：给出疲倦、虚脱类 meme

------

# 4. 产品功能需求（Core Features）

------

## **4.1 核心功能 F1：LLM Agent 推理（必须）**

### 功能描述

- LLM 负责对用户输入进行理解、决策
- 选择合适的工具（检索/生成/改写查询）
- 多轮内部 ReAct 推理

### 验收标准

- 能根据用户输入自动选择最合适工具
- 能实现「思考 → 行动 → 观察 → 再行动」的 Agent 流程

------

## **4.2 F2：Meme 检索（search_meme）**

### 描述

使用 memematch 的向量数据库进行检索：

- CLIP → embeddings
- FAISS → L2/余弦相似度
- 返回 top-k 结果

### 验收标准

- 输入文本能返回语义最接近 meme
- 相似度排序正确
- 响应时间 < 200ms

------

## **4.3 F3：查询改写（refine_query）**

### 描述

LLM 将用户模糊输入转成检索友好 query。

示例
 “我已经无语了” → “speechless reaction meme”

### 验收标准

- 语义合理
- 检索结果提升（召回率提高）

------

## **4.4 F4：情绪分类（classify_sentiment）**

使用 LLM 识别用户情绪：

| 情绪 | 对应 meme  |
| ---- | ---------- |
| 开心 | 开心表情包 |
| 生气 | 发火       |
| 无语 | speechless |
| 震惊 | surprised  |
| 绝望 | despair    |

### 验收标准

- 准确率 ≥ 80%

------

## **4.5 F5：Meme 生成（generate_meme）**

两种模式：

### A. 模板生成（PIL）

使用 Drake / Doge / Wojak 模板，填字即可。
 🟢 本地 CPU 即可运行。

### B. 文生图生成（可选）

调用 FLUX / SDXL / OpenAI Image API
 用于产生全新 meme。

### 验收标准

- 模板版生成时间 < 0.5s
- 生成内容可读性高

------

## **4.6 F6：推荐理由解释（explain）**

LLM 自动解释：

- 为什么返回这张 meme
- 它表达的情绪是什么
- 如何匹配用户输入

### 验收标准

- 自然、流畅
- 不产生幻觉

------

## **4.7 F7：Web UI（streamlit 或 gradio）**

界面包含：

- 文本输入框
- meme 展示窗口
- Top-k 结果列表
- 下载按钮
- AI 推荐理由展示

------

# 5. 非功能性需求（NFR）

## 5.1 性能

- 检索延迟 < 200ms
- Agent 推理 < 1.5s
- 模板生成 < 0.5s

## 5.2 可扩展性

支持新增 meme、替换模型、扩展工具函数。

## 5.3 可维护性

模块化设计：

```
/agent
/tools
/search
/generate
/ui
```

------

# 6. 系统架构（System Architecture）

```
User
 ↓
Frontend (Streamlit)
 ↓
Agent API
 ↓──────────────┬──────────────┬──────────────┐
                │              │              │
        search_meme       generate_meme   refine_query
                │              │              │
            Vector DB        Template       LLM（API）
          (FAISS + CLIP)     Engine        
```

------

# 7. 数据结构设计

## Meme Embedding

```
{
  "image_path": ".../happy_001.png",
  "embedding": [0.12, 0.33, ...],
  "tags": ["happy", "cute"]
}
```

## 查询结果

```
{
  "query": "我无语了",
  "refined_query": "speechless reaction meme",
  "results": [
    {"path": "meme1.png", "score": 0.88},
    {"path": "meme2.png", "score": 0.84}
  ]
}
```

------

# 8. 项目里程碑（Milestones）

| 阶段 | 内容                | 时间   |
| ---- | ------------------- | ------ |
| M1   | 搭建 FAISS 检索模块 | 1 天   |
| M2   | Agent 工具函数定义  | 1 天   |
| M3   | LLM Agent 推理链路  | 1-2 天 |
| M4   | 模板生成功能        | 0.5 天 |
| M5   | Streamlit UI        | 1 天   |
| M6   | 测试 & Demo         | 1 天   |

总开发时间：**5–7 天**

------

# 9. 风险与解决方案

| 风险                 | 可能影响   | 解决              |
| -------------------- | ---------- | ----------------- |
| LLM 输出错误调用工具 | Agent 卡死 | 添加验证器        |
| 生成图需要 GPU       | 成本上升   | 使用模板生成模式  |
| 检索质量随数据波动   | 用户体验差 | 引入 refine_query |

------

# 10. 验收标准（Acceptance Criteria）

-  输入任意一句话 → 能返回至少 1 张合理的 meme
-  搜索不到时 → 自动生成 meme
-  Agent 能自主选择工具
-  输出理由自然
-  UI 可互动、可展示 meme
-  所有功能可本地 CPU 运行