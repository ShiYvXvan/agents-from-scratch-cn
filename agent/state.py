"""
Agent 状态管理。

状态是显式的、可检查的、可修改的。
它不隐藏在对话历史或神秘的上下文中。
"""


class AgentState:
    """
    表示 agent 的当前状态。

    随着课程的推进，此类会逐步增长：
    - 第 06 课：基础状态（steps, done）
    - 第 07 课：添加记忆跟踪
    - 第 08 课：添加规划状态
    - 第 09 课：添加执行状态
    - 第 10 课：添加依赖跟踪
    """

    def __init__(self):
        """初始化一个新的 agent 状态。"""
        self.steps = 0
        self.done = False
        self.current_plan = None
        self.last_action = None

    def increment_step(self):
        """步骤计数器加一。"""
        self.steps += 1

    def mark_done(self):
        """将 agent 的任务标记为已完成。"""
        self.done = True

    def reset(self):
        """为新的任务重置状态。"""
        self.steps = 0
        self.done = False
        self.current_plan = None
        self.last_action = None

    def to_dict(self) -> dict:
        """
        将状态转换为字典，用于序列化或提示词。

        Returns:
            状态的字典表示
        """
        return {
            "steps": self.steps,
            "done": self.done,
            "current_plan": self.current_plan,
            "last_action": self.last_action,
        }

    def __repr__(self) -> str:
        """状态的字符串表示。"""
        return f"AgentState(steps={self.steps}, done={self.done})"
