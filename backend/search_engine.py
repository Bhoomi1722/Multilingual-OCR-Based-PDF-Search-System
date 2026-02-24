import re
from typing import List, Dict, Any
from rapidfuzz import fuzz, process

from backend.utils import get_context
from backend.config import FUZZY_MATCH_THRESHOLD

class SearchEngine:
    def search_keywords(
        self,
        page_texts: List[tuple[int, str, float]],
        keywords: List[str],
        source: str,
        filename: str = ""
    ) -> List[Dict[str, Any]]:
        results = []

        for page_num, text, page_conf in page_texts:
            if not text.strip():
                continue

            for keyword in keywords:
                keyword = keyword.strip()
                if not keyword:
                    continue

                # Exact matches
                pattern = re.compile(re.escape(keyword), re.UNICODE | re.IGNORECASE)
                for m in pattern.finditer(text):
                    match_str = m.group()
                    context = get_context(text, match_str)
                    results.append({
                        "filename": filename,
                        "keyword": keyword,
                        "match": match_str,
                        "context": context,
                        "source": source,
                        "page": page_num,
                        "page_conf": page_conf,
                        "match_type": "exact",
                        "score": 100 + page_conf * 0.1,
                        "position": m.start()
                    })

                # Fuzzy matches (only if no exact match found on this page for this keyword)
                if not any(r["page"] == page_num and r["keyword"] == keyword and r["match_type"] == "exact" for r in results):
                    words = text.split()
                    fuzzy_candidates = process.extract(
                        keyword, words,
                        scorer=fuzz.token_sort_ratio,
                        score_cutoff=FUZZY_MATCH_THRESHOLD
                    )
                    for match_str, score, _ in fuzzy_candidates:
                        context = get_context(text, match_str)
                        results.append({
                            "filename": filename,
                            "keyword": keyword,
                            "match": match_str,
                            "context": context + f" (~{score:.0f}%)",
                            "source": source,
                            "page": page_num,
                            "page_conf": page_conf,
                            "match_type": "fuzzy",
                            "score": score + page_conf * 0.1,
                            "position": text.find(match_str)
                        })

        # Sort: exact > fuzzy > score > page > position
        results.sort(key=lambda x: (
            0 if x["match_type"] == "exact" else 1,
            -x["score"],
            x["page"],
            x["position"]
        ))

        return results