---
title: Support Ticket Router
emoji: 🎫
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: apache-2.0
---

# Customer Support Ticket Router

An OpenEnv environment where an AI agent reads customer support tickets
and routes them to the correct department with priority and resolution.

## Live Demo
- API: https://Bhavitha12345566-support-ticket-router.hf.space
- Interactive Docs: https://Bhavitha12345566-support-ticket-router.hf.space/docs
- Health Check: https://Bhavitha12345566-support-ticket-router.hf.space/health

## Action Space
POST /step with JSON:
{"category": "Billing/Technical/General", "priority": "low/medium/high", "suggested_resolution": "..."}

## Observation Space
{ticket_id, customer_name, message, difficulty}

## Reward
- Category correct: +0.4
- Priority correct: +0.3
- Resolution keywords: up to +0.3
- Total range: 0.0 to 1.0

## Tasks
- task_easy: Route a billing complaint correctly
- task_medium: Route a technical issue with correct priority
- task_hard: Handle an ambiguous billing ticket

## Setup
pip install -r server/requirements.txt
python server/app.py

## Run Inference
python inference.py

## Baseline Scores
- task_easy: 0.9
- task_medium: 0.7
- task_hard: 0.9
- Average: 0.83