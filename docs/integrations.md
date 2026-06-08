# MoySklad Integration Notes

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
- The "Выгружено на сайте" flag is included as `false` by default when the
  attribute map is available. Setting it to `true` is a separate publication
  action after approval.

## Website Synchronization

The primary production path does not require direct Bitrix writes. Products are
created and configured in МойСклад; the existing site synchronization imports
them. The МойСклад custom field `Выгружено на сайте` controls site activation:

- default `false`: product remains inactive/not intentionally published;
- explicit `true`: product may become active after approval and synchronization.

Some products must be created only in МойСклад. The default publication mode is
therefore `ms_only`; operators must explicitly choose site activation.

## Optional Bitrix Diagnostics

The repository keeps optional Bitrix REST adapter code for diagnostics or a
future fallback, but direct Bitrix API writes are not part of the default
production write-flow.

## Required Discovery Scripts

- `scripts/dump_ms_attributes.py`: export МойСклад product custom attributes.
- `scripts/dump_bitrix_properties.py`: optional diagnostic export of Bitrix
  iblock property codes.

These scripts should be implemented before real writes to staging.

## Sources

- https://dev.moysklad.ru/doc/api/remap/1.2/
- https://apidocs.bitrix24.ru/api-reference/catalog/product/catalog-product-list.html
- https://apidocs.bitrix24.ru/api-reference/catalog/product-property/catalog-product-property-list.html
- https://apidocs.bitrix24.com/api-reference/catalog/product/index.html
- https://m.dev.1c-bitrix.ru/api_d7/bitrix/iblock/rest/iblockelementlist.php?print=Y
