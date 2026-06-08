# MoySklad and Bitrix Integration Notes

Reviewed on 2026-06-08.

## МойСклад

Primary API: JSON API Remap 1.2.

Expected resources:

- `entity/product` for product create/update/search;
- `entity/product/metadata` for custom attributes;
- `entity/productfolder` for groups;
- `entity/uom` for units of measure;
- `entity/counterparty` for suppliers;
- product images through the product media endpoints.

Important implementation notes:

- Use `Authorization: Bearer <MOYSKLAD_TOKEN>`.
- Links to related entities are passed as `meta` objects, not bare ids.
- Custom product fields must be discovered once and stored as an attribute map.
- Prices sent to МойСклад must be converted to minor units at the mapper layer.
- The "Выгружено на сайте" flag is a publication step, not a create step.

## 1С-Битрикс / Bitrix24

Preferred integration path: REST API when catalog and iblock methods are
available. Fallbacks are CommerceML import or Playwright only for fields that
cannot be reached by API.

Expected methods and areas:

- `catalog.product.list` to find products by filter;
- `catalog.productProperty.list` to discover product property codes;
- catalog product update methods for trade catalog data;
- iblock element/property methods for site-specific product fields;
- incoming webhook with `catalog` and `iblock` permissions.

Open decision before implementing the write adapter:

- Scenario A: the card is created by existing МойСклад -> Bitrix exchange, and
  this system waits for it by МойСклад code, then configures fields.
- Scenario B: this system creates or updates the card directly.

The architecture supports both scenarios through `SiteClient`.

## Required Discovery Scripts

- `scripts/dump_ms_attributes.py`: export МойСклад product custom attributes.
- `scripts/dump_bitrix_properties.py`: export Bitrix iblock property codes.

These scripts should be implemented before real writes to staging.

## Sources

- https://dev.moysklad.ru/doc/api/remap/1.2/
- https://apidocs.bitrix24.ru/api-reference/catalog/product/catalog-product-list.html
- https://apidocs.bitrix24.ru/api-reference/catalog/product-property/catalog-product-property-list.html
- https://apidocs.bitrix24.com/api-reference/catalog/product/index.html
- https://m.dev.1c-bitrix.ru/api_d7/bitrix/iblock/rest/iblockelementlist.php?print=Y
