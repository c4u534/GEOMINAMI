"""
NotebookLM Auto-Discovery & Gemini Spark Neural Linker
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from notebooklm import NotebookLMClient

SPARK_SKILLS_DIR = Path("./spark_skills")
REGISTRY_FILE = Path("./linked_silos_registry.json")

class SparkSiloLinker:
    def __init__(self, registry_path: Path = REGISTRY_FILE, skills_dir: Path = SPARK_SKILLS_DIR):
        self.registry_path = registry_path
        self.skills_dir = skills_dir
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        if self.registry_path.exists():
            try:
                return json.loads(self.registry_path.read_text())
            except Exception:
                pass
        return {"linked_notebooks": {}, "last_sync": None}

    def _save_registry(self) -> None:
        self.registry_path.write_text(json.dumps(self.registry, indent=2))

    def is_linked(self, notebook_id: str) -> bool:
        return notebook_id in self.registry.get("linked_notebooks", {})

    def generate_skill_manifest(self, notebook_id: str, title: str, sources: List[Dict[str, Any]]) -> str:
        safe_name = title.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        source_bullets = "\n".join([f"  - {s.get('title', 'Untitled Source')}" for s in sources[:10]])

        return f"""# SKILL: notebooklm_{safe_name}
# NOTEBOOK_ID: {notebook_id}
# DESCRIPTION: Auto-linked Neural Skill for the grounded NotebookLM silo '{title}'.

## SILO_METADATA
- **Notebook Title:** {title}
- **Notebook ID:** `{notebook_id}`
- **Source Count:** {len(sources)}
- **Sample Sources:**

{source_bullets if source_bullets else "  - (No sources attached yet)"}

## EXECUTION_PROTOCOL
1. **Grounded RAG Query:** Route search prompts to NotebookLM Silo `{notebook_id}` via `notebooklm_query_rag`.
2. **Citation Validation:** Enforce source-backed citations before returning findings to Gemini Spark workflows.
3. **Graph Integration:** Update solution graph G(V,E) by mapping cross-silo dependencies.
4. **Duplex Output Ingestion:** Write output artifacts back to NotebookLM using `notebooklm_ingest_artifact`.
"""

    async def run_discovery_and_linking(self) -> List[Dict[str, Any]]:
        newly_linked = []
        async with NotebookLMClient.from_storage() as client:
            all_notebooks = await client.notebooks.list()
            for nb in all_notebooks:
                nb_id = nb.id
                title = nb.title or "Untitled Notebook"
                if self.is_linked(nb_id):
                    continue

                try:
                    sources = await client.sources.list(nb_id)
                    source_data = [{"id": getattr(s, "id", "unknown"), "title": getattr(s, "title", "Untitled")} for s in sources]
                except Exception:
                    source_data = []

                skill_content = self.generate_skill_manifest(nb_id, title, source_data)
                skill_path = self.skills_dir / f"skill_notebooklm_{nb_id}.md"
                skill_path.write_text(skill_content)

                self.registry["linked_notebooks"][nb_id] = {
                    "title": title,
                    "skill_file": str(skill_path),
                    "source_count": len(source_data),
                    "linked_at": datetime.now().isoformat(),
                    "status": "active"
                }

                newly_linked.append({
                    "id": nb_id,
                    "title": title,
                    "skill_path": str(skill_path),
                    "sources_count": len(source_data)
                })

            self.registry["last_sync"] = datetime.now().isoformat()
            self._save_registry()
        return newly_linked
