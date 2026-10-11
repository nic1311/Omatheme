-- Minimal Neovim setup with the colorscheme Omarchy's Tokyo Night theme selects
-- (themes/tokyo-night/neovim.lua: colorscheme = "tokyonight-night", plugin folke/tokyonight.nvim).
-- Omarchy layers this on LazyVim; this keeps just lazy.nvim + the colorscheme so it stays light on a phone.
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable",
    "https://github.com/folke/lazy.nvim.git", lazypath })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  { "folke/tokyonight.nvim", lazy = false, priority = 1000, opts = { style = "night" } },
}, {
  install = { colorscheme = { "tokyonight-night" } },
  checker = { enabled = false },
})

vim.opt.termguicolors = true
vim.opt.number = true
vim.cmd.colorscheme("tokyonight-night")
