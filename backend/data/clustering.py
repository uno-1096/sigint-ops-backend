from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def cluster_stories(items, threshold=0.65):
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
        # Pick primary — prefer LIVE tag, then highest severity
        def score(item):
            s = 0
            if 'LIVE' in item.get('tags', []): s += 100
            if item.get('severity') == 'critical': s += 10
            if item.get('severity') == 'elevated': s += 5
            return s
        cluster.sort(key=score, reverse=True)
        primary = dict(cluster[0])
        sources = list(set(c["source"] for c in cluster))
        primary["coverage_count"] = len(cluster)
        primary["coverage_sources"] = sources[:5]
        result.append(primary)

    # Sort by severity
    priority = {"critical": 0, "elevated": 1, "monitor": 2}
    result.sort(key=lambda x: priority.get(x.get("severity"), 2))
    return result
