from pathlib import Path

from winbridge.configure import configure_mcp


def test_configure_preserves_other_settings_and_replaces_only_winbridge(tmp_path: Path):
    executable = tmp_path / "winbridge.exe"
    executable.write_bytes(b"test")
    config = tmp_path / "config.toml"
    config.write_text(
        'model = "example"\n\n[mcp_servers.other]\ncommand = "other.exe"\n\n'
        '[mcp_servers.winbridge]\ncommand = "old.exe"\n',
        encoding="utf-8",
    )
    result = configure_mcp(str(executable), str(tmp_path))
    updated = config.read_text(encoding="utf-8")
    assert result["ok"] is True
    assert 'model = "example"' in updated
    assert '[mcp_servers.other]' in updated
    assert updated.count('[mcp_servers.winbridge]') == 1
    assert str(executable).replace("\\", "\\\\") in updated
