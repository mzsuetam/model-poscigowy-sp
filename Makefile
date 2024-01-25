pdf: README.md
	 tail -n+10 README.md | pandoc -o docs/dokuemntacja.pdf --metadata-file=docs/conf.yaml -N