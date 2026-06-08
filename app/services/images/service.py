from __future__ import annotations

from typing import Protocol

from app.domain.extraction import ImageClassification
from app.domain.product_candidate import FieldWithConfidence, ProductCandidate


class ImageClassifier(Protocol):
    def classify_image_path(self, image_path: str) -> ImageClassification: ...


class ImageProcessingService:
    def __init__(self, classifier: ImageClassifier, confidence_threshold: float = 0.75) -> None:
        self.classifier = classifier
        self.confidence_threshold = confidence_threshold

    def process(self, candidate: ProductCandidate) -> ProductCandidate:
        seen: set[str] = set()
        candidate.face_images = []
        candidate.interior_images = []
        for image_path in candidate.raw_images:
            if image_path in seen:
                continue
            seen.add(image_path)
            classification = self.classifier.classify_image_path(image_path)
            if classification.confidence < self.confidence_threshold:
                self._mark_review(candidate, "image_classification_uncertain")
                continue
            if classification.image_type == "main" and candidate.main_image is None:
                candidate.main_image = image_path
            elif classification.image_type == "face":
                candidate.face_images.append(image_path)
            elif classification.image_type == "interior":
                candidate.interior_images.append(image_path)
            else:
                self._mark_review(candidate, "image_classification_uncertain")

        candidate.faces_count = FieldWithConfidence(
            value=len(candidate.face_images),
            confidence=1.0,
            source="image_processing",
        )
        if candidate.main_image is None and candidate.face_images:
            candidate.main_image = candidate.face_images[0]
        return candidate

    def _mark_review(self, candidate: ProductCandidate, reason: str) -> None:
        candidate.human_review_required = True
        if reason not in candidate.review_reasons:
            candidate.review_reasons.append(reason)
