# Silver Reference Models Validation

## Models

- Product groups: 6 validated records
- Devices: 30 validated records
- Sites: 3 validated records
- Equipment: 24 validated records

## Controls

- Required and unique business keys
- Product-group restriction flag converted to Boolean
- Device target yield converted to Decimal(9,6)
- Equipment capacity converted to Integer
- Device-to-product-group relationship validation
- Equipment-to-site relationship validation
- Production-lot reference-integrity validation
- Empty but operational reference quarantine table
- Repeatable snapshot reruns

## Result

Status: PASSED