from typing import Any, Dict


class PromptManager:
    """Manages prompt templates and variable injection for agents."""

    _templates: Dict[str, str] = {
        "opportunity_analysis": "Analyze the following business intelligence data and determine the opportunity score: {data}",
        "proposal_generation": "Generate a proposal for {business_name} using the following opportunity insights: {insights}",
        "outreach_generation": "Write a personalized cold email for {contact_name} at {business_name} addressing this pain point: {pain_point}",
    }

    @classmethod
    def get_prompt(cls, template_name: str, **kwargs: Any) -> str:
        """Retrieve a template and format it with the provided kwargs."""
        if template_name not in cls._templates:
            raise ValueError(f"Template '{template_name}' not found.")
            
        template = cls._templates[template_name]
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required format variable {e} for template '{template_name}'")
