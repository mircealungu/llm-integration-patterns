-- links-to-footnotes.lua  (PDF build only)
-- Turn external reference links ([text](https://...)) into footnotes so long
-- URLs do not break the reading flow. Internal cross-reference links (#anchor,
-- e.g. the case-study chapter refs) are left as hyperlinks, and links already
-- inside a footnote are not touched (avoids nested footnotes, e.g. the code
-- references that already carry a GitHub link).

local function is_external(target)
  return target ~= nil and target:match('^https?://') ~= nil
end

return {
  {
    traverse = 'topdown',
    -- Return the note itself plus false so traversal does NOT descend into it;
    -- returning nil would leave descent on and re-wrap the inner links forever.
    Note = function(n)
      return n, false
    end,
    Link = function(link)
      if is_external(link.target) then
        local inlines = {}
        for _, il in ipairs(link.content) do
          inlines[#inlines + 1] = il
        end
        -- Emit the URL as raw \url{} (not a pandoc Link) so it is never
        -- re-processed, and so special characters in the URL are handled.
        inlines[#inlines + 1] = pandoc.Note(pandoc.Plain({
          pandoc.RawInline('latex', '\\url{' .. link.target .. '}')
        }))
        return inlines
      end
      return nil
    end,
  }
}
