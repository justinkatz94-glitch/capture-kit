"""
Queue Manager - Content queue management

Handles the content pipeline: pending -> approved -> posted.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .schemas import (
    QueueItem, QueueStatus, generate_id, now_iso, load_json, save_json
)
from .user_manager import get_active_user, get_active_profile

# Paths
BASE_DIR = Path(__file__).parent.parent
QUEUE_DIR = BASE_DIR / "queue"
PENDING_DIR = QUEUE_DIR / "pending"
APPROVED_DIR = QUEUE_DIR / "approved"
POSTED_DIR = QUEUE_DIR / "posted"


class QueueManager:
    """
    Manages the content queue through its lifecycle.
    """

    def __init__(self):
        """Initialize queue manager."""
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        APPROVED_DIR.mkdir(parents=True, exist_ok=True)
        POSTED_DIR.mkdir(parents=True, exist_ok=True)

    def add_to_queue(
        self,
        content: str,
        platform: str = "twitter",
        reply_to_url: str = None,
        reply_to_author: str = None,
        reply_to_content: str = None,
        analysis: Dict[str, Any] = None,
        scores: Dict[str, float] = None,
        why: str = "",
    ) -> QueueItem:
        """
        Add content to the pending queue.

        Args:
            content: The content to queue
            platform: Target platform
            reply_to_url: URL of post being replied to
            reply_to_author: Author being replied to
            reply_to_content: Content being replied to
            analysis: Content analysis dict
            scores: Voice match and engagement scores
            why: Explanation of why this content was generated

        Returns:
            QueueItem
        """
        user = get_active_user()
        if not user:
            raise ValueError("No active user. Create or switch to a user first.")

        item_id = generate_id()
        now = now_iso()

        item = QueueItem(
            id=item_id,
            user=user,
            platform=platform,
            content=content,
            status=QueueStatus.PENDING.value,
            created_at=now,
            reply_to_url=reply_to_url,
            reply_to_author=reply_to_author,
            reply_to_content=reply_to_content,
            hook_type=analysis.get("hook_type", "") if analysis else "",
            framework=analysis.get("framework", "") if analysis else "",
            triggers=analysis.get("triggers", []) if analysis else [],
            techniques=analysis.get("techniques", []) if analysis else [],
            voice_match=scores.get("voice_match", 0.0) if scores else 0.0,
            engagement_prediction=scores.get("engagement_prediction", 0.0) if scores else 0.0,
            combined_score=scores.get("combined_score", 0.0) if scores else 0.0,
            why=why,
        )

        # Save to pending
        self._save_item(item, PENDING_DIR)

        return item

    def list_pending(self, user: str = None) -> List[QueueItem]:
        """List all pending items for a user."""
        return self._list_items(PENDING_DIR, user)

    def list_approved(self, user: str = None) -> List[QueueItem]:
        """List all approved items for a user."""
        return self._list_items(APPROVED_DIR, user)

    def list_posted(self, user: str = None, limit: int = 50) -> List[QueueItem]:
        """List posted items for a user."""
        items = self._list_items(POSTED_DIR, user)
        return sorted(items, key=lambda x: x.posted_at or "", reverse=True)[:limit]

    def get_item(self, item_id: str) -> Optional[QueueItem]:
        """Get a queue item by ID from any status folder."""
        for folder in [PENDING_DIR, APPROVED_DIR, POSTED_DIR]:
            item_path = folder / f"{item_id}.json"
            if item_path.exists():
                data = load_json(str(item_path))
                return QueueItem.from_dict(data)
        return None

    def approve(self, item_id: str) -> Dict[str, Any]:
        """Approve a pending item."""
        # Find in pending
        item_path = PENDING_DIR / f"{item_id}.json"
        if not item_path.exists():
            return {"error": f"Item {item_id} not found in pending queue"}

        data = load_json(str(item_path))
        item = QueueItem.from_dict(data)

        # Update status
        item.status = QueueStatus.APPROVED.value
        item.approved_at = now_iso()

        # Move to approved
        item_path.unlink()
        self._save_item(item, APPROVED_DIR)

        return {"status": "approved", "item_id": item_id}

    def reject(self, item_id: str, reason: str = "") -> Dict[str, Any]:
        """Reject a pending item."""
        item_path = PENDING_DIR / f"{item_id}.json"
        if not item_path.exists():
            return {"error": f"Item {item_id} not found in pending queue"}

        data = load_json(str(item_path))
        item = QueueItem.from_dict(data)

        # Update status
        item.status = QueueStatus.REJECTED.value
        item.why = reason if reason else item.why

        # Remove from pending (optionally archive)
        item_path.unlink()

        return {"status": "rejected", "item_id": item_id}

    def mark_posted(self, item_id: str, post_url: str = "") -> Dict[str, Any]:
        """Mark an approved item as posted."""
        item_path = APPROVED_DIR / f"{item_id}.json"
        if not item_path.exists():
            return {"error": f"Item {item_id} not found in approved queue"}

        data = load_json(str(item_path))
        item = QueueItem.from_dict(data)

        # Update status
        item.status = QueueStatus.POSTED.value
        item.posted_at = now_iso()
        item.post_url = post_url

        # Move to posted
        item_path.unlink()
        self._save_item(item, POSTED_DIR)

        return {"status": "posted", "item_id": item_id, "post_url": post_url}

    def edit_content(self, item_id: str, new_content: str) -> Dict[str, Any]:
        """Edit the content of a pending or approved item."""
        for folder in [PENDING_DIR, APPROVED_DIR]:
            item_path = folder / f"{item_id}.json"
            if item_path.exists():
                data = load_json(str(item_path))
                item = QueueItem.from_dict(data)
                item.content = new_content
                self._save_item(item, folder)
                return {"status": "updated", "item_id": item_id}

        return {"error": f"Item {item_id} not found"}

    def get_next_to_post(self, platform: str = None) -> Optional[QueueItem]:
        """Get the next approved item to post."""
        items = self.list_approved()

        if platform:
            items = [i for i in items if i.platform == platform]

        if not items:
            return None

        # Sort by score (highest first)
        items.sort(key=lambda x: x.combined_score, reverse=True)
        return items[0]

    def get_queue_stats(self, user: str = None) -> Dict[str, Any]:
        """Get queue statistics."""
        pending = self.list_pending(user)
        approved = self.list_approved(user)
        posted = self.list_posted(user, limit=100)

        return {
            "pending_count": len(pending),
            "approved_count": len(approved),
            "posted_count": len(posted),
            "avg_pending_score": sum(i.combined_score for i in pending) / len(pending) if pending else 0,
            "avg_approved_score": sum(i.combined_score for i in approved) / len(approved) if approved else 0,
            "platforms": {
                "twitter": len([i for i in pending + approved if i.platform == "twitter"]),
                "linkedin": len([i for i in pending + approved if i.platform == "linkedin"]),
                "instagram": len([i for i in pending + approved if i.platform == "instagram"]),
            }
        }

    def _list_items(self, folder: Path, user: str = None) -> List[QueueItem]:
        """List items from a folder."""
        if user is None:
            user = get_active_user()

        items = []
        for item_path in folder.glob("*.json"):
            data = load_json(str(item_path))
            if data and (user is None or data.get("user") == user):
                items.append(QueueItem.from_dict(data))

        return items

    def _save_item(self, item: QueueItem, folder: Path):
        """Save a queue item to a folder."""
        item_path = folder / f"{item.id}.json"
        save_json(str(item_path), item.to_dict())


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_manager: Optional[QueueManager] = None


def get_queue_manager() -> QueueManager:
    """Get the singleton queue manager."""
    global _manager
    if _manager is None:
        _manager = QueueManager()
    return _manager


def add_to_queue(**kwargs) -> QueueItem:
    """Add content to queue."""
    return get_queue_manager().add_to_queue(**kwargs)


def list_pending() -> List[QueueItem]:
    """List pending items."""
    return get_queue_manager().list_pending()


def approve_item(item_id: str) -> Dict[str, Any]:
    """Approve an item."""
    return get_queue_manager().approve(item_id)


def reject_item(item_id: str, reason: str = "") -> Dict[str, Any]:
    """Reject an item."""
    return get_queue_manager().reject(item_id, reason)
