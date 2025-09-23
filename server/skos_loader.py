# server/skos_loader.py
from rdflib import Graph, Namespace, RDF, Literal
from collections import defaultdict
import re, unicodedata, sqlite3, sys, pathlib

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s\-_/\.]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def init_schema(c):
    c.executescript("""
    DROP TABLE IF EXISTS concepts;
    DROP TABLE IF EXISTS prefLabels;
    DROP TABLE IF EXISTS altLabels;
    DROP TABLE IF EXISTS definitions;
    DROP TABLE IF EXISTS scopeNotes;
    DROP TABLE IF EXISTS broader;
    DROP TABLE IF EXISTS narrower;
    DROP TABLE IF EXISTS related;
    DROP TABLE IF EXISTS search_index;

    CREATE TABLE concepts(concept_uri TEXT PRIMARY KEY, notation TEXT, level INTEGER);
    CREATE TABLE prefLabels(concept_uri TEXT, lang TEXT, label TEXT);
    CREATE TABLE altLabels(concept_uri TEXT, lang TEXT, label TEXT);
    CREATE TABLE definitions(concept_uri TEXT, lang TEXT, text TEXT);
    CREATE TABLE scopeNotes(concept_uri TEXT, lang TEXT, text TEXT);
    CREATE TABLE broader(concept_uri TEXT, broader TEXT);
    CREATE TABLE narrower(concept_uri TEXT, narrower TEXT);
    CREATE TABLE related(concept_uri TEXT, related TEXT);

    CREATE TABLE search_index(
      concept_uri TEXT, pref_lang TEXT, pref_label TEXT,
      notation TEXT, norm_text TEXT, score REAL
    );
    CREATE INDEX idx_si_norm ON search_index(norm_text);
    """)

def load(path: str, out="skos.sqlite"):
    g = Graph()
    ext = pathlib.Path(path).suffix.lower()
    if ext in [".json", ".jsonld"]:
        g.parse(path, format="json-ld")
    else:
        # let rdflib auto-detect (ttl, rdf/xml, etc.)
        g.parse(path)

    cn = sqlite3.connect(out); c = cn.cursor()
    init_schema(c)

    concepts = set(g.subjects(RDF.type, SKOS.Concept))
    pref, alt, defs, scopes = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    broader, narrower, related, notation = defaultdict(list), defaultdict(list), defaultdict(list), {}

    for s in concepts:
        for _,_,lab in g.triples((s, SKOS.prefLabel, None)):
            if isinstance(lab, Literal): pref[s].append((lab.language or "und", str(lab)))
        for _,_,lab in g.triples((s, SKOS.altLabel, None)):
            if isinstance(lab, Literal): alt[s].append((lab.language or "und", str(lab)))
        for _,_,txt in g.triples((s, SKOS.definition, None)):
            if isinstance(txt, Literal): defs[s].append((txt.language or "und", str(txt)))
        for _,_,txt in g.triples((s, SKOS.scopeNote, None)):
            if isinstance(txt, Literal): scopes[s].append((txt.language or "und", str(txt)))
        for _,_,notn in g.triples((s, SKOS.notation, None)):
            notation[s] = str(notn)
        for _,_,b in g.triples((s, SKOS.broader, None)): broader[s].append(str(b))
        for _,_,n in g.triples((s, SKOS.narrower, None)): narrower[s].append(str(n))
        for _,_,r in g.triples((s, SKOS.related, None)): related[s].append(str(r))

    for s in concepts:
        level = len(broader[s])  # heuristic depth
        c.execute("INSERT INTO concepts VALUES (?,?,?)", (str(s), notation.get(s), level))
        for lang, lab in pref[s]: c.execute("INSERT INTO prefLabels VALUES (?,?,?)",(str(s),lang,lab))
        for lang, lab in alt[s]:  c.execute("INSERT INTO altLabels VALUES (?,?,?)",(str(s),lang,lab))
        for lang, tx in defs[s]:  c.execute("INSERT INTO definitions VALUES (?,?,?)",(str(s),lang,tx))
        for lang, tx in scopes[s]:c.execute("INSERT INTO scopeNotes VALUES (?,?,?)",(str(s),lang,tx))
        for b in broader[s]:      c.execute("INSERT INTO broader VALUES (?,?)",(str(s),b))
        for n in narrower[s]:     c.execute("INSERT INTO narrower VALUES (?,?)",(str(s),n))
        for r in related[s]:      c.execute("INSERT INTO related VALUES (?,?)",(str(s),r))

        bag = " ".join([*(lab for _,lab in pref[s]), *(lab for _,lab in alt[s]), notation.get(s,"")])
        c.execute("""INSERT INTO search_index VALUES (?,?,?,?,?,?)""",
                  (str(s), (pref[s][0][0] if pref[s] else "und"),
                   (pref[s][0][1] if pref[s] else ""), notation.get(s),
                   norm(bag), 1.0))

    cn.commit(); cn.close()
    print(f"OK: {out} generated")

if __name__ == "__main__":
    load(sys.argv[1] if len(sys.argv) > 1 else "data/taxonomy.jsonld")
