-- ACCEPT ALL — look'n'feel: ink glass, one phosphor voice.
-- Theme-scoped: loads only while this theme is active; personal overrides in
-- ~/.config/hypr/looknfeel.lua still load afterwards and win.
--
-- Structure follows arc-reactor's proven config; the character is different:
-- a terminal, not a hologram. Phosphor green carries everything, with one
-- amber stop in the border loop — the cursor passing by.

local active_border_color = {
  colors = {
    "rgba(39ff14ee)", -- phosphor
    "rgba(18a806ee)", -- after-image green
    "rgba(ffb000cc)", -- the amber sliver: a cursor sweeping the frame
    "rgba(18a806ee)",
    "rgba(39ff14ee)", -- close the loop so rotation never seams
  },
  angle = 45,
}

local inactive_border_color = { colors = { "rgba(16240faa)", "rgba(101a0caa)" }, angle = 45 }

hl.config({
  general = {
    gaps_in = 6,
    gaps_out = 12,
    border_size = 2,

    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },

    groupbar = {
      rounding = 6,
      gradient_rounding = 6,
      text_color = "rgb(f2f2ec)",
      text_color_inactive = "rgba(e8e6da90)",
      col = {
        active = "rgba(39ff1426)",
        inactive = "rgba(0d0d0d66)",
      },
    },
  },

  decoration = {
    -- Terminal panels: barely rounded, like a CRT bezel.
    rounding = 7,
    rounding_power = 3,

    active_opacity = 1.0,
    inactive_opacity = 0.96,

    -- Unfocused panels fall back into the scrollback.
    dim_inactive = true,
    dim_strength = 0.15,
    dim_special = 0.55,

    -- The phosphor halo on the focused window: the terminal is the product.
    glow = {
      enabled = true,
      range = 16,
      render_power = 3,
      color = "rgba(39ff1499)",
      color_inactive = "rgba(0d1a0a00)",
    },

    shadow = {
      enabled = true,
      range = 30,
      render_power = 3,
      color = "rgba(02040299)",
      color_inactive = "rgba(0204025e)",
      offset = { 0, 5 },
      scale = 0.97,
    },

    -- Frosted ink. foot paints its own alpha (foot.ini), so the blur has
    -- something real to frost.
    blur = {
      enabled = true,
      size = 7,
      passes = 3,
      new_optimizations = true,
      ignore_opacity = true,
      xray = false,
      noise = 0.015,
      contrast = 1.08,
      brightness = 0.85,
      vibrancy = 0.22,
      vibrancy_darkness = 0.1,
      special = true,
      popups = true,
      popups_ignorealpha = 0.2,
    },
  },

  animations = {
    enabled = true,
  },
})

--------------------------------------------------------------------------------
-- Motion curves: terminal-snappy. Things appear the way output prints —
-- instantly, settling with the smallest overshoot.
--------------------------------------------------------------------------------

hl.curve("crtOut", { type = "bezier", points = { { 0.05, 0.9 }, { 0.1, 1.02 } } })
hl.curve("crtSnap", { type = "bezier", points = { { 0.18, 1.24 }, { 0.34, 1 } } })
hl.curve("crtGlide", { type = "bezier", points = { { 0.22, 1 }, { 0.3, 1 } } })
hl.curve("crtScan", { type = "bezier", points = { { 0.45, 0 }, { 0.15, 1 } } })
hl.curve("crtLinear", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })
hl.curve("crtSpring", { type = "spring", mass = 0.8, stiffness = 360, dampening = 27 })

--------------------------------------------------------------------------------
-- Transitions (`speed` is deciseconds — higher is slower)
--------------------------------------------------------------------------------

hl.animation({ leaf = "global", enabled = true, speed = 4, bezier = "crtGlide" })

-- The signature: the border gradient rotates forever, so the amber "cursor"
-- stop endlessly sweeps the focused frame; the glow breathes on its own period.
hl.animation({ leaf = "borderangle", enabled = true, speed = 100, bezier = "crtLinear", style = "loop" })
hl.animation({ leaf = "glowangle", enabled = true, speed = 61, bezier = "crtLinear", style = "loop" })
hl.animation({ leaf = "border", enabled = true, speed = 6, bezier = "crtGlide" })

-- Windows print on, clear off.
hl.animation({ leaf = "windows", enabled = true, speed = 3.4, spring = "crtSpring" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 3.8, bezier = "crtSnap", style = "popin 88%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 2.2, bezier = "crtOut", style = "popin 93%" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 3.6, spring = "crtSpring" })

hl.animation({ leaf = "fade", enabled = true, speed = 2.4, bezier = "crtScan" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 2, bezier = "crtScan" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.6, bezier = "crtScan" })
hl.animation({ leaf = "fadeSwitch", enabled = true, speed = 2.2, bezier = "crtScan" })
