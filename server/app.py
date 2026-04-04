import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server.http_server import create_app
from models import SupportTicketRouterAction, SupportTicketRouterObservation
from server.support_ticket_router_environment import SupportTicketRouterEnvironment
from fastapi.responses import JSONResponse

app = create_app(
    SupportTicketRouterEnvironment,
    SupportTicketRouterAction,
    SupportTicketRouterObservation,
    env_name="support_ticket_router",
    max_concurrent_envs=1,
)

@app.get("/")
async def root():
    return JSONResponse({
        "environment": "support-ticket-router",
        "status": "ok",
        "tasks": ["task_easy", "task_medium", "task_hard"],
        "version": "1.0.0"
    })

def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()