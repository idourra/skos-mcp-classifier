# server/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Optional
import sqlite3

app = FastAPI(title="SKOS MCP Server")

def db():
    return sqlite3.connect("skos.sqlite", check_same_thread=False)

class SearchQuery(BaseModel):
    query: str
    lang: str = "es"
    k: int = 10

class ConceptHit(BaseModel):
    concept_uri: str
    prefLabel: Dict[str, str]
    altLabel: Dict[str, List[str]]
    notation: Optional[str]
    ancestors: List[str]
    descendants: List[str]
    score: float

class SearchResponse(BaseModel):
    hits: List[ConceptHit]

class GetContextQuery(BaseModel):
    concept_uri: str

class ConceptContext(BaseModel):
    concept_uri: str
    prefLabel: Dict[str, str]
    altLabel: Dict[str, List[str]]
    definition: Dict[str, str]
    scopeNote: Dict[str, str]
    notation: Optional[str]
    broader: List[str]
    narrower: List[str]
    related: List[str]

class ValidateNotationQuery(BaseModel):
    notation: str

class ValidateNotationResponse(BaseModel):
    exists: bool
    concept_uri: Optional[str] = None
    prefLabel: Optional[Dict[str, str]] = None
    level: Optional[int] = None

@app.post("/tools/search_concepts", response_model=SearchResponse)
def search_concepts(q: SearchQuery):
    cn = db(); c = cn.cursor()
    nquery = "%" + q.query.lower() + "%"
    c.execute("""
      SELECT concept_uri, pref_lang, pref_label, notation, score
      FROM search_index
      WHERE norm_text LIKE ?
      ORDER BY score DESC
      LIMIT ?""", (nquery, q.k))
    rows = c.fetchall()
    hits=[]
    for uri, _, _, notation, score in rows:
        c2 = cn.cursor()
        c2.execute("SELECT lang,label FROM prefLabels WHERE concept_uri=?", (uri,))
        pref = {lang: lab for lang, lab in c2.fetchall()}
        c2.execute("SELECT lang,label FROM altLabels WHERE concept_uri=?", (uri,))
        alts={}
        for lang,lab in c2.fetchall():
            alts.setdefault(lang,[]).append(lab)
        c2.execute("SELECT broader FROM broader WHERE concept_uri=?", (uri,))
        ancestors=[r[0] for r in c2.fetchall()]
        c2.execute("SELECT narrower FROM narrower WHERE concept_uri=?", (uri,))
        descendants=[r[0] for r in c2.fetchall()]
        hits.append(ConceptHit(
            concept_uri=uri, prefLabel=pref, altLabel=alts, notation=notation,
            ancestors=ancestors, descendants=descendants, score=score
        ))
    cn.close()
    return SearchResponse(hits=hits)

@app.post("/tools/get_context", response_model=ConceptContext)
def get_context(q: GetContextQuery):
    cn=db(); c=cn.cursor()
    c.execute("SELECT notation FROM concepts WHERE concept_uri=?", (q.concept_uri,))
    row=c.fetchone(); notation=row[0] if row else None
    c.execute("SELECT lang,label FROM prefLabels WHERE concept_uri=?", (q.concept_uri,))
    pref={lang:lab for lang,lab in c.fetchall()}
    c.execute("SELECT lang,label FROM altLabels WHERE concept_uri=?", (q.concept_uri,))
    alts={}
    for lang,lab in c.fetchall(): alts.setdefault(lang,[]).append(lab)
    c.execute("SELECT lang,text FROM definitions WHERE concept_uri=?", (q.concept_uri,))
    defs={lang:tx for lang,tx in c.fetchall()}
    c.execute("SELECT lang,text FROM scopeNotes WHERE concept_uri=?", (q.concept_uri,))
    scopes={lang:tx for lang,tx in c.fetchall()}
    c.execute("SELECT broader FROM broader WHERE concept_uri=?", (q.concept_uri,))
    broader=[r[0] for r in c.fetchall()]
    c.execute("SELECT narrower FROM narrower WHERE concept_uri=?", (q.concept_uri,))
    narrower=[r[0] for r in c.fetchall()]
    c.execute("SELECT related FROM related WHERE concept_uri=?", (q.concept_uri,))
    related=[r[0] for r in c.fetchall()]
    cn.close()
    return ConceptContext(
      concept_uri=q.concept_uri, prefLabel=pref, altLabel=alts,
      definition=defs, scopeNote=scopes, notation=notation,
      broader=broader, narrower=narrower, related=related
    )

@app.post("/tools/validate_notation", response_model=ValidateNotationResponse)
def validate_notation(q: ValidateNotationQuery):
    cn=db(); c=cn.cursor()
    c.execute("SELECT rowid, level FROM concepts WHERE notation=?", (q.notation,))
    row=c.fetchone()
    if not row:
        cn.close(); return ValidateNotationResponse(exists=False)
    _, level = row
    c.execute("SELECT concept_uri FROM concepts WHERE notation=?", (q.notation,))
    concept_uri=c.fetchone()[0]
    c.execute("SELECT lang,label FROM prefLabels WHERE concept_uri=?", (concept_uri,))
    pref={lang:lab for lang,lab in c.fetchall()}
    cn.close()
    return ValidateNotationResponse(exists=True, concept_uri=concept_uri, prefLabel=pref, level=level)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
