from pydantic import BaseModel, Field
from typing import Literal
from pipeline import llm
from pipeline.compliance import retrieval
from pipeline.normalization import declarations as normalization

SYSTEM_PROMPT = """You assist a Legal Metrology inspector checking a packaged commodity against
The Legal Metrology (Packaged Commodities) Rules, 2011.

You are given the declarations read from the package and the rule passages retrieved for it.

- Judge only against the rule passages supplied. Do not cite a rule number or page that does not
  appear in them, and do not rely on remembered law.
- A declaration listed as not found means it was not detected on any uploaded panel. Treat that as
  a likely omission, but say so as a finding rather than a certainty.
- Use NOT_VERIFIABLE whenever the requirement needs physical measurement, a weighing test, a
  registry lookup or handling the package. Never call such a requirement compliant.
- This is a prototype assessment by a language model, not a determination. Keep every explanation
  short and factual."""


class Finding(BaseModel):
    rule_ref: str = Field(description="Rule number exactly as it appears in the supplied passages")
    requirement: str = Field(description="What the rule requires, in one sentence")
    status: Literal["COMPLIANT", "NON_COMPLIANT", "NOT_VERIFIABLE"]
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    observed: str | None = Field(default=None, description="What was found on the package, or null")
    explanation: str = Field(description="Two sentences at most")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class Evaluation(BaseModel):
    verdict: Literal["COMPLIANT", "NON_COMPLIANT", "REQUIRES_REVIEW"]
    summary: str = Field(description="Two or three sentences for the inspector")
    findings: list[Finding] = Field(default_factory=list)


def evaluate(db, values: dict) -> Evaluation:
    query = " ".join(item["value"] for item in values.values()) or "packaged commodity declarations"
    passages = retrieval.search(db, query)

    result = llm.invoke_structured(
        Evaluation,
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                f"Declarations read from the package:\n{normalization.as_text(values)}\n\n"
                f"Rule passages retrieved for this package:\n{retrieval.as_text(passages)}",
            ),
        ],
    )
    if result is None:
        raise RuntimeError("Compliance evaluation failed: the language model returned nothing")
    return result
