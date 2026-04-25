# PR Rescue Probe

- Repo: `/private/tmp/cognee-pr-2705`
- Base ref: `origin/dev`
- Head ref: `pr-sentinel-pr-2705`
- Diff base: `c32b15371db09ea85b73f62226fa36c9a5eb346e`
- Changed files: `55`

## Changed Files

| Status | File | Risk | Lines | Symbols |
| --- | --- | --- | --- | --- |
| A | `.github/workflows/build_skills_hackathon_image.yml` | - | +80/-0 | - |
| M | `cognee/api/v1/remember/remember.py` | api | +161/-10 | _ensure_migrations_run, RememberKwargs, _estimate_data_size, _data_to_text, _add_to_session, _remember_entry, _dispatch_session_entry, RememberResult (+16 more) |
| M | `cognee/api/v1/remember/routers/get_remember_router.py` | api | +15/-7 | get_remember_router, remember, RememberEntryRequest, remember_entry |
| M | `cognee/api/v1/search/routers/get_search_router.py` | api | +15/-0 | SearchPayloadDTO, get_search_router, SearchHistoryItem, get_search_history, search |
| M | `cognee/api/v1/search/search.py` | api | +50/-1 | search |
| M | `cognee/api/v1/serve/cloud_client.py` | api, cli | +35/-5 | CloudClient, __init__, _get_session, close, _health_check, remember, remember_entry, recall (+5 more) |
| M | `cognee/infrastructure/engine/models/DataPoint.py` | migration | +18/-4 | MetaData, DataPoint, __init__, _get_metadata_default, _get_identity_fields, _generate_identity_id, __pydantic_init_subclass__, get_embeddable_data (+7 more) |
| A | `cognee/infrastructure/llm/prompts/agentic_system.txt` | - | +13/-0 | - |
| A | `cognee/infrastructure/llm/prompts/agentic_user.txt` | - | +9/-0 | - |
| M | `cognee/memory/__init__.py` | - | +2/-0 | - |
| M | `cognee/memory/entries.py` | - | +53/-4 | QAEntry, TraceEntry, FeedbackEntry, SkillRunEntry, normalize_scope, _validate_success_score, _validate_feedback, _validate_non_negative_ms |
| A | `cognee/modules/engine/models/Skill.py` | migration | +105/-0 | SkillResource, TaskPattern, Skill |
| A | `cognee/modules/engine/models/SkillAmendment.py` | migration | +38/-0 | AmendmentProposal, SkillAmendment |
| A | `cognee/modules/engine/models/SkillChangeEvent.py` | migration | +20/-0 | SkillChangeEvent |
| A | `cognee/modules/engine/models/SkillInspection.py` | migration | +47/-0 | InspectionResult, SkillInspection |
| A | `cognee/modules/engine/models/SkillRun.py` | migration | +68/-0 | ToolCall, CandidateSkill, SkillRun |
| A | `cognee/modules/engine/models/Tool.py` | migration | +36/-0 | Tool |
| M | `cognee/modules/engine/models/__init__.py` | migration | +6/-0 | - |
| M | `cognee/modules/graph/methods/upsert_edges.py` | storage | +3/-0 | upsert_edges |
| A | `cognee/modules/memify/skill_amendify.py` | - | +396/-0 | _tag_with_nodeset, _content_hash, _replace_skill_md_body, _load_amendment_from_graph, _load_skill_from_graph, _reconstruct_amendment, amendify, rollback_amendify (+1 more) |
| A | `cognee/modules/memify/skill_improvement.py` | - | +127/-0 | _list_skill_names, _load_skill_dict, improve_failing_skills |
| A | `cognee/modules/memify/skill_inspect.py` | - | +185/-0 | _format_run, inspect_skill |
| A | `cognee/modules/memify/skill_preview_amendify.py` | - | +121/-0 | preview_skill_amendify |
| A | `cognee/modules/retrieval/agentic_retriever.py` | - | +451/-0 | ToolCall, AgentStep, AgenticRetriever, _format_skill_catalog, _format_tool_manifest, __init__, _use_session_cache, get_retrieved_objects (+8 more) |
| M | `cognee/modules/search/methods/get_search_type_retriever_instance.py` | - | +56/-0 | get_search_type_retriever_instance |
| M | `cognee/modules/search/methods/search.py` | - | +6/-1 | search, authorized_search, search_in_datasets_context, _backwards_compatible_search_results, _search_in_dataset_context |
| M | `cognee/modules/search/types/SearchType.py` | - | +1/-0 | SearchType |
| M | `cognee/modules/storage/utils/__init__.py` | storage | +9/-1 | JSONEncoder, copy_model, get_own_properties, default, _copy_default, ConfiguredBase |
| A | `cognee/modules/tools/__init__.py` | - | +21/-0 | - |
| A | `cognee/modules/tools/builtin/__init__.py` | - | +7/-0 | - |
| ... | 25 more files omitted | | | |

## Risk Summary

- `api`: cognee/api/v1/remember/remember.py, cognee/api/v1/remember/routers/get_remember_router.py, cognee/api/v1/search/routers/get_search_router.py, cognee/api/v1/search/search.py, cognee/api/v1/serve/cloud_client.py
- `async`: cognee/modules/tools/skill_enrichment_tasks.py, cognee/modules/tools/skill_node_set_task.py, cognee/modules/tools/skill_pattern_tasks.py
- `cli`: cognee/api/v1/serve/cloud_client.py
- `migration`: cognee/infrastructure/engine/models/DataPoint.py, cognee/modules/engine/models/Skill.py, cognee/modules/engine/models/SkillAmendment.py, cognee/modules/engine/models/SkillChangeEvent.py, cognee/modules/engine/models/SkillInspection.py, cognee/modules/engine/models/SkillRun.py, cognee/modules/engine/models/Tool.py, cognee/modules/engine/models/__init__.py
- `storage`: cognee/modules/graph/methods/upsert_edges.py, cognee/modules/storage/utils/__init__.py, distributed/deploy/Dockerfile, distributed/deploy/daytona_sandbox.py
- `test`: cognee/tests/unit/modules/tools/__init__.py, cognee/tests/unit/modules/tools/test_skill_ingest.py

## Hunk Headers

- `.github/workflows/build_skills_hackathon_image.yml`
  - `@@ -0,0 +1,80 @@`
- `cognee/api/v1/remember/remember.py`
  - `@@ -19,0 +20 @@ from cognee.memory import (`
  - `@@ -36,0 +38,14 @@ logger = get_logger("remember")`
  - `@@ -50,0 +66,10 @@ class RememberKwargs(TypedDict, total=False):`
  - `@@ -153,0 +179,3 @@ async def _remember_entry(`
  - `@@ -167,0 +196,3 @@ async def _remember_entry(`
  - `@@ -186,0 +218,3 @@ async def _remember_entry(`
  - `@@ -195,0 +230,3 @@ async def _dispatch_session_entry(`
  - `@@ -199,4 +236,4 @@ async def _dispatch_session_entry(`
- `cognee/api/v1/remember/routers/get_remember_router.py`
  - `@@ -10 +10 @@ from pydantic import BaseModel, Field, WithJsonSchema`
  - `@@ -105 +105,2 @@ def get_remember_router() -> APIRouter:`
  - `@@ -109 +110 @@ def get_remember_router() -> APIRouter:`
  - `@@ -113 +114,4 @@ def get_remember_router() -> APIRouter:`
  - `@@ -123,3 +127,4 @@ def get_remember_router() -> APIRouter:`
  - `@@ -150,0 +156,3 @@ def get_remember_router() -> APIRouter:`
- `cognee/api/v1/search/routers/get_search_router.py`
  - `@@ -36,0 +37,5 @@ class SearchPayloadDTO(InDTO):`
  - `@@ -146,0 +152,5 @@ def get_search_router() -> APIRouter:`
  - `@@ -166,0 +177,5 @@ def get_search_router() -> APIRouter:`
- `cognee/api/v1/search/search.py`
  - `@@ -4,0 +5 @@ from cognee.modules.engine.models.node_set import NodeSet`
  - `@@ -47,0 +49,5 @@ async def search(`
  - `@@ -62,0 +69,10 @@ async def search(`
  - `@@ -155,0 +172,5 @@ async def search(`
  - `@@ -204,0 +226,11 @@ async def search(`
  - `@@ -210 +242,12 @@ async def search(`
  - `@@ -251,0 +295,6 @@ async def search(`
- `cognee/api/v1/serve/cloud_client.py`
  - `@@ -97,0 +98,3 @@ class CloudClient:`
  - `@@ -99 +102 @@ class CloudClient:`
  - `@@ -101 +104 @@ class CloudClient:`
  - `@@ -103,3 +105,0 @@ class CloudClient:`
  - `@@ -114,0 +115,3 @@ class CloudClient:`
  - `@@ -242,0 +246,27 @@ class CloudClient:`
- `cognee/infrastructure/engine/models/DataPoint.py`
  - `@@ -77,0 +78,12 @@ class DataPoint(BaseModel):`
  - `@@ -86,2 +98,3 @@ class DataPoint(BaseModel):`
  - `@@ -91,2 +104,3 @@ class DataPoint(BaseModel):`
- `cognee/infrastructure/llm/prompts/agentic_system.txt`
  - `@@ -0,0 +1,13 @@`
- `cognee/infrastructure/llm/prompts/agentic_user.txt`
  - `@@ -0,0 +1,9 @@`
- `cognee/memory/__init__.py`
  - `@@ -5,0 +6 @@ from .entries import (`
  - `@@ -14,0 +16 @@ __all__ = [`
- `cognee/memory/entries.py`
  - `@@ -5 +5,2 @@ Typed payloads let callers pass rich structured data to`
  - `@@ -13,0 +15 @@ from typing import Any, Literal, Optional, Union`
  - `@@ -15 +17 @@ from typing import Any, Literal, Optional, Union`
  - `@@ -67 +69,48 @@ class FeedbackEntry(BaseModel):`
  - `@@ -72 +121 @@ MemoryEntry = Union[QAEntry, TraceEntry, FeedbackEntry]`
- `cognee/modules/engine/models/Skill.py`
  - `@@ -0,0 +1,105 @@`
- `cognee/modules/engine/models/SkillAmendment.py`
  - `@@ -0,0 +1,38 @@`
- `cognee/modules/engine/models/SkillChangeEvent.py`
  - `@@ -0,0 +1,20 @@`
- `cognee/modules/engine/models/SkillInspection.py`
  - `@@ -0,0 +1,47 @@`
- `cognee/modules/engine/models/SkillRun.py`
  - `@@ -0,0 +1,68 @@`
- `cognee/modules/engine/models/Tool.py`
  - `@@ -0,0 +1,36 @@`
- `cognee/modules/engine/models/__init__.py`
  - `@@ -10,0 +11,6 @@ from .Triplet import Triplet`
- `cognee/modules/graph/methods/upsert_edges.py`
  - `@@ -28,0 +29,3 @@ async def upsert_edges(`
- `cognee/modules/memify/skill_amendify.py`
  - `@@ -0,0 +1,396 @@`
- `cognee/modules/memify/skill_improvement.py`
  - `@@ -0,0 +1,127 @@`
- `cognee/modules/memify/skill_inspect.py`
  - `@@ -0,0 +1,185 @@`
- `cognee/modules/memify/skill_preview_amendify.py`
  - `@@ -0,0 +1,121 @@`
- `cognee/modules/retrieval/agentic_retriever.py`
  - `@@ -0,0 +1,451 @@`
- `cognee/modules/search/methods/get_search_type_retriever_instance.py`
  - `@@ -31,0 +32,2 @@ from cognee.modules.retrieval.natural_language_retriever import NaturalLanguageR`
  - `@@ -257,0 +260,54 @@ async def get_search_type_retriever_instance(`
- `cognee/modules/search/methods/search.py`
  - `@@ -176,0 +177 @@ async def authorized_search(`
  - `@@ -199,0 +201 @@ async def search_in_datasets_context(`
  - `@@ -268,0 +271 @@ async def search_in_datasets_context(`
  - `@@ -313,0 +317 @@ async def search_in_datasets_context(`
  - `@@ -318 +322,2 @@ async def search_in_datasets_context(`
- `cognee/modules/search/types/SearchType.py`
  - `@@ -19,0 +20 @@ class SearchType(str, Enum):`
- `cognee/modules/storage/utils/__init__.py`
  - `@@ -29,0 +30,8 @@ def copy_model(`
  - `@@ -31 +39 @@ def copy_model(`
- `cognee/modules/tools/__init__.py`
  - `@@ -0,0 +1,21 @@`
- `cognee/modules/tools/builtin/__init__.py`
  - `@@ -0,0 +1,7 @@`

## Likely Tests

- `.github/workflows/backend_docker_build_test.yml`
- `.github/workflows/basic_tests.yml`
- `.github/workflows/cli_tests.yml`
- `.github/workflows/community_tests.yml`
- `.github/workflows/db_examples_tests.yml`
- `.github/workflows/distributed_test.yml`
- `.github/workflows/e2e_tests.yml`
- `.github/workflows/examples_tests.yml`
- `.github/workflows/graph_db_tests.yml`
- `.github/workflows/integration_tests.yml`
- `.github/workflows/load_tests.yml`
- `.github/workflows/notebooks_tests.yml`

## Suggested Commands

- `python -m pytest`
