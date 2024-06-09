# auditboard
AUDITBOARD_URL = "https://usc.auditboardapp.com/api"
API_TOKEN_AUDITBOARD = "1485:111f5973a064d7459c74f2fba77c03"
AUDITABLE_ENTITIES = "/v1/auditable_entities"
AUDITBOARD_CUSTOM_FIELDS = "/v1/custom_fields/query"
USERS = "/v1/users"

# upgaurd
UPGUARD_API_URL_BULK = "https://cyber-risk.upguard.com/api/public/vendors"
UPGUARD_URL_BASE = "https://cyber-risk.upguard.com/api/public"
API_KEY_UPGUARD = '61e7afe3-a286-4272-be1f-dcd248356b1b'
VENDOR_ATTRIBUTES = "/vendor/attributes"

HEADERS_AUDITBOARD = {
    'Authorization': f"Bearer {API_TOKEN_AUDITBOARD}"
}

HEADERS_UPGUARD = {
    'Authorization': API_KEY_UPGUARD
}

AB_TPSP_STATUS = 'ae_custom_select6_option_id'
AB_TPSRA_STATUS = 'auditable_entity_region_id'

SUPPLIER_ID_PATTERN = r"SUP-\d+"

PAYLOAD = {
    "labels": "Workday Active",
    "page_token": 1000
}
