"""
Quality Validation Service
Dynamic schema validation using Pydantic
"""
from pydantic import BaseModel, Field, ValidationError, create_model
from typing import Any, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import json

from app.db.models import Task, AuditLog, TaskStatus


TYPE_MAP = {
    "str": str,
    "string": str,
    "int": int,
    "integer": int,
    "float": float,
    "number": float,
    "bool": bool,
    "boolean": bool
}


def build_dynamic_model(schema: Dict[str, Any]):
    """
    Build a Pydantic model dynamically from a schema definition.
    
    Schema format:
    {
        "field_name": {
            "type": "str|int|float|bool",
            "required": true|false,
            "min": number,
            "max": number,
            "regex": "pattern"
        }
    }
    """
    fields = {}
    
    for field_name, rules in schema.items():
        if isinstance(rules, str):
            # Simple type definition
            base_type = TYPE_MAP.get(rules, str)
            fields[field_name] = (base_type, ...)
        else:
            # Complex definition
            base_type = TYPE_MAP.get(rules.get("type", "str"), str)
            required = rules.get("required", True)
            
            annotated_type = base_type if required else Optional[base_type]
            default = ... if required else None
            
            constraints = {}
            if "min" in rules:
                constraints["ge"] = rules["min"]
            if "max" in rules:
                constraints["le"] = rules["max"]
            if "regex" in rules:
                constraints["pattern"] = rules["regex"]
            
            fields[field_name] = (
                annotated_type,
                Field(default=default, **constraints)
            )
    
    return create_model("DynamicSchema", **fields)


def validate(schema: Dict[str, Any], data: Dict[str, Any]) -> Tuple[bool, float, list]:
    """
    Validate data against dynamic schema.
    
    Returns:
        - is_valid: bool
        - confidence: float (0.0 - 1.0)
        - errors: list of error messages
    """
    try:
        Model = build_dynamic_model(schema)
        Model(**data)
        return True, 1.0, []
    except ValidationError as e:
        errors = json.loads(e.json())
        # Calculate confidence based on number of errors
        confidence = max(0.1, 1.0 - 0.15 * len(errors))
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in errors]
        return False, confidence, error_messages


async def run_quality_check(task_id: UUID, db: AsyncSession):
    """
    Run quality validation on a task's data.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        return
    
    # Get job schema
    from app.db.models import Job
    job_result = await db.execute(select(Job).where(Job.id == task.job_id))
    job = job_result.scalar_one_or_none()
    
    if not job:
        return
    
    # Validate
    is_valid, confidence, errors = validate(job.schema, task.payload)
    
    task.confidence = confidence
    
    if is_valid:
        task.status = TaskStatus.COMPLETED
        task.result = {"validated_data": task.payload, "confidence": confidence}
    else:
        task.status = TaskStatus.FAILED
        task.result = {"errors": errors, "confidence": confidence}
    
    # Audit log
    audit = AuditLog(
        task_id=task.id,
        action="quality_check_completed" if is_valid else "quality_check_failed",
        changes={"confidence": confidence, "errors": errors if errors else None}
    )
    db.add(audit)
    await db.commit()
    
    # Route to next step
    from app.services.router import route_task
    await route_task(task.id, db)
