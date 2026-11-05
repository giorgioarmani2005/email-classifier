import re
import numpy as np
import shap
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from pathlib import Path

_DEFAULT_CKPT = Path(__file__).resolve().parent / "roberta_triage.pt"

MODEL_NAME = "roberta-base"
MAX_LEN = 256
DROPOUT = 0.3
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

DISPLAY_STOPWORDS = {
    ",", ".", ":", ";", "!", "?", "-", "/", "(", ")", "'s", "'t",
    "to", "the", "a", "an", "of", "and", "in", "on", "at", "is", "are",
    "was", "were", "be", "been", "with", "for", "by", "from", "as",
    "that", "this", "it", "its", "these", "those", "we", "our",
    "subject:", "body:", "re:", "fwd:", "fw:",
}


class MultiHeadRoberta(nn.Module):
    def __init__(self, n_triage, n_priority, n_risk, n_should, dropout=DROPOUT):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(MODEL_NAME, add_pooling_layer=False)
        h = self.encoder.config.hidden_size
        self.dropout = nn.Dropout(dropout)
        self.head_triage = nn.Linear(h, n_triage)
        self.head_priority = nn.Linear(h, n_priority)
        self.head_risk = nn.Linear(h, n_risk)
        self.head_should = nn.Linear(h, n_should)

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = self.dropout(out.last_hidden_state[:, 0])
        return {
            "logits_triage": self.head_triage(pooled),
            "logits_priority": self.head_priority(pooled),
            "logits_risk": self.head_risk(pooled),
            "logits_should": self.head_should(pooled),
        }


def _remove_citations(text: str) -> str:
    text = re.split(r"(?:[-–—]\s*){2,}original\s+message", text, flags=re.I)[0]
    text = re.split(r"(?:[-–—]\s*){2,}forwarded\s+by", text, flags=re.I)[0]
    text = re.split(r"this\s+email\s+and\s+any\s+attach", text, flags=re.I)[0]
    text = re.split(r"confidentiality\s+notice", text, flags=re.I)[0]
    return text


def parse_content(content: str) -> str:
    content = _remove_citations(content)
    subject_m = re.search(r"^Subject:\s*(.+?)(?=\n\w+:|\Z)", content, re.I | re.M)
    body_m = re.search(r"^Body:\s*(.+)$", content, re.I | re.M | re.DOTALL)

    # У нас вообще никогда нету в письме Body и Subject, вообще возможно стоит подправить бэк, чтобы это добавить, но хотя бы так сделал пока
    if subject_m or body_m:
        parts = []
        if subject_m:
            parts.append("Subject: " + subject_m.group(1).strip())
        if body_m:
            parts.append("Body: " + body_m.group(1).strip())
    else:
        parts = ["Body: " + content.strip()]

    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def word_indices_in_content(content: str, words: list) -> list[int]:
    tokens = content.split()
    low_tokens = [t.lower() for t in tokens]

    search_start = 0
    for i, t in enumerate(low_tokens):
        if t in ("subject:", "body:"):
            search_start = i
            break

    positions = []
    seen = set()
    counts = {}
    for entry in words:
        if isinstance(entry, dict):
            w = entry["word"].lower()
            nth = entry["nth_in_cleaned"]
        else:
            w = entry.lower()
            nth = counts.get(w, 0)
            counts[w] = nth + 1
        if not w:
            continue
        match_count = 0
        found = -1
        for i in range(search_start, len(low_tokens)):
            if w in low_tokens[i]:
                if match_count == nth:
                    found = i
                    break
                match_count += 1
        if found == -1 or found in seen:
            continue
        seen.add(found)
        positions.append(found)
    return positions

class TriageInference:
    def __init__(self, ckpt_path: str = str(_DEFAULT_CKPT), n_shap: int = 200):
        self.n_shap = n_shap
        ckpt = torch.load(ckpt_path, map_location=DEVICE)
        self.triage_labels = ckpt["triage_labels"]
        self.priority_labels = ckpt["priority_labels"]
        self.risk_labels = ckpt["risk_labels"]
        self.should_labels = ckpt["should_labels"]
        self.temps = ckpt.get("temps", {})
        self.thresholds = ckpt.get("thresholds", {})
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = MultiHeadRoberta(
            n_triage=len(self.triage_labels),
            n_priority=len(self.priority_labels),
            n_risk=len(self.risk_labels),
            n_should=len(self.should_labels),
        ).to(DEVICE)
        self.model.load_state_dict(ckpt["model_state"])
        self.model.eval()
        self._masker = shap.maskers.Text(r"\W+")
        self._explainers = {}

    def _labels_for(self, head: str) -> list:
        return {
            "triage": self.triage_labels,
            "priority": self.priority_labels,
            "risk": self.risk_labels,
            "should": self.should_labels,
        }[head]

    def _probs(self, cleaned_texts, head: str, T: float = 1.0) -> np.ndarray:
        T = max(float(T), 1e-3)
        enc = self.tokenizer(
            list(cleaned_texts), max_length=MAX_LEN, truncation=True,
            padding=True, return_tensors="pt",
        ).to(DEVICE)
        amp = DEVICE.type == "cuda"
        dtype = torch.bfloat16 if amp else torch.float32
        with torch.no_grad(), torch.autocast(device_type="cuda", dtype=dtype, enabled=amp):
            out = self.model(enc["input_ids"], enc["attention_mask"])
        return torch.softmax(out[f"logits_{head}"].float() / T, dim=-1).cpu().numpy()

    def _predict_from_probs(self, probs: np.ndarray, head: str) -> dict:
        labels = self._labels_for(head)
        if head in self.thresholds:
            t = np.array(self.thresholds[head])
            idx = int(probs.argmax())
            if probs[idx] < t[idx]:
                idx = int((probs - t).argmax())
        else:
            idx = int(probs.argmax())
        return {
            "label": str(labels[idx]).lower() if isinstance(labels[idx], bool) else labels[idx],
            "confidence": float(probs[idx]),
            "all_probs": {n: float(p) for n, p in zip(labels, probs)},
        }

    def _predict_head(self, cleaned: str, head: str) -> dict:
        probs = self._probs([cleaned], head, T=self.temps.get(head, 1.0))[0]
        return self._predict_from_probs(probs, head)

    def _predict_all(self, cleaned: str) -> dict:
        enc = self.tokenizer(
            [cleaned], max_length=MAX_LEN, truncation=True,
            padding=True, return_tensors="pt",
        ).to(DEVICE)
        amp = DEVICE.type == "cuda"
        dtype = torch.bfloat16 if amp else torch.float32
        with torch.no_grad(), torch.autocast(device_type="cuda", dtype=dtype, enabled=amp):
            out = self.model(enc["input_ids"], enc["attention_mask"])
        result = {}
        for head, key in (("triage", "triage"), ("priority", "priority"), ("risk", "risk"), ("should", "should_process")):
            T = max(float(self.temps.get(head, 1.0)), 1e-3)
            probs = torch.softmax(out[f"logits_{head}"].float() / T, dim=-1).cpu().numpy()[0]
            result[key] = self._predict_from_probs(probs, head)
        return result

    def _get_explainer(self, head: str) -> shap.Explainer:
        if head in self._explainers:
            return self._explainers[head]
        T = self.temps.get(head, 1.0)
        labels = self._labels_for(head)
        def predict_fn(texts):
            return self._probs(texts, head, T=T)
        exp = shap.Explainer(predict_fn, self._masker, output_names=labels, num_samples=self.n_shap)
        self._explainers[head] = exp
        return exp

    def explain(self, cleaned: str, head: str = "risk", top_k: int = 5, pred: dict = None) -> list:
        labels = self._labels_for(head)
        if pred is None:
            pred = self._predict_head(cleaned, head)
        pred_idx = labels.index(pred["label"])
        sv = self._get_explainer(head)([cleaned])
        vals = np.array(sv.values)[0]
        tokens = list(sv.data[0])

        word_seen = {}
        items = []
        for i, (tok, v) in enumerate(zip(tokens, vals[:, pred_idx])):
            tok = str(tok).strip()
            if not tok or tok.lower() in DISPLAY_STOPWORDS:
                continue
            w = tok.lower()
            nth = word_seen.get(w, 0)
            word_seen[w] = nth + 1
            items.append({"word": tok, "nth_in_cleaned": nth, "contribution": float(v)})
        items.sort(key=lambda x: -abs(x["contribution"]))
        return items[:top_k]


    def predict(self, content: str, top_k: int = 5) -> dict:
        cleaned = parse_content(content)
        result = self._predict_all(cleaned)
        explanation = self.explain(cleaned, "risk", top_k=max(top_k * 10, 50), pred=result["risk"])
        positions = word_indices_in_content(content, explanation)
        result["shap_indices"] = sorted(positions[:top_k])
        return result

    def __call__(self, content: str, **kwargs) -> dict:
        return self.predict(content, **kwargs)