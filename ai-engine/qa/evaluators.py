from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from schemas.canonical import (
    AudioAsset,
    CanonicalSource,
    CanonicalStory,
    LocalizedScript,
    QAIssue,
    QAReport,
    QASeverity,
    StoryGraph,
)
from storygraph.graph_builder import StoryGraphAnalyzer


class SourceQAEvaluator:
    """Evaluates raw extraction quality and canonical source integrity."""

    def evaluate(self, source: CanonicalSource) -> QAReport:
        issues: List[QAIssue] = []
        score = 1.0

        if not source.segments:
            issues.append(
                QAIssue(
                    stage="source",
                    severity=QASeverity.ERROR,
                    code="NO_SEGMENTS",
                    message="No segments extracted from source document.",
                )
            )
            score = 0.0
            return QAReport(stage="source", passed=False, score=score, issues=issues, summary="Source extraction failed completely.")

        empty_segs = [s for s in source.segments if not s.text.strip()]
        if empty_segs:
            issues.append(
                QAIssue(
                    stage="source",
                    severity=QASeverity.WARNING,
                    code="EMPTY_SEGMENTS",
                    message=f"Found {len(empty_segs)} empty segments.",
                )
            )
            score -= 0.1

        if source.total_words < 50:
            issues.append(
                QAIssue(
                    stage="source",
                    severity=QASeverity.WARNING,
                    code="VERY_SHORT_SOURCE",
                    message=f"Source is very short ({source.total_words} words).",
                )
            )
            score -= 0.2

        passed = not any(i.severity == QASeverity.ERROR for i in issues)
        return QAReport(
            stage="source",
            passed=passed,
            score=max(0.0, score),
            issues=issues,
            summary=f"Source QA evaluated: {len(source.segments)} segments, {source.total_words} words.",
        )


class StoryQAEvaluator:
    """Evaluates Story Graph consistency and causal integrity."""

    def evaluate(self, story_graph: StoryGraph) -> QAReport:
        issues: List[QAIssue] = []
        score = 1.0

        if not story_graph.entities:
            issues.append(
                QAIssue(
                    stage="story_graph",
                    severity=QASeverity.ERROR,
                    code="NO_ENTITIES",
                    message="No entities or characters extracted.",
                )
            )
            score -= 0.4

        if not story_graph.events:
            issues.append(
                QAIssue(
                    stage="story_graph",
                    severity=QASeverity.ERROR,
                    code="NO_EVENTS",
                    message="No story events extracted.",
                )
            )
            score -= 0.4

        # Graph validation with StoryGraphAnalyzer
        analyzer = StoryGraphAnalyzer(story_graph)
        graph_stats = analyzer.validate_graph()

        if not graph_stats["is_valid_dag"]:
            issues.append(
                QAIssue(
                    stage="story_graph",
                    severity=QASeverity.WARNING,
                    code="CAUSAL_CYCLE_DETECTED",
                    message=f"Cycles detected in causal links: {graph_stats['cycles_detected']}",
                )
            )
            score -= 0.2

        if graph_stats["orphaned_entities"]:
            issues.append(
                QAIssue(
                    stage="story_graph",
                    severity=QASeverity.INFO,
                    code="ORPHANED_ENTITIES",
                    message=f"{len(graph_stats['orphaned_entities'])} entities have no relationships.",
                )
            )

        passed = not any(i.severity == QASeverity.ERROR for i in issues) and score >= 0.6
        return QAReport(
            stage="story_graph",
            passed=passed,
            score=max(0.0, score),
            issues=issues,
            summary=f"Story Graph QA: {len(story_graph.entities)} entities, {len(story_graph.events)} events.",
        )


class LocalizationQAEvaluator:
    """Evaluates localized scripts against the canonical story to detect drift."""

    def evaluate(
        self,
        canonical: CanonicalStory,
        localized: LocalizedScript,
    ) -> QAReport:
        issues: List[QAIssue] = []
        score = 1.0

        # Chapter count match
        if len(localized.chapters) != len(canonical.chapters):
            issues.append(
                QAIssue(
                    stage="localization",
                    severity=QASeverity.ERROR,
                    code="CHAPTER_COUNT_MISMATCH",
                    message=f"Expected {len(canonical.chapters)} chapters, got {len(localized.chapters)}.",
                )
            )
            score -= 0.3

        # Word count sanity check (localized script shouldn't be under 40% or over 250% of canonical)
        if canonical.total_word_count > 0:
            ratio = localized.total_word_count / canonical.total_word_count
            if ratio < 0.4 or ratio > 2.5:
                issues.append(
                    QAIssue(
                        stage="localization",
                        severity=QASeverity.WARNING,
                        code="WORD_COUNT_DRIFT",
                        message=f"Word ratio {ratio:.2f} seems unusual compared to canonical.",
                    )
                )
                score -= 0.15

        # Check for empty localized chapters
        for ch in localized.chapters:
            if not ch.content.strip():
                issues.append(
                    QAIssue(
                        stage="localization",
                        severity=QASeverity.ERROR,
                        code="EMPTY_LOCALIZED_CHAPTER",
                        message=f"Chapter {ch.chapter_number} has empty content.",
                    )
                )
                score -= 0.3

        passed = not any(i.severity == QASeverity.ERROR for i in issues) and score >= 0.7
        return QAReport(
            stage="localization",
            passed=passed,
            score=max(0.0, score),
            issues=issues,
            summary=f"Localization QA ({localized.language_name}): score {score:.2f}.",
        )


class AudioQAEvaluator:
    """Evaluates generated TTS audio assets."""

    def evaluate(self, audio_asset: AudioAsset) -> QAReport:
        issues: List[QAIssue] = []
        score = 1.0

        if not audio_asset.chapters:
            issues.append(
                QAIssue(
                    stage="audio",
                    severity=QASeverity.ERROR,
                    code="NO_AUDIO_CHAPTERS",
                    message="No audio chapters generated.",
                )
            )
            return QAReport(stage="audio", passed=False, score=0.0, issues=issues, summary="No audio chapters.")

        for ch in audio_asset.chapters:
            p = Path(ch.audio_path)
            if not p.exists():
                issues.append(
                    QAIssue(
                        stage="audio",
                        severity=QASeverity.ERROR,
                        code="FILE_NOT_FOUND",
                        message=f"Audio file missing for chapter {ch.chapter_number}: {p}",
                    )
                )
                score -= 0.4
            elif p.stat().st_size == 0:
                issues.append(
                    QAIssue(
                        stage="audio",
                        severity=QASeverity.ERROR,
                        code="EMPTY_AUDIO_FILE",
                        message=f"Audio file is 0 bytes for chapter {ch.chapter_number}.",
                    )
                )
                score -= 0.4

        passed = not any(i.severity == QASeverity.ERROR for i in issues) and score >= 0.8
        return QAReport(
            stage="audio",
            passed=passed,
            score=max(0.0, score),
            issues=issues,
            summary=f"Audio QA ({audio_asset.language}): {len(audio_asset.chapters)} chapters, {audio_asset.total_duration_seconds:.1f}s total duration.",
        )
