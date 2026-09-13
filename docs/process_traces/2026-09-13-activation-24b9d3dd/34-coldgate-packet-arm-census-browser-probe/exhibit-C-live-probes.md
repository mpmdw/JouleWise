# Exhibit C — live probes on this machine, 2026-09-13 ~08:45 PDT (read-only pgrep; the four census patterns exactly as coded; exit code is pgrep's own; argv truncated to 160 chars)

## keep-awake: /usr/bin/pgrep -x "caffeinate"
```
pgrep exit=1 lines=0
```

## agent: /usr/bin/pgrep -lf "codex|claude|t3"
```
24974 claude
24994 node /opt/homebrew/bin/codex mcp-server -c model="gpt-5.6-sol" -c model_reasoning_effort="high" -c mcp_servers.claude.enabled=false
24996 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex mcp-server -c model="gpt-5.6-so
25641 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Service).app/Contents/MacOS/Codex (Service) 
25643 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Service).app/Contents/MacOS/Codex (Service) 
25658 /Applications/ChatGPT.app/Contents/Resources/codex -c features.code_mode_host=true app-server --analytics-default-enabled -c plugins.codex-app-tools@opena
25661 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer
25662 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer
25716 /Users/edr/.codex/computer-use/Codex Computer Use.app/Contents/MacOS/SkyComputerUseService
25859 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer
25868 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer
25871 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer
25872 /Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/Codex (Renderer).app/Contents/MacOS/Codex (Renderer
29816 /Applications/Claude.app/Contents/Frameworks/Claude Helper.app/Contents/MacOS/Claude Helper --type=utility --utility-sub-type=network.mojom.NetworkService
29828 /Applications/Claude.app/Contents/Frameworks/Claude Helper (Renderer).app/Contents/MacOS/Claude Helper (Renderer) --type=renderer --user-data-dir=/Users/e
29835 /Applications/Claude.app/Contents/Frameworks/Claude Helper (Renderer).app/Contents/MacOS/Claude Helper (Renderer) --type=renderer --user-data-dir=/Users/e
29861 /Applications/Claude.app/Contents/Frameworks/Claude Helper (Renderer).app/Contents/MacOS/Claude Helper (Renderer) --type=renderer --user-data-dir=/Users/e
29862 /Applications/Claude.app/Contents/Frameworks/Claude Helper.app/Contents/MacOS/Claude Helper --type=utility --utility-sub-type=audio.mojom.AudioService --l
29863 /Applications/Claude.app/Contents/Frameworks/Claude Helper.app/Contents/MacOS/Claude Helper --type=utility --utility-sub-type=video_capture.mojom.VideoCap
30091 /Applications/Claude.app/Contents/Frameworks/Squirrel.framework/Resources/ShipIt com.anthropic.claudefordesktop.ShipIt /Users/edr/Library/Caches/com.anthr
31413 node /opt/homebrew/bin/codex mcp-server -c model="gpt-5.6-sol" -c model_reasoning_effort="high" -c mcp_servers.claude.enabled=false
31422 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex mcp-server -c model="gpt-5.6-so
pgrep exit=0 lines=22
```

## browser: /usr/bin/pgrep -lf "Safari|Google Chrome|Chromium|Firefox|browser automation"
```
995 /System/Cryptexes/App/usr/libexec/SafariBookmarksSyncAgent
1352 /System/Volumes/Preboot/Cryptexes/App/System/Applications/Safari.app/Contents/Extensions/SafariWidgetExtension.appex/Contents/MacOS/SafariWidgetExtension -
1457 /System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/XPCServices/com.apple.SafariPlatformSupport.Helper.xpc/Contents/MacOS/com.appl
1458 /System/Library/PrivateFrameworks/SafariFoundation.framework/Versions/A/XPCServices/CredentialProviderExtensionHelper.xpc/Contents/MacOS/CredentialProvider
1481 /System/Volumes/Preboot/Cryptexes/App/System/Applications/Safari.app/Contents/Extensions/SafariLinkExtension.appex/Contents/MacOS/SafariLinkExtension -Laun
1794 /System/Library/PrivateFrameworks/SafariSafeBrowsing.framework/com.apple.Safari.SafeBrowsing.Service
3644 /System/Cryptexes/App/usr/libexec/SafariLaunchAgent
17142 /System/Library/PrivateFrameworks/SafariFoundation.framework/Versions/A/XPCServices/SafariConfigurationSubscriber.xpc/Contents/MacOS/SafariConfigurationSu
24781 /Applications/Firefox.app/Contents/MacOS/firefox
24783 /Applications/Firefox.app/Contents/MacOS/crashhelper 24781 gecko-crash-server-pipe.24781 /private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/Temporar
24784 /Applications/Firefox.app/Contents/MacOS/gpu-helper.app/Contents/MacOS/Firefox GPU Helper -parentBuildID 20260903215306 -prefsHandle 0:43216 -prefMapHandl
24785 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container -parentBuildID 20260903215306 -prefsHandle 0:43283 -prefMapH
24787 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container -parentBuildID 20260903215306 -prefsHandle 0:43506 -prefMapH
24791 /System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/XPCServices/com.apple.SafariPlatformSupport.Helper.xpc/Contents/MacOS/com.app
24792 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container -isForBrowser -prefsHandle 0:44219 -prefMapHandle 1:298091 -
24793 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container -parentBuildID 20260903215306 -sandboxingKind 0 -prefsHandle
24794 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container -isForBrowser -prefsHandle 0:60443 -prefMapHandle 1:298091 -
24804 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container -parentBuildID 20260903215306 -sandboxingKind 1 -prefsHandle
24813 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container -isForBrowser -prefsHandle 0:51967 -prefMapHandle 1:298091 -
24880 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container -isForBrowser -prefsHandle 0:52130 -prefMapHandle 1:298091 -
24892 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container -isForBrowser -prefsHandle 0:52130 -prefMapHandle 1:298091 -
25700 /System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/XPCServices/com.apple.SafariPlatformSupport.Helper.xpc/Contents/MacOS/com.app
pgrep exit=0 lines=22
```

## monitor: /usr/bin/pgrep -lf "powermetrics|window-chain|run_campaign|tail -f|watch"
```
574 /usr/libexec/watchdogd
pgrep exit=0 lines=1
```

## Browser-pattern hits classified (ps -o pid,ppid,comm): system services under /System/… versus the operator's GUI browser under /Applications/…
```
  995     1 /System/Cryptexes/App/usr/libexec/SafariBookmarksSyncAgent
 1352     1 /System/Volumes/Preboot/Cryptexes/App/System/Applications/Safari.app/Contents/Extensions/SafariWidgetExtension.appex/Contents/MacOS/Safari
 1457     1 /System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/XPCServices/com.apple.SafariPlatformSupport.Helper.xpc/Conten
 1458     1 /System/Library/PrivateFrameworks/SafariFoundation.framework/Versions/A/XPCServices/CredentialProviderExtensionHelper.xpc/Contents/MacOS/C
 1481     1 /System/Volumes/Preboot/Cryptexes/App/System/Applications/Safari.app/Contents/Extensions/SafariLinkExtension.appex/Contents/MacOS/SafariLi
 1794     1 /System/Library/PrivateFrameworks/SafariSafeBrowsing.framework/com.apple.Safari.SafeBrowsing.Service
 3644     1 /System/Cryptexes/App/usr/libexec/SafariLaunchAgent
17142     1 /System/Library/PrivateFrameworks/SafariFoundation.framework/Versions/A/XPCServices/SafariConfigurationSubscriber.xpc/Contents/MacOS/Safar
24781     1 /Applications/Firefox.app/Contents/MacOS/firefox
24783     1 /Applications/Firefox.app/Contents/MacOS/crashhelper
24784 24781 /Applications/Firefox.app/Contents/MacOS/gpu-helper.app/Contents/MacOS/Firefox GPU Helper
24785 24781 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container
24787 24781 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container
24791     1 /System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/XPCServices/com.apple.SafariPlatformSupport.Helper.xpc/Conten
24792 24781 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container
24793 24781 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container
24794 24781 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container
24804 24781 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container
24813 24781 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container
24880 24781 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container
24892 24781 /Applications/Firefox.app/Contents/MacOS/plugin-container.app/Contents/MacOS/plugin-container
25700     1 /System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/XPCServices/com.apple.SafariPlatformSupport.Helper.xpc/Conten
```

## Monitor-pattern hit classified
```
  574     1 root /usr/libexec/watchdogd
```

Note (magistrate): Firefox (pid 24781) is the operator's own browser, open on this machine at this hour; it is a correct match. The Safari entries under /System/… and /usr/libexec/watchdogd are launchd-owned system services present on every macOS login with no browser or monitor open. The agent-pattern hits are Ed's interactive session, the ChatGPT and Claude desktop app helpers, and this activation's own MCP servers and seats (all expected on a desk day; irrelevant to this packet).
