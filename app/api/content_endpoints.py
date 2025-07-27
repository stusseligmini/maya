from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

content_router = APIRouter()

# Mock content database
fake_content_db = {}
content_counter = 0

class ContentCreate(BaseModel):
    title: str
    content: str
    content_type: str = "blog"
    target_keywords: Optional[str] = None
    meta_description: Optional[str] = None

class ContentResponse(BaseModel):
    id: int
    title: str
    content: str
    content_type: str
    target_keywords: Optional[str]
    meta_description: Optional[str]
    seo_score: int
    readability_score: int
    word_count: int
    status: str
    created_at: str
    updated_at: str

@content_router.post("/create", response_model=ContentResponse)
def create_content(content: ContentCreate):
    """Create new content"""
    global content_counter
    content_counter += 1
    
    word_count = len(content.content.split())
    seo_score = 65 + (15 if content.target_keywords else 0) + min(20, word_count // 50)
    readability_score = min(100, 50 + word_count // 20)
    
    content_data = {
        "id": content_counter,
        "title": content.title,
        "content": content.content,
        "content_type": content.content_type,
        "target_keywords": content.target_keywords,
        "meta_description": content.meta_description,
        "seo_score": seo_score,
        "readability_score": readability_score,
        "word_count": word_count,
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    fake_content_db[content_counter] = content_data
    return ContentResponse(**content_data)

@content_router.get("/list", response_model=List[ContentResponse])
def list_content(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    limit: int = Query(10, description="Number of items to return")
):
    """Get list of content"""
    content_list = list(fake_content_db.values())
    
    if content_type:
        content_list = [c for c in content_list if c["content_type"] == content_type]
    
    return [ContentResponse(**c) for c in content_list[:limit]]

@content_router.get("/{content_id}", response_model=ContentResponse)
def get_content(content_id: int):
    """Get specific content by ID"""
    if content_id not in fake_content_db:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return ContentResponse(**fake_content_db[content_id])

@content_router.put("/{content_id}/optimize")
def optimize_content(content_id: int):
    """Optimize content for SEO"""
    if content_id not in fake_content_db:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content = fake_content_db[content_id]
    
    # Simulate optimization
    old_seo_score = content["seo_score"]
    content["seo_score"] = min(95, old_seo_score + 15)
    content["readability_score"] = min(95, content["readability_score"] + 10)
    content["updated_at"] = datetime.now().isoformat()
    content["status"] = "optimized"
    
    return {
        "message": "Content optimized successfully",
        "improvements": {
            "seo_score_improvement": content["seo_score"] - old_seo_score,
            "new_seo_score": content["seo_score"],
            "new_readability_score": content["readability_score"]
        },
        "content": ContentResponse(**content)
    }