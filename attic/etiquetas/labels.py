# This file is part of pylabels, a Python library to create PDFs for printing
# labels.
# Copyright (C) 2012, 2013, 2014, 2015 Blair Bonnett
#
# pylabels is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pylabels is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pylabels.  If not, see <http://www.gnu.org/licenses/>.

DEBUG = False

import json
from copy import copy, deepcopy
from itertools import repeat

from reportlab.graphics import renderPDF, renderPM, shapes
from reportlab.graphics.shapes import ArcPath, Drawing, Image
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

EPSILON = 0.3

def debug(*args):
    if DEBUG:
        for arg in args:
            print(arg, end=' ')

class Sheet(object):
    """Create one or more sheets of labels.

    """

    def __init__(self, specification, drawing_callable, pages_to_draw=None, border=False, shade_missing=False):
        """
        Parameters
        ----------
        specification: labels.Specification instance
            The sizes etc of the label sheets.
        drawing_callable: callable
            A function (or other callable object) to call to draw an individual
            label. It will be given four parameters specifying the label. In
            order, these are a `reportlab.graphics.shapes.Drawing` instance to
            draw the label on, the width of the label, the height of the label,
            and the object to draw. The dimensions will be in points, the unit
            of choice for ReportLab.
        pages_to_draw: list of positive integers, default None
            The list pages to actually draw labels on. This is intended to be
            used with the preview methods to avoid drawing labels that will
            never be displayed. A value of None means draw all pages.
        border: Boolean, default False
            Whether or not to draw a border around each label.
        shade_missing: Boolean or ReportLab colour, default False
            Whether or not to shade missing labels (those specified through the
            partial_pages method). False means leave the labels unshaded. If a
            ReportLab colour is given, the labels will be shaded in that colour.
            A value of True will result in the missing labels being shaded in
            the hex colour 0xBBBBBB (a medium-light grey).

        Notes
        -----
        If you specify a pages_to_draw list, pages not in that list will be
        blank since the drawing function will not be called on that page. This
        could have a side-affect if you rely on the drawing function modifying
        some global values. For example, in the nametags.py and preview.py demo
        scripts, the colours for each label are picked by a pseduo-random number
        generator. However, in the preview script, this generator is not
        advanced and so the colours on the last page differ between the preview
        and the actual output.

        """
        # Save our arguments.
        specification._calculate()
        self.specs = deepcopy(specification)
        self.drawing_callable = drawing_callable
        self.pages_to_draw = pages_to_draw
        self.border = border
        if shade_missing == True:
            self.shade_missing = colors.HexColor(0xBBBBBB)
        else:
            self.shade_missing = shade_missing

        # Set up some internal variables.
        self._lw = self.specs.label_width * mm
        self._lh = self.specs.label_height * mm
        self._cr = self.specs.corner_radius * mm
        self._dw = (self.specs.label_width - self.specs.left_padding - self.specs.right_padding) * mm
        self._dh = (self.specs.label_height - self.specs.top_padding - self.specs.bottom_padding) * mm
        self._lp = self.specs.left_padding * mm
        self._bp = self.specs.bottom_padding * mm
        self._pr = self.specs.padding_radius * mm
        self._used = {}
        self._pages = []
        self._current_page = None

        # Page information.
        self._pagesize = (float(self.specs.sheet_width*mm), float(self.specs.sheet_height*mm))
        self._numlabels = [self.specs.rows, self.specs.columns]
        self._position = [1, 0]
        self.label_count = 0
        self.page_count = 0

        # Background image.
        if self.specs.background_image:
            self._bgimage = deepcopy(self.specs.background_image)

            # Different classes are scaled in different ways...
            if isinstance(self._bgimage, Image):
                self._bgimage.x = 0
                self._bgimage.y = 0
                self._bgimage.width = self._pagesize[0]
                self._bgimage.height = self._pagesize[1]
            elif isinstance(self._bgimage, Drawing):
                self._bgimage.shift(0, 0)
                self._bgimage.scale(self._pagesize[0]/self._bgimage.width, self._pagesize[1]/self._bgimage.height)
            else:
                raise ValueError("Unhandled background type.")

        # Background from a filename.
        elif self.specs.background_filename:
            self._bgimage = Image(0, 0, self._pagesize[0], self._pagesize[1], self.specs.background_filename)

        # No background.
        else:
            self._bgimage = None

        # Borders and clipping paths. We need two clipping paths; one for the
        # label as a whole (which is identical to the border), and one for the
        # available drawing area (i.e., after taking the padding into account).
        # This is necessary because sometimes the drawing area can extend
        # outside the border at the corners, e.g., if there is left padding
        # only and no padding radius, then the 'available' area corners will be
        # square and go outside the label corners if they are rounded.

        # Copy some properties to a local scope.
        h, w, r = float(self._lh), float(self._lw), float(self._cr)

        # Create the border from a path. If the corners are not rounded, skip
        # adding the arcs.
        border = ArcPath()
        if r:
            border.moveTo(w - r, 0)
            border.addArc(w - r, r, r, -90, 0)
            border.lineTo(w, h - r)
            border.addArc(w - r, h - r, r, 0, 90)
            border.lineTo(r, h)
            border.addArc(r, h - r, r, 90, 180)
            border.lineTo(0, r)
            border.addArc(r, r, r, 180, 270)
            border.closePath()
        else:
            border.moveTo(0, 0)
            border.lineTo(w, 0)
            border.lineTo(w, h)
            border.lineTo(0, h)
            border.closePath()

        # Set the properties and store.
        border.isClipPath = 0
        border.strokeWidth = 1
        border.strokeColor = colors.black
        border.fillColor = None
        self._border = border

        # Clip path for the label is the same as the border.
        self._clip_label = deepcopy(border)
        self._clip_label.isClipPath = 1
        self._clip_label.strokeColor = None
        self._clip_label.fillColor = None

        # If there is no padding (i.e., the drawable area is the same as the
        # label area) then we can just use the label clip path for the drawing
        # clip path.
        if (self._dw == self._lw) and (self._dh == self._lh):
            self._clip_drawing = self._clip_label

        # Otherwise we have to generate a separate path.
        else:
            h, w, r = float(self._dh), float(self._dw), float(self._pr)
            clip = ArcPath()
            if r:
                clip.moveTo(w - r, 0)
                clip.addArc(w - r, r, r, -90, 0)
                clip.lineTo(w, h - r)
                clip.addArc(w - r, h - r, r, 0, 90)
                clip.lineTo(r, h)
                clip.addArc(r, h - r, r, 90, 180)
                clip.lineTo(0, r)
                clip.addArc(r, r, r, 180, 270)
                clip.closePath()
            else:
                clip.moveTo(0, 0)
                clip.lineTo(w, 0)
                clip.lineTo(w, h)
                clip.lineTo(0, h)
                clip.closePath()

            # Set the clipping properties.
            clip.isClipPath = 1
            clip.strokeColor = None
            clip.fillColor = None
            self._clip_drawing = clip

    def partial_page(self, page, used_labels):
        """Allows a page to be marked as already partially used so you can
        generate a PDF to print on the remaining labels.

        Parameters
        ----------
        page: positive integer
            The page number to mark as partially used. The page must not have
            already been started, i.e., for page 1 this must be called before
            any labels have been started, for page 2 this must be called before
            the first page is full and so on.
        used_labels: iterable
            An iterable of (row, column) pairs marking which labels have been
            used already. The rows and columns must be within the bounds of the
            sheet.

        """
        # Check the page number is valid.
        if page <= self.page_count:
            raise ValueError("Page {0:d} has already started, cannot mark used labels now.".format(page))

        # Add these to any existing labels marked as used.
        used = self._used.get(page, set())
        for row, column in used_labels:
            # Check the index is valid.
            if row < 1 or row > self.specs.rows:
                raise IndexError("Invalid row number: {0:d}.".format(row))
            if column < 1 or column > self.specs.columns:
                raise IndexError("Invalid column number: {0:d}.".format(column))

            # Add it.
            used.add((int(row), int(column)))

        # Save the details.
        self._used[page] = used

    def _new_page(self):
        """Helper function to start a new page. Not intended for external use.

        """
        self._current_page = Drawing(*self._pagesize)
        if self._bgimage:
            self._current_page.add(self._bgimage)
        self._pages.append(self._current_page)
        self.page_count += 1
        self._position = [1, 0]

    def _next_label(self):
        """Helper method to move to the next label. Not intended for external use.

        This does not increment the label_count attribute as the next label may
        not be usable (it may have been marked as missing through
        partial_pages). See _next_unused_label for generally more useful method.

        """
        # Special case for the very first label.
        if self.page_count == 0:
            self._new_page()

        # Filled up a page.
        elif self._position == self._numlabels:
            self._new_page()

        # Filled up a row.
        elif self._position[1] == self.specs.columns:
            self._position[0] += 1
            self._position[1] = 0

        # Move to the next column.
        self._position[1] += 1

    def _next_unused_label(self):
        """Helper method to move to the next unused label. Not intended for external use.

        This method will shade in any missing labels if desired, and will
        increment the label_count attribute once a suitable label position has
        been found.

        """
        self._next_label()

        # This label may be missing.
        if self.page_count in self._used:
            # Keep try while the label is missing.
            missing = self._used.get(self.page_count, set())
            while tuple(self._position) in missing:
                # Throw the missing information away now we have used it. This
                # allows the _shade_remaining_missing method to work.
                missing.discard(tuple(self._position))

                # Shade the missing label if desired.
                if self.shade_missing:
                    self._shade_missing_label()

                # Try our luck with the next label.
                self._next_label()
                missing = self._used.get(self.page_count, set())

        # Increment the count now we have found a suitable position.
        self.label_count += 1

    def _calculate_edges(self):
        """Calculate edges of the current label. Not intended for external use.


        """
        # Calculate the left edge of the label.
        left = self.specs.left_margin
        left += (self.specs.label_width * (self._position[1] - 1))
        if self.specs.column_gap:
            left += (self.specs.column_gap * (self._position[1] - 1))
        left *= mm

        # And the bottom.
        bottom = self.specs.sheet_height - self.specs.top_margin
        bottom -= (self.specs.label_height * self._position[0])
        if self.specs.row_gap:
            bottom -= (self.specs.row_gap * (self._position[0] - 1))
        bottom *= mm

        # Done.
        return float(left), float(bottom)

    def _shade_missing_label(self):
        """Helper method to shade a missing label. Not intended for external use.

        """
        # Start a drawing for the whole label.
        label = Drawing(float(self._lw), float(self._lh))
        label.add(self._clip_label)

        # Fill with a rectangle; the clipping path will take care of the borders.
        r = shapes.Rect(0, 0, float(self._lw), float(self._lh))
        r.fillColor = self.shade_missing
        r.strokeColor = None
        label.add(r)

        # Add the label to the page.
        label.shift(*self._calculate_edges())
        self._current_page.add(label)

    def _shade_remaining_missing(self):
        """Helper method to shade any missing labels remaining on the current
        page. Not intended for external use.

        Note that this will modify the internal _position attribute and should
        therefore only be used once all the 'real' labels have been drawn.

        """
        # Sanity check.
        if not self.shade_missing:
            return

        # Run through each missing label left in the current page and shade it.
        missing = self._used.get(self.page_count, set())
        for position in missing:
            self._position = position
            self._shade_missing_label()

    def _draw_label(self, obj, count):
        """Helper method to draw on the current label. Not intended for external use.

        """
        # Start a drawing for the whole label.
        label = Drawing(float(self._lw), float(self._lh))
        label.add(self._clip_label)

        # And one for the available area (i.e., after padding).
        available = Drawing(float(self._dw), float(self._dh))
        available.add(self._clip_drawing)

        # Call the drawing function.
        self.drawing_callable(available, float(self._dw), float(self._dh), obj)
        # Render the contents on the label.
        available.shift(float(self._lp), float(self._bp))
        label.add(available)

        # Draw the border if requested.
        if self.border:
            label.add(self._border)

        # Add however many copies we need to.
        for i in range(count):
            # Find the next available label.
            self._next_unused_label()

            # Have we been told to skip this page?
            if self.pages_to_draw and self.page_count not in self.pages_to_draw:
                continue

            # Add the label to the page. ReportLab stores the added drawing by
            # reference so we have to copy it N times.
            thislabel = copy(label)
            thislabel.shift(*self._calculate_edges())
            self._current_page.add(thislabel)

    def add_label(self, obj, count=1):
        """Add a label to the sheet.

        Parameters
        ----------
        obj:
            The object to draw on the label. This is passed without modification
            or copying to the drawing function.
        count: positive integer, default 1
            How many copies of the label to add to the sheet. Note that the
            drawing function will only be called once and the results copied
            for each label. If the drawing function maintains any state
            internally then using this parameter may break it.

        """
        self._draw_label(obj, count)

    def add_labels(self, objects, count=1):
        """Add multiple labels to the sheet.

        Parameters
        ----------
        objects: iterable
            An iterable of the objects to add. Each of these will be passed to
            the add_label method. Note that if this is a generator it will be
            consumed.
        count: positive integer or iterable of positive integers, default 1
            The number of copies of each label to add. If a single integer,
            that many copies of every label are added. If an iterable, then
            each value specifies how many copies of the corresponding label to
            add. The iterables are advanced in parallel until one is exhausted;
            extra values in the other one are ignored. This means that if there
            are fewer count entries than objects, the objects corresponding to
            the missing counts will not be added to the sheet.

            Note that if this is a generator it will be consumed. Also note
            that the drawing function will only be called once for each label
            and the results copied for the repeats. If the drawing function
            maintains any state internally then using this parameter may break
            it.

        """
        # If we can convert it to an int, do so and use the itertools.repeat()
        # method to create an infinite iterator from it. Otherwise, assume it
        # is an iterable or sequence.
        try:
            count = int(count)
        except TypeError:
            pass
        else:
            count = repeat(count)

        # If it is not an iterable (e.g., a list or range object),
        # create an iterator over it.
        if not hasattr(count, 'next') and not hasattr(count, '__next__'):
            count = iter(count)

        # Go through the objects.
        for obj in objects:
            # Check we have a count for this one.
            try:
                thiscount = next(count)
            except StopIteration:
                break

            # Draw it.
            self._draw_label(obj, thiscount)

    def save(self, filelike):
        """Save the file as a PDF.

        Parameters
        ----------
        filelike: path or file-like object
            The filename or file-like object to save the labels under. Any
            existing contents will be overwritten.

        """
        # Shade any remaining missing labels if desired.
        self._shade_remaining_missing()

        # Create a canvas.
        canvas = Canvas(filelike, pagesize=self._pagesize)

        # Render each created page onto the canvas.
        for page in self._pages:
            renderPDF.draw(page, canvas, 0, 0)
            canvas.showPage()

        # Done.
        canvas.save()

    def preview(self, page, filelike, format='png', dpi=72, background_colour=0xFFFFFF):
        """Render a preview image of a page.

        Parameters
        ----------
        page: positive integer
            Which page to render. Must be in the range [1, page_count]
        filelike: path or file-like object
            Can be a filename as a string, a Python file object, or something
            which behaves like a Python file object.  For example, if you were
            using the Django web framework, an HttpResponse object could be
            passed to render the preview to the browser (as long as you remember
            to set the mimetype of the response).  If you pass a filename, the
            existing contents will be overwritten.
        format: string
            The image format to use for the preview. ReportLab uses the Python
            Imaging Library (PIL) internally, so any PIL format should be
            supported.
        dpi: positive real
            The dots-per-inch to use when rendering.
        background_colour: Hex colour specification
            What color background to use.

        Notes
        -----
        If you are creating this sheet for a preview only, you can pass the
        pages_to_draw parameter to the constructor to avoid the drawing function
        being called for all the labels on pages you'll never look at. If you
        preview a page you did not tell the sheet to draw, you will get a blank
        image.

        Raises
        ------
        ValueError:
            If the page number is not valid.

        """
        # Check the page number.
        if page < 1 or page > self.page_count:
            raise ValueError("Invalid page number; should be between 1 and {0:d}.".format(self.page_count))

        # Shade any remaining missing labels if desired.
        self._shade_remaining_missing()

        # Rendering to an image (as opposed to a PDF) requires any background
        # to have an integer width and height if it is a ReportLab Image
        # object. Drawing objects are exempt from this.
        oldw, oldh = None, None
        if isinstance(self._bgimage, Image):
            oldw, oldh = self._bgimage.width, self._bgimage.height
            self._bgimage.width = int(oldw) + 1
            self._bgimage.height = int(oldh) + 1

        # Let ReportLab do the heavy lifting.
        renderPM.drawToFile(self._pages[page-1], filelike, format, dpi, background_colour)

        # Restore the size of the background image if we changed it.
        if oldw:
            self._bgimage.width = oldw
            self._bgimage.height = oldh

    def preview_string(self, page, format='png', dpi=72, background_colour=0xFFFFFF):
        """Render a preview image of a page as a string.

        Parameters
        ----------
        page: positive integer
            Which page to render. Must be in the range [1, page_count]
        format: string
            The image format to use for the preview. ReportLab uses the Python
            Imaging Library (PIL) internally, so any PIL format should be
            supported.
        dpi: positive real
            The dots-per-inch to use when rendering.
        background_colour: Hex colour specification
            What color background to use.

        Notes
        -----
        If you are creating this sheet for a preview only, you can pass the
        pages_to_draw parameter to the constructor to avoid the drawing function
        being called for all the labels on pages you'll never look at. If you
        preview a page you did not tell the sheet to draw, you will get a blank
        image.

        Raises
        ------
        ValueError:
            If the page number is not valid.

        """
        # Check the page number.
        if page < 1 or page > self.page_count:
            raise ValueError("Invalid page number; should be between 1 and {0:d}.".format(self.page_count))

        # Shade any remaining missing labels if desired.
        self._shade_remaining_missing()

        # Rendering to an image (as opposed to a PDF) requires any background
        # to have an integer width and height if it is a ReportLab Image
        # object. Drawing objects are exempt from this.
        oldw, oldh = None, None
        if isinstance(self._bgimage, Image):
            oldw, oldh = self._bgimage.width, self._bgimage.height
            self._bgimage.width = int(oldw) + 1
            self._bgimage.height = int(oldh) + 1

        # Let ReportLab do the heavy lifting.
        s = renderPM.drawToString(self._pages[page-1], format, dpi, background_colour)

        # Restore the size of the background image if we changed it.
        if oldw:
            self._bgimage.width = oldw
            self._bgimage.height = oldh

        # Done.
        return s

################
# specification
################

class InvalidDimension(ValueError):
    """Raised when a sheet specification has inconsistent dimensions. """
    pass


class Specification(object):
    """Specification for a sheet of labels.

    All dimensions are given in millimetres. If any of the margins are not
    given, then any remaining space is divided equally amongst them. If all the
    width or all the height margins are given, they must exactly use up all
    non-label space on the sheet.

    """
    def __init__(self, sheet_width, sheet_height, columns, rows, label_width, label_height, **kwargs):
        """
        Required parameters
        -------------------
        sheet_width, sheet_height: positive dimension
            The size of the sheet.

        columns, rows: positive integer
            The number of labels on the sheet.

        label_width, label_size: positive dimension
            The size of each label.

        Margins and gaps
        ----------------
        left_margin: positive dimension
            The gap between the left edge of the sheet and the first column.
        column_gap: positive dimension
            The internal gap between columns.
        right_margin: positive dimension
            The gap between the right edge of the sheet and the last column.
        top_margin: positive dimension
            The gap between the top edge of the sheet and the first row.
        row_gap: positive dimension
            The internal gap between rows.
        bottom_margin: positive dimension
            The gap between the bottom edge of the sheet and the last row.

        Padding
        -------
        left_padding, right_padding, top_padding, bottom_padding: positive dimensions, default 0
            The padding between the edges of the label and the area available
            to draw on.

        Corners
        ---------------------
        corner_radius: positive dimension, default 0
            Gives the labels rounded corners with the given radius.
        padding_radius: positive dimension, default 0
            Give the drawing area rounded corners. If there is no padding, this
            must be set to zero.

        Background
        ----------
        background_image: reportlab.graphics.shape.Image
            An image to use as the background to the page. This will be
            automatically sized to fit the page; make sure it has the correct
            aspect ratio.
        background_filename: string
            Filename of an image to use as a background to the page. If both
            this and background_image are given, then background_image will
            take precedence.

        Raises
        ------
        InvalidDimension
            If any given dimension is invalid (i.e., the labels cannot fit on
            the sheet).

        """
        # Compulsory arguments.
        self._sheet_width = float(sheet_width)
        self._sheet_height = float(sheet_height)
        self._columns = int(columns)
        self._rows = int(rows)
        self._label_width = float(label_width)
        self._label_height = float(label_height)

        # Optional arguments; missing ones will be computed later.
        self._left_margin = kwargs.pop('left_margin', None)
        self._column_gap = kwargs.pop('column_gap', None)
        self._right_margin = kwargs.pop('right_margin', None)
        self._top_margin = kwargs.pop('top_margin', None)
        self._row_gap = kwargs.pop('row_gap', None)
        self._bottom_margin = kwargs.pop('bottom_margin', None)

        # Optional arguments with default values.
        self._left_padding = kwargs.pop('left_padding', 0)
        self._right_padding = kwargs.pop('right_padding', 0)
        self._top_padding = kwargs.pop('top_padding', 0)
        self._bottom_padding = kwargs.pop('bottom_padding', 0)
        self._corner_radius = float(kwargs.pop('corner_radius', 0))
        self._padding_radius = float(kwargs.pop('padding_radius', 0))
        self._background_image = kwargs.pop('background_image', None)
        self._background_filename = kwargs.pop('background_filename', None)

        # Leftover arguments.
        if kwargs:
            args = kwargs.keys()
            if len(args) == 1:
                raise TypeError("Unknown keyword argument {}.".format(args[0]))
            else:
                raise TypeError("Unknown keyword arguments: {}.".format(', '.join(args)))

        # Track which attributes have been automatically set.
        self._autoset = set()

        # Check all the dimensions etc are valid.
        self._calculate()

    def _calculate(self):
        """Checks the dimensions of the sheet are valid and consistent.

        NB: this is called internally when needed; there should be no need for
        user code to call it.

        """
        # Check the dimensions are larger than zero.
        for dimension in ('_sheet_width', '_sheet_height', '_columns', '_rows', '_label_width', '_label_height'):
            if getattr(self, dimension) <= 0:
                name = dimension.replace('_', ' ').strip().capitalize()
                raise InvalidDimension("{0:s} must be greater than zero.".format(name))

        # Check margins / gaps are not smaller than zero if given.
        # At the same time, force the values to floats.
        for margin in ('_left_margin', '_column_gap', '_right_margin', '_top_margin', '_row_gap', '_bottom_margin',
                       '_left_padding', '_right_padding', '_top_padding', '_bottom_padding'):
            val = getattr(self, margin)
            if val is not None:
                if margin in self._autoset:
                    val = None
                else:
                    val = float(val)
                    if val < 0:
                        name = margin.replace('_', ' ').strip().capitalize()
                        raise InvalidDimension("{0:s} cannot be less than zero.".format(name))
                setattr(self, margin, val)
            else:
                self._autoset.add(margin)

        # Check the corner radius.
        if self._corner_radius < 0:
            raise InvalidDimension("Corner radius cannot be less than zero.")
        if self._corner_radius > (self._label_width / 2):
            raise InvalidDimension("Corner radius cannot be more than half the label width.")
        if self._corner_radius > (self._label_height / 2):
            raise InvalidDimension("Corner radius cannot be more than half the label height.")

        # If there is no padding, we don't need the padding radius.
        if (self._left_padding + self._right_padding + self._top_padding + self._bottom_padding) == 0:
            if self._padding_radius != 0:
                raise InvalidDimension("Padding radius must be zero if there is no padding.")
        else:
            if (self._left_padding + self._right_padding) >= self._label_width:
                raise InvalidDimension("Sum of horizontal padding must be less than the label width.")
            if (self._top_padding + self._bottom_padding) >= self._label_height:
                raise InvalidDimension("Sum of vertical padding must be less than the label height.")
            if self._padding_radius < 0:
                raise InvalidDimension("Padding radius cannot be less than zero.")

        # Calculate the amount of spare space.
        hspace = self._sheet_width - (self._label_width * self._columns)
        vspace = self._sheet_height - (self._label_height * self._rows)
        debug('sheet_width',self._sheet_width)
        debug('self._label_width * self._columns',self._label_width * self._columns)
        debug('self._label_height * self._rows', self._label_height * self._rows)
        debug('sheet_height',self._sheet_height)
        debug('initial hspace',hspace)
        debug('initial vspace',vspace)

        # Cannot fit.
        if hspace < 0:
            raise InvalidDimension("Labels are too wide to fit on the sheet.")
        if vspace < 0:
            raise InvalidDimension("Labels are too tall to fit on the sheet.")

        # Process the horizontal margins / gaps.
        hcount = 1 + self._columns
        if self._left_margin is not None:
            hspace -= self._left_margin
            if hspace < 0:
                raise InvalidDimension("Left margin is too wide for the labels to fit on the sheet.")
            hcount -= 1
        debug('hspace - left_margin',hspace)
        debug('****** self.column_gap',self._column_gap)
        if self._column_gap is not None and self._column_gap != 0:
            hspace -= ((self._columns - 1) * self._column_gap)
            if hspace < 0:
                raise InvalidDimension("Column gap is too wide for the labels to fit on the sheet.")
            hcount -= (self._columns - 1)
        debug('hspace - column_gap',hspace)
        if self._right_margin is not None:
            hspace -= self._right_margin
            if hspace < EPSILON and hspace > -EPSILON:
                self._right_margin += hspace
                hspace = 0
            if hspace < 0:
                debug('hspace left', hspace)
                raise InvalidDimension("Right margin is too wide for the labels to fit on the sheet.")
            hcount -= 1
        debug('hspace - right_margin',hspace)

        # Process the vertical margins / gaps.
        vcount = 1 + self._rows
        if self._top_margin is not None:
            vspace -= self._top_margin
            if vspace < 0:
                raise InvalidDimension("Top margin is too tall for the labels to fit on the sheet.")
            vcount -= 1
        debug('vspace - top_margin',vspace)
        if self._row_gap is not None and self._row_gap != 0:
            vspace -= ((self._rows - 1) * self._row_gap)
            if vspace < 0:
                raise InvalidDimension("Row gap is too tall for the labels to fit on the sheet.")
            vcount -= (self._rows - 1)
        debug('vspace - row_gap',vspace)
        if self._bottom_margin is not None:
            vspace -= self._bottom_margin
            
            if vspace < EPSILON and vspace > -EPSILON:
                self._bottom_margin += vspace
                vspace = 0
            if vspace < 0:
                debug('vspace left', vspace)
                raise InvalidDimension("Bottom margin is too tall for the labels to fit on the sheet.")
            vcount -= 1
        debug('vspace - bottom_margin',vspace)

        # If all the margins are specified, they must use up all available space.
        if hcount == 0 and hspace != 0:
            debug('hspace left', hspace)
            raise InvalidDimension("Not all width used by manually specified margins/gaps; {}mm left.".format(hspace))
        if vcount == 0 and vspace != 0:
            debug('vspace left', vspace)
            raise InvalidDimension("Not all height used by manually specified margins/gaps; {}mm left.".format(vspace))

        debug('hspace',hspace)
        debug('vspace',vspace)

        # Split any extra horizontal space and allocate it.
        if hcount:
            auto_margin = hspace / hcount
            debug('auto_margin horizontal',auto_margin)
            for margin in ('_left_margin', '_column_gap', '_right_margin'):
                if getattr(self, margin) is None:
                    setattr(self, margin, auto_margin)

        # And allocate any extra vertical space.
        if vcount:
            auto_margin = vspace / vcount
            debug('auto_margin horizontal',auto_margin)
            for margin in ('_top_margin', '_row_gap', '_bottom_margin'):
                if getattr(self, margin) is None:
                    setattr(self, margin, auto_margin)

    def bounding_boxes(self, mode='fraction', output='dict'):
        """Get the bounding boxes of the labels on a page.

        Parameters
        ----------
        mode: 'fraction', 'actual'
            If 'fraction', the bounding boxes are expressed as a fraction of the
            height and width of the sheet. If 'actual', they are the actual
            position of the labels in millimetres from the top-left of the
            sheet.
        output: 'dict', 'json'
            If 'dict', a dictionary with label identifier tuples (row, column)
            as keys and a dictionary with 'left', 'right', 'top', and 'bottom'
            entries as the values.
            If 'json', a JSON encoded string which represents a dictionary with
            keys of the string format 'rowxcolumn' and each value being a
            bounding box dictionary with 'left', 'right', 'top', and 'bottom'
            entries.

        Returns
        -------
        The bounding boxes in the format set by the output parameter.

        """
        boxes = {}

        # Check the parameters.
        if mode not in ('fraction', 'actual'):
            raise ValueError("Unknown mode {0}.".format(mode))
        if output not in ('dict', 'json'):
            raise ValueError("Unknown output {0}.".format(output))

        # Iterate over the rows.
        for row in range(1, self.rows + 1):
            # Top and bottom of all labels in the row.
            top = self.top_margin + ((row - 1) * (self.label_height + self.row_gap))
            bottom = top + self.label_height

            # Now iterate over all columns in this row.
            for column in range(1, self.columns + 1):
                # Left and right position of this column.
                left = self.left_margin + ((column - 1) * (self.label_width + self.column_gap))
                right = left + self.label_width

                # Output in the appropriate mode format.
                if mode == 'fraction':
                    box = {
                        'top': top / self.sheet_height,
                        'bottom': bottom / self.sheet_height,
                        'left': left / self.sheet_width,
                        'right': right / self.sheet_width,
                    }
                elif mode == 'actual':
                    box = {'top': top, 'bottom': bottom, 'left': left, 'right': right}

                # Add to the collection.
                if output == 'json':
                    boxes['{0:d}x{1:d}'.format(row, column)] = box
                    box['top'] = float(box['top'])
                    box['bottom'] = float(box['bottom'])
                    box['left'] = float(box['left'])
                    box['right'] = float(box['right'])
                else:
                    boxes[(row, column)] = box

        # Done.
        if output == 'json':
            return json.dumps(boxes)
        return boxes

    # Helper function to create an accessor for one of the properties.
    # attr is the 'internal' attribute e.g., _sheet_width.
    def create_accessor(attr, deletable=False):
        # Getter is simple; no processing needed.
        @property
        def accessor(self):
            return getattr(self, attr)

        # Setter is more complicated.
        @accessor.setter
        def accessor(self, value):
            # Store the original value in case we need to reset.
            original = getattr(self, attr)

            # If this was originally autoset or not.
            was_autoset = attr in self._autoset

            # Discard this attribute from the autoset list.
            self._autoset.discard(attr)

            # Set the value and see if it is valid.
            setattr(self, attr, value)
            try:
                self._calculate()
            except:
                # Reset to the original state.
                setattr(self, attr, original)
                if was_autoset:
                    self._autoset.add(attr)

                # Let the error propogate up.
                raise

        # Create a deleter if allowable.
        if deletable:
            @accessor.deleter
            def accessor(self):
                self._autoset.add(attr)
                setattr(self, attr, None)
                self._calculate()

        # And we now have our accessor.
        return accessor

    # Create accessors for all our properties.
    sheet_width = create_accessor('_sheet_width')
    sheet_height = create_accessor('_sheet_height')
    label_width = create_accessor('_label_width')
    label_height = create_accessor('_label_height')
    columns = create_accessor('_columns')
    rows = create_accessor('_rows')
    left_margin = create_accessor('_left_margin', deletable=True)
    column_gap = create_accessor('_column_gap', deletable=True)
    right_margin = create_accessor('_right_margin', deletable=True)
    top_margin = create_accessor('_top_margin', deletable=True)
    row_gap = create_accessor('_row_gap', deletable=True)
    bottom_margin = create_accessor('_bottom_margin', deletable=True)
    corner_radius = create_accessor('_corner_radius')
    padding_radius = create_accessor('_padding_radius')
    background_image = create_accessor('_background_image', deletable=True)
    background_filename = create_accessor('_background_filename', deletable=True)
    left_padding = create_accessor('_left_padding', deletable=True)
    right_padding = create_accessor('_right_padding', deletable=True)
    top_padding = create_accessor('_top_padding', deletable=True)
    bottom_padding = create_accessor('_bottom_padding', deletable=True)

    # Don't need the helper function any more.
    del create_accessor
