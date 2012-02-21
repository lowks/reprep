from . import MIME_SVG, MIME_PDF, RepRepDefaults, MIME_PNG, contract, Node
import mimetypes
import tempfile
from reprep.node import DataNode


class Attacher:

    @contract(node=Node, nid='valid_id', mime='None|str', caption='None|str')
    def __init__(self, node, nid, mime, caption):
        self.node = node
        self.nid = nid
        self.mime = mime
        self.caption = caption
        if self.mime is not None:
            suffix = mimetypes.guess_extension(self.mime)
            if not suffix:
                raise Exception('Cannot guess extension for MIME %r.' % mime)
        else:
            suffix = '.bin'

        self.temp_file = tempfile.NamedTemporaryFile(suffix=suffix)

    def __enter__(self):
        return self.temp_file.name

    def __exit__(self, _a, _b, _c):
        with open(self.temp_file.name) as f:
            data = f.read()
            self.node.data(nid=self.nid, data=data,
                           mime=self.mime,
                           caption=self.caption)
        self.temp_file.close()


class PylabAttacher:

    @contract(node=Node, nid='valid_id', mime='None|str', caption='None|str')
    def __init__(self, node, nid, mime, caption, **figure_args):
        self.node = node
        self.nid = nid
        self.mime = mime
        self.caption = caption

        if self.mime is None:
            self.mime = RepRepDefaults.default_image_format

        suffix = mimetypes.guess_extension(self.mime)
        if not suffix:
            msg = 'Cannot guess extension for MIME %r.' % mime
            raise ValueError(msg)

        self.temp_file = tempfile.NamedTemporaryFile(suffix=suffix)

        from . import reprep_pylab_instance
        self.pylab = reprep_pylab_instance
        self.figure = self.pylab.figure(**figure_args)

    def __enter__(self):
        return self.pylab

    def __exit__(self, exc_type, exc_value, traceback): #@UnusedVariable
        if exc_type is not None:
            # an error occurred. Close the figure and return false.
            self.pylab.close()
            return False

        if not self.figure.axes:
            raise Exception('You did not draw anything in the image.')

        self.pylab.savefig(self.temp_file.name,
                           **RepRepDefaults.savefig_params)

        with open(self.temp_file.name) as f:
            data = f.read()
        self.temp_file.close()

        image_node = DataNode(nid=self.nid, data=data,
                              mime=self.mime, caption=self.caption)

        # save other versions if needed
        if (self.mime != MIME_PNG) and RepRepDefaults.save_extra_png:
            with image_node.data_file('png', mime=MIME_PNG) as f2:
                self.pylab.savefig(f2, **RepRepDefaults.savefig_params)

        if (self.mime != MIME_SVG) and RepRepDefaults.save_extra_svg:
            with image_node.data_file('svg', mime=MIME_SVG) as f2:
                self.pylab.savefig(f2, **RepRepDefaults.savefig_params)

        if (self.mime != MIME_PDF) and RepRepDefaults.save_extra_pdf:
            with image_node.data_file('pdf', mime=MIME_PDF) as f2:
                self.pylab.savefig(f2, **RepRepDefaults.savefig_params)

        self.pylab.close()

        self.node.add_child(image_node)


@contract(parent=Node, nid='valid_id',
          rgb='array[HxWx(3|4)]', caption='None|str')
def data_rgb_imp(parent, nid, rgb, caption=None):
    from .graphics import Image_from_array, rgb_zoom

    # zoom images smaller than 50
    if max(rgb.shape[0], rgb.shape[1]) < 50: # XXX config
        rgb = rgb_zoom(rgb, 10)

    pil_image = Image_from_array(rgb)

    with parent.data_file(nid=nid, mime=MIME_PNG, caption=caption) as f:
        pil_image.save(f)

    return parent[nid]


