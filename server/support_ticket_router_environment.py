from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import SupportTicketRouterAction, SupportTicketRouterObservation
except ImportError:
    from models import SupportTicketRouterAction, SupportTicketRouterObservation

TASKS = [
    {
        "task_id": "task_easy",
        "difficulty": "easy",
        "ticket_id": "T001",
        "customer_name": "Amit",
        "message": "I was charged twice for my subscription this month. Please refund.",
        "correct_category": "Billing",
        "correct_priority": "high",
        "resolution_keywords": ["refund", "billing", "invoice", "payment", "charge", "duplicate"]
    },
    {
        "task_id": "task_medium",
        "difficulty": "medium",
        "ticket_id": "T002",
        "customer_name": "Divya",
        "message": "The mobile app crashes every time I open the settings page. Tried reinstalling but still broken.",
        "correct_category": "Technical",
        "correct_priority": "high",
        "resolution_keywords": ["technical", "troubleshoot", "update", "restart", "reset", "fix", "crash", "bug"]
    },
    {
        "task_id": "task_hard",
        "difficulty": "hard",
        "ticket_id": "T003",
        "customer_name": "Meera",
        "message": "I changed my plan last week but I'm not sure if the new price is correct. Also how do I download my invoice?",
        "correct_category": "Billing",
        "correct_priority": "medium",
        "resolution_keywords": ["invoice", "download", "plan", "price", "billing", "account", "subscription"]
    },
]

TASK_MAP = {t["task_id"]: t for t in TASKS}


def compute_reward(task: dict, action: SupportTicketRouterAction) -> float:
    # Base 0.05 guarantees score is NEVER 0.0
    # Max = 0.05 + 0.33 + 0.28 + 0.24 = 0.90, so NEVER reaches 1.0
    score = 0.05

    if action.category == task["correct_category"]:
        score += 0.33

    if action.priority == task["correct_priority"]:
        score += 0.28

    res = action.suggested_resolution.lower()
    matches = sum(1 for k in task["resolution_keywords"] if k in res)
    score += min(0.24, matches * 0.06)

    # Hard safety clamp — score always strictly inside (0, 1)
    score = max(0.01, min(0.99, score))

    return round(float(score), 4)


class SupportTicketRouterEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task = TASKS[0]

    def reset(self, task_id: str = None) -> SupportTicketRouterObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        if task_id and task_id in TASK_MAP:
            self._current_task = TASK_MAP[task_id]
        else:
            self._current_task = TASKS[0]

        return SupportTicketRouterObservation(
            ticket_id=self._current_task["ticket_id"],
            customer_name=self._current_task["customer_name"],
            message=self._current_task["message"],
            difficulty=self._current_task["difficulty"],
            done=False,
            reward=0.5,
        )

    def step(self, action: SupportTicketRouterAction) -> SupportTicketRouterObservation:
        self._state.step_count += 1
        reward = compute_reward(self._current_task, action)

        return SupportTicketRouterObservation(
            ticket_id=self._current_task["ticket_id"],
            customer_name=self._current_task["customer_name"],
            message=self._current_task["message"],
            difficulty=self._current_task["difficulty"],
            done=True,
            reward=reward,
            metadata={
                "task_id": self._current_task["task_id"],
                "score": reward,
                "category_correct": action.category == self._current_task["correct_category"],
                "priority_correct": action.priority == self._current_task["correct_priority"],
            }
        )

    @property
    def state(self) -> State:
        return self._state