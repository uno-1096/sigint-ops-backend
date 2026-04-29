
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def cluster_stories(items, threshold=0.45):
    """Group similar headlines together and add coverage count"""
    clusters = []
    used = set()

    for i, item in enumerate(items):
        if i in used:
            continue
        cluster = [item]
        used.add(i)
        for j, other in enumerate(items):
            if j in used or j == i:
                continue
            if similarity(item["title"], other["title"]) > threshold:
                cluster.append(other)
                used.add(j)
        clusters.append(cluster)

    result = []
    for cluster in clusters:
        primary = cluster[0]
        if len(cluster) > 1:
            sources = list(set(c["source"] for c in cluster))
            primary = dict(primary)
            primary["coverage_count"] = len(cluster)
            primary["coverage_sources"] = sources[:5]
        else:
            primary = dict(primary)
            primary["coverage_count"] = 1
            primary["coverage_sources"] = [primary["source"]]
        result.append(primary)

    return result
