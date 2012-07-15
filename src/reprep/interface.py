from . import MIME_PLAIN, contract, MIME_PYTHON
import warnings
from reprep.constants import MIME_PNG


class ReportInterface:

    @contract(nid='None|valid_id')
    def section(self, nid=None, caption=None):
        ''' Creates a subsection of the report. Returns a reference. '''
        if nid is None:
            nid = self.get_first_available_name(prefix='section')
        node = self.node(nid)
        # TODO: unify treatment of caption
        if caption:
            node.text('caption', caption)
        return node

    @contract(nid='valid_id', mime='None|str', caption='None|str')
    def data(self, nid, data, mime=MIME_PYTHON, caption=None):
        ''' 
            Attaches a data child to this node. 
        
            "data" is assumed to be a raw python structure. 
            Or, if data is a string representing a file, 
            pass a proper mime type (mime='image/png'). 
            
            Returns a reference to the node being created.
        '''
        from . import DataNode
        n = DataNode(nid=nid, data=data, mime=mime, caption=caption)
        self.add_child(n)
        return n

    @contract(nid='valid_id', mime='str', caption='None|str')
    def data_file(self, nid, mime, caption=None):
        ''' 
            Support for attaching data from a file. Note: this method is 
            supposed to be used in conjunction with the "with" construct. 
            
            For example, the following is the concise way to attach a pdf
            plot to a node.::
            
                with report.data_file('my_plot', MIME_PDF) as f:
                    pylab.figure()
                    pylab.plot(x,y)
                    pylab.title('my x-y plot')
                    pylab.savefig(f)
            
            Omit any file extension from 'id', ("my_plot" and not 
            "my_plot.pdf"), we will take care of it for you.
            
            This is a more complicated example, where we attach two versions
            of the same image, in different formats. ::
             
                for format in [MIME_PDF, MIME_PNG]:
                    with report.data_file('plot', format) as f:
                        pylab.figure()
                        pylab.plot(x,y)
                        pylab.savefig(f)
                        pylab.close()
                        
            Note that if you are mainly using pylab plots, there is the 
            function :py:func:`.plot` which offers a shortcut with less 
            ceremonies.
        '''
        from .helpers import Attacher
        import mimetypes

        if not mimetypes.guess_extension(mime):
            raise ValueError('Cannot guess extension for MIME "%s".' % mime)

        return Attacher(self, nid=nid, mime=mime, caption=caption)

    @contract(nid='None|valid_id', mime='None|str', caption='None|str')
    def data_pylab(self, nid, mime=None, caption=None, **figure_args):
        ''' Same as plot(), but deprecated. '''
        warnings.warn('data_pylab() has been deprecated, use plot().',
                      stacklevel=2)
        return self.plot(nid=nid, mime=mime, caption=caption, **figure_args)

    @contract(nid='None|valid_id', mime='None|str', caption='None|str')
    def plot(self, nid=None, mime=None, caption=None, **figure_args):
        ''' 
            Easy support for creating a node consisting of a pylab plot.
            Note: this method is supposed to be used in conjunction with 
            the "with" construct. 
            
            For example, the following is the concise way to attach a plot: ::
            
                with report.plot('my_plot') as pylab:
                    pylab.plot(x,y)
                    pylab.title('my x-y plot')
    
            Basically, data_pylab allows you to save some lines of code 
            more than with :py:func:`.data_file`.
            
            You can pass **figure_args to pylab.figure().
         '''
        from .helpers import PylabAttacher
        if nid is None:
            nid = self.get_first_available_name(prefix='plot')

        return PylabAttacher(self, nid=nid, mime=mime, caption=caption,
                             **figure_args)

    @contract(nid='valid_id|None', rgb='array[HxWx(3|4)](uint8)',
              caption='None|str')
    def data_rgb(self, nid, rgb, mime=MIME_PNG, caption=None):
        ''' 
            Create a node containing an image from a RGB[a] array.
            (internally, it will be saved as PNG)
            
            ``rgb`` must be a height x width x 3 uint8 numpy array.        
         '''
        from .helpers import data_rgb_imp
        return data_rgb_imp(parent=self, nid=nid, rgb=rgb, mime=mime, caption=caption)

    @contract(nid='valid_id|None', cols='None|(int,>=1)', caption='None|str')
    def figure(self, nid=None, cols=None, caption=None):
        ''' Attach a figure to this node. '''
        if nid is None:
            nid = self.get_first_available_name(prefix='figure')

        from . import Figure
        f = Figure(nid=nid, caption=caption, cols=cols)
        self.add_child(f)

        return f

    @contract(nid='valid_id', data='list(list)|array[HxW]', caption='None|str')
    def table(self, nid, data, cols=None, rows=None, caption=None):
        ''' 
            Attach a table to this node. 
            
            :param:data: A list of lists, or a 2D numpy array.
            :param:colos: Labels for the columns.  
            :param:rows: Labels for the rows. 
        '''
        from . import Table
        t = Table(nid=nid, data=data, cols=cols, rows=rows, caption=caption)
        self.add_child(t)
        return t

    @contract(nid='valid_id', text='str', mime='None|str')
    def text(self, nid, text, mime=MIME_PLAIN):
        ''' 
            Adds a text node with the given id.
            
            This is a very thin wrapper around data() that 
            provides a default mime type (MIME_PLAIN). 
            
            For now, only restructured text is converted to HTML,
            the rest is displayed as plain text.
        '''
        return self.data(nid=nid, data=text, mime=mime)

    def to_html(self, filename, resources_dir=None, **kwargs):
        ''' Creates a HTML representation of this report. '''
        from .output.html import node_to_html_document
        node_to_html_document(self, filename, resources_dir, **kwargs)

    def add_to(self, figure, caption=None):
        figure.sub(self, caption)

