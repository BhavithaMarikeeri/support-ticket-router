import os
import json
import requests
from openai import OpenAI

# ── Mandatory config variables ────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN", "")  # your HF token

ENV_URL = "http://127.0.0.1:8000"

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

TASKS = [
    {
        "task_id": "task_easy",
        "difficulty": "easy",
        "ticket": {"message": "I was charged twice for my subscription this month. Please refund."}
    },
    {
        "task_id": "task_medium",
        "difficulty": "medium",
        "ticket": {"message": "The mobile app crashes every time I open the settings page. Tried reinstalling but still broken."}
    },
    {
        "task_id": "task_hard",
        "difficulty": "hard",
        "ticket": {"message": "I changed my plan last week but I'm not sure if the new price is correct. Also how do I download my invoice?"}
    },
]

def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error=None):
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def agent_decide(message: str) -> dict:
    prompt = f"""You are a customer support routing agent.

Customer message: "{message}"

Respond with ONLY this JSON, no explanation:
{{
  "category": "Billing" or "Technical" or "General",
  "priority": "low" or "medium" or "high",
  "suggested_resolution": "a short sentence"
}}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.2
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def run_all_tasks():
    all_scores = []

    for task in TASKS:
        task_id = task["task_id"]
        rewards = []

        log_start(task=task_id, env="support_ticket_router", model=MODEL_NAME)

        try:
            action = agent_decide(task["ticket"]["message"])
            action_str = json.dumps(action)

            step_resp = requests.post(
                f"{ENV_URL}/step",
                json={"action": action}
            )
            result = step_resp.json()
            reward = result.get("reward", 0.0)
            rewards.append(reward)

            log_step(step=1, action=action_str, reward=reward, done=True)
            log_end(success=reward >= 0.5, steps=1, score=reward, rewards=rewards)

        except Exception as e:
            log_step(step=1, action="null", reward=0.00, done=True, error=str(e))
            log_end(success=False, steps=1, score=0.0, rewards=[0.0])

        all_scores.append(rewards[0] if rewards else 0.0)
        print()

    avg = round(sum(all_scores) / len(all_scores), 2)
    print(f"Average score: {avg}")

if __name__ == "__main__":
    run_all_tasks()