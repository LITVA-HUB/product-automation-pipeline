from app.domain.extraction import ImageClassification
from app.services.images.service import ImageProcessingService
from tests.unit.helpers import make_candidate


class FakeClassifier:
    def classify_image_path(self, image_path: str) -> ImageClassification:
        if "interior" in image_path:
            return ImageClassification(image_type="interior", confidence=0.95)
        if "face" in image_path:
            return ImageClassification(image_type="face", confidence=0.9)
        return ImageClassification(image_type="main", confidence=0.9)


def test_image_processing_deduplicates_and_groups_images():
    candidate = make_candidate(
        raw_images=["main.jpg", "face-1.jpg", "face-1.jpg", "interior.jpg"],
        main_image=None,
    )

    updated = ImageProcessingService(FakeClassifier()).process(candidate)

    assert updated.main_image == "main.jpg"
    assert updated.face_images == ["face-1.jpg"]
    assert updated.interior_images == ["interior.jpg"]
    assert updated.faces_count.value == 1


def test_image_processing_marks_uncertain_classification_for_review():
    class UncertainClassifier:
        def classify_image_path(self, image_path: str) -> ImageClassification:
            return ImageClassification(image_type="unknown", confidence=0.2, warning="unclear")

    candidate = make_candidate(raw_images=["x.jpg"])

    updated = ImageProcessingService(UncertainClassifier(), confidence_threshold=0.75).process(
        candidate
    )

    assert updated.human_review_required is True
    assert "image_classification_uncertain" in updated.review_reasons
