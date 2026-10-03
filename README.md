# Accept All — Omarchy theme

Phosphor green on ink. The OS skin for [wearacceptall.com](https://wearacceptall.com):
merch for people who ship with AI.

- **Wallpapers are generated, not downloaded** — `python3 tools/generate_art.py`
  (needs python-pillow; fonts ship in `tools/fonts/`, OFL).
- `1-phosphor` is **animated** via the `john.background` plugin's `motion.json`:
  the mark's glow breathes, the wordmark cursor blinks, and a faint CRT band
  drifts down the screen. Without the plugin it renders as a normal still.
- The focused window's border gradient rotates forever, with one amber stop —
  a cursor endlessly sweeping the frame.
- `foot.ini` ships real `alpha=0.87` so Hyprland's blur has something to frost
  (opacity rules alone dim without frosting).

## Install

```bash
./install.sh
omarchy theme set accept-all
```
