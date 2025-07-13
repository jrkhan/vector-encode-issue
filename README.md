# 🧠 vector-encode-issue

Automatically embed GitHub issues using sentence-transformers and store their vector representations for similarity search with ChromaDB.

Supports GitHub Actions-based workflows to:

* Generate and persist vector embeddings for each issue
* Detect and comment on similar issues using vector similarity
* Trigger actions via Atlantis-style commands in comments (e.g. `vectorbot embed`)

---

## 🛠️ Features

* 💬 **Comment-based Triggers:** Use `vectorbot embed` as an issue comment generate an embedding
* 🔍 **Similarity Comments:** Automatically links related issues for newly created issues, if it is similar to an existing issue.


---

## 📁 File Structure

```
/src/
  ├— update_embedding_for_issue.py  # Embed and serialize issue
  ├— comment_on_similar.py          # Comment on similar issues
  └— similarity_check.py            # Core logic, also used in unit tests

/tests/
  └— test_similarity.py             # Test similarity detection end-to-end

/embeddings/
  └— issue-<id>.json                # Serialized embedding per issue

.github/workflows/
  ├— update_embeddings.yaml         # Triggers on 'vectorbot embed'
  └— comment_on_similar.yaml        # Posts similarity comment on issue creation
```

---

## 🚀 Getting Started (Local)

### 1. Install dependencies

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -e .
```

### 2. Create a `.env` file (if running locally)

```bash
GITHUB_TOKEN=your_personal_access_token
GITHUB_REPO=your/repo-name
ISSUE_NUMBER=123
```

### 3. Run manually

```bash
python src/update_embedding_for_issue.py
python src/comment_on_similar.py
```

---

## 🤖 GitHub Actions

### Trigger 1: Embed on Command

Workflow: `.github/workflows/update_embeddings.yaml`

* Triggered by:

  * New issue
  * Issue edited
  * Issue comment with: `vectorbot embed`

### Trigger 2: Comment on Similarity

Workflow: `.github/workflows/comment_on_similar.yaml`

* Triggered automatically when a new issue is created
* Uses stored embeddings to find related issues

---

## 🧪 Testing

Run unit tests with:

```bash
pytest
```

Mocks GitHub issues and uses real ChromaDB locally for similarity testing.

---

## 🤝 Contributions Welcome

If you have ideas for additional commands (`vectorbot suggest`, `vectorbot clear`, etc.), feel free to open a PR or issue!
