import re
from typing import List, Tuple, Dict, Any
from rapidfuzz import fuzz, process
from backend.utils import get_context, logger
from backend.config import FUZZY_MATCH_THRESHOLD

class SearchEngine:
    def search_keywords(self, page_texts: List[Tuple[int, str, float]], keywords: List[str], source: str) -> List[Dict[str, Any]]:
        results = []
        for page_num, text, page_conf in page_texts:
            if not text.strip():
                continue

            for keyword in keywords:
                keyword = keyword.strip()
                if not keyword:
                    continue

                # 1. Exact matches
                pattern = re.compile(re.escape(keyword), re.UNICODE | re.IGNORECASE)
                exact_matches = list(pattern.finditer(text))
                for m in exact_matches:
                    match_str = m.group()
                    context = get_context(text, match_str, 100)
                    results.append({
                        "keyword": keyword,
                        "match": match_str,
                        "context": context,
                        "source": source,
                        "confidence": "high" if source == "unicode" else "medium",
                        "page": page_num,
                        "page_conf": page_conf,
                        "match_type": "exact",
                        "position": m.start()
                    })

                # 2. Fuzzy matches (only if no exact)
                if not exact_matches:
                    words = text.split()
                    fuzzy_candidates = process.extract(
                        keyword, words,
                        scorer=fuzz.token_sort_ratio,
                        score_cutoff=FUZZY_MATCH_THRESHOLD
                    )
                    for match_str, score, _ in fuzzy_candidates:
                        context = get_context(text, match_str, 100)
                        results.append({
                            "keyword": keyword,
                            "match": match_str,
                            "context": context + f" (fuzzy ~{score:.0f}%)",
                            "source": source,
                            "confidence": "medium",
                            "page": page_num,
                            "page_conf": page_conf,
                            "match_type": "fuzzy",
                            "position": text.find(match_str)
                        })

        # Sort: exact > fuzzy > confidence > page > position
        results.sort(key=lambda x: (
            0 if x["match_type"] == "exact" else 1,
            -x["page_conf"],
            x["page"],
            x["position"]
        ))
        return results