
from scheduler import Job, Node, select_best_node
def test_high_priority_prefers_on_demand():
    job = Job('j1', priority=10, cpu=2, memory=2, slaType='LATENCY_SENSITIVE', maxTolerableCost=100)
    nodes = [
        Node('spot1',4,8,4,8,'SPOT',0.1),
        Node('ond1',4,8,4,8,'ON_DEMAND',1.0),
    ]
    best = select_best_node(job, nodes)
    assert best.nodeId == 'ond1'

def test_low_priority_cost_sensitive_waits():
    job = Job('j2', priority=1, cpu=8, memory=8, slaType='BATCH', maxTolerableCost=0.01)
    nodes = [
        Node('cheap',16,32,16,32,'ON_DEMAND',5.0)
    ]
    best = select_best_node(job, nodes)
    assert best is None or best.cost_per_min <= job.maxTolerableCost
