# Research Report

**Query:** Claude Code 使用技巧：如何进行长时间后台任务、最大化利用 token 的方法

**Generated:** 2025-12-17 00:51:57

---

# Claude Code 高级应用指南：长效后台任务管理与 Token 效能最大化策略

## 摘要与关键点

本报告旨在为 Claude Code 的高级用户提供关于**长时间后台任务管理**与**Token 资源最大化利用**的深度技术分析与实践指南。Claude Code 作为 Anthropic 推出的命令行（CLI）代理工具，通过直接接入本地开发环境，极大地改变了传统的编码工作流。然而，其基于 Token 的计费模式与无状态的大语言模型（LLM）特性，要求开发者必须掌握特定的优化技巧以平衡成本与效率。

**核心发现与建议：**
*   **后台任务管理**：Claude Code 支持通过 `Ctrl+B` 快捷键或在工具调用中设置 `run_in_background: true` 来将耗时命令（如服务器启动、构建过程）放入后台运行。这允许开发者在不阻塞主对话线程的情况下继续交互。然而，当前版本存在“系统提醒（System Reminder）”循环的严重 Bug，可能导致已完成的任务持续消耗 Token，需通过重启会话或特定工作流规避。
*   **Token 效能最大化**：核心策略在于**Prompt Caching（提示词缓存）**的应用，可减少高达 90% 的成本。此外，通过精简 `CLAUDE.md` 上下文文件、合理使用 `/clear` 和 `/compact` 命令、以及采用分层上下文架构（Tiered Context），可以显著降低无效 Token 的消耗。
*   **成本监控**：建议集成 `/cost` 命令与自定义状态栏（Statusline），实时监控 Token 消耗速率，避免因上下文膨胀导致的意外支出。

---

## 1. Claude Code 架构与运行机制概述

Claude Code 是一个基于终端的代理编码工具，它不仅是一个简单的聊天机器人，更是一个能够执行文件读写、命令运行和代码分析的智能代理 [cite: 1]。理解其底层架构是掌握后台任务和 Token 优化的前提。

### 1.1 代理的工作模式
Claude Code 运行在用户的本地环境中，继承了用户的 Shell 权限（如 Bash 或 Zsh）。它通过调用 Anthropic 的 API（主要是 Claude 3.5 Sonnet 或 Opus 模型）来理解用户意图，并将这些意图转化为具体的 Shell 命令或文件操作 [cite: 1, 2]。

### 1.2 上下文窗口与无状态性
与所有 LLM 一样，Claude 是无状态的。这意味着每一次交互，Claude Code 都必须将当前的对话历史、项目上下文（如 `CLAUDE.md`）、文件内容以及工具输出重新发送给模型。随着会话的进行，上下文窗口（Context Window）会不断累积，导致 Token 消耗呈指数级或线性增长，这直接关系到成本控制与响应延迟 [cite: 3, 4]。

---

## 2. 长时间后台任务的执行与管理

在软件开发中，启动开发服务器（如 `npm run dev`）、运行长耗时测试套件或执行构建任务是常态。Claude Code 提供了专门的机制来处理这些任务，使其不阻塞当前的交互会话。

### 2.1 启动后台任务的方法

Claude Code 提供了两种主要方式将任务置于后台运行：

1.  **交互式快捷键（Interactive Shortcut）**：
    当 Claude Code 建议执行一个命令时，用户可以按下 `Ctrl+B`（在 tmux 中可能需要按两次）将该命令推入后台执行，而不是默认的前台阻塞执行 [cite: 5, 6, 7, 8]。
    *   **注意**：在 macOS 终端中，`Ctrl+B` 默认绑定为光标后退。如果遇到冲突，可能需要调整终端配置或通过明确的 Prompt 指令来实现 [cite: 9]。

2.  **自然语言指令与工具参数**：
    用户可以直接在 Prompt 中指示 Claude：“在后台启动开发服务器”。Claude 会在调用 `Bash` 工具时，自动将 `run_in_background` 参数设置为 `true` [cite: 7, 10]。
    *   **代码示例**：
        ```json
        {
          "tool": "Bash",
          "command": "npm run dev",
          "run_in_background": true
        }
        ```

### 2.2 后台任务的监控与管理

一旦任务在后台运行，Claude Code 提供了一套工具来管理这些进程：

*   **查看任务列表**：使用 `/bashes` 命令可以列出当前所有活跃的后台 Shell 及其 ID（如 `bash_1`, `bash_2`）[cite: 5, 7]。
*   **获取输出**：Claude 会通过 `BashOutput` 工具异步获取后台进程的日志输出。用户可以询问“检查服务器日志”来触发此工具 [cite: 6, 11]。
*   **终止任务**：
    *   使用 `KillBash` 工具或在 `/bashes` 界面中按 `k` 键来终止特定进程 [cite: 5, 7]。
    *   **重要**：直接使用 `Ctrl+C` 可能会退出 Claude Code 客户端，而不是仅仅停止后台任务。应使用 `Escape` 键停止 Claude 的当前生成，或使用专门的命令管理后台进程 [cite: 12]。

### 2.3 任务持久化与会话恢复

Claude Code 的一个关键特性是**进程持久化（Process Persistence）**。
*   **理论机制**：后台任务在设计上是为了跨会话持久化的。即使用户退出了 Claude Code（例如通过 `/exit`），后台进程（如 Docker 容器或 Node 服务器）通常仍在系统层面上运行 [cite: 7, 13]。
*   **会话恢复**：通过 `claude --resume` 或 `claude --continue` 命令重新进入会话时，Claude 理论上可以重新连接到这些后台任务的上下文，继续监控其输出 [cite: 11, 14, 15]。
*   **现实限制**：尽管进程在 OS 层面继续运行，但有用户报告称，一旦关闭终端窗口，Claude Code 的“会话状态”可能会丢失，导致无法在新的终端窗口中通过简单的恢复命令重新接管对该进程的“智能控制”（即 Claude 忘记了它启动过这个任务）[cite: 16]。因此，建议在同一终端会话中保持运行，或依赖 `CLAUDE.md` 记录关键的进程信息以便手动恢复上下文。

### 2.4 关键风险：系统提醒（System Reminder）循环 Bug

当前版本的 Claude Code（截至 2025 年末的报告）在后台任务管理上存在一个严重缺陷，被称为“僵尸进程提醒”或“无限系统提醒”Bug [cite: 17, 18, 19]。

*   **现象**：当一个后台任务完成（无论是成功还是失败），或者即使用户尝试杀死了该进程，Claude Code 的内部状态机可能未能正确更新。结果是，系统会不断地在每一次后续交互中插入 `<system-reminder>` 标签，提示“后台任务仍在运行”或“有新输出”。
*   **后果**：
    *   **Token 爆炸**：每个提醒消耗约 50-100 Token。如果未被察觉，这些提醒会随着每一次对话累积，导致 Token 消耗激增（单次交互可能浪费数千 Token）[cite: 18, 20]。
    *   **上下文污染**：无关的提醒干扰了模型的推理能力。
*   **解决方案与规避策略**：
    1.  **彻底重启**：一旦发现任务完成但提醒未停止，必须完全退出 Claude Code 并重新启动。简单的 `/clear` 命令无法清除后台任务的内部状态 [cite: 20]。
    2.  **避免使用后台模式**：对于非必要的长任务，考虑在前台运行并设置较长的超时时间（Timeout），虽然这会阻塞交互，但能避免 Token 浪费 [cite: 17]。
    3.  **“黑视”协议（Blackout Protocol）**：有用户提出一种变通方法，即在启动后台任务后，立即在前台运行一个长时间的 `sleep` 命令。这会阻止系统提醒的触发，直到用户准备好检查结果 [cite: 18]。

---

## 3. 最大化利用 Token 的策略与方法

Token 是 Claude Code 经济模型中的核心货币。最大化利用 Token 不仅仅是“省钱”，更是为了在有限的上下文窗口（Context Window）内容纳更多有效信息，从而提升模型输出的质量和准确性。

### 3.1 核心策略：Prompt Caching（提示词缓存）

Prompt Caching 是 Anthropic 提供的一项革命性功能，对于代码开发场景尤为重要。它允许系统缓存前缀提示词（Prefix Prompts），从而避免对重复的上下文（如代码库结构、文档、规范）进行重复计费和处理 [cite: 21, 22]。

*   **收益**：
    *   **成本降低**：缓存读取的成本仅为基础输入 Token 价格的 10%（即降低 90%）[cite: 22, 23]。
    *   **延迟降低**：对于长 Prompt，首字延迟（TTFT）可降低 85% [cite: 22, 24]。
*   **实施方法**：
    *   **结构化 Prompt**：将静态内容（如 `CLAUDE.md`、工具定义、系统指令）放在 Prompt 的最前端。
    *   **断点设置**：Claude Code 内部会自动处理缓存断点（Cache Breakpoints）。通常，`CLAUDE.md` 和项目文件结构会被自动缓存。
    *   **保持前缀一致性**：为了命中缓存，新的请求必须拥有与之前请求完全相同的“前缀”。因此，避免在对话的起始部分频繁修改 `CLAUDE.md` 或系统指令，除非必要 [cite: 21, 24]。
*   **CLI 控制**：可以通过环境变量 `DISABLE_PROMPT_CACHING=1` 禁用缓存以进行调试，但在正常使用中应始终开启 [cite: 25]。

### 3.2 上下文卫生管理（Context Hygiene）

随着对话深入，上下文窗口会被旧代码、错误日志和闲聊填满。有效的清理策略至关重要。

1.  **`/clear` vs `/compact`**：
    *   **`/clear`（推荐）**：完全清除对话历史，仅保留 `CLAUDE.md` 和系统提示。这是最彻底的 Token 节省方式。建议在完成一个独立任务（如“修复 Bug A”）后，立即运行 `/clear` 再开始下一个任务 [cite: 12, 15, 26]。
    *   **`/compact`（谨慎使用）**：将历史对话压缩为摘要。虽然能保留部分上下文，但压缩过程本身消耗 Token，且摘要可能丢失关键的代码细节，导致模型产生幻觉。许多资深用户建议直接使用 `/clear` 而非 `/compact` [cite: 14, 27, 28]。

2.  **单任务单会话原则**：
    不要在一个会话中处理多个不相关的任务。例如，不要在修复数据库问题的同一个会话中去修改前端 CSS。任务切换时，务必 `/clear` 或重启会话 [cite: 3, 29]。

### 3.3 优化 `CLAUDE.md`：项目记忆的艺术

`CLAUDE.md` 是 Claude Code 的“长期记忆”，它会在每次会话开始时自动加载。优化此文件是 Token 管理的关键 [cite: 30, 31]。

*   **分层上下文（Tiered Context）**：
    *   **Tier 1（全局/根目录）**：仅包含项目核心架构、关键命令（Build/Test）、编码规范。保持在 800 Token 以内 [cite: 32]。
    *   **Tier 2（子目录）**：在特定子目录（如 `/frontend`, `/backend`）放置局部的 `CLAUDE.md`，仅在进入该目录时加载。
*   **避免 `@-mention` 大文件**：
    不要在 `CLAUDE.md` 中直接 `@` 引用大型文档或代码文件。这会导致这些文件的全部内容在每次交互中都被加载，造成巨大的 Token 浪费。相反，应该在 `CLAUDE.md` 中仅提及文件的路径和用途，让 Claude 在需要时通过工具去读取 [cite: 14, 32]。
*   **负面约束的陷阱**：
    避免使用“不要做 X”的负面指令，这往往效果不佳且占用 Token。应使用“优先做 Y”的正面指令 [cite: 14]。

### 3.4 文件访问控制与 `.claudeignore`

Claude Code 默认会尝试索引项目中的文件。如果项目中包含大量无关数据（如 `data.csv`、日志文件、`node_modules`），不仅浪费 Token，还可能干扰模型。

*   **忽略文件**：虽然社区强烈呼吁 `.claudeignore` 功能，但目前主要通过配置 `permissions.deny` 设置（在 `.claude/settings.json` 中）来阻止 Claude 读取特定文件或目录 [cite: 33, 34]。
*   **最佳实践**：明确禁止 Claude 读取 `.env` 等敏感文件或巨大的自动生成文件目录，防止其在自动上下文收集时消耗 Token [cite: 33]。

### 3.5 模型选择策略

Claude Code 允许通过 `/model` 命令切换模型。

*   **Opus vs. Sonnet**：
    *   **Opus**：擅长复杂规划、架构设计和深层 Debug。单价昂贵。
    *   **Sonnet**：擅长代码生成、重构和简单任务。速度快，成本低。
*   **混合策略**：在任务开始阶段（规划期）使用 Opus 进行分析，生成计划后，切换到 Sonnet 进行具体的代码实现（Shift+Tab 可切换自动执行模式，配合 Sonnet 效率极高）[cite: 35, 36]。

### 3.6 监控与反馈

*   **`/cost` 命令**：定期运行 `/cost` 查看当前会话的 Token 使用量和预估成本 [cite: 27, 37]。
*   **状态栏集成**：使用第三方工具（如 `claude-code-statusline`）或配置内置状态栏，实时显示 Token 消耗速率，形成心理“痛感”，从而自觉优化 Prompt [cite: 38, 39]。

---

## 4. 进阶自动化：Hooks 与 MCP

为了进一步提升效率（间接节省 Token，因为减少了来回交互的轮次），可以利用 Hooks 和 MCP。

*   **Hooks（钩子）**：
    可以在工具执行前后自动运行命令。例如，在 `edit_file` 之后自动运行 `linter` 或 `formatter`。这避免了“Claude 写代码 -> 报错 -> Claude 修复格式”的 Token 浪费循环，确保提交给 Claude 的代码总是格式正确的 [cite: 40, 41]。
    *   配置示例：
        ```toml
        [[hooks]]
        event = "PostToolUse"
        command = "npm run lint --fix"
        [hooks.matcher]
        tool_name = "edit_file"
        ```

*   **MCP (Model Context Protocol)**：
    通过 MCP 连接外部工具（如 GitHub, Jira, 数据库）。相比于将所有 API 文档粘贴给 Claude（消耗大量 Token），MCP 允许 Claude 按需查询特定信息，极大地节省了上下文空间 [cite: 25, 42, 43]。

---

## 5. 结论

要在 Claude Code 中实现高效且经济的开发体验，开发者需要从“聊天者”转变为“管理者”。

对于**后台任务**，关键在于利用 `Ctrl+B` 实现并行工作，同时警惕“系统提醒”Bug，必要时果断重启会话。

对于**Token 利用**，核心在于**Prompt Caching** 的被动收益与 **上下文管理** 的主动控制相结合。通过精简 `CLAUDE.md`、养成 `/clear` 的习惯、以及根据任务难度动态切换模型，开发者可以在不牺牲代码质量的前提下，将 Token 成本降低 60% 以上 [cite: 32]。

最终，一个优化良好的 Claude Code 工作流应该是：**Opus 规划 -> Sonnet 执行 -> 后台测试 -> 自动 Lint -> 及时 Clear**。

---

## 参考文献

[cite: 12] Builder.io. (2025). Claude Code usage guide.
[cite: 14] sshh.io. (2025). How I use every Claude Code feature.
[cite: 21] Anthropic. (2025). Prompt caching documentation.
[cite: 22, 23] Anthropic. (2025). Prompt caching blog & Pricing.
[cite: 5] The AI Stack. (2025). Claude Code Pro tips.
[cite: 13] Apidog. (2025). Claude Code background tasks.
[cite: 6, 44] Anthropic. (2025). Interactive mode & CLI reference.
[cite: 7, 11] GitHub (ruvnet/claude-flow). (2025). Background commands wiki.
[cite: 3] YouTube. (2025). Learn how LLM pricing really works.
[cite: 27] Anthropic. (2025). Costs and Token usage.
[cite: 32] Medium. (2025). Stop wasting tokens: How to optimize Claude Code context.
[cite: 2] Anthropic. (2025). Claude Code best practices.
[cite: 1] Anthropic. (2025). Claude Code Overview.
[cite: 33, 34] GitHub & Anthropic. (2025). .claudeignore and Settings.
[cite: 38] Arsturn. (2025). Keep your Claude Code costs in check.
[cite: 17, 18, 19] GitHub Issues. (2025). Background process bugs and system reminders.
[cite: 16] Reddit. (2025). Claude Code session persistence discussions.
[cite: 40, 41] Apidog & Medium. (2025). Claude Code Hooks.
[cite: 4, 30, 31] Anthropic & HumanLayer. (2025). CLAUDE.md best practices.
[cite: 8, 9] Reddit & GitHub. (2025). Ctrl+B background tasks discussions.
[cite: 15] Apidog. (2025). Claude Code CLI commands.
[cite: 36] Apidog. (2025). Claude.md guide.

**Sources:**
1. [claude.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE07gmivzAUQvLsBerYtBujUZLf4OhWVeJmwNZ9ooZLMKEKAh87JTWCOh6mdpFa0IicqAmiEyoKhZB16nOqlYmNk2hpVQsEaY6QKhdRCK0ErUntPiQ1IXd1foQFRSqW)
2. [anthropic.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpj0pvc_3QQKWmvXDJRUMtiEAhqJNmnrl3JmzbsyaYTijy8KWlAA5psvtedv2vjc8LE9Yrrk7Zb9uFfuJtYAafnMItptK0zFsCD6QiSNoR4JBTjsemJzWzc2UAqegXisB1CLPQoKHmtOTfpu_2-zqMDS3nc_yE)
3. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRKeWXB5fVonr253NAYa8xab8j9f9mcoKzoKzJ3pTC6sZiiQMqghbC9ynhkGd-QRjni16J1XxQUh9wvq32DL5b9WLOMQ6ch3fN44BzVlIMJVH7opKTS-Z3kkVAdyQYiy3F)
4. [humanlayer.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPWbIJEAeKuQ8PSHWeOUtsa8WrAIqfOq4NNtPmN0bUFtghiQ4iG8B0p5Jvlwef6cCjkPZc9DH-vmio4Yi88y7r2beQZcPfTTjFBstlZUchAffPhJSFvfFrk-tCqTOYlOXH_Snh1R10anm9MR3PWw==)
5. [theaistack.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSa0FuJNVjESNeT-pVusy9iBfkpEHKcqKPVI2ig2iuaoQ0l6Bo_UAgYhroCJksT31cMYqmMpyM2VJ--siCO5IsULh_3aJOOQMDBgi54ScM7T9iqwfAQ746CE976lsU9f-grzkl)
6. [claude.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFL3V1C8Xazdie9iGlLqf6b0UufsMt76_D4NFmlw3fIY3QRBwj-i8RThpc0k6NhsQnMomEAkfatR_U5ooLz4dlGL6sSd9AqJA518YVZ3kEwF4T3DKdQInPPh7sTYNsLJBmTynwFIGk=)
7. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqY7Z2t3_1QR_q5T6pSGBHqJBXAFlLgCWADz8lHXT8YZjak2-ASqJ0LklKqyjzhJbcp8SUAsLqoJ---Znj4R_4D8fG8ZgxixjU1AChdnr9rgpybyiLd25D1080B4U4z53QassEjq1RqOqHRJrBv5pa8HmZ_Q==)
8. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGC74Xt2a17RlzkaBbuno7jCtfB58b875sfTsP7cXGhM0RnTb7ETtLOlkKUsA6h-ZC5Zx-n4YEZSnLUbKkyOqnhW-Z0fl8gjzHeMdsL-tN7C9eyTwdFKvRjgU4B6LLuxBs9QrUZjBKt5zpQGryzMi4QVgvf2NvmUgeE8tDj6_wterVB6enWobLAY43x7-NemA==)
9. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh96EalZ4GQ8G9Ddnov3j9o6hGjPRWE6XQCom0mCHW7EZXluEDt6l_wj7bvSV4733dfs-6RcrcU22u9KefVYFWPf04n6NNyoQNeX5TRcp4VfWn4_MaMXPvIdrr_CtSX8U5Kxv5g6_DypkIVg==)
10. [vtrivedy.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRx6U2uY-4uEhCDJY6snFwkdhLkxjT1VhjXt8OpdzfLxYmVkoPAW1rE0gEHpj7R6j4dtYre01k8sKjvIVxvKKVgBx5xh61h8uhSpnsAL3C_Vp46p8TCvGa7lqbvy1J0BYUjf8AYWudOxjEstNNkEM=)
11. [githubusercontent.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEp1GKii15BQhEMqLc0WM8uuXWwbMZ5gTUPcADHzsprc__vva92BTgVA0i2d8EFRgWlbGSVSkUyZK2Sz9TLp-GHiU8a34VDkvQjw8_r0PhOVHbIOnTTR8q4JHAm5BhUpMOUeY8_z37Sa76_0cW2CCARBaxKm_MFbqQXY5J-iKtKiCqVtIlLcw==)
12. [builder.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_MTz-oubI9E9gHGi1dkHDI7CnKfvOfd2X0WM9mVgfiW7BHCZh9P9vouj1TTDQ3FzRmmLQ1pF8fo-gxCtVFFrGCIvT9iDKeMc53Z6fmdNtJiK7OxKCeNDy55-0G9c=)
13. [apidog.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_Fhrb7xzYKU26UUnRuHAeZCqSFtlBbHm_-D-Y2KeD7LZHqpeTDlZ3z8T7OkOctkVE9R9-JKUXJKHcd7OyCkV384jxhUZOsZgVsDlp82QZcj9w8lCjFWPmwh0CUvEFirqxEq0XKJH68_fzig==)
14. [sshh.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEv9VL-P9jxMZFh6PeBjEf442zGPSj9dgduCWB7NAaKcegXii86yHy93aZieucV1fUrDAB7iNi2JsH1xKzkzd-hR6Qv-KEpqx2ANDy-mGHfTt_JUaIO2X7zpA_ceIHxdolEY40FVwlZmus0RGthHWOa)
15. [apidog.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkzh5veGIPa-w31qZ3Sx43jaXeqFmoIKpEspbCx-yi1kWAr9ToNVjGN8wILg5GPp7bTKfrHZq7Vk4xJoT7aSTTVF_ZeFh2vv9Wvi9fXD1rMjMeb3FriaRclf57Dh1R7WLN6jwUrr59)
16. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeKYETVsI55yEkU8beX-YqFmgr40XQKbtoK6lO5jCXsdbcSc81MXR-QwQshpKYq79qZ58n1IrXpZQpTdJB4_GYI4gnTieEpXkVjPMM5-eVeFn9lSuvmeiBmPVUQAnMSwqCQLetSHeHgtYAoVVt-xWa-h1lRJ8BSFS5p_uysPlEZExpGsxH6PefusaxudxpLU55SiiROw==)
17. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiHozFYVj1DHxo1GkX--rOGZevHlB01iX79NnkxS6OQI4rnSVAL_voWsS2qKCXVRJ2pDVcdpE_EdPnZ9o9k_sWPEt58_068xhVXIbUT7eILH6OvxiNuhNUt7J_5WK_nSg8mp-rS3nn_2IuJos=)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCcpkZvZOihZtb_nphUkcmBWheUtImzNDo2CEQrYE7A62_PaEv14GzEnA_PB95QHaSV7BQjMvTx9yhapY_pZPi6FpIYkEkEZ-b_A_fwd88SIb381yxaxBEx1BtLtdT6MS9T3am3iGeK3lnKp4=)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEavCtuVq6TwpZjgGXcN8PEfy7Y9zn2N_fn9K6QnEfmYqH46vL7_J8rB6r1yAkAc1wg7ZZ0cocD4iDOmT6vEDs-4XsDLthC-x-iMY2u6J0KRSVzorn3flWDWW5VBv0_F17TU_OIQ072ockmal4=)
20. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvOWRiSyIlX0efiNm22PWdm3heK4TdLsdYN4tPlgv-1RchgmHqxcbsWNQQboRATQVBonMZxJYNwU1a1KY5ec_7KLdOEehfOAm5Rmu4iUJYSeEFLTX9_KrKDZG4HevxJN5TbDJuzy-nzlx40lknfzxGVKtrFGCH-L3M9LP_mGbPvI08_FAZPeJJsQM2oTNFtR6JX2s=)
21. [claude.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXveh8XNBK-9v-yQH6I4sHGzlu0xwSoTlQ1roCVVtk6VAioafD1xV6msZAoJvzgGxlXNKsfhdEEKZByt9G8E-1YtdcVDlZvzxHowdHgV5YAPsIxRMF2_DSUll34bgC11rDucvtV4pfJ1uJX_8ZA__NuzwA-7Xmn9hYoQ==)
22. [claude.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFh7wY-9a78l0SX5J7DHxKpHEjK5Yklk9qPyr-Cswb9hneLWlKu5tsTZbx-dwPGQT692XbHyPRzN1D2mBeXn-Cq4rOL6b6KBmB3HVzLEgnX7xu1KSBNsi38vRiunA==)
23. [claude.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4L1Z18ANVFZznPaLQSlM-GJOtKKpN_iheHC44ytUIUtVSFQ5kMGBPk33PqJ-dePHVA0pMNEjDfNMigK3f8dW0GFX1u88v6RV0TwfLJ_ygxEmWMHET5ukZjFT7q_L8Kzzec66hoArIMYJw3c1moA==)
24. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpsvJXSXOq3QfOC-j8AXPxnFfbIf7mlHE_hsGBOuFbcTLQC1by_uOl4XwnUXVBAj04e__deOvxSyOzEErQU07Md9YZUzo64ZkgVyR5RVcrmD4ZBM7QEer4-GVWxeSIp5Lw88OIUwOSspbP8g3ArehRwEiJtCB0hWFQWCwRf_AuV6344Jm8CJq7zAgTU_HHtktRoMGVPaJgOUjOqsK2EV7G)
25. [amazon.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnaW9ZfPVPeU6j_CYNqk58IyY59lvGc8DvxajjtALnAthzyMqbfASjRmALOV00P7H5aqEGN-uE9M_PuTj7a7hn_MyMS7t451k3uIg8l9ojPlUgmRYpNKMXp2_ZUsASPNxZU0QPgM0wQMn7zDfIJ6c43i0KO6mrhJSqGgOLSoP-devqc2jTJFC16pbna1VOmlOgelaGsuWqG6Twn5BEDqIq6wCMJfR-35eCE0Rsd1GFKHEA3jI=)
26. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3j3PXqiV92G17HAAZcW6D4Vl7df10BP930J0Hjg7ypI5k3_TWQneksWuev7BY1nJzGhufiZqZob2pYq5_i-4oDrqx58M49h7pfXBipeoFZMKBdfXdJk8o7ULue38HD4pluRLOGdiGlK8XmXOQPblZqNjGduJA5sQ_VMq7oLReOTvB5HNPcZV7SOzX1S9t5aQubKyfqRfGIigq0PQ7oc6fiOMBmVk1X41aW_Fr-DcRORGSt--XJGIEpNM-6NsxomoL)
27. [claude.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAKeDviwL58SqSY-iPGDpNAhk9axSUBu1belcKlDwI6-ix7tfhRSYY0-v-TCM4xxRX1Fo5_0xXXsJgFselndUwXv7_kfIf14wxUUcz3vX1gF6G4h0bjH9Bq0z-)
28. [stevekinney.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXpujtgVfJj1Q8LPKMqRZbvsxFrZlV7Sx9kbgYBmjsP9cRLf08_I5QtYChdjdPnMBXsWngKy7Dl6yxEn_2IfYUf4BEeRqTljoiUIO31pKSk6pa4KOgNZjJiZs7sUDT0JZuQpOnLuUqbC5w_mE_GpHfbGTYqQQLMKgm-8w=)
29. [claudecode.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiOGdElWYjAtKZRW1CgijiHC9CC_8CW-BsHasVYdYOBW9LLySh9PIb4rDlEg77bTPsksbm3UabhAon-vvRQQl5kGvOjhziGYR_URnCCyvzaVnH-UXeLIxTMIYSqnI=)
30. [claude.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRw-qxeIEIxmxA8Ei-BT0kpX4_QmjSH_cP-BH9ofbqIj3CezTnbLmTC1TZBMf--4XxZG8HTr5t53ozgdHUeOEsJdTqbblhhLK_oNw7uIPYXDgTW-5DaJ0irY1Rs0ul9ZizGiM=)
31. [stevekinney.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2WJm4Fezw1GG253NC88ULDzRlfSudpB7j53-COo1vGC8ZlccnPQ1LIAWUx1N6ByGBHD0FFAqjkv8w5MLjYT5KKZ8tzNz6wQyl2mIO0WkrnRlZlrnurC63LdWrpnd9DNvY8mxxJRmUup0O9Xv1Hp8bhiY=)
32. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaiPmf6jLHZxXTvCfh5x6G7bcY7K7qwFLZKAtjybwosU3gax5rT_0fynhQPhFDpQLL87fJoMN_6e1dRXisGc6wUgMlUrMeF6efD0k63jV2SE73z7q804tUZPrKMiRV8_UpXZfescOcnX291pGFtwNRAzVQj2IupI0ZoPIOGfQZCtcC9pyW8SUVRL9m_pt93hxOinwnA12tb42yi8JQjg==)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpDigBbHYJpcbB_yTpfk7BBUHmiT9C0kuAXsmDXHLomfP95a6Sr5l3EQxA6arsL5KtJOmkSUQGr40ALYZgFkHEvgAGwnRz8O-goxjvFzpdQKoPdtUGCs4FwWelSG9B5sjD7YjvUtVtJ7ZoWw==)
34. [claude.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqLefiyX-pRvF3AD7V0Q7DevQCAseROhHq9oHUwSsmQWfkB7UDO8HMZxvACEMVWEwSn3p4thxsxqyJoFjq941dT6Vcg5ltoYEyVnC1IR0w1DRv7orrhCGHK_OMfRQF)
35. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEF4bKEUlj-78f97y0RGyEKebLrVyf2I-1lnZGDPfvQLKMHi2c2WWKmNFecHKsjuEBj09LTUZg7poMB_StN5G_lLGX_Xn5hyMdum_kZJlKC-NJ6ncM84QHEHjfw4sHPnENy)
36. [apidog.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjUEOaPNb07JZhLWTZwue-1J77PR24On2hve2EEI-f7QS6lQeN6ZFfSIN0LGFhSnpJhRRk3iIet4EStptWpboemXhYRrLIGuou8ye-9BfggrpYF4MZFYky)
37. [claude.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0SM6lOecqGz6ZVwD4l2trpIfP92djq3v8jI3rFGr6PUhtFdkPEymHKdLPiEGnVa3ZOJDUqZFLDIYKZssNPpWa-cplii7yXFkwEYh0dwWjb-BamQOuJFVapWnODwXxvSjjIKXy)
38. [arsturn.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0dD22ktfNfSx3a9JlnUarIp2N_kNrF01myP0T_SdSn2InSHPxzxRqJ6aSRMB586E97hGM3OApx-GhXKNwTCM8rWo1vC_OS7icnmVlNWRNiyPV_8HnXgWvbObjK2fHdqDsiYgsp7f0SQVumuRVqf2Y0v96TXnO6-4vPw6Q2KITITP64Asuj40qPA-Yuht708WtOGk=)
39. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELDsmsJuYBlEQWcL3wXXdQ3ZZfGGpWIOdYwGP_ZRzeaFCGnYyvKWNf4Ibeqhcizgk-dgxFj8GQa2ATy16mqvjLAi9ANM-Eos8JcORD8PgO-WLWB6BB7eV9hS6WYYMuD6ONi1x6hHMWcX8=)
40. [apidog.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHI8XIE1-pBuAVWkF-xIYAiLMJoQwfrFYxNzlpSJx2HYJOVhHa9HmNVCKcLSA-ZjCauVVlKIKgXfHVTGKB48FXlxCI7Vxhoy80zfjZ3NmtL6WqIgPX1FJlvDK0e1bMeC2k=)
41. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEI7yrRcRg3DmD6ztoL8ClGl51VK2pzpPnY4UnI8-Eu8FKE52-1yskdVk6qrQBTYcc-ieVjw_zqLDli-gL5zOp-0-DJk5Bj-7X7Ur_ODuZCBprPwvkGS8elqlv_hfX1MoZe6e46zp3FxpwXXeofINaZQl3tV-Tmo72veT_PXLMmq4Ll7-eMa02okUXi8PjChfk9NnVtEIJ3vNH2Bzw1gsPvtEDz)
42. [anthropic.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHM6eyZM47HNwbM_bbgwaaNFVztJMNZN_9BSMi0Z34rzYOXU2nD_uv5ZLGMQFk9B8nbLRnFIzuHl-NEW2wT1H0w2veBpC6YYRZIXovOuIrYlC8qXUCN-lUt4cOiZ5IfjnYUpt5onKa_YsjkHwA9)
43. [dev.to](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBC05GAbfyCL0yiSxRN8wSUy35CTwqgHxxU36RP61s6ksPp7QNWKAKX-6d_kPXqJ3sb_GYR2DtYh2dqYisX7vGQAglZGqI5Z8UD4wcP5w-u7kSJSK5XQlGmeVgqbQYrM4-wNGf0eBdzImxE-dFZFu85jCJyH1FAAavQGhrOz2_ZMWnq1wMdZh1_4MmQmuifnWSuA==)
44. [claude.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6OsVicyWXUyv6PEsghgQ0ydBF8HVDQqDDpjsKpR6oOm8DCoKHfFuEvYTUhAFEBSYKGIxEH-ywLRTKTm1BBLsERAzuISlzx6A6_mpctauT4ZHSNfd_2HkwqwriZ5UyTwF8vu4=)
