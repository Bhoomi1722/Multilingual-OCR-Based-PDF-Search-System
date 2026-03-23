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

                # Exact match
                pattern = re.compile(re.escape(keyword), re.UNICODE | re.IGNORECASE)
                for m in pattern.finditer(text):
                    match_str = m.group()
                    context = get_context(text, match_str)
                    score = 100 + page_conf * 0.1
                    results.append({
                        "filename": filename,
                        "keyword": keyword,
                        "match": match_str,
                        "context": context,
                        "source": source,
                        "page": page_num,
                        "page_conf": page_conf,
                        "match_type": "exact",
                        "score": score,
                        "position": m.start()
                    })

                # Fuzzy match if no exact
                if not any(r["page"] == page_num and r["keyword"] == keyword and r["match_type"] == "exact" for r in results):
                    words = text.split()
                    fuzzy_candidates = process.extract(
                        keyword, words,
                        scorer=fuzz.token_sort_ratio,
                        score_cutoff=FUZZY_MATCH_THRESHOLD
                    )
                    for match_str, fscore, _ in fuzzy_candidates:
                        context = get_context(text, match_str)
                        score = fscore + page_conf * 0.1
                        # Boost exact substring matches
                        if keyword.lower() in match_str.lower():
                            score += 10
                        results.append({
                            "filename": filename,
                            "keyword": keyword,
                            "match": match_str,
                            "context": context + f" (~{fscore:.0f}%)",
                            "source": source,
                            "page": page_num,
                            "page_conf": page_conf,
                            "match_type": "fuzzy",
                            "score": score,
                            "position": text.find(match_str)
                        })

        # Final ranking: exact first, then score, then page
        results.sort(key=lambda x: (
            0 if x["match_type"] == "exact" else 1,
            -x["score"],
            x["page"],
            x["position"]
        ))

        return results