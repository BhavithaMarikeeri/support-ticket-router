from openenv.core.env_server.types import Action, Observation
from pydantic import Field
from typing import Optional

class SupportTicketRouterAction(Action):
    category: str = Field(..., description="Billing / Technical / General")
    priority: str = Field(..., description="low / medium / high")
    suggested_resolution: str = Field(..., description="Short resolution sentence")

class SupportTicketRouterObservation(Observation):
    ticket_id: str = Field(default="", description="Ticket ID")
    customer_name: str = Field(default="", description="Customer name")
    message: str = Field(default="", description="Customer support message")
    difficulty: str = Field(default="", description="Task difficulty level")