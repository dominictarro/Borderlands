"""
Tests for the Oryx flow.
"""
from flows.oryx_media import extract_oryx_media


def test_stage_oryx_equipment_losses(
    mock_asset_request,
    mock_oryx_persistence_bucket_functions,
    mock_oryx_page_request,
    mock_blocks_import,
    monkeypatch,
):
    """Test the Oryx equipment loss staging flow."""
    from borderlands.oryx.stage import extract, transform
    from flows import oryx_stage

    monkeypatch.setattr(extract, "blocks", mock_blocks_import)
    monkeypatch.setattr(transform, "blocks", mock_blocks_import)
    monkeypatch.setattr(oryx_stage, "blocks", mock_blocks_import)
    oryx_stage.stage_oryx_equipment_losses.on_completion.clear()
    oryx_stage.stage_oryx_equipment_losses()


def test_extract_oryx_media(
    landed_file_path,
    mock_asset_request,
    mock_oryx_persistence_bucket_functions,
    mock_blocks_import,
    monkeypatch,
):
    """Test the Oryx media extraction flow."""
    from borderlands.oryx.media_stage.extract import core, postimg

    monkeypatch.setattr(postimg, "blocks", mock_blocks_import)
    monkeypatch.setattr(core, "blocks", mock_blocks_import)
    extract_oryx_media(landed_file_path.as_posix())
