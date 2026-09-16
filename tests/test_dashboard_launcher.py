from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from licensing import dashboard_launcher


def test_desktop_launcher_hides_shell_and_captures_output(monkeypatch):
    run = Mock(return_value=SimpleNamespace(returncode=0))
    monkeypatch.setattr(dashboard_launcher.subprocess, 'run', run)
    monkeypatch.setattr(dashboard_launcher.subprocess, 'CREATE_NO_WINDOW', 0x08000000, raising=False)
    assert dashboard_launcher.launch() == 0
    args, options = run.call_args
    assert args[0][0] == 'powershell.exe'
    assert args[0][-1] == '-Open'
    assert Path(args[0][-2]).name == 'Update-Dashboard.ps1'
    assert options['creationflags'] == 0x08000000
    assert options['capture_output'] is True
    assert options['timeout'] == 150


def test_installer_uses_validated_dependency_constraints():
    root = Path(__file__).parents[1] / 'atpa-v1'
    pins = (root / 'runtime/dependencies.txt').read_text().splitlines()
    assert 'windows-mcp==0.8.5' in pins
    assert 'cryptography==50.0.1' in pins
    assert 'fastmcp==4.0.4' in pins
    installer = (root / 'Install-System.ps1').read_text(encoding='utf-8-sig')
    assert installer.count("--python 3.12 --constraints 'runtime/dependencies.txt'") == 2
    assert 'Push-Location -LiteralPath $packageRoot' in installer
    assert '}finally{Pop-Location}' in installer
