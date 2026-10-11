# Third-party material

This repo adapts and bundles a few small pieces of other people's work. The repo's own code and
generated artwork have no license assigned yet (the owner can add one).

## Omarchy (MIT)

Source: <https://github.com/basecamp/omarchy>

Used in: `themes/tokyo-night/colors.toml` (verbatim), `termux/tmux.conf`, `termux/starship.toml` and
`termux/omarchy.sh` (adapted; each file's header lists the differences), and the color mapping in
`tools/omatheme/termux_kit.py` (follows `default/themed/alacritty.toml.tpl`). The glow color in
`tools/omatheme/scenes.py` was measured from Omarchy's `themes/tokyo-night/preview-unlock.png`; no
Omarchy image is included.

```
Copyright (c) David Heinemeier Hansson

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

## Tokyo Night

The palette originates from the Tokyo Night theme by enkia (`enkia.tokyo-night`) and folke's
`tokyonight.nvim`; Omarchy's `colors.toml` is the version used here. `termux/nvim-init.lua` installs
`folke/tokyonight.nvim` (Apache-2.0) at runtime; nothing from it is bundled.

## JetBrains Mono (SIL Open Font License 1.1)

`tools/fonts/JetBrainsMono-*.woff` (Latin subset, via the `@fontsource/jetbrains-mono` npm package) is
used only to set text in the generated palette sheet and preview. License: `tools/fonts/OFL.txt`.

`termux/setup.sh` downloads **JetBrainsMono Nerd Font Mono** from
<https://github.com/ryanoasis/nerd-fonts> onto the phone at install time (MIT for the patcher, OFL for the
font); it is not stored in this repo.
