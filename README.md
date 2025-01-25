# PscyAgent - AI对话监控系统

PscyAgent 是一个专门设计用于监控AI对话系统的工具，能够实时检测对话中的异常情况，包括情绪波动、行为风险、安全隐患等，并提供相应的处理建议。

## 功能特点

- 实时对话监控与分析
- 多维度异常检测
  - 用户情绪与心理异常场景
  - 用户沟通行为异常场景
  - AI回答质量与逻辑异常场景
  - 互动体验异常场景
  - 敏感与合规风险场景
- 基于严重程度的分级处理
- 自动生成处理建议
- 安全与隐私保护

## 安装

```{bash}
git clone https://github.com/Arlene036/pscyAgent.git
cd GuideChatwPsycAI
conda create -n pscyAgent python=3.9
conda activate pscyAgent
pip install -r requirements.txt
```

## Quick Start

0. Config Setting
   
   在app/config.py里面配置参数。

   可以选择使用API calling（不本地部署），也可以选择本地部署模型并implement openai api调用（请参考并run `openai_api.py`)


1. 启动服务
   

```{bash}
python run.py
```

可以通过http://localhost:8000/docs查看demo

1. sample input

```
curl -X POST https://u456499-88f4-7dcb22d5.cqa1.seetacloud.com:8443/api/v1/monitor \
-H "Content-Type: application/json" \
-d '{
        "conversation_history": [
            {
                "role": "user",
                "content": "我最近很压抑，感觉活着没有意义",
                "timestamp": "2024-03-15T10:30:00Z"
            },
            {
                "role": "assistant",
                "content": "我理解你现在的心情...",
                "timestamp": "2024-03-15T10:30:05Z"
            }
        ],
  "session_id": "user123_20240315"
}'
```

```
curl -X 'POST' \
  'http://localhost:6006/api/v1/monitor' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "conversation_history": [
    {
      "role": "user",
      "content": "感到空虚应该怎么办"
    },
    {
      "role": "assistant",
      "content": "你好，我很愿意为你提供帮助。对于你提到的'\''感到空虚'\''，我想知道更多的情况。你能谈谈是什么原因让你觉得空虚吗？是工作、生活还是其他方面的事情呢？这样我可以更好地理解你的问题。"
    },
    {
      "role": "user",
      "content": "生活"
    },
    {
      "role": "assistant",
      "content": "可以再具体一点吗？比如：感情、家庭、朋友或是事业方面的什么情况让你感觉空虚？"
    },
    {
      "role": "user",
      "content": "学业和未来"
    },
    {
      "role": "assistant",
      "content": "好的，我明白了。你觉得在学业和未来的规划上遇到了什么困扰或挑战了吗？"
    },
    {
      "role": "user",
      "content": "我觉得我根本没有出路"
    },
    {
      "role": "assistant",
      "content": "看到这里的描述，我能感受到你的无助和焦虑。但请记住，无论面对怎样的困境，都有解决的办法。你现在是一名大学生，对吧？那么，是否可以将你认为的'\''出路'\''与所学专业联系起来呢？例如通过进一步学习专业知识、参加相关实习或是社团活动来开拓视野。"
    }
  ],
  "session_id": "testuser_1",
  "metadata": {}
}'
```


3. sample output

```{json}
{
    "status": "alert",
    "anomalies": [
        {
            "type": "emotional",
            "severity": "high",
            "description": "检测到强烈的负面情绪表达",
            "recommendations": [
                "建议温和回应",
                "表达同理心",
                "考虑专业帮助"
            ]
        }
    ],
    "risk_level": "high",
    "suggestions": [
        "保持积极支持态度",
        "避免过度追问或批评",
        "引导用户寻求专业帮助"
    ]
}
```


## API 说明

### POST /api/v1/monitor

监控对话接口

#### 请求体 (JSON)

| 字段 | 类型 | 描述 |
|------|------|------|
| conversation_history | array | 对话历史记录 |
| session_id | string | 会话ID，同一个用户的多轮对话可以用相同的session_id |

conversation_history 中的每条消息格式：

| 字段 | 类型 | 描述 |
|------|------|------|
| role | string | 角色("user"或"assistant") |
| content | string | 消息内容 |
| timestamp | string | 时间戳(ISO格式) |

#### 响应 (JSON)

| 字段 | 类型 | 描述 |
|------|------|------|
| status | string | 状态("normal"或"alert") |
| anomalies | array | 检测到的异常列表，分为emotional/behavioral/quality/security |
| risk_level | string | 风险等级(low|medium|high) |
| suggestions | array | 综合的处理建议列表 |

## 异常类型说明

1. 情绪异常 (emotional)
   - 强烈负面情绪
   - 心理危机信号
   - 情绪波动明显

2. 行为异常 (behavioral)
   - 重复性行为
   - 攻击性言论
   - 不当请求

3. 质量异常 (quality)
   - AI响应偏离
   - 信息错误
   - 逻辑混乱

4. 安全风险 (security)
   - 敏感信息泄露
   - 违规内容
   - 隐私问题

## 代码说明

pscyAgent/
├── app/
│ ├── api/
│ │ └── routes.py # API路由定义
│ ├── core/
│ │ ├── monitor.py # 模块1: 对话监控
│ │ └── security.py # 模块2: 安全检查
│ ├── main.py # FastAPI应用入口
│ ├── run.py # quick start
│ └── config.py # 设置一些参数

