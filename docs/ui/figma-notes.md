# Velvet Rope Figma UI Notes

## Approved Screen

- Figma file: [Velvet Rope MVP](https://www.figma.com/design/Qx3kHTdnNlP5AgmwRUFRiS)
- Figma frame: Velvet Rope MVP / Level 1 Nightclub
- Frame node: `1:2`
- Primary layout: two-column desktop layout with doorway and chat on the left, level cards and hint panel on the right
- Mood display: portrait plus mood label with ambient rope lighting
- Level one world: absurd nightclub
- First gatekeeper: Marlowe, Exhausted Bouncer

## Implementation Tokens

- Background: `#09090b`
- Panel background: `#120d14`
- Secondary panel: `#101014`
- Rope accent: `#b32735`
- Rope highlight: `#e3424f`
- Gold trim: `#d6b15e`
- Text gold: `#f7e4a8`
- Muted text: `#b7ad92`
- Danger/suspicion accent: `#b32735`
- Success/softened accent: `#4f8f73`
- Border: `#2c2430`
- Border radius: `8px`

## Components

- Doorway shell
- Velvet rope with glow
- Marlowe portrait
- Mood badge
- Chat transcript
- Qualitative hint text
- Player input row
- Send button
- Reset button
- Locked level card: Cosmic Bureaucracy
- Locked level card: Enchanted Manor

## Implementation Notes

- Keep points hidden in the UI; the player sees mood, hints, portrait, and ambient color only.
- Use the Figma frame as the visual source for the first Gradio implementation.
- Preserve the custom dark nightclub styling rather than default Gradio surfaces.
- Keep the right rail focused on current mood, read-the-room hint, and locked future doors.
- Show Cosmic Bureaucracy and Enchanted Manor as locked future levels in the right rail.
