import json
import re
import uuid
from collections import defaultdict, deque
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Sequence

from llm_config import get_active_user_llm_config


MAX_KEYWORDS_TOTAL = 160
LLM_CLUSTER_SIZE = 24
LLM_RETRY_ATTEMPTS = 2
EDGE_SIMILARITY_THRESHOLD = 0.23
MAX_EDGE_COUNT_PER_NODE = 5
DEFAULT_LEVEL = 0
FALLBACK_CLUSTER_NAME = "Keyword Cluster"


PUNCTUATION_RE = re.compile(r"[\u200c\W_]+", re.UNICODE)


class MindMapGenerationError(Exception):
    """Raised when LLM generated payload cannot be normalized."""


def _normalize_keywords(keywords: Sequence[str]) -> List[str]:
    normalized: List[str] = []
    seen = set()
    for value in keywords:
        text = (value or "").strip()
        if not text:
            continue
        low = text.lower()
        if low in seen:
            continue
        seen.add(low)
        normalized.append(text)
        if len(normalized) >= MAX_KEYWORDS_TOTAL:
            break
    return normalized


def _tokenize(text: str) -> List[str]:
    parts = re.split(r"\s+", (text or "").strip())
    return [part.lower() for part in parts if len(part) > 1]


def _jaccard(a: str, b: str) -> float:
    a_tokens = set(_tokenize(a))
    b_tokens = set(_tokenize(b))
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


def _containment(a: str, b: str) -> bool:
    a_tokens = set(_tokenize(a))
    b_tokens = set(_tokenize(b))
    return bool(a_tokens) and bool(b_tokens) and b_tokens.issubset(a_tokens)


def _sequence_ratio(a: str, b: str) -> float:
    a_clean = _clean(a)
    b_clean = _clean(b)
    if not a_clean or not b_clean:
        return 0.0
    return SequenceMatcher(None, a_clean, b_clean).ratio()


def _clean(text: str) -> str:
    return re.sub(PUNCTUATION_RE, " ", (text or "").lower()).strip()


def _infer_search_intent(keyword: str) -> str:
    text = (keyword or "").lower()
    if any(token in text for token in ["خرید", "قیمت", "فروش", "فهرست قیمت", "best", "buy", "price", "service"]):
        return "commercial"
    if any(token in text for token in ["آموزش", "آموزشی", "نحوه", "چطور", "راهنما", "how", "learn", "tutorial"]):
        return "informational"
    if any(token in text for token in ["دقیق", "تحقیق", "بررسی", "analysis", "تحلیل", "راستی", "compare"]):
        return "investigational"
    if any(token in text for token in ["ورود", "ورود به", "صفحه", "site", "login", "about"]):
        return "navigational"
    return "informational"


def _build_clusters(keywords: Sequence[str], max_size: int = LLM_CLUSTER_SIZE) -> List[List[str]]:
    remaining = list(keywords)
    clusters: List[List[str]] = []
    while remaining:
        seed = remaining.pop(0)
        cluster = [seed]
        leftovers = []
        for candidate in remaining:
            score = max(
                _jaccard(seed, candidate),
                _sequence_ratio(seed, candidate),
                0.45 if _containment(seed, candidate) or _containment(candidate, seed) else 0.0,
            )
            if score >= 0.25 and len(cluster) < max_size:
                cluster.append(candidate)
            else:
                leftovers.append(candidate)
        remaining = leftovers
        clusters.append(cluster)
    return clusters


def _node_id(base: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, base.lower()))


def _extract_json(text: str) -> Dict[str, Any]:
    if not isinstance(text, str):
        raise MindMapGenerationError("LLM response is not a text string.")

    fenced = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    payload = fenced.group(1).strip() if fenced else text.strip()
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise MindMapGenerationError("LLM output root must be JSON object.")
    return data


def _normalize_node(raw_node: Dict[str, Any], fallback_cluster: str) -> Dict[str, Any]:
    keyword = (raw_node.get("keyword") or "").strip()
    if not keyword:
        raise MindMapGenerationError("Node keyword is required.")

    node = {
        "id": str(raw_node.get("id") or _node_id(keyword)),
        "keyword": keyword,
        "type": (str(raw_node.get("type") or "leaf").strip().lower() or "leaf"),
        "level": int(raw_node.get("level") or 0) if int(raw_node.get("level") or 0) >= 0 else DEFAULT_LEVEL,
        "cluster": str(raw_node.get("cluster") or fallback_cluster),
        "topic": str(raw_node.get("topic") or fallback_cluster),
        "search_intent": str(raw_node.get("search_intent") or _infer_search_intent(keyword)),
        "parent_id": raw_node.get("parent_id"),
        "cluster_strength": float(raw_node.get("cluster_strength") or 1.0),
    }
    return node


def _normalize_edge(raw_edge: Dict[str, Any]) -> Dict[str, Any]:
    source = (raw_edge.get("source") or "").strip()
    target = (raw_edge.get("target") or "").strip()
    if not source or not target:
        raise MindMapGenerationError("Each edge must have source and target.")

    relationship = (str(raw_edge.get("relationship") or "parent-child").strip() or "parent-child").lower()
    confidence = raw_edge.get("confidence", 1.0)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 1.0
    confidence = max(0.0, min(1.0, confidence))
    return {
        "source": source,
        "target": target,
        "relationship": relationship,
        "confidence": confidence,
    }


def _normalize_payload(payload: Dict[str, Any], fallback_cluster: str) -> Dict[str, Any]:
    raw_nodes = payload.get("nodes")
    raw_edges = payload.get("edges", [])
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise MindMapGenerationError("LLM output must contain nodes.")
    if not isinstance(raw_edges, list):
        raw_edges = []

    nodes: List[Dict[str, Any]] = []
    keyword_to_id: Dict[str, str] = {}
    used_ids = set()

    for raw_node in raw_nodes:
        if not isinstance(raw_node, dict):
            raise MindMapGenerationError("Invalid node object.")
        node = _normalize_node(raw_node, fallback_cluster)
        normalized_keyword = node["keyword"].lower()
        if normalized_keyword in keyword_to_id:
            node["id"] = _node_id(f"{node['id']}-{normalized_keyword}-{len(nodes)}")
        if node["id"] in used_ids:
            node["id"] = _node_id(f"{node['id']}-{len(nodes)}")
        keyword_to_id[normalized_keyword] = node["id"]
        used_ids.add(node["id"])
        nodes.append(node)

    edges: List[Dict[str, Any]] = []
    for raw_edge in raw_edges:
        if not isinstance(raw_edge, dict):
            continue
        edge = _normalize_edge(raw_edge)
        source = edge["source"]
        target = edge["target"]
        source_id = keyword_to_id.get(source.lower(), source)
        target_id = keyword_to_id.get(target.lower(), target)
        source_exists = any(node["id"] == source_id for node in nodes)
        target_exists = any(node["id"] == target_id for node in nodes)
        if not source_exists or not target_exists or source_id == target_id:
            continue
        edge["source"] = source_id
        edge["target"] = target_id
        edges.append(edge)

    return {"nodes": nodes, "edges": edges}


def _semantic_score(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    return max(
        _jaccard(a["keyword"], b["keyword"]),
        _sequence_ratio(a["keyword"], b["keyword"]),
        0.42 if _containment(a["keyword"], b["keyword"]) or _containment(b["keyword"], a["keyword"]) else 0.0,
    )


def _build_edge_candidates(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for child in nodes:
        best_parent = None
        best_score = 0.0
        for parent in nodes:
            if parent["id"] == child["id"]:
                continue
            score = _semantic_score(parent, child)
            if score > best_score:
                best_score = score
                best_parent = parent
        if best_parent and best_score >= EDGE_SIMILARITY_THRESHOLD:
            candidates.append({
                "source": best_parent["id"],
                "target": child["id"],
                "relationship": "parent-child",
                "confidence": best_score,
            })
    return candidates


def _removes_cycle(parent_map: Dict[str, str], source: str, target: str) -> bool:
    visited = set()
    cursor = source
    while cursor in parent_map and cursor not in visited:
        visited.add(cursor)
        if cursor == target:
            return False
        cursor = parent_map[cursor]
    return True


def _build_parent_tree(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    node_ids = {node["id"] for node in nodes}
    parent_edges: Dict[str, Dict[str, Any]] = {}
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        if source not in node_ids or target not in node_ids:
            continue
        edge_confidence = float(edge.get("confidence") or 0.0)
        if target in parent_edges and edge_confidence <= float(parent_edges[target].get("confidence", 0.0)):
            continue
        if not _removes_cycle({child: parent for child, parent in [(e["target"], e["source"]) for e in parent_edges.values()]}, source, target):
            continue
        parent_edges[target] = {
            "source": source,
            "target": target,
            "relationship": edge.get("relationship") or "parent-child",
            "confidence": edge_confidence,
        }

    child_to_parent: Dict[str, str] = {
        edge["target"]: edge["source"] for edge in parent_edges.values()
    }
    children_by_parent: Dict[str, List[str]] = defaultdict(list)
    for child, parent in child_to_parent.items():
        children_by_parent[parent].append(child)

    for node in nodes:
        parent_id = child_to_parent.get(node["id"])
        node["parent_id"] = parent_id

    ordered_nodes = _assign_levels_and_types(nodes, children_by_parent, parent_map=child_to_parent)
    normalized_edges = list(parent_edges.values())
    return ordered_nodes, normalized_edges


def _assign_levels_and_types(
    nodes: List[Dict[str, Any]],
    children_by_parent: Dict[str, List[str]],
    parent_map: Dict[str, str],
) -> List[Dict[str, Any]]:
    node_map = {node["id"]: node for node in nodes}
    roots = [node["id"] for node in nodes if node["id"] not in parent_map]

    for node in nodes:
        node["level"] = DEFAULT_LEVEL
        node["type"] = "root" if node["id"] in roots else "leaf"

    queue = deque(roots)
    while queue:
        current_id = queue.popleft()
        current = node_map[current_id]
        current_level = int(current.get("level", DEFAULT_LEVEL))
        for child_id in children_by_parent.get(current_id, []):
            child = node_map[child_id]
            child["parent_id"] = current_id
            child["type"] = "child"
            child["level"] = max(current_level + 1, int(child.get("level", DEFAULT_LEVEL)))
            queue.append(child_id)

    for node in nodes:
        if node["parent_id"] and node["type"] == "leaf":
            node["type"] = "child"
        if not node["parent_id"] and children_by_parent.get(node["id"]):
            node["type"] = "parent"
        if not node["type"]:
            node["type"] = "leaf"
    return nodes


def _filter_edges(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    node_by_id = {node["id"]: node for node in nodes}
    kept: List[Dict[str, Any]] = []
    parent_count = defaultdict(int)
    for edge in sorted(edges, key=lambda item: item.get("confidence", 0.0), reverse=True):
        source = edge["source"]
        target = edge["target"]
        if source not in node_by_id or target not in node_by_id or source == target:
            continue
        if parent_count[target] >= 1:
            continue
        score = max(
            _jaccard(node_by_id[source]["keyword"], node_by_id[target]["keyword"]),
            _sequence_ratio(node_by_id[source]["keyword"], node_by_id[target]["keyword"]),
        )
        if score < EDGE_SIMILARITY_THRESHOLD and float(edge.get("confidence", 0.0)) < 0.6:
            continue
        kept.append(edge)
        parent_count[target] += 1
        if len([e for e in kept if e["source"] == source]) >= MAX_EDGE_COUNT_PER_NODE:
            continue
    return kept


def _fallback_hierarchy(cluster: List[str], cluster_label: str) -> Dict[str, Any]:
    nodes = [
        {
            "id": _node_id(keyword),
            "keyword": keyword,
            "type": "leaf",
            "level": 0,
            "cluster": cluster_label,
            "topic": cluster_label,
            "search_intent": _infer_search_intent(keyword),
            "parent_id": None,
            "cluster_strength": 1.0,
        }
        for keyword in cluster
    ]
    node_map = {node["id"]: node for node in nodes}
    candidate_edges = _build_edge_candidates(nodes)
    candidate_edges = _filter_edges(nodes, candidate_edges)
    children_by_parent = defaultdict(list)
    for edge in candidate_edges:
        children_by_parent[edge["source"]].append(edge["target"])
    for node in nodes:
        node["type"] = "leaf"
        node["level"] = 0

    ordered_nodes = _assign_levels_and_types(nodes, children_by_parent, {
        edge["target"]: edge["source"] for edge in candidate_edges
    })
    for node in ordered_nodes:
        node["cluster"] = cluster_label
        node["topic"] = cluster_label

    if not candidate_edges:
        for node in ordered_nodes:
            node["type"] = "root"
            node["level"] = 0
    return {"nodes": ordered_nodes, "edges": candidate_edges}


def _build_prompt(cluster: List[str], cluster_label: str) -> str:
    keyword_lines = "\n".join([f"- {keyword}" for keyword in cluster])
    return (
        "You are an SEO topic-clustering engine.\n"
        "From the keyword list below, build one strict JSON object for topic hierarchy in mind map format.\n"
        "Rules:\n"
        "1) Return only JSON with keys: nodes and edges.\n"
        "2) nodes item keys: id, keyword, level, type(parent|child|leaf|root), cluster, search_intent, topic, parent_id(optional)\n"
        "3) edges item keys: source, target, relationship(parent-child), confidence(0-1)\n"
        "4) Use valid IDs in nodes and edges references.\n"
        "5) Use weak relationship filtering by semantic fit; do not force links.\n"
        "6) Only connect a keyword to the most semantically fitting parent.\n"
        "7) Keep number of edges minimal and meaningful.\n\n"
        f"Cluster label: {cluster_label}\n"
        "Keywords:\n"
        f"{keyword_lines}\n\n"
        "Example output:\n"
        '{\"nodes\":[{\"id\":\"seo\",\"keyword\":\"سئو\",\"level\":0,\"type\":\"parent\",\"cluster\":\"Cluster 1\",\"search_intent\":\"informational\",\"topic\":\"سئو\",\"parent_id\":null}],'
        '\"edges\":[{\"source\":\"seo\",\"target\":\"آموزش سئو\",\"relationship\":\"parent-child\",\"confidence\":0.88}]}' 
    )


def _call_llm(cluster: List[str], cluster_label: str, user) -> Dict[str, Any]:
    prompt = _build_prompt(cluster, cluster_label)
    api_key, base_url, model_id, error_msg = get_active_user_llm_config(user.id)
    if error_msg:
        raise MindMapGenerationError(error_msg)

    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    options = {"api_key": api_key, "model": model_id, "temperature": 0.15}
    if base_url:
        options["base_url"] = base_url
    llm = ChatOpenAI(**options)
    messages = [
        SystemMessage(content="Return only valid JSON. Analyze semantic topic hierarchy and relationships precisely."),
        HumanMessage(content=prompt),
    ]
    response = llm.invoke(messages)
    content = getattr(response, "content", "")
    return _extract_json(content)


def generate_keyword_mind_map(keywords: Sequence[str], user) -> Dict[str, Any]:
    normalized = _normalize_keywords(keywords)
    if not normalized:
        return {"nodes": [], "edges": [], "clusters": [], "meta": {"total_keywords": 0, "processed": 0}}

    clusters = _build_clusters(normalized, LLM_CLUSTER_SIZE)
    all_nodes: List[Dict[str, Any]] = []
    all_edges: List[Dict[str, Any]] = []
    cluster_names: List[str] = []

    for index, cluster in enumerate(clusters, start=1):
        cluster_name = f"Cluster {index}"
        cluster_names.append(cluster_name)
        if len(cluster) == 1:
            cluster_map = _fallback_hierarchy(cluster, cluster_name)
        else:
            attempt = 0
            cluster_map = None
            last_error = None
            while attempt <= LLM_RETRY_ATTEMPTS:
                try:
                    raw_map = _call_llm(cluster, cluster_name, user)
                    cluster_map = _normalize_payload(raw_map, cluster_name)
                    candidate_edges = _filter_edges(cluster_map["nodes"], cluster_map["edges"])
                    ordered_nodes, final_edges = _build_parent_tree(cluster_map["nodes"], candidate_edges)
                    if not final_edges:
                        final_edges = _build_edge_candidates(ordered_nodes)
                        final_edges = _filter_edges(ordered_nodes, final_edges)
                        ordered_nodes, final_edges = _build_parent_tree(ordered_nodes, final_edges)
                    cluster_map = {"nodes": ordered_nodes, "edges": final_edges}
                    break
                except (json.JSONDecodeError, MindMapGenerationError, RuntimeError) as exc:
                    last_error = exc
                    attempt += 1
                    cluster_map = _fallback_hierarchy(cluster, cluster_name)
                    if attempt > LLM_RETRY_ATTEMPTS:
                        break
            if cluster_map is None:
                raise MindMapGenerationError(str(last_error))

        for node in cluster_map["nodes"]:
            node["cluster"] = cluster_name
            all_nodes.append(node)
        for edge in cluster_map["edges"]:
            all_edges.append(edge)

    # Ensure every node has valid cluster and intent values
    for node in all_nodes:
        node["cluster"] = node.get("cluster") or FALLBACK_CLUSTER_NAME
        node["topic"] = node.get("topic") or node.get("cluster")
        node["search_intent"] = node.get("search_intent") or _infer_search_intent(node["keyword"])

    return {
        "nodes": all_nodes,
        "edges": all_edges,
        "clusters": cluster_names,
        "meta": {
            "total_keywords": len(normalized),
            "processed": len(all_nodes),
            "clusters": len(cluster_names),
        },
    }
