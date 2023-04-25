"""
Tests for the Oryx flow.
"""
from borderlands.oryx.flows import stage_oryx_equipment_losses


def test_stage_oryx_equipment_losses(mock_asset_request, mock_oryx_page_request, mock_oryx_bucket):
    """Test the Oryx equipment loss staging flow."""
    stage_oryx_equipment_losses()
