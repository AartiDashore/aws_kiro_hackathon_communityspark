{
  "name": "Deal Expiry Reminder",
  "version": "1.0.0",
  "description": "When a new deal is created, remind the developer to verify the background expiry task is scheduled.",
  "when": {
    "type": "fileEdited",
    "patterns": ["routers/deals.py"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "The deals router was just modified. Check that every POST /api/deals route call includes a BackgroundTasks parameter and calls background_tasks.add_task(expire_deal_after_delay, ...). If it does not, flag the issue and suggest the fix."
  }
}