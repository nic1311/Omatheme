-- Minimal Neovim setup with the colorscheme Omarchy's Tokyo Night theme selects
-- (themes/tokyo-night/neovim.lua: colorscheme = "tokyonight-night", plugin folke/tokyonight.nvim).
-- Omarchy layers this on LazyVim; this keeps just lazy.nvim + the colorscheme so it stays light on a phone.
vim.opt.termguicolors = true
vim.opt.number = true

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local out = vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable",
    "https://github.com/folke/lazy.nvim.git", lazypath })
  if vim.v.shell_error ~= 0 then
    -- Drop a half-finished clone, or every later start would find the folder and fail to load it.
    vim.fn.delete(lazypath, "rf")
    vim.api.nvim_echo({
      { "omatheme: could not download lazy.nvim, so Tokyo Night is off for now. Restart nvim when online.\n",
        "WarningMsg" },
      { out },
    }, true, {})
    return
  end
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  { "folke/tokyonight.nvim", lazy = false, priority = 1000, opts = { style = "night" } },
}, {
  install = { colorscheme = { "tokyonight-night" } },
  checker = { enabled = false },
})

-- If tokyonight.nvim itself could not be installed, lazy.nvim has already said why; keep the default colors.
pcall(vim.cmd.colorscheme, "tokyonight-night")
