# ============================================================================
# ANVIL UPLINK - DO NOT CHANGE!!!
# ============================================================================

from anvil.tables import app_tables
import anvil.server
import controller
import data_access
import logics
import schemas
import services

anvil.server.connect("server_ECKX4NUIL4QX54CHZGWUXM5R-DJLAASI6MOPSH76S")

# ============================================================================
# PUBLIC API - START PROGRAM HERE:
# ============================================================================

test = anvil.server.call("get_skus_for_material", document_id="vin_mmat_0001")

print (test)
