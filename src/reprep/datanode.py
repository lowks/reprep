from . import (MIME_PNG, MIME_PYTHON, contract, describe_value,
    colorize_success, scale, posneg, Image_from_array, rgb_zoom,
    MIME_SVG, Node)
import sys



class DataNode(Node):

    @contract(nid='valid_id', mime='str', caption='None|str')
    def __init__(self, nid, data, mime=MIME_PYTHON, caption=None):
        Node.__init__(self, nid)
        self.raw_data = data
        self.mime = mime
        self.caption = caption
        
    def __eq__(self, other):
        if not Node.__eq__(self, other):
            return False
        # FIXME: cannot compare array
        #if self.raw_data != other.raw_data:
        #    logger.error('%s, raw_data' % self)
        #    return False 
        if self.mime != other.mime:
            return False 
        return True

    def __repr__(self):
        return 'DataNode(%s,%s,%s)' % (self.nid, self.mime,
                                       describe_value(self.raw_data))

    def print_tree(self, s=sys.stdout, prefix=""):
        s.write('%s- %s (%s %s)\n' % (prefix, self.nid,
                                      self.__class__, self.mime))
        for child in self.children:
            child.print_tree(s, prefix + '  ')

    def is_image(self):
        return self.mime in [MIME_PNG, MIME_SVG] # XXX 

    # TODO: move to Figure
    def display(self, display, caption=None, **kwargs):
        # TODO: save display parameters
        if display is None:
            display = 'posneg'
        known = {'posneg': posneg,
                 'success': colorize_success,
                 'scale': scale,
                 'rgb': just_check_rgb,
                 'posneg_zoom': posneg_zoom}
        if not display in known:
            raise ValueError('No known converter %r. ' % display)
        nid = display # TODO: check; add args in the name

        converter = known[display] 
        image = converter(self.raw_data, **kwargs)
        # TODO: check return
        
        # TODO: add options somewhere for minimum size and zoom factor        
        if image.shape[0] < 50:
            image = rgb_zoom(image, 10)

        pil_image = Image_from_array(image)
        with self.data_file(nid, MIME_PNG, caption=caption) as f:
            pil_image.save(f)
            
        # Add here automatic saving of scale

        return self.resolve_url_dumb(nid) 

    @contract(mime_types='list(str)')
    def get_first_child_with_mime(self, mime_types):
        ''' Search recursively the child with the given mime. '''
        def choose(node):
            return isinstance(node, DataNode) and node.mime in mime_types
        return self.find_recursively(choose)



def just_check_rgb(value):
    ''' return value, checking it's a rgb image '''
    # TODO
    return value


def posneg_zoom(value, zoom=8, uptowidth=2048, **params):
    # TODO: add checking the image does not get too large
    rgb = posneg(value, **params)
    actual = int(min(zoom, uptowidth / rgb.shape[0]))
    z = rgb_zoom(rgb, actual)
    print('scaling %d to %s' % (actual, z.shape))
    return z

