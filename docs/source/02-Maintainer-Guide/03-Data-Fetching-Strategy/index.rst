.. _data-fetching-strategy:

Data Fetching Strategy
==============================================================================

This document describes the challenges and strategies for fetching Confluence
page hierarchy data efficiently.


Problem Statement
------------------------------------------------------------------------------

Given an include list like::

    include = [
        "https://.../folder/f1/.../*",    # All descendants of f1
        "https://.../pages/p3/.../**",    # p3 and all its descendants
        "https://.../pages/p9/...",       # Only p9 itself
    ]

We need to:

1. Fetch all matching pages from Confluence
2. Resolve their ancestor relationships (parent chain)
3. Organize pages hierarchically for downstream processing

Expected output format::

    Page(id="p2", ancestors=[Page(id="p1"), Page(id="f1")])
    Page(id="p3", ancestors=[Page(id="p1")])
    Page(id="p4", ancestors=[Page(id="p1"), Page(id="p3")])
    Page(id="p9", ancestors=[Page(id="f3")])


Confluence API Limitations
------------------------------------------------------------------------------

There are three relevant Confluence REST API v2 endpoints:

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - API
     - What it returns
     - Limitations
   * - ``GET /pages/{id}/descendants``
     - All descendants (pages + folders) with ``id``, ``title``, ``parent_id``
     - **Max depth = 5**. Does not return page content.
   * - ``GET /spaces/{id}/pages``
     - All pages in a space with full content
     - **Does not include folders**. Ancestor chain may be incomplete if parents are folders.
   * - ``GET /pages?id=id1,id2,...``
     - Full page content for specified IDs
     - Requires knowing IDs upfront.

**Critical Issue: Depth Limit**

The ``get_descendants`` API has a ``depth`` parameter with maximum value of 5.
For hierarchies deeper than 5 levels (which is common in real-world Confluence spaces),
this creates challenges for fetching complete hierarchies.

**Critical Issue: Missing Folders**

The ``get_pages_in_space`` API returns all pages but **not folders**. If a page's
ancestors are all folders, we lose the complete hierarchy::

    Space
    └── Folder1          <- Not returned by get_pages_in_space
        └── Folder2      <- Not returned
            └── Page1    <- Returned, but parent_id points to Folder2 (unknown)


Candidate Solutions
------------------------------------------------------------------------------

**Option 1: Pattern-Driven Fetching**

1. Parse ``include`` patterns to extract target node IDs
2. Fetch only the required subtrees
3. For each matched page, fetch missing ancestors on demand

*Pros*: Fetches only needed data

*Cons*: May require many API calls for ancestor resolution; complex implementation

**Option 2: Naive Boundary Recursion**

1. Call ``get_descendants(homepage_id, depth=5)`` to get L1-L5
2. For each node at depth=5, recursively call ``get_descendants``
3. Repeat until no more boundary nodes

*Pros*: Simple logic

*Cons*: If L5 has 100 nodes but only 3 have children, we waste 97 API calls

**Option 3: Parent Clustering (Chosen)**

Instead of calling API for each boundary node individually, cluster them by
their parent nodes and call from parent level. This dramatically reduces
API calls when many sibling nodes exist at the boundary.


Chosen Strategy: Parent Clustering Algorithm
------------------------------------------------------------------------------

**Why This Approach?**

Consider this scenario:

- L5 has 100 nodes
- 97 are leaf nodes (no children)
- Only 3 have children (in L6+)
- These 100 nodes have only 5 distinct L4 parents

With **Naive Boundary Recursion**: 100 API calls (97 return empty)

With **Parent Clustering**: 5 API calls (from L4 parents, each covers depth 5-9)

**Data Structure: Node Pool**

We maintain a ``node_pool`` dictionary::

    node_pool: dict[str, list[Node]]

    # Key: node ID
    # Value: path list [self, parent, grandparent, ...] (reversed order)

    # Example: for path p1/p2/p3
    node_pool["p3"] = [Node(p3), Node(p2), Node(p1)]

The path list uses singleton objects, allowing in-place updates.

**Algorithm**

.. code-block:: text

    ITERATION 1:
    ├── Call get_descendants(homepage, depth=5) → get L1-L5
    ├── Build paths for all nodes in node_pool
    ├── Find all L5 nodes (boundary nodes)
    ├── Cluster L5 nodes by their L4 parents
    └── Collect unique L4 parent IDs for next iteration

    ITERATION 2:
    ├── For each L4 parent: call get_descendants(L4_node, depth=5) → get L5-L9
    ├── Deduplicate: skip nodes already in node_pool
    ├── Update paths for new nodes
    ├── Find all L9 nodes (new boundary)
    ├── Cluster L9 nodes by their L8 parents
    └── Collect unique L8 parent IDs for next iteration

    ITERATION 3:
    ├── For each L8 parent: call get_descendants(L8_node, depth=5) → get L9-L13
    └── ... repeat ...

    TERMINATION:
    └── Stop when no boundary nodes found (no nodes at max depth)

**Implementation Outline**::

    def fetch_space_hierarchy(client, space_id) -> dict[str, list[Node]]:
        """
        Fetch complete space hierarchy using parent clustering algorithm.

        Returns node_pool where each key is node ID and value is path list
        [self, parent, grandparent, ...] in reversed order.
        """
        homepage_id = get_space_homepage(client, space_id)
        node_pool: dict[str, list[Node]] = {}
        depth_limit = 5

        # Track nodes to fetch from in next iteration
        next_roots = [homepage_id]

        while next_roots:
            # Fetch descendants from all root nodes
            new_nodes = []
            for root_id in next_roots:
                descendants = get_descendants(client, root_id, depth=depth_limit)
                for node in descendants:
                    if node.id not in node_pool:
                        new_nodes.append(node)
                        node_pool[node.id] = []  # Will build path later

            if not new_nodes:
                break

            # Build/update paths for new nodes
            build_paths(new_nodes, node_pool)

            # Find boundary nodes (at relative depth = depth_limit)
            boundary_nodes = find_boundary_nodes(new_nodes, next_roots, depth_limit)

            if not boundary_nodes:
                break

            # Cluster boundary nodes by their parents (one level up)
            # This is the key optimization!
            parent_ids = {node.parent_id for node in boundary_nodes}
            next_roots = list(parent_ids)

        return node_pool

    def build_paths(nodes: list[Node], node_pool: dict[str, list[Node]]):
        """Build path list for each node by walking up parent chain."""
        node_by_id = {n.id: n for n in nodes}
        node_by_id.update({path[0].id: path[0] for path in node_pool.values() if path})

        for node in nodes:
            path = [node]
            current = node
            while current.parent_id and current.parent_id in node_by_id:
                parent = node_by_id[current.parent_id]
                path.append(parent)
                current = parent
            node_pool[node.id] = path

    def find_boundary_nodes(nodes, root_ids, depth_limit) -> list[Node]:
        """Find nodes at exactly depth_limit relative to any root."""
        boundary = []
        for node in nodes:
            depth = calculate_relative_depth(node, root_ids, nodes)
            if depth == depth_limit:
                boundary.append(node)
        return boundary

**Example Walkthrough**

Given a 12-level hierarchy with this structure at L4-L5::

    L4: p4-1 (has 50 L5 children)
    L4: p4-2 (has 30 L5 children)
    L4: p4-3 (has 20 L5 children)
    Total L5 nodes: 100

Iteration 1:
- Call: ``get_descendants(homepage, depth=5)``
- Result: L1-L5 (100 nodes at L5)
- Cluster L5 by L4 parents → {p4-1, p4-2, p4-3}

Iteration 2:
- Calls: 3 API calls (not 100!)
  - ``get_descendants(p4-1, depth=5)`` → L5-L9 under p4-1
  - ``get_descendants(p4-2, depth=5)`` → L5-L9 under p4-2
  - ``get_descendants(p4-3, depth=5)`` → L5-L9 under p4-3
- Deduplicate L5 nodes (already fetched)
- Find L9 boundary nodes, cluster by L8 parents

Iteration 3+:
- Continue until no more boundary nodes


Performance Analysis
------------------------------------------------------------------------------

**API Call Comparison**

For a space with 1000 nodes, 12 levels deep:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Strategy
     - API Calls
     - Notes
   * - Naive (per boundary node)
     - ~200+
     - Most return empty
   * - Parent Clustering
     - ~10-20
     - One per unique parent cluster
   * - Theoretical minimum
     - ~3
     - ceil(12/5) = 3 iterations

**Caching**

- Use ``diskcache`` for persistent caching across sessions
- Cache key: ``f"space_hierarchy:{space_id}"``
- Default TTL: 1 hour (configurable)
- Force refresh option for stale data

**Memory Usage**

For a typical Confluence space with 1000 nodes:

- Node metadata: ~500 bytes/node = ~500KB
- Path lists: Shared node references, minimal overhead
- Total: < 1MB for most spaces


Final Workflow
------------------------------------------------------------------------------

1. **Fetch hierarchy** using Parent Clustering Algorithm
2. **Build node_pool** with complete ancestor paths
3. **Apply filters** using ``Selector`` class (in-memory, fast)
4. **Fetch content** only for matched pages using ``get_pages(ids=[...])``
