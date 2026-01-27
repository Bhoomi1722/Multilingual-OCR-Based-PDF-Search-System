import re
from typing import List, Tuple, Dict, Any
from backend.utils import get_context, logger

class SearchEngine:
    def search_keywords(self, page_texts: List[Tuple[int, str]], keywords: List[str], source: str) -> List[Dict[str, Any]]:
        results = []
        for page_num, text in page_texts:
            if not text.strip():
                continue
            for keyword in keywords:
                keyword = keyword.strip()
                if not keyword:
                    continue
                # Unicode-aware exact match
                pattern = re.compile(re.escape(keyword), re.UNICODE | re.IGNORECASE)
                matches = pattern.findall(text)
                for match in matches:
                    context = get_context(text, match)
                    results.append({
                        "keyword": keyword,
                        "page": page_num,
                        "match": match,
                        "context": context,
                        "source": source,
                        "confidence": "high" if source == "unicode" else "medium"
                    })
                # Optional fuzzy fallback (expandable)
                if not matches:
                    # Could add difflib ratio > 0.8 here for future
                    pass
        logger.info(f"Found {len(results)} matches")
        return results