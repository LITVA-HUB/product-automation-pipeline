from __future__ import annotations

from app.adapters.bitrix.mappers import candidate_to_bitrix_payload
from app.adapters.moysklad.mappers import candidate_to_ms_product
from app.domain.extraction import ExtractionResult
from app.domain.product_candidate import ProductCandidate
from app.services.duplicates.service import DuplicateDetectionService
from app.services.extraction.service import ExtractionService
from app.services.images.service import ImageClassifier, ImageProcessingService
from app.services.naming.service import construct_names
from app.services.rules.product_rules import apply_business_rules
from app.services.validation.service import validate_before_ms, validate_site
from app.workflow.states import WorkflowStatus


class ProductPipeline:
    def __init__(self, image_classifier: ImageClassifier, confidence_threshold: float = 0.75) -> None:
        self.image_classifier = image_classifier
        self.confidence_threshold = confidence_threshold

    def prepare_for_ms(
        self,
        candidate: ProductCandidate,
        extraction: ExtractionResult,
        existing_candidates: list[ProductCandidate],
        prompt_version: str | None = None,
    ) -> ProductCandidate:
        candidate = ExtractionService(self.confidence_threshold).apply_result(
            candidate, extraction, prompt_version=prompt_version
        )
        candidate = ImageProcessingService(
            self.image_classifier, confidence_threshold=self.confidence_threshold
        ).process(candidate)
        candidate = construct_names(candidate)
        candidate = apply_business_rules(candidate)

        duplicate_decision = DuplicateDetectionService(existing_candidates).check(candidate)
        if duplicate_decision.result == "duplicate":
            candidate.human_review_required = True
            if "duplicate" not in candidate.review_reasons:
                candidate.review_reasons.append("duplicate")
            candidate.status = WorkflowStatus.POSSIBLE_DUPLICATE
            return candidate
        if duplicate_decision.result == "possible_duplicate":
            candidate.status = WorkflowStatus.POSSIBLE_DUPLICATE
            return candidate

        validation = validate_before_ms(candidate)
        if not validation.passed:
            candidate.validation_errors = validation.errors
            candidate.status = WorkflowStatus.VALIDATION_FAILED
            candidate.human_review_required = True
            if "validation_failed" not in candidate.review_reasons:
                candidate.review_reasons.append("validation_failed")
            return candidate

        candidate.status = WorkflowStatus.VALIDATED_BEFORE_MS
        return candidate

    async def create_in_ms_and_configure_site(
        self,
        candidate: ProductCandidate,
        ms_client,
        site_client,
        ms_maps: dict,
        bitrix_property_codes: dict[str, str],
    ) -> ProductCandidate:
        if candidate.status != WorkflowStatus.VALIDATED_BEFORE_MS:
            raise ValueError("candidate must be validated before МойСклад write")

        ms_payload = candidate_to_ms_product(candidate, ms_maps)
        ms_product = await ms_client.create_product(ms_payload)
        candidate.ms_product_id = ms_product["id"]
        candidate.ms_product_code = ms_product["code"]
        candidate.status = WorkflowStatus.CREATED_IN_MS
        if candidate.main_image:
            await ms_client.upload_image(candidate.ms_product_id, candidate.main_image)
        candidate.status = WorkflowStatus.MS_VERIFIED

        bitrix_payload = candidate_to_bitrix_payload(candidate, bitrix_property_codes)
        site_product = await site_client.create_or_update_product(bitrix_payload)
        candidate.site_product_id = site_product["id"]
        candidate.status = WorkflowStatus.CREATED_ON_SITE

        await site_client.set_properties(candidate.site_product_id, bitrix_payload["properties"])
        await site_client.upload_images(
            candidate.site_product_id,
            extra=candidate.face_images,
            announce=candidate.interior_images,
            detail=candidate.interior_images,
        )
        await site_client.set_catalog_price(candidate.site_product_id, candidate.site_price)
        await site_client.set_unit_coefficient(candidate.site_product_id, candidate.unit_coefficient)
        await site_client.disable_quantity_accounting(candidate.site_product_id)
        await site_client.set_card_type(candidate.site_product_id, "Ламинат")
        await site_client.set_supplier_name(candidate.site_product_id, candidate.supplier)

        site_validation = validate_site(
            candidate,
            {
                "found_by_ms_code": True,
                "site_price": str(candidate.site_price),
                "unit_coefficient": str(candidate.unit_coefficient),
                "quantity_accounting_enabled": False,
                "site_card_type": "Ламинат",
                "supplier": candidate.supplier,
            },
        )
        if not site_validation.passed:
            candidate.validation_errors = site_validation.errors
            candidate.status = WorkflowStatus.VALIDATION_FAILED
            candidate.human_review_required = True
            return candidate
        candidate.status = WorkflowStatus.SITE_VERIFIED
        return candidate

    async def create_in_ms(self, candidate: ProductCandidate, ms_client, ms_maps: dict) -> ProductCandidate:
        if candidate.status != WorkflowStatus.VALIDATED_BEFORE_MS:
            raise ValueError("candidate must be validated before МойСклад write")

        ms_payload = candidate_to_ms_product(candidate, ms_maps)
        ms_product = await ms_client.create_product(ms_payload)
        candidate.ms_product_id = ms_product["id"]
        candidate.ms_product_code = ms_product["code"]
        candidate.status = WorkflowStatus.CREATED_IN_MS
        if candidate.main_image:
            await ms_client.upload_image(candidate.ms_product_id, candidate.main_image)
        candidate.status = WorkflowStatus.MS_VERIFIED
        return candidate
