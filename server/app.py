try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SupportTicketRouterAction, SupportTicketRouterObservation
from server.support_ticket_router_environment import SupportTicketRouterEnvironment

app = create_app(
    SupportTicketRouterEnvironment,
    SupportTicketRouterAction,
    SupportTicketRouterObservation,
    env_name="support_ticket_router",
    max_concurrent_envs=1,
)

def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

# Required for openenv validate
__all__ = ["app", "main"]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    main(port=args.port)