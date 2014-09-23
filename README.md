pyEagle
=======

Python library for creating Eagle PCB .scr files.

Usage
-----

Import the Eagle library

```Python
from pyEagle import Eagle
```

Create a board

```Python
board = Eagle.Board(outfile='~/myOutFile.scr')
```

The Eagle commands will be written to the outfile,
overwriting anything that was already there.

Create a new signal to add to the board

```Python
trace_width = .2      # Defined in mm
trace_layer = 6       # Signal layer num in Eagle
gnd = Eagle.Signal(trace_width, trace_layer)
```

Route the signal

```Python
gnd.add(0,0)          # Start Ground at the origin
gnd.r_theta(r=2, theta=0) # Extend the trace 2mm at 0 rad
```

Add the ground signal to the board

```Python
board.add(gnd)
```

We also need to add a ZIF connecter to our board.
The package is called MYZIF, and we created it in
the MYZIFLIB library. The orientation argument is
Eagle syntax: `R<deg>` orients the part at `<deg>`
degrees, and `MR<deg>` also mirrors the part.

```Python
loc = (1, 1)
ZIF = Eagle.FootprintFactory("MYZIF", "MYZIFLIB")
first_ZIF = ZIF("first_ZIF", "R0", loc)
board.add(first_ZIF)

```

We now have a board, with a ground trace that doesn't
go anywhere, and a misplaced ZIF connecter! Print it!

```Python
board.draw()
```

That's it! Now import myOutFile.src to Eagle using
`File->Execute Script...` and watch Eagle do its magic.
