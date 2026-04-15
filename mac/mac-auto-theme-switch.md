# Mac 定时切换主题

当前 macOS 主题模式只有浅色、深色和自动。自动是根据当地日出日落时间来自动切换的，但是有时候这个不是很准，或者说不是很符合我的习惯。比如下午 5 点可能环境已经有点暗了，但是根据日落时间来算的话，得等到六七点才能自动切到深色模式。所以根据自定义的时间段来切换主题，就很有必要了。

当然有一些第三方软件来做这件事，但是这么小一个事情用第三方软件感觉不太值，于是咨询 claude 后，给出了一个 script 来做这件事，极简。这里我们需要两个文件：刚说的 script 和 plist 文件。后者是 macOS launchd 的 XML 配置文件，用于管理定时任务、常驻服务和事件触发任务。假设我们分别保存为 `/Users/你的用户名/scripts/time-scheduler.sh` 和 `~/Library/LaunchAgents/com.user.theme-scheduler.plist`。

<details>
  <summary>
    点击查看 <code>time-scheduler.sh</code> 内容
  </summary>

```bash
#!/usr/bin/env bash
# Theme Scheduler — auto-generated
# Switches system theme based on time of day
# Light: 9:00 AM | Dark: 4:00 PM
#
# Usage:
#   1. chmod +x theme-scheduler.sh
#   2. Add to crontab:  * * * * * /path/to/theme-scheduler.sh

LOG="/tmp/theme-scheduler.log"
[ -f "$LOG" ] && [ $(wc -c < "$LOG") -gt 100000 ] && > "$LOG"

LIGHT_START_H=9
LIGHT_START_M=0
DARK_START_H=16
DARK_START_M=0

CURRENT_H=$(date +%-H)
CURRENT_M=$(date +%-M)
NOW_MIN=$((CURRENT_H * 60 + CURRENT_M))
LIGHT_MIN=$((LIGHT_START_H * 60 + LIGHT_START_M))
DARK_MIN=$((DARK_START_H * 60 + DARK_START_M))

get_theme() {
  if [ "$LIGHT_MIN" -lt "$DARK_MIN" ]; then
    if [ "$NOW_MIN" -ge "$LIGHT_MIN" ] && [ "$NOW_MIN" -lt "$DARK_MIN" ]; then
      echo "light"
    else
      echo "dark"
    fi
  else
    if [ "$NOW_MIN" -ge "$DARK_MIN" ] && [ "$NOW_MIN" -lt "$LIGHT_MIN" ]; then
      echo "dark"
    else
      echo "light"
    fi
  fi
}

THEME=$(get_theme)

# --- macOS ---
if [[ "$OSTYPE" == "darwin"* ]]; then
  if [ "$THEME" = "dark" ]; then
    osascript -e 'tell app "System Events" to tell appearance preferences to set dark mode to true'
  else
    osascript -e 'tell app "System Events" to tell appearance preferences to set dark mode to false'
  fi
  echo "[$(date)] macOS theme set to: $THEME"
  exit 0
fi

# --- Linux (GNOME) ---
if command -v gsettings &> /dev/null; then
  if [ "$THEME" = "dark" ]; then
    gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
    gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'
  else
    gsettings set org.gnome.desktop.interface color-scheme 'prefer-light'
    gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita'
  fi
  echo "[$(date)] GNOME theme set to: $THEME"
  exit 0
fi

echo "[$(date)] Unsupported desktop environment."  
exit 1
```

</details>

<details>
  <summary>
    点击查看 <code>com.user.theme-scheduler.plist</code> 内容
  </summary>

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.theme-scheduler</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/alan/scripts/time-scheduler.sh</string>
    </array>

    <!-- Run every 60 seconds -->
    <key>StartInterval</key>
    <integer>60</integer>

    <!-- Run at startup -->
    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/tmp/theme-scheduler.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/theme-scheduler.log</string>
</dict>
</plist>
```

</details>

然后 load 即可：

```bash
launchctl load ~/Library/LaunchAgents/com.user.theme-scheduler.plist
```

随后检查是否 load 好了：

```bash
% launchctl list|grep theme
-	0	com.user.theme-scheduler
```

也可以直接检查上述配置的日志文件。

如果要停止，那么直接将 `load` 换成 `unload` 即可。
