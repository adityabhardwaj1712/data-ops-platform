"""
Quality Rules Engine (FREE)
Validate data quality with customizable rules
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of validation rules."""
    NOT_NULL = "not_null"
    REGEX = "regex"
    RANGE = "range"
    LENGTH = "length"
    UNIQUE = "unique"
    CUSTOM = "custom"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    field: str
    rule_type: str
    passed: bool
    message: str
    value: Any = None


class ValidationRule:
    """Base validation rule."""
    
    def __init__(self, field: str, rule_type: RuleType):
        self.field = field
        self.rule_type = rule_type
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate a value. Override in subclasses."""
        raise NotImplementedError


class NotNullRule(ValidationRule):
    """Check if value is not null."""
    
    def __init__(self, field: str):
        super().__init__(field, RuleType.NOT_NULL)
    
    def validate(self, value: Any) -> ValidationResult:
        passed = value is not None and value != ""
        return ValidationResult(
            field=self.field,
            rule_type=self.rule_type.value,
            passed=passed,
            message=f"{self.field} must not be null" if not passed else "OK",
            value=value
        )


class RegexRule(ValidationRule):
    """Check if value matches regex pattern."""
    
    def __init__(self, field: str, pattern: str, description: str = ""):
        super().__init__(field, RuleType.REGEX)
        self.pattern = pattern
        self.description = description or f"Must match pattern: {pattern}"
    
    def validate(self, value: Any) -> ValidationResult:
        if value is None:
            return ValidationResult(
                field=self.field,
                rule_type=self.rule_type.value,
                passed=False,
                message=f"{self.field} is null",
                value=value
            )
        
        passed = bool(re.match(self.pattern, str(value)))
        return ValidationResult(
            field=self.field,
            rule_type=self.rule_type.value,
            passed=passed,
            message=self.description if not passed else "OK",
            value=value
        )


class RangeRule(ValidationRule):
    """Check if numeric value is within range."""
    
    def __init__(self, field: str, min_val: Optional[float] = None, max_val: Optional[float] = None):
        super().__init__(field, RuleType.RANGE)
        self.min_val = min_val
        self.max_val = max_val
    
    def validate(self, value: Any) -> ValidationResult:
        try:
            num_val = float(value)
            
            if self.min_val is not None and num_val < self.min_val:
                return ValidationResult(
                    field=self.field,
                    rule_type=self.rule_type.value,
                    passed=False,
                    message=f"{self.field} must be >= {self.min_val}",
                    value=value
                )
            
            if self.max_val is not None and num_val > self.max_val:
                return ValidationResult(
                    field=self.field,
                    rule_type=self.rule_type.value,
                    passed=False,
                    message=f"{self.field} must be <= {self.max_val}",
                    value=value
                )
            
            return ValidationResult(
                field=self.field,
                rule_type=self.rule_type.value,
                passed=True,
                message="OK",
                value=value
            )
        
        except (ValueError, TypeError):
            return ValidationResult(
                field=self.field,
                rule_type=self.rule_type.value,
                passed=False,
                message=f"{self.field} must be a number",
                value=value
            )


class LengthRule(ValidationRule):
    """Check if string length is within range."""
    
    def __init__(self, field: str, min_len: Optional[int] = None, max_len: Optional[int] = None):
        super().__init__(field, RuleType.LENGTH)
        self.min_len = min_len
        self.max_len = max_len
    
    def validate(self, value: Any) -> ValidationResult:
        if value is None:
            length = 0
        else:
            length = len(str(value))
        
        if self.min_len is not None and length < self.min_len:
            return ValidationResult(
                field=self.field,
                rule_type=self.rule_type.value,
                passed=False,
                message=f"{self.field} must be at least {self.min_len} characters",
                value=value
            )
        
        if self.max_len is not None and length > self.max_len:
            return ValidationResult(
                field=self.field,
                rule_type=self.rule_type.value,
                passed=False,
                message=f"{self.field} must be at most {self.max_len} characters",
                value=value
            )
        
        return ValidationResult(
            field=self.field,
            rule_type=self.rule_type.value,
            passed=True,
            message="OK",
            value=value
        )


@dataclass
class QualityReport:
    """Quality validation report."""
    total_checks: int
    passed: int
    failed: int
    pass_rate: float
    failures: List[ValidationResult]
    
    def is_valid(self) -> bool:
        """Check if all validations passed."""
        return self.failed == 0


class QualityRulesEngine:
    """
    Data quality validation engine.
    
    Features:
    - Multiple rule types
    - Custom rules
    - Batch validation
    - Quality scoring
    """
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule):
        """Add a validation rule."""
        self.rules.append(rule)
        logger.debug(f"Added rule: {rule.rule_type.value} for {rule.field}")
    
    def add_not_null(self, field: str):
        """Add not-null rule."""
        self.add_rule(NotNullRule(field))
    
    def add_regex(self, field: str, pattern: str, description: str = ""):
        """Add regex validation rule."""
        self.add_rule(RegexRule(field, pattern, description))
    
    def add_range(self, field: str, min_val: float = None, max_val: float = None):
        """Add range validation rule."""
        self.add_rule(RangeRule(field, min_val, max_val))
    
    def add_length(self, field: str, min_len: int = None, max_len: int = None):
        """Add length validation rule."""
        self.add_rule(LengthRule(field, min_len, max_len))
    
    def validate(self, data: Dict[str, Any]) -> QualityReport:
        """
        Validate data against all rules.
        
        Args:
            data: Data to validate
        
        Returns:
            Quality report
        """
        results = []
        
        for rule in self.rules:
            value = data.get(rule.field)
            result = rule.validate(value)
            results.append(result)
        
        failures = [r for r in results if not r.passed]
        passed = len(results) - len(failures)
        
        return QualityReport(
            total_checks=len(results),
            passed=passed,
            failed=len(failures),
            pass_rate=passed / len(results) if results else 1.0,
            failures=failures
        )
    
    def validate_batch(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate entire dataset.
        
        Returns:
            Aggregate quality metrics
        """
        all_failures = []
        total_rows = len(dataset)
        valid_rows = 0
        
        for row in dataset:
            report = self.validate(row)
            if report.is_valid():
                valid_rows += 1
            else:
                all_failures.extend(report.failures)
        
        return {
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "invalid_rows": total_rows - valid_rows,
            "validity_rate": valid_rows / total_rows if total_rows > 0 else 0,
            "total_failures": len(all_failures),
            "failure_breakdown": self._breakdown_failures(all_failures)
        }
    
    def _breakdown_failures(self, failures: List[ValidationResult]) -> Dict[str, int]:
        """Break down failures by field and rule type."""
        breakdown = {}
        for failure in failures:
            key = f"{failure.field}:{failure.rule_type}"
            breakdown[key] = breakdown.get(key, 0) + 1
        return breakdown


# Pre-defined rule sets for common data types
class CommonRules:
    """Common validation rules."""
    
    @staticmethod
    def email(field: str = "email") -> RegexRule:
        """Email validation rule."""
        return RegexRule(
            field,
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "Must be a valid email address"
        )
    
    @staticmethod
    def url(field: str = "url") -> RegexRule:
        """URL validation rule."""
        return RegexRule(
            field,
            r'^https?://[^\s]+$',
            "Must be a valid URL"
        )
    
    @staticmethod
    def phone(field: str = "phone") -> RegexRule:
        """Phone number validation rule."""
        return RegexRule(
            field,
            r'^\+?[\d\s\-\(\)]+$',
            "Must be a valid phone number"
        )
    
    @staticmethod
    def positive_number(field: str) -> RangeRule:
        """Positive number validation."""
        return RangeRule(field, min_val=0)
