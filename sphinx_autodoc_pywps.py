# -*- coding: utf-8 -*-
from sphinx.ext.autodoc import ClassDocumenter
from sphinx.util.docstrings import prepare_docstring
from sphinx.util import force_decode
from six import text_type
import pywps

class ProcessDocumenter(ClassDocumenter):
    """Sphinx autodoc ClassDocumenter subclass that understands the 
    pywps.Process class. 
    
    The Process description, its inputs and docputs are converted to a 
    numpy style docstring. Additional sections (Notes, References, 
    Examples, etc.) can be added in the Process subclass docstring. 
    """
    priority = ClassDocumenter.priority+1
    
    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return issubclass(cls, pywps.Process)
        
    def fmt_type(self, obj):
        """Input and docput type formatting (type, default and allowed 
        values).
        """
        nmax = 10
        
        doc = ''
        
        if getattr(obj, 'allowed_values', None):
            av = ', '.join(["'{}'".format(i.value) for i in obj.allowed_values[:nmax]])
            if len(obj.allowed_values) > nmax:
                av += ', ...'
        
            doc += " : {" + av + "}"
            
        elif getattr(obj, 'data_type', None):
            doc += ' : ' + obj.data_type
            
        elif getattr(obj, 'data_format', None):
            doc += ' : ' + obj.data_format.mime_type
        
        if getattr(obj, 'min_occurs', None) is not None:
            if obj.min_occurs == 0:
                doc += ', optional'
                doc += ':{0}'.format(obj.default)
        
        return doc
        
        
    def make_numpy_doc(self):
        """Numpy style docstring where meta data is scraped from the 
        class instance.
        
        The numpy style is used because it supports multiple docputs.
        
        """
        obj = self.object()
        
        # Description
        doc = []
        doc.append(u"{} *{}* – {}".format(obj.identifier, obj.version or '', obj.title))
        doc.append('')
        doc.append(obj.abstract)
        doc.append('')
        
        # Inputs
        doc.append('Parameters')
        doc.append('----------')
        for i in obj.inputs:
            doc.append("{}{}".format(i.identifier, self.fmt_type(i)))
            doc.append("   {}".format( i.abstract or i.title))
        doc.append('')    
        
        # Outputs
        doc.append("Returns")
        doc.append("-------")
        for i in obj.outputs:
            doc.append("{}{}".format(i.identifier, self.fmt_type(i)))
            doc.append("   {}".format( i.abstract or i.title))
        
        return u'\n'.join(doc)
        
                                      

    def get_doc(self, encoding=None, ignore=1):
        # Scrape the information from the Process instance.
        docstring = self.make_numpy_doc()
        
        doc = [prepare_docstring(force_decode(docstring, encoding), ignore)]
        
        # Get extra sections from the class docstring
        # I don't understand what happens here. The `get_doc` function seems to be called twice, once without this call to super, and once with it. 
        extra = super(ProcessDocumenter, self).get_doc(encoding, ignore) or [prepare_docstring(force_decode(u'', encoding), ignore)]
        
        out = doc + extra
        return out[-2:]


def setup(app):
    app.add_autodocumenter(ProcessDocumenter)
