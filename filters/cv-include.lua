-- cv-include.lua
-- Splice generated Markdown into the document at render time.
--
-- Quarto expands {{< include >}} while it scans the project, before the pre-render
-- script (scripts/build.py) has written _generated/. That breaks a fresh checkout.
-- This filter runs during the render itself, after pre-render, so the files exist.
--
-- Usage in a .qmd:
--   ::: {.cv-include file="_generated/positions.md"}
--   :::
-- Front matter key `cv-metadata: _generated/meta.yml` merges that YAML into the metadata.

local function project_path(rel)
  local base = (quarto and quarto.project and quarto.project.directory) or "."
  return pandoc.path.join({ base, rel })
end

local function read_file(rel)
  local path = project_path(rel)
  local fh = io.open(path, "r")
  if not fh then
    error("cv-include: cannot read " .. path .. " (run python3 scripts/build.py)")
  end
  local text = fh:read("a")
  fh:close()
  return text
end

local function parse(text)
  return pandoc.read(text, "markdown", PANDOC_READER_OPTIONS)
end

function Meta(meta)
  local rel = meta["cv-metadata"]
  if not rel then return nil end
  rel = pandoc.utils.stringify(rel)
  local extra = parse("---\n" .. read_file(rel) .. "\n---\n").meta
  for k, v in pairs(extra) do
    if meta[k] == nil then meta[k] = v end
  end
  -- Quarto has already defaulted the HTML page title to the file name by now.
  if extra.title ~= nil then meta.pagetitle = extra.title end
  return meta
end

function Div(div)
  if not div.classes:includes("cv-include") then return nil end
  local rel = div.attributes["file"]
  if not rel then error("cv-include: div without a file attribute") end
  return parse(read_file(rel)).blocks
end
