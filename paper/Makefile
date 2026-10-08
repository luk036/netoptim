# Build pipeline for the "Clock Skew Scheduling" survey.
#
# Flag rationale (see also the md-to-latex skill):
#   --citeproc --csl=ieee.csl : IEEE numeric in-text citations and a numeric
#       reference list.  ieee.csl is *vendored* in this directory and is
#       self-contained (it has no <link rel="independent-parent">), so the
#       build needs no network access.  Verified offline with
#       HTTP_PROXY=http://127.0.0.1:9.
#   -N                        : number sections/subsections.
#   --pdf-engine=pdflatex     : all mathematics and text are ASCII, so pdflatex
#       is sufficient; no xelatex/font fallback is required.
#   -V geometry:margin=1in    : comfortable single-column page.
#
# Figures are *native TikZ* included via \input{figures/*.tikz}.  We do NOT
# convert the source SVGs with rsvg-convert: without a font configuration it
# silently drops every <text> element, producing empty figures.  Compiling the
# original .tikz sources keeps the labels (text) intact and the output vector.
#
# We deliberately do NOT use pandoc-crossref/cleveref.  Plain LaTeX
# \label/\ref/\eqref is used for every cross-reference; this is robust across
# document classes and avoids the cleveref/\newlabel conflicts that render
# references as "??" with older classes.

PANDOC ?= pandoc
CSL    ?= ieee.csl
BIB    ?= refs.bib
MD      = clock_skew_scheduling.md
OUT     = clock_skew_scheduling.pdf

PDFFLAGS = -s -t latex -N --pdf-engine=pdflatex \
           --pdf-engine-opt=-interaction=nonstopmode \
           --citeproc --csl=$(CSL) \
           -V geometry:margin=1in

.PHONY: paper pdf html tex clean

paper: pdf

pdf: $(OUT)

$(OUT): $(MD) metadata.yaml latex.yaml $(BIB) $(CSL)
	$(PANDOC) $(PDFFLAGS) metadata.yaml latex.yaml $(MD) -o $(OUT)

html: $(MD) metadata.yaml latex.yaml $(BIB) $(CSL)
	$(PANDOC) -s -t html5 --citeproc --csl=$(CSL) --mathjax \
	  metadata.yaml latex.yaml $(MD) -o clock_skew_scheduling.html

tex: $(MD) metadata.yaml latex.yaml $(BIB) $(CSL)
	$(PANDOC) -s -t latex -N --citeproc --csl=$(CSL) \
	  metadata.yaml latex.yaml $(MD) -o clock_skew_scheduling.tex

clean:
	rm -f $(OUT) clock_skew_scheduling.tex clock_skew_scheduling.html
