PY ?= python3

.PHONY: all numbers test paper clean

all: numbers test paper

numbers:            ## regenerate every table and figure into out/
	PYTHONPATH=src $(PY) -m pqabdsrs --outdir out
	cp out/size-params.png out/size-ciphertext.png paper/Figures/

test:               ## check the code agrees with the numbers printed in the paper
	PYTHONPATH=src $(PY) -m pytest -q

paper:              ## build the PDF (three passes for cross-references)
	cd paper && pdflatex -interaction=nonstopmode template.tex >/dev/null
	cd paper && pdflatex -interaction=nonstopmode template.tex >/dev/null
	cd paper && pdflatex -interaction=nonstopmode template.tex >/dev/null
	@cd paper && ! grep -q "Undefined control sequence" template.log \
	  || (echo "FAIL: undefined macros in the LaTeX source" && exit 1)
	@echo "built paper/template.pdf"

clean:
	rm -rf out paper/*.aux paper/*.log paper/*.out paper/*.spl paper/template.pdf
	find . -name __pycache__ -type d -exec rm -rf {} +
