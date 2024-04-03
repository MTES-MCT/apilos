from typing import Any


class Stepper:
    steps: list[str]

    def __init__(self, steps) -> None:
        self.steps = steps

    def get_form_step(self, step_number: int) -> dict[str, Any] | None:
        count_steps = len(self.steps)
        if step_number < 1 or step_number > count_steps:
            return None
        return {
            "number": step_number,
            "total": count_steps,
            "current_step": self.steps[step_number - 1],
            "next_step": self.steps[step_number] if step_number < count_steps else None,
        }
