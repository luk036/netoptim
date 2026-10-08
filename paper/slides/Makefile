# Build the 30-minute beamer deck.
#
# md-to-beamer rules applied:
#   * emoji     -> LuaLaTeX + font fallback (rule 1)
#   * preamble  -> separate preamble.tex loaded via --include-in-header (rule 3)
#   * the flag is a CLI flag, NOT a YAML key (rule 4)
#   * compile twice for navigation / outlines (rule 10)
#
# Build:  make slides
# Verify: grep -c "Missing character" slides.log   (expect 0)

PANDOC ?= pandoc
DOC     = slides

.PHONY: all clean verify

all: $(DOC).pdf

$(DOC).tex: $(DOC).md beamer.yaml preamble.tex
	$(PANDOC) -t beamer -s --include-in-header=preamble.tex beamer.yaml $(DOC).md -o $(DOC).tex

$(DOC).pdf: $(DOC).tex preamble.tex
	lualatex -interaction=nonstopmode -halt-on-error $(DOC).tex
	lualatex -interaction=nonstopmode -halt-on-error $(DOC).tex

verify:
	@echo -n "Missing characters: "; grep -c "Missing character" $(DOC).log || true
	@echo -n "Pages: "; pdfinfo $(DOC).pdf | grep Pages || true

clean:
	rm -f $(DOC).pdf $(DOC).tex $(DOC).aux $(DOC).log $(DOC).nav $(DOC).out $(DOC).snm $(DOC).toc
