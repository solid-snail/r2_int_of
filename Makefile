.PHONY: all
all:
	gcc -O0 -gdwarf-4 -o intof intof.c
	python3 modify_dwarf_ref.py
	chmod +100 intof_mod
	# size: 4194304 - 2 (for "//l" suffix)
	python3 -c "import sys; sys.stdout.buffer.write(b'p' * 4194302 + b'\n')" > dummy.c
	python3 -c "import sys; sys.stdout.buffer.write(b'p' * 4194302 + b'\n')" >> dummy.c
	python3 -c "import sys; sys.stdout.buffer.write(b'p' * 4194302 + b'\n')" >> dummy.c
	python3 -c "import sys; sys.stdout.buffer.write(b'p' * (4194302 - 5) + b'\n')" >> dummy.c
