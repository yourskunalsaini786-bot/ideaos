---
name: IdeaOS
colors:
  surface: '#0f131c'
  surface-dim: '#0f131c'
  surface-bright: '#353942'
  surface-container-lowest: '#0a0e16'
  surface-container-low: '#181c24'
  surface-container: '#1c2028'
  surface-container-high: '#262a33'
  surface-container-highest: '#31353e'
  on-surface: '#dfe2ee'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#dfe2ee'
  inverse-on-surface: '#2c3039'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
  tertiary: '#d0bcff'
  on-tertiary: '#3c0091'
  tertiary-container: '#a078ff'
  on-tertiary-container: '#340080'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#0f131c'
  on-background: '#dfe2ee'
  surface-variant: '#31353e'
typography:
  display-xl:
    fontFamily: Geist
    fontSize: 56px
    fontWeight: '600'
    lineHeight: 64px
    letterSpacing: -0.03em
  display-xl-mobile:
    fontFamily: Geist
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0em
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.02em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.03em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '400'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system defines an authoritative, high-precision content operating system. It merges technical command-center aesthetics with refined creative studio tooling. Designed for multi-platform creators, growth teams, and editorial strategists, the experience conveys calm mastery over complex generative workflows, signal extraction, and content repurposing matrices.

The visual style combines **Modern Minimalist Utility** with **Subtle Glassmorphism and Controlled Luminance**:
- **Structured Architectural Base:** Deep slate and charcoal planes provide a focused canvas devoid of visual noise, anchoring intense generative tasks.
- **Controlled Luminescence:** Ambient cyan-violet highlights represent AI cognitive states, semantic clustering, and data routing without overwhelming editorial readability.
- **Precision Engineered Polish:** Micron-thin surface outlines, strict linear alignment, and disciplined monospaced telemetry tokens impart tactile confidence reminiscent of modern developer tooling and elite audio production suites.

## Colors

The palette leverages a dark-first spectrum to reduce fatigue during extensive curation and scripting sessions, accented by spectral cues to indicate operational status and intelligence density.

### Palette Hierarchy & Intent
- **Canvas & Surface Architecture:** 
  - `Base Canvas`: `#0B0F17` (Deep space navy-charcoal).
  - `Surface Tier 1`: `#111827` (Panel layers, toolbars, side rails).
  - `Surface Tier 2`: `#1E293B` (Cards, inspector wells, modal backings).
  - `Surface Tier 3`: `#334155` (Hover states, active selections, nested items).
- **Primary Accent (`#3B82F6`):** Electric Cobalt drives primary interactive focus, confirmed actions, and active studio pipelines.
- **Secondary AI Accent (`#06B6D4`):** Electric Cyan signals real-time intelligence feeds, audio/video ingestion nodes, and signal extraction algorithms.
- **Tertiary Accent (`#8B5CF6`):** Vibrant Violet highlights synthesis operations, tone transformation models, and multi-format repurposing recipes.
- **Functional & Semantic:**
  - `Success`: `#10B981` (Dispatched, generated, published).
  - `Warning`: `#F59E0B` (Token cap alert, tone drift).
  - `Destructive`: `#EF4444` (Pruned fragments, pipeline errors).
- **Text & Contrast:**
  - `Primary Text`: `#F8FAFC` (High-contrast 100% white-slate for headlines and prompt fields).
  - `Secondary Text`: `#94A3B8` (Balanced mid-tone for structural prose and metrics).
  - `Muted Text`: `#64748B` (Metadata, node IDs, monospaced specs).

## Typography

Typography establishes systematic hierarchy between generative workspaces and analytical metadata.

- **Primary Typeface (Geist):** Powers all headlines, body copy, and UI controls. Its neutral, engineered proportions ensure clarity across dense studio interfaces and script editors.
- **Technical & Node Typeface (JetBrains Mono):** Dictates timestamps, model versions, token counts, telemetry logs, audio waveform points, and automation parameters.
- **Dynamic Letter Spacing:** Headings scale with tight, negative tracking (`-0.03em` to `-0.01em`) to create a unified editorial presence, while monospaced labels leverage relaxed tracking for immediate legibility at compact dimensions.

## Layout & Spacing

The layout philosophy follows a rigid, modular workstation architecture based on a fluid 12-column grid. It scales seamlessly from single-column mobile monitoring to expansive multi-pane studio command desks.

### Desktop Workstation Architecture (>= 1280px)
- **Left Rail (Fixed 72px / 240px Collapsible):** Ingestion sources, global project trees, and studio settings.
- **Center Canvas (Flexible Multi-Pane Grid):** 12 columns with `1.5rem` gutters. Accommodates split views for Source Transcription, AI Synthesis nodes, and Repurposing Matrix outputs.
- **Right Inspector (Fixed 360px):** Model parameter knobs, prompt modifiers, platform-specific constraints, and export queues.

### Tablet & Mobile Reflow (< 1024px)
- Grid shifts to 4 columns on mobile, 8 columns on tablet.
- Multi-pane studio workflows switch to docked, swipeable tab layers (Source → Remix → Export).
- Margins compress from `2rem` down to `1rem` on narrow viewports to preserve dense content surface area.

## Elevation & Depth

Elevation is achieved through layered surface darkness, micron-thin translucent borders, and subtle radial backlights rather than traditional drop shadows.

### Elevation Levels
- **Level 0 (Canvas Base):** Solid `#0B0F17`. The structural substrate for the viewport.
- **Level 1 (Docked Structural Panels):** Background `#111827` with a 1px solid border of `rgba(255, 255, 255, 0.06)` or `#1E293B`.
- **Level 2 (Studio Cards & Canvas Nodes):** Background `#1E293B` with 70% opacity, supported by a `backdrop-filter: blur(12px)`. Border is 1px solid `rgba(255, 255, 255, 0.08)`.
- **Level 3 (Modals, Popovers, Active Drag Nodes):** Background `#1E293B` with high saturation. Soft ambient shadow: `0 16px 40px -8px rgba(0, 0, 0, 0.6)`.

### Controlled AI Luminescence
Active processing nodes and focused synthesis modules utilize directional ambient glows instead of heavy outlines:
- Primary active glow: `0 0 24px -4px rgba(59, 130, 246, 0.25)`.
- AI extraction glow: `0 0 24px -4px rgba(6, 182, 212, 0.22)`.
- Fusion node glow: `0 0 24px -4px rgba(139, 92, 246, 0.22)`.

## Shapes

The design system incorporates a disciplined, compact shape system (`roundedness: 1`) to project technical precision:
- **Base Components (Inputs, buttons, small tags):** `0.25rem` (4px). Clean, crisp corners that maximize screen real estate.
- **Cards, Panels, and Containers (`rounded-lg`):** `0.5rem` (8px). Subtle softening for content modules and repurposing cards.
- **Overlays, Floating Palettes (`rounded-xl`):** `0.75rem` (12px). Distinct floating presence without drifting into casual rounded forms.
- **Status Pills & Telemetry Chips:** Strict full pills (`9999px`) are reserved exclusively for live pipeline status badges and audio scrubber playheads.

## Components

### Buttons
- **Primary:** Background `#3B82F6` text `#F8FAFC`. Subtle top inner highlight `inset 0 1px 0 rgba(255, 255, 255, 0.2)`. Hover shifts to `#2563EB`. Active state scales down to `0.98`.
- **AI Action / Synthesis:** Linear gradient `135deg, #06B6D4 0%, #3B82F6 50%, #8B5CF6 100%` with high-contrast bold typography and soft outer luminescent hover.
- **Ghost / Tool Button:** Transparent background, 1px border `rgba(255, 255, 255, 0.06)`, text `#94A3B8`. Hover background `#1E293B`, text `#F8FAFC`.

### Chips & Badges
- **Status Indicators:** Pill-shaped, micro-font (`label-sm`). Translucent tinting with solid 6px dot indicator (e.g., `#06B6D4` background at 12% opacity with solid `#06B6D4` dot for "Transcribing").
- **Model / Tag Chips:** Rectangular `0.25rem` radius, `#1E293B` background, border `1px solid rgba(255, 255, 255, 0.08)`, text `#94A3B8`.

### Input Fields & Prompt Editors
- Background `#111827`, 1px solid border `#1E293B`.
- Focus state triggers border `#3B82F6` with a faint `0 0 0 1px #3B82F6` ring.
- Integrated right-side token counter using `JetBrains Mono` (`label-sm`, `#64748B`).

### Studio Cards & Repurposing Nodes
- Background `rgba(30, 41, 59, 0.65)` with backdrop-filter `blur(12px)`.
- Border `1px solid rgba(255, 255, 255, 0.08)`.
- Header section separated by a subtle 1px divider `#1E293B`.
- Drag handles and node sockets rendered in monospaced geometry with contextual hover states.

### Waveform Visualizations & Timeline Controls
- Audio/Video scrub track: `#111827` trough with 1px border `#1E293B`.
- Waveform bars: Dynamic amplitude rendered in `#334155` default, shifting to `#06B6D4` when scrubbed, and `#8B5CF6` for AI-extracted key moments.
- Scrubber head: 2px wide `#3B82F6` vertical laser with a pill-shaped timestamp indicator aloft.

### Checkboxes & Segmented Controls
- **Checkboxes:** 16x16px, `0.25rem` radius, `#111827` background, `#334155` border. Checked state transitions to `#3B82F6` with crisp white SVG check icon.
- **Segmented Switchers:** Embedded `#0B0F17` track with `0.25rem` padding. Active tab sits on `#1E293B` with a crisp 1px border `rgba(255, 255, 255, 0.08)` and high-contrast text.