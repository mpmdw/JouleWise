# Exhibit F — the machine's process list matching the census pattern (this activation's launch census, 2026-09-13 06:10 PDT; pgrep -fl 'claude|codex', argv truncated to 220 chars)

```
24974 claude
24994 node /opt/homebrew/bin/codex mcp-server -c model="gpt-5.6-sol" -c model_reasoning_effort="high" -c mcp_servers.claude.enabled=false
24996 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex mcp-server -c model="gpt-5.6-sol" -c model_reasoning_effort="high" -c mcp_servers.claude.en
25641 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Service).app/Contents/MacOS/Codex (Service) --type=utility --utility-sub-type=network.mojom.NetworkServi
25643 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Service).app/Contents/MacOS/Codex (Service) --type=utility --utility-sub-type=storage.mojom.StorageServi
25658 /Applications/ChatGPT.app/Contents/Resources/codex -c features.code_mode_host=true app-server --analytics-default-enabled -c plugins.codex-app-tools@openai-bundled.mcp_servers.codex_app.enabled=true
25661 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer) --type=renderer --user-data-dir=/Users/edr/Library/Applica
25662 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer) --type=renderer --user-data-dir=/Users/edr/Library/Applica
25859 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer) --type=renderer --user-data-dir=/Users/edr/Library/Applica
25868 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer) --type=renderer --user-data-dir=/Users/edr/Library/Applica
25871 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer) --type=renderer --user-data-dir=/Users/edr/Library/Applica
25872 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer) --type=renderer --user-data-dir=/Users/edr/Library/Applica
```

Full argv of the app-server helper (pid 25658), for what the process can do:
```
25658 /Applications/ChatGPT.app/Contents/Resources/codex -c features.code_mode_host=true app-server --analytics-default-enabled -c plugins.codex-app-tools@openai-bundled.mcp_servers.codex_app.enabled=true
```

Parent chain of pid 25658 and 25641 (ps -o pid,ppid,comm):
```
  PID  PPID COMM
25633     1 /Applications/ChatGPT.app/Contents/MacOS/ChatGPT
25635     1 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/browser_crashpad_handler
25641 25633 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Service).app/Contents/MacOS/Codex (Service)
25658 25633 /Applications/ChatGPT.app/Contents/Resources/codex
```
