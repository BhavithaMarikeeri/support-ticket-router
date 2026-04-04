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
        "resolution_keywords": ["refund", "billing team", "invoice", "payment", "charge"]
    },
    {
        "task_id": "task_medium",
        "difficulty": "medium",
        "ticket_id": "T002",
        "customer_name": "Divya",
        "message": "The mobile app crashes every time I open the settings page. Tried reinstalling but still broken.",
        "correct_category": "Technical",
        "correct_priority": "high",
        "resolution_keywords": ["technical team", "troubleshoot", "update", "restart", "reset", "fix"]
    },
    {
        "task_id": "task_hard",
        "difficulty": "hard",
        "ticket_id": "T003",
        "customer_name": "Meera",
        "message": "I changed my plan last week but I'm not sure if the new price is correct. Also how do I download my invoice?",
        "correct_category": "Billing",
        "correct_priority": "medium",
        "resolution_keywords": ["technical team", "troubleshoot", "update", "restart", "reset", "fix", "cache", "clear", "device", "reinstall"]
    },
]

def compute_reward(task: dict, action: SupportTicketRouterAction) -> float:
    score = 0.0

    if action.category == task["correct_category"]:
        score += 0.4

    if action.priority == task["correct_priority"]:
        score += 0.3

    res = action.suggested_resolution.lower()
    matches = sum(1 for k in task["resolution_keywords"] if k in res)
    score += min(0.3, matches * 0.1)

    return round(score, 2)


class SupportTicketRouterEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task = TASKS[0]

    def reset(self) -> SupportTicketRouterObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task = TASKS[0]

        return SupportTicketRouterObservation(
            ticket_id=self._current_task["ticket_id"],
            customer_name=self._current_task["customer_name"],
            message=self._current_task["message"],
            difficulty=self._current_task["difficulty"],
            done=False,
            reward=0.0,
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