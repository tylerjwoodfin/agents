# macOS

## Closing GUI apps

- Prefer AppleScript quit: `osascript -e 'quit app "Spotify"'` (swap the app name).
- Do not treat bare `pkill -i AppName` as proof of success. On macOS it often signals helper processes, exits 0, and leaves the main app running.
- Before claiming an app is closed, re-check with `pgrep -ix AppName` (or `pgrep -x Spotify`). If it is still there, quit again (`osascript` or `killall`) and re-check. Never claim success from a kill command alone.
