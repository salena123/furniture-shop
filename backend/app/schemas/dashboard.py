from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    total_requests: int
    new_requests: int
    in_progress_requests: int
    contacted_requests: int
    measurement_scheduled_requests: int
    quote_prepared_requests: int
    completed_requests: int
    cancelled_requests: int
    requests_today: int
    unassigned_requests: int
    assigned_to_me: int
    total_products: int
    active_products: int
