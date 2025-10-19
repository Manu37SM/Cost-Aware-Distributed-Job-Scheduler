
from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class Job:
    jobId: str
    priority: int  # 1-10 (10 highest)
    cpu: float
    memory: float
    slaType: str  # BATCH or LATENCY_SENSITIVE
    maxTolerableCost: float

@dataclass
class Node:
    nodeId: str
    capacity_cpu: float
    capacity_mem: float
    allocatable_cpu: float
    allocatable_mem: float
    type: str  # ON_DEMAND or SPOT
    cost_per_min: float
    gpu_type: Optional[str] = None

def score_job_node(job: Job, node: Node) -> float:
    import math
    # Reject if insufficient resources
    if node.allocatable_cpu < job.cpu or node.allocatable_mem < job.memory:
        return -math.inf

    # Reject if node cost exceeds maxTolerableCost
    if node.cost_per_min > job.maxTolerableCost:
        return -math.inf

    # Base fit score (1 = perfect fit)
    cpu_fit = 1 - ((node.allocatable_cpu - job.cpu) / node.capacity_cpu)
    mem_fit = 1 - ((node.allocatable_mem - job.memory) / node.capacity_mem)
    fit_score = (cpu_fit + mem_fit) / 2

    # Cost factor: cheaper = higher score, capped at 1.0
    cost_factor = min(1.0, job.maxTolerableCost / max(node.cost_per_min, 1e-6))

    # Priority multiplier
    priority_mult = 1 + (job.priority / 10)

    # SPOT risk: if latency-sensitive, heavy penalty
    if node.type == "SPOT" and job.slaType == "LATENCY_SENSITIVE":
        spot_penalty = 0.3
    else:
        spot_penalty = 1.0

    return fit_score * cost_factor * priority_mult * spot_penalty


def select_best_node(job: Job, nodes: List[Node]) -> Optional[Node]:
    best = None
    best_score = -math.inf
    for n in nodes:
        s = score_job_node(job, n)
        if s > best_score:
            best_score = s
            best = n
    return best if best_score > -math.inf else None
