基于搜索到的信息，我来为您绘制一份 Browser Use Agent 的执行流程图。

graph TD
    A[开始] --> B[初始化 Agent]
    B --> C[配置参数]
    C --> D[启动浏览器会话]
    D --> E[开始执行 agent.run()]
    
    E --> F[步骤开始 - on_step_start Hook]
    F --> G[获取当前页面状态]
    G --> H[截取页面截图]
    H --> I[提取页面内容]
    I --> J[构建上下文信息]
    
    J --> K[LLM 分析当前状态]
    K --> L[LLM 生成思考过程]
    L --> M[LLM 决定下一步动作]
    
    M --> N{是否使用 Planner?}
    N -->|是| O[Planner LLM 制定计划]
    N -->|否| P[直接执行动作]
    O --> P
    
    P --> Q[Controller 执行动作]
    Q --> R{动作类型}
    
    R -->|导航| S[go_to_url]
    R -->|点击| T[click_element]
    R -->|输入| U[type_text]
    R -->|滚动| V[scroll_page]
    R -->|提取| W[extract_content]
    R -->|自定义| X[custom_action]
    
    S --> Y[记录动作结果]
    T --> Y
    U --> Y
    V --> Y
    W --> Y
    X --> Y
    
    Y --> Z[更新 Agent 状态]
    Z --> AA[步骤结束 - on_step_end Hook]
    AA --> BB{任务完成?}
    
    BB -->|否| CC{达到最大步数?}
    CC -->|否| DD{发生错误?}
    DD -->|否| F
    DD -->|是| EE[错误处理]
    CC -->|是| FF[达到步数限制]
    
    BB -->|是| GG[任务完成]
    EE --> HH{重试次数}
    HH -->|未超限| F
    HH -->|超限| II[执行失败]
    
    FF --> JJ[返回执行历史]
    GG --> JJ
    II --> JJ
    
    JJ --> KK[关闭浏览器会话]
    KK --> LL[结束]

    %% 样式定义
    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef action fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef hook fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    
    class A,LL startEnd
    class B,C,D,E,G,H,I,J,K,L,M,O,Q,Y,Z,JJ,KK process
    class N,BB,CC,DD,HH decision
    class S,T,U,V,W,X action
    class F,AA hook

流程说明
1. 初始化阶段
Agent 初始化: 配置任务、LLM、控制器等参数
浏览器启动: 创建 BrowserSession，启动浏览器实例
环境准备: 设置用户数据目录、允许域名等
2. 执行循环
每个执行步骤包含：

步骤开始 (on_step_start Hook)
执行用户自定义的步骤开始钩子
可以进行状态监控、日志记录等
状态感知
页面状态获取: 获取当前页面 URL、标题、DOM 结构
截图: 如果启用视觉功能，截取页面截图
内容提取: 提取页面文本内容和交互元素
上下文构建: 整合历史信息和当前状态
LLM 决策
状态分析: LLM 分析当前页面状态和任务进度
思考过程: 生成推理过程和下一步计划
动作决策: 决定执行哪个具体动作
规划器 (可选)
如果配置了 Planner LLM，会进行高级任务规划
帮助分解复杂任务和制定策略
动作执行
Controller 调度: 根据 LLM 决策调用相应的动作函数
内置动作: 导航、点击、输入、滚动、内容提取等
自定义动作: 用户定义的扩展功能
步骤结束 (on_step_end Hook)
执行用户自定义的步骤结束钩子
可以进行结果处理、状态保存等
3. 终止条件
任务完成: LLM 判断任务已完成
步数限制: 达到最大执行步数 (默认 100)
错误处理: 发生不可恢复的错误
4. 结果返回
执行历史: 返回 AgentHistoryList 对象
状态信息: 包含访问的 URL、截图、动作记录等
资源清理: 关闭浏览器会话
关键特性
状态管理: 维护完整的执行历史和上下文
错误恢复: 支持重试机制和错误处理
扩展性: 支持自定义动作和生命周期钩子
可观测性: 提供详细的执行日志和状态跟踪
安全性: 支持敏感数据处理和域名限制
这个流程图展示了 Browser Use Agent 从初始化到完成任务的完整执行过程，包括了所有主要的组件和决策点。