from comfy_execution.graph_utils import is_link


def explore_dependencies(node_id, dynprompt, upstream=None):
    if upstream is None:
        upstream = dict()
    node_info = dynprompt.get_node(node_id)
    if "inputs" not in node_info:
        return
    for k, v in node_info["inputs"].items():
        if is_link(v):
            parent_id = v[0]
            if parent_id not in upstream:
                upstream[parent_id] = []
                explore_dependencies(parent_id, dynprompt, upstream)
            upstream[parent_id].append(node_id)
    return upstream


def collect_contained(node_id, upstream, contained=None):
    if contained is None:
        contained = set()
    if node_id not in upstream:
        return
    for child_id in upstream[node_id]:
        if child_id not in contained:
            contained.add(child_id)
            collect_contained(child_id, upstream, contained)
    return contained


def search_nodes_between(start_node_id, end_node_id, dynprompt):
    upstream = explore_dependencies(end_node_id, dynprompt)
    return collect_contained(start_node_id, upstream)


def search_downstream(node_id, dynprompt):
    result = []
    all_node_ids = dynprompt.all_node_ids()
    for id in all_node_ids:
        node_info = dynprompt.get_node(id)
        if "inputs" not in node_info:
            continue
        for k, v in node_info["inputs"].items():
            if is_link(v) and v[0] == node_id:
                result.append((id, v[1]))
    return result


def find_max_output_index_from_downstream(downstream):
    max_index = -1
    for id, index in downstream:
        max_index = max(max_index, index)
    return max_index


def find_max_output_index(node_id, dynprompt):
    downstream = search_downstream(node_id, dynprompt)
    return find_max_output_index_from_downstream(downstream)
