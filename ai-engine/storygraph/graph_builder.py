from __future__ import annotations
from typing import Dict, List, Set
import networkx as nx

from schemas.canonical import StoryEvent, StoryGraph


class StoryGraphAnalyzer:
    """
    Validates and analyzes the semantic Story Graph using NetworkX graphs:
    1. Entity Interaction Graph (Who interacts with whom)
    2. Event Causal Graph (Event A -> Event B)
    3. Identifies crucial causal paths for compression
    """

    def __init__(self, story_graph: StoryGraph):
        self.story_graph = story_graph
        self.entity_graph = nx.Graph()
        self.causal_graph = nx.DiGraph()
        self._build_graphs()

    def _build_graphs(self):
        # 1. Build Entity Graph
        for entity in self.story_graph.entities:
            self.entity_graph.add_node(
                entity.id,
                name=entity.name,
                type=entity.type.value if hasattr(entity.type, "value") else str(entity.type),
                importance=entity.importance_score,
            )

        for rel in self.story_graph.relationships:
            self.entity_graph.add_edge(
                rel.source_entity_id,
                rel.target_entity_id,
                relation=rel.relation_type,
                description=rel.description or "",
            )

        # 2. Build Event Causal Graph
        for ev in self.story_graph.events:
            self.causal_graph.add_node(
                ev.id,
                title=ev.title,
                importance=ev.importance_score,
                is_crucial=ev.is_crucial,
                chronology=ev.chronological_order,
            )

        for link in self.story_graph.causal_links:
            self.causal_graph.add_edge(
                link.cause_event_id,
                link.effect_event_id,
                link_type=link.link_type,
            )

    def get_crucial_ancestor_events(self, event_id: str) -> Set[str]:
        """Find all upstream prerequisite events that caused/enabled this event."""
        if event_id not in self.causal_graph:
            return set()
        return nx.ancestors(self.causal_graph, event_id)

    def get_critical_path(self) -> List[str]:
        """
        Find sequence of top-ranked crucial events that cannot be dropped
        without breaking causal narrative continuity.
        """
        crucial_event_ids = {
            ev.id for ev in self.story_graph.events if ev.is_crucial or ev.importance_score >= 0.7
        }
        
        # Add all ancestor dependencies of crucial events
        complete_required_set = set(crucial_event_ids)
        for ev_id in crucial_event_ids:
            ancestors = self.get_crucial_ancestor_events(ev_id)
            complete_required_set.update(ancestors)

        # Sort chronologically
        events_by_id = {ev.id: ev for ev in self.story_graph.events}
        ordered = sorted(
            [events_by_id[eid] for eid in complete_required_set if eid in events_by_id],
            key=lambda x: x.chronological_order or x.sequence,
        )
        return [e.id for e in ordered]

    def validate_graph(self) -> dict[str, bool | list[str]]:
        """Validate for cycles or disconnected required entities."""
        is_causal_dag = nx.is_directed_acyclic_graph(self.causal_graph)
        cycles = list(nx.simple_cycles(self.causal_graph)) if not is_causal_dag else []
        
        orphaned_entities = [
            node for node, degree in dict(self.entity_graph.degree()).items() if degree == 0
        ]

        return {
            "is_valid_dag": is_causal_dag,
            "cycles_detected": cycles,
            "orphaned_entities": orphaned_entities,
            "total_entities": len(self.entity_graph.nodes),
            "total_events": len(self.causal_graph.nodes),
            "total_causal_links": len(self.causal_graph.edges),
        }
