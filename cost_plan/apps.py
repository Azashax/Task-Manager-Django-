from django.apps import AppConfig


class CostPlanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cost_plan'

    def ready(self):
        import cost_plan.signals